# Bootcamper request: add a "done modifying model/effort?" pause after an accepted switch

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement — **but see "Conflict with invariants" below: this request directly contradicts INV-064 and requires a maintainer decision before implementation.**

## Problem

After the module-start offer "👉 Would you like to switch to /model opus + /effort
high for this module?", when the bootcamper answers **yes**, the guide continues
into the module in the same turn (a one-line run-commands statement immediately
followed by Step 1, ending on Step 1's 👉 question). The bootcamper — who must run
`/model` and `/effort` themselves, which takes a moment — asked for an explicit
extra gate after "yes":

> "👉 Are you done modifying the model and effort?"

so there is a clear window to finish switching before the module proceeds. The
feedback explicitly notes this is "a design-change request, not a defect."

## Root cause

Working as currently designed. The accepted-switch continuation is governed by
`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
("Best-value model/effort prompt" / "After an affirmative module-transition") and
mirrored at `plugins/senzing-bootcamp/skills/graduation/SKILL.md`. That flow was
**deliberately** shaped by `specs/model-switch-single-turn-continuation.md` to
land Step 1 on the reply turn with **no** separate confirmation gate — which is
now the invariant INV-064.

Note the current flow already yields to the bootcamper: the "yes" turn ends on
Step 1's 👉 question, so the module does not advance until the bootcamper responds
— they can run `/model` and `/effort` during that yield. The bootcamper's concern
is that this window is not *labelled* as a switch-confirmation, so it reads as "the
module proceeds immediately."

## Conflict with invariants (decision required)

This request is the **direct opposite** of a change already made from earlier
bootcamper feedback:

- **INV-064** — "When the Bootcamper accepts a recommended model/effort switch …
  the guide MUST continue the accepted path in a **single** turn … It MUST NOT
  insert a separate confirmation-only gate between the switch and the first step
  …". The requested "👉 Are you done modifying the model and effort?" is exactly
  the separate confirmation-only gate INV-064 forbids.
- `specs/model-switch-single-turn-continuation.md` established INV-064 specifically
  to *remove* this gate after two prior bootcampers found the "two-turn dance"
  (switch offer → separate "ready to start?" confirmation → Step 1) clunky.

So adopting this request would **reverse** a deliberate, feedback-driven decision
and require **superseding INV-064** (new invariant ID; INV-064 marked superseded
per the INVARIANTS.md maintenance rules). It would also re-open the friction the
earlier reports raised. Per the feedback-to-specs guardrails, this is surfaced —
not silently implemented.

## Options for the maintainer

1. **Decline (keep INV-064).** The current single-turn continuation already yields
   (Step 1's 👉) and gives the bootcamper a window; the earlier feedback favored
   removing the extra gate. No code change. Optionally soften the run-commands
   statement so the yield reads more clearly as "take your time switching, then
   answer below."
2. **Adopt the gate (supersede INV-064).** Add, on "yes", a single pinned
   👉 confirmation ("👉 Are you done modifying the model and effort?") on its own
   yielding turn, then present Step 1 on the following turn. Requires: edit
   `ground-rules.md` and `graduation/SKILL.md`; pin the exact wording (INV-056);
   keep the switch-offer question its own turn (INV-063); write a new invariant
   superseding INV-064; update `docs/model-selection.md` for consistency (INV-003).
3. **Compromise (no new gate).** Keep the single turn but reword the "yes"
   continuation statement to explicitly grant the switching window before Step 1's
   question (e.g. "Run `/model …` then `/effort …` now — take your time; when
   you're set, answer the question below."). Satisfies the bootcamper's intent
   without a second gate, and stays within INV-064 (arguably a clarification, not a
   change — confirm it does not cross into a "confirmation gate").

## Acceptance criteria

*(Apply only if the maintainer chooses Option 2 or 3.)*

- [ ] If Option 2: on "yes", the guide asks exactly one pinned 👉 confirmation on
      its own yielding turn before Step 1; the switch-offer question remains its own
      turn (INV-063); INV-064 is superseded by a new invariant recorded in
      `specs/INVARIANTS.md`.
- [ ] If Option 3: the "yes" continuation statement explicitly grants the switching
      window before Step 1's 👉, with no separate confirmation-only gate, and INV-064
      still holds.
- [ ] `ground-rules.md`, `graduation/SKILL.md`, and `docs/model-selection.md`
      describe the accepted-switch continuation consistently (INV-003).
- [ ] Every 👉 question stays unambiguous yes/no (INV-008) with pinned wording
      (INV-056); one 👉 per yielding turn (INV-005/INV-054).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per
      @INVARIANTS.md).

## Affected files

*(Options 2/3 only.)*

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the "yes"
  continuation in the model/effort switch flow.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — same continuation at the
  graduation switch.
- `plugins/senzing-bootcamp/docs/model-selection.md` — keep the mirrored
  description consistent.
- `specs/INVARIANTS.md` — Option 2 only: append a new invariant superseding INV-064.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add a \"done modifying
  model/effort?\" confirmation after the model-switch offer" (2026-07-17, Module:
  General — module-start model/effort switch prompt)
- Priority: Medium
- Related specs: `model-switch-single-turn-continuation.md` (INV-064 — this request
  contradicts it), `model-effort-change-prompt.md` (INV-063 — the switch offer),
  `module-start-model-nudge.md`, `onboarding-explore-gate-wording.md` (INV-056 —
  pinned wording if a new gate is added).

## Decision (2026-07-17)

Maintainer chose **Option 2 — adopt the gate** (supersede INV-064). Implemented:
on an accepted switch the guide runs the `/model`/`/effort` statement, then ends
the turn on the pinned gate "👉 Are you done modifying the model and effort?", with
the stage's first step deferred to the turn after the Bootcamper confirms; on a
declined switch the first step stays on the reply turn with no gate. INV-064 is
marked superseded by the new INV-069.

## Invariants introduced

- `INV-069` — When the Bootcamper accepts a recommended model/effort switch at a
  module start or graduation start, the guide MUST end that reply turn on a single
  confirmation gate whose wording is pinned verbatim (INV-056) — "👉 Are you done
  modifying the model and effort?" — presented after the one-line `/model`/`/effort`
  run-commands statement, and MUST defer the stage's first step to the turn after
  the Bootcamper confirms; the gate is asked once (INV-006) and the switch-offer
  question remains its own prior yielding turn (INV-063). On a declined switch the
  first step lands on the reply turn with no gate. (Supersedes INV-064; recorded in
  `specs/INVARIANTS.md`.)
