# Reconcile "Action Taken" (INV-048) with the implemented "Actions Taken"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-048 names one of the four required recap sections **"Action Taken"**
(singular). Every implementation surface uses **"Actions Taken"** (plural). The
spec and the code therefore disagree on a pinned section name — a small but real
INV-003 consistency gap in the crown-jewel trophy (INV-048).

## Root cause (confirmed)

- Invariant text: `specs/INVARIANTS.md:145` — "Action Taken" (singular).
- Implementation uses the plural everywhere:
  `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:53` (the
  `REQUIRED_SECTIONS` constant), the shipped example
  `docs/examples/bootcamp_recap.example.md` (all module headings),
  `skills/bootcamp-onboarding/module-completion.md:66,81`,
  `skills/graduation/SKILL.md:76,101,164,236,240`,
  `skills/bootcamp-onboarding/ground-rules.md:132`, and
  `skills/module-03-system-verification/phase3-report-close.md:177`.
- It is not currently a functional failure: `generate_recap_pdf.py:109-120`
  (`_normalize_heading`) maps `action taken` → `actions taken`, so the parser and
  `--check` accept either. The defect is purely spec-vs-implementation wording.

## Proposed change

Reconcile to the plural, which is the de-facto standard across the codebase:

- Edit `specs/INVARIANTS.md:145` to say **"Actions Taken"**. Per the file's own
  maintenance rules this is an allowed in-place wording clarification (it does not
  change the invariant's meaning — the same section, renamed for accuracy), so it
  does **not** require a new INV-NNN.
- Leave the implementation as-is (already plural), and keep the
  `_normalize_heading` singular→plural mapping so any legacy singular input still
  parses.

## Acceptance criteria

- [ ] `specs/INVARIANTS.md` INV-048 lists the four sections as "Information Shared", "Questions & Responses", "Actions Taken", and "Journal" — matching the implementation exactly.
- [ ] No implementation change is needed; `generate_recap_pdf.py --check` still passes on the shipped example, and the singular→plural normalization remains.
- [ ] A repo-wide grep shows the recap section name is identical ("Actions Taken") across the invariant, the generator, the skills, and the shipped example.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-048: "Action Taken" → "Actions Taken" (in-place wording clarification, no new invariant).

## Source

- Invariant audit, 2026-07-17 (deep-dive over the plugin), INV-048 wording-drift finding.
- Priority: Low.
- Related specs: `recap-pdf-professional-design.md`, `example-recap-reference.md` (both use the plural). Bears on INV-048, INV-003.
