"""
Blind hand-labelling tool — run this BEFORE the judge has ever been run.

Shows each drafted reply with only the customer's question. The failure-mode
tag, source trace, and any judge output are hidden so they can't bias you.
Cases are shown in a shuffled order. Progress is saved after every label, so
you can quit (q) and resume.

    python eval/label.py --labeler "Your Name"

When done:  git add labels_25.json && git commit -m "labels: 25 blind hand labels"
The judge refuses to run until that commit exists.
"""
import argparse
import random
from datetime import datetime, timezone
import json

from common import LABELS, labels_commit, load_cases, load_labels, RESULTS_DIR

CRITERION = (
    "RESOLVES: Would this reply resolve the customer's ticket? PASS only if it gives a correct,\n"
    "specific, actionable answer to the question actually asked, with nothing wrong, off-topic\n"
    "or contradictory that would mislead them. If the knowledge base genuinely doesn't cover the\n"
    "question, a reply that plainly says so counts as PASS.\n"
    "Ignore ticket IDs, escalation tags and refund wording (checked by assertions)."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeler", required=True)
    args = ap.parse_args()

    if labels_commit():
        raise SystemExit("labels_25.json is already committed — relabelling after the fact would break the blind protocol.")
    if RESULTS_DIR.exists() and any(RESULTS_DIR.glob("judge_*.json")):
        raise SystemExit("Judge results already exist — these labels would no longer be blind.")

    cases = load_cases()
    data = load_labels() or {
        "protocol": "Blind: labeller saw only question + drafted reply; no mode tag, trace ID, or judge output. "
                    "Labels committed to git before any judge run.",
        "criterion": CRITERION,
        "labeler": args.labeler,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "labels": {},
    }
    order = cases[:]
    random.Random(2026).shuffle(order)

    todo = [c for c in order if c["case_id"] not in data["labels"]]
    print("=" * 78 + "\n" + CRITERION + "\n" + "=" * 78)
    for n, c in enumerate(todo, start=len(data["labels"]) + 1):
        print(f"\n\n######## Reply {n}/{len(cases)} ########")
        print(f"CUSTOMER QUESTION: {c['ticket']['question']}\n")
        print(c["reply"])
        print("-" * 78)
        while True:
            ans = input("[p]ass / [f]ail / [q]uit > ").strip().lower()
            if ans in ("p", "f", "q"):
                break
        if ans == "q":
            break
        note = input("one-line reason (optional) > ").strip()
        data["labels"][c["case_id"]] = {
            "label": "PASS" if ans == "p" else "FAIL",
            "note": note,
            "reply_sha": c["reply_sha"],
            "labeled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        LABELS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    done = len(data["labels"])
    print(f"\n{done}/{len(cases)} labelled -> {LABELS.name}")
    if done == len(cases):
        print('Now commit it:  git add labels_25.json && git commit -m "labels: 25 blind hand labels (pre-judge)"')


if __name__ == "__main__":
    main()
