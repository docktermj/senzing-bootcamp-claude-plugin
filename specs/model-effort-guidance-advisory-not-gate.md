# Demote the model/effort switch from a blocking two-gate dance to a one-line advisory

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At the start of Data processing, the INV-063 nudge fired as a blocking yes/no question:

> 👉 **Would you like to switch to Sonnet 5 at high reasoning effort for this module?**

The bootcamper found it clunky and asked for a better way to optionally change model and effort. They
did not answer it — they filed feedback instead, which is itself evidence the question landed poorly.

**The core objection: the plugin is asking permission for something it cannot do.** Only the bootcamper
can change the model or effort. On "yes" there is no action for the assistant to take except *wait* —
which is precisely why the design needs a second blocking gate:

> 👉 **Are you done modifying the model and effort?**

So an accepted switch costs **two extra round-trips before any module work begins**. It is a
notification implemented as a decision.

Contributing problems the bootcamper enumerated:

1. **Two settings bundled into one yes/no.** Model and effort are independent dials; "yes" does not say
   whether both were changed.
2. **It recurs.** The gate fires whenever the recommendation *changes*, so a Core run hits the same
   question repeatedly with different nouns.
3. **Blocking buys nothing.** Model/effort can be changed mid-module at any time with no penalty, so
   stopping at the module boundary adds friction without adding safety.
4. **The current setting is never named,** so the bootcamper cannot see the comparison they are being
   asked to judge — the single most useful piece of information is missing.
5. **A downgrade is presented in the same neutral tone as an upgrade.** Here it offered a step *down*
   from Opus 5 to Sonnet 5 with no signal that it was a downgrade.

Their summary of the cost: two round-trips to change a setting they could change unprompted, repeated
across a run, "trains them to reflexively answer 'no' and stop reading the apparatus block entirely.
That is the opposite of the intent."

## Root cause

**Confirmed. The blocking design is mandated by two invariants, not by an implementation slip.**

`ground-rules.md:245-271` implements exactly what the bootcamper describes:

- `:245-246` — on a changed recommendation, "end the turn with a **single** 👉 yes/no question offering
  the switch, and do NOT also show Step 1 this turn".
- `:250` / `:255` — the pinned switch question (CLI and non-CLI surface variants).
- `:263` — the pinned second gate: "👉 **Are you done modifying the model and effort?**"
- `:265-266` — "Step 1 comes on the turn **after** the bootcamper confirms."
- `:270-271` — "You never change the session yourself — only the bootcamper can." The skill states the
  premise that makes the gate pointless, and gates anyway.

Duplicated in `graduation/SKILL.md:91, 99`. Referenced at module start by **10 skill files**
(`ground-rules.md` plus 9 module skills).

**This is an invariant conflict, and the spec must be implemented as an invariant supersession, not a
silent override.** The blocking behavior *is* the invariant:

- **INV-063** — "When the recommendation **changes** from the current stage, it MUST pause with a single
  👉 yes/no question offering the switch — its own yielding turn."
- **INV-069** — "MUST end that reply turn on a single confirmation gate whose wording is pinned verbatim
  (INV-056) — '👉 Are you done modifying the model and effort?' … and MUST defer the stage's first step
  to the turn after the Bootcamper confirms."

Per @INVARIANTS.md's maintenance rules, these may not be deleted or edited into a new meaning: a change
of meaning is a **new invariant with a new ID** that marks the old ones superseded. There is direct
precedent in this very chain — INV-062 (non-blocking nudge, never a 👉 question) was superseded by
INV-063, and INV-064 was superseded by INV-069.

**Maintainer decision required.** That chain shows the design has oscillated, and it oscillated because
of *bootcamper requests in both directions*: `specs/model-effort-change-prompt.md` added the blocking
question, and `specs/model-effort-switch-done-confirmation.md` added the done-modifying gate — both at
bootcampers' explicit request. This feedback asks to remove both. Two bootcampers want opposite things,
so a straight revert will simply re-open the earlier report. **The bootcamper's own suggestion #6
resolves it, and is why this spec recommends it rather than a plain revert.**

## Proposed change

**Ask the preference once, then honor it.** This is the load-bearing change: it satisfies both camps
instead of picking one, and it replaces N per-module questions with one per-run question — which is
what INV-006's ask-once principle intends.

1. **One question in Bootcamp preparation**, alongside the other preferences captured there:

   > 👉 **How would you like model guidance handled? Reply with a number:**
   > 1. A one-line recommendation at each module (recommended)
   > 2. Don't show it
   > 3. Stop and ask me each time

   Persist as `model_guidance: advisory | off | prompt` in `config/bootcamp_preferences.yaml`. Default
   to `advisory` when the preference is absent (older sessions, or preparation skipped) so no run is
   left without guidance.

2. **`advisory` (the default) — one line, no question, no gate.** Fold it into the module-start
   apparatus block beside the time estimate, then continue straight into Step 1 in the same turn:

   > **Recommended here:** Sonnet 5 · high effort — you're on **Opus 5**, which is stronger; staying is
   > fine. Change anytime; it takes effect on your next message.

   Requirements for that line:
   - **Always name the current model/effort** next to the recommendation, so the comparison is visible
     and can be dismissed with confidence. This fixes objection 4 and is worth doing regardless of the
     rest.
   - **State "change anytime."** It is true, and it removes the false impression that the module
     boundary is the only opportunity.
   - **Flag direction explicitly** when the recommendation is *below* the current setting, and say why a
     carve-out may not apply (e.g. Data processing's "Opus if bespoke load code"). This fixes objection
     5 and prevents the nudge from ever reading as advice to downgrade.
   - **Name model and effort separately**, since they are independent dials (objection 1).
   - Adapt to the Claude surface per INV-098 — exact `/model`/`/effort` commands on the CLI, intent-based
     phrasing elsewhere.

3. **`off`** — show nothing at module start. The bootcamper opted out; respect it.

4. **`prompt`** — keep today's INV-063/INV-069 behavior exactly as specified, including both pinned
   gates. This is what preserves the earlier bootcampers' requested experience and keeps
   `specs/model-effort-change-prompt.md` and `specs/model-effort-switch-done-confirmation.md` satisfied
   rather than reverted.

5. **Delete the "👉 Are you done modifying the model and effort?" gate from the non-`prompt` paths**
   (`ground-rules.md:263`, `graduation/SKILL.md:99`). It exists only to service the blocking behavior;
   with no block there is nothing to wait for.

6. **Record the invariant change properly.** Add a new invariant stating that module/graduation-start
   model/effort guidance is advisory by default, blocking only when the bootcamper selected `prompt`,
   and always names the current setting and the direction of change. Append `(Superseded by INV-NNN)` to
   INV-063 and INV-069 rather than editing them. Note that this partially restores INV-062's original
   non-blocking intent.

7. **Apply once, inherit everywhere.** The nudge is referenced by `ground-rules.md` and 9 module skills;
   the behavior must live in `ground-rules.md` alone so the module skills need no per-file edit beyond
   their existing reference.

**Sequencing:** `specs/refresh-model-guidance-to-current-top-tier-model.md` edits many of these same
lines. Implement one, then the other — whichever is scheduled first — and do not rewrite the same lines
twice. The advisory line's example text should carry the *current* top-tier model, not Opus 4.8.

## Acceptance criteria

- [ ] Bootcamp preparation asks one pinned 👉 question capturing `model_guidance`, persisted to
      `config/bootcamp_preferences.yaml`; absent preference defaults to `advisory`.
- [ ] Under `advisory`, module start and graduation start cost **zero** extra turns: the recommendation
      appears in the apparatus block and Step 1 lands in the same turn.
- [ ] The advisory line always names the **current** model and effort alongside the recommendation,
      names model and effort as separate dials, states "change anytime", and explicitly flags a
      recommendation that is *below* the current setting as a downgrade.
- [ ] Under `off`, no model/effort output appears at module start.
- [ ] Under `prompt`, today's INV-063/INV-069 behavior is reproduced exactly, both pinned gates included
      and verbatim (INV-056).
- [ ] The "Are you done modifying the model and effort?" gate no longer appears on the `advisory` or
      `off` paths, in either `ground-rules.md` or `graduation/SKILL.md`.
- [ ] A new invariant records the advisory-by-default rule; INV-063 and INV-069 are marked superseded in
      place, neither deleted nor renumbered, per @INVARIANTS.md's maintenance rules.
- [ ] The behavior lives in `ground-rules.md`; the 9 module skills need no change beyond their existing
      INV-063 reference, and none contradicts the new default.
- [ ] Surface-aware phrasing (INV-098) is preserved on every path.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): interaction
      and wording only, with no platform- or language-specific behavior.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — lines ~240-306: the nudge
  branch, both pinned gates, and the follow-on description at ~304
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — lines ~81-99: same flow at graduation start
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — add the one-time `model_guidance`
  question
- `plugins/senzing-bootcamp/docs/model-selection.md` — describe the three modes and where the preference
  lives
- `specs/INVARIANTS.md` — append the new invariant; mark INV-063 and INV-069 superseded in place
- The 9 module skills referencing INV-063 (`module-01` … `module-07`, `module-03b`) — verify no local
  restatement contradicts the new default

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Replace the blocking model/effort switch gate
  with a one-line advisory" (2026-07-24, General — INV-063 module-start apparatus)
- Earlier related reports: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_04.md` → "Model-switch flow ended a turn
  without a closing question" and "Model/effort switch flow is a recurring two-turn dance (repeat of
  earlier report)" (2026-07-16) — both already addressed by the specs below; this item revisits the same
  friction from the opposite direction
- Priority: Medium
- Related specs: `specs/model-effort-change-prompt.md` (added the blocking question, INV-063),
  `specs/model-effort-switch-done-confirmation.md` (added the second gate, INV-069),
  `specs/model-switch-single-turn-continuation.md` (INV-064, superseded),
  `specs/module-start-model-nudge.md` (INV-062, the original non-blocking design),
  `specs/surface-aware-model-effort-instructions.md` (INV-098),
  `specs/refresh-model-guidance-to-current-top-tier-model.md` (**same lines — check sequencing**),
  `specs/module-preface-time-estimate.md` (the apparatus block this line joins)
