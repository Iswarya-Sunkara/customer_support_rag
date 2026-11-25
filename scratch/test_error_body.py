import urllib.request
import json

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

try:
    resp = urllib.request.urlopen(req)
    print("Success:", resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error code:", e.code)
    print("Error body:", e.read().decode('utf-8'))
except Exception as e:
    print("Other error:", e)

