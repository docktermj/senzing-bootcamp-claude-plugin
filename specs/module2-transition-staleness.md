# Fix stale references in Module 2's SDK-setup skill (Module 3 Truth Set; phantom Module 8)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two stale references in `skills/module-02-sdk-setup/SKILL.md`:

1. **Module 3 still described as Truth-Set-based.** The transition prose (`:756`) reads "The next
   module (Module 3) verifies the full setup end-to-end **using the Senzing TruthSet**:". This
   contradicts INV-082 — System Verification now verifies with **synthetic** records; the Truth
   Set belongs only to the separate Truth Set visualization module. It is the last line the
   bootcamper reads before entering Module 3, so it sets the wrong expectation.
2. **Phantom "Module 8".** `:589` reads "every later capacity or sampling decision (Modules 1, 4,
   6, **and 8**) …". There is no numbered Module 8 — Advanced Topics ship as graduation
   production-hardening follow-ups (INV-013/INV-076), not a numbered module. A coherence gap
   (INV-003).

## Root cause

Both lines predate this session's changes and were missed: the Module 3 line predates the
`module3-synthetic-verification-data` rework; the "Module 8" reference is a leftover from the
retired Modules 8–11 numbering (see `advanced-modules-8-11-scope.md`).

## Proposed change

- `:756` — reword to describe synthetic-record verification, mentioning the Truth Set only as the
  separate (optional) visualization: e.g. "The next module (System verification) verifies the full
  setup end-to-end with synthetic records — and, when the Truth Set visualization is selected,
  visualizes the Senzing Truth Set:". Prefer the module **name** (INV-079).
- `:589` — drop "and 8" → "(Modules 1, 4, and 6)".

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` no longer says Module 3 / System Verification uses the Senzing Truth Set; it describes synthetic-record verification (INV-082), consistent with the Module 3 skills.
- [ ] No reference to a numbered "Module 8" remains in the file.
- [ ] The following 👉 transition question is unchanged and still name-based (INV-079).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — transition prose (`:756`) and capacity-decision prose (`:589`).

## Source

- Audit (deep-dive conformance/coherence review), 2026-07-19 — findings #4 (MEDIUM) and #5 (LOW).
- Priority: Medium.
- Related specs: `module3-synthetic-verification-data.md` (INV-082), `advanced-modules-8-11-scope.md` (Modules 8–11 are not numbered modules).
