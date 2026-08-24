from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Collection to test
collection = client.get_collection("strategy_b")

# Test query that matches both Billing/Payment and Authentication/Troubleshooting domains
query_text = "How do I troubleshoot payment failures and authorization errors?"
query_embedding = model.encode(query_text).tolist()

print("=" * 80)
print(f"QUERY: '{query_text}'")
print("=" * 80)

# 1. SEARCH WITHOUT METADATA FILTERING
print("\n--- UNFILTERED SEARCH (All Product Areas) ---")
unfiltered_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
)

unfiltered_list = []
for i in range(len(unfiltered_results["documents"][0])):
    doc = unfiltered_results["documents"][0][i]
    meta = unfiltered_results["metadatas"][0][i]
    dist = unfiltered_results["distances"][0][i]
    unfiltered_list.append((meta, dist, doc))
    print(f"\nResult {i+1}:")
    print(f"  Chunk ID:     {meta.get('chunk_id')}")
    print(f"  Article ID:   {meta.get('article_id')}")
    print(f"  Source File:  {meta.get('source_file')}")
    print(f"  Product Area: {meta.get('product_area')}")
    print(f"  Distance:     {dist:.4f}")
    print(f"  Snippet:      {doc[:200]}...")

# 2. SEARCH WITH METADATA FILTER: product_area = "Authentication"
print("\n" + "=" * 80)
print("--- FILTERED SEARCH (product_area = 'Authentication') ---")
print("=" * 80)

filtered_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    where={"product_area": "Authentication"},
)

filtered_list = []
for i in range(len(filtered_results["documents"][0])):
    doc = filtered_results["documents"][0][i]
    meta = filtered_results["metadatas"][0][i]
    dist = filtered_results["distances"][0][i]
    filtered_list.append((meta, dist, doc))
    print(f"\nResult {i+1}:")
    print(f"  Chunk ID:     {meta.get('chunk_id')}")
    print(f"  Article ID:   {meta.get('article_id')}")
    print(f"  Source File:  {meta.get('source_file')}")
    print(f"  Product Area: {meta.get('product_area')}")
    print(f"  Distance:     {dist:.4f}")
    print(f"  Snippet:      {doc[:200]}...")

top1_unfiltered = unfiltered_list[0][0]["source_file"]
top1_filtered = filtered_list[0][0]["source_file"]

print("\n" + "=" * 80)
print("METADATA FILTER EFFECT SUMMARY")
print("=" * 80)
print(f"Unfiltered Top-1 Source File: {top1_unfiltered} (Product Area: {unfiltered_list[0][0]['product_area']}, Score: {unfiltered_list[0][1]:.4f})")
print(f"Filtered Top-1 Source File:   {top1_filtered} (Product Area: {filtered_list[0][0]['product_area']}, Score: {filtered_list[0][1]:.4f})")
if top1_unfiltered != top1_filtered:
    print("\n[SUCCESS] Metadata filtering successfully CHANGED the Top-1 retrieved document!")
else:
    print("\nTop-1 document remained unchanged.")