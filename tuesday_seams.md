# Tuesday's Unedited Seam List — Integration Friction Log

> **Project:** Tier-1 Support Deflection Assistant (Variant A)  
> **Date Written:** Tuesday, October 27, 2026 (Unedited integration record)  
> **Lead Integrator:** Iswarya Sunkara  
> **Rule:** No post-hoc sanitization. Every seam discovered when connecting Week 3 RAG, Week 7 Agent, Week 9 MCP, and Week 11 Telemetry is logged verbatim with status `FIXED`, `ACCEPTED`, or `RAN-OUT-OF-TIME`.

---

## 1. Summary Status Matrix

| Seam ID | Subsystem Seam Boundary | Discovered Interface Failure / Friction | Resolution Status | Mitigation / Note |
|---|---|---|:---:|---|
| **SEAM-01** | **RAG Corpus $\leftrightarrow$ Agent Tool** | Both 14-day and 30-day refund articles returned in top-2 RAG chunks; agent cited superseded 14-day macro to modern customer. | **FIXED** | Added mandatory `check_customer_entitlement` tool called *before* RAG policy lookup. |
| **SEAM-02** | **MCP Wire $\leftrightarrow$ Tracing** | Trace ID generated in Agent did not propagate across MCP stdio child process; sub-spans lost parent ID. | **FIXED** | Injected `trace_id` and `parent_span_id` into MCP JSON-RPC tool call headers and result wrapper. |
| **SEAM-03** | **Agent Loop $\leftrightarrow$ PII Boundary** | Customer emails (`alice@corp.com`) and street addresses leaked into Langfuse shared spans and console stdout. | **FIXED** | Implemented regex-based `sanitize_pii()` filter at ticket ingestion boundary before trace logging. |
| **SEAM-04** | **Judge v2 $\leftrightarrow$ Regression C26** | Week 6 `run_eval.py` crashed with `REFUSING: unlabelled cases ['C26']` because C26 lacked a human label. | **FIXED** | Guarded human agreement pool strictly to frozen $n=25$ baseline, allowing regression assertions on C26. |
| **SEAM-05** | **Agent Reasoning $\leftrightarrow$ Trajectory Eval** | Agent resolved refund correctly from prompt text without calling `fetch_order_details` (Right Answer Down Wrong Path). | **FIXED** | Enforced docstring precondition contract; made `fetch_order_details` a mandatory prerequisite. |
| **SEAM-06** | **FastMCP Stdio $\leftrightarrow$ Windows UTF-8** | Unicode checkmark `\u2713` crashed Windows PowerShell subprocess with `cp1252` encoding error. | **FIXED** | Reconfigured `sys.stdout` and `sys.stderr` to UTF-8 on Windows at startup in all entry points. |
| **SEAM-07** | **Physical Hardware $\leftrightarrow$ Return Logistics** | Agent approves hardware return within 14 days, but cannot generate a physical PDF shipping return label. | **ACCEPTED** | Tier-1 assistant provides return warehouse address and creates Tier-2 logistics ticket for label generation. |
| **SEAM-08** | **Multi-Language Inquiries $\leftrightarrow$ Retriever** | Spanish/German billing tickets match BM25 poorly against English-only Help Center articles. | **ACCEPTED** | Explicitly stated in eval suite non-coverage disclaimer. Post-capstone candidate for multilingual embeddings. |
| **SEAM-09** | **Real-time Carrier Tracking $\leftrightarrow$ Shipping SLA** | Shipping matrix is static table; cannot poll live FedEx/DHL API for delayed delivery exceptions. | **RAN-OUT-OF-TIME** | Logged as post-capstone technical backlog item #1. Requires carrier webhook integration. |
| **SEAM-10** | **Voice Transcription Audio $\leftrightarrow$ Text RAG** | Telephony IVR voice transcripts contain phoneme errors ("fourty nine" vs "$49") that degrade regex extraction. | **RAN-OUT-OF-TIME** | Logged as post-capstone backlog item #2. Scope limited to Web/Email ticket queues. |

---

## 2. Deep-Dive on Critical Fixed Seams

### Seam SEAM-01: The CEO Escalation Seam (RAG vs Entitlement)
- **The Friction:** When a customer asked *"Can I get a refund for my Cloudflare Pro subscription from 20 days ago?"*, the hybrid retriever pulled `article_08_refund_returns_policy_14day_legacy.md` alongside `article_07_refund_returns_policy_30day.md`. The LLM agent selected the 14-day policy because the retired Zendesk macro text ("Under our 14-day policy...") matched the query keywords with higher BM25 term density. It denied the refund to a customer legally entitled to 30 days. This exact seam caused the client's two recent escalations to the CEO.
- **The Fix:** We established a strict architectural rule: **Never let retrieval determine entitlement.** The agent is constrained by a system contract to call `check_customer_entitlement(customer_id)` first. The tool returns the customer's legal terms (`"terms_version": "30-day-current"`) and the explicit slug (`"refund-and-returns-policy-30day-v2"`). Retrieval is used only for prose explanations, not policy authorization.

### Seam SEAM-02: Telemetry Trace ID Fracture Across MCP Hop
- **The Friction:** The Host Agent assigned `tr_capstone_20261103_84920` to the incoming ticket. When the agent spawned FastMCP child processes over stdio to run `fetch_order_details`, the tool executed in an isolated process with no shared context. In Langfuse, tool executions appeared as disconnected orphan spans with generated UUIDs, destroying MTTR drill investigations.
- **The Fix:** Formulated unified telemetry context propagation. The tool caller passes `caller_trace_id` through the invocation envelope, and the FastMCP server returns `span_id`, parent span ID, token counts, and microsecond latencies inside the structured response payload. The host merges them into one unbroken span tree in `trace_integrated.json`.

### Seam SEAM-03: The PII Leakage Seam
- **The Friction:** In Week 11 drills, raw customer tickets were copied directly into trace logs. When simulating support queries, real customer emails (`alice.chen@corp.com`) and shipping addresses appeared in plaintext in `traces_live.jsonl`, accessible by any engineer with read access to the repo.
- **The Fix:** Built `sanitize_pii()` at the entry point of `src/integrated_assistant.py`. All incoming questions and drafted replies pass through regex filters that mask emails (`a***@corp.com`), postal addresses (`[REDACTED_POSTAL_ADDRESS]`), and credit cards before persisting to disk or sending to Langfuse.

