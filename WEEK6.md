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

## Results

_Filled in after the protocol runs. See the `git log` order of labels, then judge v1, then prediction, then judge v2._
