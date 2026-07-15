#!/usr/bin/env bash
# Stop hook: nudge for a single closing question ONLY when a bootcamp is active.
# "Active" = a bootcamp progress file exists in the working directory. In any other
# session (including building/porting the bootcamp itself) this emits nothing, so the
# plugin never alters unrelated Claude Code turns.
if [ ! -f "config/bootcamp_progress.json" ]; then
  exit 0
fi
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"Bootcamp is active. If you just completed a bootcamp step and no leading question is already pending, end your turn with exactly one closing question, prefixed with the pointer marker (the pointing-hand emoji) and bolded, inviting the next step. If a leading question is already pending, or you did not just complete a step, add nothing."}}
JSON
exit 0
