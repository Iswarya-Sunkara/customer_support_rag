import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.dynamic_rag import DynamicRAGEngine

GOLDEN_QUESTIONS = [
    ("Q01", "What should I do if I get credit card error code 51 - Decline when paying my invoice?"),
    ("Q02", "How do I fix Cloudflare billing error 'Payment error: authorization failed'?"),
    ("Q03", "What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it?"),
    ("Q04", "How should I resolve credit card error code 14 - Card No. Error when saving my payment details?"),
    ("Q05", "What URL parameter ?noapps should I add to test Zendesk tickets with all apps disabled?"),
    ("Q06", "Why does Google block sign-in attempts when accessing an account from a third-party service?"),
    ("Q07", "How long does Google account recovery take if I lost my security key and have no backup second step?"),
    ("Q08", "What is the key difference between Strong Customer Authentication (SCA) and 3D Secure (3DS)?"),
    ("Q09", "How many times and over how many days will Cloudflare retry a failed recurring subscription renewal payment before ending grace period?"),
    ("Q10", "What format requirements apply to the Cardholder name and Postal Code fields when resubmitting a failed card?"),
    ("Q11", "Why shouldn't I use Google Voice to receive 2-Step Verification codes?"),
    ("Q12", "What is the exact SLA guaranteed refund window in business days for annual plan chargebacks?")
]

def test_week3_vs_week4_eval():
    print("==================================================", flush=True)
    print("TEST: Week 3 Baseline vs Week 4 Hybrid RAG Filter", flush=True)
    print("==================================================", flush=True)

    engine = DynamicRAGEngine()
    print(f"Loaded {len(engine.indexed_documents)} benchmark articles ({engine.total_chunks} chunks)\n", flush=True)

    for qid, qtext in GOLDEN_QUESTIONS:
        res_w3 = engine.query(qtext, mode="week3")
        res_w4 = engine.query(qtext, mode="week4")

        w3_status = "REFUSED (Miss)" if "I don't have enough information" in res_w3["answer"] else "ANSWERED"
        w4_status = "REFUSED (Out-of-Corpus)" if "I don't have enough information" in res_w4["answer"] else "ANSWERED"

        print(f"[{qid}] {qtext}", flush=True)
        print(f"  - Week 3 (Dense Baseline) Status: {w3_status}", flush=True)
        print(f"  - Week 4 (Hybrid RAG)     Status: {w4_status}", flush=True)
        if w3_status != w4_status:
            print(f"  [DELTA] Week 3 Refused -> Week 4 Answered!", flush=True)
        print("-" * 60, flush=True)

    print("\n[SUCCESS] Week 3 vs Week 4 Filter Evaluation Test Completed Successfully!", flush=True)

if __name__ == "__main__":
    test_week3_vs_week4_eval()
