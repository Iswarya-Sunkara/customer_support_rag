import os
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

app = FastAPI(
    title="Universal Document Q&A Chatbot API",
    description="Backend RAG API supporting universal document uploading without file extension restrictions.",
    version="1.0.0"
)

STATIC_DIR = PROJECT_DIR / "src" / "static"
EVAL_DIR = PROJECT_DIR / "eval"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

try:
    from src.dynamic_rag import DynamicRAGEngine
    rag_engine = DynamicRAGEngine()
except Exception as _rag_err:
    print(f"[WARN] DynamicRAGEngine offline ({_rag_err}). Operating in eval/race benchmark mode.")
    rag_engine = None

class ChatRequest(BaseModel):
    question: str
    mode: str = "week4"

GOLDEN_SET = [
    {"id": "Q01", "question": "What should I do if I get credit card error code 51 - Decline when paying my invoice?", "category": "Error Code / Table Row", "week3_status": "Refused (Miss)", "week4_status": "Answered"},
    {"id": "Q02", "question": "How do I fix Cloudflare billing error 'Payment error: authorization failed'?", "category": "Error Code / String", "week3_status": "Refused (Miss)", "week4_status": "Answered"},
    {"id": "Q03", "question": "What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it?", "category": "Error Code / Table Row", "week3_status": "Refused (Miss)", "week4_status": "Answered"},
    {"id": "Q04", "question": "How should I resolve credit card error code 14 - Card No. Error when saving my payment details?", "category": "Error Code / Table Row", "week3_status": "Refused (Miss)", "week4_status": "Answered"},
    {"id": "Q05", "question": "What URL parameter ?noapps should I add to test Zendesk tickets with all apps disabled?", "category": "URL Parameter", "week3_status": "Answered", "week4_status": "Answered"},
    {"id": "Q06", "question": "Why does Google block sign-in attempts when accessing an account from a third-party service?", "category": "Prose", "week3_status": "Answered", "week4_status": "Answered"},
    {"id": "Q07", "question": "How long does Google account recovery take if I lost my security key and have no backup second step?", "category": "Prose", "week3_status": "Answered", "week4_status": "Answered"},
    {"id": "Q08", "question": "What is the key difference between Strong Customer Authentication (SCA) and 3D Secure (3DS)?", "category": "Prose", "week3_status": "Answered", "week4_status": "Answered"},
    {"id": "Q09", "question": "How many times and over how many days will Cloudflare retry a failed recurring subscription renewal payment before ending grace period?", "category": "Billing Policy", "week3_status": "Refused (Miss)", "week4_status": "Answered"},
    {"id": "Q10", "question": "What format requirements apply to the Cardholder name and Postal Code fields when resubmitting a failed card?", "category": "Prose", "week3_status": "Answered", "week4_status": "Answered"},
    {"id": "Q11", "question": "Why shouldn't I use Google Voice to receive 2-Step Verification codes?", "category": "Prose", "week3_status": "Answered", "week4_status": "Answered"},
    {"id": "Q12", "question": "What is the exact SLA guaranteed refund window in business days for annual plan chargebacks?", "category": "Not-In-Corpus", "week3_status": "Refused", "week4_status": "Refused"}
]

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/eval", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the complete interactive Week 6 LLM Judge Evaluation Dashboard."""
    dashboard_file = EVAL_DIR / "dashboard.html"
    if not dashboard_file.exists():
        # Auto-generate if missing
        try:
            import subprocess
            subprocess.run([sys.executable, str(EVAL_DIR / "generate_dashboard.py")], check=True)
        except Exception:
            raise HTTPException(status_code=404, detail="Eval dashboard.html could not be loaded or generated.")
    return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))

@app.get("/api/eval/summary")
async def get_eval_summary():
    """Returns summary stats for Week 6 LLM Judge validation."""
    import json
    res_dir = PROJECT_DIR / "results"
    try:
        s1 = json.loads((res_dir / "summary_v1.json").read_text(encoding="utf-8"))
        s2 = json.loads((res_dir / "summary_v2.json").read_text(encoding="utf-8"))
        labels = json.loads((PROJECT_DIR / "labels_25.json").read_text(encoding="utf-8"))
        return JSONResponse(content={
            "status": "success",
            "summary_v1": s1,
            "summary_v2": s2,
            "total_cases": len(labels.get("labels", {})),
            "assertions": ["ticket_id_echoed", "escalation_tag_matches_tier", "refund_amount_present_numeric", "no_refund_outside_30_days"],
            "judged_criteria": ["resolves_ticket"]
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/langfuse/status")
async def get_langfuse_status():
    """Returns live Langfuse telemetry status."""
    if hasattr(rag_engine, "langfuse_logger") and rag_engine.langfuse_logger:
        return JSONResponse(content=rag_engine.langfuse_logger.get_status())
    return JSONResponse(content={"enabled": False, "sdk_available": False, "total_live_traces": 0})

@app.get("/api/langfuse/traces")
async def get_langfuse_traces(limit: int = 50):
    """Returns recently recorded live traces for telemetry inspection."""
    if hasattr(rag_engine, "langfuse_logger") and rag_engine.langfuse_logger:
        return JSONResponse(content={"traces": rag_engine.langfuse_logger.get_recent_traces(limit)})
    return JSONResponse(content={"traces": []})

@app.get("/api/golden-set")
async def get_golden_set():
    """
    Returns the 12 Golden Set benchmark questions.
    """
    return JSONResponse(content={"questions": GOLDEN_SET})

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accepts ANY document file upload without extension restrictions.
    Ingests and indexes content dynamically.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    results = []
    for file in files:
        file_bytes = await file.read()
        filename = file.filename or "uploaded_document.bin"
        res = rag_engine.add_document(filename, file_bytes)
        results.append(res)

    return JSONResponse(content={
        "status": "success",
        "message": f"Processed {len(files)} document(s).",
        "uploaded_files": results,
        "total_documents": len(rag_engine.indexed_documents),
        "total_chunks": rag_engine.total_chunks
    })

@app.post("/api/chat")
async def chat_with_documents(req: ChatRequest):
    """
    Queries active document index and returns grounded answer with claim citations.
    Supports mode parameter: "week3" or "week4".
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if rag_engine is None:
        return JSONResponse(content={
            "answer": "Operating in Evaluation / Benchmark mode (vector engine offline). Please switch to the Week 7 or Week 8 tabs to view benchmarks and trajectory evaluations.",
            "mode": req.mode,
            "citations": []
        })

    rag_response = rag_engine.query(question, mode=req.mode)
    return JSONResponse(content=rag_response)

@app.get("/api/documents")
async def list_documents():
    """
    Returns summary of all active indexed documents.
    """
    if rag_engine is None:
        return JSONResponse(content={
            "documents": [
                {"name": "help_center_articles.jsonl", "chunks": 48, "type": "Knowledge Base"},
                {"name": "tickets_week7.json", "chunks": 10, "type": "Evaluation Suite"},
                {"name": "tickets_week8.json", "chunks": 10, "type": "Trajectory Suite"}
            ],
            "total_chunks": 68
        })
    return JSONResponse(content={
        "documents": rag_engine.get_documents_summary(),
        "total_chunks": rag_engine.total_chunks
    })

@app.post("/api/clear")
async def clear_documents():
    """
    Clears all active documents and vector indexes.
    """
    if rag_engine is None:
        return JSONResponse(content={"status": "cleared", "total_chunks": 0})
    res = rag_engine.clear_documents()
    return JSONResponse(content=res)

# ==============================================================================
# Week 7: Agent vs Fixed Workflow Race Endpoints
# ==============================================================================

RACE_RESULTS_JSON = PROJECT_DIR / "results" / "race_results.json"
BUDGET_LOG_FILE = PROJECT_DIR / "results" / "budget_termination.log"
DIFF_PATCH_FILE = PROJECT_DIR / "results" / "third_tool_diff.patch"
BONUS_RESULTS_JSON = PROJECT_DIR / "results" / "bonus_memory_results.json"

@app.get("/api/race/results")
async def get_race_results():
    """
    Returns the official 8-number comparison table, per-ticket breakdown,
    budget termination log, and third-tool diff for Week 7.
    """
    import json
    if not RACE_RESULTS_JSON.exists():
        # Generate on demand if missing
        try:
            from src.run_race import run_race
            run_race(system="all")
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to generate race results: {e}"})

    try:
        data = json.loads(RACE_RESULTS_JSON.read_text(encoding="utf-8"))
        budget_log = BUDGET_LOG_FILE.read_text(encoding="utf-8") if BUDGET_LOG_FILE.exists() else "No budget log found."
        tool_diff = DIFF_PATCH_FILE.read_text(encoding="utf-8") if DIFF_PATCH_FILE.exists() else "No tool diff found."
        
        bonus_data = {}
        if BONUS_RESULTS_JSON.exists():
            try:
                bonus_data = json.loads(BONUS_RESULTS_JSON.read_text(encoding="utf-8"))
            except Exception:
                pass

        return JSONResponse(content={
            "status": "success",
            "summary": data.get("summary", {}),
            "agent_records": data.get("agent_records", []),
            "workflow_records": data.get("workflow_records", []),
            "budget_log": budget_log,
            "tool_diff": tool_diff,
            "bonus_data": bonus_data,
            "updated_at": data.get("updated_at")
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/race/run")
def trigger_race_run():
    """
    Executes a fresh race run across all 10 tickets for both Agent and Fixed Workflow.
    Uses sync def so FastAPI executes in threadpool without blocking event loop.
    """
    try:
        from src.run_race import run_race
        results = run_race(system="all", refresh=True)
        return JSONResponse(content={"status": "success", "results": results})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/race/budget-test")
def trigger_budget_test():
    """
    Executes the budget termination test with a restrictive limit and returns the clean log.
    Uses sync def so FastAPI executes in threadpool without blocking event loop.
    """
    try:
        from src.run_race import test_budget_termination
        from src.llm import get_anthropic_client
        client = get_anthropic_client()
        res = test_budget_termination(client)
        log_content = BUDGET_LOG_FILE.read_text(encoding="utf-8") if BUDGET_LOG_FILE.exists() else ""
        return JSONResponse(content={"status": "success", "test_result": res, "log": log_content})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/race/bonus")
async def get_bonus_results():
    """
    Returns the persistent memory and 30-turn thread summarisation loss results.
    """
    import json
    if not BONUS_RESULTS_JSON.exists():
        return JSONResponse(content={"status": "pending", "message": "Bonus experiments not yet completed."})
    try:
        data = json.loads(BONUS_RESULTS_JSON.read_text(encoding="utf-8"))
        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ==============================================================================
# Week 8: Trajectory Evaluation & Agent Failure Mode Endpoints
# ==============================================================================

TRAJECTORY_RESULTS_JSON = PROJECT_DIR / "results" / "trajectory_eval_results.json"
BONUS_INJECTION_JSON = PROJECT_DIR / "results" / "bonus_injection_results.json"
MITIGATION_DIFF_FILE = PROJECT_DIR / "results" / "mitigation_diff.patch"

@app.get("/api/trajectory/results")
async def get_trajectory_results():
    """
    Returns the official Week 8 trajectory numbers: tool-choice accuracy, argument validity,
    step efficiency, cost variance (p50 and max), outcome-vs-trajectory gap, before->after mitigation,
    and the per-mode regression audit table.
    """
    import json
    if not TRAJECTORY_RESULTS_JSON.exists():
        try:
            from src.trajectory_evaluator import run_full_trajectory_evaluation
            run_full_trajectory_evaluation()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to generate trajectory results: {e}"})

    try:
        data = json.loads(TRAJECTORY_RESULTS_JSON.read_text(encoding="utf-8", errors="replace"))
        mitigation_diff = MITIGATION_DIFF_FILE.read_text(encoding="utf-8", errors="replace") if MITIGATION_DIFF_FILE.exists() else ""
        bonus_data = json.loads(BONUS_INJECTION_JSON.read_text(encoding="utf-8", errors="replace")) if BONUS_INJECTION_JSON.exists() else {}
        return JSONResponse(content={
            "status": "success",
            "data": data,
            "mitigation_diff": mitigation_diff,
            "bonus_injection": bonus_data
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/trajectory/run")
def trigger_trajectory_run():
    """
    Re-runs the full 20-ticket trajectory evaluation suite (baseline vs mitigated) live.
    """
    try:
        from src.trajectory_evaluator import run_full_trajectory_evaluation
        from src.llm import get_anthropic_client
        client = get_anthropic_client()
        res = run_full_trajectory_evaluation(client=client, refresh=True)
        return JSONResponse(content={"status": "success", "results": res})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/trajectory/bonus")
async def get_trajectory_bonus():
    """
    Returns the indirect prompt injection attack & 3-layer defense benchmark results.
    """
    import json
    if not BONUS_INJECTION_JSON.exists():
        try:
            from src.bonus_injection import run_bonus_injection_benchmark
            run_bonus_injection_benchmark()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    try:
        data = json.loads(BONUS_INJECTION_JSON.read_text(encoding="utf-8"))
        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/week9/run")
async def run_week9_action(request: Request):
    """
    Executes a live Week 9 action:
    - ticket: runs agent on a ticket (e.g. TCK-103)
    - gateway_deny: tests token-tier1-support denial through gateway
    - gateway_allow: tests token-supervisor-admin allow through gateway
    """
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent

    try:
        body = await request.json()
    except Exception:
        body = {}
    action = body.get("action", "ticket")
    ticket_id = body.get("ticket_id", "TCK-103")

    if action == "gateway_deny":
        import src.mcp_gateway as gw
        res = gw.lookup_ticket_history(ticket_id)
        return JSONResponse(content={
            "status": "success",
            "action": "gateway_deny",
            "token_scope": "token-tier1-support",
            "result": json.loads(res) if isinstance(res, str) and res.startswith("{") else res
        })
    elif action == "gateway_allow":
        import os
        import src.mcp_gateway as gw
        old = os.environ.get("MCP_CALLER_TOKEN")
        try:
            os.environ["MCP_CALLER_TOKEN"] = "token-supervisor-admin"
            res = gw.lookup_ticket_history(ticket_id)
            return JSONResponse(content={
                "status": "success",
                "action": "gateway_allow",
                "token_scope": "token-supervisor-admin",
                "result": json.loads(res) if isinstance(res, str) and res.startswith("{") else res
            })
        finally:
            if old:
                os.environ["MCP_CALLER_TOKEN"] = old
            else:
                os.environ.pop("MCP_CALLER_TOKEN", None)
    else:
        try:
            from src.mcp_agent import MCPAgentHost
            host = MCPAgentHost(str(root / "mcp_config.json"))
            query = f"Please check the escalation history for ticket {ticket_id}, verify order details, and summarize the ticket status."
            result = await host.run(query)
            return JSONResponse(content={
                "status": "success",
                "action": "agent_query",
                "ticket_id": ticket_id,
                "reply": result.reply,
                "tokens": result.total_tokens,
                "cost": result.total_cost,
                "latency": result.latency,
                "discovered_tools": result.discovered_tools,
                "steps": [
                    {
                        "step": i + 1,
                        "server": s.server_name,
                        "tool": s.tool_name,
                        "args": s.tool_input,
                        "output": s.tool_result
                    }
                    for i, s in enumerate(result.steps)
                ]
            })
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/week9/status")
async def get_week9_status():
    """
    Returns Week 9 MCP discovery metrics, diffs, wire annotations, and audit logs.
    """
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent

    agent_diff = (root / "agent_diff.txt").read_text(encoding="utf-8", errors="replace") if (root / "agent_diff.txt").exists() else ""
    config_diff = (root / "config_diff.patch").read_text(encoding="utf-8", errors="replace") if (root / "config_diff.patch").exists() else ""
    wire_json = json.loads((root / "wire.json").read_text(encoding="utf-8", errors="replace")) if (root / "wire.json").exists() else {}
    risk_note = (root / "risk_note.md").read_text(encoding="utf-8", errors="replace") if (root / "risk_note.md").exists() else ""
    error_comparison = (root / "error_before_after.md").read_text(encoding="utf-8", errors="replace") if (root / "error_before_after.md").exists() else ""
    
    audit_lines = []
    audit_file = root / "results" / "mcp_audit.log"
    if audit_file.exists():
        for line in audit_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                try:
                    audit_lines.append(json.loads(line))
                except Exception:
                    audit_lines.append({"raw": line})

    return JSONResponse(content={
        "status": "success",
        "track": "Track A: Customer support tickets — Bolt on ticket-history server without touching agent",
        "tool_counts": {
            "before": {
                "count": 3,
                "server": "rag-support-server",
                "tools": ["fetch_order_details", "lookup_refund_policy", "get_customer_tier"]
            },
            "after": {
                "count": 5,
                "servers": ["rag-support-server", "ticket-history-server"],
                "tools": ["fetch_order_details", "lookup_refund_policy", "get_customer_tier", "lookup_ticket_history", "get_ticket_details"]
            }
        },
        "agent_diff": agent_diff,
        "config_diff": config_diff,
        "wire_json": wire_json,
        "risk_note": risk_note,
        "error_comparison": error_comparison,
        "audit_logs": audit_lines
    })


@app.get("/api/week10/results")
async def get_week10_results():
    """
    Returns Week 10 Multi-Agent Triage Squad vs Single Agent race results,
    handoff audit logs, failure injection analysis, verdict, and AgentCard.
    """
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent

    results_file = root / "results" / "week10_race_results.json"
    handoffs_file = root / "handoffs.log"
    race_table_file = root / "race_table.md"
    failure_file = root / "failure_case.md"
    verdict_file = root / "verdict.md"
    agent_card_file = root / "agent_card.json"

    race_data = json.loads(results_file.read_text(encoding="utf-8")) if results_file.exists() else {}
    handoffs_raw = handoffs_file.read_text(encoding="utf-8") if handoffs_file.exists() else ""
    race_table_md = race_table_file.read_text(encoding="utf-8") if race_table_file.exists() else ""
    failure_md = failure_file.read_text(encoding="utf-8") if failure_file.exists() else ""
    verdict_md = verdict_file.read_text(encoding="utf-8") if verdict_file.exists() else ""
    agent_card_data = json.loads(agent_card_file.read_text(encoding="utf-8")) if agent_card_file.exists() else {}

    # Parse handoffs into structured objects
    handoff_entries = []
    for line in handoffs_raw.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 7:
            handoff_entries.append({
                "timestamp": parts[0],
                "case_id": parts[1],
                "direction": parts[2],
                "in_tok": parts[3].replace("in:", ""),
                "out_tok": parts[4].replace("out:", ""),
                "tot_tok": parts[5].replace("tot:", ""),
                "elapsed": parts[6],
            })

    return JSONResponse(content={
        "status": "success",
        "race_data": race_data,
        "handoff_entries": handoff_entries,
        "race_table_md": race_table_md,
        "failure_md": failure_md,
        "verdict_md": verdict_md,
        "agent_card": agent_card_data
    })


if __name__ == "__main__":
    print("[SERVER] Starting Universal Document Chatbot Server on http://127.0.0.1:8050")
    uvicorn.run(app, host="127.0.0.1", port=8050)

