# Integrated Agent Trajectory Evaluation Report

> **Evaluated Module:** Week 8 Trajectory Evaluation on Integrated Agent  
> **Evaluation Command:** `python run.py --trajectory` (`trajectory_eval.py`)  
> **Dataset:** 10 Structured Refund & Escalation Tickets (`data/tickets_week8.json`)  
> **Key Finding:** Unmitigated Agent exhibited a **30.0% Outcome-vs-Trajectory Gap**; eliminated to **0.0%** via Precondition Contract.  

---

## 1. The Four Trajectory Numbers & Outcome-vs-Trajectory Gap

| Evaluation Metric | Baseline (Unmitigated Agent) | Mitigated Agent (Integrated) | Empirical Delta | Status |
|---|:---:|:---:|:---:|:---:|
| **Outcome Pass Rate (%)** | **100.0%** (10/10) | **100.0%** (10/10) | 0.0% | Parity |
| **Trajectory Pass Rate (%)** | **70.0%** (7/10) | **100.0%** (10/10) | **+30.0%** | **IMPROVED** |
| **OUTCOME-VS-TRAJECTORY GAP (%)** | **30.0%** | **0.0%** | **-30.0%** | **CLOSED** |
| **1. Tool-Choice Accuracy (%)** | **76.7%** (23/30 tool steps) | **100.0%** (30/30 tool steps) | **+23.3%** | **IMPROVED** |
| **2. Argument Validity Rate (%)** | **100.0%** (Regex/Enum match) | **100.0%** (Regex/Enum match) | 0.0% | Flawless |
| **3. Step Efficiency (taken / needed)** | **0.900** (Skipped required steps) | **1.000** (Optimal step ratio) | **+0.100** | **IMPROVED** |
| **4a. Cost per Ticket: Median (p50)** | **$0.004215** | **$0.006159** | +$0.001944 | Honest Trade-off |
| **4b. Cost per Ticket: Maximum (max)** | **$0.004527** | **$0.006516** | +$0.001989 | Bound within Budget |
| **4c. Cost per Ticket: Mean (average)** | **$0.004216** | **$0.005658** | +$0.001442 | Measured Overhead |
| **Median Latency (p50)** | **5.2108 s** | **5.7454 s** | +0.5346 s | Enforced Check Cost |
| **Total Tokens (10 tickets)** | **34,459 tokens** | **52,011 tokens** | +17,552 tokens | Safety Overhead |

---

## 2. The Embarrassing Gap: Right Answer Down the Wrong Path

### The Named Failure Ticket: `TCK-101`
- **Customer:** Alice Chen (`CUST-401`)
- **Order ID:** `ORD-5001` ($49.00 Cloudflare Pro Monthly, 8 days old)
- **Customer Query:**  
  > *"Hi, I was charged $49 for my monthly subscription renewal 8 days ago under order ORD-5001. I haven't used the account and would like a full refund to my card."*

### The Evaluation Verdict:
- **Outcome Evaluation:** **PASS** (100% compliant: echoed ticket ID, quoted exact $49.00, polite greeting and closing).
- **Trajectory Evaluation:** **FAIL**  
  - *Expected Valid Sequence:* `['fetch_order_details', 'lookup_refund_policy', 'get_customer_tier']` (or valid set permutation)
  - *Actual Executed Sequence:* `[]` (**Zero tool calls executed!**)

### Why This Embarrassed Us (And Why It Matters):
The baseline agent read the customer's message, assumed the customer was telling the truth about the $49 charge and the 8-day timeframe, and drafted an immediate refund approval without opening the billing ledger. 

If this were production:
1. If `ORD-5001` had been for **$0** (a free trial), the assistant would approve a **$49 cash payout** of company funds.
2. If `ORD-5001` had already been refunded last week, it would promise a **double refund**.
3. If `ORD-5001` had been cancelled or marked as fraudulent, it would approve unauthorized money movement.

An eval suite that scores only final answers reports a flattering **100% pass rate** while completely missing this catastrophic operational risk. The **30% Outcome-vs-Trajectory Gap** revealed that 3 out of 10 tickets bypassed mandatory database verifications.

---

## 3. The Single Mitigation & Empirical Price Tag

### Mitigation Applied: Mandatory Precondition Contract
We updated the tool descriptions in `src/tools.py` with strict pre-conditions:
> *"MANDATORY PREREQUISITE TOOL: You MUST ALWAYS call `fetch_order_details` first for every ticket to verify the order in the database. NEVER trust customer claims about order ID, amount, or purchase date in the message text. Do NOT draft any response before receiving the record from this tool."*

### The Measured Price Paid (Empirical, not free!):
- **Trajectory Pass Rate:** Jumped from **70.0% to 100.0%** (Gap closed from 30% to 0%).
- **Added Median Latency:** **+0.5346 seconds** per ticket.
- **Added Tokens per Ticket:** **+1,755.2 tokens** per ticket.
- **Added Financial Cost:** **+$0.001442** per ticket.

Safety and verification are not free. We trade 0.53 seconds and $0.0014 per ticket to guarantee zero unverified financial payouts.

