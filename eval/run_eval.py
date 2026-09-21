"""
ONE command for the whole eval:

    python eval/run_eval.py                 # assertions only (free, no API key)
    python eval/run_eval.py --judge v1      # + LLM judge v1, agreement vs labels_25.json
    python eval/run_eval.py --judge v2      # + LLM judge v2

Prints pass rate BY FAILURE MODE (never just one overall number), the
assertion-vs-judged criteria count, and judge/human agreement.
"""
import argparse
import json
import sys
from collections import defaultdict

from assertions import ASSERTIONS, run_assertions
from common import RESULTS_DIR, labels_commit, labels_dirty, load_cases, load_labels

JUDGED_CRITERIA = ["resolves_ticket"]


def pct(a, b):
    return f"{100 * a / b:5.1f}%" if b else "   - "


def cohen_kappa(pairs):
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(h == j for h, j in pairs) / n
    ph = sum(h == "PASS" for h, _ in pairs) / n
    pj = sum(j == "PASS" for _, j in pairs) / n
    pe = ph * pj + (1 - ph) * (1 - pj)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def guard_labels(cases, labels):
    commit = labels_commit()
    if not labels or not commit:
        sys.exit("REFUSING to run the judge: labels_25.json is not committed yet. "
                 "Label first (python eval/label.py), commit, then judge.")
    if labels_dirty():
        sys.exit("REFUSING: labels_25.json has uncommitted edits after the commit — that is moving the ruler.")
    missing = [c["case_id"] for c in cases if c["case_id"] not in labels["labels"]]
    if missing:
        sys.exit(f"REFUSING: unlabelled cases {missing}")
    changed = [c["case_id"] for c in cases if labels["labels"][c["case_id"]]["reply_sha"] != c["reply_sha"]]
    if changed:
        sys.exit(f"REFUSING: replies changed since labelling for {changed}")
    return commit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", help="judge prompt version, e.g. v1 or v2")
    ap.add_argument("--refresh", action="store_true", help="ignore cached judge verdicts")
    args = ap.parse_args()

    cases = load_cases()
    labels = load_labels()
    for c in cases:
        c["assertions"] = run_assertions(c["ticket"], c["reply"])
        c["assert_pass"] = all(r["pass"] for r in c["assertions"].values())
        c["human"] = labels["labels"][c["case_id"]]["label"] if labels and c["case_id"] in labels["labels"] else None

    verdicts, meta, jcache = {}, {}, {}
    if args.judge:
        commit = guard_labels(cases, labels)
        from judge import judge_cases
        print(f"Labels committed in {commit[0][:10]} at {commit[1]} (before any judge run)")
        verdicts, meta, jcache = judge_cases(cases, args.judge, refresh=args.refresh)
        print(f"Judge {args.judge} first run at {jcache['first_run_at']}  model={jcache['model']}\n")
        for c in cases:
            c["judge"] = verdicts[c["case_id"]]["verdict"]

    # ---------------- pass rate by mode ----------------
    by_mode = defaultdict(list)
    for c in cases:
        by_mode[c["mode"]].append(c)

    hdr = f"{'mode':36} {'n':>3} {'assert':>7} {'judge':>7} {'overall':>8} {'human':>7}"
    print(hdr + "\n" + "-" * len(hdr))
    tot = defaultdict(int)
    for mode in sorted(by_mode):
        cs = by_mode[mode]
        n = len(cs)
        a = sum(c["assert_pass"] for c in cs)
        j = sum(c.get("judge") == "PASS" for c in cs)
        o = sum(c["assert_pass"] and (c.get("judge", "PASS") == "PASS") for c in cs)
        h = sum(c["human"] == "PASS" for c in cs)
        for k, v in (("n", n), ("a", a), ("j", j), ("o", o), ("h", h)):
            tot[k] += v
        print(f"{mode:36} {n:>3} {pct(a, n):>7} {pct(j, n) if args.judge else '   - ':>7} "
              f"{pct(o, n):>8} {pct(h, n) if labels else '   - ':>7}")
    print("-" * len(hdr))
    print(f"{'ALL':36} {tot['n']:>3} {pct(tot['a'], tot['n']):>7} "
          f"{pct(tot['j'], tot['n']) if args.judge else '   - ':>7} {pct(tot['o'], tot['n']):>8} "
          f"{pct(tot['h'], tot['n']) if labels else '   - ':>7}")
    reg = [c for c in cases if c["regression"]]
    print(f"\nRegression cases (verbatim failed traces): "
          + ", ".join(f"{c['case_id']}<-{c['source_trace_id']}" for c in reg))
    print(f"Criteria: {len(ASSERTIONS)} deterministic assertions {list(ASSERTIONS)}  vs  "
          f"{len(JUDGED_CRITERIA)} judged criterion {JUDGED_CRITERIA}")

    fails = [(c["case_id"], k, r["detail"]) for c in cases for k, r in c["assertions"].items() if not r["pass"]]
    if fails:
        print("\nAssertion failures:")
        for f in fails:
            print("  ", *f)

    summary = {"judge": args.judge, "n_cases": len(cases), "assertions": len(ASSERTIONS),
               "judged_criteria": len(JUDGED_CRITERIA)}

    # ---------------- agreement ----------------
    if args.judge:
        pairs = [(c["human"], c["judge"]) for c in cases]
        agree = sum(h == j for h, j in pairs)
        conf = defaultdict(int)
        for h, j in pairs:
            conf[(h, j)] += 1
        print(f"\nJUDGE {args.judge} vs HUMAN agreement: {agree}/{len(pairs)} = {100 * agree / len(pairs):.1f}%"
              f"   (Cohen's kappa {cohen_kappa(pairs):.2f})")
        print(f"  human PASS / judge PASS: {conf[('PASS', 'PASS')]:>2}   human PASS / judge FAIL: {conf[('PASS', 'FAIL')]:>2}")
        print(f"  human FAIL / judge PASS: {conf[('FAIL', 'PASS')]:>2}   human FAIL / judge FAIL: {conf[('FAIL', 'FAIL')]:>2}")
        summary.update(agreement=round(100 * agree / len(pairs), 1), kappa=round(cohen_kappa(pairs), 3),
                       confusion={f"{h}/{j}": v for (h, j), v in conf.items()})

        fewshot = [x.strip() for x in meta.get("few-shot-case-ids", "").split(",") if x.strip()]
        if fewshot:
            held = [(c["human"], c["judge"]) for c in cases if c["case_id"] not in fewshot]
            ha = sum(h == j for h, j in held)
            print(f"  held-out (excluding few-shot cases {fewshot}): {ha}/{len(held)} = {100 * ha / len(held):.1f}%")
            summary["agreement_held_out"] = round(100 * ha / len(held), 1)

        dis = [c for c in cases if c["human"] != c["judge"]]
        print(f"\nDisagreements ({len(dis)}):")
        for c in dis:
            print(f"  {c['case_id']} [{c['mode']}] human={c['human']} judge={c['judge']}")
            print(f"      judge: {verdicts[c['case_id']]['reason']}")
            note = labels["labels"][c["case_id"]].get("note")
            if note:
                print(f"      human: {note}")
        RESULTS_DIR.mkdir(exist_ok=True)
        (RESULTS_DIR / f"disagreements_{args.judge}.json").write_text(json.dumps([
            {"case_id": c["case_id"], "mode": c["mode"], "question": c["ticket"]["question"], "reply": c["reply"],
             "human": c["human"], "human_note": labels["labels"][c["case_id"]].get("note", ""),
             "judge": c["judge"], "judge_reason": verdicts[c["case_id"]]["reason"]} for c in dis
        ], indent=2, ensure_ascii=False), encoding="utf-8")
        (RESULTS_DIR / f"summary_{args.judge}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
