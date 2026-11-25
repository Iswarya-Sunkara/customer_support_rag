import urllib.request
import json

# Test that server endpoints are responding
summary_resp = urllib.request.urlopen("http://127.0.0.1:8050/api/week12/summary")
summary_data = json.loads(summary_resp.read().decode('utf-8'))
print("Summary endpoint status:", summary_data.get("status"))
print("Gate status:", summary_data.get("gate_status"))
print("Numbers that moved count:", len(summary_data.get("numbers_that_moved", [])))
print("Taxonomy count:", len(summary_data.get("taxonomy_integrated", [])))
print("10x plan:", summary_data.get("ten_x_plan", {}).get("bottleneck"))

# Test live ticket run
req = urllib.request.Request(
    "http://127.0.0.1:8050/api/week12/run-ticket",
    data=json.dumps({
        "ticket_id": "TKT-84920",
        "customer_id": "CUST-401",
        "order_id": "ORD-5001",
        "question": "Hi, I was charged $49 for Cloudflare Pro renewal 8 days ago under ORD-5001. Can I get a full refund to my card?"
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
ticket_resp = urllib.request.urlopen(req)
ticket_data = json.loads(ticket_resp.read().decode('utf-8'))
print("Ticket run status:", ticket_data.get("status"))
print("Ticket resolution status:", ticket_data.get("ticket_result", {}).get("status"))
print("Policy cited:", ticket_data.get("ticket_result", {}).get("policy_cited"))

