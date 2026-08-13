# A reassurance attached to a pinned question must be placed before it, everywhere

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two steps in the plugin pair a reassurance with a pinned 👉 question. One states the ordering
explicitly and gives the reason; the other lays it out in the opposite order, where following it
literally is impossible.

**Explicit and correct** — Module 1 is not involved; this is Bootcamp preparation Step 3
(`bootcamp-preparation/SKILL.md:173-176`):

> **Before asking, tell them the choice is not permanent** — that they can change it any time
> ("change verbosity", or "more code walkthroughs"). This has to come **first**: INV-005 requires the
> 👉 question to end the turn, so nothing can follow it, and a reassurance delivered after the answer
> cannot inform the choice it was meant to inform.

**Ambiguous** — Module 1 Phase 2 Step 10a
(`module-01-business-problem/phase2-document-confirm.md:92-102`) has the same shape, but the
reassurance is printed *after* the question **and after the end-the-turn directive**:

> 👉 **Where do you plan to deploy the final solution? Reply with a number:**
>
> 1. A cloud hyperscaler (AWS/Azure/GCP).
> …
> 4. Not sure yet.
>
> *(Internal: end the turn and wait.)* Reassure: "We'll develop everything locally first; deployment
> is addressed in the graduation production project and migration checklist."

Read literally there are only bad options. Placing the reassurance where it appears would put text
after the 👉, which **INV-005 forbids** (the question must end the turn). Deferring it to the reply
turn delivers it after the choice is already made — the exact failure Step 3's reasoning names, and
it matters most for option 4 ("Not sure yet"), where a bootcamper who does not yet know their
deployment target may guess rather than admit uncertainty precisely because nobody has told them the
answer is non-binding and revisited later.

This is not a broken path — the guide resolves it, as the dry-run walk did, by moving the
reassurance ahead of the question. But it resolves it by importing reasoning from a different file,
which is what makes it a defect worth fixing: an instruction that must be silently reinterpreted to
be followable teaches that the surrounding instructions are approximate.

## Root cause

The ordering rule is stated as local prose inside Bootcamp preparation Step 3 rather than as a
general rule about pinned questions, so nothing propagated it to the second site. Step 10a was
written with the question first (natural, since the question is the step's substance) and the
reassurance appended as a note, without noticing that the appended position is unreachable under
INV-005.

No invariant covers the ordering. INV-005 governs *that* exactly one 👉 ends the turn; INV-056 governs
the question's *wording*. Neither says where accompanying context goes, so there is nothing for a
conformance sweep to check and nothing for a reviewer to cite.

## Proposed change

1. **`phase2-document-confirm.md` Step 10a** — move the `Reassure:` sentence to *before* the pinned
   deployment-target question, matching Step 3's layout, and keep `*(Internal: end the turn and
   wait.)*` as the last line after the numbered choices.
2. **Generalize the rule once** rather than in two places. State it where the 👉 protocol lives —
   `bootcamp-onboarding/ground-rules.md`, "Conversation protocol (the 👉 rules)": any reassurance,
   caveat, recommendation, or framing that is meant to inform an answer MUST be presented **before**
   the 👉 question, because nothing may follow it and context arriving after the answer cannot inform
   it. Then have Step 3 and Step 10a rely on that rule instead of restating the reasoning.
3. **Sweep for other instances.** Any step whose text places explanatory content after its 👉 has the
   same defect; Step 4's "one-line recommendation" (`phase1-discovery.md:42-48`) already gets this
   right and can serve as the second correct example.

## Acceptance criteria

- [ ] Step 10a's reassurance appears before its pinned 👉 question.
- [ ] `ground-rules.md`'s 👉 protocol states the before-the-question ordering rule generally, with
      the reason (nothing may follow the 👉; context after the answer cannot inform it).
- [ ] No step in `plugins/` places a reassurance, recommendation, or caveat after its 👉 question.
- [ ] A repo-level stdlib-only test asserts that in every file under `skills/`, no non-blank,
      non-internal-directive prose line follows a `👉` line within the same step block — with the
      numbered-choice list that belongs to the question explicitly permitted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 10a
  ordering.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — state the rule once in the
  👉 protocol.
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — Step 3 can cite the general rule
  rather than restating its reasoning (optional tidy, not required for correctness).
- `tests/test_reassurance_precedes_question.py` — new guard.

## Source

- Feedback: none — dry run phase 3 (2026-08-13), conversational walk, Module 1 Phase 2 Step 10a
  reached with the maintainer answering as the Bootcamper
  (`Source: self-observed (assistant retrospective)`)
- Priority: Low — the guide resolves it correctly by analogy and no bootcamper-facing output is
  wrong. Worth fixing because it is an instruction that cannot be followed as written, which is the
  class the phase-3 procedure calls out for eroding the authority of neighbouring ⛔ rules.
- MCP re-check: n/a (no Senzing fact) — this is entirely an interaction-layer ordering question.
- Upstream: not applicable.
- Related specs: none
