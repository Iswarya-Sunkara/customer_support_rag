from pathlib import Path
import json
import time
import statistics
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.hybrid_retriever import HybridRRFRetriever

GOLDEN_SET_PATH = PROJECT_DIR / "golden_set.jsonl"

def load_golden_set():
    items = []
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line.strip()))
    return items

def run_hybrid_evaluation():
    print("=" * 80)
    print("RUNNING HYBRID BM25 + RRF RETRIEVAL EVALUATION (Week 4 Improvement)")
    print("=" * 80)

    retriever = HybridRRFRetriever()
    golden_set = load_golden_set()
    
    hits = 0
    total_evaluable = 0
    latencies = []
    results = []

    for item in golden_set:
        q_id = item["id"]
        q_text = item["question"]
        expected_cid = item["expected_chunk_id"]

        search_res = retriever.search(q_text, top_k=3, top_n=25, k_rrf=60)
        elapsed_ms = search_res["latency_ms"]
        latencies.append(elapsed_ms)

        retrieved_results = search_res["results"]
        retrieved_ids = [r["chunk_id"] for r in retrieved_results]
        rrf_scores = [r["rrf_score"] for r in retrieved_results]

        is_hit = False
        hit_rank = None

        if expected_cid != "NONE":
            total_evaluable += 1
            if expected_cid in retrieved_ids:
                is_hit = True
                hits += 1
                hit_rank = retrieved_ids.index(expected_cid) + 1

        record = {
            "id": q_id,
            "question": q_text,
            "expected_chunk_id": expected_cid,
            "has_exact_token": item["has_exact_token"],
            "retrieved_ids": retrieved_ids,
            "rrf_scores": rrf_scores,
            "is_hit": is_hit,
            "hit_rank": hit_rank,
            "latency_ms": elapsed_ms,
        }
        results.append(record)

        status_str = f"HIT (Rank {hit_rank})" if is_hit else ("NOT-IN-CORPUS" if expected_cid == "NONE" else "MISS")
        print(f"\n[{q_id}] {status_str} | Expected: {expected_cid} | Latency: {elapsed_ms:.2f} ms")
        print(f"    Query: {q_text}")
        print("    Retrieved Top 3 (Hybrid RRF):")
        for rank, r in enumerate(retrieved_results, start=1):
            snippet = r["document"].replace("\n", " ")[:90]
            print(f"      Rank {rank}: [{r['chunk_id']} | RRF Score: {r['rrf_score']:.6f}] {snippet}...")

    hit_rate = (hits / total_evaluable) * 100.0 if total_evaluable > 0 else 0.0
    p50_latency = statistics.median(latencies)
    mean_latency = statistics.mean(latencies)

    print("\n" + "=" * 80)
    print("HYBRID RETRIEVAL EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Questions Evaluated:  {len(golden_set)}")
    print(f"Evaluable Corpus Questions: {total_evaluable}")
    print(f"Hybrid Hits@3:              {hits} / {total_evaluable}")
    print(f"Hybrid Hit-rate@3:          {hit_rate:.2f}%")
    print(f"Hybrid p50 Query Latency:   {p50_latency:.2f} ms")
    print(f"Hybrid Mean Latency:        {mean_latency:.2f} ms")
    print("=" * 80)

    summary_file = PROJECT_DIR / "hybrid_results.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "hits": hits,
            "total_evaluable": total_evaluable,
            "hit_rate_at_3": round(hit_rate, 2),
            "p50_latency_ms": round(p50_latency, 2),
            "mean_latency_ms": round(mean_latency, 2),
            "detailed_results": results,
        }, f, indent=2)

    return results, hit_rate, p50_latency

if __name__ == "__main__":
    run_hybrid_evaluation()
