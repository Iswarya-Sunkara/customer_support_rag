import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from src.tools import DATA_FILE, _load_data
from src.agent import run_agent, AgentBudgets
from src.llm import get_anthropic_client

data = _load_data()
tickets = data["tickets"]
client = get_anthropic_client()

print(f"Testing {len(tickets)} tickets...")
for t in tickets:
    res = run_agent(t, client=client)
    tools_called = [(s.tool_name, s.tool_input) for s in res.steps if s.tool_name]
    tool_names = [tc[0] for tc in tools_called]
    print(f"{t['ticket_id']}: outcome_pass={res.pass_assertions}, tokens={res.total_tokens}, cost={res.total_cost}, tools={tool_names}")
