# Pin the Module 6 iterate-vs-proceed decision as a proper numbered 👉 question

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 6's "Iterate vs. proceed decision gate" presents the 80–89% branch as freeform prose:

> **UAT 80–89%:** "Most tests pass but there are gaps. Iterate or move forward?"

This bootcamper-facing decision has **no 👉 prefix** (INV-005), joins its two choices with **"or"**
with no numbered list (INV-009/INV-051), is **ambiguous** for a Yes/No answer (INV-008), and is
**not pinned verbatim** as a gate (INV-056) — five interaction invariants at once. The parallel
decision gates in Module 5 are done correctly (neutral lead + "Reply with a number:" + numbered
list).

## Root cause

`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — the
`## Iterate vs. proceed decision gate` section renders all three UAT branches as quoted prose,
with the 80–89% branch carrying the `or`-joined question. Pre-existing (not caused by a recent
change).

## Proposed change

Reword the gate so the two routing branches (≥90%, <80%) are statements that flow directly to the
module transition question, and the mixed 80–89% branch asks a single pinned 👉 question with a
neutral lead and a numbered list (INV-051), e.g.:

> 👉 **Most tests pass but there are gaps. What would you like to do? Reply with a number:**
> 1. Iterate now to improve the results before moving on.
> 2. Move forward to the next module.

Also drop the number-leading module references in this section ("proceed to Module 7", "going back
to Module 5") in favor of module names (INV-079 polish).

## Acceptance criteria

- [ ] The 80–89% branch is a single pinned 👉 question with a neutral lead and a numbered list; no "or"-joined choices (INV-005/008/009/051/056).
- [ ] The ≥90% and <80% branches are statements that route to the transition question; they name modules, not numbers (INV-079).
- [ ] No other 👉 question is introduced; the module's transition question is unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — the iterate-vs-proceed decision gate.

## Source

- Audit (deep-dive conformance/coherence review), 2026-07-19 — finding #3 (MAJOR; pre-existing).
- Priority: High.
- Related specs: `interaction-or-questions.md` (INV-051), `module-references-by-name-not-number.md` (INV-079).
