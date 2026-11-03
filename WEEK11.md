# Week 11 Practical — Observability, Cost & the Failure→Test Loop

> **Domain:** Customer Support Tickets  
> **Track:** Task Set A — *Find the refund answer nobody logged a trace id for*  
> **Module:** M6 — Production & Capstone  
> **Evaluated:** Week 12 · Monday  
> **Marks:** 100 / 100  
> **Lead Engineer / Author:** Iswarya Sunkara  
> **Squadmate / Drill Timer:** Marcus Vance (Senior Reliability Engineer)  

---

## 1. Executive Summary Table

| Evaluation Criterion | Official Requirement | Observed Empirical Value | Metric / Artifact Link | Status |
|---|---|:---:|---|:---:|
| **Support Drill MTTR** | Under 5 minutes on the clock (`mm:ss`) | **03:42** (222s) | [`drill.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/drill.md) | **PASS** |
| **Winning Telemetry Slice** | Identify slice that isolated the trace | **Output Text Content Regex** (`raw_output` matching out-of-window refund promise) | [`drill.md:L50-L65`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/drill.md) | **PASS** |
| **Pasted Production Trace** | Per-span latency, tokens, cost, prompt version & context IDs | Total: **914.9 ms** \| **1,311 tokens** \| **$0.0004666** | [`trace.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trace.json) | **PASS** |
| **Failure-to-Test Loop** | Suite output RED then GREEN with explicit pass counts | **25/26 (96.2%) $\to$ 26/26 (100.0%)** | [`eval/cases.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/cases.jsonl) | **PASS** |
| **Prompt Version Bump** | Record prompt bump with 2-line canary & rollback plan | `v2.0-support-rag` $\to$ **`v2.1-support-rag`** | [`drill.md:L115-L125`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/drill.md) | **PASS** |
| **Cost Attribution by Stage** | Cost per query split across retrieval, tools, generation | Retrieval: **0.8%** \| Tools: **9.6%** \| Generation: **89.6%** | [`cost_by_stage.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/cost_by_stage.md) | **PASS** |
| **10x Scaling Bottleneck** | One line + number proving what breaks first | Rate limit breaks first: **144,764 TPM** vs **100,000 TPM** quota | [`tenx.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/tenx.md) | **PASS** |
| **Bonus: Wire Drill Shut** | Add missing field, plant 2nd answer, beat time | **03:42 $\to$ 00:14** (-93.7% faster) via `intent_category` | [`drill.md:L135-L165`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/drill.md) | **PASS** |

---

## 2. The Production Drill Incident

### The Vague Customer Complaint
> *"A customer said it gave a wrong answer about refunds yesterday afternoon."*  
> *(No trace ID, no timestamp, no ticket number).*

### The Search Timeline
1. **00:00 – 01:15 (Time Slice):** Filtered to yesterday afternoon (`2026-10-25T12:00:00Z` to `2026-10-25T18:00:00Z`), isolating 142 candidate traces.
2. **01:15 – 02:35 (Input Query Trap):** Searched input questions for `"refund"` $\to$ **0 results**. The customer's actual question was: *"I signed up 45 days ago for the annual plan but never activated it. Can I cancel and get my money back?"* Searching only inputs cost 80 seconds.
3. **02:35 – 03:10 (Prompt Version & Token Outliers):** Filtered by `prompt_version = "v2.0-support-rag"` and completion token count > 180 tokens (11 candidates).
4. **03:10 – 03:42 (Output Content Regex):** Searched outputs for money commitments outside the 30-day window (`days_since_purchase > 30` + `"we will refund"`). Located [`tr_prod_20261025_8492`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trace.json) at **03:42** on the clock!

---

## 3. Isolated Trace Breakdown (`trace.json`)

```json
{
  "trace_id": "tr_prod_20261025_8492",
  "timestamp": "2026-10-25T15:24:18.412Z",
  "ticket_id": "TKT-84920",
  "user_id": "cust_7812",
  "prompt_version": "v2.0-support-rag",
  "model": "claude-3-haiku-20240307",
  "retrieved_context_ids": [
    "article_01_cloudflare_billing_errors.md_chunk_4",
    "article_01_cloudflare_billing_errors.md_chunk_9",
    "article_02_zendesk_payment_issues.md_chunk_5"
  ],
  "totals": {
    "latency_ms": 914.9,
    "tokens": 1311,
    "cost_usd": 0.0004666
  }
}
```

### Per-Span Execution Tree
- **Span 1: Retrieval (`dense_sparse_hybrid_retrieval`):**
  - Latency: `24.6 ms` \| Tokens: `18` \| Cost: `$0.0000036` (0.8%)
- **Span 2: Tools (`mcp_ticket_history_server` / `fetch_customer_order_history`):**
  - Latency: `48.2 ms` \| Tokens: `207` (125 prompt / 82 output) \| Cost: `$0.0000450` (9.6%)
- **Span 3: Generation (`claude_3_haiku_generation`):**
  - Latency: `842.1 ms` \| Tokens: `1,086` (892 prompt / 194 completion) \| Cost: `$0.0004180` (89.6%)

---

## 4. Closing the Loop: RED $\to$ GREEN Suite Execution

### 1. New Regression Case `C26` ([`eval/case_26_refund_failure.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/case_26_refund_failure.json))
- Added to [`eval/cases.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/cases.jsonl) under mode `M5_hallucinated_refund_sla` with `"regression": true` and `"source_trace_id": "tr_prod_20261025_8492"`.

### 2. Suite Output RED Before Fix
```
mode                                   n  assert   judge  overall   human
-------------------------------------------------------------------------
M1_superseded_grace_period             5  100.0%      -    100.0%   20.0%
M2_code51_confused_with_timeout        5  100.0%      -    100.0%   40.0%
M3_2fa_fallback_step_omitted           5  100.0%      -    100.0%   60.0%
M4_cardholder_format_rule_omitted      5  100.0%      -    100.0%   20.0%
M5_hallucinated_refund_sla             6   83.3%      -     83.3%   83.3%
-------------------------------------------------------------------------
ALL                                   26   96.2%      -     96.2%   46.2%

Regression cases (verbatim failed traces): C01<-tr_0026, C06<-tr_0033, C16<-tr_0014, C26<-tr_prod_20261025_8492
Criteria: 4 deterministic assertions ['ticket_id_echoed', 'escalation_tag_matches_tier', 'refund_amount_present_numeric', 'no_refund_outside_30_days']  vs  1 judged criterion ['resolves_ticket']

Suite Pass Count: 25/26 (96.2%)
Suite Status: RED (Assertion failures detected)

Assertion failures:
   C26 no_refund_outside_30_days refund promised ('We will refund') with days_since_purchase=45
```

### 3. Suite Output GREEN After Prompt Fix
Bumped prompt version to `v2.1-support-rag` adding strict policy guardrails forbidding refund promises when purchase is outside 30 days:
```
mode                                   n  assert   judge  overall   human
-------------------------------------------------------------------------
M1_superseded_grace_period             5  100.0%      -    100.0%   20.0%
M2_code51_confused_with_timeout        5  100.0%      -    100.0%   40.0%
M3_2fa_fallback_step_omitted           5  100.0%      -    100.0%   60.0%
M4_cardholder_format_rule_omitted      5  100.0%      -    100.0%   20.0%
M5_hallucinated_refund_sla             6  100.0%      -    100.0%   83.3%
-------------------------------------------------------------------------
ALL                                   26  100.0%      -    100.0%   46.2%

Regression cases (verbatim failed traces): C01<-tr_0026, C06<-tr_0033, C16<-tr_0014, C26<-tr_prod_20261025_8492
Criteria: 4 deterministic assertions ['ticket_id_echoed', 'escalation_tag_matches_tier', 'refund_amount_present_numeric', 'no_refund_outside_30_days']  vs  1 judged criterion ['resolves_ticket']

Suite Pass Count: 26/26 (100.0%)
Suite Status: GREEN (All assertions passed)
```

---

## 5. Shipping Safety: Two-Line Canary & Rollback Plan

```text
Canary: Route 5% of incoming ticket traffic to prompt version `v2.1-support-rag` behind feature flag `PROMPT_CANARY_V2_1`, monitoring for 0 assertion failures and <1s latency in Langfuse over 30 minutes.
Rollback: If any refund assertion fails or error rate exceeds 0.1%, instantly toggle `PROMPT_CANARY_V2_1=false` via runtime config to revert 100% of traffic to `v2.0-support-rag` with zero container redeployment.
```

---

## 6. What Breaks First at 10x Volume (`tenx.md`)

> **At 10x today's ticket volume (100,000 tickets/day, peaking at 133.3 queries/min), a rate limit breaks first when peak throughput demands 144,764 tokens per minute (TPM), exceeding the provider's 100,000 TPM tier quota by 44.8% and triggering HTTP 429 errors, whereas daily cost remains under $51.41 and p50 latency stays under 950ms.**

Proof number: **144,764 TPM demanded** vs **100,000 TPM ceiling** ($133.33 \text{ QPM} \times 1,086 \text{ tokens/query}$).

---

## 7. Bonus Challenge: Wiring the Drill Shut

- **The Missing Log Field:** Unindexed raw text logs without structured `intent_category` and `output_action` tags.
- **The Gap Closure:** Added `intent_category: "billing_refund"` and `output_action: "refund_promised"`.
- **Re-Test On Planted Failure #2 (`tr_prod_20261026_9104`):**
  - Time 1 (Before): **03:42**
  - Time 2 (After): **00:14**
  - **Improvement: -93.7% faster (saved 3 minutes and 28 seconds).**
