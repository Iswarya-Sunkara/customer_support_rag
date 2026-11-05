# Re-Scored Production Error Taxonomy (Integrated System)

> **Evaluated System:** Integrated Tier-1 Deflection Assistant (RAG + Agent + MCP + Telemetry)  
> **Source Pool:** 1,000 Live Support Traces (`traces.jsonl`) + Integration Test Suite  
> **Taxonomy Modes:** 6 Named Modes (5 Historical + 1 Integration-Born Mode)  
> **Status:** Audited on Integrated System; Mode M6 Identified as New Integration Risk  

---

## 1. Ranked Taxonomy Overview Table

| Mode Code | Named Failure Mode Taxonomy | Frequency (%) | Severity Level | Exemplar Trace ID | Root Cause & Integration Trigger |
|---|---|:---:|:---:|:---:|---|
| **M1** | **`M1_superseded_grace_period`** | **30.0%** | **HIGH** | `tr_0026` | Agent cites retired 14-day refund window instead of current 30-day policy due to legacy macro contamination. |
| **M2** | **`M2_code51_confused_with_timeout`** | **25.0%** | **MEDIUM** | `tr_0033` | Dense embeddings smoothed away alphanumeric token `51`, conflating card decline with network timeout. |
| **M3** | **`M3_2fa_fallback_step_omitted`** | **15.0%** | **LOW** | `tr_0758` | Assistant fails to state the 3–5 day recovery delay when customer loses primary Titan security key. |
| **M4** | **`M4_cardholder_format_rule_omitted`** | **10.0%** | **LOW** | `tr_0014` | Card error 14 resolution text omits strict alphanumeric formatting rule for postal code/cardholder fields. |
| **M5** | **`M5_hallucinated_refund_sla`** | **15.0%** | **CRITICAL** | `tr_prod_20261025_8492` | Model hallucinated an exception approving a refund for an annual plan purchase at day 45 (> 30 days). |
| **M6** | **`M6_tool_rag_policy_collision`** | **5.0%** | **HIGH** | `tr_integ_0042` | **[NEW MODE BORN OF INTEGRATION]** Tool returns `30-day-current`, but RAG snippet quotes `14-day-legacy`, causing citation conflict. |

---

## 2. The Integration-Born Failure Mode: `M6_tool_rag_policy_collision`

### Why This Mode Did Not Exist in Isolation:
- In Week 4 (Isolated RAG), the retriever simply matched text against documents based on BM25 and cosine distance. There were no tools, no customer accounts, and no contract terms.
- In Week 7 & 9 (Isolated Agent & MCP), the tools returned mock JSON payloads without querying a 120-article knowledge base.
- **The Seam Collision:** When RAG and MCP tools were wired together behind the single entry point, the system acquired **two sources of truth**:
  1. The CRM Entitlement Tool (`check_customer_entitlement`): reports customer account tier, contract date, and legal terms (`terms_version: "30-day-current"`).
  2. The Knowledge Retriever (`search_help_center`): returns public markdown articles where both `article_07_refund_returns_policy_30day.md` and `article_08_refund_returns_policy_14day_legacy.md` co-exist.

### The Trace Failure Breakdown (`tr_integ_0042`):
```json
{
  "trace_id": "tr_integ_0042",
  "ticket_id": "TKT-10821",
  "customer_id": "CUST-403",
  "order_id": "ORD-5003",
  "prompt_version": "v2.0-support-rag",
  "tool_execution": {
    "tool": "check_customer_entitlement",
    "output": {
      "status": "success",
      "terms_version": "30-day-current",
      "applicable_refund_window_days": 30
    }
  },
  "retrieval_execution": {
    "top_chunk": "article_08_refund_returns_policy_14day_legacy.md_chunk_1",
    "snippet": "Under our historical policy, refund eligibility is capped at 14 calendar days from the invoice date."
  },
  "synthesizer_hallucination": "We confirmed your account is on 30-day terms, however under our 14-day policy [refund-and-returns-policy-14day-legacy], your refund is approved.",
  "seam_failure": "Entitlement tool and RAG snippet collided in prompt context; LLM hallucinated contradictory hybrid explanation."
}
```

### Mitigation Implemented in `v2.1-support-rag`:
We added a hard syntactic priority constraint in the agent prompt:
> *"The output of `check_customer_entitlement` is an immutable contractual authorization. If the tool specifies `30-day-current`, you are strictly forbidden from citing `refund-and-returns-policy-14day-legacy` or using any phrasing referring to a 14-day window. You must cite `[refund-and-returns-policy-30day-v2]` exclusively."*

This eliminated Mode M6 across all regression runs.

