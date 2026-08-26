# The acknowledge rule does not say it must land *before* the next module's tool calls

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Bootcamper answered **yes** to the pinned transition question *"Are you ready to move on to the
next module: Query, Visualize and Discover?"* — and then had to answer **yes** a second time.

What the transcript establishes: after the first `yes`, the guide made three consecutive tool calls
— invoking the `module-07-query-visualize-discover` skill, then two `Bash` reads of that skill's own
`.md` files to find its step list and 👉 questions — and emitted **no user-visible text at all**
between the answer and the eventual module-start banner. The Bootcamper's next message arrived as
`[Request interrupted by user]` followed by `yes`.

⚠️ **Recorded as inference, not fact, because the entry itself says so:** that the silence is what
prompted the second `yes`. The guide cannot see the Bootcamper's screen and does not know whether a
permission prompt, a spinner, or nothing at all was displayed during those calls. The
*unacknowledged interval* is the verified part; the causal link is the Bootcamper's account of it.

Their words:

> "I lost my place and had to re-confirm"

The cost is not the extra keystroke. The transition gate is the one moment per module where the
bootcamp deliberately stops and waits, and an answer that appears to change nothing reads as
unregistered — in a multi-hour guided flow where the Bootcamper then has to reconstruct where they
were and what they had just agreed to.

## Root cause

⚠️ **The entry concluded "Nothing in the plugin currently requires the answer to be acknowledged
first, so the gap is in the instructions." That is not what the files say, and the correction
narrows this spec considerably.** The rule exists.

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:141-151`:

```text
- **Acknowledge** the bootcamper's answer before proceeding: at most 2 sentences and 50 words,
  referencing at least one specific thing they said. Never a bare "Got it." / "Okay." A
  dead-end acknowledgment (no next step, no question) is a violation - always follow with the
  next step or the next 👉 question.
  - **When the answer carries nothing to reference, name the consequence instead.** A bare
    readiness signal ("no", "ready", "let's go"), a bare option number, or a one-word decline has
    no specific content to quote […] Satisfy its **intent** — prove you read the answer — by
    naming what that answer selected or what happens because of it […]
```

A bare `yes` to a transition question is precisely the sub-case that clause was written for. So the
guide had a rule and did not satisfy it.

**What the rule does not say is *when* — and the transition is the one place where "when" is a
structural question rather than a stylistic one.** "Acknowledge the answer before proceeding" is
satisfiable, on a plain reading, by an acknowledgment composed into the same reply as the module
banner: the guide acknowledges, then proceeds, and both land together. That reading is correct
everywhere except here, because everywhere else the next step is *composed*, not *loaded*.

At a module transition the next step cannot be composed until the skill is invoked and its phase
files are read. `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:456-458`:

```text
*(Internal: end the turn on this question and wait.)* On completion, set `current_step` to
`null` in `config/bootcamp_progress.json` and, on an affirmative reply, produce the Module 7
start banner, journey map, before/after framing, and step overview per the ground rules.
```

It specifies **what** to produce and is silent on what the Bootcamper sees first. The same silence
is in the shared step —
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:370-378` ("Step 4:
Transition question") defines asking the question and says nothing about receiving the answer.

So the acknowledgment and the banner get composed together *after* the loading, and the loading is
where the silence lives. **This recurs at every one of the module transitions** — it is not a
property of this run.

⛔ **This is not the INV-247 class and must not be fixed as one.** Nothing was improvised and no
extra question was asked. The guide followed a rule that did not reach far enough.

## Proposed change

**State the ordering where the acknowledge rule is defined, in `ground-rules.md`.** Add to the
acknowledge clause that when proceeding requires loading anything — invoking a skill, reading files,
running a script — the acknowledgment is emitted **first, in its own turn-visible text, before the
first tool call**. Name the reason: tool calls produce no bootcamper-visible output, so an
acknowledgment composed after them leaves the answer looking unregistered for the whole interval.

**Name the transition as the case that motivates it.** One line at
`module-completion.md` Step 4 stating that on an affirmative transition answer the guide emits a
short visible line naming the module being started, *then* invokes that module's skill. One line is
enough — it is an acknowledgment, not a preview, and it must not duplicate the banner, restate the
journey map, or ask anything (a dead-end acknowledgment is already a violation under the same
clause, and the banner that follows is the next step).

⚠️ **Do not add a 👉 question, and do not turn the acknowledgment into a turn boundary.** The
acknowledgment is a statement; the module-start apparatus follows in the same flow. INV-005–INV-009
are untouched, and the transition question is still asked exactly once (INV-006).

**Point `phaseD-validation.md`'s transition paragraph at the shared rule** rather than restating it,
per the state-it-once discipline (INV-179). The other modules' transitions inherit from
`module-completion.md` already, which is why the fix belongs there and not in ten phase files.

## Acceptance criteria

- [ ] `ground-rules.md`'s acknowledge clause states that when proceeding requires a skill
      invocation, file read or script run, the acknowledgment is emitted before the first tool call.
- [ ] `module-completion.md` Step 4 states that an affirmative transition answer is acknowledged
      with a short visible line naming the module being started, before that module's skill is
      invoked.
- [ ] The added line is a statement, contains no 👉, and does not duplicate the module-start banner,
      journey map, before/after framing or step overview.
- [ ] The transition question itself is unchanged and still asked once (INV-006); no new question is
      introduced (INV-005–INV-009, INV-247).
- [ ] A test asserts the ordering rule ships in `ground-rules.md` and that `module-completion.md`
      Step 4 carries the acknowledgment instruction. ⚠️ Whether a given run *emits* it is not
      statically testable — say so in the guard's docstring rather than implying otherwise.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the acknowledge clause
  gains its ordering-relative-to-tool-calls requirement
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — Step 4: acknowledge
  the affirmative answer before invoking the next module's skill
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — point the
  transition paragraph at the shared rule instead of leaving the interval unstated
- `specs/INVARIANTS.md` — register the ordering rule
- `tests/` — a guard asserting both sites carry it

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Module transition \"yes\" is not
  acknowledged before the next module loads" (2026-08-25, Module: Query, Visualize and Discover;
  `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). The defect is entirely in the plugin's own interaction rules;
  no SDK method, flag, response shape or server behavior is asserted. Verified in the shipped files
  on 2026-08-25.
- Upstream: not applicable.
- Related specs: `specs/reassurance-must-precede-its-pinned-question.md` (the same
  ordering-of-visible-text concern at a different point), `specs/module5-ending-and-transition.md`,
  `specs/statement-only-step-cannot-satisfy-one-question-per-turn.md`

## What the re-check changed in this spec

The entry's stated divergence — *"Nothing in the plugin currently requires the answer to be
acknowledged first"* — is **incorrect**: `ground-rules.md:141` has required exactly that, including
an explicit sub-case for bare readiness signals like `yes`. Had the spec been written from the
report, it would have added a second, competing acknowledge rule beside the existing one.

The real gap is narrower and is what this spec fixes: the rule is silent on **ordering relative to
tool calls**, and the module transition is the one point in the bootcamp where "before proceeding"
spans a multi-call, zero-output interval.

## Deviations from this spec, and why (2026-08-26)

No Senzing fact is involved, so nothing was re-verified against the server. Two deviations, both
widening the fix rather than narrowing it.

1. **The site set is four, not one.** This spec named `phaseD-validation.md` and reasoned that
   *"the other modules' transitions inherit from `module-completion.md` already, which is why the
   fix belongs there and not in ten phase files."* True of inheritance; false of the sites that
   **restate** the transition inline. An INV-246 scan for prose acting on an affirmative reply found
   three more, all with the identical zero-output interval:

   - `module-03-system-verification/phase2-report-close.md:183`
   - `module-03b-truthset-visualization/phase2-close.md:172`
   - `bootcamp-onboarding/module-completion.md`'s **graduation gate** — *"On an affirmative reply,
     invoke the `graduation` skill"* — which is the same defect at the last gate of the bootcamp,
     where an answer that appears to change nothing is the closing impression.

   All four now carry the rule and name the file that defines it, per the state-it-once discipline.

2. **INV-012 and INV-006 are cited at Step 4, and neither is the rule.** `conformance.py rules`
   flagged the new Step 4 stop sign as sitting in a section citing no invariant. Both cited
   invariants genuinely bear on the finding — the interval is invisible from the Bootcamper's point
   of view (INV-012), and the observed cost was the question being effectively answered twice
   (INV-006) — but the ordering requirement itself is registered by neither. It is deferred with
   drafted wording in this spec's `specs/IMPLEMENTED.md` entry, because Step 5 requires sign-off
   and the maintainer was away.
