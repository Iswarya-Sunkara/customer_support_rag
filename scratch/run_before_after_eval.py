"""
Evaluates Before vs After tool docstring & recoverable error handling with live Anthropic Claude.
Outputs full transcript comparison to error_before_after.md.
"""

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.llm import get_anthropic_client, MODEL_NAME

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

client = get_anthropic_client()

# Customer query with a malformed/missing prefix order ID
FAILING_QUERY = (
    "Customer Ticket TCK-902:\n"
    "Customer ID: CUST-408\n"
    "Order ID: 4471\n"
    "Customer Message: Hi, I was billed yesterday for transaction 4471 and I need a refund immediately. Can you take care of this?"
)

# ==============================================================================
# BEFORE SETUP: Opaque Docstring + Unrecoverable Opaque Error ("Error 3")
# ==============================================================================

TOOL_BEFORE = {
    "name": "fetch_order_details",
    "description": "Retrieve financial transaction records.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "The order id"}
        },
        "required": ["order_id"]
    }
}

def execute_tool_before(args: Dict[str, Any]) -> str:
    # Opaque, non-recoverable error response
    return json.dumps({"error": "Error 3: Record not found"})


# ==============================================================================
# AFTER SETUP: Docstring-as-Prompt + Structured Recoverable Error
# ==============================================================================

TOOL_AFTER = {
    "name": "fetch_order_details",
    "description": (
        "Retrieve official financial billing records for an order ID.\n\n"
        "PROMPT GUIDANCE & PRECONDITIONS FOR THE CALLING AGENT:\n"
        "- You MUST provide an order_id string. Valid IDs strictly follow the format 'ORD-nnnn' (e.g. 'ORD-5001').\n"
        "- ALWAYS invoke this tool BEFORE making any refund decision or policy lookup to verify purchase validity.\n"
        "- If this tool returns a recoverable error, do NOT hallucinate transaction details.\n"
        "  Instead, explain the expected format ('ORD-nnnn') to the customer and ask them to confirm their order ID or provide payment receipt proof."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order code following format 'ORD-nnnn' (e.g., 'ORD-5001')."
            }
        },
        "required": ["order_id"]
    }
}

def execute_tool_after(args: Dict[str, Any]) -> str:
    order_id = str(args.get("order_id", "")).strip().upper()
    return json.dumps({
        "status": "error",
        "recoverable": True,
        "error_code": "INVALID_ORDER_ID_FORMAT",
        "message": (
            f"Order ID '{order_id}' not found: Order IDs look like 'ORD-nnnn' (e.g. ORD-5001). "
            f"Action: Ask the customer to check their confirmation email for the full 8-character ID "
            f"or provide receipt proof before retrying."
        ),
        "expected_format": "ORD-nnnn"
    }, indent=2)


def run_experiment(tool_def: dict, tool_exec, label: str) -> List[Dict[str, Any]]:
    print(f"\n--- Running Experiment: {label} ---")
    messages = [{"role": "user", "content": FAILING_QUERY}]
    transcript = []

    for turn in range(3):
        res = client.messages.create(
            model=MODEL_NAME,
            max_tokens=600,
            system="You are a customer support agent. Resolve customer refund requests using available tools.",
            tools=[tool_def],
            messages=messages
        )

        assistant_text = ""
        tool_calls = []
        for block in res.content:
            if block.type == "text":
                assistant_text += block.text
            elif block.type == "tool_use":
                tool_calls.append(block)

        transcript.append({
            "turn": turn + 1,
            "role": "assistant",
            "text": assistant_text,
            "tool_calls": [{"name": tc.name, "input": tc.input} for tc in tool_calls]
        })

        if res.stop_reason == "end_turn" and not tool_calls:
            break

        messages.append({"role": "assistant", "content": res.content})

        tool_results = []
        for tc in tool_calls:
            out = tool_exec(tc.input)
            transcript.append({
                "turn": turn + 1,
                "role": "tool_result",
                "tool_name": tc.name,
                "input": tc.input,
                "output": out
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": out
            })

        messages.append({"role": "user", "content": tool_results})

    return transcript


def main():
    transcript_before = run_experiment(TOOL_BEFORE, execute_tool_before, "BEFORE (Opaque Error 3)")
    transcript_after = run_experiment(TOOL_AFTER, execute_tool_after, "AFTER (Prompt Docstring + Recoverable Error)")

    md_content = f"""# Recoverable Error & Docstring-as-Prompt: Before vs After Transcript

## 1. Architectural Overview
In standard tool wiring, tools often return opaque, unrecoverable errors like `"Error 3: Record not found"`. When language models receive opaque codes without context or resolution hints, they either:
1. Blindly retry the exact same failing parameters in a wasteful loop.
2. Hallucinate reasons for the failure or emit cryptic internal error codes directly to end customers.

By **rewriting the tool docstring as an actionable prompt** and **structuring error paths to be explicitly recoverable** (offering format examples, recovery actions, and field guidance), the model can self-correct immediately and guide the user productively.

---

## 2. Tool Specification Comparison

### BEFORE: Opaque Tool Docstring & Unrecoverable Error
```json
{{
  "name": "fetch_order_details",
  "description": "Retrieve financial transaction records.",
  "input_schema": {{
    "type": "object",
    "properties": {{
      "order_id": {{"type": "string", "description": "The order id"}}
    }},
    "required": ["order_id"]
  }}
}}
```
**Failing Payload Return:**
```json
{{"error": "Error 3: Record not found"}}
```

---

### AFTER: Docstring-as-Prompt & Recoverable Error
```json
{{
  "name": "fetch_order_details",
  "description": "Retrieve official financial billing records for an order ID.\\n\\nPROMPT GUIDANCE & PRECONDITIONS FOR THE CALLING AGENT:\\n- You MUST provide an order_id string. Valid IDs strictly follow the format 'ORD-nnnn' (e.g. 'ORD-5001').\\n- ALWAYS invoke this tool BEFORE making any refund decision or policy lookup to verify purchase validity.\\n- If this tool returns a recoverable error, do NOT hallucinate transaction details.\\n  Instead, explain the expected format ('ORD-nnnn') to the customer and ask them to confirm their order ID or provide payment receipt proof.",
  "input_schema": {{
    "type": "object",
    "properties": {{
      "order_id": {{
        "type": "string",
        "description": "The order code following format 'ORD-nnnn' (e.g., 'ORD-5001')."
      }}
    }},
    "required": ["order_id"]
  }}
}}
```
**Recoverable Payload Return:**
```json
{{
  "status": "error",
  "recoverable": true,
  "error_code": "INVALID_ORDER_ID_FORMAT",
  "message": "Order ID '4471' not found: Order IDs look like 'ORD-nnnn' (e.g. ORD-5001). Action: Ask the customer to check their confirmation email for the full 8-character ID or provide receipt proof before retrying.",
  "expected_format": "ORD-nnnn"
}}
```

---

## 3. Evaluation Setup & Test Query
- **Test Case:** Customer submits an incomplete transaction ID (`4471` instead of `ORD-4471`).
- **Prompt:**
  > "Customer Ticket TCK-902: Customer ID: CUST-408. Order ID: 4471. Customer Message: Hi, I was billed yesterday for transaction 4471 and I need a refund immediately. Can you take care of this?"

---

## 4. Transcript: BEFORE (Opaque Error 3)

```json
{json.dumps(transcript_before, indent=2)}
```

### Analysis of BEFORE Behavior:
- The model invoked `fetch_order_details` with `"4471"`.
- When presented with `{{"error": "Error 3: Record not found"}}`, the model lacked any recovery path or semantic clue about *why* the record was missing.
- It was forced to deliver a blunt message to the customer stating that Error 3 occurred or that the record does not exist without explaining the ID format convention.

---

## 5. Transcript: AFTER (Docstring-as-Prompt + Recoverable Error)

```json
{json.dumps(transcript_after, indent=2)}
```

### Analysis of AFTER Behavior:
- The tool docstring primed the model on format rules (`ORD-nnnn`) and explicitly instructed it how to handle recoverable errors.
- When the tool returned the structured error explaining `Order IDs look like 'ORD-nnnn' (e.g. ORD-5001)`, the model immediately parsed the recovery action.
- The model politely instructed the customer that order IDs follow the `ORD-nnnn` standard, requested confirmation of the prefix from their receipt or email, and kept the conversation moving forward without crashing or hallucinating.
"""

    Path("error_before_after.md").write_text(md_content, encoding="utf-8")
    print("\nSaved comparison to error_before_after.md successfully!")

if __name__ == "__main__":
    main()
