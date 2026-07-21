# Mark the boundary between the bootcamp flow and the feedback flow

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

When a bootcamper submits feedback mid-bootcamp, the feedback workflow's
questions and answers run inline in the same transcript as the bootcamp's own
questions and answers, with no visual distinction between the two. It is hard to
tell when feedback collection starts and when it ends and control returns to the
bootcamp.

> "Bootcampers need to easily switch their mental context between the bootcamp
> and the feedback workflow, and back again."

Suggested fix: a visible border/banner when feedback collection starts and when
it ends (e.g. "Feedback submitted — back to the bootcamp").

## Root cause

Not a defect — no entry/exit marker is specified. The feedback workflow in
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` moves straight
from context capture (Step 0, `:13-31`) into the 👉 questions (Step 2, `:48-60`)
and, at the end, "returns the bootcamper to exactly where they left off"
(Step 4, `:112-116`) — but with no visual banner opening or closing the
workflow. `ground-rules.md:151-155` (the "Bootcamp feedback" any-time control)
likewise specifies the behavior without any boundary marker.

No invariant currently mandates such a marker (INV-010 allows feedback anytime;
INV-015 requires it be captured), so this is a new UX affordance. It is
consistent with the bootcamp's established use of banners as bookends — WELCOME
(INV-022), GRADUATION (INV-047), and the END OF SENZING BOOTCAMP terminal banner
(INV-057).

## Proposed change

Bracket the feedback workflow with a clear entry banner and a clear exit
marker, matching the bootcamp's banner visual language:

- **Entry:** when the feedback workflow begins (triggered by the
  `UserPromptSubmit` hook, the `/bootcamp-feedback` command, or a "bootcamp
  feedback" utterance), present a pinned entry banner (e.g. "BOOTCAMP FEEDBACK")
  before the first 👉 feedback question, signaling the bootcamper has left the
  bootcamp flow.
- **Exit:** after the entry is confirmed saved (`feedback.md` Step 3b/Step 4),
  present a pinned closing marker (e.g. "Feedback submitted — back to the
  bootcamp") before resuming the pending bootcamp step, signaling control has
  returned.
- **Preserve the resume contract.** The exit marker is a statement, not a
  question; after it, re-present the exact pending 👉 bootcamp question the
  bootcamper was on (INV-006 ask-once, INV-005 exactly one 👉 per yielding turn).
  The feedback questions and the resumed bootcamp question must not collide into
  one turn.
- Pin the banner/marker wording verbatim in `feedback.md` (INV-056 style) so it
  does not drift, and note the affordance in `ground-rules.md`'s any-time
  "Bootcamp feedback" control.

## Acceptance criteria

- [ ] A distinct, pinned entry banner appears when the feedback workflow starts,
      before its first 👉 question.
- [ ] A distinct, pinned exit marker appears when the feedback workflow ends and
      control returns to the bootcamp, before the pending bootcamp step resumes.
- [ ] The exit marker is a statement (not a 👉 question); the bootcamper is
      returned to exactly the pending 👉 question they left (INV-006), with
      exactly one 👉 ending that yielding turn (INV-005).
- [ ] The banner/marker wording is pinned verbatim in `feedback.md` and cannot
      drift at runtime.
- [ ] The markers are purely visual and do not alter what feedback is captured
      (INV-015) or where (`docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — add the pinned entry banner before Step 2 and the pinned exit marker in Step 4 (`:48-60`, `:112-116`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — note the entry/exit markers in the any-time "Bootcamp feedback" control (`:151-155`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Mark the boundary between bootcamp flow and feedback flow" (2026-07-17, Module General/Onboarding)
- Priority: Medium
- Related specs: `specs/end-of-bootcamp-banner.md` (banner-as-bookend precedent); `specs/enrich-feedback-context.md` and `specs/feedback-file-durability.md` (feedback content/durability, distinct concerns).

## Invariants introduced

- `INV-074` — The feedback workflow MUST be bracketed by pinned-verbatim banners (a "BOOTCAMP
  FEEDBACK" entry banner before the first 👉 question, and a "FEEDBACK SAVED — BACK TO THE
  BOOTCAMP" exit banner before the pending bootcamp 👉 question resumes). Recorded in
  `specs/INVARIANTS.md` (maintainer-approved).
