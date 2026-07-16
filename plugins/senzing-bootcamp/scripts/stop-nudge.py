#!/usr/bin/env python3
"""Stop hook: a safety net that nudges for a single closing 👉 question. It fires
ONLY when a bootcamp is active AND the model actually forgot the question, and it can
NEVER loop.

Three deterministic gates, checked in order. The hook stays silent (exit 0, no
output) unless ALL three pass:
  1. stop_hook_active is true  -> return success immediately. This is the loop
     breaker: a Stop hook that blocks re-runs on the continuation it caused, so
     without this guard the nudge re-fired every turn until Claude Code hit its
     block cap.
  2. No config/bootcamp_progress.json -> not a bootcamp; never touch unrelated
     sessions.
  3. The last assistant turn already ended with a 👉 question -> the closing
     question exists, so add nothing (honors the "ask each question only once"
     invariant).
Only when none of the above short-circuits does it inject exactly one closing
nudge.

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required.
"""
import json
import os
import sys

POINTER = "\U0001f449"  # 👉

data = sys.stdin.read()
try:
    payload = json.loads(data)
except ValueError:
    payload = {}

# Gate 1: never re-fire on our own continuation. This alone prevents the block-cap
# loop.
if payload.get("stop_hook_active") is True:
    sys.exit(0)

# Gate 2: only act during an active bootcamp.
if not os.path.isfile(os.path.join("config", "bootcamp_progress.json")):
    sys.exit(0)

# Gate 3: if the last assistant turn already ended with a 👉 pointer question, add
# nothing. Best-effort: if we cannot tell, fall through to the nudge, which is safe
# (gate 1 still guarantees it blocks at most once).
transcript = payload.get("transcript_path", "")
if transcript and os.path.isfile(transcript):
    try:
        last_text = ""
        with open(transcript, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") != "assistant":
                    continue
                msg = rec.get("message")
                content = msg.get("content") if isinstance(msg, dict) else None
                if isinstance(content, list):
                    texts = [
                        c.get("text", "")
                        for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    ]
                    if texts:
                        last_text = "\n".join(texts)
        if POINTER in last_text:
            sys.exit(0)  # a pointer question is already pending -> stay silent
    except OSError:
        pass  # can't read transcript -> undecided -> fall through to the nudge

# All gates passed: block once and ask for the single closing question. Because gate
# 1 releases on the very next Stop, this blocks at most one time.
print(json.dumps({
    "decision": "block",
    "reason": (
        "Bootcamp is active and your last turn ended without a 👉 closing question. "
        "If you just completed a bootcamp step and it is your turn to yield, add "
        "exactly one closing question — prefixed with 👉 and bolded — inviting the "
        "next step. Otherwise (you are mid-work, or the bootcamp is complete) add "
        "nothing."
    ),
}, ensure_ascii=False))
sys.exit(0)
