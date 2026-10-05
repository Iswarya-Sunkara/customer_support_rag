"""
Week 8 Practical — Task Set A: Customer Support Ticket Agent
Agent Failure Modes & Trajectory Evals

Usage:
    python trajectory_eval.py               # View full evaluation results table & regression check
    python trajectory_eval.py --refresh     # Re-run live API calls across all 10 tickets
    python trajectory_eval.py --bonus       # Run the Indirect Prompt Injection Bonus Challenge
"""

import argparse
import json
from pathlib import Path
import sys
import time

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.trajectory_evaluator import run_full_trajectory_evaluation, load_week8_dataset
from src.llm import get_anthropic_client


def print_banner(title: str):
    width = 90
    print("\n" + "=" * width)
    print(f" {title.center(width - 2)} ")
    print("=" * width)


def print_expected_sequences(data: dict):
    print_banner("1. THE 10 EXPECTED TOOL SEQUENCES & LEGITIMATE ALTERNATE PATHS")
    tickets = data["tickets"]
    hdr = f"{'Ticket ID':<10} | {'Type / Window':<26} | {'Allowed Paths (Set)':<50}"
    print(hdr)
    print("-" * 90)
    for t in tickets:
        t_id = t["ticket_id"]
        scenario = t.get("expected_outcome", "")[:24]
        seqs = t.get("valid_tool_sequences", [])
        alt_flag = "[ALT SET]" if len(seqs) > 1 else "[STRICT]"
        seq_str = f"{alt_flag} {len(seqs)} paths: " + " | ".join(
            "->".join(p) for p in seqs[:2]
        )
        if len(seqs) > 2:
            seq_str += f" (+{len(seqs) - 2} more)"
        print(f"{t_id:<10} | {scenario:<26} | {seq_str:<50}")
    print("-" * 90)
    print("✓ Alternate-path cases marked as sets: TCK-101 to TCK-107 allow (tier <-> order) permutations;")
    print("  TCK-105 accepts 2-step (optimal) or 3-step (defensive); TCK-108 to TCK-110 strictly forbid policy lookup.")


def print_results_table(b_sum: dict, m_sum: dict):
    print_banner("2. THE FOUR TRAJECTORY NUMBERS & OUTCOME-VS-TRAJECTORY GAP")
    hdr = f"{'Evaluation Metric':<36} | {'Baseline (Unmitigated)':<24} | {'Mitigated Agent':<24}"
    print(hdr)
    print("-" * 90)
    print(f"{'Outcome Pass Rate (%)':<36} | {b_sum['outcome_pass_rate_pct']:>22.1f}% | {m_sum['outcome_pass_rate_pct']:>22.1f}%")
    print(f"{'Trajectory Pass Rate (%)':<36} | {b_sum['trajectory_pass_rate_pct']:>22.1f}% | {m_sum['trajectory_pass_rate_pct']:>22.1f}%")
    print(f"{'OUTCOME-VS-TRAJECTORY GAP (%)':<36} | {b_sum['outcome_vs_trajectory_gap_pct']:>22.1f}% | {m_sum['outcome_vs_trajectory_gap_pct']:>22.1f}%")
    print("-" * 90)
    print(f"{'1. Tool-Choice Accuracy (%)':<36} | {b_sum['tool_choice_accuracy_pct']:>22.1f}% | {m_sum['tool_choice_accuracy_pct']:>22.1f}%")
    print(f"{'2. Argument Validity Rate (%)':<36} | {b_sum['argument_validity_rate_pct']:>22.1f}% | {m_sum['argument_validity_rate_pct']:>22.1f}%")
    print(f"{'3. Step Efficiency (taken / needed)':<36} | {b_sum['step_efficiency_mean']:>23.3f} | {m_sum['step_efficiency_mean']:>23.3f}")
    print(f"{'4a. Cost per Ticket: Median (p50)':<36} | ${b_sum['cost_p50_usd']:>21.6f} | ${m_sum['cost_p50_usd']:>21.6f}")
    print(f"{'4b. Cost per Ticket: Maximum (max)':<36} | ${b_sum['cost_max_usd']:>21.6f} | ${m_sum['cost_max_usd']:>21.6f}")
    print(f"{'4c. Cost per Ticket: Mean (average)':<36} | ${b_sum['cost_mean_usd']:>21.6f} | ${m_sum['cost_mean_usd']:>21.6f}")
    print("-" * 90)
    print(f"{'Median Latency (p50)':<36} | {b_sum['p50_latency_sec']:>21.4f}s | {m_sum['p50_latency_sec']:>21.4f}s")
    print(f"{'Total Tokens (10 tickets)':<36} | {b_sum['total_tokens']:>24,} | {m_sum['total_tokens']:>24,}")
    print("-" * 90)


def print_named_case(case_info: dict):
    print_banner("3. NAMED RIGHT-ANSWER-WRONG-PATH TICKET: TCK-101")
    print(f"Target Ticket:    {case_info['ticket_id']} (Customer: {case_info['customer_id']} | Order: {case_info['order_id']})")
    print(f"Customer Message: \"{case_info['customer_question']}\"")
    print("\nEvaluation Verdict:")
    print(f"  • Outcome Eval:    {case_info['outcome_result']}")
    print(f"  • Trajectory Eval: {case_info['trajectory_result']}")
    print("\nRoot Cause & Danger:")
    print(f"  {case_info['diagnosis']}")


def print_mitigation_and_regression(mitigation: dict, regression_table: list):
    print_banner("4. EXACTLY ONE MITIGATION & MEASURED PRICE PAID")
    print(f"Mitigation Applied:   {mitigation['name']}")
    print(f"Target Failure Mode:  {mitigation['target_failure_mode']}")
    print(f"Before -> After Count: {mitigation['before_count']} -> {mitigation['after_count']} (Mode completely eliminated: -{mitigation['before_count']})")
    print("\nMeasured Price Paid (Empirical, not free!):")
    price = mitigation["measured_price"]
    print(f"  • Added Latency:            +{price['added_p50_latency_sec']:.4f} seconds median latency")
    print(f"  • Added Tokens per Ticket:  +{price['added_tokens_per_ticket']:.1f} tokens / ticket")
    print(f"  • Added Cost per Ticket:    +${price['added_cost_per_ticket_usd']:.6f} / ticket")
    print(f"  • Total Overhead (10 tkts): +{price['total_tokens_overhead']:,} tokens across suite")

    print_banner("5. PER-MODE REGRESSION TABLE (FULL TAXONOMY AUDIT)")
    hdr = f"{'Mode Code':<8} | {'Failure Mode Taxonomy Name':<42} | {'Before':<7} | {'After':<7} | {'Delta':<6} | {'Status':<12}"
    print(hdr)
    print("-" * 90)
    for row in regression_table:
        print(
            f"{row['mode_key']:<8} | {row['mode_name']:<42} | "
            f"{row['before_count']:>6} | {row['after_count']:>6} | "
            f"{row['delta']:>5} | {row['status']:<12}"
        )
    print("-" * 90)
    worsened = [r for r in regression_table if r["delta"] > 0]
    improved = [r for r in regression_table if r["delta"] < 0]
    neutral = [r for r in regression_table if r["delta"] == 0]
    if worsened:
        print(f"Regression Verdict: ⚠️ {len(worsened)} mode(s) worsened: {', '.join(w['mode_key'] for w in worsened)}")
    else:
        print("Regression Verdict: ✅ 0 modes worsened; 0 new modes introduced.")
    print(f"  • Modes Improved: {len(improved)} ({', '.join(m['mode_key'] for m in improved)})")
    print(f"  • Modes Neutral:  {len(neutral)} ({', '.join(m['mode_key'] for m in neutral)})")
    print(f"  • All Modes Checked: {', '.join(m['mode_key'] for m in regression_table)}")


def main():
    parser = argparse.ArgumentParser(description="Week 8 Trajectory Evaluation Runner")
    parser.add_argument("--refresh", action="store_true", help="Re-run live API calls across all 10 tickets")
    parser.add_argument("--bonus", action="store_true", help="Run Bonus Indirect Prompt Injection Benchmark")
    args = parser.parse_args()

    client = get_anthropic_client()
    data = load_week8_dataset()

    print("\nExecuting Week 8 Trajectory Evaluation Suite...")
    res = run_full_trajectory_evaluation(client=client, refresh=args.refresh)

    print_expected_sequences(data)
    print_results_table(res["baseline"]["summary"], res["mitigated"]["summary"])
    print_named_case(res["named_case_deep_dive"])
    print_mitigation_and_regression(res["single_mitigation"], res["regression_table"])

    if args.bonus:
        from src.bonus_injection import run_bonus_injection_benchmark
        run_bonus_injection_benchmark(client=client)
    else:
        print("\nTip: Run with --bonus to execute the Indirect Prompt Injection challenge.")


if __name__ == "__main__":
    main()
