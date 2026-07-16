#!/usr/bin/env python3
"""UserPromptSubmit hook: "to capture bootcamp feedback".

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
        "silently capture context from config/bootcamp_progress.json (current "
        "module, completed modules) and what they were just doing, then gather the "
        "feedback one leading question at a time. APPEND (never overwrite) a "
        "formatted entry to docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md, "
        "creating that file with its header if it does not exist. Do not submit "
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
