# Skip the "involve business users" UAT question for bootcamp-generated scenarios

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 6 (Data Processing), Phase D, Step 25 asks a pinned yes/no question:

> 👉 **Would you like to involve business users in testing the cross-source results?**

For a bootcamp-generated scenario there are no real stakeholders (this session's "Harborview
Financial" case was generated in Module 1, not a real organization), so the answer is always "no".
Asking a question whose answer is already determined by known context wastes a turn and interrupts
flow.

## Root cause

`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:79-91` (Step 25)
presents the question whenever 2+ sources loaded, **without** checking whether the business problem
is real or bootcamp-generated. The generated-scenario marker is written to
`docs/business_problem.md` on Business Case Offer acceptance:
`plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:81-82` inserts
`> 🤖 Bootcamp-generated business case` directly below the title (and
`phase1-discovery.md:74` routes the accepted offer to that write).

## Proposed change

Before Step 25, detect the generated marker (or the absence of any real stakeholders on record):

- **Generated / no real stakeholders** (marker present in `docs/business_problem.md`): **skip** the
  Step 25 question and take the self-directed spot-check path directly — spot-check 5–10 cross-source
  entities, document findings in `docs/uat_results.md` — stating briefly why the question was skipped
  (INV-012), adding no turn.
- **Real business problem** (no marker): ask Step 25 exactly as today, pinned verbatim (INV-056).

This mirrors the flow's existing context-conditional skipping (Steps 23–27 already run only for 2+
sources) and honors INV-006/INV-012. Skipping an inapplicable question and taking its natural
default is not "assuming an answer to a posed question" (INV-007) — the question is never posed.

## Acceptance criteria

- [ ] When `docs/business_problem.md` carries the `> 🤖 Bootcamp-generated business case` marker (or no real stakeholders are recorded), Step 25's question is not asked; the self-directed spot-check runs and `docs/uat_results.md` is written.
- [ ] When the business problem is real (no marker), Step 25 asks the pinned verbatim question exactly as today (INV-056).
- [ ] The skip is stated briefly (not silent to the point of confusion) and adds no turn.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — add a marker guard around Step 25.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Skip the \"involve business users\" UAT question for bootcamp-generated scenarios" (2026-07-20, Module 6)
- Priority: Medium
- Related specs: `encourage-own-business-case.md` (the generated-scenario marker), `pin-remaining-interaction-questions.md`
