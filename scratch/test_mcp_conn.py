import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_code = """
from fastmcp import FastMCP
m = FastMCP("mini")

@m.tool()
def echo(msg: str) -> str:
    return f"ECHO: {msg}"

if __name__ == "__main__":
    m.run()
"""
    scratch_server = Path("scratch/mini_server.py")
    scratch_server.parent.mkdir(parents=True, exist_ok=True)
    scratch_server.write_text(server_code, encoding="utf-8")

    python_exe = sys.executable

    server_params = StdioServerParameters(
        command=python_exe,
        args=["scratch/mini_server.py"],
        env=None
    )

    print("Connecting to mini server via stdio...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            init_res = await session.initialize()
            print("Initialized successfully! Server name:", init_res.server_info.name)
            
            tool_list = await session.list_tools()
            tool_names = [t.name for t in tool_list.tools]
            print("Discovered tools:", tool_names)
            
            call_res = await session.call_tool("echo", {"msg": "hello MCP"})
            print("Tool call result:", [c.text for c in call_res.content])

if __name__ == "__main__":
    asyncio.run(main())
