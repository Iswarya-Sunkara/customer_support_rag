# Verdict: Single Agent vs Multi-Agent Triage Squad

Sunk-cost bias would urge us to keep the multi-agent squad simply because we spent days architecting its manager-worker prompts and hand-offs.
However, the empirical evidence demands that we KILL the multi-agent orchestrator in favor of the single agent.
At identical pass rates (80.0% vs 80.0%), the multi-agent squad imposes a 2.1x context re-send penalty (14,563 vs 6,775 tokens).
Furthermore, multi-agent cost surges by 106.5% ($0.00244 vs $0.00118 per ticket) and p50 latency is 126.7% slower (5.68s vs 2.50s).
Without true parallelization or disjoint security boundaries, multi-agent is merely expensive fashion.
Verdict: KILL the multi-agent squad; KEEP the single agent in production.