# Dry-run scaffold uses a verification filename the plugin never writes

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The dry-run skill's scaffold builds a mid-bootcamp fixture at
`src/system_verification/records.jsonl`. System verification writes its synthetic
records to `src/system_verification/verification_data.jsonl`. The names do not
match, so the fixture exercises a path the plugin never touches, and a mid-bootcamp
dry run starts **without** the file the plugin actually expects to find.

The scaffold's own `--explain` output says "Every fixture is here because a naive
one hid a defect". This one cannot catch the defect it is named for.

## Root cause

- `.claude/skills/dry-run/scaffold_project.py:270` creates
  `src/system_verification/records.jsonl`.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md:171-172`
  — "Write at least 4 records to `src/system_verification/verification_data.jsonl`
  (one JSON object per line, overwrite any existing file)".

`verification_data.jsonl` is the only spelling the plugin uses; a grep for
`records.jsonl` under `plugins/` returns nothing for this path. Confirmed by
executing the module on this walk: Step 2 wrote `verification_data.jsonl`, and
`records.jsonl` was never read or written by anything.

Nothing catches the drift, because the scaffold is a maintainer tool and the
repo-level tests cover `plugins/` rather than `.claude/`.

## Proposed change

1. Rename the fixture in `scaffold_project.py` to
   `src/system_verification/verification_data.jsonl`, and make its contents match
   the shape Step 2 specifies — at least four records, `DATA_SOURCE` of `VERIFY`,
   unique `RECORD_ID`s, Entity Specification attribute names, a merge cluster plus
   a distractor.
2. Add a repo-level test that fails when a path named in `scaffold_project.py`'s
   fixture table does not appear in any file under `plugins/`. That is the general
   form of this defect — the scaffold asserting a filename the plugin does not use —
   and it is cheap to guard. Stdlib only, no `plugins/` import (INV-108).
3. While there: check the other fixture paths in the same table against `plugins/`,
   since nothing has been verifying any of them.

## Acceptance criteria

- [ ] `scaffold_project.py` creates `src/system_verification/verification_data.jsonl`,
      not `records.jsonl`.
- [ ] The fixture's contents satisfy Step 2's stated shape, so a mid-bootcamp run
      resumes against data the module recognizes.
- [ ] A repo-level test fails if any fixture path in `scaffold_project.py` is absent
      from every file under `plugins/`, and is negative-controlled by restoring the
      `records.jsonl` spelling.
- [ ] Every other fixture path in the scaffold's table is confirmed present in
      `plugins/`, or corrected.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/scaffold_project.py` — the fixture path and its contents.
- `tests/test_dry_run_scaffold_paths_exist.py` — new guard.

## Source

- Feedback: dry run phase 3, 2026-08-13 — noticed while executing System
  verification Step 2, which wrote a different filename than the scaffold's
  `--explain` listing had named (`Source: self-observed (assistant retrospective)`)
- Priority: Low — it degrades a maintainer tool rather than the bootcamper
  experience, but it silently weakens the mid-bootcamp fixture that exists to catch
  resume defects.
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none
