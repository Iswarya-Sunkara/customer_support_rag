import urllib.request
import json

req = urllib.request.Request(
    "http://127.0.0.1:8050/api/week12/run-ticket",
    data=json.dumps({
        "ticket_id": "TKT-99120",
        "customer_id": "CUST-408",
        "order_id": None,
        "question": "Urgent: I see an unauthorized fraudulent charge and have initiated a bank chargeback dispute. Refund this immediately or I will file an FTC complaint!"
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)

resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode('utf-8'))
res = data.get("ticket_result", {})
print("Ticket 1b Status:", res.get("status"))
print("Reply excerpt:", res.get("reply")[:120])
print("Policy cited:", res.get("policy_cited"))
print("Trace id:", res.get("trace_id"))

