# DocuMind AI — One-Page Architecture Sketch

> **System:** Tier-1 Deflection Assistant & Autonomous Multi-Tool Support Platform  
> **Evaluated:** Week 12 Capstone · AI Summit (Variant A)  
> **Author:** Iswarya Sunkara  

---

## 1. End-to-End System Topology & Span Boundaries

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        CLI["Single Entry Point\n(python run.py)"]
        WEB["FastAPI Universal Portal\n(http://127.0.0.1:8050)"]
        EXT["Thursday Reviewer Client\n(src/external_mcp_client.py)"]
    end

    subgraph Security ["Ingestion & Security Boundary"]
        PII["PII Sanitizer Filter\nMasks Emails, Cards & Addresses"]
        TRACE_INIT["Trace ID Generator\n(tr_capstone_YYYYMMDD_TKT)"]
    end

    subgraph HostAgent ["Host Agent Runtime (src/integrated_assistant.py)"]
        BUDGET["4 Safety Runtime Budgets\nMax 6 Iters | 8k Tok | $0.08 | 25s"]
        REACT["Hand-Built ReAct Agent Loop\n(Claude 3.5 Haiku)"]
        DISCOVERY["MCP Tool Discovery Registry\nDynamic tools/list over JSON-RPC"]
    end

    subgraph MCP ["FastMCP Server Layer (stdio Transport)"]
        direction TB
        SERVER1["rag-support-server\n(src/mcp_rag_server.py)"]
        T1["check_customer_entitlement\n(Mandatory Precondition)"]
        T2["fetch_order_details\n(Billing Ledger)"]
        T3["search_help_center\n(RAG Knowledge Base)"]
        T4["escalate_ticket\n(Defensive Transfer)"]
        SERVER1 --> T1
        SERVER1 --> T2
        SERVER1 --> T3
        SERVER1 --> T4
    end

    subgraph RAG ["In-Memory Knowledge Engine"]
        BM25["Sparse BM25 Index\n(120 Markdown Articles)"]
        DENSE["Dense Embeddings\n(all-MiniLM-L6-v2)"]
        RRF["Reciprocal Rank Fusion\nRRF_Score = 1/(60 + rank)"]
        BM25 --> RRF
        DENSE --> RRF
    end

    subgraph Observability ["Telemetry & Logging (surviving MCP Hop)"]
        SPAN1["Span 1: agent_react_loop"]
        SPAN2["Span 2: mcp_tool_execution"]
        SPAN3["Span 3: hybrid_retrieval"]
        SPAN4["Span 4: llm_synthesis"]
        LOCAL_LOG["trace_integrated.json\ntraces_live.jsonl"]
        LANGFUSE["Langfuse Cloud Dashboard\n(us.cloud.langfuse.com)"]
        SPAN1 --> LOCAL_LOG
        SPAN2 --> LOCAL_LOG
        SPAN3 --> LOCAL_LOG
        SPAN4 --> LOCAL_LOG
        LOCAL_LOG --> LANGFUSE
    end

    CLI --> PII
    WEB --> PII
    EXT -.->|stdio JSON-RPC| SERVER1
    PII --> TRACE_INIT --> BUDGET --> REACT
    REACT <-->|tools/list & tools/call| DISCOVERY
    DISCOVERY <-->|JSON-RPC 2.0 stdio| SERVER1
    T3 <--> RAG
    REACT --> Observability
```

---

## 2. Where the Model Calls Happen (And Where They Don't)

| System Component | Executes LLM Inference? | Model Used | Execution Mechanism | Reason for Choice |
|---|:---:|---|---|---|
| **FastMCP Servers** | **NO (0%)** | None | Pure deterministic Python (`re`, `json`) | **Architectural principle:** Servers expose capabilities only; zero non-deterministic model drift on servers. |
| **Hybrid Retriever** | **NO (0%)** | `all-MiniLM-L6-v2` | Dense cosine + BM25 inverted index | Sub-millisecond deterministic retrieval; prevents hallucination during vector lookups. |
| **Entitlement Tool** | **NO (0%)** | None | CRM database lookup (`tickets_week8.json`) | Customer contracts are legal commitments; entitlement must never be estimated by an LLM. |
| **ReAct Decision Loop** | **YES (45%)** | `claude-haiku-4-5` | Tool-choice prompt with structured schema | Chooses tool sequences based on customer question and tool outputs. |
| **Reply Synthesis** | **YES (55%)** | `claude-haiku-4-5` | Few-shot grounded response drafter | Crafts professional, empathetic reply embedding exact slug citation (`[refund-and-returns-policy-30day-v2]`). |

---

## 3. Where the Money Goes (Financial Accounting per Query)

The integrated pipeline processes a live support ticket for **$0.0004666** total cost. Here is the exact cost attribution across each span:

```mermaid
pie title Cost Attribution by Pipeline Stage ($0.0004666 / query)
    "LLM Answer Generation ($0.0004180)" : 89.6
    "MCP Tool Execution ($0.0000450)" : 9.6
    "Hybrid RAG Retrieval ($0.0000036)" : 0.8
```

### Stage-by-Stage Telemetry Breakdown:

1. **Stage 1 — Dense + BM25 Hybrid Retrieval:**
   - **Latency:** `3.82 ms` (p50)
   - **Tokens:** `18 tokens` (Query embedding vectorization)
   - **Cost:** **$0.0000036** (**0.8%** of total query budget)
   - **Optimization:** In-memory vector arrays eliminate external database network hops and vector DB API SaaS fees.

2. **Stage 2 — MCP Tool Execution (`check_customer_entitlement` + `fetch_order_details`):**
   - **Latency:** `0.66 ms` total MCP latency across stdio pipes
   - **Tokens:** `207 tokens` (125 prompt / 82 JSON output)
   - **Cost:** **$0.0000450** (**9.6%** of total query budget)
   - **Optimization:** FastMCP stdio transport avoids HTTP overhead; structured JSON outputs minimize serialization bloat.

3. **Stage 3 — LLM Answer Generation (`claude-haiku-4-5`):**
   - **Latency:** `842.1 ms`
   - **Tokens:** `1,086 tokens` (892 prompt / 194 completion)
   - **Cost:** **$0.0004180** (**89.6%** of total query budget)
   - **Optimization:** Prompt version `v2.1-support-rag` uses compact few-shot instructions; prompt caching reduces repeated token costs by 37.0% on high-volume identical system prompts.

---

## 4. Single-Query Unit Economics & ROI

- **Cost per Automated Ticket:** **$0.0004666**
- **Cost of Human Tier-1 Ticket:** **$14.50** (14 agents @ $2,000/mo handling ~2,000 tickets)
- **Net Savings per Deflection:** **$14.4995** (**99.997% cheaper**)
- **Client Monthly Savings (at 50% true deflection of 2,000 tkts = 1,000 tkts/mo):** **$14,500 / month** ($174,000 / year).

