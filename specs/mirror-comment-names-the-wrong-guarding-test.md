# The tabApplicable mirror comment names the wrong guarding test

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/scripts/capture_screenshots.py:348-350` carries a ⛔ comment above
`_APPLICABILITY`, the Python mirror of the app's `tabApplicable()`:

> ⛔ MIRRORS `tabApplicable()` IN `senzing_viz_server.py` — the app is the authority, and
> `tests/test_capture_tabs.py` asserts the two agree, because a silent divergence here is
> the whole defect this function exists to fix. If you change one, change both.

`tests/test_capture_tabs.py` does **not** assert the two agree. It asserts the tab *inventory*
matches the contract's table (`:358`) and that the page guards on applicability and presence
(`:393`), and nothing in it compares `_APPLICABILITY`'s predicates to `tabApplicable()`'s.

The assertion the comment promises is real, but it lives in a **different file**:
`tests/test_capture_suppressed_tabs.py:121`, `test_python_rule_matches_the_apps_javascript_rule`,
which parses `tabApplicable()` out of `senzing_viz_server.py` and compares the gated tab set, the
stats field each gates on, and the literal thresholds. It is a strong guard, and it is not where the
comment sends the reader.

## Root cause

A maintainer following the comment opens `test_capture_tabs.py`, finds only inventory assertions,
and reasonably concludes the mirror is unguarded. Two bad outcomes follow from that, and the second
is worse than the first: they either duplicate the guard, or they edit `_APPLICABILITY` believing
nothing checks it — the exact "silent divergence" the comment exists to prevent.

This is the class **INV-184** was written from, one step removed. INV-184's own text records
`generate_discoveries_pdf.py` drifting *"while its own comment claimed a test asserted it"* — a
comment claiming coverage that did not exist. Here the coverage does exist; only the pointer is
wrong. That is a milder failure with the same mechanism: the comment is the reader's index into the
suite, and an index that misdirects is trusted exactly as much as one that lies.

Nothing detects it. `citations.py verify` resolves `INV-NNN` IDs, not test filenames; no guard
asserts that a filename named in shipped source contains the assertion claimed of it, and the
existing test-file-existence check is satisfied because `test_capture_tabs.py` does exist.

## Proposed change

1. **Correct the pointer** at `capture_screenshots.py:349` to name
   `tests/test_capture_suppressed_tabs.py` and its test method, so the reader lands on the assertion
   rather than on a file that merely sounds right. Naming the **method** as well as the file is what
   makes the claim checkable at a glance.
2. **Consider naming both** if `test_capture_tabs.py` is also relevant to the mirror's inventory
   half — but only for what each actually asserts. A pointer listing two files where one is padding
   restores the ambiguity.
3. **Add a guard for the class**: assert that where shipped source claims "`tests/<name>.py` asserts
   X", that file exists **and** the claim is plausible — at minimum that the named test file
   references the symbol the comment is about (`_APPLICABILITY`, `tabApplicable`). Derive the pairs
   by scanning shipped source for `tests/test_*.py` references (INV-246), never from a list.

## Acceptance criteria

- [ ] `capture_screenshots.py`'s mirror comment names the file **and** the test method that actually
      asserts the two rules agree.
- [ ] Every `tests/test_*.py` filename referenced from shipped source under `plugins/` names a file
      that exists **and** that references the symbol the referring comment concerns.
- [ ] The guard derives its (source file → named test) pairs by scanning, not from a hardcoded list
      (INV-246) — **negative-controlled**: repoint the comment at an unrelated test file, confirm the
      guard fails, then revert.
- [ ] The guard carries a docstring stating what it cannot check — that a named test *references* a
      symbol is not proof it *asserts* the claimed property, so this catches a misdirected pointer
      and not a weak assertion.
- [ ] `tests/test_capture_suppressed_tabs.py` is unchanged — the assertion is correct where it is.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — `:349`, the pointer.
- `tests/test_comment_test_pointers_resolve.py` — new.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15 (second run of the day)
  (`Source: self-observed (assistant retrospective)`). Found while verifying that an explicitly
  declared mirror between two shipped scripts was in sync — it is; only its pointer is wrong.
- Priority: **Low**. The mirror is correct, the guard exists and is strong, and the two rules agree
  today (verified 2026-08-15: gated set, stats fields and thresholds all match). Nothing a Bootcamper
  can hit; the exposure is a maintainer misled into thinking the mirror is unguarded.
- MCP re-check: **n/a (no Senzing fact).** Internal consistency between the plugin's own scripts and
  its own test suite; no MCP tool was called and no Senzing claim is asserted. Server **1.32.9**
  recorded this session (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `deep-dive-audit-2026-07-30` (INV-184, established after a comment claimed a test
  asserted something it did not), `guards-enforce-class-scoped-rules-from-hardcoded-site-sets` (the
  sibling INV-246 finding from the same run), and INV-184, INV-246, INV-155, INV-232.

## Deviations from this spec, and why (2026-08-15)

- **The corrected comment names the method AND says what the other file actually guards.** Naming
  only the right file would have left the next reader to rediscover that `test_capture_tabs.py` is
  about tab *inventory*; the comment now says so in one clause, so the wrong pointer cannot be
  re-derived from the same confusion.
- **The guard covers two claims, not one.** Beyond the symbol-plausibility check this spec asks for,
  it also asserts that **every** `tests/test_*.py` name referenced anywhere in shipped source exists
  — the cheaper half, which catches the pure INV-184 shape (a comment naming a guard that was never
  written) across the whole corpus rather than only at mirror comments.
- ⛔ **Its stated limit is real and load-bearing:** it checks that a named test *mentions* the symbol,
  never that it *asserts* the property. A weak or vacuous assertion in a correctly-named file passes.
  That is disclosed in a ⛔ block in the docstring rather than left for a reader to discover, per
  `coverage-reports-count-known-non-defects-as-hits`.
- **No Senzing fact required re-verification.** `get_capabilities` was called this session to date
  the run (server **1.32.9**, 2026-08-15), confirming this spec's `MCP re-check: n/a`. The claim that
  the two rules agree today was re-checked by reading both: gated set, stats fields and thresholds
  all match.
