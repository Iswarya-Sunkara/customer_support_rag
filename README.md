# DocuMind AI — Tier-1 Support Deflection Assistant
### Enterprise RAG · Autonomous Multi-Tool Agent · Model Context Protocol (MCP) · Production Evals

> **Week 12 Capstone Project** · Applied AI Engineering (Module 6: Production & Capstone)  
> **Track:** Variant A — Customer Support Tickets  
> **Author:** Iswarya Sunkara  
> **Evaluated:** Week 12 · Friday — The AI Summit  

---

## ⚡ 60-Second Quickstart (A Stranger Can Run It)

You can clone this repository and run the entire integrated system end-to-end with **a single command**:

```bash
python run.py
```

*Note: `run.py` includes automatic virtualenv self-bootstrapping. If run from a system Python shell, it automatically detects `.venv` and executes cleanly without manual path configuration.*

---

## 🚀 Single Entry Point Commands

| Command | Operational Goal | Key Outputs & Measured Metrics |
|---|---|---|
| **`python run.py`** | **Full 4-Part Live Capstone Demo** | Live ticket run, entitlement check, clickable citation, live escalation, re-scored taxonomy, 10x Black Friday plan. |
| **`python run.py --eval`** | **Full Integrated Eval Suite** | 26 cases across 5 failure modes. Deterministic assertions (**100% GREEN**) + Calibrated LLM Judge (**92.0% Agreement**, $\kappa = 0.84$). |
| **`python run.py --trajectory`** | **Trajectory Evaluation Suite** | 10 tickets. Tool-Choice Accuracy (**100.0%**), Outcome-vs-Trajectory Gap (**0.0%**, closed from 30%). |
| **`python run.py --second-contact`** | **Bonus: Second-Contact Eval** | Models realistic customer follow-ups. Reports Deflection Rate (**100%**) vs Simulated Re-Open Rate (**50%**) as an honest pair. |
| **`python run.py --mcp-client`** | **Thursday Fresh-Eyes MCP Client** | Independent external client querying `search_help_center` & `check_customer_entitlement` live over MCP stdio JSON-RPC. |
| **`python run.py --server`** | **Universal Web Application** | FastAPI + HTML5/CSS3 interface at `http://127.0.0.1:8050` with customer chatbot & admin audit portals. |

---

## 📖 The Problem & Business Brief

The client operates a 14-person Tier-1 customer support team handling ~2,000 tickets per month. 
- **The Bottleneck:** Half of all tickets are simple inquiries answered by an agent copying a macro from a help-center article the customer could have read. Easy tickets bury difficult ones, driving first-response time on critical escalations to **9 hours**.
- **The Critical CEO Escalation:** Two of their last three escalations to the executive CEO came from an agent quoting the **retired 14-day refund policy** to a customer who was on the **current 30-day satisfaction policy**, because the old macro was still in the Zendesk folder. Both policies exist in the help center because legacy pre-2024 accounts remain on old terms.
- **The Solution:** An integrated assistant that:
  1. Checks actual customer contract entitlement via CRM tools **before** discussing refund windows.
  2. Resolves Tier-1 tickets using hybrid RAG with clickable citations that explicitly name **which** refund-policy version was applied (`[refund-and-returns-policy-30day-v2]`).
  3. Proactively **escalates** to Tier-2 Operations rather than guessing when a ticket involves chargebacks or complex disputes.

---

## 🏗️ Architecture at a Glance

```text
Incoming Ticket (Web/Email) ──► PII Sanitizer (Masks emails, cards, addresses)
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
       [Chargeback / Dispute?]              [Tier-1 Inquiry]
                     │                               │
            (YES)    │                     (NO)      │
                     ▼                               ▼
        MCP: escalate_ticket            MCP: check_customer_entitlement
        Route: Tier-2 Queue             Returns: "30-day-current" or "14-day-legacy"
        SLA: 4 business hours                        │
                                                     ▼
                                        MCP: fetch_order_details
                                        Verifies: Amount, days_since_purchase
                                                     │
                                                     ▼
                                        MCP: search_help_center (Hybrid RAG)
                                        Retrieves: Markdown chunks + slug
                                                     │
                                                     ▼
                                        Synthesize Grounded Response
                                        Clickable: [refund-and-returns-policy-30day-v2]
                                                     │
                                                     ▼
                                        Telemetry & Langfuse Span Tree
                                        Cost: $0.0004666 | Latency: ~5ms | PII Held
```

---

## 📁 Submission Checklist Artifacts

All required Week 12 Capstone submission documents are completed and linked below:

| Checklist Requirement | Artifact Document | Core Findings & Evidence |
|---|---|---|
| **1. Single Entry Point & README** | [`run.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/run.py) & [`README.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/README.md) | Single command executes all suites and demos. Tested with zero coaching. |
| **2. Tuesday's Unedited Seam List** | [`tuesday_seams.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/tuesday_seams.md) | 10 seams logged on Tuesday. Marked `FIXED`, `ACCEPTED`, or `RAN-OUT-OF-TIME`. |
| **3. One-Page Architecture Sketch** | [`architecture.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/architecture.md) | Box-and-arrow diagrams, model call sites, and per-stage cost attribution. |
| **4. Integrated Eval Suite Report** | [`eval_report.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/eval_report.md) | Pass rate per mode, 92.0% judge agreement ($\kappa = 0.84$), and cold non-coverage statement. |
| **5. Re-Scored Error Taxonomy** | [`taxonomy_integrated.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/taxonomy_integrated.md) | 6 named modes. Identifies `M6_tool_rag_policy_collision` born of integration. |
| **6. Trajectory Evaluation Results** | [`trajectory_results.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trajectory_results.md) | 10 tickets. Closed the 30% Outcome-vs-Trajectory Gap on Ticket `TCK-101`. |
| **7. Multi-Span Production Trace** | [`trace_integrated.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/trace_integrated.json) | Unified `trace_id` surviving agent & MCP hops. Per-span cost & latency. PII line held. |
| **8. Top 3 Known Weaknesses** | [`wednesday_weaknesses.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/wednesday_weaknesses.md) | Written Wednesday before anyone asked: 2nd contact gap, shipping labels, rate limit. |
| **9. Unit Economics & 10x Plan** | [`cost_and_tenx.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/cost_and_tenx.md) | $0.0004666 / ticket. Proves rate limit breaks first at 144,764 TPM vs 100k quota. |
| **10. Thursday Fresh-Eyes Note** | [`fresh_eyes_note.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/fresh_eyes_note.md) | Marcus Vance (Reliability Squad) review notes, stumbles, and interpreter bootstrapping fix. |
| **11. 10-Minute Demo Script & Q&A** | [`demo_script.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/demo_script.md) | 4-part timed speaking script + defense against 5 hostile questions. |
| **12. Bonus: Second-Contact Eval** | [`second_contact_eval.md`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/second_contact_eval.md) | Deflection Rate (100%) vs Simulated Re-Open Rate (50%) honest pair. |

---

## 📊 Key Evaluation Metrics Summary

| Metric | Before Integration | After Integration | Delta | Status |
|---|:---:|:---:|:---:|:---:|
| **Superseded Policy Citation Rate** | 20.0% (5/25) | **0.0% (0/26)** | -20.0% | **ELIMINATED** |
| **Deterministic Assertion Pass Rate** | 96.2% (25/26) | **100.0% (26/26)** | +3.8% | **SUITE GREEN** |
| **LLM Judge vs Human Agreement** | 68.0% ($\kappa = 0.34$) | **92.0% ($\kappa = 0.84$)** | +24.0% | **HIGH RELIABILITY** |
| **Outcome-vs-Trajectory Gap** | 30.0% (Silent Bypass) | **0.0% (Preconditions)** | -30.0% | **CLOSED** |
| **Initial Automated Deflection** | — | **100.0% (10/10)** | — | **MEASURED** |
| **Simulated 2nd-Contact Re-Open** | — | **50.0% (5/10)** | — | **HONEST PAIR** |
| **Cost per Deflected Ticket** | $14.00 (Human) | **$0.0004666** | -99.997% | **SAVINGS: $14k/mo** |
| **10x Bottleneck Metric** | — | **144,764 TPM** | — | Rate limit breaks first |

---

## 🛠️ Environment Configuration

System configuration is stored in `.env` (a working template is provided in `.env.example`):

```bash
# Langfuse Observability & Telemetry (Optional - falls back to local traces_live.jsonl)
LANGFUSE_PUBLIC_KEY="pk-lf-xxxxxxxxxxxxxxxx"
LANGFUSE_SECRET_KEY="sk-lf-xxxxxxxxxxxxxxxx"
LANGFUSE_BASE_URL="https://us.cloud.langfuse.com"

# Anthropic Claude API Key (Optional - cached evaluations run deterministically offline)
ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxx"
```

---

## 🤝 Authorship & Defense
- **Lead AI Systems Engineer:** Iswarya Sunkara
- **Reviewers:** Marcus Vance (Reliability Engineering) & Elena Rostova (Support Operations)
- **Gate:** Module 6 (Production & Capstone) $\to$ Certified Applied AI Engineer

