import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.document_parser import parse_document
from src.dynamic_rag import DynamicRAGEngine

def test_universal_parser():
    print("==================================================", flush=True)
    print("TEST 1: Testing Universal Document Parser", flush=True)
    print("==================================================", flush=True)

    test_files = {
        "sample.txt": b"Customer Support Policy:\nStandard refund processing takes 3-5 business days. For urgent billing issues, contact support@company.com.",
        "sample.md": b"# System Guide\n## Troubleshooting\nTo clear cache, navigate to Settings > Advanced > Clear Storage.",
        "data.csv": b"Ticket_ID,Issue_Type,Status,Resolution_Time_Hours\nTCK-101,Login Failure,Resolved,2\nTCK-102,Billing Error,Pending,24",
        "script.py": b"def calculate_tax(amount):\n    # Standard tax rate is 15%\n    return amount * 0.15",
        "custom_config.json": b'{"server": "prod-1", "port": 8080, "timeout_sec": 30}',
        "random_binary.bin": b"\x00\x01\x02SECRET_KEY=ABC123XYZ987\x00\x00\xFF\xFEVERSION_NUMBER=4.2.0\x00\x00"
    }

    for fname, fbytes in test_files.items():
        res = parse_document(file_bytes=fbytes, filename=fname)
        print(f"[{res['extension'].upper()}] File: {res['filename']} ({res['size_bytes']} bytes) -> Chars: {res['char_count']}, Lines: {res['line_count']}", flush=True)
        print(f"   Status: {res['status']} | Msg: {res['message']}", flush=True)
        print(f"   Snippet: {res['text'][:100].strip()}\n", flush=True)

    print("==================================================", flush=True)
    print("TEST 2: Testing Dynamic RAG Engine Ingestion & Q&A", flush=True)
    print("==================================================", flush=True)

    engine = DynamicRAGEngine()

    # Ingest test files
    for fname, fbytes in test_files.items():
        ingest_res = engine.add_document(fname, fbytes)
        print(f"Indexed {ingest_res['filename']}: {ingest_res['chunks_added']} chunks added.", flush=True)

    # Ask Questions
    questions = [
        "How long does standard refund processing take?",
        "What port does the server configuration use?",
        "What is the resolution time for TCK-101 in the CSV?",
        "What is the SECRET_KEY from the binary file?"
    ]

    for q in questions:
        print(f"\n--------------------------------------------------", flush=True)
        print(f"QUESTION: {q}", flush=True)
        print(f"--------------------------------------------------", flush=True)
        res = engine.query(q)
        print(f"ANSWER:\n{res['answer']}\n", flush=True)
        print("CITATIONS:", flush=True)
        for c in res["citations"]:
            print(f"  - [{c['similarity_score']}] File: {c['filename']} | Chunk: {c['chunk_id']}", flush=True)

    print("\n[SUCCESS] Universal Parser and Dynamic RAG Test Completed Successfully!", flush=True)

if __name__ == "__main__":
    test_universal_parser()
