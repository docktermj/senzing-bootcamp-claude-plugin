#!/usr/bin/env bash
# Stop hook: a safety net that nudges for a single closing 👉 question. It fires ONLY when a
# bootcamp is active AND the model actually forgot the question, and it can NEVER loop.
#
# Three deterministic gates, checked in order. The hook stays silent (exit 0, no output) unless
# ALL three pass:
#   1. stop_hook_active is true  -> return success immediately. This is the loop breaker: a Stop
#      hook that blocks re-runs on the continuation it caused, so without this guard the nudge
#      re-fired every turn until Claude Code hit its block cap. (The harness itself advises:
#      "check stop_hook_active in the input and return success while it's true".)
#   2. No config/bootcamp_progress.json -> not a bootcamp; never touch unrelated sessions.
#   3. The last assistant turn already ended with a 👉 question -> the closing question exists,
#      so add nothing (honors the "ask each question only once" invariant).
# Only when none of the above short-circuits does it inject exactly one closing-question nudge.

# Read the hook payload once (stdin must be consumed).
input="$(cat)"

# Gate 1: never re-fire on our own continuation. This alone prevents the block-cap loop.
if printf '%s' "$input" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

# Gate 2: only act during an active bootcamp.
if [ ! -f "config/bootcamp_progress.json" ]; then
  exit 0
fi

# Gate 3: if the last assistant turn already ended with a 👉 pointer question, add nothing.
# Best-effort: parse the transcript when python3 is available. If we cannot tell, we fall
# through to the nudge, which is safe (gate 1 still guarantees it blocks at most once).
transcript="$(printf '%s' "$input" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
if [ -n "$transcript" ] && [ -f "$transcript" ] && command -v python3 >/dev/null 2>&1; then
  if python3 - "$transcript" <<'PY'
import json, sys

last_text = ""
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
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
                texts = [c.get("text", "") for c in content
                         if isinstance(c, dict) and c.get("type") == "text"]
                if texts:
                    last_text = "\n".join(texts)
except OSError:
    sys.exit(2)  # can't read transcript -> undecided; let the shell nudge

# Exit 0 => a pointer question is already pending => the hook stays silent.
sys.exit(0 if "\U0001f449" in last_text else 1)
PY
  then
    exit 0
  fi
fi

# All gates passed: block once and ask for the single closing question. Because gate 1 releases
# on the very next Stop, this blocks at most one time.
cat <<'JSON'
{"decision":"block","reason":"Bootcamp is active and your last turn ended without a 👉 closing question. If you just completed a bootcamp step and it is your turn to yield, add exactly one closing question — prefixed with 👉 and bolded — inviting the next step. Otherwise (you are mid-work, or the bootcamp is complete) add nothing."}
JSON
exit 0
