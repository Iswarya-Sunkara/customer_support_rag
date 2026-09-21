"""
Deterministic assertions — criteria that were REMOVED from the LLM judge
(compare judge_v0_all_criteria.txt with judge_v1.txt).

A regex never has an off day and costs nothing, so anything checkable by
string inspection is checked here, not by a model.
"""
import re

REFUND_WINDOW_DAYS = 30
ESCALATION_TAG = "[ESCALATE:PRIORITY]"

# Phrases that commit us to paying money back. The "unable to refund" wording
# used for out-of-window tickets deliberately does not match.
_REFUND_PROMISE = re.compile(
    r"\bwe will refund\b"
    r"|\bwe(?:'ll| will) (?:issue|process) (?:a|your) refund\b"
    r"|\brefund\b[^.]{0,40}?\b(?:has been|will be|is being) (?:issued|processed|approved)\b"
    r"|(?<!not )\beligible for (?:a |your )?(?:full |partial )?refund\b",
    re.IGNORECASE,
)
_MONEY = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)")


def a_ticket_id_echoed(ticket, reply):
    return ticket["ticket_id"] in reply, f"expected {ticket['ticket_id']} in reply"


def a_escalation_tag(ticket, reply):
    has_tag = ESCALATION_TAG in reply
    if ticket.get("tier") == "Priority":
        return has_tag, "Priority ticket missing escalation tag"
    return not has_tag, "non-Priority ticket carries escalation tag"


def a_refund_amount_numeric(ticket, reply):
    rr = ticket.get("refund_request")
    if not rr:
        return True, "n/a"
    amounts = [float(m.replace(",", "")) for m in _MONEY.findall(reply)]
    ok = any(abs(a - rr["amount"]) < 0.005 for a in amounts)
    return ok, f"expected numeric ${rr['amount']:.2f}, found {amounts}"


def a_no_refund_outside_window(ticket, reply):
    rr = ticket.get("refund_request")
    days = rr["days_since_purchase"] if rr else None
    promised = _REFUND_PROMISE.search(reply)
    if promised and (days is None or days > REFUND_WINDOW_DAYS):
        return False, f"refund promised ('{promised.group(0)}') with days_since_purchase={days}"
    return True, "ok"


ASSERTIONS = {
    "ticket_id_echoed": a_ticket_id_echoed,
    "escalation_tag_matches_tier": a_escalation_tag,
    "refund_amount_present_numeric": a_refund_amount_numeric,
    "no_refund_outside_30_days": a_no_refund_outside_window,
}


def run_assertions(ticket, reply):
    results = {}
    for name, fn in ASSERTIONS.items():
        ok, detail = fn(ticket, reply)
        results[name] = {"pass": bool(ok), "detail": "" if ok else detail}
    return results
