"""
Builds eval/cases.jsonl — 25 mode-tagged ticket cases replayed from traces.jsonl.

Every case carries the logged RAG output (raw_output) VERBATIM from a real trace,
so the eval is deterministic and needs no embedding model. Ticket metadata
(ticket ID, tier, refund request) is attached so the reply drafter and the
deterministic assertions have something to check.

Run once:  python eval/build_cases.py
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACES = ROOT / "traces.jsonl"
OUT = ROOT / "eval" / "cases.jsonl"
SEED = 6

# Week-5 taxonomy (taxonomy.md) -> trace categories that probe that mode
MODES = {
    "M1_superseded_grace_period": ["billing_grace"],
    "M2_code51_confused_with_timeout": ["error_51", "auth_failed"],
    "M3_2fa_fallback_step_omitted": ["google_recovery", "google_2fa_voice", "google_3rd_party"],
    "M4_cardholder_format_rule_omitted": ["error_14", "error_430357"],
    "M5_hallucinated_refund_sla": ["sla_refund"],
}
PER_MODE = 5

# Regression cases: real failed traces, replayed verbatim.
#   tr_0033  error-51 ticket answered with only "**Category:** Payment" (no decline guidance at all)
#   tr_0014  430357 lost/stolen-card ticket answered with only "**Category:** Payment"
#   tr_0026  retry-schedule ticket whose first two bullets are the unrelated "cannot modify
#            subscription" table row (cited as the Mode-1 example in taxonomy.md)
REGRESSION = {
    "tr_0033": "M2_code51_confused_with_timeout",
    "tr_0014": "M4_cardholder_format_rule_omitted",
    "tr_0026": "M1_superseded_grace_period",
}

# Refund requests for the refund-mode tickets: in-window, boundary, and out-of-window.
REFUNDS = [
    {"amount": 49.00, "days_since_purchase": 12},
    {"amount": 239.88, "days_since_purchase": 30},
    {"amount": 19.99, "days_since_purchase": 31},
    {"amount": 588.00, "days_since_purchase": 45},
    {"amount": 99.00, "days_since_purchase": 90},
]


def main():
    traces = [json.loads(l) for l in TRACES.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {t["trace_id"]: t for t in traces}
    rng = random.Random(SEED)

    selected = []  # (mode, trace, is_regression)
    for mode, cats in MODES.items():
        forced = [by_id[tid] for tid, m in REGRESSION.items() if m == mode]
        picked = [(mode, t, True) for t in forced]
        seen_outputs = {t["raw_output"] for t in forced}
        pool = [t for t in traces if t["category_tag"] in cats]
        rng.shuffle(pool)
        for t in pool:
            if len(picked) >= PER_MODE:
                break
            # prefer distinct replies; the refund mode only has one logged output, so allow repeats there
            if t["raw_output"] in seen_outputs and mode != "M5_hallucinated_refund_sla":
                continue
            seen_outputs.add(t["raw_output"])
            picked.append((mode, t, False))
        selected += picked

    cases = []
    refund_i = 0
    for i, (mode, t, is_reg) in enumerate(selected, start=1):
        tier = "Priority" if rng.random() < 0.4 else "Standard"
        case = {
            "case_id": f"C{i:02d}",
            "mode": mode,
            "regression": is_reg,
            "source_trace_id": t["trace_id"],
            "ticket": {
                "ticket_id": f"TKT-{rng.randint(10000, 99999)}",
                "tier": tier,
                "question": t["question"],
            },
            "rag_answer": t["raw_output"],
        }
        if mode == "M5_hallucinated_refund_sla":
            case["ticket"]["refund_request"] = REFUNDS[refund_i]
            refund_i += 1
        cases.append(case)

    with OUT.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
