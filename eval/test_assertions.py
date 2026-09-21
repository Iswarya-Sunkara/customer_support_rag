"""Negative tests: each assertion must actually fire on a bad reply.  python eval/test_assertions.py"""
from assertions import run_assertions

PRIORITY_LATE = {"ticket_id": "TKT-1", "tier": "Priority", "refund_request": {"amount": 19.99, "days_since_purchase": 45}}
STANDARD = {"ticket_id": "TKT-1", "tier": "Standard"}
STANDARD_LATE = {"ticket_id": "TKT-1", "tier": "Standard", "refund_request": {"amount": 588.0, "days_since_purchase": 45}}


def check(ticket, reply, expect):
    got = {k: v["pass"] for k, v in run_assertions(ticket, reply).items()}
    assert got == expect, (reply, got)


check(PRIORITY_LATE, "hello, we will refund $20 soon",
      {"ticket_id_echoed": False, "escalation_tag_matches_tier": False,
       "refund_amount_present_numeric": False, "no_refund_outside_30_days": False})
check(STANDARD, "TKT-1 [ESCALATE:PRIORITY] you are eligible for a refund",
      {"ticket_id_echoed": True, "escalation_tag_matches_tier": False,
       "refund_amount_present_numeric": True, "no_refund_outside_30_days": False})
check(STANDARD_LATE, "TKT-1 you are not eligible for a refund of $588.00",
      {"ticket_id_echoed": True, "escalation_tag_matches_tier": True,
       "refund_amount_present_numeric": True, "no_refund_outside_30_days": True})
check(STANDARD_LATE, "TKT-1 refund of 588 dollars has been approved",
      {"ticket_id_echoed": True, "escalation_tag_matches_tier": True,
       "refund_amount_present_numeric": False, "no_refund_outside_30_days": False})
print("assertion tests: all passed")
