# Interaction: eliminate "or"-joined questions

Maintain the invariant conditions in @invariants.md and implement the following improvement:

## Problem

Many 👉 questions asked of the bootcamper join two or more alternatives with the
word "or" (e.g. "concise, standard, or detailed?", "SQLite … or PostgreSQL?"),
which the invariants explicitly discourage ("Questions should not be 'complex'.
The use of 'or' is discouraged") and which the plugin's own ground rules forbid.
This is systemic — it appears across most modules, not one place.

## Root cause

Questions were authored with inline "or"-joined choices instead of the mandated
pattern in `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:22-24`:
"For two or more alternatives, use a neutral lead question plus a numbered list."

Confirmed instances (👉 questions to the bootcamper; instruction/rule text such
as "skip, combine, or abbreviate" is **not** in scope):

- `skills/module-02-sdk-setup/SKILL.md:102, 459, 551`
- `skills/module-01-business-problem/phase1-discovery.md:163, 192, 194, 213`
- `skills/module-04-data-collection/SKILL.md:396` (already numbered, but still says "or")
- `skills/module-05-data-quality-mapping/phase1-quality-assessment.md:232, 238`
- `skills/module-05-data-quality-mapping/phase2-data-mapping.md:30, 283, 287`
- `skills/module-05-data-quality-mapping/phase3-test-load.md:120, 164`
- `skills/module-07-query-visualize-discover/phase2-discover.md:137, 189`
- `skills/module-07-query-visualize-discover/phase2b-discover.md:94`
- `skills/bootcamp-onboarding/feedback.md:42, 44, 45`
- `skills/graduation/SKILL.md:86, 155`

The two preface questions (`skills/bootcamp-onboarding/onboarding-flow.md:114, 139`)
were already converted to the neutral-lead + numbered-list pattern and are the
reference model for this cleanup.

## Proposed change

- Rewrite each multi-choice 👉 question as a **neutral lead** question ending in
  "… Reply with a number:" followed by a **numbered list** of the options — the
  pattern already applied at `onboarding-flow.md:114, 139`.
- For compound questions that bundle two asks joined by "or" (e.g. feedback.md:42
  "What happened, or what would you change?"), split into a single clear ask.
- Leave answer-format hints that legitimately use "or" alone (e.g.
  `module-02-sdk-setup/SKILL.md:174` "Please respond yes or no").

## Acceptance criteria

- [ ] No 👉 question **to the bootcamper** joins two or more choices with "or"; every multi-choice question uses a neutral lead question plus a numbered list per `ground-rules.md:22-24`.
- [ ] Instruction/rule text and legitimate yes/no answer-format hints are unchanged.
- [ ] A grep for `👉` lines containing " or " across `skills/` returns only rule/instruction text, not questions.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @invariants.md).

## Affected files

- The skill files listed under **Root cause** — reword the enumerated questions.

## Source

- Audit: `migrate-kiro-power` verify/backfill audit (2026-07-15), invariants I4/I5.
- Priority: Medium (interaction-quality; violates the plugin's own ground rule).
- Related specs: `migrate-kiro-power.md`; preface portion already fixed.
