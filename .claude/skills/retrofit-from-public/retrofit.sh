#!/usr/bin/env bash
set -euo pipefail
# Retrofit changes made in the PUBLIC access repo (Senzing/senzing-bootcamp-claude-plugin)
# back into this DEVELOPMENT repo. Files only — this never commits or pushes.
#
# It is the inverse of propagate-to-public: it copies the propagated content back
# and applies the INVERSE owner rewrite (Senzing -> docktermj). Because the
# rewrite is a clean inverse, running this when the repos are already in sync
# produces NO change in the dev tree. See SKILL.md for the manifest and rationale.
#
# Usage: retrofit.sh [path-to-public-repo]
#   Default public repo: ~/senzing.git/senzing-bootcamp-claude-plugin

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"   # dev repo root (destination)
default_src="$HOME/senzing.git/senzing-bootcamp-claude-plugin"
src="${1:-$default_src}"

# --- Safety guards --------------------------------------------------------- #
[ -d "$here/plugins/senzing-bootcamp" ] || {
  echo "This doesn't look like the dev repo: $here" >&2; exit 1; }
[ -d "$src/.git" ] || {
  echo "Public repo not found (or not a git repo): $src" >&2; exit 1; }

# Refuse to retrofit from anything but the intended public repo.
origin="$(git -C "$src" remote get-url origin 2>/dev/null || true)"
case "$origin" in
  *Senzing/senzing-bootcamp-claude-plugin*) : ;;
  *) echo "Refusing: source '$src' origin is '$origin', not Senzing/senzing-bootcamp-claude-plugin." >&2
     exit 1 ;;
esac

# Never retrofit from the dev repo into itself.
if [ "$(cd "$here" && pwd)" = "$(cd "$src" && pwd)" ]; then
  echo "Refusing: source and destination are the same directory." >&2; exit 1
fi

command -v rsync >/dev/null 2>&1 || { echo "rsync is required but not found." >&2; exit 1; }

# Warn on a dirty dev tree so the retrofit diff can be reviewed in isolation.
if ! git -C "$here" diff --quiet -- plugins .claude-plugin docs README.md \
   || ! git -C "$here" diff --cached --quiet -- plugins .claude-plugin docs README.md; then
  echo "WARNING: dev working tree already has uncommitted changes in retrofit paths;" >&2
  echo "         the retrofit will overlay onto them (harder to review)." >&2
fi

echo "Source (public): $src"
echo "Public origin:   $origin"
echo "Public branch:   $(git -C "$src" branch --show-current 2>/dev/null || echo '(detached)')"
echo "Dest (dev):      $here"
echo

# --- Retrofit the allowlisted paths (add/update ONLY; never delete) --------- #
# NO --delete on purpose: a dev file missing from public must never be deleted
# here (it may be a dev addition not yet propagated). Files removed in public are
# reported below for manual handling instead. Governance files (.github/, LICENSE,
# .vscode/, .gitignore, public .claude/settings.json) are out of scope by
# construction — they are never read from the source.
excludes=(--exclude='__pycache__/' --exclude='*.pyc')

echo "=== Updating plugins/ (add/update, minus __pycache__ / *.pyc) ==="
rsync -a "${excludes[@]}" "$src/plugins/" "$here/plugins/"

echo "=== Updating .claude-plugin/ (marketplace.json) ==="
rsync -a "$src/.claude-plugin/" "$here/.claude-plugin/"

echo "=== Updating docs/ ==="
rsync -a "$src/docs/" "$here/docs/"

echo "=== Updating README.md ==="
rsync -a "$src/README.md" "$here/README.md"

# --- Reverse the owner rewrite (Senzing -> docktermj) ---------------------- #
# Narrowly scoped: only this plugin repo's own slug, and the marketplace owner
# name. plugin.json's author "Senzing" (the company), the many product mentions
# of "Senzing" in skill content, and LICENSE text are NEVER touched.
echo
echo "=== Reversing owner self-references (Senzing -> docktermj) ==="
python3 - "$here" <<'PY'
import os, sys
dev = sys.argv[1]
SLUG_OLD = "Senzing/senzing-bootcamp-claude-plugin"
SLUG_NEW = "docktermj/senzing-bootcamp-claude-plugin"

targets = [os.path.join(dev, "README.md")]
for sub in ("plugins", ".claude-plugin", "docs"):
    root = os.path.join(dev, sub)
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith((".md", ".json")):
                targets.append(os.path.join(dp, fn))

changed = 0
for f in targets:
    if not os.path.isfile(f):
        continue
    with open(f, encoding="utf-8") as fh:
        s = fh.read()
    t = s.replace(SLUG_OLD, SLUG_NEW)
    if os.path.basename(f) == "marketplace.json":
        t = t.replace('"name": "Senzing"', '"name": "docktermj"')
    if t != s:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(t)
        changed += 1
        print("  reversed", os.path.relpath(f, dev))
print(f"  ({changed} file(s) rewritten)")
PY

# --- Report tracked dev files that are absent from public (NOT deleted) ----- #
# These are either dev-only additions not yet propagated, or content removed in
# public that you may want to remove here by hand. Nothing is deleted for you.
echo
echo "=== In dev but not in public (NOT deleted — review manually) ==="
missing=0
while IFS= read -r rel; do
  case "$rel" in */__pycache__/*|*.pyc) continue ;; esac
  if [ ! -e "$src/$rel" ]; then
    echo "  $rel"
    missing=$((missing + 1))
  fi
done < <(cd "$here" && git ls-files plugins .claude-plugin docs README.md)
[ "$missing" -eq 0 ] && echo "  (none)"

# --- Report (no commit, no push) ------------------------------------------- #
echo
echo "=== Dev repo status in retrofit paths (review before committing) ==="
git -C "$here" status --short -- plugins .claude-plugin docs README.md
echo
echo "Retrofit applied to the working tree. Nothing committed or pushed — review:"
echo "  git -C \"$here\" diff -- plugins .claude-plugin docs README.md"
echo "then commit manually."
