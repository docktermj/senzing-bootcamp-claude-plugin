# A host-rendered control prompt interrupts a pending 👉 question

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A bootcamper on plugin 0.5.0 was interrupted during the onboarding preface, with
`👉 Do you have any questions before we get started?` (`onboarding-flow.md:199`) pending and
unanswered, by the Claude Code host prompt:

> **Set up auto mode for your environment?** — "Set it up" / "Not now" / "Don't show again"

Their report: it "cost the bootcamper their place in the flow and caused confusion about whether
the prompt was part of the bootcamp itself — it was their impression that the guided flow 'knows
what it is doing,' and this was not the flow asking it."

**This is the second report of the same interruption in one day, on a fresh run.** The earlier
entry (2026-08-15 10:00, archived as
`feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK_1786803006.md`) produced
`specs/a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper.md` and INV-247. This one
was filed at 13:13 against a fresh bootcamp — same preface, same pending 👉, same prompt. It is a
recurrence, not a re-report.

⚠️ **The new entry settles what the first one left open, and the answer is not the one that
shipped.** The first entry said only that the bootcamper "was asked about 'auto-mode for the
bootcamp'" and its `Divergence` field guessed at the CLI harness. This entry quotes the dialog
verbatim, with its three native options — UI chrome the harness renders, not text a model emits.
The prompt was **host-rendered**, and the guide originated nothing.

## Root cause

Two parts. The first is an uncovered case; the second is a claim the plugin now ships that its
evidence does not support.

### 1. The shipped apparatus handles origination and solicitation, not interruption

INV-247's implementation covers two situations, and the reported one is neither:

| Case | Shipped handling |
|---|---|
| The guide **originates** a host-control question | Forbidden — `ground-rules.md:106-115` |
| The bootcamper **asks** about a host control | One-sentence answer, then re-present — `ground-rules.md:666-674` |
| **The host renders a control prompt unbidden, with a 👉 pending** | *nothing* |

The third row is what happened, twice. `:666` is explicitly conditioned on "**if the bootcamper
asks** about auto mode" — here they did not ask; a dialog appeared at them.

The generic recovery rule at `ground-rules.md:677-684` does formally reach it — "after **any**
interruption that left a 👉 question hanging" — but its enumeration names four interruptions ("a
compaction, a session boundary, the feedback detour, or the bootcamper going off on a tangent and
coming back") that are all *conversational* and all *visible to the guide*. A host dialog is
neither. This repo has already recorded that hazard against itself: INV-205's own maintenance note
describes a rule "generalised from one instance" whose enumeration "broke on the next, one workflow
step later".

### 2. `ground-rules.md` and the guard both assert a defect nobody has observed

`ground-rules.md:127-132` justifies INV-247 to the guide with:

> ⚠️ **Why this is a rule and not an assumption.** Observed 2026-08-15: a bootcamper **was asked**
> about "auto-mode for the bootcamp" during the onboarding preface […] No file in this plugin asks
> that.

`tests/test_no_host_control_is_offered_as_a_question.py:3-10` repeats it and goes further — "The
question came from outside the bootcamp's scripted flow, and nothing on the books forbade it".

Both read as: *the guide put a question to the bootcamper*. The verbatim dialog in this entry shows
it did not. Re-run at triage, `grep -rniE 'auto-mode|auto mode|auto-accept|permission mode|plan
mode|fast mode|bypass permissions'` across `plugins/`, `.claude/` and `tests/` returns matches
**only** in the INV-247 rule text and its guard — no plugin file asks it, and no run has now shown
the guide asking it either.

⚠️ **This is not a case for retracting INV-247.** The hazard it names is real and this entry
strengthens it: a bootcamper who has been asked to operate `/model` and `/effort` genuinely cannot
tell a host dialog from bootcamp content — that indistinguishability is the whole content of both
reports. INV-247 is sound prophylaxis. What is wrong is the *evidence line beneath it*, which
converts "a host prompt appeared and looked native" into "the guide asked an unsanctioned
question". A rule whose shipped citation overstates its instance is the pattern
`newly-minted-invariants-carry-no-shipped-citation` and
`coverage-reports-count-known-non-defects-as-hits` both exist to catch.

## What re-verification and analysis changed about the request

**The entry's suggested fix — "Never show the 'Set up auto mode?' prompt during a bootcamp
session" — is not available to this plugin, for the second time.** A plugin ships skills, hooks and
commands; none of those reach the host's UI. `ground-rules.md:671-672` already says so in shipped
prose, and `specs/a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper.md:56-67`
recorded the same refusal three hours earlier. Writing a suppression criterion would produce a
criterion nobody can meet.

**The entry's `Routing: unclear` is correct on its own terms and this spec does not overturn it.**
The prompt is authored by the Claude Code harness — neither the bootcamp plugin nor the Senzing MCP
server. What is routed `plugin` here is strictly the remainder: the recovery the bootcamp owes a
displaced 👉, and the accuracy of a citation the plugin ships.

## Proposed change

1. **Name the host interruption in the recovery enumeration** (`ground-rules.md:677-684`). Add the
   host-rendered prompt to the list of interruptions that leave a 👉 hanging, so the case does not
   depend on a reader generalising from four conversational examples:

   > […] a compaction, a session boundary, the feedback detour, a host-rendered prompt from their
   > Claude interface appearing over the bootcamp, or the bootcamper going off on a tangent and
   > coming back […]

2. **Widen the any-time-controls bullet from "asks about" to "raises"** (`ground-rules.md:666`). It
   must fire when the bootcamper mentions that a host prompt *appeared*, not only when they ask a
   question about a control. Same one-sentence answer, same re-presentation, same prohibitions
   already at `:670-674`.

3. **Correct the citation in both places that ship it**, to what the two entries jointly establish —
   a host-rendered prompt appeared over the bootcamp with a 👉 pending, and the bootcamper could not
   tell it from bootcamp content:
   - `ground-rules.md:127-132` — the ⚠️ "Why this is a rule and not an assumption" block.
   - `tests/test_no_host_control_is_offered_as_a_question.py:3-10` — the docstring.

   Keep the justification; it survives the correction intact, and arguably reads stronger, because
   the indistinguishability is now demonstrated rather than inferred. Drop only the implication that
   the guide asked.

4. **Record the correction on INV-247 as a dated clarification.** The MUST condition does not
   change — only the observation beneath it — so `INVARIANTS.md` rule 2 permits an in-place edit,
   in the house form: `(⚠️ **Observation corrected 2026-08-15, no meaning change.** …)`.
   ⛔ Requires the maintainer's explicit sign-off before it is written (`implement-spec` Step 5).

5. ⛔ **Add no claim that the plugin can suppress, dismiss or pre-empt a host prompt.** The scope
   limit above is to be recorded, not papered over — `ground-rules.md:671-672` already forbids the
   guide from claiming it, and this change must not contradict that line.

### Decided: the answer stays silent on "Don't show again"

The dialog offers **"Don't show again"**, which is a real remedy — but it belongs to the
bootcamper, not the bootcamp. The question was whether the one-sentence answer may *name* it.

⛔ **It may not.** Maintainer decision, 2026-08-15: the guide answers that it is their session
setting, the bootcamp neither needs nor recommends a value, and re-presents the pending 👉 — and
says nothing about how to dismiss the prompt. This is the conservative reading of
`ground-rules.md:670-671` ("do not offer to change it for them", "the bootcamp neither needs nor
recommends a value") and keeps INV-247's boundary exactly where it is: the module-start
model/effort switch remains the **only** Claude-interface control the bootcamp directs the
bootcamper to operate. Naming a dismissal control would make it a second one by implication.

The cost is accepted knowingly — the interruption may be reported a third time, and the plugin's
answer will still be "that is yours, not ours". That is the correct answer even when it is not the
satisfying one.

## Acceptance criteria

- [ ] The recovery rule's interruption list names a host-rendered prompt appearing over the
      bootcamp, so the case is not left to generalisation from conversational examples.
- [ ] The any-time-controls host-control bullet fires when the bootcamper **raises** a host control
      in any form, not only when they ask a question about one.
- [ ] Neither `ground-rules.md` nor the guard docstring states or implies that the guide asked the
      bootcamper about auto mode; both describe a host-rendered prompt.
- [ ] INV-247's MUST condition is byte-identical after the edit — only its parenthetical
      observation changes, and the maintainer approved the wording.
- [ ] No shipped file gains a claim that the plugin can suppress or dismiss a host control.
- [ ] The host-control answer does **not** name "Don't show again" or any other dismissal
      affordance — per the decision above, the model/effort switch stays the only Claude-interface
      control the bootcamp directs the bootcamper to operate.
- [ ] A test asserts the corrected citation and the widened trigger, scoped to their owning sections
      (INV-183) — **negative-controlled**, mutation verified to land, then reverted.
- [ ] ⛔ Not verifiable by this or any test, and MUST NOT be claimed by one: whether a guide actually
      re-presents the pending 👉 after a host dialog interrupts. The guide may never observe the
      dialog at all — if the bootcamper clicks "Not now", nothing enters the conversation — so the
      recovery fires only when they mention it. Static checks read files; this is `dry-run` phase 3
      territory, and even there it is reachable only by simulating the mention.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:677-684` the
  interruption list; `:666` the trigger widening; `:127-132` the corrected observation.
- `tests/test_no_host_control_is_offered_as_a_question.py` — docstring correction, plus assertions
  for criteria 1–3.
- `specs/INVARIANTS.md` — INV-247's parenthetical observation only, maintainer-approved.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Suppress the 'Set up auto mode?'
  host prompt during the bootcamp" (2026-08-15, Module General — onboarding preface;
  `Source: bootcamper-reported`)
- Priority: **Medium** (filed **High**). The High rating attached to the suppression request, which
  is unavailable to a plugin. What remains plugin-owned — recovery wording and citation accuracy —
  is real but narrower. The recurrence within one day is the argument against filing it lower.
- MCP re-check: **n/a (no Senzing fact).** The entry asserts nothing about Senzing, the SDK or the
  MCP server; it concerns a Claude Code harness prompt and the bootcamp's interaction layer, so
  there is no server fact to re-verify and no absence claim about the server to substantiate.
  `get_capabilities` was called once at triage to date the run: server **1.32.9**, 2026-08-15.
- Upstream: not applicable — not a Senzing MCP server defect. ⛔ Note there is **no** upstream
  channel for this finding: `submit_feedback` reaches Senzing, and the prompt is authored by the
  Claude Code harness, so filing it there would misroute a report to a party that does not own it.
- Related specs: `a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper` (the first
  report of this interruption; established INV-247),
  `host-control-handling-clause-can-be-read-as-two-questions-in-one-turn` (the same clause's turn
  boundary), `inv247-guard-is-narrower-than-the-invariant-it-enforces` (the guard's two disclosed
  limits), `newly-minted-invariants-carry-no-shipped-citation`,
  `coverage-reports-count-known-non-defects-as-hits`, and INV-005, INV-007, INV-183, INV-247.
