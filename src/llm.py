"""
Unified LLM Client and Token/Cost Accounting for Week 7 Race.

Ensures identical model, client credentials, and pricing math for both
the Hand-Built Agent and the Fixed Workflow.
"""

import json
import os
from pathlib import Path
from typing import Tuple
import anthropic

MODEL_NAME = "claude-haiku-4-5"

# Pricing per million tokens (Claude 3.5 Haiku standard rates)
PROMPT_PRICE_PER_MTOK = 0.80
COMPLETION_PRICE_PER_MTOK = 4.00


def get_anthropic_client() -> anthropic.Anthropic:
    """
    Initializes Anthropic client with fallback to Claude CLI OAuth credentials
    stored in ~/.claude/.credentials.json if ANTHROPIC_API_KEY is unset.
    """
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        cred_path = Path.home() / ".claude" / ".credentials.json"
        if cred_path.exists():
            try:
                creds = json.loads(cred_path.read_text(encoding="utf-8"))
                tok = creds.get("claudeAiOauth", {}).get("accessToken")
                if tok:
                    os.environ["ANTHROPIC_AUTH_TOKEN"] = tok
            except Exception:
                pass
    return anthropic.Anthropic()


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculates exact dollar cost for prompt and completion tokens.
    """
    cost_prompt = (input_tokens / 1_000_000.0) * PROMPT_PRICE_PER_MTOK
    cost_completion = (output_tokens / 1_000_000.0) * COMPLETION_PRICE_PER_MTOK
    return round(cost_prompt + cost_completion, 7)
