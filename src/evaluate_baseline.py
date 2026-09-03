from pathlib import Path
import json
import time
import statistics
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"
GOLDEN_SET_PATH = PROJECT_DIR / "golden_set.jsonl"

def load_golden_set():
    items = []
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line.strip()))
    return items

def run_baseline_evaluation():
    print("=" * 80)
    print("RUNNING BASELINE DENSE RETRIEVAL EVALUATION (Week 3 System)")
    print("=" * 80)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection("strategy_b")

    golden_set = load_golden_set()
    
    hits = 0
    total_evaluable = 0  # Excludes Not-In-Corpus question for hit-rate
    latencies = []
    results = []

    for item in golden_set:
        q_id = item["id"]
        q_text = item["question"]
        expected_cid = item["expected_chunk_id"]

        start_time = time.perf_counter()
        q_embedding = model.encode(q_text).tolist()
        res = collection.query(
            query_embeddings=[q_embedding],
            n_results=3,
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        latencies.append(elapsed_ms)

        retrieved_ids = res["ids"][0]
        retrieved_docs = res["documents"][0]
        retrieved_metas = res["metadatas"][0]
        retrieved_dists = res["distances"][0]

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
            "retrieved_distances": [round(d, 4) for d in retrieved_dists],
            "is_hit": is_hit,
            "hit_rank": hit_rank,
            "latency_ms": round(elapsed_ms, 2),
        }
        results.append(record)

        # Print inspection output for analysis
        status_str = f"HIT (Rank {hit_rank})" if is_hit else ("NOT-IN-CORPUS" if expected_cid == "NONE" else "MISS")
        print(f"\n[{q_id}] {status_str} | Expected: {expected_cid} | Latency: {elapsed_ms:.2f} ms")
        print(f"    Query: {q_text}")
        print("    Retrieved Top 3:")
        for rank, (cid, dist, doc) in enumerate(zip(retrieved_ids, retrieved_dists, retrieved_docs), start=1):
            snippet = doc.replace("\n", " ")[:90]
            print(f"      Rank {rank}: [{cid} | Dist: {dist:.4f}] {snippet}...")

    hit_rate = (hits / total_evaluable) * 100.0 if total_evaluable > 0 else 0.0
    p50_latency = statistics.median(latencies)
    mean_latency = statistics.mean(latencies)

    print("\n" + "=" * 80)
    print("BASELINE EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Questions Evaluated:  {len(golden_set)}")
    print(f"Evaluable Corpus Questions: {total_evaluable}")
    print(f"Baseline Hits@3:            {hits} / {total_evaluable}")
    print(f"Baseline Hit-rate@3:        {hit_rate:.2f}%")
    print(f"Baseline p50 Query Latency: {p50_latency:.2f} ms")
    print(f"Baseline Mean Latency:      {mean_latency:.2f} ms")
    print("=" * 80)

    summary_file = PROJECT_DIR / "baseline_results.json"
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
    run_baseline_evaluation()
