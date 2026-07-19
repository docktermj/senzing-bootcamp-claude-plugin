# Record the Truth Set visualization as a first-class module (modules_completed entry + recap section)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The "Truth Set visualization" is a selectable module (INV-077) and is treated as a first-class
module by the example recap (its own `## Truth Set visualization` section) and by graduation
(`graduation/SKILL.md:88-91` assumes `truthset_visualization` is a `modules_completed` entry
needing its own section). **But the module flow never records it.** Module 3's close
(`phase3-report-close.md` Step 12) adds only `system_verification` to `modules_completed` and
appends only the "System verification" recap section; `phase2-visualization.md` has no
completion/recap-append step. A plugin-wide grep shows `truthset_visualization` is **never added to
`modules_completed`** by any skill.

Consequences: mid-bootcamp (resume/handoff) the recap is missing the visualization "wow-moment"
section; `modules_completed` never reflects the visualization; and graduation's general
reconcile-by-`modules_completed` loop rests on a false premise — the section is recovered only by a
hard-coded special-case backfill. Compounded by a number-vs-name mismatch:
`module-completion.md:21` says "add this module's **number**," while graduation matches **by name**
and `modules_completed` uses name tokens (`truthset_visualization`).

## Root cause

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md:161-181`
  (Step 12) records only "Module 3" / `system_verification`.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — no
  completion step for the Truth Set visualization module.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:21` — "Add this
  module's number to `modules_completed`" (should be a name token).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:83-92` — reconcile hard-codes synthesizing
  `truthset_visualization` because the flow never records it.

## Proposed change

Maintainer decision (2026-07-19): treat Truth Set visualization as a **full module** recorded by
the flow.

1. **Module 3 close (`phase3-report-close.md` Step 12):** record BOTH modules, in experienced order
   (System verification first, then Truth Set visualization when it ran). Add `system_verification`
   to `modules_completed`; when the Truth Set visualization ran, also add `truthset_visualization`.
   Append a name-based recap section for each — `## System verification — {ts}` and, when the viz
   ran, `## Truth Set visualization — {ts}` (each with the four subsections; the viz section embeds
   any captured screenshot). Both idempotent, append-only (INV-085).
2. **`module-completion.md` Step 1:** `modules_completed` entries are module **name tokens**, never
   catalog numbers; a skill hosting more than one selectable module adds one entry per module it
   completed.
3. **Graduation reconcile (`graduation/SKILL.md` Step 1a):** since the flow now records both
   entries, the reconcile is normally a no-op; reframe it as a recovery/backfill for modules
   interrupted before their completion step ran.

## Acceptance criteria

- [ ] When the Truth Set visualization runs, `truthset_visualization` is added to `modules_completed` (name token, after `system_verification`) and a name-based `## Truth Set visualization` recap section is appended by the module flow (not only by graduation).
- [ ] `modules_completed` uses module name tokens everywhere (no "add this module's number"); graduation's name-based reconcile matches what the flow writes.
- [ ] Graduation's reconcile is reframed as a recovery backfill (no longer premised on the flow never recording `truthset_visualization`).
- [ ] The shipped example recap remains consistent (System verification + Truth Set visualization sections), `--check` passes, and the PDF re-renders.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — Step 12 dual recording.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — name-token wording.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — reconcile reframed as recovery.
- `specs/INVARIANTS.md` — new INV-086.

## Source

- Audit (second deep-dive), 2026-07-19 — new MAJOR coherence/completeness finding; maintainer chose "full module".
- Priority: High.
- Related specs: `customizable-module-selection.md` (INV-077), `module3-synthetic-verification-data.md` (the system_verification/truthset_visualization split), `recap-sections-name-based-and-complete.md` (INV-085), `recap-durability.md` (INV-059 recovery).

## Invariants introduced

- `INV-086` — When the Truth Set visualization module runs, the Module 3 close records `truthset_visualization` as its own name-token `modules_completed` entry (after `system_verification`) and appends its own name-based `## Truth Set visualization` recap section; `modules_completed` entries are name tokens, never numbers. (recorded in `specs/INVARIANTS.md`, pending maintainer wording sign-off).
