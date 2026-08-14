# Statement-only step cannot satisfy one-question-per-turn

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Discover the Business Problem opens with a step that is explicitly a statement and
carries no 👉 question. Two ground rules then contradict each other over what the
guide does with it, and a third asserts something about it that is false:

- **INV-005** — "Exactly one 👉 question ends each yielding turn (zero or
  two-or-more is a violation)." Presenting the privacy reminder as its own turn
  ends a turn with **zero** 👉.
- **"Advance exactly one step at a time"** — folding the reminder into the same
  turn as Step 2's question advances **two** steps.
- **`ground-rules.md:624`** — "On **no** to the switch, acknowledge and present
  Step 1 the same reply turn, **ending on Step 1's single 👉 question**." Module
  1's Step 1 has no 👉 question to end on, so this instruction cannot be executed
  as written for the first module a bootcamper reaches after the model/effort
  nudge.

The right resolution is obvious in practice — a statement-only step is not a
yielding turn, so it rides along with the next step — but nothing in the plugin
says so, and the guide is left choosing which rule to break. That is the cost:
an instruction that cannot be followed teaches the model to read the surrounding
⛔ rules as advisory.

## Root cause

`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:6-12`
defines step 1 as "Data privacy reminder (**statement, no question**)" with its own
`**Checkpoint:** write step 1.`, and step 2 at `:14-18` as a separate section with
its own 👉 and its own checkpoint. The file's structure presents them as two
independent steps.

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` states the
three rules that collide:

- `:39` — exactly one 👉 ends each yielding turn.
- `:87-88` — "Advance exactly one step at a time."
- `:624` and `:684-693` — the post-nudge sequence, both of which assume Step 1
  ends on a 👉.

The plugin has no concept of a **non-yielding step**: every rule about step
boundaries assumes a step ends by asking something. Module 1's step 1 is the only
step in the plugin explicitly *labelled* statement-only, but the gap is structural
and it is not confined to single steps.

**Long non-yielding runs are the more consequential form**, found on the same walk:

- `module-01-business-problem/phase1-discovery.md` — steps 4a, 4b, 5 and 5a all
  complete without asking anything, so reaching the next 👉 (step 6a) advances
  **five** steps in one turn.
- `module-02-sdk-setup/SKILL.md` — after Step 1 finds an existing install, Steps
  1b, 4, 5 and 6 are all non-yielding and the next 👉 is Step 7's database
  question at `:848`. That run includes generating and executing a verification
  script (Step 4's two `generate_scaffold` calls), so a faithful turn does
  substantial work — and several progress checkpoints — before it may legally end.

That matters beyond tidiness, because `ground-rules.md:397-400` ties progress
writes to "each numbered-step boundary". Either those boundaries no longer coincide
with turn boundaries — so several checkpoints land in one turn, which is the write
noise INV-012 exists to reduce — or the guide holds them and writes once, which is
not what the rule says.

**The limiting case is a whole module.** `module-03-system-verification` contains
**exactly one** 👉 question — the module-transition question at
`phase2-report-close.md:135`. Steps 1, 1a, 2, 3, 4, 5, 5a, 6, 7, 8, 9, 10 and 11 —
MCP check, engine initialization, synthetic record generation, SDK initialization,
code generation, build, data-source registration, loading, results validation,
database operations, the verification report and cleanup — are all non-yielding. A
faithful walk therefore executes the entire module, including code generation,
compilation and a data load, inside a single turn.

Three of the module's own instructions become unfollowable at that point:

- `module-03-system-verification/SKILL.md:17-19` — "Execute every numbered step one
  at a time, in order", stated to have "the same absolute precedence as a mandatory
  gate".
- `phase1-verification.md:3-7` — "signal a stop by ending the turn on the single 👉
  question and waiting", describing a mechanism the module never provides.
- `phase1-verification.md:74` (Agent rule 10) — "every step MUST write its
  checkpoint to `config/bootcamp_progress.json`", which puts eleven checkpoint
  writes inside that one turn.

So this is not a cosmetic inconsistency about step 1 of one module. A rule the
plugin marks with gate-level precedence is unimplementable across a whole module,
and the fix — naming the non-yielding step, and decoupling checkpoint boundaries
from turn boundaries — is the same one.

n/a — no Senzing fact is involved.

## Proposed change

Name the concept once, in `ground-rules.md`, rather than patching Module 1:

1. Add a short rule to the conversation-protocol section: a step that is a
   **statement with no 👉 question is non-yielding** — it is presented in the same
   turn as the next step that does ask, and the two share that turn's single 👉.
   Say that this does not violate one-step-at-a-time, because a non-yielding step
   never ends a turn, and that the checkpoint for both steps is written once at
   that boundary.
2. Fix `ground-rules.md:624` (and the matching sentence at `:684-693`) to say
   "ending on the next single 👉 question" rather than "Step 1's single 👉
   question", so the post-nudge sequence is correct for a module whose Step 1 does
   not ask.
3. In `phase1-discovery.md`, mark step 1 as non-yielding using the new vocabulary,
   so the reader of that file does not have to derive it.

## Acceptance criteria

- [ ] `ground-rules.md` defines a non-yielding step and states that it shares a
      turn with the next step that asks a 👉 question.
- [ ] `ground-rules.md` no longer asserts that Step 1 ends on a 👉 question; the
      post-model-nudge instruction reads "the next single 👉 question" in both
      places it appears.
- [ ] `phase1-discovery.md` step 1 is marked non-yielding, and its checkpoint
      instruction is consistent with being written at the shared boundary.
- [ ] A walk that answers "no" to the model/effort switch at Discover the Business
      Problem produces one turn containing the privacy reminder and exactly one 👉
      (step 2's), violating neither INV-005 nor the one-step-at-a-time rule.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — define
  the non-yielding step; correct both post-nudge sentences.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` —
  mark step 1 non-yielding.

## Source

- Feedback: dry run phase 3, 2026-08-13 — hit on the reply turn after declining the
  model/effort switch at the start of Discover the Business Problem
  (`Source: self-observed (assistant retrospective)`)
- Priority: **High** — raised from Medium on 2026-08-13 after finding that
  `module-03-system-verification` has a single 👉 in the whole module, which makes
  its own gate-precedence "one step at a time" rule unimplementable end to end.
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none

## Deviations from this spec, and why (2026-08-14)

- **`module-03-system-verification` was fixed in place, which the Proposed change did not
  ask for.** The spec's Root cause devotes most of its length to that module — one 👉 in the
  whole of it, and three of its own instructions describing a mechanism it never provides —
  and then concludes that naming the concept centrally *is* the fix. It is not quite: a file
  that says "signal a stop by ending the turn on the single 👉 question" is still
  self-contradictory after the ground rules define the term, because the reader of that file
  has to infer the connection. So all three named instructions were repaired:
  `SKILL.md` (the module has one 👉; "one at a time" is about order, not turns),
  `phase1-verification.md`'s header (every step in the phase is non-yielding), and agent
  rule 10 (one write at the end of the turn instead of eleven inside it).
- **A partial-turn fallback was added that the spec does not mention.** Collapsing eleven
  checkpoint writes to the end of a turn means a turn that dies mid-run records nothing, which
  is worse for resume than the noise it replaced. Agent rule 10 now requires writing whatever
  completed before stopping.
- **Criterion 4 is not runtime-verified.** It describes a live walk ("a walk that answers no to
  the model/effort switch at Discover the Business Problem produces one turn containing the
  privacy reminder and exactly one 👉"). No live bootcamp runs in this environment, so what is
  asserted is that every instruction the walk follows now composes to that outcome. Recorded as
  implemented-but-not-runtime-verified rather than ticked.
