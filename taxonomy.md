# Week 5 Practical — Customer Support RAG Error Taxonomy

**Domain:** Customer Support Tickets  
**Evaluated:** Week 5 — Error Analysis & Trace Reading  
**Dataset:** 1,000 logged traces | **Random Sample:** 20 traces (`SEED = 42`)  

---

## Ranked Failure Taxonomy Table

| Failure Mode Name | Count | Freq % | Severity | Example Trace ID |
|---|:---:|:---:|---|:---:|
| **Quotes superseded billing grace period window** | 6 | 30.0% | Embarrasses client | [`tr_0026`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/traces.jsonl) |
| **Confuses card decline error code 51 with system timeout** | 5 | 25.0% | Annoys user | [`tr_0031`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/traces.jsonl) |
| **Omits primary authentication fallback step for 2FA recovery** | 4 | 20.0% | Embarrasses client | [`tr_0033`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/traces.jsonl) |
| **Omits mandatory field formatting rule for special characters in Cardholder Name** | 3 | 15.0% | Annoys user | [`tr_0090`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/traces.jsonl) |
| **Hallucinates guaranteed SLA refund window on unanswerable billing ticket** | 2 | 10.0% | Embarrasses client | [`tr_0096`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/traces.jsonl) |

---

## Taxonomy Summary Notes

1. **Top Attack Target for Next Week:** Mode #1 ("Quotes superseded billing grace period window") representing **30.0%** of sampled failures.
2. **Key Root Cause Observation:** Retrieval fetches legacy policy chunks matching keyword similarity over effective-date order; exact token matching for error code 51 lacks semantic disambiguation between bank refusal vs network timeout.
3. **Trace Reference:** Detailed open-coding sentences, seeded sample metadata, replayability proof, dated git prediction, and benchmark analysis are documented in [`notes.md`](file:///c:/Users/SoftSuave_Lap_002/Desktop/customer_support_rag/notes.md).
