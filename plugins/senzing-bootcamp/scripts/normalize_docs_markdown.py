#!/usr/bin/env python3
"""Normalize the bootcamp's Markdown docs — cosmetically, and provably losslessly.

During the bootcamp the guide writes `docs/*.md` plain (see `ground-rules.md` →
"Markdown files"); graduation prettifies them once, immediately before the recap PDF
renders. That ordering is what makes the guard below load-bearing: a cosmetic pass that
dropped prose would produce a valid, prettier, **shorter** recap, and the PDF would ship
it. Nothing else in the pipeline would notice — the generator's content-retention figure
(INV-110) is computed against the *normalized* file, so it would report success against
the already-damaged input.

Two safety properties, both enforced in code rather than promised in prose:

1. **Content preservation.** Each file's non-whitespace content is fingerprinted line by
   line before and after. If the normalized text does not carry every source line's
   content forward, the original is restored and the file is reported on stderr. The only
   permitted change to a line's content is an opening code fence gaining an info string
   (MD040) — everything else must match exactly.

2. **Scope.** Only top-level `docs/*.md` is globbed, never recursively, so
   `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` cannot be touched (INV-015). The
   feedback file is the bootcamper's own record and must survive graduation intact.

House rules applied (outside fenced code blocks only):

* **MD022** — blank line above and below every ATX heading.
* **MD031** — blank line above an opening fence and below a closing fence.
* **MD032** — blank line above the first item of a list and below the last.
* **MD040** — an info string on every opening fence (defaults to ``text``).
* ``**Label:**`` colon spacing — no space before the colon, one after.

Usage::

    python3 normalize_docs_markdown.py [--docs-dir docs] [--dry-run]

Exit codes: 0 = finished (including "nothing to change", and including files skipped by
the content guard, which warn but never fail the run — a formatting issue must never
block graduation, INV-048); 1 = the docs directory does not exist.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# A fence opener/closer: ``` or ~~~ with an optional info string.
_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*(\S.*)?$")
_ATX_HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
_TABLE_ROW = re.compile(r"^\s*\|")

DEFAULT_FENCE_LANG = "text"


def _signature(text: str) -> list:
    """Each non-blank line's content with all whitespace removed, in order.

    Whitespace-insensitive because every rule here either inserts blank lines or adjusts
    spacing; content-sensitive because that is precisely what must not change.
    """
    return [re.sub(r"\s+", "", line) for line in text.splitlines() if line.strip()]


def _signatures_compatible(before: list, after: list) -> bool:
    """True when `after` carries every line's content from `before`.

    The single permitted difference is a bare opening fence gaining an info string
    (MD040): ``` -> ```text. Anything else — a dropped line, reordering, rewritten
    prose — is a content change and fails.
    """
    if len(before) != len(after):
        return False
    for old, new in zip(before, after):
        if old == new:
            continue
        if re.fullmatch(r"(`{3,}|~{3,})", old) and new.startswith(old[:3]):
            continue  # fence gained a language
        return False
    return True


def _fix_label_spacing(line: str) -> str:
    """`**Label :**value` -> `**Label:** value`. Bold-label lines only."""
    line = re.sub(r"\*\*([^*\n]+?)\s+:\*\*", r"**\1:**", line)
    return re.sub(r"(\*\*[^*\n]+?:\*\*)(?=\S)", r"\1 ", line)


def normalize_text(text: str) -> str:
    """Apply the house rules to one document's text."""
    lines = text.splitlines()
    out: list = []
    in_fence = False
    fence_marker = ""

    def last_is_blank() -> bool:
        return not out or not out[-1].strip()

    def blank_before() -> None:
        """Ensure a blank line separates the previous block, never at file start."""
        if out and not last_is_blank():
            out.append("")

    def leaving_block() -> bool:
        """True when the previous emitted line was a list item, its continuation, or a
        table row — i.e. the line about to be emitted closes that block (MD032)."""
        if not out or not out[-1].strip():
            return False
        prev = out[-1]
        return bool(
            _LIST_ITEM.match(prev)
            or _TABLE_ROW.match(prev)
            or prev.startswith((" ", "\t"))  # an item's wrapped continuation
        )

    for index, raw in enumerate(lines):
        fence = _FENCE.match(raw)

        if in_fence:
            out.append(raw)
            if fence and fence.group(2).startswith(fence_marker[:1]) and len(
                fence.group(2)
            ) >= len(fence_marker) and not fence.group(3):
                in_fence = False
                fence_marker = ""
                # MD031: blank line after the closing fence, when more content follows.
                if index + 1 < len(lines) and lines[index + 1].strip():
                    out.append("")
            continue

        if fence:
            # Opening fence: MD031 blank line above, MD040 info string.
            blank_before()
            indent, marker, info = fence.group(1), fence.group(2), fence.group(3)
            out.append(f"{indent}{marker}{info if info else DEFAULT_FENCE_LANG}")
            in_fence = True
            fence_marker = marker
            continue

        if _ATX_HEADING.match(raw):
            blank_before()
            out.append(raw.rstrip())
            # MD022: blank line below, when more content follows.
            if index + 1 < len(lines) and lines[index + 1].strip():
                out.append("")
            continue

        if _LIST_ITEM.match(raw):
            # MD032: blank line above the FIRST item only — a blank line between every
            # item would turn one list into several, changing the document's structure.
            prev = out[-1] if out else ""
            prev_is_list = bool(_LIST_ITEM.match(prev)) or (
                prev.strip() and prev.startswith((" ", "\t"))
            )
            if not prev_is_list:
                blank_before()
            out.append(_fix_label_spacing(raw.rstrip()))
            continue

        if _TABLE_ROW.match(raw):
            prev = out[-1] if out else ""
            if not _TABLE_ROW.match(prev):
                blank_before()
            out.append(raw.rstrip())
            continue

        if raw.strip():
            # MD032: a blank line closes a list/table before ordinary prose resumes.
            # An indented line is a continuation of the preceding item, not a new block.
            if not raw.startswith((" ", "\t")) and leaving_block():
                out.append("")
            out.append(_fix_label_spacing(raw.rstrip()))
        else:
            out.append("")

    # Collapse runs of blank lines to one, and end with exactly one newline.
    collapsed: list = []
    for line in out:
        if not line.strip() and collapsed and not collapsed[-1].strip():
            continue
        collapsed.append(line)
    while collapsed and not collapsed[-1].strip():
        collapsed.pop()
    return "\n".join(collapsed) + "\n" if collapsed else ""


def target_files(docs_dir: Path) -> list:
    """Top-level ``docs/*.md`` only — never recursive (INV-015).

    ``Path.glob("*.md")`` does not descend, so ``docs/feedback/`` is structurally out of
    reach. The explicit parent check is belt-and-braces against a future edit to this
    pattern.
    """
    return sorted(
        p for p in docs_dir.glob("*.md") if p.is_file() and p.parent == docs_dir
    )


def normalize_file(path: Path, dry_run: bool = False) -> str:
    """Normalize one file. Returns "changed", "unchanged", "skipped" or "error"."""
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(f"{path}: could not read ({exc}); left untouched.\n")
        return "error"

    normalized = normalize_text(original)
    if normalized == original:
        return "unchanged"

    if not _signatures_compatible(_signature(original), _signature(normalized)):
        # The guard that makes this pass safe to run immediately before the render.
        sys.stderr.write(
            f"{path}: normalization would change content, not just formatting; "
            "keeping the original. This is a bug in the normalizer, not in the "
            "document — report it rather than hand-formatting the file.\n"
        )
        return "skipped"

    if dry_run:
        return "changed"
    try:
        path.write_text(normalized, encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"{path}: could not write ({exc}); left untouched.\n")
        return "error"
    return "changed"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--docs-dir",
        default="docs",
        help="Directory holding the Markdown docs (default: docs). Never recursed.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing.",
    )
    args = ap.parse_args(argv)

    docs_dir = Path(args.docs_dir)
    if not docs_dir.is_dir():
        sys.stderr.write(f"{docs_dir}: no such directory; nothing to normalize.\n")
        return 1

    counts = {"changed": 0, "unchanged": 0, "skipped": 0, "error": 0}
    changed_names = []
    for path in target_files(docs_dir):
        result = normalize_file(path, dry_run=args.dry_run)
        counts[result] += 1
        if result == "changed":
            changed_names.append(path.name)

    verb = "would normalize" if args.dry_run else "normalized"
    print(
        f"{verb} {counts['changed']} of {sum(counts.values())} file(s) in {docs_dir}"
        + (f": {', '.join(changed_names)}" if changed_names else "")
    )
    if counts["skipped"]:
        print(
            f"{counts['skipped']} file(s) left as written by the content guard.",
            file=sys.stderr,
        )
    # Always 0: a formatting pass must never block graduation (INV-048).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
