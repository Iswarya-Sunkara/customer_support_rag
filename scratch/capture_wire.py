"""
Script to capture the exact raw JSON-RPC 2.0 wire protocol exchanges:
1. initialize (Request & Response)
2. notifications/initialized (Notification)
3. tools/list (Request & Response)
4. tools/call (Request & Response for lookup_ticket_history)
"""

import json
import subprocess
import sys

def main():
    proc = subprocess.Popen(
        [sys.executable, "src/mcp_ticket_history_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    messages = []

    def send_and_recv(req: dict):
        line = json.dumps(req) + "\n"
        proc.stdin.write(line)
        proc.stdin.flush()
        resp_line = proc.stdout.readline()
        resp = json.loads(resp_line)
        return resp

    # 1. initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "mcp-agent-host",
                "version": "1.0.0"
            }
        }
    }
    init_res = send_and_recv(init_req)
    messages.append({"phase": "1_initialize", "request": init_req, "response": init_res})

    # 2. notifications/initialized
    notif = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    proc.stdin.write(json.dumps(notif) + "\n")
    proc.stdin.flush()
    messages.append({"phase": "2_initialized_notification", "notification": notif})

    # 3. tools/list
    tools_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    tools_res = send_and_recv(tools_req)
    messages.append({"phase": "3_tools_list", "request": tools_req, "response": tools_res})

    # 4. tools/call
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "lookup_ticket_history",
            "arguments": {
                "ticket_id": "TCK-103"
            }
        }
    }
    call_res = send_and_recv(call_req)
    messages.append({"phase": "4_tools_call", "request": call_req, "response": call_res})

    proc.terminate()

    with open("scratch/raw_wire_capture.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

    print("Wire capture complete. Saved to scratch/raw_wire_capture.json")

if __name__ == "__main__":
    main()
