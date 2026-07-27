# PR #4 review: batched minor fixes (context manager, logging, sync-guard, screenshot robustness, field-name drift, DRY)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

The PR #4 code review surfaced a cluster of small, low-severity items, none blocking but each
a cheap correctness/robustness/clarity improvement:

1. **File handle not closed** — `senzing_viz_server.py:1142`:
   `settings = open(args.settings, encoding="utf-8").read()` opens without a context manager,
   inconsistent with the `with open(...)` used elsewhere in the file.
2. **Silent `except Exception` with no trace** — `senzing_viz_server.py` `build_model` and the
   snapshot-probe search path swallow exceptions (justified by INV-077: a why/search failure
   must never block the model/snapshot) but leave no diagnostic breadcrumb, making an empty
   "Feature Scores"/probe tab hard to debug. Add a `sys.stderr.write(...)` note on catch while
   still not raising.
3. **Manual brand-token sync is unguarded** — `generate_recap_pdf.py` and `senzing_viz_server.py`
   each keep a fallback copy of the `brand_tokens.py` palette "kept in sync by comment," with
   no check that the fallbacks match the source. A future edit to one copy can silently
   diverge. Add a lightweight guard (a check that the fallback constants equal `brand_tokens`
   when it imports; wire it into `scripts/sync-check.sh` or the `write-gate-tests` harness).
4. **Screenshot capture robustness** — `capture_screenshots.py:85-86` uses
   `wait_until="networkidle"` on a `file://` URL (can hang/behave inconsistently for local
   files with no network events) and sets no `device_scale_factor`. Prefer `load`/
   `domcontentloaded` (or a bounded timeout) for local files; optionally set a device scale
   factor for crisper captures. Best-effort and try/except-wrapped, so this is robustness, not
   a bug fix.
5. **Checkpoint field-name drift** — `module-03-system-verification/phase1-verification.md:139`
   records `expected_merge_record_count` while the results-validation checkpoints
   (`phase1-verification.md:354`, `phase2-report-close.md:63`) use `matches_verified`. Confirm
   whether these are the same concept named two ways (reconcile to one name) or legitimately
   distinct (expected vs. verified) — if distinct, leave a one-line note so the difference is
   intentional, not accidental drift.
6. **DRY / readability nit** — `write-gate.py:95-101` inlines the temp-path prefixes as a chain
   of `startswith` calls; a tuple + `any(low.startswith(p) for p in TEMP_PREFIXES)` reads
   cleaner. (Coordinate with `specs/harden-write-gate.md`, which also edits this region.)

Optional, no change unless desired: record the vendored d3 version/SHA in a comment or note.
The version is already in the file header (`v7.9.0`); a SHA pin would only add upgrade-diff
assurance.

## Root cause

Each item cites its `file:line` above; all are localized, low-risk edits. None changes
bootcamper-facing behavior.

## Proposed change

Apply items 1–3 and 6 as direct edits; treat 4 as a robustness improvement; investigate 5 and
either reconcile or annotate. Keep every change consistent with the offline/error-handling
invariants (INV-077/INV-091) — logging additions go to `stderr` and never raise.

## Acceptance criteria

- [ ] `senzing_viz_server.py:1142` reads the settings file via `with open(...)`.
- [ ] `build_model` / snapshot-probe swallow-paths write a `stderr` diagnostic on catch and
      still never raise (INV-077 preserved).
- [ ] A guard fails loudly if any in-file brand-token fallback diverges from `brand_tokens.py`.
- [ ] `capture_screenshots.py` no longer waits on `networkidle` for `file://` targets (uses a
      local-file-appropriate wait/timeout); captures still succeed.
- [ ] The Module 3 checkpoint field names are either reconciled to one name or annotated as
      intentionally distinct.
- [ ] `write-gate.py`'s temp-prefix check is expressed as a single iterated collection.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — items 1, 2.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`, `senzing_viz_server.py`,
  `brand_tokens.py` — item 3 (sync guard).
- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — item 4.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`
  (and `phase2-report-close.md`) — item 5.
- `plugins/senzing-bootcamp/scripts/write-gate.py` — item 6 (with `harden-write-gate`).

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #4 (comment 5073711304),
  Parts 1, 2 & 5 — assorted minor findings.
- Priority: Low.
- Related specs: `specs/harden-write-gate.md`, `specs/write-gate-tests.md`,
  `specs/audit3-minor-fixes.md`, `specs/audit-polish-cleanup.md`.

## Invariants introduced

- `INV-107` — The inlined brand-palette fallbacks in `senzing_viz_server.py` and
  `generate_recap_pdf.py` MUST equal `brand_tokens.py`, enforced by
  `tests/test_brand_sync.py` (recorded in `specs/INVARIANTS.md`).
