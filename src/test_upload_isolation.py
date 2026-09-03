import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.dynamic_rag import DynamicRAGEngine

def test_upload_isolation():
    print("==========================================", flush=True)
    print("TEST: Upload List Isolation Verification", flush=True)
    print("==========================================", flush=True)

    engine = DynamicRAGEngine()
    
    # 1. Initial State: Benchmark loaded in background, user list must be 0!
    user_docs_initial = engine.get_documents_summary()
    print(f"Initial User Uploaded Files Count: {len(user_docs_initial)} (Expected: 0)", flush=True)
    assert len(user_docs_initial) == 0, "Error: Initial uploaded files list is not 0!"

    # 2. User uploads a document
    sample_content = b"BustleSpot Activity Report: User Sunkara Iswarya Total Hours 09:19 hrs Total Activity 46%"
    engine.add_document("Bustlespot_Report.pdf", sample_content, is_benchmark=False)

    user_docs_after = engine.get_documents_summary()
    print(f"After User Upload Files Count: {len(user_docs_after)} (Expected: 1)", flush=True)
    print(f"Uploaded File Name: {user_docs_after[0]['filename']}", flush=True)
    assert len(user_docs_after) == 1, "Error: Uploaded files count should be 1!"
    assert user_docs_after[0]['filename'] == "Bustlespot_Report.pdf", "Error: Wrong filename!"

    print("\n[SUCCESS] Upload List Isolation Verified Successfully!", flush=True)

if __name__ == "__main__":
    test_upload_isolation()
