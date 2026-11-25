import urllib.request
import json

req = urllib.request.Request(
    "http://127.0.0.1:8050/api/chat",
    data=json.dumps({
        "question": "What should I do if I get credit card error code 51 - Decline when paying my invoice?",
        "mode": "week4"
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)

resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode('utf-8'))
print("Chat status:", resp.status)
print("Answer excerpt:", data.get("answer")[:150])
print("Citations count:", len(data.get("citations", [])))

