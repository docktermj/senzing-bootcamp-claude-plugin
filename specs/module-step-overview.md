# Module start: enumerate a numbered step overview

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The invariants require that "At the beginning of each module, enumerate the steps
that will be taken in the module." The global ground rules mandate this, but each
module's own start instruction lists only the banner, journey map, and
before/after framing — it does not remind the model to present the numbered step
overview, so the enumeration can be dropped in practice.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:127` mandates
"a brief numbered step overview" at every module start, but each module SKILL's
"First:" line (e.g. `module-01-business-problem/SKILL.md:14`,
`module-02-sdk-setup/SKILL.md:14`, `module-03-system-verification/SKILL.md:14`,
and the same pattern in modules 04–07) enumerates only banner + journey map +
before/after and omits the step overview.

## Proposed change

Append the numbered step overview to each module SKILL's start ("First:")
instruction, so every module explicitly presents banner → journey map →
before/after → **numbered step overview** before its first step.

## Acceptance criteria

- [ ] Each module SKILL's start instruction (modules 01–07) explicitly includes presenting a brief numbered overview of that module's steps.
- [ ] The wording is consistent across modules and references the existing `ground-rules.md:127` requirement.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/SKILL.md` and the SKILL.md of modules 02–07 — extend the "First:" start instruction.

## Source

- Audit: `migrate-kiro-power` verify/backfill audit (2026-07-15), invariant M4.
- Priority: Low.
- Related specs: `migrate-kiro-power.md`.
