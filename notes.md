# Week 5 Practical Notes & Trace Analysis Evidence

**Domain:** Customer Support Tickets  
**Evaluated:** Week 5 — Error Analysis & Trace Reading  

---

## 1. Seeded Random Sample Metadata

- **Random Seed:** `42`
- **Total Trace Pool:** 1,000 customer support ticket traces in [`traces.jsonl`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/traces.jsonl)
- **Seeded Sample (20 Trace IDs):**
  `['tr_0026', 'tr_0031', 'tr_0033', 'tr_0090', 'tr_0096', 'tr_0105', 'tr_0115', 'tr_0143', 'tr_0229', 'tr_0251', 'tr_0282', 'tr_0433', 'tr_0559', 'tr_0605', 'tr_0655', 'tr_0693', 'tr_0755', 'tr_0759', 'tr_0760', 'tr_0914']`

---

## 2. Trace Replay Evidence (Trace `tr_0026`)

### Replay Target Details
- **Selected Trace ID:** `tr_0026`
- **Question:** `Help needed - If my automatic subscription payment fails on day 1, when is the next retry attempt made?`
- **Model & Parameters:** `sentence-transformers/all-MiniLM-L6-v2` | `top_k: 3` | `similarity_threshold: 0.65` | `mode: week4_hybrid`
- **Prompt Version:** `v1.2-support-rag`

### Side-by-Side Output Comparison

```
--- ORIGINAL OUTPUT ---
**Answer based on article_01_cloudflare_billing_errors.md (Week 4 Hybrid RAG System):**

• Refer to [Resolve "you cannot modify this subscription"](https://developers.cloudflare.com/billing/troubleshooting/) if payment fails on retry.
• | "You cannot modify this subscription since it is currently scheduled to be cancelled" | You are trying to change a subscription that already has a pending cancellation.
• Cloudflare will retry up to 5 times over 5 days.

*Cited from `article_01_cloudflare_billing_errors.md` (article_01_cloudflare_billing_errors.md_chunk_14) with 54.1% relevance confidence.*

--- REPLAYED OUTPUT ---
**Answer based on article_01_cloudflare_billing_errors.md (Week 4 Hybrid RAG System):**

• Refer to [Resolve "you cannot modify this subscription"](https://developers.cloudflare.com/billing/troubleshooting/) if payment fails on retry.
• | "You cannot modify this subscription since it is currently scheduled to be cancelled" | You are trying to change a subscription that already has a pending cancellation.
• Cloudflare will retry up to 5 times over 5 days.

*Cited from `article_01_cloudflare_billing_errors.md` (article_01_cloudflare_billing_errors.md_chunk_14) with 54.1% relevance confidence.*
```

- **Replay Verification Result:** `EXACT MATCH (100% Deterministic)`
- **Trace Fields Reconstructed:** None. All fields (`prompt_version`, `model`, `model_params`, `retrieved_chunks` with `chunk_id` and similarity scores, `raw_output`) were present in the logged trace record.

---

## 3. Open-Coding Observation Sentences (20 Sampled Traces)

1. `tr_0026`: Response states retry schedule is up to 5 times over 5 days, but cites outdated 2021 grace period chunk instead of active 2026 policy.
2. `tr_0031`: Response instructs user to resolve error code 51 by checking Zendesk system network status instead of contacting bank for card decline.
3. `tr_0033`: Response details 2-step verification review timeline but omits mandatory requirement to submit backup codes before 3-day recovery review.
4. `tr_0090`: Response lists 5-digit ZIP requirement but omits rule stripping special characters and accents from Cardholder Name field.
5. `tr_0096`: Response provides generic 30-day refund window answer for annual plan chargeback question despite no chargeback SLA existing in corpus.
6. `tr_0105`: Response quotes superseded 14-day subscription retry window alongside current 5-day policy chunk, presenting conflicting grace periods.
7. `tr_0115`: Response misidentifies credit card error code 51 as an internal Zendesk payment gateway timeout.
8. `tr_0143`: Response explains Google account recovery timeline but fails to state that backup codes bypass the 3-day security review.
9. `tr_0229`: Response specifies billing ZIP format but does not mention stripping punctuation from cardholder names.
10. `tr_0251`: Response states subscription renewal retries occur over 14 days based on an old article header, contradicting the active 5-day schedule.
11. `tr_0282`: Response attributes error code 51 to an authorization timeout rather than an issuing bank card decline.
12. `tr_0433`: Response explains 2FA security key recovery but omits the step requiring emergency single-use backup code entry.
13. `tr_0559`: Response lists billing address formatting guidelines but leaves out restrictions on accented characters in cardholder name.
14. `tr_0605`: Response claims an annual subscription chargeback SLA of 30 days when the documentation contains no chargeback SLA.
15. `tr_0655`: Response cites legacy Cloudflare retry policy of 14 days rather than active 5-retry policy.
16. `tr_0693`: Response advises checking network connectivity for card decline code 51 instead of requesting bank authorization retry.
17. `tr_0755`: Response outlines Google account security review steps without mentioning the backup verification code option.
18. `tr_0759`: Response details ZIP code formatting for payment submission but excludes cardholder name special character rules.
19. `tr_0760`: Response provides a 14-day renewal grace period snippet from superseded 2021 documentation.
20. `tr_0914`: Response categorizes credit card error code 51 as a system gateway refusal rather than insufficient card funds.

---

## 4. Dated Falsifiable Prediction

- **Date:** 2026-09-03
- **Target Failure Mode:** Mode #1 ("Quotes superseded billing grace period window").
- **Baseline Frequency:** 30.0% (6 / 20 traces in random sample).
- **Proposed Technical Change:** Implement effective-date metadata filtering in retriever pre-processing to exclude legacy 2021 policy chunks prior to RRF reranking.
- **Expected Quantitative Delta:** Drops Mode #1 frequency from **30.0% (6/20)** to under **5.0% (<=1/20)** on seeded random 20-trace samples.
- **Git Commit Hash:** `PENDING_GIT_COMMIT`

---

## 5. Public Benchmark Note (3 Sentences)

Standard public benchmarks (e.g. MMLU, HumanEval) evaluate general reasoning and synthetic coding logic rather than domain-specific customer ticket support nuances. Public benchmarks do not test temporal currency or effective-date policy precedence, completely missing cases where a model retrieves superseded internal billing policy documents. Furthermore, public benchmarks lack coverage for exact vendor error code tables (e.g. Zendesk/Cloudflare decline codes 51 vs 14), masking retrieval confusions between bank declines and system timeouts.

---

## 6. Bonus Challenge — Curated Demo Set Analysis

### Open-Coding of 10 Curated Demo Set Traces
1. `demo_tr_01`: Response correctly identifies payment authorization failure and cites active Cloudflare troubleshooting steps.
2. `demo_tr_02`: Response correctly specifies adding `?noapps` parameter to URL to disable Zendesk app extensions.
3. `demo_tr_03`: Response accurately explains differences between SCA compliance and 3D Secure verification.
4. `demo_tr_04`: Response correctly provides cardholder name and postal code formatting guidelines.
5. `demo_tr_05`: Response correctly details why Google Voice numbers cannot receive 2FA SMS security codes.
6. `demo_tr_06`: Response provides general decline handling steps for error code 51 without detailed bank refusal distinction.
7. `demo_tr_07`: Response correctly cites resolution steps for card number error code 14.
8. `demo_tr_08`: Response correctly identifies lost/stolen card error code 430357 and replacement procedure.
9. `demo_tr_09`: Response accurately explains why Google blocks third-party app sign-in attempts.
10. `demo_tr_10`: Response accurately states the 3-5 business day timeline for Google account recovery review.

### Frequency Comparison (Top Failure Mode: "Quotes superseded billing grace period window")
- **Random Sample Frequency:** **30.0%** (6 / 20 traces)
- **Demo Set Frequency:** **0.0%** (0 / 10 traces)

### Team Self-Deception Analysis
For the past month, our team has been telling itself that our RAG chatbot was nearly flawless with a 100% pass rate on client demos. We repeatedly tested the same 10 curated demo tickets, which only covered happy-path documentation queries and clean error codes. Because our demo set never included tickets inquiring about subscription retry schedules or superseded policy documents, we suffered severe confirmation bias. We mistook demo readiness for real-world reliability, completely unaware that 30% of actual customer billing tickets were receiving outdated policy answers.
