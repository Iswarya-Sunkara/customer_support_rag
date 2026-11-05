import urllib.request
import json

url = "http://127.0.0.1:8050/api/week12/run-ticket"
payload = {
    "ticket_id": "TKT-84920",
    "customer_id": "CUST-401",
    "order_id": "ORD-5001",
    "question": "Hi, I was charged $49 for Cloudflare Pro renewal 8 days ago under ORD-5001. Can I get a full refund to my card?"
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("API Status:", res.get("status"))
        t_res = res.get("ticket_result", {})
        print("Ticket Status:", t_res.get("status"))
        print("Policy Cited:", t_res.get("policy_cited"))
        print("Entitlement Checked:", t_res.get("entitlement_checked"))
        print("Cost USD:", t_res.get("cost_usd"))
        print("Trace ID:", t_res.get("trace_id"))
except Exception as e:
    print("Error:", e)

