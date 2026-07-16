# Pin a single-meaning explore-gate question (no ambiguous "or")

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The entity-resolution exploration gate was asked as an either/or:

> "Would you like to explore any entity-resolution concepts, or shall we move on
> to the welcome?"

A bare "yes" is ambiguous — it could mean "yes, explore" or "yes, move on." This
violates INV-008 (each 👉 question must be unambiguous for a yes/no answer) and
INV-009/INV-051 (choices are not joined with "or").

## Root cause

The exploration-gate wording is **not pinned** in the skill, so the guide
improvised a non-compliant either/or question.
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/entity-resolution-intro.md:49-61`
("Mandatory exploration gate") and
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:75-84`
(step 3) instruct the guide to "end the turn on a single 👉 question" but do not
give the verbatim question. `specs/interaction-or-questions.md` (implemented,
INV-051) reworded *hardcoded* "or"-joined questions, but there was no hardcoded
question here to rewrite — the wording is left to the model, so the invariant can
still be violated at runtime.

## Proposed change

Add an explicit, INV-008/INV-051-compliant gate-question template to
`entity-resolution-intro.md`, and reference it from `onboarding-flow.md` step 3.
Phrase it as a single yes/no where "yes" and "no" each have exactly one meaning
and no alternatives are joined with "or" — e.g.:

> 👉 **Are you ready to move on to the welcome?**

"yes" (or a readiness signal) advances to the WELCOME banner; "no" or a follow-up
"?" keeps exploring. This maps directly onto the advance / keep-exploring logic
already at `entity-resolution-intro.md:63-69`.

## Acceptance criteria

- [ ] `entity-resolution-intro.md` provides a verbatim explore-gate 👉 question that is a single yes/no with exactly one meaning for "yes" and one for "no" (INV-008), with no "or"-joined choices (INV-051).
- [ ] The advance / keep-exploring branch logic still maps cleanly onto the pinned wording (readiness → advance; follow-up or "no" → re-present the gate).
- [ ] A grep for 👉 lines across `skills/bootcamp-onboarding/` shows no ambiguous either/or gate question.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/entity-resolution-intro.md` — add the pinned gate question.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — step 3 references the pinned wording.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Ambiguous \"or\" gate question has two meanings for \"yes\"" (2026-07-16, Module 0)
- Priority: Medium
- Related specs: `interaction-or-questions.md` (established INV-051; did not cover the un-pinned gate wording); `migrate-kiro-power.md`

## Invariants introduced

- `INV-056` — Every mandatory (⛔) gate question presented to the Bootcamper MUST have its exact wording pinned verbatim in the skill file, not left to the model to improvise (recorded in `specs/INVARIANTS.md`).
