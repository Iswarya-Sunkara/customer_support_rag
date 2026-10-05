"""
Week 7 — Tool Definitions for Ticket Resolution Agent and Fixed Workflow.

Each tool strictly implements the Single Responsibility Principle:
1. fetch_order_details: Retrieves financial transaction & order metadata.
2. lookup_refund_policy: Retrieves refund policy duration and rules by category.
3. get_customer_tier: (Third tool) Retrieves customer membership tier and SLA priority.
"""

from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets_week7.json"


# ==============================================================================
# Parameter Enums
# ==============================================================================

class RefundCategoryEnum(str, Enum):
    SUBSCRIPTION = "subscription"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    SERVICES = "services"


class SupportChannelEnum(str, Enum):
    WEB = "web"
    EMAIL = "email"
    API = "api"
    PHONE = "phone"


class CustomerTierEnum(str, Enum):
    STANDARD = "Standard"
    PRIORITY = "Priority"
    ENTERPRISE = "Enterprise"


class OrderStatusEnum(str, Enum):
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"
    NOT_FOUND = "NOT_FOUND"


# ==============================================================================
# Tool 1: fetch_order_details
# ==============================================================================

TOOL_FETCH_ORDER = {
    "name": "fetch_order_details",
    "description": "Retrieve financial transaction record for an order: purchase date, amount paid, item category, and fulfillment status.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The unique order identification code (e.g., 'ORD-5001', 'ORD-9991')."
            }
        },
        "required": ["order_id"],
        "additionalProperties": False
    }
}


# ==============================================================================
# Tool 2: lookup_refund_policy
# ==============================================================================

TOOL_LOOKUP_POLICY = {
    "name": "lookup_refund_policy",
    "description": "Retrieve refund policy terms, window duration in days, and return conditions for a product category.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["subscription", "software", "hardware", "services"],
                "description": "The official product classification enum to check policy rules against."
            }
        },
        "required": ["category"],
        "additionalProperties": False
    }
}


# ==============================================================================
# Tool 3 (New): get_customer_tier
# ==============================================================================

TOOL_GET_CUSTOMER_TIER = {
    "name": "get_customer_tier",
    "description": "Retrieve customer account tier and SLA escalation priority for a customer ID.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The unique customer account identifier (e.g., 'CUST-401')."
            },
            "channel": {
                "type": "string",
                "enum": ["web", "email", "api", "phone"],
                "description": "The inbound communication channel used by the customer."
            }
        },
        "required": ["customer_id", "channel"],
        "additionalProperties": False
    }
}

# The complete tool registry exposed to the LLM agent (Baseline)
TOOLS_REGISTRY = [
    TOOL_FETCH_ORDER,
    TOOL_LOOKUP_POLICY,
    TOOL_GET_CUSTOMER_TIER
]


# ==============================================================================
# Single Mitigation: Tighter Tool Descriptions & Mandatory Precondition Enforced
# ==============================================================================

TOOL_FETCH_ORDER_MITIGATED = {
    "name": "fetch_order_details",
    "description": (
        "MANDATORY PREREQUISITE TOOL: Retrieve official financial transaction record for an order "
        "(purchase date, amount paid, item category, and fulfillment status). "
        "You MUST ALWAYS call this tool first for every ticket to verify the order in the database. "
        "NEVER trust customer claims about order ID, amount, or purchase date in the message text. "
        "Do NOT draft any response before receiving the record from this tool."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "pattern": "^ORD-[0-9]{4}$",
                "description": "The unique 8-character order code (e.g., 'ORD-5001', 'ORD-9991'). Must match ORD-XXXX format."
            }
        },
        "required": ["order_id"],
        "additionalProperties": False
    }
}

TOOL_LOOKUP_POLICY_MITIGATED = {
    "name": "lookup_refund_policy",
    "description": (
        "Retrieve refund policy terms, window duration in days, and return conditions for a product category. "
        "PREREQUISITE: Only call this tool AFTER verifying that an order exists in fetch_order_details. "
        "Do NOT call this tool if the order status is NOT_FOUND or already REFUNDED."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["subscription", "software", "hardware", "services"],
                "description": "The official product classification enum to check policy rules against."
            }
        },
        "required": ["category"],
        "additionalProperties": False
    }
}

# The mitigated tool registry enforcing tighter descriptions & pre-conditions
MITIGATED_TOOLS_REGISTRY = [
    TOOL_FETCH_ORDER_MITIGATED,
    TOOL_LOOKUP_POLICY_MITIGATED,
    TOOL_GET_CUSTOMER_TIER
]


def validate_tool_call_arguments(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates whether tool call arguments conform to schema regex and enums.
    Returns {'valid': bool, 'errors': List[str]}.
    """
    import re
    errors = []
    if name == "fetch_order_details":
        order_id = str(arguments.get("order_id", "")).strip().upper()
        if not order_id:
            errors.append("Missing required argument 'order_id'")
        elif not re.match(r"^ORD-\d{4}$", order_id):
            errors.append(f"Invalid order_id format '{order_id}': expected ORD-XXXX")
    elif name == "lookup_refund_policy":
        category = str(arguments.get("category", "")).strip().lower()
        valid_cats = [c.value for c in RefundCategoryEnum]
        if not category:
            errors.append("Missing required argument 'category'")
        elif category not in valid_cats:
            errors.append(f"Invalid category '{category}': must be one of {valid_cats}")
    elif name == "get_customer_tier":
        customer_id = str(arguments.get("customer_id", "")).strip().upper()
        channel = str(arguments.get("channel", "")).strip().lower()
        valid_channels = [ch.value for ch in SupportChannelEnum]
        if not customer_id:
            errors.append("Missing required argument 'customer_id'")
        elif not re.match(r"^CUST-\d{3}$", customer_id):
            errors.append(f"Invalid customer_id format '{customer_id}': expected CUST-XXX")
        if channel and channel not in valid_channels:
            errors.append(f"Invalid channel '{channel}': must be one of {valid_channels}")
    else:
        errors.append(f"Unknown tool name '{name}'")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }



# ==============================================================================
# Tool Implementation Functions
# ==============================================================================

def _load_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Mock database file not found at {DATA_FILE}")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def fetch_order_details(order_id: str) -> Dict[str, Any]:
    """
    Looks up financial order details by order_id.
    Returns transaction record or a structured NOT_FOUND payload.
    """
    data = _load_data()
    clean_id = (order_id or "").strip().upper()
    order = data.get("orders", {}).get(clean_id)
    if order:
        return {
            "found": True,
            "status": order["status"],
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "item": order["item"],
            "category": order["category"],
            "amount": float(order["amount"]),
            "days_since_purchase": int(order["days_since_purchase"]),
            "refunded_date": order.get("refunded_date")
        }
    return {
        "found": False,
        "status": OrderStatusEnum.NOT_FOUND.value,
        "order_id": clean_id,
        "error": f"Order {clean_id} was not found in billing transaction records."
    }


def lookup_refund_policy(category: str) -> Dict[str, Any]:
    """
    Looks up refund window duration and rules for a category enum.
    """
    data = _load_data()
    cat_lower = (category or "").strip().lower()
    policy = data.get("policies", {}).get(cat_lower)
    if policy:
        return {
            "category": policy["category"],
            "window_days": int(policy["window_days"]),
            "rules": policy["rules"],
            "found": True
        }
    # Fallback default policy
    return {
        "category": cat_lower,
        "window_days": 30,
        "rules": "Default standard 30-day refund window applies.",
        "found": False
    }


def get_customer_tier(customer_id: str, channel: str = "web") -> Dict[str, Any]:
    """
    Looks up customer account tier and SLA escalation flag.
    """
    data = _load_data()
    clean_id = (customer_id or "").strip().upper()
    cust = data.get("customers", {}).get(clean_id)
    if cust:
        tier = cust.get("tier", "Standard")
        return {
            "customer_id": cust["customer_id"],
            "name": cust["name"],
            "tier": tier,
            "channel": channel,
            "is_priority": (tier == CustomerTierEnum.PRIORITY.value),
            "loyalty_years": cust.get("loyalty_years", 1),
            "found": True
        }
    return {
        "customer_id": clean_id,
        "name": "Customer",
        "tier": CustomerTierEnum.STANDARD.value,
        "channel": channel,
        "is_priority": False,
        "loyalty_years": 0,
        "found": False
    }


def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a tool call by name and validates arguments.
    """
    if name == "fetch_order_details":
        return fetch_order_details(order_id=arguments.get("order_id", ""))
    elif name == "lookup_refund_policy":
        return lookup_refund_policy(category=arguments.get("category", "subscription"))
    elif name == "get_customer_tier":
        return get_customer_tier(
            customer_id=arguments.get("customer_id", ""),
            channel=arguments.get("channel", "web")
        )
    else:
        return {"error": f"Unknown tool: '{name}'"}
