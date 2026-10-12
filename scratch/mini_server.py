
from fastmcp import FastMCP
m = FastMCP("mini")

@m.tool()
def echo(msg: str) -> str:
    return f"ECHO: {msg}"

if __name__ == "__main__":
    m.run()
