import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.reply_drafter import draft_reply  # noqa: E402

CASES = ROOT / "eval" / "cases.jsonl"
LABELS = ROOT / "labels_25.json"
RESULTS_DIR = ROOT / "results"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_cases():
    cases = [json.loads(l) for l in CASES.read_text(encoding="utf-8").splitlines() if l.strip()]
    for c in cases:
        c["reply"] = draft_reply(c["ticket"], c["rag_answer"])
        c["reply_sha"] = sha(c["reply"])
    return cases


def load_labels():
    if not LABELS.exists():
        return None
    return json.loads(LABELS.read_text(encoding="utf-8"))


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def labels_commit():
    """(hash, ISO commit time) of the first commit that added labels_25.json, or None."""
    out = git("log", "--diff-filter=A", "--format=%H %cI", "--", LABELS.name)
    if not out:
        return None
    return tuple(out.splitlines()[-1].split(" ", 1))


def labels_dirty():
    return bool(git("status", "--porcelain", "--", LABELS.name))
