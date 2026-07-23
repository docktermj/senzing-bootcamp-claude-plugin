#!/usr/bin/env python3
"""UserPromptSubmit hook: "to capture bootcamp feedback and verbosity changes".

Only active during a bootcamp (a config/bootcamp_progress.json file exists in the
working directory). If the bootcamper's message asks to give feedback or to change
verbosity, inject guidance so those "at any time" requests are handled the same way
anywhere in the bootcamp. Emits nothing otherwise, so the plugin never alters
unrelated Claude Code sessions.

Cross-platform: invoked in exec form (``python3 <path>``) so no shell is required.
"""
import json
import os
import re
import sys

raw = sys.stdin.read()

# Gate: outside a bootcamp, do nothing at all.
if not os.path.isfile(os.path.join("config", "bootcamp_progress.json")):
    sys.exit(0)

# The prompt text is what we inspect; fall back to the raw payload if it is not JSON.
try:
    prompt = json.loads(raw).get("prompt", "")
except (ValueError, AttributeError):
    prompt = raw
lower = prompt.lower()

FEEDBACK = re.compile(
    r"bootcamp feedback|plugin feedback|power feedback|submit feedback|"
    r"provide feedback|i have feedback|report an issue|report a bug"
)
VERBOSITY = re.compile(
    r"change verbosity|more detail|less detail|more code walkthrough|"
    r"be more concise|be more detailed|too verbose|too terse|more verbose|less verbose"
)

ctx = ""
if FEEDBACK.search(lower):
    ctx = (
        "The bootcamper is submitting bootcamp feedback. Follow the bootcamp "
        "feedback workflow (the feedback.md file in the bootcamp-onboarding skill): "
        "begin with the pinned BOOTCAMP FEEDBACK entry banner and end with the "
        "FEEDBACK SAVED exit banner (see feedback.md for the verbatim banner wording); "
        "silently capture as much relevant context as possible (the time; the plugin "
        "version from ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json; current_module, current_step, and "
        "completed modules from config/bootcamp_progress.json; the recent questions "
        "asked and the bootcamper's responses; what the plugin was doing behind the "
        "scenes; the observed problem; the expected behavior per the active "
        "hooks/skills; and why expected did not match actual) -- never ask extra "
        "questions, and record \"Unknown\" when a source is missing. Then gather the "
        "feedback one leading question at a time. APPEND (never overwrite) a "
        "formatted entry to docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md, "
        "creating that file with its header if it does not exist; then verify the "
        "entry landed (re-read and re-append if missing) before telling the "
        "bootcamper it was saved (INV-067). Do not submit "
        "feedback externally unless the bootcamper explicitly asks. When done, "
        "return the bootcamper to exactly where they left off without making them "
        "re-explain their context."
    )
elif VERBOSITY.search(lower):
    ctx = (
        "The bootcamper wants to change the bootcamp's verbosity. Update the "
        "verbosity settings in config/bootcamp_preferences.yaml per the bootcamp "
        "ground rules, confirm the new setting in one sentence, then continue from "
        "where they left off. This is not a gate and must not interrupt the current "
        "step's pending question."
    )

if ctx:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx,
        }
    }))
sys.exit(0)
