"""
Week 9 Bonus Challenge — Unified MCP Gateway Process

Features:
1. SINGLE FRONT DOOR: The agent connects to this gateway process as its single MCP entrypoint.
2. FAN-OUT ARCHITECTURE: Aggregates capabilities from both Server 1 (rag-support) and Server 2 (ticket-history).
3. UNIFIED AUDIT LOGGING: Every tool call is logged to results/mcp_audit.log in a single structured line
   containing (timestamp, caller, tool, ticket_id, status, token_scope).
4. TOKEN-SCOPED PERMISSIONS & RECOVERABLE DENIAL:
   Scopes tokens (e.g. 'tier1-basic' vs 'supervisor-admin').
   Denies 'lookup_ticket_history' when caller lacks 'ticket:history:read' scope,
   and returns a structured, recoverable denial that reaches the model cleanly.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastmcp import FastMCP

# Initialize Unified Gateway MCP Server
gateway = FastMCP("mcp-unified-gateway")

AUDIT_LOG_FILE = _REPO_ROOT / "results" / "mcp_audit.log"
AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Caller token configuration (can be passed via environment or default to restricted tier1)
CALLER_ID = os.getenv("MCP_CALLER_ID", "agent-session-401")
CALLER_TOKEN = os.getenv("MCP_CALLER_TOKEN", "token-tier1-support")

# Token Permissions Map
TOKEN_SCOPES = {
    "token-tier1-support": ["orders:read", "policies:read", "customers:read", "tickets:read_basic"],
    "token-supervisor-admin": ["orders:read", "policies:read", "customers:read", "tickets:read_basic", "ticket:history:read"]
}


def _write_audit_line(caller: str, tool: str, ticket_id: Optional[str], status: str, scope: str, details: Optional[str] = None):
    """Writes a single immutable audit line to results/mcp_audit.log."""
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caller": caller,
        "tool": tool,
        "ticket_id": ticket_id or "N/A",
        "status": status,
        "token_scope": scope,
        "details": details or ""
    }
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_entry) + "\n")
    # Also log to stderr for live monitoring
    print(f"[GATEWAY AUDIT] {json.dumps(audit_entry)}", file=sys.stderr)


# ==============================================================================
# Downstream Delegations with Audit Logging and Scoped Access Control
# ==============================================================================

@gateway.tool()
def fetch_order_details(order_id: str) -> str:
    """Retrieve official billing records for an order ID (routed via Gateway to Server 1)."""
    import src.mcp_rag_server as srv1
    caller_token = os.getenv("MCP_CALLER_TOKEN", CALLER_TOKEN)
    scopes = TOKEN_SCOPES.get(caller_token, [])

    _write_audit_line(
        caller=CALLER_ID,
        tool="fetch_order_details",
        ticket_id=order_id,
        status="ALLOWED",
        scope="orders:read"
    )
    return srv1.fetch_order_details(order_id)


@gateway.tool()
def lookup_refund_policy(category: str) -> str:
    """Retrieve refund terms and return conditions for a category (routed via Gateway to Server 1)."""
    import src.mcp_rag_server as srv1
    _write_audit_line(
        caller=CALLER_ID,
        tool="lookup_refund_policy",
        ticket_id=None,
        status="ALLOWED",
        scope="policies:read"
    )
    return srv1.lookup_refund_policy(category)


@gateway.tool()
def get_customer_tier(customer_id: str, channel: str = "web") -> str:
    """Retrieve customer account membership tier (routed via Gateway to Server 1)."""
    import src.mcp_rag_server as srv1
    _write_audit_line(
        caller=CALLER_ID,
        tool="get_customer_tier",
        ticket_id=customer_id,
        status="ALLOWED",
        scope="customers:read"
    )
    return srv1.get_customer_tier(customer_id, channel)


@gateway.tool()
def get_ticket_details(ticket_id: str) -> str:
    """Retrieve basic ticket intake metadata (routed via Gateway to Server 2)."""
    import src.mcp_ticket_history_server as srv2
    _write_audit_line(
        caller=CALLER_ID,
        tool="get_ticket_details",
        ticket_id=ticket_id,
        status="ALLOWED",
        scope="tickets:read_basic"
    )
    return srv2.get_ticket_details(ticket_id)


@gateway.tool()
def lookup_ticket_history(ticket_id: str) -> str:
    """Retrieve escalation history and prior touches for a support ticket (routed via Gateway to Server 2).

    RBAC POLICY: Requires elevated scope 'ticket:history:read'.
    """
    caller_token = os.getenv("MCP_CALLER_TOKEN", CALLER_TOKEN)
    scopes = TOKEN_SCOPES.get(caller_token, [])

    # Token Scope Check
    if "ticket:history:read" not in scopes:
        # Permission Denied -> Write audit line
        _write_audit_line(
            caller=CALLER_ID,
            tool="lookup_ticket_history",
            ticket_id=ticket_id,
            status="DENIED",
            scope=caller_token,
            details="Missing required scope 'ticket:history:read'"
        )
        # Return structured recoverable denial to the model
        return json.dumps({
            "status": "denied",
            "recoverable": True,
            "error_code": "PERMISSION_DENIED",
            "caller": CALLER_ID,
            "required_scope": "ticket:history:read",
            "assigned_scopes": scopes,
            "message": (
                f"PERMISSION DENIED: Caller '{CALLER_ID}' lacks required scope 'ticket:history:read'. "
                f"Escalation history for ticket '{ticket_id}' is restricted to supervisory roles. "
                "Recovery Guidance: Proceed with standard customer inquiry resolution using basic ticket details "
                "or request token elevation from sec-ops@company.internal."
            )
        }, indent=2)

    # Allowed -> Forward to downstream Server 2
    import src.mcp_ticket_history_server as srv2
    _write_audit_line(
        caller=CALLER_ID,
        tool="lookup_ticket_history",
        ticket_id=ticket_id,
        status="ALLOWED",
        scope="ticket:history:read"
    )
    return srv2.lookup_ticket_history(ticket_id)


if __name__ == "__main__":
    gateway.run(show_banner=False)
