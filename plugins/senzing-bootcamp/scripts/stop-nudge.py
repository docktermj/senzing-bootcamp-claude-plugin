#!/usr/bin/env python3
"""Stop hook: a safety net that nudges for a single closing 👉 question. It fires
ONLY when a bootcamp is active AND the model actually forgot the question, and it can
NEVER loop.

Gates, checked in order. The hook stays silent (exit 0, no output) unless every
gate passes:
  1. stop_hook_active is true  -> return success immediately. This is the loop
     breaker: a Stop hook that blocks re-runs on the continuation it caused, so
     without this guard the nudge re-fired every turn until Claude Code hit its
     block cap.
  2. No config/bootcamp_progress.json -> not a bootcamp; never touch unrelated
     sessions.
  3. The bootcamper opted out (env var or preferences key) -> stay silent. Gives a
     documented way to disable/quiet the nudge (see hooks/README.md).
  3b. The bootcamp is complete (``bootcamp_complete: true`` in preferences, set by
     graduation before the terminal "END OF SENZING BOOTCAMP" banner) -> stay silent,
     so the net never nudges for a closing question after the bootcamp is over.
  4. The current turn already ended with a 👉 question -> the closing question
     exists, so add nothing (honors the "ask each question only once" invariant).

Gate 4 detection is deliberately biased toward silence. A blocking Stop hook forces
the model to produce output again, so a false positive is how a bootcamper ends up
seeing the same 👉 question twice — the #1 complaint (zero tolerance). Two defenses
address it: (a) this gate scans the whole current turn (every assistant record since
the last real user prompt), handles a string OR list ``message.content``, and stays
silent when the turn's assistant text is not yet on disk (a flush/timing race) —
a missed nudge is far cheaper than a duplicate; and (b) even if the hook does block,
the block reason tells the model to verify its own last message first and repeat
nothing, so a false block can never surface as a duplicate question.

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required.
"""
import json
import os
import sys

POINTER = "\U0001f449"  # 👉


def content_of(rec):
    """The message content of a transcript record, or None."""
    msg = rec.get("message")
    return msg.get("content") if isinstance(msg, dict) else None


def assistant_text(rec):
    """Concatenated visible text of an assistant record. Handles both the list
    (content blocks) and the plain-string shapes of ``message.content``."""
    content = content_of(rec)
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    if isinstance(content, str):
        return content
    return ""


def is_real_user_prompt(rec):
    """True for a genuine user prompt, False for a tool-result carrier record.
    Tool results arrive as ``user`` records whose content is a list of
    ``tool_result`` blocks; those do not delimit a new turn."""
    if rec.get("type") != "user":
        return False
    content = content_of(rec)
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return not any(
            isinstance(block, dict) and block.get("type") == "tool_result"
            for block in content
        )
    return False


def truthy(value):
    """Interpret a string/bool as an on/off flag without a YAML dependency."""
    if isinstance(value, bool):
        return value
    return str(value).strip().strip("\"'").lower() in {"1", "true", "yes", "on"}


def pref_flag(key):
    """True if a top-level ``key: <truthy>`` entry is set in
    config/bootcamp_preferences.yaml. The YAML is scanned line-by-line so no
    third-party parser is required (INV-052: python3-only)."""
    prefs = os.path.join("config", "bootcamp_preferences.yaml")
    try:
        with open(prefs, encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped.startswith("#") or ":" not in stripped:
                    continue
                name, _, val = stripped.partition(":")
                # top-level key only (no leading indentation)
                if name == key and line[:1] not in (" ", "\t"):
                    return truthy(val)
    except OSError:
        pass
    return False


def nudge_disabled():
    """Honor an explicit opt-out: the SENZING_BOOTCAMP_DISABLE_STOP_NUDGE env var,
    or a top-level ``disable_stop_nudge: true`` key in
    config/bootcamp_preferences.yaml (INV-055)."""
    if truthy(os.environ.get("SENZING_BOOTCAMP_DISABLE_STOP_NUDGE", "")):
        return True
    return pref_flag("disable_stop_nudge")


def bootcamp_complete():
    """True once graduation has ended the bootcamp. The graduation closing step
    sets a top-level ``bootcamp_complete: true`` in config/bootcamp_preferences.yaml
    right before it renders the terminal "END OF SENZING BOOTCAMP" banner (which
    ends the turn with no 👉 question). Standing down here keeps the safety net from
    nudging for a closing question after the bootcamp is over."""
    return pref_flag("bootcamp_complete")


def current_turn_text(transcript_path):
    """Return the concatenated assistant text produced since the last real user
    prompt (the current turn), or None if the transcript cannot be read. Sidechain
    (subagent) records are excluded — they are not the user-facing turn."""
    records = []
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        return None

    # Find the last genuine user prompt; the current turn is everything after it.
    start = 0
    for idx, rec in enumerate(records):
        if is_real_user_prompt(rec):
            start = idx + 1

    texts = [
        assistant_text(rec)
        for rec in records[start:]
        if rec.get("type") == "assistant" and not rec.get("isSidechain")
    ]
    return "\n".join(t for t in texts if t)


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

# Gate 3: respect an explicit opt-out.
if nudge_disabled():
    sys.exit(0)

# Gate 3b: stand down once the bootcamp is complete. Graduation's terminal
# "END OF SENZING BOOTCAMP" banner ends the turn with no 👉 question on purpose;
# without this the safety net would nudge for one after the bootcamp is over.
if bootcamp_complete():
    sys.exit(0)

# Gate 4: block ONLY when we can positively read the current turn and it ended
# without a 👉 question. Every other case biases to silence, because a blocking Stop
# hook forces another turn and a false block is how a duplicate 👉 question reaches
# the bootcamper (the #1 complaint). Undecided -> silent covers: no transcript path,
# a missing/unreadable file, and a turn whose assistant text is not yet flushed.
transcript = payload.get("transcript_path", "")
turn_text = current_turn_text(transcript) if transcript else None
if turn_text is None:
    sys.exit(0)  # no readable transcript -> undecided -> stay silent
if POINTER in turn_text:
    sys.exit(0)  # a pointer question is already pending -> stay silent
if not turn_text.strip():
    sys.exit(0)  # nothing flushed for this turn yet -> stay silent

# All gates passed: block once and ask for the single closing question. Gate 1
# releases on the very next Stop, so this blocks at most one time. The reason makes
# a false block harmless: the model checks its own last message and never repeats a
# question it already asked.
print(json.dumps({
    "decision": "block",
    "reason": (
        "Bootcamp is active. Before doing anything else, re-read your own most "
        "recent message. If it ALREADY ends with a single 👉 closing question, you "
        "have asked it — do NOT ask it again; simply end your turn without "
        "repeating the question. Only if your last message genuinely has no 👉 "
        "closing question, and you just finished a bootcamp step and it is your "
        "turn to yield, add exactly one closing question, prefixed with 👉 and "
        "bolded, inviting the next step. If you are mid-work or the bootcamp is "
        "complete, add nothing."
    ),
}, ensure_ascii=False))
sys.exit(0)
