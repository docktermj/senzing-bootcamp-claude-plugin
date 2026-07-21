# Give the Truth Set visualization module its full per-module apparatus

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The previous audit made Truth Set visualization a first-class **recorded** module (INV-086): it now
earns its own `truthset_visualization` name token in `modules_completed` and its own name-based
recap section. But recording alone left a coherence gap surfaced by the third ("be extra picky")
deep-dive: a first-class module is required to carry the **full per-module apparatus**
(INV-028–032) — a module-start banner, journey-map refresh, before/after framing, step overview
(INV-079), and the model/effort nudge (INV-063) at its start, plus its own end-of-module summary
and `✅ Module complete:` line (INV-032) at its close. Truth Set visualization had **none** of
this: Phase 2 dropped the bootcamper straight into "Step 9 setup" with no module-start apparatus,
and Module 3 close presented a single combined summary rather than one per completed module. The
module was recorded like a first-class module but *presented* like a sub-step, contradicting
INV-028–032 for a module that is explicitly **not** apparatus-exempt (unlike Bootcamp preparation,
INV-075, and Module 0, INV-078).

## Root cause

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — Phase 2
  began at "Step 9 setup" with no module-start apparatus block for `truthset_visualization`.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:144-187` — Steps 3–4
  assumed one module per skill turn: one completion line, one summary, one transition question.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md:161-181` —
  Step 12 recorded two modules but presented a single close.
- INV-086 stated Truth Set visualization is first-class and recorded, but did not spell out that
  "first-class" entails the full apparatus and non-exemption.

## Proposed change

Maintainer decision (2026-07-19): **give it the full apparatus.**

1. **Phase 2 module start (`phase2-visualization.md`):** before Step 9 setup, when
   `truthset_visualization` is selected, present a module-start apparatus block — set
   `current_module=truthset_visualization`; a `🚀🚀🚀 MODULE: TRUTH SET VISUALIZATION 🚀🚀🚀`
   banner; journey-map refresh with it shown `🔄` current; before/after framing; step overview
   (INV-028–031/INV-079); and the model/effort nudge (INV-063).
2. **`module-completion.md` Steps 3–4:** generalize for a skill that completed **more than one**
   module this turn — present a completion line **and** its own four-part summary **per** completed
   module (experienced order), and ask the single transition question **once**, after the last
   completed module's summary.
3. **Module 3 close (`phase3-report-close.md` Step 12):** present a completion line +
   end-of-module summary for **each** recorded module (System verification, then Truth Set
   visualization when it ran); ask the transition question once, after both.
4. **`INV-086`:** clarify in place that Truth Set visualization, as a first-class module, receives
   the full per-module apparatus and is **not** apparatus-exempt (no meaning change — hardens
   INV-077/INV-085 and aligns with INV-028–032).
5. **Module 3 `SKILL.md` Phase 2 bullet:** note it is a first-class module with its own apparatus.

## Acceptance criteria

- [x] When Truth Set visualization is selected, Phase 2 opens with a module-start banner, journey refresh (it `🔄` current), before/after, step overview, and model/effort nudge before Step 9 setup.
- [x] At Module 3 close, each recorded module gets its own `✅ Module complete:` line + four-part summary, in experienced order; the transition question is asked exactly once, after the last summary.
- [x] `module-completion.md` documents the multi-module-per-turn case for Steps 3–4.
- [x] INV-086 states the full-apparatus/non-exempt clause; Module 3 `SKILL.md` Phase 2 bullet reflects it.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — module-start apparatus block.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — Steps 3–4 multi-module handling.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — Step 12 per-module close.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — handoff note (first-class module).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — Phase 2 bullet.
- `specs/INVARIANTS.md` — INV-086 full-apparatus clarification.

## Source

- Audit (third deep-dive, "be extra picky"), 2026-07-19 — apparatus-gap finding introduced by the INV-086 recording change; maintainer chose "Give it the full apparatus".
- Priority: High.
- Related specs: `specs/record-truthset-visualization-completion.md`.
