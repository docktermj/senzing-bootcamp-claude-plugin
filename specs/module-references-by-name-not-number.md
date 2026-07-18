# Reference modules by name, not number, in banners/transitions/completion lines (and lightly highlight completion)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Once modules become customizable (they can be skipped or effectively reordered),
fixed module numbers stop making sense. Across three feedback entries the
bootcamper asked to reference modules **by name** instead of number in:

- the **module-start banner** — "🚀🚀🚀 MODULE 1: DISCOVER THE BUSINESS PROBLEM 🚀🚀🚀"
  → "🚀🚀🚀 MODULE: DISCOVER THE BUSINESS PROBLEM 🚀🚀🚀";
- the **module-transition / readiness questions** — "👉 Are you ready to move on
  to Module 1?" → "👉 Are you ready to move on to the next module: Discover the
  Business Problem?"; and the completion-transition form "Module 2 complete. Ready
  to verify your setup end-to-end in Module 3?" → title-based;
- the **end-of-module completion line** — "✅ Module 1 complete: Discover the
  Business Problem" → "✅ Module complete: Discover the Business Problem" — and, per
  the bootcamper, make this line **lightly highlighted** (more visible than plain
  text, less prominent than the module-start banner).

## Root cause

Not a defect — the numbering is by design and is templated in a few places:

- **Banner template** hardcodes the number: `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:216-222`
  — "🚀🚀🚀  MODULE N: [MODULE NAME IN CAPS]  🚀🚀🚀". This is pinned by **INV-028**
  ("MODULE n: [title]") — see **Conflict with invariants**.
- **Transition questions** hardcode numbers:
  - template `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:144-145` ("Module N complete. Ready to …?");
  - `module-completion.md:155` (Module 7 close-out);
  - `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:140` ("Module 1 complete. Ready to install and configure the Senzing SDK in Module 2?");
  - `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:728` ("Module 2 complete. Ready to verify your setup end-to-end in Module 3?");
  - `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md:191` ("Module 3 complete. Ready to identify and collect your data sources in Module 4?");
  - Module 0's readiness gate names Module 1 by number: `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md:63` and `.../SKILL.md:44-48` ("Are you ready to move on to Module 1?").
- **Completion line** template: `module-completion.md:120-136` — line 121 "✅ Module N complete: {Module name}", inside a ```text fence with no emphasis beyond the ✅.

## Conflict with invariants

**Reconciliation decision (2026-07-18): drop the number everywhere and amend INV-028.**
The number is removed from the module-start banner as well as from transitions and
completion lines, for fully consistent name-based referencing.

- **INV-028** — "At the beginning of each module, a banner is presented 'MODULE n:
  [title]'." Dropping the numeral changes this outcome; per the decision above,
  INV-028 is amended to "MODULE: [title]" (a meaning change, i.e. a new/amended
  invariant recorded by `implement-spec`).
- **INV-006 / INV-056** — the readiness gate at `concepts.md:63` is pinned
  verbatim; changing its wording must keep it pinned and single-meaning.

## Proposed change

- Update the banner template (`ground-rules.md:216-222`) to "🚀🚀🚀  MODULE:
  [MODULE NAME IN CAPS]  🚀🚀🚀" (no number).
- Reword every numbered transition/readiness question to name the next module:
  "👉 Are you ready to move on to the next module: {Module Name}?" and "✅ Module
  complete: {Module Name}. Ready to move on to the next module: {Next Module
  Name}?", keeping each single-meaning (INV-008) and pinned where required (INV-056).
- Change the completion line (`module-completion.md:121`) to "✅ Module complete:
  {Module Name}" and **lightly highlight** it — e.g. bold the line and wrap it with
  a thin rule of `─` characters above and below (lighter than the banner's
  `━━━`/emoji-triplet). Keep the four completion subsections (INV-032) unchanged.
- Keep the journey map (INV-029) name-based, not sequence-number-based.
- Amend INV-028 accordingly.

This change follows the customizable-module-selection work, since the motivation is
that numbers break once modules are reorderable/skippable.

## Acceptance criteria

- [ ] The module-start banner reads "MODULE: {NAME IN CAPS}" with no number (INV-028 amended).
- [ ] No module-transition or readiness 👉 question references a module by number; each names the next module and stays single-meaning (INV-008), pinned where required (INV-056).
- [ ] The end-of-module completion line reads "✅ Module complete: {Module Name}" (no number) and is lightly highlighted (bold + thin `─` rule above/below), distinct from prose but lighter than the module banner.
- [ ] The four completion subsections (INV-032) and the journey map (INV-029) still render, name-based.
- [ ] A grep across `skills/` finds no bootcamper-facing banner/transition/completion text hardcoding "Module N"/"Module {number}" (recap-heading `## Module N:` templates that index the recap file are out of scope).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — banner template (`:216-222`), transition-pattern note (`:224`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — completion line (`:120-136`), transition template + Module 7 close-out (`:144-145`, `:155`).
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — transition (`:140`).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — transition (`:728`).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — transition (`:191`).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md`, `.../SKILL.md` — readiness gate wording (`concepts.md:63`, `SKILL.md:44-48`).
- `specs/INVARIANTS.md` — amend INV-028.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Drop fixed module numbers from banners/transition questions once modules are customizable" (2026-07-18, Module 1); "Drop module number from the end-of-module completion line, and lightly highlight it" (Module 1); "Module-completion transition question should use module titles, not numbers" (Module 2).
- Priority: Medium.
- Related specs: `customizable-module-selection.md` (the customizable-modules feature this follows from), `module-step-overview.md` / `end-of-bootcamp-banner.md` (banner/step framing), `onboarding-explore-gate-wording.md` (INV-056 pinned gate wording).
