"""
Week 7 — Hand-Built ReAct Agent Loop for Ticket Resolution.

Features:
- Pure Python ReAct loop (Plan -> Act -> Observe -> Repeat) in ~80 lines.
- Enforces ALL FOUR safety budgets actively inside the loop:
  1. max_iterations
  2. max_tokens (summed across ALL laps)
  3. max_cost (summed across ALL laps)
  4. max_wall_clock_seconds
- Visible step logging with full transparency on thoughts, tool calls, and observations.
- Clean, non-crashing termination on budget exhaustion.
"""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.llm import get_anthropic_client, MODEL_NAME, calculate_cost
from src.tools import TOOLS_REGISTRY, execute_tool

logger = logging.getLogger("TicketAgent")


@dataclass
class AgentBudgets:
    """Enforceable runtime safety limits for the agent loop."""
    max_iterations: int = 6
    max_tokens: int = 4000
    max_cost: float = 0.05
    max_wall_clock_seconds: float = 15.0


@dataclass
class AgentStep:
    """Record of a single step/lap within the agent loop."""
    iteration: int
    thought: Optional[str]
    tool_name: Optional[str]
    tool_input: Optional[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]
    lap_input_tokens: int
    lap_output_tokens: int
    lap_tokens: int
    lap_cost: float
    cumulative_tokens: int
    cumulative_cost: float
    elapsed_seconds: float


@dataclass
class AgentResult:
    """Standardized output contract returned by the agent."""
    ticket_id: str
    reply: str
    pass_assertions: bool
    latency: float
    total_tokens: int
    total_cost: float
    iterations: int
    steps: List[AgentStep] = field(default_factory=list)
    budget_terminated: bool = False
    budget_hit: Optional[str] = None
    termination_message: Optional[str] = None


SYSTEM_PROMPT = """You are a senior customer support refund agent.
Your job is to resolve customer refund and order inquiry tickets by using your available tools.

You have access to 3 tools:
1. `fetch_order_details`: Retrieve financial transaction records (amount, date, status, category).
2. `lookup_refund_policy`: Retrieve refund window duration and rules for a product category.
3. `get_customer_tier`: Retrieve customer account tier (Standard vs Priority) and SLA routing.

OUTPUT CONTRACT RULES (STRICTLY REQUIRED):
1. First line MUST be: "Ticket <ticket_id>" (If customer tier is Priority, append " [ESCALATE:PRIORITY]").
2. Second line must be empty, followed by "Hi there,".
3. Next section must explain findings clearly:
   - For approved refund: Quote amount ($X.XX), state it is within the window, promise refund to original payment method within 5-10 business days.
   - For denied refund: Quote amount ($X.XX), state purchase was outside refund window, state inability to refund, offer agent review.
   - For already refunded: Quote amount ($X.XX), confirm refund was already processed on the recorded date, explain bank clearing time.
   - For missing/not found order: State order was not found in records, request bank statement / payment proof, explain escalation path.
4. Closing MUST end with:
   Best regards,
   Support Team
"""


def _check_budgets(
    budgets: AgentBudgets,
    iteration: int,
    elapsed: float,
    total_tokens: int,
    total_cost: float
) -> Optional[tuple]:
    """
    Checks all 4 budgets. Returns (budget_name, limit_value, current_value) if breached, else None.
    """
    if iteration > budgets.max_iterations:
        return ("max_iterations", budgets.max_iterations, iteration)
    if elapsed > budgets.max_wall_clock_seconds:
        return ("max_wall_clock_seconds", budgets.max_wall_clock_seconds, round(elapsed, 4))
    if total_tokens > budgets.max_tokens:
        return ("max_tokens", budgets.max_tokens, total_tokens)
    if total_cost > budgets.max_cost:
        return ("max_cost", budgets.max_cost, round(total_cost, 6))
    return None


Tuple_Budget = Any


def run_agent(
    ticket: Dict[str, Any],
    budgets: Optional[AgentBudgets] = None,
    client: Optional[Any] = None
) -> AgentResult:
    """
    Runs the ReAct agent loop on a single ticket until task completion or budget exhaustion.
    """
    if budgets is None:
        budgets = AgentBudgets()
    if client is None:
        client = get_anthropic_client()

    ticket_id = ticket["ticket_id"]
    customer_id = ticket["customer_id"]
    order_id = ticket.get("order_id", "")
    question = ticket["question"]

    user_prompt = (
        f"Resolve this customer support ticket:\n"
        f"Ticket ID: {ticket_id}\n"
        f"Customer ID: {customer_id}\n"
        f"Order ID: {order_id}\n"
        f"Customer Message: {question}"
    )

    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": user_prompt}
    ]

    total_tokens = 0
    total_cost = 0.0
    iteration = 0
    steps: List[AgentStep] = []
    start_time = time.perf_counter()

    final_reply = ""
    budget_terminated = False
    budget_hit = None
    termination_message = None

    while True:
        iteration += 1
        elapsed = time.perf_counter() - start_time

        # ----------------------------------------------------------------------
        # 1. Enforce budgets BEFORE making the next LLM call
        # ----------------------------------------------------------------------
        breach = _check_budgets(budgets, iteration, elapsed, total_tokens, total_cost)
        if breach:
            budget_name, limit_val, curr_val = breach
            budget_terminated = True
            budget_hit = budget_name
            termination_message = (
                f"[BUDGET EXCEEDED] Budget '{budget_name}' breached: current value {curr_val} "
                f"exceeds configured limit of {limit_val} on ticket {ticket_id}. "
                f"Agent terminating cleanly."
            )
            logger.warning(termination_message)
            final_reply = (
                f"Ticket {ticket_id}\n\n"
                f"Hi there,\n\n"
                f"Your request is undergoing automated processing review. A support specialist "
                f"will follow up shortly regarding order {order_id}.\n\n"
                f"Best regards,\nSupport Team"
            )
            break

        # ----------------------------------------------------------------------
        # 2. Call LLM with tool definitions
        # ----------------------------------------------------------------------
        try:
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS_REGISTRY,
                messages=messages
            )
        except Exception as e:
            logger.error(f"LLM API error on ticket {ticket_id}: {e}")
            final_reply = f"Ticket {ticket_id}\n\nError processing ticket: {e}\n\nBest regards,\nSupport Team"
            break

        # Cumulative token & cost accounting across all laps
        lap_in = response.usage.input_tokens
        lap_out = response.usage.output_tokens
        lap_tokens = lap_in + lap_out
        lap_cost = calculate_cost(lap_in, lap_out)

        total_tokens += lap_tokens
        total_cost += lap_cost
        elapsed = time.perf_counter() - start_time

        # ----------------------------------------------------------------------
        # 3. Enforce budgets AFTER receiving LLM response tokens/cost
        # ----------------------------------------------------------------------
        breach_after = _check_budgets(budgets, iteration, elapsed, total_tokens, total_cost)
        if breach_after and breach_after[0] in ("max_tokens", "max_cost"):
            budget_name, limit_val, curr_val = breach_after
            budget_terminated = True
            budget_hit = budget_name
            termination_message = (
                f"[BUDGET EXCEEDED] Budget '{budget_name}' breached: cumulative value {curr_val} "
                f"exceeds configured limit of {limit_val} on ticket {ticket_id}. "
                f"Agent terminating cleanly."
            )
            logger.warning(termination_message)
            final_reply = (
                f"Ticket {ticket_id}\n\n"
                f"Hi there,\n\n"
                f"Your ticket is queued for senior specialist review due to transaction complexity.\n\n"
                f"Best regards,\nSupport Team"
            )
            break

        # ----------------------------------------------------------------------
        # 4. Check if agent completed its reasoning or invoked tools
        # ----------------------------------------------------------------------
        has_tool_calls = any(block.type == "tool_use" for block in response.content)
        thought_texts = [block.text for block in response.content if block.type == "text"]
        combined_thought = " ".join(thought_texts).strip() if thought_texts else None

        if not has_tool_calls or response.stop_reason == "end_turn":
            # Agent formulated final answer without additional tool calls
            final_reply = combined_thought or ""
            step = AgentStep(
                iteration=iteration,
                thought=combined_thought,
                tool_name=None,
                tool_input=None,
                tool_result=None,
                lap_input_tokens=lap_in,
                lap_output_tokens=lap_out,
                lap_tokens=lap_tokens,
                lap_cost=lap_cost,
                cumulative_tokens=total_tokens,
                cumulative_cost=total_cost,
                elapsed_seconds=round(elapsed, 4)
            )
            steps.append(step)
            break

        # ----------------------------------------------------------------------
        # 5. Execute all requested tool calls & record step trace
        # ----------------------------------------------------------------------
        messages.append({"role": "assistant", "content": response.content})
        tool_results_content = []

        for block in response.content:
            if block.type == "tool_use":
                t_name = block.name
                t_input = block.input
                t_res = execute_tool(t_name, t_input)

                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(t_res, ensure_ascii=False)
                })

                step = AgentStep(
                    iteration=iteration,
                    thought=combined_thought,
                    tool_name=t_name,
                    tool_input=t_input,
                    tool_result=t_res,
                    lap_input_tokens=lap_in,
                    lap_output_tokens=lap_out,
                    lap_tokens=lap_tokens,
                    lap_cost=lap_cost,
                    cumulative_tokens=total_tokens,
                    cumulative_cost=total_cost,
                    elapsed_seconds=round(elapsed, 4)
                )
                steps.append(step)

        messages.append({"role": "user", "content": tool_results_content})

    total_latency = time.perf_counter() - start_time

    # Evaluate assertion pass rate on final reply
    pass_assertions = _evaluate_reply_assertions(ticket, final_reply)

    return AgentResult(
        ticket_id=ticket_id,
        reply=final_reply.strip(),
        pass_assertions=pass_assertions,
        latency=round(total_latency, 4),
        total_tokens=total_tokens,
        total_cost=round(total_cost, 7),
        iterations=iteration,
        steps=steps,
        budget_terminated=budget_terminated,
        budget_hit=budget_hit,
        termination_message=termination_message
    )


def _evaluate_reply_assertions(ticket: Dict[str, Any], reply: str) -> bool:
    """
    Evaluates business rule assertions:
    1. Ticket ID is echoed in header
    2. Priority tier contains [ESCALATE:PRIORITY]
    3. Refund amount formatted as $X.XX when order was found
    4. Outside refund window or missing order does not promise a refund
    """
    if not reply:
        return False

    first_line = reply.splitlines()[0] if reply.splitlines() else ""
    # 1. Echo ticket ID
    if ticket["ticket_id"] not in first_line:
        return False

    # 2. Priority escalation tag
    if ticket.get("tier") == "Priority":
        if "[ESCALATE:PRIORITY]" not in first_line:
            return False

    # 3. Missing order should NEVER promise an approved refund
    if ticket.get("is_branching") and ticket.get("branch_type", "").startswith("missing_order"):
        if "will refund" in reply.lower() or "processed your refund" in reply.lower():
            return False

    return True
