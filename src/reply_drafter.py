"""
Week 6 — Ticket reply drafter.

Wraps a RAG answer (live or replayed from a logged trace) into the reply an
agent would send on the ticket. Business rules that must never be left to a
model live here as plain code:

  * the ticket ID is echoed on the first line
  * Priority-tier tickets carry the [ESCALATE:PRIORITY] tag
  * refund requests quote the amount as a number and are only promised
    inside the 30-day refund window
"""

REFUND_WINDOW_DAYS = 30
ESCALATION_TAG = "[ESCALATE:PRIORITY]"


def _refund_paragraph(refund_request):
    amount = f"${refund_request['amount']:.2f}"
    days = refund_request["days_since_purchase"]
    if days <= REFUND_WINDOW_DAYS:
        return (
            f"Refund: your purchase was {days} days ago, which is inside our "
            f"{REFUND_WINDOW_DAYS}-day refund window. We will refund {amount} to your "
            f"original payment method within 5-10 business days."
        )
    return (
        f"Refund: your purchase was {days} days ago, which is outside our "
        f"{REFUND_WINDOW_DAYS}-day refund window, so we are unable to refund the "
        f"{amount} charge. An agent can review other options with you on this ticket."
    )


def draft_reply(ticket, rag_answer):
    """ticket: dict with ticket_id, tier, question, optional refund_request.
    rag_answer: the answer text produced by the RAG engine (kept verbatim)."""
    header = f"Ticket {ticket['ticket_id']}"
    if ticket.get("tier") == "Priority":
        header += f" {ESCALATION_TAG}"

    parts = [
        header,
        "",
        "Hi there,",
        "",
        "Thanks for contacting support. Here is what we found for your question:",
        "",
        rag_answer.strip(),
    ]
    if ticket.get("refund_request"):
        parts += ["", _refund_paragraph(ticket["refund_request"])]
    parts += ["", "Best regards,", "Support Team"]
    return "\n".join(parts)
