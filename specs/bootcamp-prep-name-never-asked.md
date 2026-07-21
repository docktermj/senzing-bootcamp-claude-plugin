# Reconcile the `name` preference: documented as asked in Bootcamp preparation, but never asked

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`name` is documented as one of the setup answers "asked in the Bootcamp preparation module," but no
step in Bootcamp preparation asks for it, and the consolidated write only records "`name` if it was
captured." The documentation describes a question that does not exist — an INV-003 coherence defect.

## Root cause (confirmed)

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:148-151` lists `name` among
  the preferences "asked in the **Bootcamp preparation** module and persisted in **one** consolidated
  write."
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` Steps 1–5 contain **no** name
  question; Step 6's consolidated write hedges "`name` if it was captured" (`:219`) — confirming it
  may never be captured.
- The shipped example recap uses a bootcamper name (e.g. "Alex Rivera" in
  `docs/examples/bootcamp_recap.example.md`), so a name is *consumed* by the recap even though it is
  never *asked*.

## Proposed change

**Maintainer decision required** between:

- **(a) Capture it without a new question (recommended).** If the recap/graduation genuinely want a
  name, source it silently from the environment/git config (e.g. `git config user.name`) during
  Bootcamp preparation and hold it for the consolidated write — no extra 👉 question (keeps the
  question count and friction unchanged; consistent with INV-012). Update `ground-rules.md` to say
  "detected, not asked."
- **(b) Ask it.** Add a pinned-verbatim (INV-056), single-meaning (INV-008), non-blocking 👉 question
  in Bootcamp preparation to capture the name, held for the consolidated write (INV-058).
- **(c) Drop it.** If no name is needed, remove `name` from `ground-rules.md:149`, drop the "`name`
  if it was captured" hedge, and confirm the recap/graduation do not depend on it.

Pick based on whether the recap/graduation actually rely on a name; do not guess. Whichever is
chosen, `ground-rules.md` and Bootcamp preparation must agree, and no documented question may exist
without an implementation (or vice-versa).

## Acceptance criteria

- [ ] `ground-rules.md` and `bootcamp-preparation/SKILL.md` agree on whether/how `name` is captured; there is no documented question without a matching implementation.
- [ ] If `name` is kept (a or b), the recap/graduation consumers read it consistently; if dropped (c), no consumer relies on it and the hedge is removed.
- [ ] If a question is added (b), it is pinned-verbatim, single-meaning, and non-blocking (INV-056 / INV-008 / INV-005); if detected (a), no new question is introduced (INV-012).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the `name` claim at `:149`.
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — the consolidated-write hedge at `:219`, and a capture step if option (a)/(b) is chosen.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` and recap generation — only if the name-consumption path needs to match the decision.

## Source

- Final review audit (2026-07-20), finding **M4** (medium).
- Priority: Medium
- Related specs: `customizable-module-selection.md` / `relocate-setup-questions-to-bootcamp-preparation.md` (INV-075 / INV-088 Bootcamp-preparation setup set + consolidated write), `suppress-admin-write-noise.md` (INV-058).
