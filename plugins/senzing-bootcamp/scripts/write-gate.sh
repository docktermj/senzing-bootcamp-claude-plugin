#!/usr/bin/env bash
# PreToolUse gate for Write/Edit: block stray paths and obvious secrets DURING a bootcamp only.
# Read the hook payload first (stdin must be consumed either way).
input="$(cat)"

# Gate: only enforce when a bootcamp is active, so the plugin never blocks writes in
# unrelated Claude Code sessions.
if [ ! -f "config/bootcamp_progress.json" ]; then
  exit 0
fi

if printf '%s' "$input" | grep -Eq '/tmp/|%TEMP%|/Downloads/'; then
  echo "Write blocked: use a project-relative path, not a system temp or Downloads directory." >&2
  exit 2
fi

if printf '%s' "$input" | grep -Eq 'BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|AKIA[0-9A-Z]{16}'; then
  echo "Write blocked: a possible hardcoded secret was detected. Use environment variables instead." >&2
  exit 2
fi

exit 0
