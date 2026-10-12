"""
Week 9 — MCP Host Agent Module
Demonstrates dynamic tool discovery over the Model Context Protocol (MCP).

KEY ARCHITECTURAL HIGHLIGHTS:
1. ZERO HARDCODED TOOLS: Discovers all capabilities dynamically from tools/list via MCP.
2. CONFIG-DRIVEN ARCHITECTURE: Servers are declared in an external config file (mcp_config.json).
   Adding new servers (e.g. ticket-history-server) requires ZERO changes to this code.
3. CLEAR SEPARATION OF CONCERNS:
   - Host (this module): Runs the LLM (Claude Haiku 4.5), manages conversation state, enforces safety budgets.
   - Servers: Expose deterministic tool interfaces over JSON-RPC 2.0 stdio transport. No LLM runs on servers.
"""

import argparse
import asyncio
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.llm import get_anthropic_client, MODEL_NAME, calculate_cost

# UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MCPAgent")


@dataclass
class AgentBudgets:
    """Enforceable runtime safety limits for the agent loop."""
    max_iterations: int = 6
    max_tokens: int = 8000
    max_cost: float = 0.08
    max_wall_clock_seconds: float = 25.0


@dataclass
class AgentStep:
    iteration: int
    thought: Optional[str]
    tool_name: Optional[str]
    server_name: Optional[str]
    tool_input: Optional[Dict[str, Any]]
    tool_result: Optional[str]
    tokens: int
    cost: float
    elapsed: float


@dataclass
class AgentRunResult:
    query: str
    reply: str
    discovered_tools: List[str]
    tool_counts_by_server: Dict[str, int]
    steps: List[AgentStep]
    total_tokens: int
    total_cost: float
    latency: float
    budget_terminated: bool = False
    budget_hit: Optional[str] = None


SYSTEM_PROMPT = """You are a senior customer support refund & escalation agent.
Your job is to resolve customer inquiries and support tickets using available tools.

You discover your tools dynamically via the Model Context Protocol (MCP).
Use the tools that best address the user's inquiry:
- If asked about an order or refund, check order details and policy rules.
- If asked about ticket escalation status, agent notes, or prior touches, use the ticket history tools.
- If a tool reports a recoverable error or guidance, follow the guidance and explain next steps to the customer.

OUTPUT CONTRACT:
1. Provide a professional, concise, empathetic response.
2. Always quote relevant IDs (Ticket ID, Order ID, Customer ID, Escalation status).
3. If an escalation exists, highlight the escalation level and prior agent touches.
4. Conclude with:
   Best regards,
   Support Team
"""


def _check_budgets(
    budgets: AgentBudgets,
    iteration: int,
    elapsed: float,
    total_tokens: int,
    total_cost: float
) -> Optional[Tuple[str, Any, Any]]:
    if iteration > budgets.max_iterations:
        return ("max_iterations", budgets.max_iterations, iteration)
    if elapsed > budgets.max_wall_clock_seconds:
        return ("max_wall_clock_seconds", budgets.max_wall_clock_seconds, round(elapsed, 4))
    if total_tokens > budgets.max_tokens:
        return ("max_tokens", budgets.max_tokens, total_tokens)
    if total_cost > budgets.max_cost:
        return ("max_cost", budgets.max_cost, round(total_cost, 6))
    return None


class MCPAgentHost:
    """
    Host Agent that discovers tools dynamically across all configured MCP servers.
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path).resolve()
        if not self.config_path.exists():
            raise FileNotFoundError(f"MCP configuration file not found at {self.config_path}")
        
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.servers_cfg = self.config.get("mcpServers", {})
        
        # Discovered state
        self.sessions: Dict[str, ClientSession] = {}
        self.tool_to_server: Dict[str, str] = {}
        self.discovered_tools_schema: List[Dict[str, Any]] = []
        self.tools_by_server: Dict[str, List[str]] = {}

    async def connect_and_discover(self, stack: AsyncExitStack) -> List[Dict[str, Any]]:
        """
        Connects to all configured MCP servers via stdio and discovers tools via tools/list.
        """
        logger.info(f"Connecting to {len(self.servers_cfg)} MCP server(s) configured in {self.config_path.name}...")
        self.discovered_tools_schema = []
        self.tool_to_server = {}
        self.tools_by_server = {}

        for server_name, srv_info in self.servers_cfg.items():
            cmd = srv_info.get("command", "python")
            # Ensure using current virtualenv python when 'python' is specified
            if cmd == "python":
                cmd = sys.executable
            
            args = srv_info.get("args", [])
            env = srv_info.get("env", None)
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)
            else:
                merged_env = None

            server_params = StdioServerParameters(
                command=cmd,
                args=args,
                env=merged_env
            )

            read_stream, write_stream = await stack.enter_async_context(stdio_client(server_params))
            session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
            
            # MCP Handshake: initialize
            init_result = await session.initialize()
            logger.info(f"Connected to MCP server '{server_name}' (protocol {init_result.protocol_version})")
            
            # MCP Dynamic Tool Discovery: tools/list
            tools_response = await session.list_tools()
            self.sessions[server_name] = session
            self.tools_by_server[server_name] = []

            for tool in tools_response.tools:
                tool_name = tool.name
                self.tool_to_server[tool_name] = server_name
                self.tools_by_server[server_name].append(tool_name)
                
                # Transform MCP tool definition to Anthropic tool schema
                anthropic_tool = {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema if hasattr(tool, "inputSchema") and tool.inputSchema else {
                        "type": "object",
                        "properties": {}
                    }
                }
                self.discovered_tools_schema.append(anthropic_tool)
                logger.info(f"  -> Discovered tool: '{tool_name}' on server '{server_name}'")

        return self.discovered_tools_schema

    async def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Dispatches a tool call over MCP stdio to the designated server hosting the tool.
        """
        server_name = self.tool_to_server.get(tool_name)
        if not server_name or server_name not in self.sessions:
            return json.dumps({
                "status": "error",
                "error": f"Tool '{tool_name}' is not registered on any connected MCP server."
            })

        session = self.sessions[server_name]
        logger.info(f"[MCP WIRE CALL] Routing tool '{tool_name}' to server '{server_name}' with args {arguments}")
        
        try:
            call_res = await session.call_tool(tool_name, arguments)
            # Combine content blocks from MCP call
            content_pieces = []
            for item in call_res.content:
                if hasattr(item, "text"):
                    content_pieces.append(item.text)
                else:
                    content_pieces.append(str(item))
            
            result_str = "\n".join(content_pieces)
            return result_str
        except Exception as e:
            logger.error(f"Error executing MCP tool '{tool_name}' on '{server_name}': {e}")
            return json.dumps({"status": "error", "message": str(e), "recoverable": True})

    async def run(
        self,
        query: str,
        budgets: Optional[AgentBudgets] = None,
        client: Optional[Any] = None
    ) -> AgentRunResult:
        """
        Executes ReAct loop over discovered MCP tools.
        """
        if budgets is None:
            budgets = AgentBudgets()
        if client is None:
            client = get_anthropic_client()

        start_time = time.perf_counter()
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": query}
        ]

        total_tokens = 0
        total_cost = 0.0
        iteration = 0
        steps: List[AgentStep] = []
        final_reply = ""
        budget_terminated = False
        budget_hit = None

        tool_counts = {srv: len(tools) for srv, tools in self.tools_by_server.items()}

        async with AsyncExitStack() as stack:
            # 1. Connect and dynamically discover tools over MCP
            tools_schema = await self.connect_and_discover(stack)

            # 2. ReAct Agent Loop
            while True:
                iteration += 1
                elapsed = time.perf_counter() - start_time

                breach = _check_budgets(budgets, iteration, elapsed, total_tokens, total_cost)
                if breach:
                    budget_hit, limit_val, curr_val = breach
                    budget_terminated = True
                    logger.warning(f"Budget '{budget_hit}' hit: current={curr_val}, limit={limit_val}")
                    final_reply = (
                        "Your request is undergoing automated processing review. A support specialist "
                        "will follow up shortly.\n\nBest regards,\nSupport Team"
                    )
                    break

                # 3. Model call happens exclusively on host agent side
                try:
                    response = client.messages.create(
                        model=MODEL_NAME,
                        max_tokens=1024,
                        system=SYSTEM_PROMPT,
                        tools=tools_schema,
                        messages=messages
                    )
                except Exception as e:
                    logger.error(f"LLM API error: {e}")
                    final_reply = f"Error processing request: {e}\n\nBest regards,\nSupport Team"
                    break

                lap_in = response.usage.input_tokens
                lap_out = response.usage.output_tokens
                lap_tokens = lap_in + lap_out
                lap_cost = calculate_cost(lap_in, lap_out)
                total_tokens += lap_tokens
                total_cost += lap_cost
                elapsed = time.perf_counter() - start_time

                # Check post-inference budgets
                breach_after = _check_budgets(budgets, iteration, elapsed, total_tokens, total_cost)
                if breach_after and breach_after[0] in ("max_tokens", "max_cost"):
                    budget_hit = breach_after[0]
                    budget_terminated = True
                    final_reply = "Processing queued for specialist review due to token limits.\n\nBest regards,\nSupport Team"
                    break

                # 4. Process Model output blocks
                tool_calls_in_lap = []
                thought_text = ""

                for block in response.content:
                    if block.type == "text":
                        thought_text += block.text
                    elif block.type == "tool_use":
                        tool_calls_in_lap.append(block)

                if response.stop_reason == "end_turn" and not tool_calls_in_lap:
                    final_reply = thought_text
                    break

                # Append assistant message with its tool use requests
                messages.append({"role": "assistant", "content": response.content})

                # 5. Execute tool calls over MCP stdio
                tool_result_contents = []
                for tool_call in tool_calls_in_lap:
                    t_name = tool_call.name
                    t_input = tool_call.input
                    t_id = tool_call.id
                    srv_name = self.tool_to_server.get(t_name, "unknown")

                    print(f"\n>>> [TRACE: MCP TOOL CALL] Server: {srv_name} | Tool: {t_name} | Args: {t_input}")
                    mcp_output = await self.execute_tool_call(t_name, t_input)
                    print(f"<<< [TRACE: MCP TOOL RESULT] Server: {srv_name} | Output:\n{mcp_output}\n")

                    step = AgentStep(
                        iteration=iteration,
                        thought=thought_text,
                        tool_name=t_name,
                        server_name=srv_name,
                        tool_input=t_input,
                        tool_result=mcp_output,
                        tokens=lap_tokens,
                        cost=lap_cost,
                        elapsed=elapsed
                    )
                    steps.append(step)

                    tool_result_contents.append({
                        "type": "tool_result",
                        "tool_use_id": t_id,
                        "content": mcp_output
                    })

                # Feed observations back to conversation context
                messages.append({
                    "role": "user",
                    "content": tool_result_contents
                })

        return AgentRunResult(
            query=query,
            reply=final_reply,
            discovered_tools=list(self.tool_to_server.keys()),
            tool_counts_by_server=tool_counts,
            steps=steps,
            total_tokens=total_tokens,
            total_cost=total_cost,
            latency=time.perf_counter() - start_time,
            budget_terminated=budget_terminated,
            budget_hit=budget_hit
        )


async def discover_only(config_path: str):
    """Utility to inspect and print tool discovery without running queries."""
    host = MCPAgentHost(config_path)
    async with AsyncExitStack() as stack:
        tools = await host.connect_and_discover(stack)
        total_count = len(tools)
        print("\n" + "=" * 70)
        print(f"MCP TOOL DISCOVERY REPORT — Config: {Path(config_path).name}")
        print("=" * 70)
        print(f"Total Servers Connected : {len(host.servers_cfg)}")
        print(f"Total Tools Discovered  : {total_count}")
        for srv, srv_tools in host.tools_by_server.items():
            print(f"\nServer: '{srv}' ({len(srv_tools)} tools):")
            for t in srv_tools:
                print(f"  - {t}")
        print("=" * 70 + "\n")
        return host.tools_by_server


def main():
    parser = argparse.ArgumentParser(description="Week 9 MCP Host Agent")
    parser.add_argument("--config", default="mcp_config.json", help="Path to MCP configuration file")
    parser.add_argument("--discover-only", action="store_true", help="Only run tool discovery and report counts")
    parser.add_argument("--ticket", default=None, help="Ticket ID to resolve (e.g., TCK-103)")
    parser.add_argument("--query", default=None, help="Custom query string")
    args = parser.parse_args()

    if args.discover_only:
        asyncio.run(discover_only(args.config))
        return

    # Formulate query
    if args.ticket:
        query = (
            f"Please investigate ticket {args.ticket}. Check its escalation history and touches, "
            f"inspect associated order records, and provide a full status summary."
        )
    elif args.query:
        query = args.query
    else:
        # Default query designed to exercise both Server 1 and Server 2
        query = (
            "Please check the escalation history for ticket TCK-103, verify order ORD-5003 details, "
            "and explain the current status and recommended resolution."
        )

    host = MCPAgentHost(args.config)
    result = asyncio.run(host.run(query))

    print("\n" + "=" * 70)
    print("FINAL AGENT RESOLUTION")
    print("=" * 70)
    print(result.reply)
    print("=" * 70)
    print(f"Discovered Tools : {result.discovered_tools}")
    print(f"Total Tokens     : {result.total_tokens}")
    print(f"Total Cost       : ${result.total_cost:.5f}")
    print(f"Latency          : {result.latency:.2f}s")
    print(f"Steps Taken      : {len(result.steps)}")
    for i, s in enumerate(result.steps, 1):
        print(f"  Step {i}: [{s.server_name}] -> {s.tool_name}({s.tool_input})")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
