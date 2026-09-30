"""
Week 7 — Fixed Workflow Implementation for Ticket Resolution.

Features:
- Completely linear, hard-coded DAG execution (Step 1 -> Step 2 -> Step 3 -> LLM Draft).
- Zero loop: No `while` loop, no iterative re-prompting, no tool-thrash risk.
- Identical tools, identical model (claude-haiku-4-5), identical input tickets, identical output contract.
- Deterministic branching: Missing orders, already-refunded items, and standard policy checks
  branch explicitly via Python if/else logic rather than LLM guessing.
"""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.llm import get_anthropic_client, MODEL_NAME, calculate_cost
from src.tools import fetch_order_details, lookup_refund_policy, get_customer_tier
from src.agent import _evaluate_reply_assertions

logger = logging.getLogger("FixedWorkflow")


@dataclass
class WorkflowStep:
    """Record of a hard-coded step execution."""
    step_num: int
    step_name: str
    action: str
    payload: Dict[str, Any]
    elapsed_seconds: float


@dataclass
class WorkflowResult:
    """Standardized output contract matching AgentResult."""
    ticket_id: str
    reply: str
    pass_assertions: bool
    latency: float
    total_tokens: int
    total_cost: float
    iterations: int = 1  # Exactly 1 step/pass, no loop
    steps: List[WorkflowStep] = field(default_factory=list)
    budget_terminated: bool = False
    budget_hit: Optional[str] = None
    termination_message: Optional[str] = None


WORKFLOW_DRAFTER_SYSTEM_PROMPT = """You are a senior customer support drafter.
You will receive a ticket with pre-retrieved facts from our backend databases (order record, customer tier, and refund policy).
Your job is to draft the final response to the customer strictly adhering to the output contract.

OUTPUT CONTRACT RULES:
1. First line MUST be: "Ticket <ticket_id>" (If customer tier is Priority, append " [ESCALATE:PRIORITY]").
2. Second line must be empty, followed by "Hi there,".
3. Next section must explain findings clearly based on the retrieved facts:
   - For approved refund: Quote amount ($X.XX), state it is within the window, promise refund to original payment method within 5-10 business days.
   - For denied refund: Quote amount ($X.XX), state purchase was outside refund window, state inability to refund, offer agent review.
   - For already refunded: Quote amount ($X.XX), confirm refund was already processed on the recorded date, explain bank clearing time.
   - For missing/not found order: State order was not found in records, request bank statement / payment proof, explain escalation path.
4. Closing MUST end with:
   Best regards,
   Support Team
"""


def run_workflow(
    ticket: Dict[str, Any],
    client: Optional[Any] = None
) -> WorkflowResult:
    """
    Executes the fixed hardcoded sequence on a ticket.
    """
    if client is None:
        client = get_anthropic_client()

    start_time = time.perf_counter()
    ticket_id = ticket["ticket_id"]
    customer_id = ticket["customer_id"]
    order_id = ticket.get("order_id", "")
    channel = ticket.get("channel", "web")
    question = ticket["question"]

    steps: List[WorkflowStep] = []

    # --------------------------------------------------------------------------
    # Step 1: Deterministic Order Fetch
    # --------------------------------------------------------------------------
    t0 = time.perf_counter()
    order_info = fetch_order_details(order_id=order_id)
    steps.append(WorkflowStep(
        step_num=1,
        step_name="fetch_order_details",
        action=f"Lookup financial record for {order_id}",
        payload=order_info,
        elapsed_seconds=round(time.perf_counter() - t0, 4)
    ))

    # --------------------------------------------------------------------------
    # Step 2: Deterministic Customer Tier Fetch
    # --------------------------------------------------------------------------
    t1 = time.perf_counter()
    customer_info = get_customer_tier(customer_id=customer_id, channel=channel)
    steps.append(WorkflowStep(
        step_num=2,
        step_name="get_customer_tier",
        action=f"Lookup tier and SLA priority for {customer_id}",
        payload=customer_info,
        elapsed_seconds=round(time.perf_counter() - t1, 4)
    ))

    # --------------------------------------------------------------------------
    # Step 3: Hard-coded Branching (Deterministic DAG)
    # --------------------------------------------------------------------------
    t2 = time.perf_counter()
    policy_info = None

    if not order_info.get("found"):
        # Branch 3A: Order Missing / Not Found
        branch_action = "Missing Order Escalation Path (no policy lookup applicable)"
        policy_info = {"status": "NOT_APPLICABLE", "reason": "Order missing from billing database"}
    elif order_info.get("status") == "REFUNDED":
        # Branch 3B: Already Refunded
        branch_action = "Already Refunded Path (transaction previously settled)"
        policy_info = {"status": "ALREADY_SETTLED", "refunded_date": order_info.get("refunded_date")}
    else:
        # Branch 3C: Standard Order -> Lookup Category Policy
        category = order_info.get("category", "subscription")
        policy_info = lookup_refund_policy(category=category)
        branch_action = f"Category Policy Lookup for '{category}'"

    steps.append(WorkflowStep(
        step_num=3,
        step_name="branch_policy_resolution",
        action=branch_action,
        payload=policy_info,
        elapsed_seconds=round(time.perf_counter() - t2, 4)
    ))

    # --------------------------------------------------------------------------
    # Step 4: Single LLM Synthesis Call
    # --------------------------------------------------------------------------
    t3 = time.perf_counter()
    synthesis_prompt = (
        f"Ticket Context:\n"
        f"- Ticket ID: {ticket_id}\n"
        f"- Customer ID: {customer_id}\n"
        f"- Order ID: {order_id}\n"
        f"- Customer Message: {question}\n\n"
        f"Retrieved Facts:\n"
        f"- Customer Record: {json.dumps(customer_info, ensure_ascii=False)}\n"
        f"- Order Record: {json.dumps(order_info, ensure_ascii=False)}\n"
        f"- Policy / Resolution Info: {json.dumps(policy_info, ensure_ascii=False)}\n\n"
        f"Draft the exact response following all output contract rules."
    )

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            system=WORKFLOW_DRAFTER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        in_tokens = response.usage.input_tokens
        out_tokens = response.usage.output_tokens
        total_tokens = in_tokens + out_tokens
        total_cost = calculate_cost(in_tokens, out_tokens)
        reply = next((b.text for b in response.content if b.type == "text"), "").strip()
    except Exception as e:
        logger.error(f"Workflow LLM error on ticket {ticket_id}: {e}")
        reply = f"Ticket {ticket_id}\n\nError processing workflow: {e}\n\nBest regards,\nSupport Team"
        total_tokens = 0
        total_cost = 0.0

    steps.append(WorkflowStep(
        step_num=4,
        step_name="llm_draft_reply",
        action="Single LLM contract synthesis",
        payload={"input_tokens": in_tokens, "output_tokens": out_tokens, "cost": total_cost},
        elapsed_seconds=round(time.perf_counter() - t3, 4)
    ))

    total_latency = time.perf_counter() - start_time
    pass_assertions = _evaluate_reply_assertions(ticket, reply)

    return WorkflowResult(
        ticket_id=ticket_id,
        reply=reply,
        pass_assertions=pass_assertions,
        latency=round(total_latency, 4),
        total_tokens=total_tokens,
        total_cost=round(total_cost, 7),
        iterations=1,
        steps=steps
    )
