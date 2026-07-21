# Trim onboarding preface copy: drop the foreshadowing line and soften the "trophy" framing

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two bootcamper-facing wording nits in the onboarding preface (`onboarding-flow.md`):

1. **Foreshadowing filler.** The step-0 setup preamble tells the bootcamper that after
   setup "you'll see a big **WELCOME TO THE SENZING BOOTCAMP** banner: that's when the
   guided bootcamp officially starts and I'll begin asking you questions." The
   bootcamper flagged this as unnecessary foreshadowing that just delays getting
   started — the bootcamp begins immediately after anyway.
2. **"Trophy" reads as cheesy.** The step-3 overview describes the recap PDF as a
   "professional **recap PDF** trophy — a keepsake of everything you built." The
   bootcamper found "trophy" a little pretentious/cheesy and asked for wording that
   conveys the PDF's value without that connotation.

## Root cause

Both are wording choices, not defects:

- Foreshadowing line: `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:26-28`
  ("Then you'll see a big **WELCOME TO THE SENZING BOOTCAMP** banner: that's when the
  guided bootcamp officially starts and I'll begin asking you questions.").
- "Trophy" framing: `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:94`
  ("You finish with a professional **recap PDF** trophy — a keepsake of everything you
  built, …").

INV-012 (suppress output that is not important to the bootcamper) supports trimming the
foreshadowing line. INV-048 uses the word "trophy" as the *internal* name of the recap
document — that internal term is out of scope here; only the bootcamper-facing
descriptive copy is softened.

## Proposed change

- **Step 0 preamble (`:24-28`):** drop the forward-looking sentence about the WELCOME
  banner and questions. Keep the short administrative narration ("I'm going to do some
  quick administrative setup: creating your project directory and checking your
  environment."). The WELCOME banner in step 3 already announces that the bootcamp is
  starting, so nothing is lost.
- **Step 3 overview (`:94-98`):** reword the recap-PDF line to highlight its value
  without "trophy" — e.g. "You finish with a professional **recap PDF** — a keepsake of
  everything you built, module by module, to keep and share with your team." Leave the
  sample-recap pointer (`:95-98`) intact.
- Do **not** touch INV-048's internal "trophy document" term, the graduation 🏆 reveal
  (`graduation/SKILL.md:256`), or other internal "trophy" references — this change is
  scoped to the two preface copy lines the bootcamper reacted to.

## Acceptance criteria

- [ ] The step-0 preamble no longer foreshadows the WELCOME banner or "I'll begin asking you questions"; it reads as brief administrative narration only.
- [ ] The step-3 overview describes the recap PDF's value without the word "trophy" (bootcamper-facing copy), and still points to the shipped sample recap.
- [ ] INV-048's internal "trophy document" naming and the graduation reveal are unchanged.
- [ ] No 👉 question is added or removed; INV-005/INV-012 remain satisfied.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — drop the foreshadowing sentence (`:26-28`); reword the recap-PDF line to remove "trophy" (`:94`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Remove 'foreshadowing' line from setup preamble" (2026-07-18, Module: onboarding); "'Trophy' wording for the recap PDF sounds pretentious/cheesy" (2026-07-18, Module: onboarding).
- Priority: Medium.
- Related specs: none.
