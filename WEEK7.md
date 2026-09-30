# Week 7: Agent Loops — and When Not to Use Them (Task Set A)

> **Track A:** Customer support tickets — *Race the ticket agent against a fixed workflow*  
> **Course:** Module 4 · Agents  
> **Evaluation:** Sat on Week 8 · Monday (Marks: 100)

---

## 1. Executive Summary & One-Command Reproduction

Both systems run the identical 10 customer refund tickets against Anthropic Claude 3.5 Haiku (`claude-haiku-4-5`) using the exact same backend tools and output contract.

```bash
# Run both systems head-to-head, generate race.csv and summary table
python src/run_race.py --system all

# Or run each system independently with one command:
python src/run_race.py --system agent       # Hand-built ReAct agent loop
python src/run_race.py --system workflow    # Fixed hard-coded linear DAG

# Test all 4 safety budgets with live clean termination log
python src/run_race.py --test-budget

# Run bonus challenge: persistence across restart + 30-turn thread analysis
python src/bonus_memory.py
```

### Master Dashboard Access
- **FastAPI Web App (Port 8050):** View the live **`W7: Race & Budgets`** tab on `http://127.0.0.1:8050/`
- **Streamlit Web App (Port 8501):** View the **`🏁 Week 7: Agent vs Fixed Workflow Race`** tab on `http://localhost:8501/`

---

## 2. The Official 8-Number Evaluation Table (30 Points)

The race was executed across the identical 10 customer refund tickets (including 3 branching tickets where Step 3 depends on what Step 2 found, e.g. order not found in billing DB).

| Metric | Hand-Built Agent (Loop) | Fixed Hard-Coded Workflow | Empirical Delta / Operational Winner |
|---|:---:|:---:|---|
| **1. Pass Rate (%)** | **100.0%** (10/10) | **100.0%** (10/10) | **Parity** (Both systems achieve 100% compliance) |
| **2. Median Latency (p50)** | **5.9374 s** | **3.0474 s** | **-2.89s (-48.7% faster)** (1 LLM call vs 2 iterative laps) |
| **3. Total Tokens (10 Tickets)** | **34,548 tokens** | **7,860 tokens** | **-26,688 tokens (-77.2%)** (Zero message-list re-sending) |
| **4. Cost per Ticket (USD)** | **$0.004223 / ticket** | **$0.001353 / ticket** | **-$0.002870 (-68.0% cost)** ($0.0135 vs $0.0422 total) |

*Full per-ticket records are committed to [`race.csv`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/race.csv).*

### Detailed Per-Ticket Race Breakdown

| Ticket ID | Customer / Order | Scenario / Branch Type | Agent Latency | Agent Tokens | Workflow Latency | Workflow Tokens | Pass? |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| `TCK-101` | CUST-401 / ORD-5001 | Standard refund (8d <= 30d window) | 8.39s | 3,451 | 2.68s | 764 | ✅ / ✅ |
| `TCK-102` | CUST-402 / ORD-5002 | Standard denial (45d > 30d window) | 5.15s | 3,448 | 2.62s | 787 | ✅ / ✅ |
| `TCK-103` | CUST-403 / ORD-5003 | Priority within window (`[ESCALATE:PRIORITY]`) | 6.02s | 3,480 | 3.50s | 836 | ✅ / ✅ |
| `TCK-104` | CUST-404 / ORD-5004 | Priority outside window (`[ESCALATE:PRIORITY]`) | 5.88s | 3,471 | 2.98s | 806 | ✅ / ✅ |
| `TCK-105` | CUST-405 / ORD-5005 | Already refunded transaction notice | 6.00s | 3,507 | 2.52s | 754 | ✅ / ✅ |
| `TCK-106` | CUST-406 / ORD-5006 | Hardware return (10d <= 14d window) | 5.32s | 3,460 | 4.28s | 807 | ✅ / ✅ |
| `TCK-107` | CUST-407 / ORD-5007 | Hardware denial (22d > 14d window) | 5.53s | 3,465 | 2.62s | 762 | ✅ / ✅ |
| `TCK-108` | CUST-408 / ORD-9991 | **Branching 1:** Missing order -> Receipt request | 5.27s | 3,300 | 3.11s | 706 | ✅ / ✅ |
| `TCK-109` | CUST-409 / ORD-9992 | **Branching 2:** Missing order -> Priority Ops escalation | 7.45s | 3,439 | 3.30s | 782 | ✅ / ✅ |
| `TCK-110` | CUST-410 / ORD-9993 | **Branching 3:** Missing order -> Fraud escalation desk | 7.14s | 3,527 | 4.89s | 856 | ✅ / ✅ |

---

## 3. The Decision Rule Verdict (20 Points)

> **Decision Rule:** *"Does the execution path vary dynamically by input?"*  
> **Word count:** 137 words (Strictly under 150 words).

Applying the decision rule (*"does the execution path vary dynamically by input?"*), **none of the 10 tickets forces an agent**. Although tickets TCK-108, TCK-109, and TCK-110 trigger an escalation branch because their orders are missing, this condition is deterministic: if the order is not found, route to verification. Because the branching rules are known in advance, the fixed workflow handles them in deterministic code without loop overhead. The workflow achieves **100.0% pass rate** while beating the agent on all three operational metrics: **p50 latency dropped from 5.94s to 3.05s (-48.7%)**, **total tokens fell from 34,548 to 7,860 (-77.2%)**, and **cost per ticket decreased from $0.00422 to $0.00135 (-68.0%)**. We would ship the fixed workflow: an agent adds non-deterministic latency and 4.4x token amplification without buying any routing capability that three hard-coded steps cannot deliver.

---

## 4. Third Tool Specification & Parameter Diff (10 Points)

The third tool added to the loop is **`get_customer_tier`** in [`src/tools.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/tools.py).

### Single Responsibility & Non-Overlap Guarantee
1. **`fetch_order_details` (Tool 1):** Single Job = Retrieve the financial transaction record (amount, date, status, category) for an order ID.
2. **`lookup_refund_policy` (Tool 2):** Single Job = Retrieve refund window days and policy rules for a product category enum.
3. **`get_customer_tier` (Tool 3):** Single Job = Retrieve customer account tier and SLA escalation priority for a customer ID.

*No tool descriptions overlap: Tool 1 inspects order transactions; Tool 2 inspects category policies; Tool 3 inspects customer account priority.*

### Parameter Enums
- `SupportChannelEnum`: `["web", "email", "api", "phone"]`
- `CustomerTierEnum`: `["Standard", "Priority", "Enterprise"]`
- `RefundCategoryEnum`: `["subscription", "software", "hardware", "services"]`

### Git Diff ([`results/third_tool_diff.patch`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results/third_tool_diff.patch))

```diff
--- a/src/tools.py	(revision base: 2 tools)
+++ b/src/tools.py	(revision added: third tool get_customer_tier)
@@ -18,6 +18,18 @@
     SERVICES = "services"
 
 
++class SupportChannelEnum(str, Enum):
++    WEB = "web"
++    EMAIL = "email"
++    API = "api"
++    PHONE = "phone"
++
++
++class CustomerTierEnum(str, Enum):
++    STANDARD = "Standard"
++    PRIORITY = "Priority"
++    ENTERPRISE = "Enterprise"
++
 
 # ==============================================================================
 # Tool 1: fetch_order_details
@@ -52,10 +64,36 @@
 }
 
 
+# ==============================================================================
+# Tool 3 (New): get_customer_tier
+# ==============================================================================
+
++TOOL_GET_CUSTOMER_TIER = {
++    "name": "get_customer_tier",
++    "description": "Retrieve customer account tier and SLA escalation priority for a customer ID.",
++    "input_schema": {
++        "type": "object",
++        "properties": {
++            "customer_id": {
++                "type": "string",
++                "description": "The unique customer account identifier (e.g., 'CUST-401')."
++            },
++            "channel": {
++                "type": "string",
++                "enum": ["web", "email", "api", "phone"],
++                "description": "The inbound communication channel used by the customer."
++            }
++        },
++        "required": ["customer_id", "channel"],
++        "additionalProperties": False
++    }
++}
+
 # The complete tool registry exposed to the LLM agent
 TOOLS_REGISTRY = [
     TOOL_FETCH_ORDER,
     TOOL_LOOKUP_POLICY,
++   TOOL_GET_CUSTOMER_TIER
 ]
```

---

## 5. Fixed Workflow Implementation (20 Points)

The fixed workflow in [`src/workflow.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/workflow.py) fulfills the identical task with:
- **Same Inputs:** Identical 10 ticket objects.
- **Same Tools:** Directly calls `fetch_order_details`, `get_customer_tier`, and `lookup_refund_policy`.
- **Same Model:** Anthropic Claude 3.5 Haiku (`claude-haiku-4-5`).
- **Same Output Contract:** Echoes Ticket ID on Line 1, attaches `[ESCALATE:PRIORITY]` if Priority tier, quotes amount ($X.XX), checks policy window, and signs off.
- **No Hidden Loop:** Pure linear DAG:
  1. `order = fetch_order_details(ticket["order_id"])`
  2. `cust = get_customer_tier(ticket["customer_id"], channel)`
  3. `if not order["found"]`: route to escalation branch. `elif order["status"] == "REFUNDED"`: route to settled branch. `else`: `lookup_refund_policy(order["category"])`.
  4. Single LLM call to draft the compliant customer reply.

---

## 6. Safety Budgets Enforcement & Termination Log (20 Points)

All 4 runtime safety limits are actively checked in [`src/agent.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/agent.py) inside the loop before and after every LLM call and tool execution:
1. `max_iterations = 6` (Loop iterations counter)
2. `max_tokens = 4000` (Cumulative input + output tokens across ALL laps)
3. `max_cost = $0.05` (Cumulative dollar cost across ALL laps)
4. `max_wall_clock_seconds = 15.0s` (Elapsed wall-clock timer)

### Clean Termination Run Log ([`results/budget_termination.log`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results/budget_termination.log))

```text
================================================================================
BUDGET TERMINATION RUN LOG
Timestamp: 2026-09-29 05:36:45 UTC
================================================================================
Target Ticket:          TCK-101
Configured Budgets:     max_iterations=1, max_tokens=4000, max_cost=$0.05, max_wall_clock=15.0s
Budget Reached:         max_iterations
Configured Limit:       1
Terminated Cleanly:     True
Elapsed Latency:        1.7216 seconds
Tokens Consumed:        1479
Cost Incurred:          $0.001798
Termination Message:    [BUDGET EXCEEDED] Budget 'max_iterations' breached: current value 2 exceeds configured limit of 1 on ticket TCK-101. Agent terminating cleanly.

Final Clean Fallback Output:
Ticket TCK-101

Hi there,

Your request is undergoing automated processing review. A support specialist will follow up shortly regarding order ORD-5001.

Best regards,
Support Team
================================================================================
```

---

## 7. Bonus Challenge: Persistence & 30-Turn Thread Analysis

Implemented in [`src/bonus_memory.py`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/src/bonus_memory.py) and cached in [`results/bonus_memory_results.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/results/bonus_memory_results.json).

### 1. Fact Persistence Across Full Process Restart
- Fact: Customer `CUST-403` customer_tier = `'Priority'`
- Persisted to local disk file: [`data/agent_memory.json`](file:///c:/Users/kiran/OneDrive/Desktop/projects/customer_support_rag/data/agent_memory.json)
- On new Python process invocation, the tier was loaded directly from disk cache in 0.001s without any tool calls or database queries, surviving full process restart.

### 2. Lossy Summarisation Failure Analysis (3 Long 30-Turn Threads)

| Thread ID | Critical Fact Introduced Early | Detail Destroyed by Summarisation | Failure Impact at Turn 28 |
|---|---|---|---|
| **`TCK-LONG-01`** | Return tracking number `TRK-882914-US` provided in Turn 4 | Alphanumeric tracking code `TRK-882914-US` | Summarisation compressed context to *"customer mailed return package"*. At Turn 28, when customer asked for verification, the agent was forced to ask for the tracking number again. |
| **`TCK-LONG-02`** | Support authorized a **$35.00 goodwill credit** in Turn 5 | Exact dollar amount `$35.00` | Summarisation reduced context to *"billing discounts discussed"*. At Turn 28, agent miscalculated remaining balance by ignoring the $35 credit. |
| **`TCK-LONG-03`** | Warehouse RMA code `RMA-7710-PRIORITY` issued in Turn 6 | Priority barcode suffix `-PRIORITY` | Summarisation simplified code to `RMA-7710`, stripping the priority intake directive needed for express warehouse processing. |

---

## 8. Submission Verification Checklist

- [x] **Agent and workflow both runnable by one command each:**
  - `python src/run_race.py --system agent`
  - `python src/run_race.py --system workflow`
- [x] **`race.csv` and table with all 8 numbers over the same 10 ticket IDs:** Committed to repository root.
- [x] **Log excerpt of budget-triggered termination showing which budget fired:** Committed to `results/budget_termination.log`.
- [x] **Diff of third tool's description and parameter enums:** Committed to `results/third_tool_diff.patch`.
- [x] **Verdict paragraph naming the ticket class that does or does not need an agent:** Written under Section 3 (137 words).
- [x] **Interactive UI integration:** Both FastAPI (`/`) and Streamlit (`port 8501`) feature interactive Week 7 comparison dashboards.
- [x] **Bonus challenge completed:** Process-restart persistence verified and 30-turn thread summarisation loss analyzed.
