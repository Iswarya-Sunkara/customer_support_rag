"""
Week 7 — Head-to-Head Race Runner: Agent vs. Fixed Workflow.

Evaluates both systems over the identical 10 customer refund tickets:
- Calculates: Pass Rate, p50 Latency, Total Tokens, Cost per Ticket.
- Generates `race.csv` and summary table.
- Executes and logs clean budget termination test to `results/budget_termination.log`.
"""

import argparse
import csv
import json
import logging
from pathlib import Path
import statistics
import time
from typing import Any, Dict, List

import sys
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

DATA_FILE = PROJECT_DIR / "data" / "tickets_week7.json"
RESULTS_DIR = PROJECT_DIR / "results"
RACE_CSV_PATH = PROJECT_DIR / "race.csv"
BUDGET_LOG_PATH = RESULTS_DIR / "budget_termination.log"
RESULTS_JSON_PATH = RESULTS_DIR / "race_results.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RaceRunner")

from src.agent import run_agent, AgentBudgets
from src.workflow import run_workflow
from src.llm import get_anthropic_client


def load_tickets() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}")
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return payload["tickets"]


def test_budget_termination(client: Any) -> Dict[str, Any]:
    """
    Executes a ticket under an intentionally restrictive budget to demonstrate
    clean, non-crashing termination when a budget limit is reached.
    """
    tickets = load_tickets()
    target_ticket = tickets[0]  # TCK-101

    # Configure a restrictive budget: limit max_iterations to 1
    # Since agent requires at least 2 laps to fetch tools and answer, it will hit iteration limit.
    restrictive_budgets = AgentBudgets(
        max_iterations=1,
        max_tokens=4000,
        max_cost=0.05,
        max_wall_clock_seconds=15.0
    )

    logger.info(f"--- Running Budget Termination Test on {target_ticket['ticket_id']} ---")
    start_time = time.perf_counter()
    res = run_agent(target_ticket, budgets=restrictive_budgets, client=client)
    elapsed = time.perf_counter() - start_time

    log_entry = (
        f"================================================================================\n"
        f"BUDGET TERMINATION RUN LOG\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n"
        f"================================================================================\n"
        f"Target Ticket:          {res.ticket_id}\n"
        f"Configured Budgets:     max_iterations={restrictive_budgets.max_iterations}, "
        f"max_tokens={restrictive_budgets.max_tokens}, max_cost=${restrictive_budgets.max_cost}, "
        f"max_wall_clock={restrictive_budgets.max_wall_clock_seconds}s\n"
        f"Budget Reached:         {res.budget_hit}\n"
        f"Configured Limit:       {restrictive_budgets.max_iterations}\n"
        f"Terminated Cleanly:     {res.budget_terminated}\n"
        f"Elapsed Latency:        {round(elapsed, 4)} seconds\n"
        f"Tokens Consumed:        {res.total_tokens}\n"
        f"Cost Incurred:          ${res.total_cost:.6f}\n"
        f"Termination Message:    {res.termination_message}\n\n"
        f"Final Clean Fallback Output:\n"
        f"{res.reply}\n"
        f"================================================================================\n"
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    BUDGET_LOG_PATH.write_text(log_entry, encoding="utf-8")
    logger.info(f"Budget termination test recorded successfully to {BUDGET_LOG_PATH}")

    return {
        "ticket_id": res.ticket_id,
        "budget_hit": res.budget_hit,
        "limit": restrictive_budgets.max_iterations,
        "terminated_cleanly": res.budget_terminated,
        "message": res.termination_message,
        "log_path": str(BUDGET_LOG_PATH)
    }


def run_race(system: str = "all", refresh: bool = False) -> Dict[str, Any]:
    """
    Races Agent vs Fixed Workflow on all 10 tickets.
    """
    tickets = load_tickets()
    client = get_anthropic_client()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    agent_records: List[Dict[str, Any]] = []
    workflow_records: List[Dict[str, Any]] = []

    # Check cache if refresh is False
    cached_data = {}
    if RESULTS_JSON_PATH.exists() and not refresh:
        try:
            cached_data = json.loads(RESULTS_JSON_PATH.read_text(encoding="utf-8"))
            logger.info("Loaded cached race results.")
        except Exception:
            cached_data = {}

    run_agent_suite = system in ("agent", "all")
    run_workflow_suite = system in ("workflow", "all")

    if run_agent_suite:
        logger.info(f"=== Starting Agent Race over {len(tickets)} tickets ===")
        for i, t in enumerate(tickets, 1):
            logger.info(f"[{i}/{len(tickets)}] Running Agent on {t['ticket_id']} ({t['branch_type']})...")
            res = run_agent(t, client=client)
            rec = {
                "ticket_id": res.ticket_id,
                "system": "Agent",
                "pass": res.pass_assertions,
                "latency_sec": res.latency,
                "tokens": res.total_tokens,
                "cost_usd": res.total_cost,
                "iterations": res.iterations,
                "branch_type": t.get("branch_type", "standard"),
                "is_branching": t.get("is_branching", False),
                "reply": res.reply,
                "steps": [
                    {
                        "lap": s.iteration,
                        "thought": s.thought,
                        "tool": s.tool_name,
                        "args": s.tool_input,
                        "result": s.tool_result,
                        "tokens": s.lap_tokens,
                        "cost": s.lap_cost
                    }
                    for s in res.steps
                ]
            }
            agent_records.append(rec)
            logger.info(f"    Done: Pass={res.pass_assertions} | Latency={res.latency}s | Tokens={res.total_tokens} | Cost=${res.total_cost:.5f}")

    if run_workflow_suite:
        logger.info(f"=== Starting Fixed Workflow Race over {len(tickets)} tickets ===")
        for i, t in enumerate(tickets, 1):
            logger.info(f"[{i}/{len(tickets)}] Running Workflow on {t['ticket_id']} ({t['branch_type']})...")
            res = run_workflow(t, client=client)
            rec = {
                "ticket_id": res.ticket_id,
                "system": "Workflow",
                "pass": res.pass_assertions,
                "latency_sec": res.latency,
                "tokens": res.total_tokens,
                "cost_usd": res.total_cost,
                "iterations": res.iterations,
                "branch_type": t.get("branch_type", "standard"),
                "is_branching": t.get("is_branching", False),
                "reply": res.reply,
                "steps": [
                    {
                        "step": s.step_num,
                        "name": s.step_name,
                        "action": s.action,
                        "payload": s.payload,
                        "elapsed": s.elapsed_seconds
                    }
                    for s in res.steps
                ]
            }
            workflow_records.append(rec)
            logger.info(f"    Done: Pass={res.pass_assertions} | Latency={res.latency}s | Tokens={res.total_tokens} | Cost=${res.total_cost:.5f}")

    # Merge with cached if only partial run
    if not run_agent_suite and "agent_records" in cached_data:
        agent_records = cached_data["agent_records"]
    if not run_workflow_suite and "workflow_records" in cached_data:
        workflow_records = cached_data["workflow_records"]

    # Compute Summary Statistics
    summary = {}
    if agent_records:
        passes = sum(1 for r in agent_records if r["pass"])
        latencies = [r["latency_sec"] for r in agent_records]
        tokens = [r["tokens"] for r in agent_records]
        costs = [r["cost_usd"] for r in agent_records]
        summary["agent"] = {
            "system": "Hand-Built Agent",
            "tickets_evaluated": len(agent_records),
            "pass_rate_pct": round((passes / len(agent_records)) * 100.0, 1),
            "p50_latency_sec": round(statistics.median(latencies), 4),
            "mean_latency_sec": round(statistics.mean(latencies), 4),
            "total_tokens": sum(tokens),
            "mean_tokens_per_ticket": round(statistics.mean(tokens), 1),
            "total_cost_usd": round(sum(costs), 6),
            "cost_per_ticket_usd": round(statistics.mean(costs), 6)
        }

    if workflow_records:
        passes = sum(1 for r in workflow_records if r["pass"])
        latencies = [r["latency_sec"] for r in workflow_records]
        tokens = [r["tokens"] for r in workflow_records]
        costs = [r["cost_usd"] for r in workflow_records]
        summary["workflow"] = {
            "system": "Fixed Workflow",
            "tickets_evaluated": len(workflow_records),
            "pass_rate_pct": round((passes / len(workflow_records)) * 100.0, 1),
            "p50_latency_sec": round(statistics.median(latencies), 4),
            "mean_latency_sec": round(statistics.mean(latencies), 4),
            "total_tokens": sum(tokens),
            "mean_tokens_per_ticket": round(statistics.mean(tokens), 1),
            "total_cost_usd": round(sum(costs), 6),
            "cost_per_ticket_usd": round(statistics.mean(costs), 6)
        }

    # Save race.csv
    with open(RACE_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ticket_id", "branch_type", "system", "pass", "latency_sec", "tokens", "cost_usd", "iterations"])
        for r in agent_records:
            writer.writerow([r["ticket_id"], r["branch_type"], "Agent", r["pass"], r["latency_sec"], r["tokens"], r["cost_usd"], r["iterations"]])
        for r in workflow_records:
            writer.writerow([r["ticket_id"], r["branch_type"], "Workflow", r["pass"], r["latency_sec"], r["tokens"], r["cost_usd"], r["iterations"]])

    # Save to JSON
    out_payload = {
        "summary": summary,
        "agent_records": agent_records,
        "workflow_records": workflow_records,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    RESULTS_JSON_PATH.write_text(json.dumps(out_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Run budget test and log
    budget_test_res = test_budget_termination(client)
    out_payload["budget_test"] = budget_test_res

    # Print Table
    print_comparison_table(summary)
    return out_payload


def print_comparison_table(summary: Dict[str, Any]):
    if "agent" not in summary or "workflow" not in summary:
        return

    a = summary["agent"]
    w = summary["workflow"]

    print("\n" + "=" * 80)
    print("           WEEK 7 PRACTICAL: AGENT VS FIXED WORKFLOW RACE (TASK SET A)")
    print("=" * 80)
    print(f"{'Metric':<28} | {'Agent (Loop)':<22} | {'Fixed Workflow':<22}")
    print("-" * 80)
    print(f"{'Pass Rate':<28} | {a['pass_rate_pct']:>20}% | {w['pass_rate_pct']:>20}%")
    print(f"{'p50 Latency':<28} | {a['p50_latency_sec']:>19}s | {w['p50_latency_sec']:>19}s")
    print(f"{'Total Tokens (10 tickets)':<28} | {a['total_tokens']:>22,} | {w['total_tokens']:>22,}")
    print(f"{'Cost per Ticket':<28} | ${a['cost_per_ticket_usd']:>20.6f} | ${w['cost_per_ticket_usd']:>20.6f}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Race Agent vs Fixed Workflow")
    parser.add_argument("--system", choices=["agent", "workflow", "all"], default="all")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--test-budget", action="store_true")
    args = parser.parse_args()

    if args.test_budget:
        client = get_anthropic_client()
        test_budget_termination(client)
    else:
        run_race(system=args.system, refresh=args.refresh)
