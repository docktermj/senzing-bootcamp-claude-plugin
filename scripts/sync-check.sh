#!/usr/bin/env bash
set -euo pipefail
# Show what changed in the Kiro Power since the last-synced commit, scoped to the
# content that maps into this Claude plugin. See MIGRATION.md.
#
# Usage: scripts/sync-check.sh [path-to-kiro-repo]

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # plugin repo root
state="$here/.sync-state.json"
[ -f "$state" ] || { echo "Missing $state" >&2; exit 1; }

field() { python3 -c "import json;print(json.load(open('$state'))$1)"; }

kiro_local="$(field "['source']['local']")"
kiro_local="${kiro_local/#\~/$HOME}"
synced="$(field "['syncedCommit']")"
kiro="${1:-$kiro_local}"

[ -d "$kiro/.git" ] || { echo "Kiro repo not found at: $kiro" >&2; exit 1; }

# Content paths that map into this plugin (keep in step with MIGRATION.md).
paths=(senzing-bootcamp .kiro/hooks)

echo "Kiro repo:     $kiro"
echo "Synced commit: ${synced:0:7}"
echo "Kiro HEAD:     $(git -C "$kiro" rev-parse --short HEAD) ($(git -C "$kiro" branch --show-current))"
echo

if ! git -C "$kiro" cat-file -e "${synced}^{commit}" 2>/dev/null; then
  echo "WARNING: synced commit $synced not found in the Kiro repo (fetch or fix .sync-state.json)." >&2
  exit 1
fi
if ! git -C "$kiro" merge-base --is-ancestor "$synced" HEAD 2>/dev/null; then
  echo "WARNING: synced commit is not an ancestor of HEAD (history rewritten?)." >&2
fi

echo "=== Changed bootcamp content since last sync ==="
if git -C "$kiro" diff --quiet "$synced" HEAD -- "${paths[@]}"; then
  echo "(no changes in mapped content paths -- plugin is in sync)"
else
  git -C "$kiro" diff --stat "$synced" HEAD -- "${paths[@]}"
  echo
  echo "Full diff:  git -C \"$kiro\" diff $synced HEAD -- ${paths[*]}"
  echo "Then port per MIGRATION.md and bump syncedCommit in .sync-state.json."
fi
