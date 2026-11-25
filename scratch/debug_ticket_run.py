import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

import traceback

try:
    from src.integrated_assistant import Tier1DeflectionAssistant
    assistant = Tier1DeflectionAssistant()
    res = assistant.process_ticket({
        "ticket_id": "TKT-84920",
        "customer_id": "CUST-401",
        "order_id": "ORD-5001",
        "question": "Hi, I was charged $49 for Cloudflare Pro renewal 8 days ago under ORD-5001. Can I get a full refund to my card?"
    })
    print("Success status:", res["status"])
    print("Policy cited:", res["policy_cited"])
    print("Entitlement checked:", res["entitlement_checked"])
    print("Trace id:", res["trace_id"])
except Exception as e:
    print("Exception:")
    traceback.print_exc()
