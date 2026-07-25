# Guarantee the entity-resolution quiz offer is actually presented

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamper reports that the quiz offer:

> 👉 **Would you like to test your knowledge of entity resolution with a short quiz?**

is sometimes **not asked**. It was asked in the reported session (they accepted and answered three
questions), but they have seen runs where the module skipped it. This is intermittent behavior across
runs, not a failure observed in that session.

Why it matters, in their words: "The quiz is the only interactive knowledge check in the entire bootcamp.
When it is skipped, the bootcamper gets a lecture instead of a check on understanding, and neither they
nor the plugin ever learns whether the concepts landed before the hands-on modules begin. Because Module
0's content is foundational, a silent skip there compounds through everything after it."

And the broader cost: "It also erodes trust in the module contract generally: if a question documented as
'pinned, asked verbatim' can quietly not happen, the bootcamper cannot rely on any of the other pinned
questions either."

## Root cause

**Confirmed: the wording is already correct; the enforcement is not.** The question *is* pinned verbatim
at `concepts.md:92` under INV-056. The surrounding text then gives three separate signals that presenting
it is optional:

- `concepts.md:88` — "it is entirely optional and **never blocks**"
- `concepts.md:95` — "This is optional, **NOT a ⛔ gate**"
- `concepts.md:116` — "The quiz never replaces the mandatory exploration/readiness gate"

So the module contains two adjacent 👉 questions where the **first** (quiz) is explicitly marked
unenforced and the **second** (readiness gate) is mandatory. Under any pressure toward brevity, the
rational reading is to collapse the optional question into the mandatory one and go straight to "Are you
ready to move on…?".

**The underlying conflation:** "never blocks" was written to describe the **bootcamper's** obligation —
they must not be forced to take a quiz — but it reads as describing the **assistant's** obligation to
ask.

**And nothing detects the omission.** Other parts of the bootcamp verify their own output: recap sections
are re-read to confirm they landed (`module-completion.md` Step 2c) and the Truth Set visualization
artifact is re-checked for existence before the module is marked complete (INV-077). There is no
post-hoc check that the quiz was ever offered, so a skip is silent and unrecoverable.

Note that the same file already has this exact structure a second time: the questions/discussion
invitation at `concepts.md:58-79` is also marked "NOT a ⛔ gate — it never blocks" (`:73`). It is exposed
to the identical failure mode and should be fixed in the same pass.

## Proposed change

In order of impact, following the reporter's own ordering:

1. **Separate "asking" from "answering" explicitly in the spec.** Replace the ambiguous "never blocks"
   framing with wording that cannot be misread, e.g.:

   > **Presenting this question is MANDATORY (INV-005/INV-056). Declining it is free and costs the
   > bootcamper nothing. "Never blocks" describes the bootcamper's ANSWER — not whether you ask.**

   Apply the same clarification to the questions/discussion invitation at `concepts.md:73`.
2. **Record the outcome.** Write `quiz_offered: true|false` and `quiz_taken: true|false` into
   `config/bootcamp_progress.json` at Module 0's close. The module already writes `modules_completed` and
   a recap section there, so this is one more field in an existing write. A silent skip becomes a visible
   one, and the data makes the intermittency measurable across runs.
3. **Verify it at Module 0's recap step.** Module 0 already appends a recap section whose "Questions &
   Responses" subsection is specified to include the quiz offer/questions if taken. Make that step
   **assert** the offer was presented, mirroring how the Truth Set visualization module re-checks its
   artifact exists before marking itself complete (INV-077). If the assertion fails, present the offer
   then — the recovery is cheap and the module has not yet closed.
4. **Delete "This is optional, NOT a ⛔ gate."** (`concepts.md:95`) It is the single line most likely to
   license skipping, and the protection it provides is already fully covered by the bootcamper's
   standing ability to exit at any time plus the mandatory readiness gate that follows.
5. **Keep the quiz itself genuinely declinable.** The fix must not turn the quiz into a ⛔ gate: a
   bootcamper answering "no" proceeds immediately, and any readiness signal mid-quiz still ends it with no
   penalty (`concepts.md:111`). The mandatory thing is the *asking*.

Do not weaken `concepts.md:116` ("The quiz never replaces the mandatory exploration/readiness gate") —
that sentence is correct and load-bearing; it just needs to stop reading as license to skip the quiz.

## Acceptance criteria

- [ ] `concepts.md` states that **presenting** the quiz offer is mandatory (INV-005/INV-056) and that
      "never blocks" describes the bootcamper's answer, not whether the question is asked.
- [ ] "This is optional, NOT a ⛔ gate." is removed from the quiz offer; the equivalent line on the
      questions/discussion invitation (`concepts.md:73`) receives the same clarification.
- [ ] Module 0's close writes `quiz_offered` and `quiz_taken` to `config/bootcamp_progress.json`.
- [ ] Module 0's recap step asserts the offer was presented and presents it if it was not, before the
      module can close.
- [ ] A bootcamper who declines proceeds immediately with no penalty, and a mid-quiz readiness signal
      still ends the quiz — the quiz never becomes a ⛔ gate.
- [ ] The mandatory exploration/readiness gate still always follows, whether the quiz was taken or
      declined.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): wording and a
      progress-file field only, with no platform- or language-specific behavior.

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — lines 58-79
  (questions invitation, incl. line 73), 85-116 (quiz offer, incl. lines 88, 92, 95, 116)
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — the module close:
  write the two progress fields
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — the recap step that gains
  the assertion, alongside the existing Step 2c re-read pattern

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Guarantee the entity-resolution quiz offer is
  actually presented" (2026-07-25, Entity Resolution Concepts)
- Priority: Medium
- Related specs: `specs/concepts-module-verified-qa-and-quiz.md` (added the quiz, INV-056),
  `specs/concepts-questions-before-quiz.md` (added the questions invitation with the same "NOT a ⛔ gate"
  wording), `specs/capture-entity-resolution-concepts-in-recap.md`,
  `specs/record-truthset-visualization-completion.md` (the INV-077 self-check pattern to mirror)

## Invariants introduced

- `INV-112` — The Entity Resolution Concepts module MUST present the pinned quiz-offer question
  verbatim on every run; "optional"/"never blocks" describes the Bootcamper's answer, never whether
  the question is asked. The module MUST record `quiz_offered`/`quiz_taken` at its close and MUST
  assert `quiz_offered` before closing. (Recorded in `specs/INVARIANTS.md`.)
