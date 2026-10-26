# Week 10 Race: Single Agent vs Triage Squad

> **Domain**: Customer support tickets  
> **Evaluation**: 10 Identical Week-6 Cases (`eval/cases.jsonl`)  
> **Evaluator**: Same Judge (`eval/assertions.py` + `judge_v2.txt`)  

---

## 🏁 The Official 4-Metric Comparison Table

| Metric | Single Agent (Arm 1) | Multi-Agent Triage Squad (Arm 2) | Comparison & Operational Delta |
| :--- | :---: | :---: | :--- |
| **1. Pass Rate (%)** | **80.0%** (8/10) | **80.0%** (8/10) | **Parity (+0.0%)** |
| **2. Median Latency (p50)** | **2.50 s** | **5.68 s** | **+3.17 s (+126.7% slower)** |
| **   99th Percentile Latency (p99)** | **4.56 s** | **13.80 s** | **+9.24 s (+202.8% slower)** |
| **3. Total Tokens (10 Cases)** | **6,775 tokens** | **14,563 tokens** | **+7,788 tokens (+115.0% bill)** |
| **4. Cost per Ticket (USD)** | **$0.00118** | **$0.00244** | **+$0.00126 (+106.5% cost)** |

---

## 🔄 Context Re-Send Multiplier & Attribution

**Context re-send multiplier:** **2.1x** (`multi tokens / single tokens` = 14,563 / 6,775)  
**Attributed dominant hand-off:** **orchestrator -> reply_synthesis**, accounting for **49.2%** of all multi-agent tokens (7,158 tokens).

### Token Breakdown Across Hand-offs:
- **orchestrator -> reply_synthesis**: 7,158 tokens (49.2% of multi-agent total)
- **orchestrator -> policy_worker**: 4,231 tokens (29.1% of multi-agent total)
- **orchestrator -> triage_worker**: 3,174 tokens (21.8% of multi-agent total)

---

## 📋 Per-Case Breakdown on the Same 10 Week-6 Cases

| Case ID | Ticket ID | Mode / Topic | Tier | Single Pass? | Multi Pass? | Single Latency | Multi Latency | Single Tokens | Multi Tokens |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `C01` | `TKT-97673` | M1_superseded_grace_period | Standard | ✅ | ❌ | 4.06s | 13.80s | 701 | 1,505 |
| `C02` | `TKT-37593` | M1_superseded_grace_period | Priority | ❌ | ✅ | 1.93s | 5.76s | 652 | 1,535 |
| `C06` | `TKT-10930` | M2_code51_confused_with_timeout | Priority | ✅ | ❌ | 3.62s | 5.60s | 651 | 1,384 |
| `C08` | `TKT-38181` | M2_code51_confused_with_timeout | Standard | ✅ | ✅ | 2.47s | 4.32s | 772 | 1,459 |
| `C11` | `TKT-88454` | M3_2fa_fallback_step_omitted | Standard | ✅ | ✅ | 2.05s | 5.27s | 671 | 1,434 |
| `C12` | `TKT-21664` | M3_2fa_fallback_step_omitted | Standard | ✅ | ✅ | 3.62s | 5.46s | 750 | 1,532 |
| `C16` | `TKT-92654` | M4_cardholder_format_rule_omitted | Standard | ✅ | ✅ | 4.56s | 7.07s | 664 | 1,590 |
| `C18` | `TKT-62515` | M4_cardholder_format_rule_omitted | Standard | ❌ | ✅ | 2.52s | 7.65s | 726 | 1,611 |
| `C21` | `TKT-66518` | M5_hallucinated_refund_sla | Priority | ✅ | ✅ | 2.45s | 5.03s | 584 | 1,289 |
| `C22` | `TKT-16240` | M5_hallucinated_refund_sla | Priority | ✅ | ✅ | 2.49s | 11.71s | 604 | 1,224 |
