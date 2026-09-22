# Week 6: Validating the ticket-reply judge (Task Set A)

## One command

```bash
pip install -r requirements-eval.txt
python eval/run_eval.py              # assertions only: free, no key needed
python eval/run_eval.py --judge v1   # + judge v1 and agreement with labels_25.json (needs ANTHROPIC_API_KEY)
python eval/run_eval.py --judge v2   # + judge v2
```

The runner prints the pass rate **by Week-5 failure mode**, the count of assertions vs judged criteria, and the judge's agreement with the human labels, including the confusion matrix and every disagreement.

## Eval set (`eval/cases.jsonl`, built by `eval/build_cases.py`)

- 25 cases, 5 for each Week-5 taxonomy mode (M1–M5 from `taxonomy.md`).
- Every case replays a real logged RAG output from `traces.jsonl` verbatim, so the eval is deterministic and needs no embedding model.
- There are 3 regression cases, each a real failed trace replayed verbatim:
  - `C01 <- tr_0026`: the retry-schedule answer leads with the unrelated "cannot modify subscription" row.
  - `C06 <- tr_0033`: the error-51 ticket was answered with only `**Category:** Payment`.
  - `C16 <- tr_0014`: the 430357 lost/stolen-card ticket was answered with only `**Category:** Payment`.
- Ticket metadata (ticket ID, tier, refund request) was added so that `src/reply_drafter.py` can build the reply the agent would actually send.

## Assertion/judge split

The original judge (`judge_v0_all_criteria.txt`) asked the model to check 5 things. Four of them are string checks, so they now live in `eval/assertions.py` and were deleted from the prompt:

| Criterion | Where it runs now |
|---|---|
| Ticket ID is echoed | assertion |
| Refund amount is present and numeric | assertion |
| Escalation tag is set only when the tier is Priority | assertion |
| No refund is promised outside the 30-day window | assertion |
| The reply resolves the customer's question | **LLM judge** (`judge_v1.txt`, a single binary criterion) |

The result is **4 assertions vs 1 judged criterion**. The assertions are tested against bad replies in `eval/test_assertions.py`.

The assertions catch real failures. On the raw Week-4 app output, before the drafter existed:

- The ticket ID was echoed on 0/25 cases.
- The escalation tag was correct on 17/25 cases, so all 8 Priority tickets were missed.
- The refund amount was present on 20/25 cases, so all 5 refund tickets were missed.

## Blind protocol (order is enforced in code)

1. `python eval/label.py --labeler "<name>"` shows the question and drafted reply only, in a shuffled order. It doesn't show the mode tag, the trace ID or any judge output.
2. `git add labels_25.json && git commit -m "labels: 25 blind hand labels (pre-judge)"`
3. `python eval/run_eval.py --judge v1` refuses to run unless `labels_25.json` is committed and unchanged since that commit. It also refuses if any reply changed after labelling (each label stores the reply's hash). The label tool refuses to run once judge results exist.
4. Write `prediction.txt` and commit it **before** creating `judge_v2.txt`.
5. `judge_v2.txt` = v1 plus 2 of v1's own disagreements as few-shot examples. It lists them in the `# few-shot-case-ids:` header, and the runner reports held-out agreement with those two cases excluded.

## Results & Protocol Verification

### 1. Provenance & Commit Order
The blind protocol ordering is provable in `git log`:
1. `fb4c42a` at `2026-09-22 11:18:39 +05:30`: `labels: 25 blind hand labels (pre-judge)` committed **before** judge run.
2. `83393c6`: Judge v1 run results committed (`first_run_at: 2026-09-22T05:50:29Z` = `11:20:29 +05:30`).
3. `d4a9035`: `prediction.txt` committed **before** `judge_v2.txt`.
4. `a9d3336`: `judge_v2.txt` prompt iteration committed with few-shot disagreement examples (`C08`, `C21`).
5. `a40ad5f`: Judge v2 run results committed (`first_run_at: 2026-09-22T06:08:11Z` = `11:38:11 +05:30`).

### 2. Criterion Counts
- **Deterministic Assertions (4):** `ticket_id_echoed`, `escalation_tag_matches_tier`, `refund_amount_present_numeric`, `no_refund_outside_30_days`.
- **Judged Criteria (1):** `resolves_ticket` (Binary: PASS / FAIL).

### 3. Eval Table (Pass Rate by Week-5 Failure Mode)

| Mode | n | Assert Pass | Judge v1 | Judge v2 | Overall (Assert+v2) | Human Ground Truth |
|---|---|---|---|---|---|---|
| **M1: Superseded Grace Period** | 5 | 100.0% | 0.0% | 40.0% | 40.0% | 20.0% |
| **M2: Code 51 vs Timeout** | 5 | 100.0% | 20.0% | 40.0% | 40.0% | 40.0% |
| **M3: 2FA Fallback Omitted** | 5 | 100.0% | 20.0% | 40.0% | 40.0% | 60.0% |
| **M4: Cardholder Format Omitted**| 5 | 100.0% | 20.0% | 20.0% | 20.0% | 20.0% |
| **M5: Hallucinated Refund SLA** | 5 | 100.0% | 20.0% | 100.0% | 100.0% | 100.0% |
| **ALL Modes Combined** | **25**| **100.0%**| **16.0%**| **48.0%** | **48.0%** | **48.0%** |

- **Regression Cases (3 verbatim traces):** `C01<-tr_0026`, `C06<-tr_0033`, `C16<-tr_0014`.

### 4. Agreement Movement (Before -> After)

- **Agreement Before (Judge v1):** **68.0%** (17/25) | Cohen's kappa: **0.34**
  - Confusion matrix: Human PASS / Judge PASS: 4 | Human PASS / Judge FAIL: 8 | Human FAIL / Judge PASS: 0 | Human FAIL / Judge FAIL: 13
- **Agreement After (Judge v2):** **92.0%** (23/25) | Cohen's kappa: **0.84**
  - Confusion matrix: Human PASS / Judge PASS: 11 | Human PASS / Judge FAIL: 1 | Human FAIL / Judge PASS: 1 | Human FAIL / Judge FAIL: 12
  - **Held-Out Agreement (excluding few-shot C08, C21):** **91.3%** (21/23)

### 5. Prediction vs Outcome
- **Prediction (`prediction.txt`):**
  > *"Few-shot examples demonstrating that knowledge-base gap acknowledgments must be graded PASS despite boilerplate refund paragraphs and that answers providing the exact error-code resolution must not be failed for table formatting flaws will resolve disagreements on refund-SLA cases (C21-C24) and error 51 (C08), raising agreement from 68% to over 85%."*
- **Where the Prediction Was Right:**
  - Correctly predicted resolution of all 4 refund-SLA cases (`C21`, `C22`, `C23`, `C24`) where boilerplate refund paragraphs had misled Judge v1 into grading them FAIL despite honest knowledge-base gap acknowledgments.
  - Correctly predicted resolution of `C08`, preventing the judge from failing valid error-51 solutions due to Markdown table formatting flaws.
  - Correctly predicted agreement exceeding 85% (achieved **92.0%** overall, **91.3%** held-out).
- **Where the Prediction Was Wrong:**
  - The prediction did not anticipate that teaching the judge to forgive formatting flaws would make it slightly over-tolerant on `C02`, where it graded a reply PASS despite prominent off-topic subscription cancellation rows and failing to state when the next retry happens.
  - Did not anticipate that `C13` would remain a disagreement due to a truncated list ending with "if:".

### 6. Disagreement Analysis (Who Was Right?)

1. **Case C02 (`M1_superseded_grace_period`): Human = FAIL, Judge v2 = PASS**
   - *Question:* "Hi team, If my automatic subscription payment fails on day 1, when is the next retry attempt made?"
   - *Judge v2 Verdict:* PASS ("The core answer is correct and resolves the customer's ticket.")
   - *Human Verdict:* FAIL ("Off-topic subscription cancellation guidance; does not answer when next retry attempt occurs.")
   - *Verdict on who was right:* **The Human was right.** The customer specifically asked *when* the *next* retry attempt occurs. Saying "retries up to 5 times over 5 days" gives total retries but omits the exact next attempt timing, and leading with an irrelevant subscription cancellation table row severely misleads a billing user. Judge v2 was over-forgiving.

2. **Case C13 (`M3_2fa_fallback_step_omitted`): Human = PASS, Judge v2 = FAIL**
   - *Question:* "Billing query: Why does Google block sign-in attempts when accessing an account from a third-party service?"
   - *Judge v2 Verdict:* FAIL ("The response appears truncated or incomplete, cutting off mid-sentence without delivering the substantive information needed to resolve the ticket.")
   - *Human Verdict:* PASS ("Explains why sign-in is blocked: when Google cannot verify account ownership identity.")
   - *Verdict on who was right:* **The Judge was right.** Although the opening sentence stated "when we can't verify it's really you", the reply abruptly ends with an incomplete bullet `• You may be blocked from signing in to your Google Account if:` followed by an article header. A customer receiving an unfinished sentence would not consider their ticket resolved.

### 7. Bonus Challenge: Faithfully Wrong (RAGAS Faithfulness vs Context Precision)

- **Target Case:** `C01` (Trace `tr_0026`, `M1_superseded_grace_period`)
- **Customer Question:** *"If my automatic subscription payment fails on day 1, when is the next retry attempt made?"*
- **RAG Reply:** Cites `article_01_cloudflare_billing_errors.md_chunk_14`. Leads with:
  `• Refer to [Resolve "you cannot modify this subscription"]...`
  `• | "You cannot modify this subscription since it is currently scheduled to be cancelled" | You are trying to change a subscription that already has a pending cancellation.`
- **RAGAS Metrics:**
  - **Faithfulness:** **1.0 (100%)** — Every claim and sentence in the output was lifted verbatim from the retrieved chunk without hallucinating novel words.
  - **Context Precision:** **0.0 - 0.33** (Low) — The retriever surfaced and prioritized the wrong table section (subscription modification cancellations instead of failed payment retry intervals).
- **Why the Overall Average Hides It:**
  Reporting an aggregate Faithfulness score (e.g. 92%) gives a false sense of security: leadership assumes a 92% score means the customer receives accurate support 92% of the time. In reality, faithfulness only measures factual fidelity to the *retrieved context*, completely ignoring whether that context is the *relevant policy*. A reply can be 100% faithful to an irrelevant or superseded document section, providing a confidently, faithfully wrong answer to the customer while artificially inflating overall eval scores.

