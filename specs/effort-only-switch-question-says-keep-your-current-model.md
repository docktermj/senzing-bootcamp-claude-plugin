# Effort-only switch question says "keep your current model"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

When a module's recommendation differs on the **effort** dial only, the pinned
model/effort switch question asks about effort and then offers, as its decline
hint, "reply no to keep your current **model**" — an answer hint about a dial the
question is not touching. The Bootcamper is asked one thing and told what
declining does to another:

> 👉 **Would you like to switch to `/effort high` for this module?** (Recommended for best value; reply no to keep your current model.)

Reaching SDK setup on Opus 5 produces exactly this. It is the common case rather
than an edge case: a Bootcamper who stays on Opus 5 through the conversational
stages hits an effort-only step-up at the first code-heavy module, which is the
first time the nudge has anything to say to them.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:593` pins the
CLI form:

> 👉 **Would you like to switch to `/model {model}` + `/effort {effort}` for this module?** (Recommended for best value; reply no to keep your current model.)

and `:586-588` instructs that only the differing dial be named — "a bootcamper on
Opus 5 at medium effort entering a stage recommending Opus 5 at high effort is
asked to change the effort only, never told to re-set the model they are already
on."

The two are consistent for the question stem, which is bracketed and substitutable,
but the trailing answer hint hardcodes the word "model" outside any bracket. INV-056
pins the wording, so the hint cannot be improvised away at runtime; following both
rules literally produces the mismatch. The interface-neutral variant at `:599` has
the same hint and the same problem.

The confirmation gate that follows a **yes** is unaffected — `:619` reads "Reply
yes once you've set your model and effort", which is accurate for either dial.

n/a — no Senzing fact is involved.

## Proposed change

Make the answer hint dial-aware in both pinned variants, the same way the stem
already is. Options, in order of preference:

1. **Substitute the dial name.** Bracket it: "reply no to keep your current
   {dial}", resolving to "model", "effort", or "model and effort" as appropriate.
   Smallest change, keeps one pinned string per interface.
2. **Make it dial-neutral.** "reply no to keep your current settings" — correct in
   all three cases with no substitution. Slightly less specific, but immune to the
   same drift recurring.

Whichever is chosen, state at `:586-588` that the hint moves with the dial, so the
"name only the dial that differs" rule visibly covers the whole sentence rather
than just the stem.

## Acceptance criteria

- [ ] An effort-only switch question's decline hint refers to effort (or to
      settings generally), never to the model.
- [ ] A model-only switch question's hint refers to the model.
- [ ] A both-dials switch question's hint covers both.
- [ ] Both the CLI form (`ground-rules.md:593`) and the interface-neutral form
      (`:599`) are fixed; INV-056 still pins each, with the dial as a substitutable
      value.
- [ ] `tests/test_model_guidance_sync.py` still passes, and the pinned-wording
      check (if any) is updated to accept the substituted dial rather than a fixed
      literal.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the two
  pinned switch-question forms and the name-only-the-differing-dial rule.

## Source

- Feedback: dry run phase 3, 2026-08-13 — hit at the SDK setup module start on
  Opus 5, where the recommendation (Opus 5, high effort) differs from the session
  on effort alone (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none
