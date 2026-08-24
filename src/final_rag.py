from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"

DISTANCE_THRESHOLD = 1.0
TOP_K = 3

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection("strategy_b")

def run_rag(question):
    print("=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    question_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    best_distance = distances[0]
    print(f"Best Retrieval Distance: {best_distance:.4f}")

    if best_distance > DISTANCE_THRESHOLD:
        print("\nSTATUS: REFUSED (Out of Corpus)")
        print("\nVERBATIM REFUSAL TRANSCRIPT:")
        print("I don't have enough information in my knowledge base to answer this question.")
        print("-" * 80 + "\n")
        return {
            "status": "refused",
            "distance": round(best_distance, 4),
            "response": "I don't have enough information in my knowledge base to answer this question."
        }

    print("\nSTATUS: ANSWERED (Grounded in Corpus)")
    print("\nANSWER WITH CLAIM-LEVEL CITATIONS:")
    
    best_doc = documents[0]
    best_meta = metadatas[0]
    chunk_id = best_meta.get("chunk_id", "unknown_chunk")
    art_id = best_meta.get("article_id", "unknown_article")
    source_file = best_meta.get("source_file", "")
    prod_area = best_meta.get("product_area", "")

    # Format grounded claim citations
    print(f"- Main Finding/Fix: {best_doc[:300].strip()}... [Citation -> chunk_id: {chunk_id}, article: {art_id} ({source_file})]")
    print("\nCITATIONS DETAILED BREAKDOWN:")
    print(f"  • Cited Chunk ID:   {chunk_id}")
    print(f"  • Article ID:       {art_id}")
    print(f"  • Source File:      {source_file}")
    print(f"  • Product Area:     {prod_area}")
    print(f"  • Distance Score:   {best_distance:.4f}")
    print("-" * 80 + "\n")

    return {
        "status": "answered",
        "distance": round(best_distance, 4),
        "chunk_id": chunk_id,
        "article_id": art_id,
        "source_file": source_file,
    }

if __name__ == "__main__":
    print("--- TESTING ANSWERABLE QUESTIONS ---")
    run_rag("What should I do if my Cloudflare payment authorization fails?")
    run_rag("Why was my Zendesk credit card declined?")
    run_rag("How long does Google account recovery take if I lost my security key and have no backup step?")

    print("--- TESTING OUT-OF-CORPUS UNANSWERABLE QUESTIONS ---")
    run_rag("What is the exact refund SLA for annual billing chargebacks?")
    run_rag("How do I reset my Facebook password?")
    run_rag("What is the weather in Bangalore today?")