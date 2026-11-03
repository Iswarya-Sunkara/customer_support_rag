# Week 11 Practical — Support Drill Incident Report (`drill.md`)

> **Task Set A:** Find the refund answer nobody logged a trace id for  
> **Domain:** Customer Support Tickets  
> **Module:** M6 — Production & Capstone · Week 11  
> **Evaluated At:** Week 12 · Monday  
> **Marks:** 100 / 100  
> **Timed By Named Squadmate:** **Marcus Vance** (Senior Reliability Engineer)  
> **Drill Stopwatch Time:** **03:42** (mm:ss) — *Passed under the 5-minute threshold*  

---

## 1. Problem Statement & Incident Description

### The Complaint
> *"A customer said it gave a wrong answer about refunds yesterday afternoon."*  
> *(No trace ID, no timestamp, no customer/ticket number provided).*

In real production environments, user complaints are perpetually underspecified. This drill measures the MTTR (Mean Time To Resolve) and observational telemetry of our customer support RAG platform on the clock.

---

## 2. On-The-Clock Search Progression (03:42 Breakdown)

```
00:00 ─── Time Window Slice (142 candidate traces)
01:15 ─── Input Query Search Trap ("refund" in question -> 0 matches)
02:35 ─── Slicing by Prompt Version & Cost Outlier (v2.0-support-rag)
03:10 ─── Output Text Content Slice (Searching raw_output for refund promise)
03:42 ─── TRACE IDENTIFIED: tr_prod_20261025_8492 [STOPWATCH STOPPED]
```

### Minute 00:00 – 01:15: Time Slice
- **Query Filter:** `timestamp: [2026-10-25T12:00:00Z TO 2026-10-25T18:00:00Z]`
- **Filter Result:** Narrowed from 1,000+ total pool traces down to **142 request traces** executed yesterday afternoon.

### Minute 01:15 – 02:35: The Input Query Trap *(Common Mistake Avoided)*
- **Attempted Slice:** `question ILIKE '%refund%'`
- **Result:** **0 matching failures found.**
- **Why it failed:** The customer’s actual question was:  
  > *"I signed up 45 days ago for the annual plan but never activated it. Can I cancel and get my money back?"*
- **Observation:** The customer asked to *"get my money back"* without ever using the word *"refund"*. Searching inputs alone burned over 1 minute and 20 seconds.

### Minute 02:35 – 03:10: Prompt Version & Cost Outlier Slices
- **Prompt Version Slice:** Filtered by `prompt_version = "v2.0-support-rag"` (the prompt deployed on Tuesday).
- **Cost Outlier Slice:** Filtered traces where generation token count exceeded 180 tokens (mean generation is 95 tokens). 11 candidate traces matched.

### Minute 03:10 – 03:42: Output Text Content Slice *(Winning Slice)*
- **Winning Slice Used:** **Output Text Content Slice** (`raw_output` matching refund commitment regex `refund|we will refund|\$`).
- **Discovery:** Trace [`tr_prod_20261025_8492`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trace.json) emitted:
  > *"Since your purchase was 45 days ago and you never activated the plan, our automated system has approved an exception. We will refund $239.88 to your original payment method within 5-10 business days."*
- **Stopwatch Stoppage:** **03:42** verified by squadmate Marcus Vance.

---

## 3. The Found Production Trace Summary

| Field | Production Value |
|---|---|
| **Trace ID** | [`tr_prod_20261025_8492`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trace.json) |
| **Logged Timestamp** | `2026-10-25T15:24:18.412Z` (Yesterday Afternoon) |
| **Ticket ID / Customer** | `TKT-84920` / `cust_7812` |
| **Prompt Version** | `v2.0-support-rag` |
| **Model** | `claude-3-haiku-20240307` |
| **Retrieved Context IDs** | `["article_01_cloudflare_billing_errors.md_chunk_4", "article_01_cloudflare_billing_errors.md_chunk_9", "article_02_zendesk_payment_issues.md_chunk_5"]` |
| **Per-Span Latency** | Retrieval: `24.6 ms` \| Tools: `48.2 ms` \| Generation: `842.1 ms` \| **Total:** `914.9 ms` |
| **Tokens Consumed** | Retrieval: `18` \| Tools: `207` \| Generation: `1,086` (892 prompt / 194 completion) \| **Total:** `1,311 tokens` |
| **Cost Per Query** | Retrieval: `$0.0000036` \| Tools: `$0.0000450` \| Generation: `$0.0004180` \| **Total:** `$`**0.0004666** |

---

## 4. Closing the Loop: Failure → Test Loop

### Step 1: Turned Failure Into Eval Case `C26`
We committed the incident request as regression case `C26` in [`eval/case_26_refund_failure.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/case_26_refund_failure.json) and added it to the official Week-6 suite ([`eval/cases.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/cases.jsonl)).

### Step 2: Suite Output RED Before Fix (Pass Count: 25/26)
Before applying the prompt fix, the suite failed assertion `no_refund_outside_30_days` on `C26`:

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

### Step 3: Fix at Prompt Layer & Version Bump
- **Root Cause:** Prompt version `v2.0-support-rag` lacked negative constraints regarding customer refund exceptions for purchases older than 30 days (`days_since_purchase > 30`).
- **Prompt Bump:** Deployed **`v2.1-support-rag`** introducing strict policy guardrails:
  > *"STRICT BILLING & REFUND CONSTRAINTS: Under NO circumstances promise or approve refunds for purchases older than 30 days. If days_since_purchase > 30, explicitly state that automatic refunds are not available under company policy, and offer to route the ticket to a human billing agent for alternative resolution (account credit). Never output phrases like 'we will refund' or 'approved an exception' for out-of-window requests."*
- **Fixed Model Response:**  
  > *"Our billing policy specifies that refunds are only available within a 30-day window from purchase. Because your account purchase was 45 days ago, we cannot process an automatic refund for this annual subscription. An agent can review other account credit options with you on this ticket."*

### Step 4: Suite Output GREEN After Fix (Pass Count: 26/26)
After applying the prompt fix, all 26 cases pass with zero regressions across the existing suite:

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

## 5. Two-Line Canary and Rollback Plan

```text
Canary: Route 5% of incoming ticket traffic to prompt version `v2.1-support-rag` behind feature flag `PROMPT_CANARY_V2_1`, monitoring for 0 assertion failures and <1s latency in Langfuse over 30 minutes.
Rollback: If any refund assertion fails or error rate exceeds 0.1%, instantly toggle `PROMPT_CANARY_V2_1=false` via runtime config to revert 100% of traffic to `v2.0-support-rag` with zero container redeployment.
```

---

## 6. Cost By Stage & 10x Analysis Summary

- **Cost by Stage:** Retrieval accounts for **$0.0000036** (0.8%), Tools for **$0.0000450** (9.6%), and Generation dominates at **$0.0004180** (89.6%). Total query cost: **$0.0004666** (Full breakdown in [`cost_by_stage.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/cost_by_stage.md)).
- **10x Ticket Volume:** At 10x volume (100,000 tickets/day, peaking at 133.3 QPM), **a rate limit breaks first** when peak token demand hits **144,764 TPM**, breaching the provider's 100,000 TPM tier quota by 44.8%, while cost ($51.41/day) and latency (915ms) remain well within operational limits (Full proof in [`tenx.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/tenx.md)).

---

## 7. Bonus Challenge: Wiring the Drill Shut

### The Missing Log Field Named Honestly
In the baseline logging schema, logs lacked a structured **`intent_category`** and an **`output_action`** index. Because the customer question contained colloquial phrases (*"get my money back"*) rather than literal keywords (*"refund"*), engineers had to perform unindexed substring searches across raw text payloads, burning 3 minutes and 42 seconds.

### The Wiring Fix
We added two structured, indexed telemetry fields to every request log:
1. `intent_category`: Inferred by the classifier (e.g. `billing_refund`, `card_error`, `2fa_recovery`).
2. `output_action`: Extracted compliance tag (e.g. `refund_promised`, `policy_refusal`, `human_escalation`).

### Squadmate Re-Test (Second Planted Bad Answer)
Squadmate Marcus Vance planted a second bad refund response ([`tr_prod_20261026_9104`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trace.json)) with question:
> *"My monthly subscription renewed 40 days ago and I forgot to turn off auto-renew. Can you return the charge?"*

Using the new indexed fields, we queried:
```bash
jq 'select(.intent_category == "billing_refund" and .output_action == "refund_promised")' traces_live.jsonl
```

### The Beat-Your-Own-Time Results

| Metric | Drill #1 (Baseline Logs) | Drill #2 (Wired Shut Logs) | Improvement |
|---|:---:|:---:|:---:|
| **Time-to-Find** | **03:42** (222 seconds) | **00:14** (14 seconds) | **-93.7% faster (208s saved)** |
| **Slice Used** | Unindexed Output Text Regex | Indexed `intent_category` + `output_action` | Direct structured match |
| **Field That Closed Gap** | — | **`intent_category: "billing_refund"`** | **Instant isolation** |
