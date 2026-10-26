# DocuMind AI — Master Curriculum & Weekly Tasks Reference

> **Project Title**: Enterprise Customer Support RAG, LLM Evaluation & Multi-Agent MCP Platform  
> **Course / Program**: Applied AI Engineering · LLM Systems & Autonomous Agents  
> **Repository**: `customer_support_rag`  
> **Author**: Iswarya Sunkara  
> **Date**: October 2026  
> **Master Portals**:
> - **FastAPI Universal Web Application**: `http://127.0.0.1:8050/`
> - **Streamlit Analytical Dashboard**: `http://localhost:8501/`
> - **Standalone Week 6 Judge Dashboard**: `http://127.0.0.1:8050/dashboard`

---

## 📑 Executive Curriculum Summary Table (Weeks 1 – 10)

| Week | Core Focus Area | Primary Tasks & Deliverables | Empirical Results / Key Metrics | Primary Files |
| :---: | :--- | :--- | :--- | :--- |
| **Week 1** | **Corpus Curation & Ingestion** | • Curate help-center articles (Cloudflare, Zendesk, Google)<br/>• Character & token chunking strategy<br/>• Metadata extraction | 6 core documents, 48 initial chunks | `data/article_01.md` – `data/article_06.md` |
| **Week 2** | **Embeddings & Vector Database** | • Dense vector embeddings (`all-MiniLM-L6-v2`)<br/>• ChromaDB HNSW cosine indexing | 384-dimensional dense vectors, zero SQLite lock overhead | `src/create_vector_db.py`, `chroma_db/` |
| **Week 3** | **Dense Baseline & Benchmark** | • Formulate 12-Question Golden Set<br/>• Dense retrieval evaluation<br/>• Error token failure separation | **54.55% Hit-Rate@3**<br/>**83.3% Failure Rate** on alphanumeric codes | `golden_set.jsonl`, `src/evaluate_baseline.py`, `results.md` |
| **Week 4** | **Hybrid RAG & Universal Parser** | • Sparse BM25 + Dense RRF ($k=60$)<br/>• Universal In-Memory Document Parser (PDF, DOCX, CSV, Excel, TXT, Images) | **100.0% Hit-Rate@3** (+45.45% gain)<br/>Latency: 23.13 ms (-10.8% faster) | `src/dynamic_rag.py`, `src/hybrid_retriever.py`, `src/document_parser.py` |
| **Week 5** | **Error Taxonomy & Trace Reading** | • 1,000 trace pool audit (`traces.jsonl`)<br/>• Seeded random sample (`SEED=42`, $n=20$)<br/>• Ranked Failure Taxonomy (M1–M5)<br/>• Deterministic replay of `tr_0026` | 5 Failure Modes categorized<br/>Replay similarity: 100% exact match | `taxonomy.md`, `notes.md`, `framed_10_questions_results.json` |
| **Week 6** | **LLM-as-a-Judge Validation** | • 4 Deterministic Assertions vs 1 Semantic Judge<br/>• Blind Protocol (`fb4c42a5b4` commit hash)<br/>• Cohen's Kappa calibration ($\kappa = 0.84$)<br/>• Held-out generalization (91.3%)<br/>• "Faithfully Wrong" bonus case (C01) | Agreement: **68% $\to$ 92%** ($\kappa = \mathbf{0.84}$)<br/>Assertions: **100% Pass**<br/>Deterministic replay caching | `WEEK6.md`, `eval/judge.py`, `eval/assertions.py`, `eval/dashboard.html` |
| **Week 7** | **Agent vs Fixed Workflow Race** | • ReAct Agent Loop vs Linear Workflow on 10 tickets<br/>• Official 8-Number Evaluation Table<br/>• 4 Runtime Safety Budgets<br/>• Conversation memory persistence | Workflow **48.7% faster** (3.05s vs 5.94s)<br/>Workflow **68.0% cheaper** ($0.00135 vs $0.00422)<br/>100% Pass Rate parity | `WEEK7.md`, `src/run_race.py`, `race.csv`, `src/bonus_memory.py` |
| **Week 8** | **Trajectory Evals & Gap Discovery** | • 10 Expected Tool Sequences with legitimate alternate paths<br/>• Outcome-vs-Trajectory Gap discovery<br/>• Right answer down wrong path analysis<br/>• Single mitigation price tag & regression audit | 4-number metric matrix<br/>Cost reported with p50 & Max variance<br/>Zero tool hallucination | `WEEK8.md`, `trajectory_eval.py`, `src/trajectory_evaluator.py` |
| **Week 9** | **Model Context Protocol (MCP)** | • 2 FastMCP stdio servers (5 tools total)<br/>• Config-driven tool discovery via `mcp_config.json`<br/>• 0 changed lines in agent code (`agent_diff.txt`)<br/>• JSON-RPC wire trace & recoverable errors<br/>• Bonus: Unified MCP Gateway & RBAC audit | **0 changed lines** in `mcp_agent.py`<br/>Hand-annotated `wire.json`<br/>Immutable `results/mcp_audit.log` | `WEEK9.md`, `src/mcp_rag_server.py`, `src/mcp_ticket_history_server.py`, `src/mcp_gateway.py` |
| **Week 10** | **Multi-Agent & A2A (Triage Squad Race)** | • Single Agent vs Multi-Agent Triage Squad race<br/>• Same 10 Week-6 cases evaluated with same judge<br/>• Context re-send multiplier & dominant hand-off<br/>• Injected HTTP 500 failure & honest behavior record<br/>• Sunk-cost bias verdict (KILL multi-agent)<br/>• Bonus: AgentCard & A2A lifecycle mapping | Pass Rate Parity: **80.0% vs 80.0%**<br/>Single Agent **126.7% faster** (p50: 2.50s vs 5.68s)<br/>Single Agent **51.6% cheaper** ($0.00118 vs $0.00244)<br/>Multi Context Multiplier: **2.1x** | `race_table.md`, `handoffs.log`, `failure_case.md`, `verdict.md`, `agent_card.json`, `src/run_week10_race.py` |
| **Full App** | **2-Role Access & Live Chatbot** | • Role-based access control (User vs Admin)<br/>• User: Pure AI customer chatbot, all-week Q&A, file uploads<br/>• Admin: Week 3–10 labs, golden benchmarks, MCP wire trace, audit log table<br/>• Transparent MCP tool attribution in chat | Live MCP tool execution & RAG citations in chat; 0 UI overlap | `src/static/index.html`, `src/static/styles.css`, `src/static/app.js`, `src/server.py` |

---

## 🛠️ Detailed Breakdown by Week

---

### 📘 Week 1: Knowledge Corpus Collection & Ingestion Pipeline
#### Objectives & Tasks:
1. **Domain Selection**: Selected realistic enterprise customer support scenarios focusing on:
   - Billing failures, card declines, and authorization errors.
   - Subscription lifecycle, cancellation grace periods, and renewal policies.
   - Account security, 2-Step Verification, security keys, and Google Voice risks.
   - Ticket troubleshooting and Zendesk app management.
2. **Corpus Curation**: Created 6 ground-truth markdown documentation files in [`data/`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data):
   - [`article_01_cloudflare_billing_errors.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/article_01_cloudflare_billing_errors.md)
   - [`article_02_zendesk_payment_issues.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/article_02_zendesk_payment_issues.md)
   - [`article_03_zendesk_credit_card_failures.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/article_03_zendesk_credit_card_failures.md)
   - [`article_04_zendesk_app_troubleshooting.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/article_04_zendesk_app_troubleshooting.md)
   - [`article_05_google_third_party_signin.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/article_05_google_third_party_signin.md)
   - [`article_06_google_2step_verification.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/article_06_google_2step_verification.md)
3. **Chunking Strategy**: Implemented sliding window chunking (500 tokens, 100-token overlap) preserving tabular error codes and markdown header structures.

---

### 📘 Week 2: Embeddings & Vector Database Indexing
#### Objectives & Tasks:
1. **Dense Vector Embeddings**: Utilized `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional dense vectors.
2. **Vector DB Storage**: Ingested chunks into ChromaDB with HNSW cosine distance index.
3. **Resilience Engineering**: Built [`SimpleTextEmbedder`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/dynamic_rag.py#L16-L35) fallback with n-gram hash vectorization and L2 normalization, allowing fast sub-millisecond execution even in environments without PyTorch or CUDA.

---

### 📘 Week 3: Dense Retrieval Baseline & 12 Golden Benchmark Evaluation
#### Objectives & Tasks:
1. **Golden Benchmark Dataset Formulation**: Designed the official 12-question benchmark ([`golden_set.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/golden_set.jsonl)) spanning 4 query categories:
   - Specific Alphanumeric Error Codes (Q01: Error 51, Q02: Authorization Failed, Q03: Error 430357, Q04: Error 14).
   - URL Parameters (Q05: `?noapps`).
   - Prose & Policy Inquiries (Q06 to Q11: SCA vs 3DS, Grace Periods, Google Voice 2-Step).
   - Out-of-Corpus Negative Sample (Q12: SLA Guaranteed Refund Window for chargebacks).
2. **Dense Retrieval Benchmark**: Evaluated Top-3 retrieval:
   - **Hit-Rate@3**: **54.55%** (6/11 answerable queries).
   - **Median Latency (p50)**: **18.75 ms**.
3. **Root Cause Analysis (The Alphanumeric Token Miss)**:
   - Discovered that dense vector embeddings smooth away exact strings: **83.3% of failures** occurred on exact error codes (Code 51, Code 14, 430357), returning baseline refusal *"I don't have enough information..."*.

---

### 📘 Week 4: Hybrid RAG (BM25 + Dense RRF) & Universal Document Parser
#### Objectives & Tasks:
1. **Hybrid Architecture**: Built [`src/hybrid_retriever.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/hybrid_retriever.py) combining:
   - Sparse keyword search: Inverted index with BM25 term weighting ($k_1=1.5, b=0.75$).
   - Dense semantic search: Vector cosine similarity.
2. **Reciprocal Rank Fusion (RRF)**:
   - Rank fusion formula: $RRF\_Score(d) = \sum \frac{1}{60 + rank(d)}$.
   - Solved all alphanumeric token misses: **Hit-Rate@3 jumped from 54.55% to 100.0%**.
3. **Universal Document Parser**:
   - Implemented [`src/document_parser.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/document_parser.py) supporting **any file format without restriction**: PDF, DOCX, CSV, Excel, TXT, Markdown, Python/Code, Images, and Binary fallback.
4. **Latency Gain**: Mean latency dropped from 25.93 ms to 23.13 ms (**-10.8% faster**).

---

### 📘 Week 5: Production Error Taxonomy & Trace Analysis
#### Objectives & Tasks:
1. **Trace Pool Inspection**: Analyzed 1,000 production trace records in [`traces.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/traces.jsonl).
2. **Scientific Seeded Sampling**: Sampled 20 representative cases using a reproducible seed (`SEED = 42`).
3. **Ranked Error Taxonomy (M1 – M5)**: Documented in [`taxonomy.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/taxonomy.md):
   - **M1: Retrieval Miss / Out-of-Corpus Failure** (35% of errors).
   - **M2: Hallucinated Policy or Number** (25% of errors).
   - **M3: Arithmetic / Calculation Error** (15% of errors).
   - **M4: Formatting & Assertion Failure** (15% of errors).
   - **M5: Tone & De-escalation Inconsistency** (10% of errors).
4. **Deterministic Trace Replay**:
   - Replayed trace `tr_0026` with exact token parameters, demonstrating 100% reproducible diagnostic replay.
5. **Framing 10 Failure-Inducing Questions**:
   - Built a 10-question framed test suite ([`framed_10_questions_results.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/framed_10_questions_results.json)) to systematically provoke each failure mode.

---

### 📘 Week 6: LLM-as-a-Judge Evaluation & Scientific Blind Protocol
#### Objectives & Tasks:
1. **Deterministic Assertions vs LLM Judge Split**:
   - Divided evaluation into **4 Python assertions** (Ticket ID present, Refund amount numeric, Escalation tag correct, No refund outside 30 days) achieving **100% pass rate**, and **1 subjective LLM judge criterion** (`resolves_ticket`).
2. **Blind Protocol & Cryptographic Anti-Contamination**:
   - Human labels committed to git at `fb4c42a5b4` *before* the judge evaluated cases.
   - Evaluator strictly verifies git commit SHA and SHA-256 reply hashes before running.
3. **Claude 3.5 Haiku Implementation**:
   - Strict JSON Schema API output: `{ "reason": string, "verdict": "PASS" | "FAIL" }`.
   - Deterministic SHA-256 caching in `results/judge_vN.json` preventing re-billing.
4. **Inter-Rater Reliability (Cohen's $\kappa$)**:
   - **Judge v1**: 68.0% agreement ($\kappa = 0.34$, low reliability).
   - **Judge v2**: Iterated prompt with 2 few-shot calibration examples (C08, C21), reaching **92.0% agreement ($\kappa = \mathbf{0.84}$)**.
   - **Held-Out Agreement**: **91.3%** on the remaining 23 unseen cases.
5. **Bonus Challenge ("Faithfully Wrong")**:
   - Demonstrated on Case C01: Answer had **100% RAGAS Faithfulness** (quoted context perfectly) but **Zero Precision** because the retrieved context was completely irrelevant to the customer's actual question.

---

### 📘 Week 7: Agent Loops vs Fixed Workflows (Latency & Budget Race)
#### Objectives & Tasks:
1. **Head-to-Head Race (10 Refund Tickets)**:
   - Hand-Built ReAct Agent Loop vs Fixed Linear Workflow executed on identical tickets with Anthropic Claude 3.5 Haiku.
2. **Official 8-Number Evaluation Table** ([`WEEK7.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/WEEK7.md)):
   - **Pass Rate**: Both achieved **100.0%** (10/10).
   - **Median Latency (p50)**: Workflow is **48.7% faster** (3.05 s vs 5.94 s).
   - **Total Tokens**: Workflow used **77.2% fewer tokens** (7,860 vs 34,548 tokens).
   - **Cost per Ticket**: Workflow is **68.0% cheaper** ($0.00135 vs $0.00422).
3. **Enforceable Runtime Safety Budgets**:
   - Built 4 hard budget limits: Max Iterations (6), Max Tokens (8,000), Max Cost ($0.08), Max Wall-Clock Time (25.0s). Tested clean termination with zero unhandled exceptions.
4. **Bonus Challenge (Conversation State & Memory Degradation)**:
   - Verified persistence across restarts and analyzed multi-turn context degradation across a 30-turn thread ([`src/bonus_memory.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/bonus_memory.py)).

---

### 📘 Week 8: Agent Trajectory Evaluations & Gap Discovery
#### Objectives & Tasks:
1. **10 Expected Tool Sequences with Legitimate Alternate Paths**:
   - Defined legitimate paths as mathematical sets in code ([`data/tickets_week8.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/tickets_week8.json)), accepting valid permutations (e.g. customer tier before or after order details; 2-step optimal vs 3-step defensive).
2. **Outcome-vs-Trajectory Gap**:
   - Discovered tickets where the final drafted reply sounded acceptable (Pass), but the tool execution sequence was sub-optimal or redundant.
3. **Right Answer Down Wrong Path**:
   - Analyzed cases where an agent reached a correct refund conclusion despite querying unrelated tools, proving why evaluating final replies alone is insufficient.
4. **Single Mitigation with Empirical Price Tag**:
   - Applied docstring prompt conditioning; audited trade-off between increased prompt tokens vs eliminated redundant loop laps.
5. **Per-Mode Regression Audit**: Executed trajectory scoring via [`trajectory_eval.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trajectory_eval.py).

---

### 📘 Week 9: Model Context Protocol (MCP), Multi-Agent Tools & RBAC
#### Objectives & Tasks:
1. **Architecture & Separation of Concerns**:
   - **Host Agent**: Runs the LLM (Claude Haiku 4.5), manages conversation state, enforces budgets ([`src/mcp_agent.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/mcp_agent.py)).
   - **FastMCP Servers**: Expose deterministic tools over standard JSON-RPC 2.0 stdio pipes. **Zero LLM inference runs on the servers**.
2. **Two Custom FastMCP Servers (5 Tools Total)**:
   - **`rag-support-server`** (Server 1): `fetch_order_details`, `lookup_refund_policy`, `get_customer_tier`.
   - **`ticket-history-server`** (Server 2): `lookup_ticket_history`, `get_ticket_details`.
3. **Config-Driven Tool Discovery (0 Lines Changed in Agent)**:
   - Config file [`mcp_config.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/mcp_config.json) connects to both servers.
   - Proved via git diff: **`agent_diff.txt` shows 0 changed lines in `src/mcp_agent.py`**.
4. **Raw Wire Protocol Trace**:
   - Captured and hand-annotated `initialize` -> `tools/list` -> `tools/call` JSON-RPC messages in [`wire.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/wire.json).
5. **Docstrings-as-Prompts & Recoverable Errors**:
   - Rewrote `fetch_order_details` docstring with preconditions and input regex format; structured recoverable error JSON with expected pattern (`^ORD-[0-9]{4}$`) documented in [`error_before_after.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/error_before_after.md).
6. **Remote MCP Risk Note**:
   - Wrote [`risk_note.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/risk_note.md) analyzing authentication vulnerabilities, MITM risks, and credential exposure over HTTP/SSE transports.
7. **Bonus Challenge: Unified MCP Gateway & RBAC Audit Logging**:
   - Implemented [`src/mcp_gateway.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/mcp_gateway.py) as a single front door.
   - Enforced token-based RBAC: `token-tier1-support` (denied ticket history access) vs `token-supervisor-admin` (allowed access).
   - Writes immutable single-line audit entries to [`results/mcp_audit.log`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results/mcp_audit.log).

---

### 📘 Week 10: Multi-Agent & A2A — With Evidence, Not Fashion (Task Set A)
#### Objectives & Tasks:
1. **Head-to-Head Race on the SAME 10 Week-6 Eval Cases**:
   - Raced the Single Agent (Arm 1) against the Multi-Agent Triage Squad (Arm 2: Orchestrator + Triage Worker + Policy-Lookup Worker + Synthesis) across 10 identical cases (`C01`, `C02`, `C06`, `C08`, `C11`, `C12`, `C16`, `C18`, `C21`, `C22`) from `eval/cases.jsonl`.
   - Evaluated both arms using the exact same Week-6 judge: 4 deterministic assertions ([`eval/assertions.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/assertions.py)) and 1 LLM judge criterion ([`judge_v2.txt`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/judge_v2.txt)).
2. **The 4 Core Comparison Numbers Reported** ([`race_table.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/race_table.md)):
   - **Pass Rate**: **80.0%** parity (8/10 on both arms).
   - **Median Latency (p50)**: Single Agent is **126.7% faster** (2.50s vs 5.68s); p99 latency is 4.56s vs 13.80s (+202.8% slower for multi-agent).
   - **Total Tokens**: Multi-Agent consumed **14,563 tokens** vs **6,775 tokens** for Single Agent (+115.0% token bill).
   - **Cost per Ticket**: Single Agent is **51.6% cheaper** ($0.00118 vs $0.00244 per ticket).
3. **Context Re-Send Multiplier & Attribution**:
   - **Context Multiplier**: **2.1x** (`14,563 / 6,775`).
   - **Dominant Hand-off**: `orchestrator -> reply_synthesis`, consuming **49.2%** of all multi-agent tokens (7,158 tokens) due to re-sending accumulated context from both workers.
   - Per-hand-off audit logged in [`handoffs.log`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/handoffs.log).
4. **Injected Worker Failure (HTTP 500 Fault Injection)** ([`failure_case.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/failure_case.md)):
   - Injected HTTP 500 error on Policy-Lookup Worker for Case C08.
   - **Orchestrator Actual Behavior**: **Lied by synthesising as if the worker had answered** (`lied`): the orchestrator acknowledged a temporary policy system issue, but synthesized specific card decline and bank troubleshooting advice from its parametric memory rather than pausing.
5. **Senior Engineering Verdict** ([`verdict.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/verdict.md)):
   - Named **sunk-cost bias** out loud: despite time spent building the squad, empirical numbers dictate we **KILL** the multi-agent orchestrator in favor of the single agent in production.
6. **Bonus Challenge: AgentCard & A2A Task Lifecycle** ([`agent_card.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/agent_card.json)):
   - Published standard `AgentCard` advertising capabilities, input/output modes, and bearer authentication scopes.
   - Mapped the failed case onto the A2A lifecycle (`input-required` state awaiting ticket owner).
   - Formulated 2-line analysis contrasting stateful A2A vs ephemeral plain REST.

---

### 🌐 Full-Stack Application, RBAC & Chatbot Integration
#### Objectives & Tasks:
1. **2-Role Access Control System (User vs Admin)**:
   - Sleek Login & Role Selection modal with instant `[Switch Role]` button in the top navigation bar.
   - **👤 User Role (Customer Mode)**:
     - Pure customer support chatbot experience.
     - Document upload drop zone active (user can upload PDFs, Word, TXT, etc. and ask questions).
     - Customer Help Center quick topic buttons.
     - **Strictly hides all week-wise curriculum elements**: No curriculum popovers, no Week 3–9 buttons, no 12 golden questions panel, no W3 vs W4 filter switch, no fullscreen eval links.
   - **👑 Admin Role (Lab & Control Center)**:
     - Full access to all Week 3–9 interactive labs, Golden benchmarks, Filter switches, Trajectory evals, Live MCP wire runner, and Audit log table.
2. **Live MCP Tool Attribution in Chatbot**:
   - Integrated MCP tool resolution directly into [`src/dynamic_rag.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/dynamic_rag.py):
     - Orders (`ORD-5001`) $\to$ Triggers `fetch_order_details` on `rag-support-server`.
     - Tickets (`TCK-103`) $\to$ Triggers `lookup_ticket_history` on `ticket-history-server`.
     - Refund policies $\to$ Triggers `lookup_refund_policy` on `rag-support-server`.
     - Error codes & General Help $\to$ Triggers Hybrid RAG Knowledge Base.
   - Every answer explicitly displays its execution trace: tool name, FastMCP server, token scope, and audit logging status.
3. **Langfuse Live Telemetry**:
   - Real-time logging of latency, token counts, retrieval similarity scores, and span trees in [`traces_live.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/traces_live.jsonl).

---

## 🚀 How to Run & Verify Every Task

### 1. Launch the Master Application
```bash
# Start the FastAPI Web Server (Hosts UI + API + MCP endpoints on Port 8050)
.\.venv\Scripts\python.exe -m uvicorn src.server:app --host 127.0.0.1 --port 8050

# Open in Browser
http://127.0.0.1:8050/
```

### 2. Run Weekly CLI Test Suites
```bash
# Week 3 & 4: Evaluate Dense Baseline vs Hybrid RAG
python src/evaluate_baseline.py

# Week 6: Run LLM-as-a-Judge Evaluation & Agreement Calibration
python eval/run_eval.py

# Week 7: Run Head-to-Head Latency & Cost Race (Agent vs Workflow)
python src/run_race.py --system all
python src/run_race.py --test-budget

# Week 8: Run Trajectory Evaluation on 10 Refund Tickets
python trajectory_eval.py
python trajectory_eval.py --bonus

# Week 9: Run MCP Multi-Server Agent Loop via stdio
python src/mcp_agent.py --config mcp_config.json --query "Check ticket TCK-103"

# Week 10: Run Multi-Agent Triage Squad vs Single Agent Race & Handoff Audit
python src/run_week10_race.py
```

---

## 📂 Key Repository Files Reference

```text
customer_support_rag/
├── data/                                 # Ground-truth articles & ticket datasets
│   ├── article_01_cloudflare_billing_errors.md
│   ├── article_02_zendesk_payment_issues.md
│   ├── article_03_zendesk_credit_card_failures.md
│   ├── article_04_zendesk_app_troubleshooting.md
│   ├── article_05_google_third_party_signin.md
│   ├── article_06_google_2step_verification.md
│   ├── tickets_week7.json
│   └── tickets_week8.json
├── eval/                                 # Week 6 LLM-as-a-Judge test suite
│   ├── assertions.py
│   ├── judge.py
│   ├── label.py
│   ├── run_eval.py
│   └── dashboard.html
├── results/                              # Generated logs & evaluation artifacts
│   ├── mcp_audit.log                     # Week 9 Unified Gateway single-line audit trail
│   ├── summary_v1.json
│   └── summary_v2.json
├── src/                                  # Core application source code
│   ├── dynamic_rag.py                    # In-memory universal RAG engine + MCP tool routing
│   ├── server.py                         # FastAPI web server & API endpoints
│   ├── document_parser.py                # Universal multi-format file parser
│   ├── hybrid_retriever.py               # Sparse BM25 + Dense RRF fusion retriever
│   ├── mcp_rag_server.py                 # FastMCP Server 1 (Support Ops & Billing)
│   ├── mcp_ticket_history_server.py      # FastMCP Server 2 (Escalation & Touch History)
│   ├── mcp_gateway.py                    # Unified MCP Gateway & Scoped RBAC
│   ├── mcp_agent.py                      # ReAct Host Agent with dynamic tool discovery
│   ├── langfuse_tracer.py                # Live observability telemetry
│   └── static/                           # Frontend assets
│       ├── index.html                    # 2-Role UI, Curriculum Popover, Chatbot & Labs
│       ├── styles.css                    # Design system, glassmorphism, responsive CSS
│       └── app.js                        # Role controller, view switcher, API connectors
├── golden_set.jsonl                      # 12 Golden Benchmark Questions
├── race.csv                              # Week 7 Agent vs Workflow 10-ticket race data
├── wire.json                             # Week 9 Hand-annotated JSON-RPC wire trace
├── agent_diff.txt                        # Proof of 0 lines changed in src/mcp_agent.py
├── config_diff.patch                     # Proof of config-only server addition
├── error_before_after.md                 # Recoverable error before/after transcript
├── risk_note.md                          # Remote MCP security risk analysis
├── taxonomy.md                           # Week 5 Production Error Taxonomy (M1–M5)
├── race_table.md                         # Week 10 4-metric comparison table (Single vs Multi)
├── handoffs.log                          # Week 10 per-hand-off token audit log
├── failure_case.md                       # Week 10 injected worker failure (HTTP 500) analysis
├── verdict.md                            # Week 10 senior engineering verdict (keep/kill)
├── agent_card.json                       # Week 10 bonus AgentCard & A2A task lifecycle
├── SYLLABUS_AND_LLM_JUDGE_GUIDE.md       # Comprehensive master defense guide
├── WEEK6.md                              # Week 6 detailed evaluation report
├── WEEK7.md                              # Week 7 Agent vs Workflow report
├── WEEK8.md                              # Week 8 Trajectory evaluation report
├── WEEK9.md                              # Week 9 MCP implementation report
└── src/run_week10_race.py                # Week 10 automated race runner script
```
