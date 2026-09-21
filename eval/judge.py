"""
LLM judge — one binary criterion (RESOLVES), prompt loaded from judge_vN.txt.

Lines starting with '#' in the prompt file are metadata/comments and are not
sent to the model. Verdicts are cached in results/judge_vN.json keyed by
(prompt hash, reply hash) so re-running the eval does not re-bill.
"""
import json

import anthropic

from common import ROOT, RESULTS_DIR, sha

MODEL = "claude-haiku-4-5"
SCHEMA = {
    "type": "object",
    "properties": {
        "reason": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
    },
    "required": ["reason", "verdict"],
    "additionalProperties": False,
}


def load_prompt(version):
    raw = (ROOT / f"judge_{version}.txt").read_text(encoding="utf-8")
    meta = {}
    body = []
    for line in raw.splitlines():
        if line.startswith("#"):
            if ":" in line:
                k, v = line[1:].split(":", 1)
                meta[k.strip()] = v.strip()
            continue
        body.append(line)
    return "\n".join(body).strip(), meta


def judge_cases(cases, version, refresh=False):
    template, meta = load_prompt(version)
    prompt_sha = sha(template)
    cache_path = RESULTS_DIR / f"judge_{version}.json"
    cache = {}
    if cache_path.exists() and not refresh:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        if cache.get("prompt_sha") != prompt_sha:
            cache = {}
    verdicts = cache.get("verdicts", {})

    client = None
    for c in cases:
        hit = verdicts.get(c["case_id"])
        if hit and hit["reply_sha"] == c["reply_sha"]:
            continue
        client = client or anthropic.Anthropic()
        prompt = template.replace("{question}", c["ticket"]["question"]).replace("{reply}", c["reply"])
        resp = client.messages.create(
            model=MODEL,
            max_tokens=512,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        )
        text = next(b.text for b in resp.content if b.type == "text")
        out = json.loads(text)
        verdicts[c["case_id"]] = {**out, "reply_sha": c["reply_sha"]}
        print(f"  judged {c['case_id']} -> {out['verdict']}", flush=True)

    RESULTS_DIR.mkdir(exist_ok=True)
    cache = {
        "version": version,
        "model": MODEL,
        "prompt_sha": prompt_sha,
        "first_run_at": cache.get("first_run_at") or _now(),
        "verdicts": verdicts,
    }
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    return verdicts, meta, cache


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
