# Week 4 Evaluation Results — Debugging Retrieval, Failure Separation & Hybrid RAG (Task Set A)

## Executive Summary

This report documents the Week 4 retrieval evaluation and failure analysis for the **Customer Support Tickets** RAG system. The goal of this benchmark is to separate retrieval failures ($R$) from generation failures ($G$) and out-of-corpus requests ($Not-In-Corpus$), apply **exactly one retrieval improvement** (BM25 + RRF Hybrid Fusion, $k=60$), measure before and after `hit-rate@3` and median (`p50`) query latency over a 12-question Golden Set, and render a data-backed shipping decision.

---

## 1. 12-Question Golden Set Benchmark (`golden_set.jsonl`)

A 12-question Golden Set was assembled from the 6 ingested help-center articles (`article_01` to `article_06`). **5 of the 12 questions (41.7%) specifically target exact identifiers, error codes, and URL parameters** that dense vector search is structurally weak at retrieving.

| Q # | Type | Question Text | Target Chunk ID | Article ID | Target Section / Category | Exact Token |
|---|---|---|---|---|---|---|
| **Q01** | Table Row | What should I do if I get credit card error code 51 - Decline when paying my invoice? | `strategy_b_36` | `article_03` | Resolving other types of errors | `51 - Decline` |
| **Q02** | Table Row | How do I fix Cloudflare billing error 'Payment error: authorization failed'? | `strategy_b_3` | `article_01` | Error messages | `"Payment error: authorization failed"` |
| **Q03** | Table Row | What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it? | `strategy_b_39` | `article_03` | Resolving other types of errors | `430357 - Lost or Stolen Card` |
| **Q04** | Table Row | How should I resolve credit card error code 14 - Card No. Error when saving my payment details? | `strategy_b_35` | `article_03` | Resolving other types of errors | `14 - Card No. Error` |
| **Q05** | Token / URL | What URL parameter ?noapps should I add to test Zendesk tickets with all apps disabled? | `strategy_b_42` | `article_04` | Disable all apps | `?noapps` |
| **Q06** | Prose | Why does Google block sign-in attempts when accessing an account from a third-party service? | `strategy_b_49` | `article_05` | Why you were blocked from signing in | N/A |
| **Q07** | Prose | How long does Google account recovery take if I lost my security key and have no backup second step? | `strategy_b_60` | `article_06` | My security key was lost or stolen | N/A |
| **Q08** | Prose | What is the key difference between Strong Customer Authentication (SCA) and 3D Secure (3DS)? | `strategy_b_21` | `article_02` | Authenticate 3D secure payments | N/A |
| **Q09** | Prose / Table | How many times and over how many days will Cloudflare retry a failed recurring subscription renewal payment before ending grace period? | `strategy_b_7` | `article_01` | Email notifications | N/A |
| **Q10** | Prose | What format requirements apply to the Cardholder name and Postal Code fields when resubmitting a failed card? | `strategy_b_31` | `article_03` | Resolving transaction errors | N/A |
| **Q11** | Prose | Why shouldn't I use Google Voice to receive 2-Step Verification codes? | `strategy_b_68` | `article_06` | Why you shouldn't use Google Voice | N/A |
| **Q12** | Out of Corpus | What is the exact SLA guaranteed refund window in business days for annual plan chargebacks? | `NONE` | N/A | Not-In-Corpus | N/A |

---

## 2. Baseline Dense Retrieval Results (Week 3 System)

- **Retriever**: Dense Vector Search (`all-MiniLM-L6-v2` embeddings in ChromaDB HNSW Index, `strategy_b` collection).
- **Top-K**: 3 candidates.
- **Baseline Hits@3**: 6 / 11 evaluable questions.
- **Baseline Hit-rate@3**: **54.55%**
- **Baseline p50 Latency**: **18.75 ms** (mean: 25.92 ms).

---

## 3. Failure Inspection & Classification Tally

Every miss was inspected through the retrieval log to analyze candidate chunks and determine root failure causes.

### Inspection Evidence per Failed Question

1. **Q01 (MISS — R)**:
   - *Target Chunk*: `strategy_b_36` (`51 - Decline | Insufficient funds`).
   - *Retrieved Top 3*: `strategy_b_12` (Dist: 0.9555), `strategy_b_31` (Dist: 0.9949), `strategy_b_15` (Dist: 1.0146).
   - *Line of Evidence*: Target chunk `strategy_b_36` exists in `article_03`, but dense vector embedding distance matched generic prose troubleshooting terms rather than exact error code `51`.
2. **Q02 (MISS — R)**:
   - *Target Chunk*: `strategy_b_3` (`"Payment error: authorization failed" | Your bank declined...`).
   - *Retrieved Top 3*: `strategy_b_0` (Dist: 0.5105), `strategy_b_8` (Dist: 0.5152), `strategy_b_9` (Dist: 0.9421).
   - *Line of Evidence*: Target chunk `strategy_b_3` exists in `article_01`, but dense vector search fetched high-level article titles/headers instead of the specific error message table row.
3. **Q03 (MISS — R)**:
   - *Target Chunk*: `strategy_b_39` (`430357 - Lost or Stolen Card | Bank has frozen your card...`).
   - *Retrieved Top 3*: `strategy_b_30` (Dist: 0.4715), `strategy_b_40` (Dist: 0.5155), `strategy_b_26` (Dist: 0.5342).
   - *Line of Evidence*: Target chunk `strategy_b_39` exists in `article_03`, but vector search returned general article intro and support contact chunks instead of the specific numeric error row.
4. **Q04 (MISS — R)**:
   - *Target Chunk*: `strategy_b_35` (`14 - Card No. Error | Invalid card number`).
   - *Retrieved Top 3*: `strategy_b_31` (Dist: 0.7516), `strategy_b_15` (Dist: 0.8315), `strategy_b_28` (Dist: 0.8708).
   - *Line of Evidence*: Target chunk `strategy_b_35` exists in `article_03`, but dense retrieval fetched general payment error prose chunks rather than table row `strategy_b_35`.
5. **Q09 (MISS — R)**:
   - *Target Chunk*: `strategy_b_7` (`We couldn't process your renewal payment | Cloudflare will retry up to 5 times over 5 days`).
   - *Retrieved Top 3*: `strategy_b_0` (Dist: 0.9196), `strategy_b_8` (Dist: 1.0823), `strategy_b_9` (Dist: 1.1097).
   - *Line of Evidence*: Target chunk `strategy_b_7` exists in `article_01`, but dense embeddings ranked general billing overview chunks ahead of the renewal email retry policy chunk.
6. **Q12 (Refused — Not-In-Corpus)**:
   - *Target Chunk*: `NONE`.
   - *Retrieved Top 3*: `strategy_b_28` (Dist: 1.4361), `strategy_b_9` (Dist: 1.5138), `strategy_b_60` (Dist: 1.5220).
   - *Line of Evidence*: Question asks for annual plan refund chargeback SLA business days, which is absent from all 6 ingested documents; top distance 1.4361 > 1.0 threshold triggered correct verbatim refusal.

### Failure Classification Tally

| Failure Type | Count | Percentage of Failures |
|---|:---:|:---:|
| **R (Retrieval Failure)** | **5** | **83.3%** |
| **G (Generation Failure)** | **0** | **0.0%** |
| **Not-In-Corpus** | **1** | **16.7%** |
| **Total Failures** | **6** | **100.0%** |

---

## 4. Single Retrieval Improvement Justification

> **Chosen Change**: **BM25 Keyword Search + Reciprocal Rank Fusion (RRF, $k=60$)** over top-25 candidate pools.

**Justification**:
The failure tally demonstrates that **83.3% of failures (5 out of 6) are pure Retrieval Failures ($R$)**, where exact error codes (`51 - Decline`, `14 - Card No. Error`, `430357 - Lost or Stolen Card`), exact string messages (`"Payment error: authorization failed"`), and specific numeric retry rules (`5 times over 5 days`) failed to surface in dense vector search. Dense embedding models represent natural language questions and short tabular key-value pairs in distant vector space. Combining sparse BM25 keyword matching with dense HNSW vector search using Reciprocal Rank Fusion ($k=60$) directly addresses this failure pattern by elevating exact token matches without sacrificing semantic coverage.

---

## 5. Metrics Comparison: Before vs After

| Metric | Before (Dense Baseline) | After (BM25 + RRF Hybrid) | Absolute Delta | Percentage Change |
|---|:---:|:---:|:---:|:---:|
| **Hit-rate@3** | **54.55%** (6 / 11) | **54.55%** (6 / 11) | **0.00%** | **0.0%** |
| **p50 Latency (Median)** | **18.75 ms** | **20.38 ms** | **+1.63 ms** | **+8.7%** |
| **Mean Latency** | **25.92 ms** | **23.13 ms** | **-2.79 ms** | **-10.8%** |

---

## 6. Per-Question Results & Failure Status Breakdown

| Q # | Expected Chunk | Dense Baseline Status | Dense Rank | Hybrid RRF Status | Hybrid Rank | Status / Delta |
|---|---|---|:---:|---|:---:|---|
| **Q01** | `strategy_b_36` | **MISS** | — | **MISS** | — | Unfixed R Failure |
| **Q02** | `strategy_b_3` | **MISS** | — | **MISS** | — | Unfixed R Failure |
| **Q03** | `strategy_b_39` | **MISS** | — | **MISS** | — | Unfixed R Failure |
| **Q04** | `strategy_b_35` | **MISS** | — | **MISS** | — | Unfixed R Failure |
| **Q05** | `strategy_b_42` | **HIT** | Rank 2 | **HIT** | Rank 2 | Intact Pass |
| **Q06** | `strategy_b_49` | **HIT** | Rank 2 | **HIT** | Rank 2 | Intact Pass |
| **Q07** | `strategy_b_60` | **HIT** | Rank 1 | **HIT** | Rank 3 | Intact Pass |
| **Q08** | `strategy_b_21` | **HIT** | Rank 1 | **HIT** | Rank 1 | Intact Pass |
| **Q09** | `strategy_b_7` | **MISS** | — | **MISS** | — | Unfixed R Failure |
| **Q10** | `strategy_b_31` | **HIT** | Rank 1 | **HIT** | Rank 1 | Intact Pass |
| **Q11** | `strategy_b_68` | **HIT** | Rank 1 | **HIT** | Rank 1 | Intact Pass |
| **Q12** | `NONE` | **NOT-IN-CORPUS** | Refused | **NOT-IN-CORPUS** | Refused | Intact Refusal |

---

## 7. Data-Backed Shipping Decision

### Decision: **DO NOT SHIP**

### Empirical Rationale:
1. **Zero Hit-Rate Improvement**: BM25 + RRF ($k=60$) yielded a `hit-rate@3` of **54.55%**, exactly identical to the dense vector baseline (6 / 11 hits).
2. **Latency Penalty**: Hybrid search increased median (`p50`) query latency from **18.75 ms** to **20.38 ms** (+1.63 ms, an **+8.7% performance overhead**).
3. **Root Cause Analysis of Failure to Fix**:
   - In short table chunks (`strategy_b_34`–`strategy_b_39`), natural language user queries contain high-frequency domain terms ("credit", "card", "error", "payment", "invoice") that match prose troubleshooting articles with higher BM25 term frequency scores than the 2-row table chunks.
   - Consequently, BM25 scores for prose chunks dominated the RRF fusion pool, leaving table chunks below rank 3.
4. **Next Recommended Action**:
   - Instead of deploying standard BM25+RRF, the team should evaluate **Query Rewriting / HyDE** (expanding user queries into exact error table headers) or **Cross-Encoder Reranking over an expanded candidate pool (top 50)** or **Table-Flattening Chunking** to solve table row retrieval failures.

---

## 8. Code Diff Showing Single Retrieval Change

The single retrieval modification introduces `src/hybrid_retriever.py` and integrates it into `src/final_rag.py`:

```diff
--- a/src/final_rag.py
+++ b/src/final_rag.py
@@ -1,15 +1,52 @@
 from pathlib import Path
+import sys
 import chromadb
 from sentence_transformers import SentenceTransformer

 PROJECT_DIR = Path(__file__).resolve().parent.parent
+CHROMA_DIR = PROJECT_DIR / "chroma_db"
+sys.path.append(str(PROJECT_DIR))
+
+from src.hybrid_retriever import HybridRRFRetriever

 DISTANCE_THRESHOLD = 1.0
 TOP_K = 3

 model = SentenceTransformer("all-MiniLM-L6-v2")
 client = chromadb.PersistentClient(path=str(CHROMA_DIR))
 collection = client.get_collection("strategy_b")
+hybrid_retriever = None

-def run_rag(question):
+def run_rag(question, use_hybrid=False):
+    global hybrid_retriever
     print("=" * 80)
-    print(f"QUESTION: {question}")
+    print(f"QUESTION: {question} (Mode: {'Hybrid BM25+RRF' if use_hybrid else 'Dense Baseline'})")
     print("=" * 80)

+    if use_hybrid:
+        if hybrid_retriever is None:
+            hybrid_retriever = HybridRRFRetriever()
+        search_res = hybrid_retriever.search(question, top_k=TOP_K)
+        res_list = search_res["results"]
+        if not res_list:
+            return {"status": "refused", "response": "No relevant context found."}
+        best_item = res_list[0]
+        return {
+            "status": "answered",
+            "chunk_id": best_item["chunk_id"],
+            "article_id": best_item["metadata"].get("article_id"),
+            "rrf_score": best_item["rrf_score"],
+        }
```
