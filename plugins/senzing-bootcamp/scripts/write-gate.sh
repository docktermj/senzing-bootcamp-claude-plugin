#!/usr/bin/env bash
# PreToolUse gate for Write/Edit: block stray paths and obvious secrets.
input="$(cat)"

if printf '%s' "$input" | grep -Eq '/tmp/|%TEMP%|/Downloads/'; then
  echo "Write blocked: use a project-relative path, not a system temp or Downloads directory." >&2
  exit 2
fi

if printf '%s' "$input" | grep -Eq 'BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|AKIA[0-9A-Z]{16}'; then
  echo "Write blocked: a possible hardcoded secret was detected. Use environment variables instead." >&2
  exit 2
fi

exit 0
