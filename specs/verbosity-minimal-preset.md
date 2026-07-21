# Add a verbosity preset below "concise" for minimal/no explanatory output

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The onboarding "level of detail" question offers exactly three presets —
**concise**, **standard**, **detailed** — with nothing below "concise". An
experienced bootcamper who already knows what they are doing was annoyed by the
visual clutter of even the "concise" level and wanted a near-zero-detail mode.

> "One of the Bootcampers was annoyed by all of the visual clutter. They knew
> what they were doing."

## Root cause

Not a defect — the current design offers only three presets:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:120-144`
  (step 5) lists concise / standard / detailed and shows the persisted
  `verbosity` shape (a `preset` plus five numeric `categories`: `explanations`,
  `code_walkthroughs`, `step_recaps`, `technical_details`,
  `code_execution_framing`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:139-144`
  (the Verbosity section) fixes the same three presets.

No invariant fixes the *number* of presets: INV-024 requires only that the
bootcamper be asked their level of detail; INV-011 lets them change verbosity at
any time; INV-012 requires output not important to the bootcamper to be
suppressed. A lower tier is fully invariant-compatible — and arguably advances
INV-012 for expert users.

## Proposed change

Add a fourth preset below "concise" (suggested name **minimal**, or **quiet**)
that produces little-to-no explanatory output: no code walkthroughs, no per-step
recaps, no SDK-internals framing — just the questions, the results, and what is
strictly needed to proceed. It never suppresses required outcomes (👉 questions,
gates, banners, module completion artifacts).

- Add the preset to the step-5 numbered list in `onboarding-flow.md` (below
  concise) with a one-line description, and define its `categories` mapping
  (e.g. all five categories at their lowest level).
- Add the preset to the Verbosity section in `ground-rules.md` so "change
  verbosity" (INV-011) can select it at any time.
- Keep **standard** the recommended/default; the new tier is opt-in.
- Ensure the preset only reduces *explanatory* output — it must not weaken any
  invariant-required output (👉 questions per INV-005, gates, module banners per
  INV-028, completion recap per INV-032, the recap trophy per INV-048).

## Acceptance criteria

- [ ] The level-of-detail question presents a fourth preset below "concise" that
      yields minimal-to-no explanatory output.
- [ ] The new preset is persistable under the `verbosity` key with a defined
      `categories` mapping, and is selectable at any time via "change verbosity"
      (INV-011).
- [ ] Choosing the new preset never suppresses invariant-required output: every
      👉 question (INV-005), gate, module banner (INV-028), module completion
      summary (INV-032), and the recap trophy (INV-048) still appear.
- [ ] `standard` remains the default when the bootcamper skips the question.
- [ ] The preset list is presented with a neutral lead + numbered list, no
      "or"-joined choices (INV-051), single-meaning (INV-008).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — add the fourth preset to the step-5 list (`:120-144`) and its `categories` mapping.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — add the preset to the Verbosity section (`:139-144`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add a verbosity level below \"concise\" for minimal/no detail" (2026-07-17, Module General/Onboarding)
- Priority: Medium
- Related specs: `specs/interaction-or-questions.md` (verbosity-question wording, different concern); `specs/suppress-admin-write-noise.md` (admin write diffs, distinct).
