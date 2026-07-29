# Module 5 step 16: the ≥80%-quality branch has no 👉 question, contradicting its own header

Maintain the invariant conditions in @INVARIANTS.md.

## Problem

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`,
step 16 ("Iterate vs. proceed decision gate"), opens with:

> "After presenting quality results, guide the decision and close the turn on one 👉
> question:"

— an unconditional instruction to end the turn on a 👉 question, followed by three
quality-tier branches. Two of the three carry an explicit pinned 👉 question with
numbered options:

- 70-79%: "👉 **Quality is acceptable. What would you like to do? Reply with a
  number:** 1. Proceed to loading now. 2. Iterate to improve [specific weak areas]
  first."
- <70%: "👉 **Quality needs improvement... What would you like to do? Reply with a
  number:** 1. Iterate to improve the data. 2. Proceed anyway..."

The ≥80% branch has no question at all — only a declarative statement: "Quality looks
strong. Ready to proceed to loading (Data processing)." There is no 👉 marker, no
numbered options, and no question mark.

Followed literally, this is unsatisfiable in the way `phase3-conversational.md`
describes: the section header says "close the turn on one 👉 question" for every case,
but the ≥80% case supplies no question to close on. An assistant following the file has
exactly two non-conforming choices: render a bare statement with no question (violating
the header's own instruction and leaving the turn without its required gate), or invent
an ad-hoc question not written anywhere in the skill (risking a different numbered-list
shape or wording each time, which is exactly what INV-051/INV-056 pinned-wording rules
exist to prevent elsewhere in this same file).

## Root cause

`phase2-data-mapping.md:547-565` (module-05-data-quality-mapping/phase2-data-mapping.md)
— the three quality-tier branches were authored with the two "needs a decision" cases
pinned explicitly, but the ≥80% "no real decision needed" case was left as prose only,
without updating the section's opening sentence to say "except when quality is ≥80%,
in which case state readiness and pause without a numbered question" (or, alternatively,
without adding a pinned question of its own).

Observed live during a phase-3 dry-run walk: Module 5 mapping for a real GLEIF source
scored 100% on NAME/ADDRESS/TRUSTED_ID, 96.5% on NATIONAL_ID, 100% on LEI_NUMBER — solidly
in the ≥80% branch — and the assistant following this file hit exactly the described
gap.

## Proposed change

Give the ≥80% branch its own pinned 👉 question, in the same numbered, no-"or" shape as
the other two branches, e.g.:

```markdown
- **Quality ≥80% and all critical fields mapped:**

  👉 **Quality looks strong. Ready to proceed to loading (Data processing)? Reply with a number:**

  1. Yes, proceed to loading.
  2. No, I'd like to iterate on something first.
```

This keeps the section's own "close the turn on one 👉 question" instruction true for
all three branches, and keeps the ≥80% path consistent with INV-005/INV-051/INV-056
rather than leaving it as the one branch where the assistant has to improvise.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` step 16's ≥80% branch contains an explicit 👉-marked,
      numbered question with no "or" joining choices, matching the shape of the other
      two branches.
- [ ] The section's opening sentence ("close the turn on one 👉 question") is true for
      all three branches without exception.
- [ ] Cross-platform / language-agnostic: this is a prose-only change to bootcamper-facing
      guidance, so it holds identically on Linux, macOS, and Windows and is unaffected by
      the bootcamper's chosen programming language.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
  (step 16, the "Iterate vs. proceed decision gate" section, ~lines 547-565).

## Source

Self-observed during a maintainer-run phase-3 dry-run walk (`.claude/skills/dry-run/`),
continuing a "push through the entire Bootcamp" session, while mapping a real GLEIF
(Moscow CORD) data source end-to-end through `mapping_workflow`. Not bootcamper-reported.
Date: 2026-07-29.
