#!/usr/bin/env bash
# PreToolUse gate for Write/Edit: block writes into the system temp or Downloads
# directory, and block obvious secrets — DURING a bootcamp only.
# Read the hook payload first (stdin must be consumed either way).
input="$(cat)"

# Gate: only enforce when a bootcamp is active, so the plugin never blocks writes in
# unrelated Claude Code sessions.
if [ ! -f "config/bootcamp_progress.json" ]; then
  exit 0
fi

# Extract the write target (tool_input.file_path) from the JSON payload. File paths
# do not contain double quotes, so a simple field match is enough and avoids a hard
# dependency on jq (not guaranteed on Linux/macOS/Windows). tool_input serializes
# file_path before content, so the first match is the real target; fail open (allow
# on location grounds) if extraction yields nothing.
file_path="$(printf '%s' "$input" \
  | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -n1 \
  | sed -E 's/^"file_path"[[:space:]]*:[[:space:]]*"(.*)"$/\1/')"

# An unexpanded Windows temp env-var reference (%TEMP%/%TMP%) is always a temp
# target, independent of the project directory.
case "$file_path" in
  *%TEMP%* | *%TMP%*)
    echo "Write blocked: use a project-relative path, not a system temp or Downloads directory." >&2
    exit 2 ;;
esac

# Resolve to an absolute path. A relative path is, by definition, inside the
# project, so it is always allowed on location grounds.
case "$file_path" in
  /* | [A-Za-z]:[\\/]*) abs_path="$file_path" ;;  # POSIX or Windows-drive absolute
  "")                   abs_path="" ;;            # extraction failed -> fail open
  *)                    abs_path="$PWD/$file_path" ;;
esac

# Location check: exempt the project directory FIRST, then block temp/Downloads.
# The gate's intent is "don't write outside the project"; a project that merely
# lives under a path containing /tmp/ (e.g. /home/user/tmp/proj) must not trip it.
# Match on backslash-normalized paths so Windows targets compare portably.
if [ -n "$abs_path" ]; then
  norm="$(printf '%s' "$abs_path" | tr '\\' '/' | sed -E 's#/+#/#g')"
  pwd_norm="$(printf '%s' "$PWD" | tr '\\' '/' | sed -E 's#/+#/#g')"
  case "$norm" in
    "$pwd_norm"/* | "$pwd_norm")
      : ;;  # inside the project -> allowed on location grounds
    /tmp/* | /var/tmp/* | /private/tmp/* | /private/var/folders/* | */Downloads/* | */AppData/Local/Temp/*)
      echo "Write blocked: use a project-relative path, not a system temp or Downloads directory." >&2
      exit 2 ;;
    *)
      # macOS puts the per-user temp dir under $TMPDIR (e.g. /var/folders/...).
      if [ -n "$TMPDIR" ]; then
        tmp_norm="$(printf '%s' "${TMPDIR%/}" | tr '\\' '/' | sed -E 's#/+#/#g')"
        case "$norm" in
          "$tmp_norm"/*)
            echo "Write blocked: use a project-relative path, not a system temp or Downloads directory." >&2
            exit 2 ;;
        esac
      fi
      ;;
  esac
fi

if printf '%s' "$input" | grep -Eq 'BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|AKIA[0-9A-Z]{16}'; then
  echo "Write blocked: a possible hardcoded secret was detected. Use environment variables instead." >&2
  exit 2
fi

exit 0
