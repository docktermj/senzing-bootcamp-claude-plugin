# Drop the word "trophy" from bootcamp language

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamp's onboarding, module-completion, and graduation language calls the accumulating recap
document (`docs/bootcamp_recap.md`) and the graduation PDF a "trophy" (e.g. "the recap trophy",
"the trophy the bootcamper keeps"). "Trophy" was requested in an earlier version of the plugin, but
the bootcamper now finds it a pretentious word for what is a recap/keepsake document and wants it
removed going forward.

## Root cause

Not a defect — deliberate wording that is now superseded. `grep -rni "trophy" plugins/ scripts/`
finds it pervasively (bootcamper-facing and internal):

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — `:3,17,70,73,100,128,256,261`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — `:7,29,85,113,120,196`
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:249`
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md:161`
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:129`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:112,123,168`
- `plugins/senzing-bootcamp/hooks/README.md` — `:16,20,21,73`
- `plugins/senzing-bootcamp/commands/graduate.md:2`
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `:2,49,596`
- `plugins/senzing-bootcamp/scripts/session-start.py:6`
- `plugins/senzing-bootcamp/scripts/capture_screenshots.py:2`
- `plugins/senzing-bootcamp/scripts/brand_tokens.py:7`

It also appears in two invariants: **INV-048** ("A trophy document, `docs/bootcamp_recap.pdf`...")
and **INV-081** ("...the recap PDF trophy...").

## Proposed change

Replace "trophy" throughout the user-facing and internal skill/script/hook language with a neutral
term: **"recap PDF"** for the PDF, **"recap"** for the accumulating `.md`, **"keepsake"** where a
noun reads better. Keep the 🏆 emoji decision to the maintainer — this feedback targets the *word*
"trophy", not the emoji (see graduation `SKILL.md:261`); flag it and let the maintainer choose.

Update **INV-048** and **INV-081** wording **in place** to drop "trophy" — a pure wording
clarification with no meaning change, permitted by INVARIANTS.md maintenance rule 2. Do **not** add
new invariants and do **not** renumber for a rename.

## Acceptance criteria

- [ ] `grep -rni "trophy" plugins/ scripts/` returns no bootcamper-facing or internal skill/script/hook occurrences (or only an occurrence the maintainer explicitly chooses to retain).
- [ ] INV-048 and INV-081 read without "trophy", meaning unchanged, no renumbering (maintenance rule 2).
- [ ] The recap PDF still always renders (INV-048) and every user-facing reference to the recap/PDF remains coherent (INV-003).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md`
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md`
- `plugins/senzing-bootcamp/hooks/README.md`
- `plugins/senzing-bootcamp/commands/graduate.md`
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`, `session-start.py`, `capture_screenshots.py`, `brand_tokens.py` — comments/docstrings
- `specs/INVARIANTS.md` — INV-048 and INV-081 wording (in place, no meaning change)

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Drop the word \"trophy\" from bootcamp language (recap \"trophy\" -> something else)" (2026-07-20, Module 6)
- Priority: Medium
- Related specs: `recap-pdf-professional-design.md`, `apply-senzing-style-guide-to-deliverables.md`
