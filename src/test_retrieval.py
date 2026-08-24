from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# 8 Known-Answer Questions (4 Troubleshooting Table Rows + 4 Prose)
questions = [
    {
        "id": "Q1",
        "type": "Table Row",
        "question": "What should I do if I receive error code 51 - Decline when paying an invoice?",
        "expected_article_id": "article_03",
        "expected_source_file": "article_03_zendesk_credit_card_failures.md",
        "expected_section": "Resolving other types of errors (Table: 51 - Decline)",
    },
    {
        "id": "Q2",
        "type": "Table Row",
        "question": "What does the error message 'Payment error: authorization failed' mean in Cloudflare billing and what is the fix?",
        "expected_article_id": "article_01",
        "expected_source_file": "article_01_cloudflare_billing_errors.md",
        "expected_section": "Error messages (Table: Payment error: authorization failed)",
    },
    {
        "id": "Q3",
        "type": "Table Row",
        "question": "What does error code 430357 - Lost or Stolen Card indicate and how should I resolve it?",
        "expected_article_id": "article_03",
        "expected_source_file": "article_03_zendesk_credit_card_failures.md",
        "expected_section": "Resolving other types of errors (Table: 430357 - Lost or Stolen Card)",
    },
    {
        "id": "Q4",
        "type": "Table Row",
        "question": "How do I fix error code 14 - Card No. Error when updating credit card details?",
        "expected_article_id": "article_03",
        "expected_source_file": "article_03_zendesk_credit_card_failures.md",
        "expected_section": "Resolving other types of errors (Table: 14 - Card No. Error)",
    },
    {
        "id": "Q5",
        "type": "Prose",
        "question": "What URL parameter should I append to test Zendesk ticket issues with all support apps disabled?",
        "expected_article_id": "article_04",
        "expected_source_file": "article_04_zendesk_app_troubleshooting.md",
        "expected_section": "Disable all apps",
    },
    {
        "id": "Q6",
        "type": "Prose",
        "question": "Why might Google block my sign-in when accessing my account from a third-party service?",
        "expected_article_id": "article_05",
        "expected_source_file": "article_05_google_third_party_signin.md",
        "expected_section": "Why you were blocked from signing in",
    },
    {
        "id": "Q7",
        "type": "Prose",
        "question": "How long does Google account recovery take if I lost my security key and have no backup second step?",
        "expected_article_id": "article_06",
        "expected_source_file": "article_06_google_2step_verification.md",
        "expected_section": "My security key was lost or stolen",
    },
    {
        "id": "Q8",
        "type": "Prose",
        "question": "What is the difference between Strong Customer Authentication (SCA) and 3D Secure (3DS)?",
        "expected_article_id": "article_02",
        "expected_source_file": "article_02_zendesk_payment_issues.md",
        "expected_section": "Authenticate 3D secure payments",
    },
]

def run_benchmark():
    scores = {"strategy_a": 0, "strategy_b": 0}
    summary_records = []

    print("=" * 80)
    print("RETRIEVAL EVALUATION BENCHMARK (HIT-IN-TOP-5)")
    print("=" * 80)

    for item in questions:
        q_id = item["id"]
        q_text = item["question"]
        expected_art = item["expected_article_id"]
        q_type = item["type"]

        q_embedding = model.encode(q_text).tolist()

        record = {
            "id": q_id,
            "type": q_type,
            "question": q_text,
            "expected_article": expected_art,
            "expected_section": item["expected_section"],
            "strategy_a_rank": None,
            "strategy_a_dist": None,
            "strategy_a_hit": False,
            "strategy_b_rank": None,
            "strategy_b_dist": None,
            "strategy_b_hit": False,
        }

        print(f"\n[{q_id}] ({q_type}) Question: {q_text}")
        print(f"Target Article: {expected_art} ({item['expected_source_file']})")
        print(f"Target Section: {item['expected_section']}")

        for strategy in ["strategy_a", "strategy_b"]:
            collection = client.get_collection(strategy)
            res = collection.query(
                query_embeddings=[q_embedding],
                n_results=5,
            )

            docs = res["documents"][0]
            metas = res["metadatas"][0]
            dists = res["distances"][0]

            hit_found = False
            top_rank = None
            top_dist = None

            print(f"\n--- Strategy: {strategy} ---")
            for idx, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
                art_id = meta.get("article_id", "")
                chunk_id = meta.get("chunk_id", "")
                is_hit = (art_id == expected_art)

                print(f"  Rank {idx}: [Chunk: {chunk_id} | Art: {art_id} | Dist: {dist:.4f}] {'[HIT]' if is_hit else ''}")

                if is_hit and not hit_found:
                    hit_found = True
                    top_rank = idx
                    top_dist = dist

            if hit_found:
                scores[strategy] += 1
                if strategy == "strategy_a":
                    record["strategy_a_hit"] = True
                    record["strategy_a_rank"] = top_rank
                    record["strategy_a_dist"] = round(top_dist, 4)
                else:
                    record["strategy_b_hit"] = True
                    record["strategy_b_rank"] = top_rank
                    record["strategy_b_dist"] = round(top_dist, 4)

        summary_records.append(record)

    print("\n" + "=" * 80)
    print("FINAL BENCHMARK SCORE SUMMARY")
    print("=" * 80)
    print(f"Strategy A (Standard Splitter):           {scores['strategy_a']} / 8")
    print(f"Strategy B (Structure-Aware Table Splitter): {scores['strategy_b']} / 8")
    print("-" * 80)

    print("| Q # | Type | Expected Article | Strategy A Rank | Strategy A Hit | Strategy B Rank | Strategy B Hit |")
    print("|---|---|---|---|---|---|---|")
    for r in summary_records:
        a_str = f"Rank {r['strategy_a_rank']}" if r["strategy_a_hit"] else "Not in Top 5"
        b_str = f"Rank {r['strategy_b_rank']}" if r["strategy_b_hit"] else "Not in Top 5"
        print(f"| {r['id']} | {r['type']} | {r['expected_article']} | {a_str} | {'HIT' if r['strategy_a_hit'] else 'MISS'} | {b_str} | {'HIT' if r['strategy_b_hit'] else 'MISS'} |")

    return summary_records, scores

if __name__ == "__main__":
    run_benchmark()