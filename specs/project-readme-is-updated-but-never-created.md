# Project README is updated but never created

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Discover the Business Problem tells the guide to "**Update** `README.md`. Fill the
Overview and Business Problem sections" — but no earlier step creates the project
`README.md`, and nothing defines those sections. On every fresh bootcamp the step
is an instruction to edit a file that does not exist, with a shape nobody
specified.

The practical damage is small — a guide writes a README rather than stalling — but
the result differs run to run, and the step reads as though a template exists to
fill in.

## Root cause

`plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:192-195`
is the only place the project README is written, and it is phrased as an update.

Nothing creates it:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:69-76`
  ("1. Project setup") creates `src/`, `data/`, `docs/`, `config/`, `database/`
  and the two `config/` files, and no README.
- `bootcamp-preparation/SKILL.md` writes only
  `config/bootcamp_preferences.yaml` and `config/bootcamp_progress.json`
  (`:322-360`).
- `ground-rules.md:254-256` permits `README.md` in the project root whitelist,
  which is the only other mention — a permission, not a creation.

The one other README reference in the plugin is a different file
(`module-05-data-quality-mapping/phase2-data-mapping.md:854`, a `docs/README.md`).

This is the same class as `specs/nothing-owns-creating-the-recap-header.md`: a step
says *update* an artifact whose creation no step owns. That one is High because the
missing header has downstream consumers that degrade the keepsake; this one is Low
because nothing downstream reads the project README. The shared shape is the reason
to fix them together.

n/a — no Senzing fact is involved.

## Proposed change

1. Create the README where the rest of the project scaffold is created:
   `onboarding-flow.md` "1. Project setup", alongside the two `config/` files, with
   an `## Overview` and a `## Business Problem` heading and a one-line placeholder
   under each — so Step 12's "fill the sections" has sections to fill. Keep it
   silent, like the rest of that step (INV-012).
2. Reword `phase2-document-confirm.md:192-195` to say it fills the two sections
   created at project setup, and to create the file if it is absent (a resumed
   project, or one the bootcamper started by hand).
3. Say what else belongs in the README, or explicitly that nothing does — the
   current step names two sections and leaves the rest of the file undefined.

## Acceptance criteria

- [ ] After the onboarding preface completes on a fresh project, `README.md`
      exists in the project root with `## Overview` and `## Business Problem`
      headings.
- [ ] `phase2-document-confirm.md` Step 12 fills those sections and creates the
      file if absent, rather than assuming it.
- [ ] The README stays in the project-root whitelist and no other `.md` is added
      to the root (`ground-rules.md:254-256`).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` —
  create the README at project setup.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` —
  Step 12 fills rather than assumes, and creates if absent.

## Source

- Feedback: dry run phase 3, 2026-08-13 — hit at Step 12 on a fresh Core walk; the
  file did not exist (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: `specs/nothing-owns-creating-the-recap-header.md` (same class:
  a step updates an artifact whose creation is unowned)
