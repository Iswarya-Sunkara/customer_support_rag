import os
from typing import Dict, Any, List
from pathlib import Path

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except Exception as e:
    LANGFUSE_AVAILABLE = False
    print(f"[Langfuse Import Notice]: {e}")



# Auto-load .env file if available
PROJECT_DIR = Path(__file__).resolve().parent.parent
env_file = PROJECT_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")


class LangfuseTraceLogger:
    """
    Langfuse Integration Helper for Customer Support RAG System.
    Logs RAG execution steps, retrieval contexts, model parameters, and failure tags.
    """
    def __init__(self):
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
        self.host = os.getenv("LANGFUSE_BASE_URL", os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")).strip()
        
        self.recent_traces: List[Dict[str, Any]] = []
        self.traces_file = PROJECT_DIR / "traces_live.jsonl"
        self._load_cached_traces()

        if LANGFUSE_AVAILABLE and self.public_key and self.secret_key:
            try:
                self.client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=self.host
                )
                self.enabled = True
                print(f"[Langfuse] Initialized live telemetry client for host {self.host} successfully.")
            except Exception as e:
                self.client = None
                self.enabled = False
                print(f"[Langfuse] Connection error: {e}")
        else:
            self.client = None
            self.enabled = False
            print(f"[Langfuse] SDK available: {LANGFUSE_AVAILABLE}, Public key present: {bool(self.public_key)}, Secret key present: {bool(self.secret_key)}")

    def _load_cached_traces(self):
        """Loads locally stored live traces if present."""
        if self.traces_file.exists():
            import json
            try:
                with open(self.traces_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.recent_traces.append(json.loads(line))
            except Exception:
                pass

    def get_status(self) -> Dict[str, Any]:
        """Returns the current Langfuse configuration and telemetry status."""
        return {
            "enabled": self.enabled,
            "sdk_available": LANGFUSE_AVAILABLE,
            "has_public_key": bool(self.public_key),
            "has_secret_key": bool(self.secret_key),
            "host": self.host,
            "cloud_url": self.host,
            "total_live_traces": len(self.recent_traces)
        }

    def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent RAG query traces."""
        return list(reversed(self.recent_traces[-limit:]))

    def log_rag_trace(
        self,
        trace_id: str,
        question: str,
        answer: str,
        retrieved_chunks: List[Dict[str, Any]],
        model_params: Dict[str, Any],
        category_tag: str = "",
        status: str = "success"
    ):
        """
        Logs a single RAG trace execution to Langfuse dashboard and locally.
        """
        import datetime
        import json
        
        record = {
            "trace_id": trace_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "question": question,
            "answer": answer,
            "status": status,
            "category_tag": category_tag,
            "model_params": model_params,
            "retrieved_chunks": retrieved_chunks,
            "cloud_synced": self.enabled
        }
        self.recent_traces.append(record)
        
        # Save to local traces_live.jsonl
        try:
            with open(self.traces_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass

        if not self.enabled:
            print(f"[Langfuse Telemetry] Recorded trace `{trace_id}` locally (Cloud sync waiting for API keys).")
            return
            
        try:
            # Start RAG Observation Span
            span = self.client.start_observation(
                name="customer_support_rag_query",
                as_type="SPAN",
                input={"question": question},
                output={"answer": answer, "status": status},
                metadata={
                    "trace_id": trace_id,
                    "category_tag": category_tag,
                    "model_params": model_params,
                    "retrieved_chunks": retrieved_chunks
                }
            )
            # Flush telemetry queue
            self.client.flush()
            print(f"[Langfuse Live] Successfully streamed trace `{trace_id}` to dashboard ({self.host}).")
        except Exception as e:
            print(f"[Langfuse Streaming Warning]: {e}")

if __name__ == "__main__":
    logger = LangfuseTraceLogger()
    logger.log_rag_trace(
        trace_id="tr_demo_01",
        question="If my automatic subscription payment fails on day 1, when is the next retry attempt made?",
        answer="Cloudflare will retry up to 5 times over 5 days.",
        retrieved_chunks=[{"chunk_id": "article_01_chunk_14", "score": "54.1%"}],
        model_params={"model": "all-MiniLM-L6-v2", "mode": "week4_hybrid"},
        category_tag="billing_grace"
    )


