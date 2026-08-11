# The feedback trigger phrase is taught only at graduation, after every chance to use it has passed

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

A bootcamper can say "bootcamp feedback:" at any point to open the feedback workflow — INV-010
guarantees it, and `ground-rules.md` lists it under "Any-time bootcamper controls". The mechanism
works: the entry reporting this *was itself filed that way*.

**Nothing in the bootcamper-facing flow teaches it.** Searching every shipped skill for the phrase
returns four files:

- `bootcamp-onboarding/feedback.md` — the workflow itself, which runs *after* the trigger fires
- `bootcamp-onboarding/ground-rules.md` — the guide's own rules, never shown to the bootcamper
- `module-06-data-processing/phaseD-validation.md` — one module, mid-bootcamp
- `graduation/SKILL.md` — the closing step: *"Say \"bootcamp feedback\" anytime if you'd like to
  share your experience."*

`onboarding-flow.md` — the WELCOME banner and overview, the one place every bootcamper reads
first — **never mentions it.**

So the phrase is taught at graduation, which is precisely when there is nothing left to give feedback
*about*. Every point of friction a bootcamper might have reported has already passed.

**Why the reporting bootcamper is not evidence against this.** They knew the phrase — the entry's
own context records the `UserPromptSubmit` hook firing on their first message of the run, during the
Module 0 primer, before any module completed. A bootcamper who does not already know it has no way
to learn it until the end. Discoverability that depends on already knowing is not discoverability,
and it silently biases the feedback the project receives toward people who were told out of band.

## Root cause

The feedback capture flow was specified from the trigger inward — `feedback.md` defines what happens
once the phrase is said, and `ground-rules.md` tells the guide to watch for it. Neither owns
teaching it, and the onboarding preface was written before the feedback flow existed. The graduation
mention was added where a closing "anything else?" naturally sits, which is the one place it cannot
change a run.

Nothing catches it: `test_feedback_routing.py` exercises the hook, INV-010 is satisfied (the
capability exists at any time), and no invariant requires the capability to be *announced*.

## Proposed change

1. **Name the trigger once, early, in bootcamper-facing text** — in the onboarding overview, after
   the WELCOME banner, where the bootcamp explains what it is about to do. One sentence: they can say
   "bootcamp feedback:" at any point and it will be captured without losing their place.
2. **Say what it costs them**, because that is the barrier: the flow brackets itself with entry and
   exit banners (INV-074) and returns them to the pending question, so raising something is not
   abandoning the module.
3. **Respect verbosity.** This is explanatory output, so it is suppressed under the `minimal` preset
   and one line under `concise` (INV-011/INV-012) — the same treatment INV-096 gives the time
   estimate. Do not add it to every module banner; once, early, is the point.
4. **Leave the graduation mention in place.** It serves a different purpose — a last invitation once
   the bootcamper has the whole run in view — and removing it would trade one gap for another.

⚠️ **Do not turn this into a 👉 question.** It is a statement. A question here costs a turn, needs an
answer nobody has, and INV-012 forbids output the bootcamper cannot act on.

⚠️ **Do not add it to every module start.** The module-start apparatus is already dense
(INV-028–031, INV-096, the model/effort nudge), and repeating an always-available control at every
boundary is the noise INV-012 exists to suppress.

## Acceptance criteria

- [ ] The onboarding overview names the trigger phrase in bootcamper-facing text, before the first
      content module.
- [ ] It states that using it does not lose the bootcamper's place, consistent with INV-074's
      bracketing banners.
- [ ] It is a statement, not a 👉 question, and does not extend the preface by more than a line under
      `concise`.
- [ ] It is suppressed under the `minimal` verbosity preset (INV-011/INV-012).
- [ ] The existing graduation mention is unchanged — verified by **opening
      `graduation/SKILL.md`**, not inferred from the onboarding edit (INV-182).
- [ ] A test asserts the phrase appears in bootcamper-facing onboarding text, so it cannot be
      dropped back into developer-only files.
- [ ] **Not runtime-verified:** whether a bootcamper who was told actually uses it is a
      conversational outcome only `dry-run` phase 3 can observe.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — the overview, after the
  WELCOME banner.
- `tests/` — the bootcamper-facing-mention assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Proactively tell bootcampers about the
  \"bootcamp feedback:\" trigger phrase" (2026-07-27, Module: Entity Resolution Concepts;
  Priority: not specified — the bootcamper moved to a new item before being asked;
  `Source: bootcamper-reported`).
- Priority: **Medium** (assigned here, not by the bootcamper). Nothing breaks, but the project's
  feedback channel is only reachable by people who already know it exists, which skews every entry
  the project receives — including the twelve others in this same file.
- MCP re-check: **n/a (no Senzing fact), server 1.32.3, 2026-07-31.** Onboarding wording is entirely
  plugin-side; no MCP tool owns it and none was called.
- Upstream: not applicable.
- Related specs: none cover feedback discoverability. `specs/feedback-flow-boundary-banner.md`
  (INV-074) defines the bracketing this spec's second criterion relies on.

## Deviations from this spec, and why (2026-08-11)

**Criterion 4 (`minimal` suppression) is implemented conditionally, not unconditionally.** The
spec treats the mention as ordinary explanatory output — suppressed under `minimal`, one line
under `concise`. That holds only *where a preset is readable*, which on a fresh bootcamp it is
not: INV-075 moved the verbosity question out of the preface into Bootcamp preparation, which runs
after step 3, so no `verbosity` key exists in `config/bootcamp_preferences.yaml` when the overview
is spoken. The bullet is therefore shown in full on a fresh run, and the suppression path is
reachable on a resumed run or when the bootcamper pre-seeded the preference (INV-133). This is the
same qualification INV-105 already carries for the plugin-version line eight lines above it in the
same file, and `onboarding-flow.md` states the caveat in both places rather than only one.

Evidence: `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:101-107` (the
pre-existing version-line caveat) and `:143-152` (the same caveat for this bullet); INVARIANTS.md
INV-105's "Clarified 2026-07-26" note, which records the identical finding from a phase-3 dry run.

Nothing else deviates: the change touches exactly the two Affected files, and criterion 7 is
reported as the spec already anticipated — not runtime-verified.

## Invariants introduced

- `INV-196` — The onboarding preface's overview MUST name the bootcamp-feedback trigger phrase in
  bootcamper-facing text before the first content module, as a statement and never a 👉 question,
  saying that using it does not cost the bootcamper their place; verbosity-aware where a preset is
  readable; never repeated at every module start; graduation's closing invitation retained in
  addition, never instead (recorded in `specs/INVARIANTS.md`, indexed under **Feedback capture**).
