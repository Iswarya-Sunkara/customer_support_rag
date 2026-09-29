# Master Defense Guide: Customer Support RAG System (Weeks 3 – 6)

This document maps the entire 4-week curriculum across the repository and explains how **Weeks 3, 4, 5, and 6** are implemented, benchmarked, and unified into the master dashboards.

---

## 🗺️ Where Are the 4 Weeks in This Project?

Every single week of the curriculum is fully implemented, verified, and accessible across both the **FastAPI Web App (Port 8050)** and the **Streamlit Web App (Port 8501)**:

| Week | Focus Area | Key Deliverables & Code | Location in UI |
|---|---|---|---|
| **Week 3** | **Dense Retrieval Baseline** | • 12-Question Golden Set ([`golden_set.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/golden_set.jsonl))<br/>• Dense `all-MiniLM-L6-v2` in ChromaDB<br/>• Hit-Rate@3: **54.55%** (p50: 18.75 ms)<br/>• Failure Separation: **83.3% R Failures** on alphanumeric error codes | • Web App: **`W3: Baseline`** tab<br/>• Streamlit: **`📈 Week 3: Dense Baseline Evaluation`** tab<br/>• Source: [`results.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results.md#L30-L79) |
| **Week 4** | **Hybrid RAG & Universal Parser** | • Sparse BM25 + Dense Vectors<br/>• Reciprocal Rank Fusion ($k=60$)<br/>• Universal In-Memory Document Parser (PDF, DOCX, CSV, Excel, TXT, MD, Code, Images)<br/>• Latency: Mean 23.13 ms (-10.8% faster) | • Web App: **`W4: Hybrid`** tab<br/>• Streamlit: **`⚡ Week 4: Hybrid RAG & Universal Parser`** tab<br/>• Source: [`src/dynamic_rag.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/dynamic_rag.py), [`results.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results.md#L82-L135) |
| **Week 5** | **Error Taxonomy & Trace Reading** | • 1,000 trace pool ([`traces.jsonl`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/traces.jsonl))<br/>• Seeded random sample (`SEED = 42`, $n=20$)<br/>• Ranked Failure Taxonomy (**M1–M5**)<br/>• Deterministic replay of `tr_0026` (100% match)<br/>• 10 Framed failure-inducing test questions | • Web App: **`W5: Taxonomy`** tab<br/>• Streamlit: **`📊 Week 5: Error Taxonomy & 10 Framed Questions`** tab<br/>• Source: [`taxonomy.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/taxonomy.md), [`notes.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/notes.md) |
| **Week 6** | **LLM-as-a-Judge Validation** | • **4 Assertions** (100% Pass) vs **1 LLM Judge** (`resolves_ticket`)<br/>• Blind Protocol (`fb4c42a5b4` commit hash)<br/>• Inter-rater agreement: **68% $\to$ 92%** ($\kappa = \mathbf{0.84}$)<br/>• Held-out agreement: **91.3%**<br/>• "Faithfully Wrong" bonus challenge (C01) | • Web App: **`W6: LLM Judge`** tab<br/>• Streamlit: **`⚖️ Week 6: LLM-as-a-Judge Validation`** tab<br/>• Standalone: [`eval/dashboard.html`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/dashboard.html)<br/>• Source: [`WEEK6.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/WEEK6.md) |
| **Telemetry** | **Langfuse Observability** | • Distributed tracing of queries, spans & chunks<br/>• Local trace buffer (`traces_live.jsonl`)<br/>• Cloud sync to `https://us.cloud.langfuse.com` | • Web App: **`Langfuse`** tab<br/>• Streamlit: **`📡 Langfuse Observability & Telemetry`** tab<br/>• Source: [`src/langfuse_tracer.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/langfuse_tracer.py) |

---

## 📑 Syllabus Coverage Audit Matrix


| Syllabus Requirement | Implementation Location | Provenance / Evidence | Status |
|---|---|---|:---:|
| **1. LLM-as-a-Judge Implementation** | [`eval/judge.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/judge.py)<br/>[`judge_v1.txt`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/judge_v1.txt), [`judge_v2.txt`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/judge_v2.txt) | Claude 3.5 Haiku (`claude-haiku-4-5`), JSON Schema structured output, SHA cache | ✅ **Complete** |
| **2. Deterministic Assertions vs LLM Judge Split** | [`eval/assertions.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/assertions.py)<br/>[`eval/test_assertions.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/test_assertions.py) | **4 Assertions** (regex/string checks) vs **1 Judged Criterion** (`resolves_ticket`) | ✅ **Complete** |
| **3. Blind Protocol & Anti-Contamination** | [`eval/label.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/label.py)<br/>[`eval/run_eval.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/run_eval.py#L37-L51) | Labels committed at `fb4c42a5b4` *before* judge run; git SHA & reply hash verified | ✅ **Complete** |
| **4. Inter-Rater Reliability (Cohen's $\kappa$)** | [`eval/run_eval.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/run_eval.py#L26-L35)<br/>[`results/summary_v2.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results/summary_v2.json) | Agreement moved from **68.0%** ($\kappa = 0.34$) to **92.0%** ($\kappa = 0.84$) | ✅ **Complete** |
| **5. Held-Out Generalization Calibration** | [`prediction.txt`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/prediction.txt)<br/>[`judge_v2.txt`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/judge_v2.txt) | Pre-registered prediction; held-out agreement is **91.3%** excluding few-shot C08, C21 | ✅ **Complete** |
| **6. Disagreement Analysis ("Who Was Right?")** | [`WEEK6.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/WEEK6.md#L98-L111)<br/>[`eval/dashboard.html`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval/dashboard.html) | Deep dives on C02 (Human right) and C13 (Judge right) | ✅ **Complete** |
| **7. "Faithfully Wrong" Bonus Challenge** | [`WEEK6.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/WEEK6.md#L112-L125) | Case C01: RAGAS Faithfulness = 1.0 (100%) vs Context Precision = 0.0 (Low) | ✅ **Complete** |
| **8. Langfuse Live Observability Integration** | [`src/langfuse_tracer.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/langfuse_tracer.py)<br/>[`src/dynamic_rag.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/dynamic_rag.py#L224-L240) | Live span streaming, trace IDs, chunk confidence, local buffer & cloud sync | ✅ **Complete** |
| **9. Combined Interactive Dashboard** | [`src/static/index.html`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/static/index.html)<br/>[`src/streamlit_app.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/streamlit_app.py) | Week 6 Eval + Langfuse embedded directly into main FastAPI and Streamlit apps | ✅ **Complete** |

---

## 1. Clear Understanding & Explanation of the Claude Implementation

### Why Claude 3.5 Haiku was chosen:
1. **Low Latency & Cost:** `claude-haiku-4-5` delivers fast response times at a fraction of the token cost of frontier models while offering sufficient reasoning ability for binary compliance decisions.
2. **Guaranteed Structured Output:** Uses Anthropic's JSON Schema API (`output_config={"format": {"type": "json_schema", "schema": SCHEMA}}`) to strictly enforce that the model only outputs `{ "reason": string, "verdict": "PASS" | "FAIL" }`. This prevents parsing failures or invalid verdict strings.
3. **Deterministic Re-run Caching:** Every judge run computes a SHA-256 hash of the prompt (`prompt_sha`) and reply (`reply_sha`). Results are cached in `results/judge_vN.json`. If a case has already been judged with the identical prompt and reply, the cached result is used. This prevents accidental re-billing and ensures reproducible evaluation runs.

### How the Judge Works:
```
Customer Ticket + Drafted Reply 
              │
              ▼
    [eval/judge.py]
              │
              ├── Loads prompt template from judge_v1.txt or judge_v2.txt
              ├── Injects {question} and {reply}
              ├── Enforces JSON schema: { reason, verdict: "PASS" | "FAIL" }
              └── Calls claude-haiku-4-5 via Anthropic SDK
              │
              ▼
   Cached Output: results/judge_vN.json
```

---

## 2. Deterministic Assertions vs LLM Judge Split

In real-world engineering, asking an LLM to check simple formatting rules wastes money, introduces non-deterministic flake, and degrades judge focus.

We divided the 5 original criteria from `judge_v0_all_criteria.txt` into **4 deterministic Python string/regex assertions** and **1 LLM judge criterion**:

| Criterion | Implementation | Method | Rationale |
|---|---|---|---|
| **Ticket ID is echoed** | `eval/assertions.py` | String match (`ticket["id"] in reply`) | Deterministic check; 0 tokens wasted |
| **Refund amount present & numeric** | `eval/assertions.py` | Regex (`\$\s*\d+`) | Deterministic check; 0 tokens wasted |
| **Escalation tag matches tier** | `eval/assertions.py` | Conditional string match | Only Priority tickets require `[ESCALATED]` tag |
| **No refund outside 30 days** | `eval/assertions.py` | Negative regex check | Policy prohibits promising refunds after 30 days |
| **Reply resolves customer question** | `eval/judge.py` | **LLM Judge (`claude-haiku-4-5`)** | Subjective, semantic question resolution |

**Result:** On the 25 evaluation cases, deterministic assertions achieved a **100.0% pass rate**, isolating all evaluation variance to the semantic question-resolution quality.

---

## 3. The Blind Protocol (Scientific Anti-Contamination)

To prevent data contamination and confirmation bias ("moving the ruler"):

1. **Blind Hand-Labeling (`eval/label.py`):**
   - The labeler reviews 25 cases presented in randomized order.
   - The interface strictly hides the failure mode category, the trace ID, and all judge outputs.
2. **Cryptographic Commit Enforcement:**
   - Hand labels were committed to git: `fb4c42a5b4` at `2026-09-22 11:18:39 +05:30`.
   - `eval/run_eval.py` strictly **refuses to run** if `labels_25.json` is uncommitted, dirty, or if any reply hash has changed.
3. **Pre-Registered Prediction:**
   - `prediction.txt` was written and committed to git *before* creating `judge_v2.txt`.
4. **Few-Shot Prompt Iteration (`judge_v2.txt`):**
   - 2 of Judge v1's own disagreements (`C08` and `C21`) were added as few-shot calibration examples.
   - The runner computes **held-out agreement** excluding these two cases (achieving **91.3%** held-out agreement across the remaining 23 cases).

---

## 4. Inter-Rater Reliability & Agreement Movement

### Mathematical Definition of Cohen's Kappa ($\kappa$):
$$\kappa = \frac{p_o - p_e}{1 - p_e}$$
where:
- $p_o$: observed proportionate agreement.
- $p_e$: hypothetical probability of chance agreement based on marginal frequencies.

### Quantitative Results:

| Metric | Judge v1 | Judge v2 | Delta / Improvement |
|---|:---:|:---:|:---:|
| **Agreement with Human** | **68.0%** (17/25) | **92.0%** (23/25) | **+24.0%** |
| **Cohen's Kappa ($\kappa$)** | **0.34** (*Slight*) | **0.84** (*Near-Perfect*) | **+0.50** |
| **Held-Out Agreement** | 68.0% | **91.3%** (21/23) | **+23.3%** |
| **Human PASS / Judge PASS** | 4 | **11** | +7 |
| **Human FAIL / Judge FAIL** | 13 | **12** | -1 |
| **False Positives (Human FAIL / Judge PASS)** | 0 | 1 (`C02`) | +1 |
| **False Negatives (Human PASS / Judge FAIL)** | 8 | 1 (`C13`) | -7 |

---

## 5. Disagreement Analysis: Who Was Right?

### Case C02 (`M1_superseded_grace_period`): Human = FAIL, Judge v2 = PASS
- **Customer Question:** *"If my automatic subscription payment fails on day 1, when is the next retry attempt made?"*
- **Judge v2:** PASS (*"The core answer is correct and resolves ticket: retries up to 5 times over 5 days."*)
- **Human Ground Truth:** FAIL (*"Off-topic cancellation guidance; does not answer when next retry occurs."*)
- **Verdict:** **The Human was right.** The customer specifically asked *when* the *next* retry attempt occurs. Saying "up to 5 times over 5 days" gives the overall retry window but omits the exact schedule, and leading with an irrelevant subscription cancellation table row severely misleads a billing customer. Judge v2 was over-forgiving.

### Case C13 (`M3_2fa_fallback_step_omitted`): Human = PASS, Judge v2 = FAIL
- **Customer Question:** *"Billing query: Why does Google block sign-in attempts when accessing an account from a third-party service?"*
- **Judge v2:** FAIL (*"Response appears truncated or incomplete, cutting off mid-sentence."*)
- **Human Ground Truth:** PASS (*"Explains why sign-in is blocked: when Google cannot verify account identity."*)
- **Verdict:** **The Judge was right.** Although the opening sentence stated the reason, the reply abruptly ended with an incomplete bullet: `• You may be blocked from signing in to your Google Account if:` followed by an article header. A customer receiving an unfinished sentence would not consider their ticket resolved.

---

## 6. Bonus Challenge: The "Faithfully Wrong" Trap

- **Case C01 (Trace `tr_0026`):**
  - Question: *"If my automatic subscription payment fails on day 1, when is the next retry attempt made?"*
  - RAG Reply: Cites `article_01_cloudflare_billing_errors.md_chunk_14` (table row discussing pending cancellation of subscriptions).
- **RAGAS Faithfulness: 1.0 (100%)** — Every claim was extracted verbatim from the retrieved chunk without hallucinations.
- **Context Precision: 0.0 - 0.33 (Low)** — The retriever surfaced and prioritized the wrong table section.
- **Key Takeaway:** An aggregate Faithfulness metric (e.g. 92%) creates a dangerous illusion of quality. A reply can be 100% faithful to an irrelevant chunk, producing a confidently, faithfully wrong answer for the customer.

---

## 7. Langfuse Live Observability Integration

Langfuse telemetry is implemented in [`src/langfuse_tracer.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/langfuse_tracer.py) and integrated into [`src/dynamic_rag.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/dynamic_rag.py#L224-L240):

1. **Span Tracing:** Every call to `rag_engine.query(...)` starts a typed `SPAN` observation:
   - Input: `{ "question": question }`
   - Output: `{ "answer": answer, "status": "success" }`
   - Metadata: `trace_id`, `category_tag`, `model_params`, and `retrieved_chunks` (with citation scores and chunk IDs).
2. **Cloud Sync & Local Buffer Fallback:**
   - If `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are provided, traces stream directly to Langfuse Cloud (`https://us.cloud.langfuse.com`).
   - If running offline or without credentials, traces are preserved in a local buffer and written to `traces_live.jsonl`, viewable in the dashboard's **Langfuse Telemetry** tab.

---

## 8. Combined Dashboards (How to Run & Inspect)

Both main application interfaces now seamlessly incorporate Week 6 Evaluation and Langfuse Observability:

### Option A: Universal Web Dashboard (FastAPI)
```powershell
.\.venv\Scripts\python.exe src/server.py
```
- Open [http://127.0.0.1:8050](http://127.0.0.1:8050)
- **Top Tabs:**
  - `💬 Chatbot`: Interactive Q&A with 12 Golden Set benchmark questions.
  - `⚖️ Week 6: LLM Judge`: Full interactive Week 6 evaluation dashboard.
  - `📡 Langfuse Telemetry`: Live query trace stream and connection monitor.
- Direct endpoint: [http://127.0.0.1:8050/dashboard](http://127.0.0.1:8050/dashboard)

### Option B: Streamlit Dashboard
```powershell
.\.venv\Scripts\python.exe -m streamlit run src/streamlit_app.py
```
- Open [http://localhost:8501](http://localhost:8501)
- **Tabs:**
  - `💬 Customer Support Chatbot`
  - `📊 Week 5 Error Taxonomy & 10 Framed Questions`
  - `⚖️ Week 6: LLM-as-a-Judge Validation & Telemetry` (Metrics, Confusion Matrix, Disagreements, Case Browser, Live Eval Runner, and Full HTML Dashboard).

### Option C: Direct CLI Evaluation Suite
```powershell
.\.venv\Scripts\python.exe eval/run_eval.py --judge v2
```
Outputs pass rates by failure mode (M1–M5), 4 assertions vs 1 judge criterion, Cohen's kappa agreement ($\kappa = 0.84$), held-out agreement ($91.3\%$), and disagreement analyses in the terminal.
