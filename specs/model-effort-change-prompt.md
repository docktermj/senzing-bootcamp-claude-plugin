# Pause with a 👉 question when the recommended model/effort changes

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At each module start the bootcamp surfaces the best-value model/effort
recommendation as a non-blocking statement (e.g. "for best value, switch up:
`/model opus` then `/effort high`") and then continues immediately — straight into
the module's first question. Because it is a passing statement, the bootcamp moves
on before the bootcamper has a dedicated moment to run `/model` and `/effort`. A
bootcamper reported that they switched to Opus only because they paused themselves,
and asked for an explicit prompt so the switch happens before the heavier work
begins.

## Root cause

This is by design — and it conflicts with a current invariant. `ground-rules.md` →
"Module start banners and transitions" defines the best-value nudge as "a STATEMENT
— never a 👉 question, never a ⛔ gate, never blocks progress," and `INV-062`
codifies exactly that ("MUST surface … as a concise, non-blocking suggestion …
never as a 👉 question or ⛔ gate, and never blocking progress"). The feedback asks
for the opposite: a blocking 👉 question. **This cannot be implemented without
amending INV-062** (see Invariant impact).

## Proposed change

Turn the nudge into an *optional pause* at the points where switching actually
matters, without breaking the one-👉-per-turn rule:

- When the recommended model/effort **changes** from the current stage (entering
  Module 2 or 5, or graduation, or stepping back down), end that module-start turn
  with a **single** 👉 yes/no question — its own yielding turn, not combined with
  the module's Step 1 question:

  > 👉 **Would you like to switch to `/model opus` + `/effort high` for this module?** (Recommended for best value; reply no to keep your current model.)

  On "yes", tell them to run the two commands and continue once they confirm; on
  "no", proceed. The guide still never changes the session itself — it only prompts.
- When the recommendation is **unchanged** from the stage just completed, keep it a
  brief non-blocking statement (or omit) — no question, so the bootcamp does not ask
  a pointless "switch?" every module (INV-012).
- The module's Step 1 👉 question then follows in the next turn, preserving exactly
  one 👉 per yielding turn (INV-008/INV-009/INV-051). Update the "After an
  affirmative module-transition" sequence so that, on a change-stage, the turn ends
  at the switch question and Step 1 comes after the reply.

## Invariant impact

This **amends `INV-062`**, which currently forbids the nudge from being a 👉
question or blocking. Recording the change requires maintainer sign-off. Proposed
amended wording:

> `INV-062` (amended) — At every module start and graduation start, the guide MUST
> surface the recommended session model and reasoning effort with the exact
> `/model`/`/effort` commands. When the recommendation **changes** from the current
> stage it MUST pause with a **single** 👉 yes/no question offering the switch (its
> own yielding turn, never combined with another 👉 question); when unchanged it
> remains a concise, non-blocking statement. The guide MUST never change the session
> itself and MUST never block beyond that one optional question. The specific
> per-stage model/effort values remain advisory (`docs/model-selection.md`).

## Acceptance criteria

- [ ] When the recommended model/effort differs from the stage just completed, the module-start turn ends with a single 👉 yes/no question offering the switch, and no other 👉 question shares that turn (INV-008/INV-009/INV-051).
- [ ] When the recommendation is unchanged, no switch question is asked (a brief statement or nothing) — no per-module "switch?" nagging (INV-012).
- [ ] On "yes" the guide instructs the bootcamper to run `/model`/`/effort` and waits; on "no" it proceeds. The guide never runs or applies the session change itself.
- [ ] Graduation start applies the same change-triggered rule.
- [ ] `ground-rules.md`, `graduation/SKILL.md`, and `docs/model-selection.md` are updated consistently, and `INV-062` is amended (with maintainer sign-off) to match.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — change the "best-value model/effort nudge" from a pure statement to a change-triggered single 👉 question, and adjust the "After an affirmative module-transition" sequence.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — apply the same change-triggered prompt at the graduation banner.
- `plugins/senzing-bootcamp/docs/model-selection.md` — update the "Module-start commands (the nudge)" description to match.
- `specs/INVARIANTS.md` — amend `INV-062` (maintainer sign-off required).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Prompt to change model/effort right after recommending it" (2026-07-16, Module 2).
- Priority: Medium.
- Related specs: `module-start-model-nudge.md` (introduced `INV-062`, which this supersedes); `skill-model-selection.md` (the per-stage evaluation).

## Invariants introduced

- `INV-063` — At every module start and graduation start, the guide MUST surface the recommended session model and reasoning effort with the exact `/model`/`/effort` commands; when the recommendation changes from the current stage it MUST pause with a single 👉 yes/no switch question (its own yielding turn, never combined with another 👉), else a concise non-blocking statement; the guide never changes the session itself and never blocks beyond that one optional question; per-stage values are advisory. **Supersedes `INV-062`** (recorded in `specs/INVARIANTS.md`).
