# An invariant names its enforcing test, and nothing checks the test names it back

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

**22 invariants name a specific test as their enforcer** — *"`tests/test_brand_sync.py` enforces
this and MUST pass"*. Measured 2026-08-12: **11 of the 22 are not cited back by the test they
name.** Exactly half.

| Invariant | Names as enforcer | Visible on the coverage report? |
|---|---|---|
| INV-114 | `test_model_guidance_sync.py` | **masked** by `test_interface_naming.py`, `test_invariants_index.py` |
| INV-121 | `test_discoveries_pdf.py` | **masked** by 3 recap-PDF tests |
| INV-140 | `test_model_guidance_sync.py` | visible as uncited |
| INV-159 | `test_recap_pdf_font_safety.py` | **masked** by 2 files |
| INV-167 | `test_windows_powershell_guidance.py` | **masked** by `test_bundled_script_and_production_paths.py` |
| INV-183 | `test_generated_html_deliverables.py` | **masked** by 5 files |
| INV-185 | `test_bundled_script_and_production_paths.py` | **masked** by 2 files |
| INV-188 | `test_tab_set_is_singular.py` | visible as uncited |
| INV-191 | `test_partial_row_and_schema_coverage.py` | visible as uncited |
| INV-203 | `test_cord_fetch_integrity.py` | visible as uncited |
| INV-204 | `test_liveness_probe_is_not_a_document_search.py` | visible as uncited |

**The guarantees are real; only the citation is missing.** Four were read to confirm this
(`test_liveness_probe_is_not_a_document_search.py`, `test_cord_fetch_integrity.py`,
`test_tab_set_is_singular.py`, `test_partial_row_and_schema_coverage.py`) — each enforces its
invariant's subject. **No phantom tests**: every test file named by an invariant exists.

**Why it matters is the report, not the docstring.**
`.claude/skills/dry-run/coverage_reports.py invariants` is the repo's only signal for *"this rule
has no guard"*, and it keys on the ID appearing **anywhere** under `tests/`. So a missing
back-citation is scored one of two wrong ways:

- **False alarm** (5 above) — the invariant reads as unguarded when a dedicated test enforces it,
  sending a future audit to build a guard that already exists.
- **False all-clear** (6 above) — an unrelated file mentions the ID in passing, so the invariant
  reads as covered and the missing citation becomes undiscoverable. INV-183's five "citations"
  are all *rationale* references (*"a rule deliberately restated at the step it governs is
  INV-183"*), none in the test INV-183 names.

**This already cost a run.** `production-readiness-audit-2026-08-11` finding (3) recorded exactly
three of these — INV-183, INV-188, INV-191 — and said *"the fix is three docstring lines"*. It was
recorded in the ledger and **never actioned**: all three are still missing on 2026-08-12, and
INV-183 has since been masked, so the report that would have caught it went quiet.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

Three compounding, none of them careless:

1. **Nothing asserts the link.** `INVARIANTS.md` rule 3 binds a new invariant to an index entry
   (`test_invariants_index.py` fails otherwise). No equivalent binds an invariant to the test it
   names, so the citation is a convention with no enforcement.
2. **The report cannot distinguish enforcement from mention.** `coverage_reports.py` documents its
   proxy honestly — *"an ID mentioned only in a test's comment or docstring counts as cited here,
   so this UNDER-reports"* — but the observed failure is the **opposite**: an incidental mention
   producing a false *positive*. The docstring warns about the direction that does not bite.
3. **The 2026-08-11 fix was a three-line chore with no ticket.** Recorded in a ledger summary
   rather than as a spec, so nothing re-offered it and nothing failed while it went undone.

## Proposed change

1. **Add the missing back-citations** to the 11 tests, in the docstring, naming the invariant each
   discharges. Docstrings only — **no assertion changes**.

2. **Add `tests/test_invariant_enforcer_citations.py`**: for every invariant naming
   `tests/test_*.py`, assert the file exists **and** cites the invariant ID. This is the rule-3
   discipline applied to the enforcement link, and it makes the class self-policing.

3. **Record the false-positive mode in `coverage_reports.py`'s docstring.** Its stated weakness is
   under-reporting; the observed one is over-reporting. State both, and point at the new test as
   the reliable signal for the named-enforcer subset.

⛔ **Do not "fix" a masked invariant by deleting the unrelated mention.** Those references are
legitimate — INV-183 as rationale is exactly the reasoning the repo wants recorded. The fix is the
missing citation, never the removal of a correct one.

## Acceptance criteria

- [ ] Each of the 11 invariants above is cited in the test file it names, in that file's docstring,
      saying which invariant the file discharges. Verified by opening each of the 11 files (INV-182:
      a criterion naming a file is checked against that file).
- [ ] **No assertion is changed** in any of the 11 files. Verified by `git diff` touching only
      docstring/comment lines.
- [ ] `tests/test_invariant_enforcer_citations.py` exists and asserts, for every invariant naming a
      `tests/test_*.py` file, that the file exists and cites the ID. It passes on the corrected tree.
- [ ] **Not vacuous:** the test asserts the number of invariant→test pairs it found against a pinned
      literal derived by running the extractor at implementation time (22 on 2026-08-12), with a
      comment recording what the number counts.
- [ ] **Negative-controlled, mutation verified to land:** removing one back-citation fails the new
      test; renaming an invariant's named test to a non-existent file fails it with a distinct
      message. Revert both.
- [ ] `coverage_reports.py`'s docstring states the over-reporting mode with a worked example, and
      names the new test as the reliable check for named-enforcer invariants.
- [ ] Record the uncited count before and after (**79 before**); it should fall by the 5 that were
      visible, and the 6 masked ones will not move — state that explicitly so the number is not read
      as the whole fix.
- [ ] `citations.py verify` clean; full suite passes (baseline **1743 passed, 3 skipped, 1342
      subtests**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); cross-platform and language-agnostic.

## Affected files

- `tests/` — the 11 named test files (docstrings only).
- `tests/test_invariant_enforcer_citations.py` — new.
- `.claude/skills/dry-run/coverage_reports.py` — docstring only.

## Source

- Audit: `production-readiness-audit`, 2026-08-12 (`Source: self-observed (assistant
  retrospective)`). Found by sweeping every invariant that names a `tests/test_*.py` file and
  checking the back-citation, after `coverage_reports.py invariants` was observed masking INV-184
  earlier the same day.
- Prior art this supersedes in scope: `production-readiness-audit-2026-08-11` finding (3), which
  recorded three of the eleven and was never actioned.
- Priority: **Medium.** No shipped behaviour is wrong and no guarantee is unenforced. The value is
  that the repo's only unguarded-rule signal is currently unreliable in both directions.
- MCP re-check: **n/a — no Senzing fact.** `get_capabilities` reported server **1.32.9** this
  session for unrelated work; no tool was called for this finding.

## Invariants introduced

**None proposed.** INV-182 already governs verifying a criterion against the file it names, and
`INVARIANTS.md` rule 3 already governs the index link; this is the same discipline applied to the
enforcement link, and a test is the right enforcement, not a new rule.
