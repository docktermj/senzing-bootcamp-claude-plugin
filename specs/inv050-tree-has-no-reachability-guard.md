# INV-050's layout tree has no guard, so a future unannotated entry would go unnoticed

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

INV-050 states *"The generated Bootcamp project MUST follow this layout"* followed by a
`text` tree (`specs/INVARIANTS.md:156-212`). The tree is **currently correct** — verified
below — and **nothing checks that it stays correct.**

⚠️ **Read this before the rest: the tree is not stale.** A previous spec,
`specs/inv050-layout-tree-names-three-artifacts-nothing-produces.md`, claimed three entries
were unproduced and unannotated. That claim is **false**, and this spec does not inherit it.
All three carry `(reserved)`:

```text
specs/INVARIANTS.md:166   │   ├── session_log.jsonl              # Session activity log (reserved)
specs/INVARIANTS.md:167   │   └── visualization_tracker.json     # Visualization run tracking (reserved)
specs/INVARIANTS.md:197   │   ├── completion_summary.md          # (reserved)
```

They were annotated deliberately on **2026-07-17** via `specs/layout-tree-reconciliation.md`
(commit `cc46a55`), whose ledger entry says so in as many words: *"annotated the
reserved/unused entries (`config/session_log.jsonl`, `config/visualization_tracker.json`,
`data/backups/`, `docs/completion_summary.md`, `src/server/`, `monitoring/`, `tests/`)"*.

**The real defect is the missing guard.** Verified 2026-08-11 against the whole tree, with
each entry accepted as accounted for if it is either referenced under `plugins/` **or**
annotated `reserved|superseded|legacy|future`:

| Entry kind | Entries | Unaccounted |
|---|---|---|
| files | 24 | **0** |
| directories (excluding the root) | 30 | **0** |

So there is no current defect to repair — and no test would notice if there were. Nothing in
`tests/` parses the tree: `tests/test_bundled_script_and_production_paths.py:14` is the only
test that mentions INV-050 at all, and only in a docstring noting the layout has no
top-level `scripts/`. Grepping `tests/` for the three reserved filenames returns nothing.

**Why it is worth building anyway.** The tree is a fenced block inside a foundational
invariant, widely cited and quoted in audits, and it reads authoritative whether or not it
is true. This is the stale-enumeration class the audit skill ranks fourth: *"one listing
members breaks the moment a member moves, and it breaks silently because the list still
reads authoritative."* A guard fails on a **future** entry added without an annotation, and
on an existing entry that quietly loses its producer — neither of which anything catches
today. It would also have caught the false claim above in seconds.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

Two separate gaps, and only the second is a defect.

1. **Why the tree is fine.** `layout-tree-reconciliation` (2026-07-17) established the
   annotation convention and applied it. The convention works; it is just unenforced.
2. **Why nothing guards it.** The tree has never been machine-readable to any test. It is
   prose inside an invariant, and every check that touches project layout
   (`test_bundled_script_and_production_paths.py`) works from paths it names itself rather
   than from the tree.

**Why the previous spec got it backwards, which the guard must not repeat.** Its extraction
ran `body = line.split("#")[0]` before matching — discarding the comment column, which is
the only place the annotation lives. It then asked "is this filename mentioned anywhere
else in the repo?", got no, and concluded the tree was stale. The evidence that refutes the
finding sat in the part the scan deleted. **The comment column is load-bearing data, not
decoration**, and any guard that drops it reproduces the same error.

## Proposed change

Add one test that walks the INV-050 tree and asserts every leaf entry is **either**
referenced under `plugins/` **or** annotated in its own comment as
`reserved | superseded | legacy | future`.

**Three parsing hazards, all live in the current tree.** Each was hit while verifying the
table above; a guard that ignores them either crashes or passes vacuously:

1. **The comment column must be kept.** See the root cause. Split the line into
   `left, comment` and match the name in `left` — never discard `comment`.
2. **Continuation lines carry no entry.** `backups/` has a two-line comment
   (`specs/INVARIANTS.md:210-211`); the second line is box-drawing plus comment text with no
   filename. It must be skipped, not counted as an entry or treated as unaccounted.
3. **Placeholder names are not literal.** `docs/stakeholder_summary_module{n}.md` never
   appears verbatim under `plugins/` — the real files are `stakeholder_summary_module1.md`
   and `stakeholder_summary_module6.md`. Probing on the literal string reports it
   unaccounted (confirmed 2026-08-11); probe on the prefix before `{`.

**Do not pin the entry count by copying a number out of a spec.** The previous spec says
"53 entries" and "23 files"; this one measured 56 tree lines, 24 files and 30 directories.
Both are defensible — they differ on whether the root, the continuation line and the
placeholder entry count — which is exactly why the number must come from running *your*
extractor and be pinned with a comment saying what it counts.

Scope it to **files and directories both**: all 30 directory entries already satisfy the
rule (verified above), so covering them costs nothing and closes the same gap for entries
like `monitoring/` and `tests/`, which are `(reserved)` today and would silently become
wrong if someone dropped the annotation.

## Acceptance criteria

- [ ] A test in `tests/` extracts the INV-050 tree's leaf entries **with their comment
      column intact** and asserts each is either referenced under `plugins/` or annotated
      `reserved|superseded|legacy|future`. It passes against the tree as it stands today.
- [ ] The three parsing hazards are handled and each is pinned by its own assertion, so a
      later simplification cannot silently reintroduce one: the comment column is kept
      (an entry annotated but unreferenced **passes**), the `backups/` continuation line is
      not counted as an entry, and `stakeholder_summary_module{n}.md` resolves via its
      prefix rather than being reported unaccounted.
- [ ] **Not vacuous:** the test asserts the extracted entry count against a pinned literal,
      derived by running the extractor at implementation time — not copied from this spec or
      from `inv050-layout-tree-names-three-artifacts-nothing-produces`, which disagree. A
      comment records what the number counts (root? continuation lines? placeholders?).
- [ ] **Negative-controlled, with the mutation verified to land:** adding a fictional
      unannotated entry to the tree fails the test; adding the same entry *with* a
      `(reserved)` annotation passes. Revert both.
- [ ] The test does **not** assert that `session_log.jsonl`,
      `visualization_tracker.json` or `completion_summary.md` are a defect — they are
      correctly annotated, and a test encoding the opposite would re-enshrine the false
      claim this spec supersedes.
- [ ] INV-050 is **not** shortened, renumbered, annotated or otherwise edited: this spec
      adds a guard only, and the tree is already correct.
- [ ] Stdlib-only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      the extraction is pure text over `specs/INVARIANTS.md` and must not shell out to
      `grep` or depend on path separators.

## Affected files

- `tests/` — the new tree-walk guard (one new file; nothing existing needs to change).
- `specs/INVARIANTS.md` — **read only.** Listed because the guard parses it; it is not edited.

## Source

- Audit: `production-readiness-audit`, 2026-08-11 (`Source: self-observed (assistant
  retrospective)`) — the run that produced the superseded spec. The surviving idea is its
  acceptance criteria; its Problem and Root cause are void.
- Re-verified 2026-08-11 in a later `implement-spec` session: the `(reserved)` annotations
  at `specs/INVARIANTS.md:166,167,197`, commit `cc46a55`, the zero-unaccounted table above,
  and the three parsing hazards were each established by running the corrected check, not
  by reading the previous spec.
- Priority: **Medium-low.** No live defect and nothing a Bootcamper sees; the value is that
  a foundational enumeration currently has no way to fail.
- MCP re-check: **n/a — no Senzing fact.** No tool was called for this finding. (`get_capabilities`
  was called in the same session for unrelated specs and reported server **1.32.9**.)
- Upstream: not applicable.
- Related specs: **supersedes the surviving idea of**
  `specs/inv050-layout-tree-names-three-artifacts-nothing-produces.md` (whose Problem and
  Root cause are false — see above); `specs/layout-tree-reconciliation.md` (established the
  annotation convention, 2026-07-17, commit `cc46a55`).

## Invariants introduced

- `INV-202` — Every leaf entry in INV-050's project-layout tree MUST be either referenced
  under `plugins/` or annotated in its own comment as reserved/superseded/legacy/future;
  an unproduced entry gains the annotation rather than being deleted, and the comment
  column is load-bearing data (recorded in `specs/INVARIANTS.md`).
