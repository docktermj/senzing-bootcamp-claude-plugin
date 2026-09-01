# feedback.md Step 2 has no case for a partial feedback report

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Step 2 lists five questions to ask "each as its own turn", then names exactly one shortcut:

> If the bootcamper gives everything in one message, do not re-ask: confirm what you captured and
> proceed.

Real feedback usually arrives **partially** complete. Observed live on 2026-08-31, a bootcamper
opened with:

> bootcamp feedback: For the "👉 How would you like to define the business problem? Reply with a
> number:" question, add another option for showing additional examples of common business problems
> that entity resolution can solve

That single message answers question 1 (what it is about), question 2 (what happened) and
question 4 (a suggested fix), and leaves 3 (why it matters) and 5 (priority) open. Step 2 covers
neither "all five" nor "none", so the guide must choose between two readings that diverge badly:

- **Literal** — ask all five in order, which **re-asks three questions the bootcamper just
  answered**. INV-006 forbids exactly this, and it is most galling in the feedback flow, where the
  bootcamper is already spending goodwill to report a problem.
- **Sensible** — ask only the unanswered ones. Correct, but the guide has to derive it, and a guide
  reading the ⛔-dense files literally has been trained to follow them literally.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md`:

Step 2's shortcut clause is written as an all-or-nothing test ("gives
  **everything** in one message"), so the partial case falls through to the default of asking all
  five. The sibling any-time-control workflow gets this right and states it explicitly:
  `notes.md` carries ⛔ *"Do not ask what they want to note when they already said it"* (INV-006).
  Two workflows of the same shape, one of which names the rule and one of which does not.
## Proposed change

Rewrite Step 2's shortcut clause to cover partial answers. Wording along the lines of: *"Ask only
   the questions the bootcamper has not already answered. Anything their message already supplies —
   in whole or in part — is captured, not re-asked (INV-006); confirm what you captured in one line
   and ask only the gaps, one 👉 per turn."* This subsumes the existing "gives everything" case
   rather than sitting beside it.

## Acceptance criteria

- [ ] `feedback.md` Step 2 states that only unanswered questions are asked, and the "gives
      everything in one message" case reads as an instance of that rule rather than a separate one.
- [ ] A feedback message supplying some but not all of the five fields results in only the missing
      fields being asked — no question the bootcamper already answered is re-asked (INV-006).
- [ ] No question in `feedback.md` Step 2 acquires an INV-056 pin as part of this change — they are
      not pinned today and this spec does not make them so.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — Step 2: rewrite the shortcut
  clause.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Discover the Business Problem
  (`Source: self-observed (assistant retrospective)`) — surfaced by the maintainer submitting a
  genuine partial feedback report in character during the walk.
- Priority: Medium
- MCP re-check: n/a (no Senzing fact) — both defects are in the plugin's own interaction
  specification.
- Upstream: not applicable
- Related specs: `specs/three-numbered-questions-render-their-options-inline.md` (found in the same passage; split out because it is a different root cause with a wider blast radius)
