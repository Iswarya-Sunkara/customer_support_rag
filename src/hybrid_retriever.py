from pathlib import Path
import math
import re
import time
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"

RRF_K = 60
TOP_N_CANDIDATES = 25

class BM25Retriever:
    def __init__(self, documents, ids, k1=1.5, b=0.75):
        self.documents = documents
        self.ids = ids
        self.k1 = k1
        self.b = b
        self.corpus_size = len(documents)
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_tokens = []
        self._initialize()

    def _tokenize(self, text):
        return re.findall(r"\w+", text.lower())

    def _initialize(self):
        total_words = 0
        df = {}
        for doc in self.documents:
            tokens = self._tokenize(doc)
            self.doc_tokens.append(tokens)
            total_words += len(tokens)
            frequencies = {}
            for token in tokens:
                frequencies[token] = frequencies.get(token, 0) + 1
            self.doc_freqs.append(frequencies)
            for token in set(tokens):
                df[token] = df.get(token, 0) + 1

        self.avgdl = total_words / self.corpus_size if self.corpus_size > 0 else 1

        for token, freq in df.items():
            # Standard BM25 IDF formula with smoothing
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)

    def get_scores(self, query):
        query_tokens = self._tokenize(query)
        scores = [0.0] * self.corpus_size

        for i, doc_len in enumerate([len(t) for t in self.doc_tokens]):
            freqs = self.doc_freqs[i]
            score = 0.0
            for token in query_tokens:
                if token not in freqs:
                    continue
                tf = freqs[token]
                idf = self.idf.get(token, 0.0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                score += idf * (numerator / denominator)
            scores[i] = score

        return scores

    def query(self, query_text, top_n=TOP_N_CANDIDATES):
        scores = self.get_scores(query_text)
        indexed_scores = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in indexed_scores[:top_n]:
            if score > 0:
                results.append((self.ids[idx], score, self.documents[idx]))
        return results

class HybridRRFRetriever:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_collection("strategy_b")

        # Load all documents from ChromaDB collection for BM25
        chroma_res = self.collection.get()
        self.all_ids = chroma_res["ids"]
        self.all_docs = chroma_res["documents"]
        self.all_metas = chroma_res["metadatas"]
        
        self.id_to_doc = {id_: doc for id_, doc in zip(self.all_ids, self.all_docs)}
        self.id_to_meta = {id_: meta for id_, meta in zip(self.all_ids, self.all_metas)}

        self.bm25 = BM25Retriever(self.all_docs, self.all_ids)

    def search(self, query_text, top_k=3, top_n=TOP_N_CANDIDATES, k_rrf=RRF_K):
        start_time = time.perf_counter()

        # 1. Dense Vector Search
        q_embedding = self.model.encode(query_text).tolist()
        dense_res = self.collection.query(
            query_embeddings=[q_embedding],
            n_results=top_n,
        )
        dense_ids = dense_res["ids"][0]
        dense_dists = dense_res["distances"][0]

        # 2. Sparse BM25 Keyword Search
        bm25_res = self.bm25.query(query_text, top_n=top_n)
        bm25_ids = [item[0] for item in bm25_res]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        
        # Dense ranks
        for rank, cid in enumerate(dense_ids, start=1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k_rrf + rank))

        # BM25 ranks
        for rank, cid in enumerate(bm25_ids, start=1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k_rrf + rank))

        # Sort candidate chunk_ids by RRF score descending
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        top_candidates = sorted_candidates[:top_k]
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        final_results = []
        for cid, rrf_score in top_candidates:
            # Find dense distance if available
            dist = None
            if cid in dense_ids:
                dist = dense_dists[dense_ids.index(cid)]

            final_results.append({
                "chunk_id": cid,
                "rrf_score": round(rrf_score, 6),
                "dense_distance": round(dist, 4) if dist is not None else None,
                "document": self.id_to_doc[cid],
                "metadata": self.id_to_meta[cid],
            })

        return {
            "query": query_text,
            "latency_ms": round(elapsed_ms, 2),
            "results": final_results,
            "dense_ids": dense_ids[:5],
            "bm25_ids": bm25_ids[:5],
        }

if __name__ == "__main__":
    retriever = HybridRRFRetriever()
    res = retriever.search("What should I do if I get credit card error code 51 - Decline when paying my invoice?")
    print(f"Latency: {res['latency_ms']} ms")
    print("Top 3 Hybrid RRF Results:")
    for idx, r in enumerate(res["results"], start=1):
        print(f"  Rank {idx}: [{r['chunk_id']} | RRF Score: {r['rrf_score']}] {r['document'][:80]}...")
