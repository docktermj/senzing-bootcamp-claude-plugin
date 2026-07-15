#!/usr/bin/env bash
# UserPromptSubmit hook: "to capture bootcamp feedback".
#
# Only active during a bootcamp (a config/bootcamp_progress.json file exists in
# the working directory). If the bootcamper's message asks to give feedback or to
# change verbosity, inject guidance so those "at any time" requests are handled
# the same way anywhere in the bootcamp. Emits nothing otherwise, so the plugin
# never alters unrelated Claude Code sessions.
input="$(cat)"

# Gate: outside a bootcamp, do nothing at all.
if [ ! -f "config/bootcamp_progress.json" ]; then
  exit 0
fi

lower="$(printf '%s' "$input" | tr '[:upper:]' '[:lower:]')"

ctx=""
if printf '%s' "$lower" | grep -Eq 'bootcamp feedback|plugin feedback|power feedback|submit feedback|provide feedback|i have feedback|report an issue|report a bug'; then
  ctx="The bootcamper is submitting bootcamp feedback. Follow the bootcamp feedback workflow (the feedback.md file in the bootcamp-onboarding skill): silently capture context from config/bootcamp_progress.json (current module, completed modules) and what they were just doing, then gather the feedback one leading question at a time. APPEND (never overwrite) a formatted entry to docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md, creating that file with its header if it does not exist. Do not submit feedback externally unless the bootcamper explicitly asks. When done, return the bootcamper to exactly where they left off without making them re-explain their context."
elif printf '%s' "$lower" | grep -Eq 'change verbosity|more detail|less detail|more code walkthrough|be more concise|be more detailed|too verbose|too terse|more verbose|less verbose'; then
  ctx="The bootcamper wants to change the bootcamp's verbosity. Update the verbosity settings in config/bootcamp_preferences.yaml per the bootcamp ground rules, confirm the new setting in one sentence, then continue from where they left off. This is not a gate and must not interrupt the current step's pending question."
fi

if [ -n "$ctx" ]; then
  esc="$(printf '%s' "$ctx" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null)"
  if [ -n "$esc" ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":%s}}\n' "$esc"
  fi
fi
exit 0
