# Thursday Fresh-Eyes Review Note

> **Session:** Pre-Summit External Squad Peer Review  
> **Date:** Thursday, October 29, 2026  
> **Reviewers:**  
> - **Marcus Vance** (Senior Reliability Engineer · SRE & Observability Squad)  
> - **Elena Rostova** (Support Operations Lead · Tier-1 Support Squad)  
> **Host / Author:** Iswarya Sunkara  

---

## 1. Context & Setup
On Thursday afternoon, Marcus and Elena conducted a blind "fresh-eyes" execution of our repository on a clean developer machine. They were handed only the URL to the repository and the instructions in `README.md`. No verbal coaching or internal setup scripts were permitted.

---

## 2. Where the Reviewers Stumbled

### Stumble 1: The Missing Virtualenv Activation Trap
- **The Stumble:** Marcus cloned the repository and immediately ran `python run.py` using his system Python 3.12 interpreter instead of `.venv`. Because `fastmcp` and `langfuse` were installed inside `.venv`, the command crashed with:  
  `ModuleNotFoundError: No module named 'fastmcp'`
- **Marcus's Critique:** *"If you hand this to an executive or an external client, they will not read 5 lines of virtualenv commands. Your single entry point must be genuinely bulletproof."*
- **What We Changed:**  
  Added automatic interpreter self-bootstrapping to the top of `run.py`:
  ```python
  VENV_PYTHON = _REPO_ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
  if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
      args = [str(VENV_PYTHON)] + sys.argv
      sys.exit(subprocess.call(args))
  ```
  Now, even if a stranger runs `python run.py` from their system terminal, `run.py` detects `.venv` and re-executes cleanly without intervention.

---

### Stumble 2: Ambiguous Markdown Link vs Plain Text Citation
- **The Stumble:** Elena tested Ticket 1a (`TKT-84920`) and examined the drafted reply. The reply ended with:  
  `Policy Cited: refund-and-returns-policy-30day-v2`  
  Elena noted: *"Our Tier-1 support reps work inside Zendesk. They don't want to copy a string into their browser URL bar — they need a clickable citation that takes them directly to the exact article section so they can verify the terms while talking to the customer."*
- **What We Changed:**  
  Updated `src/integrated_assistant.py` and `search_help_center` to return standard clickable markdown links:  
  `[refund-and-returns-policy-30day-v2](https://help.example.com/articles/refund-and-returns-policy-30day-v2)`  
  Clicking the citation instantly navigates the support agent directly to the live help-center article.

---

### Stumble 3: Plaintext Customer Emails in Telemetry Logs
- **The Stumble:** Marcus inspected the live trace log (`traces_live.jsonl`) generated during his test run and searched for the query text. He found:  
  `"query": "Hi, I'm Alice Chen (alice.chen@nexuscorp.com) at 742 Evergreen Terrace..."`  
  Marcus flagged this immediately: *"Your logging survives the MCP hop, but your PII line failed. SREs across the entire company have read access to this log stream. You cannot ship with customer emails in raw JSON spans."*
- **What We Changed:**  
  Built `sanitize_pii()` directly into `src/integrated_assistant.py` before any trace object is instantiated. Customer emails are masked to `a***@nexuscorp.com` and physical addresses are redacted to `[REDACTED_POSTAL_ADDRESS]`, holding the PII line strictly.

---

## 3. Reviewer Sign-Off & Verdict

```text
REVIEWER SIGN-OFF:
[x] Single command (python run.py) runs end-to-end without manual intervention.
[x] MCP capabilities (search_help_center, check_customer_entitlement) called live via external client.
[x] Clickable citations strictly distinguish current 30-day terms from retired 14-day terms.
[x] Defensive escalation preferred over hallucinated financial commitments.
[x] PII redaction verified across all local and remote spans.

VERDICT: APPROVED FOR FRIDAY AI SUMMIT DEMO
Signed: Marcus Vance (Reliability Squad) & Elena Rostova (Support Ops Squad)
```

