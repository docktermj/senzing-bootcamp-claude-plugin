# Drop the Module 4 data-collection-checklist gate and the Module 6 executive-summary gate — generate by default and announce

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two more low-stakes yes/no gates sit in front of generating deliverables the bootcamper
almost always wants — the same pattern already fixed for Module 1's stakeholder summary
and graduation's production config by `drop-deliverable-generation-gates.md`. The
bootcamper asked to remove both: always generate, and announce (as a statement) what was
created in the end-of-module summary.

1. **Module 4 data-collection checklist** — Step 4 asks "👉 I have a data collection
   checklist … Want me to add it to `docs/data_collection_checklist.md`?" before creating
   the file.
2. **Module 6 executive/stakeholder summary** — Phase D offers "Would you like a one-page
   executive summary for your team?" before writing `docs/stakeholder_summary_module6.md`.

## Root cause

Both gate a deliverable behind an optional question by design:

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:242` — "👉 **I have
  a data collection checklist … Want me to add it to `docs/data_collection_checklist.md`?**"
  then (`:244-248`) create the file only if yes.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:167` —
  "After validation, offer: 'Would you like a one-page executive summary for your team?' If
  yes, … save it to `docs/stakeholder_summary_module6.md`" (`:167-170`).

No invariant requires either gate. INV-012 (suppress output not important to the
bootcamper) favors dropping low-value confirmations; INV-032 requires the end-of-module
summary to list files produced, which is where each creation is announced.

## Proposed change

- **Module 4 Step 4:** drop the 👉 gate (`:242`). Always create
  `docs/data_collection_checklist.md` (Data Inventory Table + Validation Checklist) and
  state its creation in the module's end-of-module "Files produced" list (INV-032). Keep
  the guidance to fill it in before Module 5, phrased as a statement, not a question.
- **Module 6 Phase D:** drop the executive-summary offer (`:167-170`). Always create
  `docs/stakeholder_summary_module6.md` and state its creation in the Step 28 end-of-module
  "Files produced" list (INV-032).
- Leave the genuinely optional visualization offers in these modules intact — the
  data-collection loading-strategy question (`module-04 SKILL.md:409`), the Module 6
  cross-source visualization offer (`phaseD-validation.md:58`), and the results-dashboard
  offer (`phaseD-validation.md:118`) are separate and out of scope here.

## Acceptance criteria

- [ ] `docs/data_collection_checklist.md` is always generated in Module 4 (no 👉 gate) and its creation is announced as a statement in the end-of-module summary (INV-032).
- [ ] `docs/stakeholder_summary_module6.md` is always generated in Module 6 (no gate) and announced in the Step 28 end-of-module summary (INV-032).
- [ ] Neither removed gate leaves a dangling reference (step text/checkpoints reconciled); no new 👉 question is introduced (INV-005/INV-012).
- [ ] The unrelated visualization/loading-strategy offers in these modules are unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — remove the Step 4 checklist gate (`:239-248`); always create the file; announce at completion.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — remove the executive-summary offer (`:165-170`); always create the file; announce in the Step 28 summary (`:104-134`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Drop the data-collection-checklist yes/no gate; create it by default" (2026-07-18, Module: data_collection); "Drop the executive-summary yes/no gate; create it by default" (2026-07-18, Module: data_processing).
- Priority: Medium.
- Related specs: `drop-deliverable-generation-gates.md` (established this pattern for the Module 1 stakeholder summary and graduation config — this extends it to two more gates).
