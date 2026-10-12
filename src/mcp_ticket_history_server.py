"""
Week 9 — Server 2: Ticket History & Escalation MCP Server (Support Ops Server)
Stood up by Support Operations to expose ticket escalation history and operational records.

Tools exposed (2 tools):
1. lookup_ticket_history: Retrieve escalation history, agent touches, and escalation status by ticket_id.
2. get_ticket_details: Retrieve initial ticket metadata, customer query, and category classification.

ARCHITECTURAL PRINCIPLE:
The server exposes support operations data over standard MCP stdio.
The LLM never runs inside this server; all model reasoning occurs inside the host agent.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List

from fastmcp import FastMCP

# Initialize FastMCP Server for Support Ops
mcp = FastMCP("ticket-history-server")

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets_week8.json"


def _get_history_database() -> Dict[str, Dict[str, Any]]:
    """In-memory operational database for Support Ops ticket history."""
    return {
        "TCK-101": {
            "ticket_id": "TCK-101",
            "customer_id": "CUST-401",
            "order_id": "ORD-5001",
            "status": "OPEN",
            "escalation_level": "L1",
            "escalated": False,
            "touches": 1,
            "history": [
                {
                    "timestamp": "2026-09-28T14:22:10Z",
                    "agent": "Automated Ingestion",
                    "action": "Ticket created via Web Portal",
                    "note": "Customer submitted refund request for Cloudflare Pro Monthly (ORD-5001)."
                }
            ]
        },
        "TCK-102": {
            "ticket_id": "TCK-102",
            "customer_id": "CUST-402",
            "order_id": "ORD-5002",
            "status": "PENDING_REVIEW",
            "escalation_level": "L1",
            "escalated": False,
            "touches": 2,
            "history": [
                {
                    "timestamp": "2026-09-27T10:11:00Z",
                    "agent": "Automated Ingestion",
                    "action": "Ticket created via Email",
                    "note": "Customer requested refund for annual charge of $199."
                },
                {
                    "timestamp": "2026-09-27T16:45:00Z",
                    "agent": "Agent David",
                    "action": "Policy eligibility check",
                    "note": "Flagged as 45 days since purchase (> 30 days). Awaiting formal policy communication."
                }
            ]
        },
        "TCK-103": {
            "ticket_id": "TCK-103",
            "customer_id": "CUST-403",
            "order_id": "ORD-5003",
            "status": "ESCALATED",
            "escalation_level": "L2_PRIORITY",
            "escalated": True,
            "touches": 3,
            "history": [
                {
                    "timestamp": "2026-09-29T09:15:00Z",
                    "agent": "Automated Ingestion",
                    "action": "Ticket created via Web Portal",
                    "note": "Priority client Nexus Corp requested $250 refund for onboarding consulting under ORD-5003."
                },
                {
                    "timestamp": "2026-09-29T10:00:00Z",
                    "agent": "Agent Sarah",
                    "action": "Escalated to Priority Tier Support",
                    "note": "Customer holds Priority SLA. Escalated to tier 2 for expedited supervisor review."
                },
                {
                    "timestamp": "2026-09-29T11:30:00Z",
                    "agent": "Supervisor Marcus",
                    "action": "Review in progress",
                    "note": "Confirmed services unconsumed. Ready for refund execution approval."
                }
            ]
        },
        "TCK-104": {
            "ticket_id": "TCK-104",
            "customer_id": "CUST-404",
            "order_id": "ORD-5004",
            "status": "RESOLVED",
            "escalation_level": "L1",
            "escalated": False,
            "touches": 2,
            "history": [
                {
                    "timestamp": "2026-09-25T08:00:00Z",
                    "agent": "Automated Ingestion",
                    "action": "Ticket created via Email",
                    "note": "Apex Holdings inquiring about already processed refund."
                },
                {
                    "timestamp": "2026-09-25T09:20:00Z",
                    "agent": "Billing Bot",
                    "action": "Refund confirmation sent",
                    "note": "Provided bank settlement trace ID."
                }
            ]
        },
        "TCK-105": {
            "ticket_id": "TCK-105",
            "customer_id": "CUST-405",
            "order_id": "ORD-9999",
            "status": "PENDING_CUSTOMER",
            "escalation_level": "L1",
            "escalated": False,
            "touches": 2,
            "history": [
                {
                    "timestamp": "2026-09-26T12:00:00Z",
                    "agent": "Automated Ingestion",
                    "action": "Ticket created via Web Portal",
                    "note": "Customer claims charge for non-existent order ORD-9999."
                },
                {
                    "timestamp": "2026-09-26T14:10:00Z",
                    "agent": "Agent Leo",
                    "action": "Information requested",
                    "note": "Requested credit card statement copy from customer."
                }
            ]
        }
    }


# ==============================================================================
# Tool 1: lookup_ticket_history
# ==============================================================================

@mcp.tool()
def lookup_ticket_history(ticket_id: str) -> str:
    """Retrieve the escalation history, prior agent touches, and escalation level for a support ticket.

    Args:
        ticket_id: The unique support ticket code (e.g., 'TCK-101', 'TCK-103').
    """
    clean_id = (ticket_id or "").strip().upper()
    histories = _get_history_database()

    # Recoverable format check
    if not clean_id or not re.match(r"^TCK-\d+$", clean_id):
        return json.dumps({
            "status": "error",
            "recoverable": True,
            "error_code": "INVALID_TICKET_ID_FORMAT",
            "message": (
                f"Ticket ID '{clean_id}' is malformed. "
                "Ticket IDs must follow the format 'TCK-nnn' (e.g. 'TCK-101', 'TCK-103'). "
                "Please verify the ticket identifier before retrying."
            )
        }, indent=2)

    entry = histories.get(clean_id)
    if entry:
        return json.dumps({
            "status": "success",
            "found": True,
            "ticket_id": entry["ticket_id"],
            "customer_id": entry["customer_id"],
            "order_id": entry["order_id"],
            "current_status": entry["status"],
            "escalation_level": entry["escalation_level"],
            "is_escalated": entry["escalated"],
            "total_touches": entry["touches"],
            "audit_trail": entry["history"]
        }, indent=2)

    # Recoverable not found path
    return json.dumps({
        "status": "error",
        "recoverable": True,
        "error_code": "TICKET_NOT_FOUND",
        "message": (
            f"Ticket '{clean_id}' not found in Support Ops database. "
            "Ticket IDs follow format 'TCK-nnn' (e.g. TCK-101, TCK-102). "
            "Action required: Check if ticket was archived or verify ticket ID."
        ),
        "searched_id": clean_id
    }, indent=2)


# ==============================================================================
# Tool 2: get_ticket_details
# ==============================================================================

@mcp.tool()
def get_ticket_details(ticket_id: str) -> str:
    """Retrieve ticket intake metadata, customer message summary, and reported channel.

    Args:
        ticket_id: The unique support ticket code (e.g., 'TCK-101', 'TCK-103').
    """
    clean_id = (ticket_id or "").strip().upper()
    
    # Check underlying tickets file if present
    data = {}
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    tickets_list = data.get("tickets", [])
    matched = next((t for t in tickets_list if t.get("ticket_id") == clean_id), None)
    
    if matched:
        return json.dumps({
            "status": "success",
            "found": True,
            "ticket_id": matched["ticket_id"],
            "customer_id": matched["customer_id"],
            "order_id": matched.get("order_id"),
            "channel": matched.get("channel", "web"),
            "customer_message": matched.get("question", ""),
            "expected_outcome": matched.get("expected_outcome", "")
        }, indent=2)

    # Fallback to in-memory records
    histories = _get_history_database()
    if clean_id in histories:
        h = histories[clean_id]
        return json.dumps({
            "status": "success",
            "found": True,
            "ticket_id": h["ticket_id"],
            "customer_id": h["customer_id"],
            "order_id": h["order_id"],
            "channel": "web",
            "customer_message": f"Inquiry for order {h['order_id']}",
            "expected_outcome": h["status"]
        }, indent=2)

    return json.dumps({
        "status": "error",
        "recoverable": True,
        "error_code": "TICKET_NOT_FOUND",
        "message": f"Ticket '{clean_id}' not found in intake system.",
        "searched_id": clean_id
    }, indent=2)


if __name__ == "__main__":
    # Run stdio MCP server cleanly
    mcp.run(show_banner=False)
