import os
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.dynamic_rag import DynamicRAGEngine

app = FastAPI(
    title="Universal Document Q&A Chatbot API",
    description="Backend RAG API supporting universal document uploading without file extension restrictions.",
    version="1.0.0"
)

STATIC_DIR = PROJECT_DIR / "src" / "static"
EVAL_DIR = PROJECT_DIR / "eval"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Instantiate global RAG Engine
rag_engine = DynamicRAGEngine()

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

    rag_response = rag_engine.query(question, mode=req.mode)
    return JSONResponse(content=rag_response)

@app.get("/api/documents")
async def list_documents():
    """
    Returns summary of all active indexed documents.
    """
    return JSONResponse(content={
        "documents": rag_engine.get_documents_summary(),
        "total_chunks": rag_engine.total_chunks
    })

@app.post("/api/clear")
async def clear_documents():
    """
    Clears all active documents and vector indexes.
    """
    res = rag_engine.clear_documents()
    return JSONResponse(content=res)

if __name__ == "__main__":
    print("[SERVER] Starting Universal Document Chatbot Server on http://127.0.0.1:8050")
    uvicorn.run(app, host="127.0.0.1", port=8050)
