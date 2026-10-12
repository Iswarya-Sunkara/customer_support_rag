"""
Week 9 — Server 1: Support RAG & Tool Server (Host App Capabilities)
Exposes deterministic customer support tools over the Model Context Protocol (MCP) via stdio.

Tools exposed (3 tools):
1. fetch_order_details: Retrieve financial transaction records with prompt-guided docstring & recoverable errors.
2. lookup_refund_policy: Retrieve refund policy duration and rules by product category.
3. get_customer_tier: Retrieve customer account tier and SLA escalation flag.

ARCHITECTURAL PRINCIPLE:
This server exposes deterministic capabilities only. No LLM call runs inside this server.
The model runs exclusively on the host agent side.
"""

import json
from pathlib import Path
import re
import sys
from typing import Any, Dict

from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("rag-support-server")

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets_week8.json"


def _load_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        fallback = Path(__file__).resolve().parent.parent / "data" / "tickets_week7.json"
        if fallback.exists():
            return json.loads(fallback.read_text(encoding="utf-8"))
        raise FileNotFoundError(f"Mock database file not found at {DATA_FILE}")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


# ==============================================================================
# Tool 1: fetch_order_details (Rewritten Docstring-as-Prompt & Recoverable Error)
# ==============================================================================

@mcp.tool()
def fetch_order_details(order_id: str) -> str:
    """Retrieve official financial billing records for an order ID.

    PROMPT GUIDANCE & PRECONDITIONS FOR THE CALLING AGENT:
    - You MUST provide an order_id string. Valid IDs strictly follow the format 'ORD-nnnn' (e.g. 'ORD-5001').
    - ALWAYS invoke this tool BEFORE making any refund decision or policy lookup to verify purchase validity.
    - If this tool returns a recoverable error, do NOT hallucinate transaction details.
      Instead, ask the customer to confirm their 8-character order ID or provide payment receipt proof.
    """
    clean_id = (order_id or "").strip().upper()
    data = _load_data()
    orders = data.get("orders", {})

    # Validation: Format checking for recoverable error
    if not clean_id or not re.match(r"^ORD-\d{4}$", clean_id):
        return json.dumps({
            "status": "error",
            "recoverable": True,
            "error_code": "INVALID_ORDER_ID_FORMAT",
            "message": (
                f"Order ID '{clean_id}' is malformed. "
                "Order IDs must strictly follow the format 'ORD-nnnn' (e.g., 'ORD-5001', 'ORD-5002'). "
                "Please verify the ID with the customer or check the transaction receipt."
            ),
            "expected_pattern": "^ORD-[0-9]{4}$"
        }, indent=2)

    order = orders.get(clean_id)
    if order:
        return json.dumps({
            "status": "success",
            "found": True,
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "item": order["item"],
            "category": order["category"],
            "amount": float(order["amount"]),
            "days_since_purchase": int(order["days_since_purchase"]),
            "order_status": order.get("status", "COMPLETED"),
            "refunded_date": order.get("refunded_date")
        }, indent=2)

    # Recoverable error for unrecorded order ID
    return json.dumps({
        "status": "error",
        "recoverable": True,
        "error_code": "ORDER_NOT_FOUND",
        "message": (
            f"Order '{clean_id}' was not found in billing transaction records. "
            "Valid order IDs follow format 'ORD-nnnn'. "
            "Action required: Ask customer to verify their order number from confirmation email, "
            "or request proof of payment for manual billing reconciliation."
        ),
        "searched_id": clean_id
    }, indent=2)


# ==============================================================================
# Tool 2: lookup_refund_policy
# ==============================================================================

@mcp.tool()
def lookup_refund_policy(category: str) -> str:
    """Retrieve refund terms, window duration in days, and return conditions for a product category.

    Categories:
    - 'subscription': Cloud subscriptions (30-day window)
    - 'software': Digital licenses (30-day window)
    - 'hardware': Physical keys and hardware (14-day window)
    - 'services': Onboarding & consulting (30-day window)
    """
    clean_cat = (category or "").strip().lower()
    data = _load_data()
    policies = data.get("policies", {})

    policy = policies.get(clean_cat)
    if policy:
        return json.dumps({
            "status": "success",
            "category": policy["category"],
            "window_days": int(policy["window_days"]),
            "rules": policy["rules"],
            "found": True
        }, indent=2)

    return json.dumps({
        "status": "error",
        "recoverable": True,
        "error_code": "UNKNOWN_CATEGORY",
        "message": f"Category '{category}' not recognized. Allowed categories: ['subscription', 'software', 'hardware', 'services'].",
        "default_fallback": "Standard 30-day refund window applies."
    }, indent=2)


# ==============================================================================
# Tool 3: get_customer_tier
# ==============================================================================

@mcp.tool()
def get_customer_tier(customer_id: str, channel: str = "web") -> str:
    """Retrieve customer account membership tier (Standard vs Priority) and SLA routing.

    - customer_id: Customer identifier (e.g. 'CUST-401')
    - channel: Inbound communication channel ('web', 'email', 'phone', 'api')
    """
    clean_id = (customer_id or "").strip().upper()
    data = _load_data()
    customers = data.get("customers", {})

    cust = customers.get(clean_id)
    if cust:
        tier = cust.get("tier", "Standard")
        return json.dumps({
            "status": "success",
            "customer_id": cust["customer_id"],
            "name": cust["name"],
            "tier": tier,
            "channel": channel,
            "is_priority": (tier == "Priority"),
            "loyalty_years": cust.get("loyalty_years", 1),
            "found": True
        }, indent=2)

    return json.dumps({
        "status": "warning",
        "customer_id": clean_id,
        "name": "Guest Customer",
        "tier": "Standard",
        "channel": channel,
        "is_priority": False,
        "loyalty_years": 0,
        "found": False,
        "message": f"Customer ID '{clean_id}' not found in CRM. Defaulting to Standard tier."
    }, indent=2)


if __name__ == "__main__":
    # Run stdio MCP server cleanly
    mcp.run(show_banner=False)
