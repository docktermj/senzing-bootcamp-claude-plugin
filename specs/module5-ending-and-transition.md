# Module 5 must run module-completion on its mandatory path and use selected-modules transition

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5 (Data quality & mapping) has two defects at its end, both in the same place:

1. When the **optional** Phase 3 is skipped, Module 5 ends with none of the per-module completion
   apparatus — no end-of-module summary, no recap section, no "✅ Module complete" line
   (INV-032 / INV-079).
2. Its transition routes to the next module by re-checking whether SDK setup is done — a branch that
   is dead under the fixed module ordering (INV-076) and bypasses the `selected_modules`-driven
   transition every other module uses.

## Root cause (confirmed)

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:376-393`
  ("### 20. Transition", the end of the **mandatory** Phase 2) closes the turn on the transition
  👉 question with **no** Module Completion — no INV-032 summary, no `docs/bootcamp_recap.md`
  append (INV-085), no `✅ Module complete: Data quality & mapping` line (INV-079).
- The **only** invocation of the standard Module Completion process is in Phase 3, step 26
  (`phase3-test-load.md:154`), and Phase 3 is explicitly "**optional**" (`phase3-test-load.md:6-8`).
  So a bootcamper who skips Phase 3 gets a Module 5 transition with no INV-032 end elements and no
  INV-079 completion line. (`phase2-data-mapping.md` is absent from the set of files that reference
  `module-completion.md`; only `phase3-test-load.md` references it.)
- `phase2-data-mapping.md:381-386` routes "If Module 2 (SDK Setup) is already complete → Module 6 …
  If Module 2 is not yet complete → Module 2 (SDK Setup)." But the canonical ordering fixes SDK setup
  at position 4, always before Data quality & mapping (position 8) — see
  `bootcamp-preparation/SKILL.md:45-63` — so the "→ Module 2" branch is unreachable/contradictory,
  and neither branch uses the `selected_modules`-driven next-module logic in
  `bootcamp-onboarding/module-completion.md:22,183`.

## Proposed change

1. **Run Module Completion on the mandatory path.** Invoke the standard Module Completion process
   (`bootcamp-onboarding/module-completion.md`) at the end of Module 5's mandatory flow — after
   Phase 2, independent of whether the optional Phase 3 runs — so the end-of-module summary, the
   name-based recap append (INV-085), and the `✅ Module complete: Data quality & mapping` line
   (INV-079) always fire exactly once. Phase 3, when taken, must not double-run completion.
2. **Use the canonical transition.** Replace `phase2-data-mapping.md:381-386`'s SDK-based branch with
   the `selected_modules`-driven transition (the next selected module after Data quality & mapping),
   naming it in the pinned 👉 question per INV-079; delete the dead "→ Module 2 (SDK Setup)" branch.

## Acceptance criteria

- [ ] Whether or not the optional Phase 3 runs, Module 5 presents all four INV-032 end elements (accomplished / files / why it matters / what's next), the INV-079 `✅ Module complete: Data quality & mapping` line, and appends its name-based recap section (INV-085) — exactly once.
- [ ] Module 5's transition question names the next module from `selected_modules` (INV-076 / INV-079); no branch routes back to SDK setup.
- [ ] Exactly one 👉 ends the yielding turn (INV-005).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — run Module Completion at the end of the mandatory path; replace step-20 routing with the `selected_modules` transition.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — ensure Phase 3 does not double-invoke completion (it becomes a follow-on, not the sole completion site).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — reference only; the canonical transition/completion source.

## Source

- Final review audit (2026-07-20), findings **M1** (missing completion apparatus) and **M2** (stale transition routing), merged (one edit surface).
- Priority: Medium
- Related specs: `module-references-by-name-not-number.md` (INV-079), `recap-sections-name-based-and-complete.md` (INV-085), `customizable-module-selection.md` (INV-076 ordering / `selected_modules`).
