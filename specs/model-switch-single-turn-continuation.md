# Collapse the accepted model/effort switch into one clean continuation turn

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two bootcamper reports, both about what happens **after** the model/effort switch
offer is accepted (the offer itself, INV-063, works as intended):

1. **Module 1→2 boundary — turn ended on a bare statement, no 👉.** After the
   bootcamper answered "yes" to the switch, the guide told them to run the two
   commands and closed the turn with a plain statement ("Let me know once you've
   switched and I'll kick off Module 2") instead of a 👉 question. The bootcamper
   noticed the turn yielded with no question and asked, *"Why aren't you asking me a
   question at this point?"* This violates the one-👉-per-yielding-turn contract
   (INV-005) and the Stop-hook safety net (INV-054).

2. **Module 4→5 boundary — recurring two-turn dance.** This time the guide *did*
   end the turn on a 👉 ("Ready to start Module 5 once you've switched?"), so a
   closing question was present — but the bootcamper reported the friction recurs at
   every switch point: accepting the switch costs **two** guide turns (turn 1 =
   offer the switch; turn 2 = tell them to run `/model`/`/effort` **and** ask a
   separate "ready to start?" confirmation). That extra confirmation gate is a
   decision-free question and reads as clunky. Reported as a repeat of item 1.

The two reports are two faces of the same defect: the accepted-switch path is an
under-specified extra turn, and every way the model fills it is wrong — either a
bare statement (no 👉, item 1) or a redundant confirmation gate (item 2).

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:170-206`
("Best-value model/effort prompt" + "After an affirmative module-transition")
specifies the switch **offer** precisely but leaves the accepted continuation
ambiguous and one turn too long:

- `ground-rules.md:179-180` — on **yes**, "tell the bootcamper to run those two
  commands and **continue once they confirm** … **Produce Step 1 on the next
  turn.**" "Continue once they confirm" invites a confirmation gate; "Produce Step 1
  on the next turn" forces Step 1 into a *third* turn (transition question → switch
  offer → confirm → Step 1). The intervening turn has no legitimate 👉 to end on —
  there is no real decision left — so the model either drops the 👉 (item 1) or
  invents a redundant "ready?" gate (item 2).
- `ground-rules.md:202-206` — the "After an affirmative module-transition" sequence
  says Step 1 "follows after the reply" for the change-stage case, which is what
  strands the accepted-switch turn with nothing to ask.

The same wording is mirrored at graduation:
`plugins/senzing-bootcamp/skills/graduation/SKILL.md:41` — "have the bootcamper run
those two commands and **continue once they confirm**" — so the defect recurs at
graduation start as well.

This is a refinement of, not a duplicate of, `model-effort-change-prompt.md`
(INV-063), which established the switch **question**. INV-063 constrains only that
question (its own yielding turn, never combined with another 👉); it says nothing
about the accepted continuation, which is where this defect lives. INV-063 is
preserved unchanged by this fix.

## Proposed change

Make the accepted ("yes") path a **single continuation turn** that ends on Step 1's
own 👉 question — no separate confirmation gate, no deferring Step 1 to a further
turn. The banner, journey map, before/after, and step overview were already shown in
the switch-offer turn, so the continuation turn only needs the run-commands
instruction plus Step 1.

Rewrite `ground-rules.md:170-206` so the change-stage flow is exactly:

- **Turn A (switch offer):** banner + journey map + before/after + step overview,
  ending on the single 👉 switch question (unchanged — this is INV-063).
- **Turn B (the reply, either answer):** produce Step 1, ending the turn on Step 1's
  single 👉 question.
  - On **yes**: open with a one-line **statement** telling the bootcamper to run
    `/model …` then `/effort …` and that the guide will pick up from their answer to
    Step 1 — then present Step 1. Do **not** add a "ready to start?" confirmation
    gate; running the commands and answering Step 1 *is* the go-ahead.
  - On **no**: acknowledge, then present Step 1.

So entering a change-stage module costs exactly the switch-offer turn plus one Step 1
turn, symmetric across yes/no. Update `ground-rules.md:179-180` (drop "continue once
they confirm" / "Produce Step 1 on the next turn"; replace with "present Step 1 this
turn, ending on Step 1's 👉 question; do not add a confirmation gate") and
`ground-rules.md:202-206` (the change-stage branch produces Step 1 on the reply turn,
not a turn later).

Apply the identical change at `graduation/SKILL.md:41`: on "yes", tell the
bootcamper to run the commands and proceed straight into the first graduation step,
ending that turn on its 👉 question — no "ready to start graduation?" gate.

Keep `docs/model-selection.md:85-89` in sync (it references ground-rules.md as the
source of truth; adjust its one-line description if it implies a confirmation turn).

No invariant is amended: INV-063 (switch question is its own yielding turn) and
INV-005/INV-054 (every yielding turn ends on exactly one 👉) both hold and are, in
fact, what this fix enforces on the previously-ambiguous continuation turn.

## Acceptance criteria

- [ ] On "yes" to the switch, the guide's next turn opens with a plain statement to run `/model …` + `/effort …`, then presents Step 1 and ends on Step 1's single 👉 question — it never ends on a bare statement with no 👉 (fixes item 1).
- [ ] The accepted-switch path never inserts a separate confirmation-only gate (e.g. "ready to start Module N once you've switched?") between the switch and Step 1 (fixes item 2).
- [ ] The "yes" and "no" branches both produce Step 1 in the turn immediately following the switch-offer turn; entering a change-stage module costs exactly two guide turns after the module-transition question, regardless of the answer.
- [ ] INV-063 is preserved: the switch question remains its own yielding turn, never combined with another 👉, and the guide never runs `/model`/`/effort` itself.
- [ ] Graduation start applies the identical single-turn continuation (`graduation/SKILL.md`): no "ready to start graduation?" gate after an accepted switch.
- [ ] `ground-rules.md`, `graduation/SKILL.md`, and `docs/model-selection.md` describe the accepted-switch continuation consistently (INV-003), with no residual "continue once they confirm" / "Produce Step 1 on the next turn" wording.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — rewrite the "yes" continuation in "Best-value model/effort prompt" (`:170-192`) and the change-stage branch of "After an affirmative module-transition" (`:202-206`) so Step 1 is produced on the reply turn, ending on Step 1's 👉, with no confirmation gate.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — apply the same single-turn continuation at the graduation switch (`:41`).
- `plugins/senzing-bootcamp/docs/model-selection.md` — keep the mirrored description (`:85-89`) consistent; ensure it does not imply a confirmation turn.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Model-switch flow ended a turn without a closing question" (2026-07-16, Module 2) and "Model/effort switch flow is a recurring two-turn dance (repeat of earlier report)" (2026-07-16, Module 5).
- Priority: Medium.
- Related specs: `model-effort-change-prompt.md` (INV-063, the switch question — refined here, not duplicated); `module-start-model-nudge.md`; `stop-hook-false-positive.md` (INV-054, the closing-question safety net item 1 tripped).

## Invariants introduced

- `INV-064` — When the Bootcamper accepts a recommended model/effort switch at a module start or graduation start, the guide MUST continue the accepted path in a **single** turn: a one-line statement instructing the `/model`/`/effort` commands, immediately followed by the stage's first step, ending that turn on that step's single 👉 question; it MUST NOT insert a separate confirmation-only gate between the switch and the first step, and MUST NOT defer the first step to a later turn. (Hardens INV-005/INV-054 for the accepted-switch continuation; complements INV-063.) (Recorded in `specs/INVARIANTS.md`, 2026-07-16.)
