from pathlib import Path
import sys
import shutil
import chromadb
from sentence_transformers import SentenceTransformer

sys.path.append(str(Path(__file__).resolve().parent))

from chunk_documents import chunks as strategy_a_chunks
from structure_aware_chunking import chunks as strategy_b_chunks

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_vector_database():
    # Remove stale ChromaDB files to prevent HNSW segment reader disk errors
    if CHROMA_DIR.exists():
        try:
            shutil.rmtree(CHROMA_DIR)
        except Exception:
            pass

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    def create_collection(name, chunks):
        collection = client.get_or_create_collection(name=name)
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.metadata.get("chunk_id", f"{name}_{i}") for i, chunk in enumerate(chunks)]

        embeddings = model.encode(texts).tolist()

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        print(f"Collection '{name}': {len(chunks)} chunks added successfully.")

    create_collection("strategy_a", strategy_a_chunks)
    create_collection("strategy_b", strategy_b_chunks)
    print("\nVector database created successfully.")

if __name__ == "__main__":
    build_vector_database()
