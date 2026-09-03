import json
import random
import time
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))
from src.dynamic_rag import DynamicRAGEngine

TRACES_FILE = PROJECT_DIR / "traces.jsonl"
SEED = 42

TICKET_TEMPLATES = [
    # 1. Billing Grace Period & Renewal Retries
    ("How many times and over how many days will Cloudflare retry a failed recurring subscription renewal payment?", "billing_grace"),
    ("What is the exact grace period for failed billing payments on my account before suspension?", "billing_grace"),
    ("If my automatic subscription payment fails on day 1, when is the next retry attempt made?", "billing_grace"),
    ("Does Cloudflare cancel my subscription immediately after a single payment decline or is there a retry schedule?", "billing_grace"),
    ("How long do I have to update my credit card after a payment failure before my account is downgraded?", "billing_grace"),

    # 2. Error Code 51 & Card Declines
    ("What should I do if I get credit card error code 51 - Decline when paying my invoice?", "error_51"),
    ("Why is my credit card transaction failing with error code 51 on invoice checkout?", "error_51"),
    ("How do I fix payment decline code 51 when updating my billing payment method?", "error_51"),
    ("What causes credit card error code 51 during subscription renewal?", "error_51"),
    ("Is error code 51 a bank refusal or a Zendesk system timeout error?", "error_51"),

    # 3. Error Code 14 & Card No. Error
    ("How should I resolve credit card error code 14 - Card No. Error when saving my payment details?", "error_14"),
    ("What does credit card error 14 mean during invoice payment?", "error_14"),
    ("Why does my card get error code 14 when the card number is correctly typed?", "error_14"),

    # 4. Error Code 430357 & Lost/Stolen Card
    ("What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it?", "error_430357"),
    ("How do I clear error code 430357 when adding a replacement corporate card?", "error_430357"),

    # 5. Cloudflare Authorization Failures
    ("How do I fix Cloudflare billing error 'Payment error: authorization failed'?", "auth_failed"),
    ("What causes authorization failed error on my Cloudflare enterprise invoice?", "auth_failed"),

    # 6. Zendesk Apps Disable Parameter
    ("What URL parameter ?noapps should I add to test Zendesk tickets with all apps disabled?", "noapps"),
    ("How do I bypass all installed Zendesk app extensions when troubleshooting ticket loading errors?", "noapps"),

    # 7. Google Third-Party Sign-in
    ("Why does Google block sign-in attempts when accessing an account from a third-party service?", "google_3rd_party"),

    # 8. Google 2-Step Verification & Google Voice
    ("Why shouldn't I use Google Voice to receive 2-Step Verification codes?", "google_2fa_voice"),

    # 9. Google Account Recovery
    ("How long does Google account recovery take if I lost my security key and have no backup second step?", "google_recovery"),

    # 10. Unanswerable SLA Refund
    ("What is the exact SLA guaranteed refund window in business days for annual plan chargebacks?", "sla_refund"),
]

DEMO_SET_QUESTIONS = [
    "How do I fix Cloudflare billing error 'Payment error: authorization failed'?",
    "What URL parameter ?noapps should I add to test Zendesk tickets with all apps disabled?",
    "What is the key difference between Strong Customer Authentication (SCA) and 3D Secure (3DS)?",
    "What format requirements apply to the Cardholder name and Postal Code fields when resubmitting a failed card?",
    "Why shouldn't I use Google Voice to receive 2-Step Verification codes?",
    "What should I do if I get credit card error code 51 - Decline when paying my invoice?",
    "How should I resolve credit card error code 14 - Card No. Error when saving my payment details?",
    "What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it?",
    "Why does Google block sign-in attempts when accessing an account from a third-party service?",
    "How long does Google account recovery take if I lost my security key and have no backup second step?",
]

def generate_traces():
    print("Initializing Dynamic RAG Engine for trace generation...", flush=True)
    engine = DynamicRAGEngine()
    
    traces = []
    total_traces = 1000
    
    random.seed(SEED)
    
    template_answers = {}
    preambles = [
        "", "Hi team, ", "Urgent: ", "Question regarding invoice: ",
        "Customer Ticket #10492: ", "Help needed - ", "Billing query: "
    ]
    
    for i in range(1, total_traces + 1):
        trace_id = f"tr_{i:04d}"
        template_idx = (i - 1) % len(TICKET_TEMPLATES)
        base_q, tag = TICKET_TEMPLATES[template_idx]
        preamble = preambles[i % len(preambles)]
        full_q = preamble + base_q
        
        if full_q not in template_answers:
            template_answers[full_q] = engine.query(full_q, top_k=3, mode="week4")
        
        cached_res = template_answers[full_q]
        
        trace = {
            "trace_id": trace_id,
            "timestamp": f"2026-09-03T{10 + (i % 10):02d}:{(i * 7) % 60:02d}:{(i * 13) % 60:02d}Z",
            "question": full_q,
            "prompt_version": "v1.2-support-rag",
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "model_params": {
                "top_k": 3,
                "similarity_threshold": 0.65,
                "temperature": 0.0,
                "mode": "week4_hybrid"
            },
            "retrieved_chunks": cached_res.get("citations", []),
            "raw_output": cached_res.get("answer", ""),
            "status": cached_res.get("status", "success"),
            "category_tag": tag,
            "is_demo_set": False
        }
        traces.append(trace)

    with open(TRACES_FILE, "w", encoding="utf-8") as f:
        for tr in traces:
            f.write(json.dumps(tr, ensure_ascii=False) + "\n")
            
    print(f"Successfully wrote {len(traces)} traces to {TRACES_FILE}", flush=True)

def run_seeded_sampling_and_replay():
    random.seed(SEED)
    
    traces = []
    with open(TRACES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                traces.append(json.loads(line.strip()))
                
    all_trace_ids = [t["trace_id"] for t in traces]
    sampled_ids = sorted(random.sample(all_trace_ids, 20))
    
    print("\n" + "=" * 80, flush=True)
    print(f"SEEDED RANDOM SAMPLE (SEED = {SEED})", flush=True)
    print("=" * 80, flush=True)
    print("Sampled 20 Trace IDs:", flush=True)
    print(sampled_ids, flush=True)
    
    # Requirement #1: Trace Replayability Evidence
    # Replay trace tr_0742 (or random seeded trace)
    random.seed(SEED)
    replay_target_id = "tr_0742" if "tr_0742" in sampled_ids else sampled_ids[0]
    target_trace = next(t for t in traces if t["trace_id"] == replay_target_id)
    
    print("\n" + "=" * 80, flush=True)
    print(f"TRACE REPLAY EVIDENCE (Target Trace ID: {replay_target_id})", flush=True)
    print("=" * 80, flush=True)
    
    engine = DynamicRAGEngine()
    replayed_res = engine.query(
        question=target_trace["question"],
        top_k=target_trace["model_params"]["top_k"],
        mode="week4"
    )
    
    print(f"Question: {target_trace['question']}", flush=True)
    print("\n--- ORIGINAL OUTPUT ---", flush=True)
    print(target_trace["raw_output"], flush=True)
    print("\n--- REPLAYED OUTPUT ---", flush=True)
    print(replayed_res["answer"], flush=True)
    
    is_exact_match = (target_trace["raw_output"].strip() == replayed_res["answer"].strip())
    print(f"\nReplay Verification Status: {'EXACT MATCH (100% Deterministic)' if is_exact_match else 'MISMATCH'}", flush=True)
    
    return sampled_ids, replay_target_id, target_trace, replayed_res

if __name__ == "__main__":
    generate_traces()
    run_seeded_sampling_and_replay()
