# The screenshot-embed rule requires a turn in which the recap section does not yet exist

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots" requires:

> when a capture succeeds, embedding every screenshot it produced is required, not optional, and no
> count cap applies (INV-146): add them all to this module's **Actions Taken** as Markdown images —
> `![caption](visualizations/<name>-<tab-slug>.png)` — **in the same turn the capture ran**, in the
> app's tab order.

In the Truth Set visualization module the capture and the recap section are separated by **two turn
boundaries**, so "the same turn" cannot be satisfied:

| Event | Where | Turn boundary after it |
|---|---|---|
| Capture runs | `phase1-visualization.md` Step 2.4 | — |
| Guided tour | `phase1-visualization.md` Step 2.5 | 👉 *"Are you ready to continue?"* (`:555`) |
| Teardown consent | `phase2-close.md` | 👉 *"Ready for me to stop the visualization server…"* (`:75`) |
| **Recap section appended** | `phase2-close.md` Step 11 → module completion Step 2 | 👉 transition question (`:178`) |

At capture time this module's `## {Name}` recap section does not exist, so there is no
**Actions Taken** to add image lines to. Observed live on 2026-08-31: six captures written at
Step 2.4 against a running server, with the recap section not created until the module close, two
gates later.

The same shape applies in **Query, Visualize and Discover**, which reuses the tabbed app.

⚠️ This is the **unsatisfiable-instruction** class. The section's own next sentence supplies the
operational answer — *"record it at the step checkpoint"* — so a careful reader lands correctly, but
the two clauses are in tension and the emphatic one is the impossible one. The cost is not lost
images; it is that an instruction which cannot be followed teaches that these rules are approximate.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md`, "Capturing
visualization screenshots". The clause was written from the perspective of a module whose capture
and recap append happen together. Both modules that actually capture separate the two **by design** —
the guided tour and the teardown-consent gate sit between them, and both gates are deliberate
(the teardown gate exists precisely because teardown is irreversible).

The reason the rule is emphatic is sound and must be preserved: a previous run captured images and
never embedded them, and graduation had to backfill.

## Proposed change

Restate the timing so it binds the same behavior without requiring the impossible turn:

> **Record the capture at the step checkpoint in the same turn it ran** — the file paths and the tab
> each one shows — and **embed every one of them in this module's Actions Taken when that section is
> written at module close.** The embed is required, not optional, and no count cap applies
> (INV-146). Recording at the checkpoint is what carries the capture across the turn boundaries
> between the two; a capture recorded nowhere is one graduation has to backfill.

Keep the rest of the section unchanged — the `visualizations/…` relative-path rule (INV-161), the
own-line block form (INV-242), the no-pruning ⛔, and the open-the-graph-image check.

## Acceptance criteria

- [ ] The screenshot section states a timing rule that both capturing modules can satisfy without
      violating their own turn structure.
- [ ] The requirement to embed **every** captured image, with no count cap, is unchanged in force.
- [ ] The checkpoint is named as the mechanism that carries the capture across the turn boundary.
- [ ] No module needs its 👉 gates reordered to comply.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — "Capturing
  visualization screenshots": the timing clause.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Truth Set visualization Step 2.4
  (`Source: self-observed (assistant retrospective)`) — found by capturing six screenshots against a
  live server and having nowhere to embed them. No previous phase-3 walk reached a capture.
- Priority: Low
- MCP re-check: n/a (no Senzing fact).
- Upstream: not applicable
- Related specs: `specs/step-15s-both-versions-gate-is-unsatisfiable-on-a-generated-scenario.md` —
  same finding class (an instruction the guide provably cannot follow).

## Deviations from this spec, and why (2026-09-01)

**None to the substance.** The timing is restated as two moments, the force of the requirement is
unchanged, the checkpoint is named as the carrier, and no module's 👉 gates were touched.

**One thing the spec did not anticipate, recorded because it is the more useful finding.** Editing
this bullet made an existing guard fail —
`tests/test_conformance_sees_a_rule_beside_a_citation.py::test_it_reports_only_hard_rules_and_only_from_shipped_markdown`
— and the guard was wrong, not the change. It asserts that every line `conformance.py since` reports
is a hard rule, by running the script's own `classify()` over the reported text; but `since`
**truncates its display at 110 characters**, so it was classifying a *prefix*. This bullet is 638
characters and carries its ⛔ past the cut, so `classify()` returned `None` and the failure read as
*"conformance reported a non-rule"* — when `classify()` on the **full** line returns `mid-line` and
conformance was correct throughout.

The test had passed only because no reported line had previously been long enough to lose its rule
marker to truncation. It now resolves the reported prefix back to its source line before
classifying. That is strictly stronger: the old form would have silently accepted any long rule as
"not a rule", which is the same false-negative shape the guard exists to prevent.

⚠️ **The new rule was put on its own line rather than appended to the bullet.** A 638-character
bullet carrying three separate ⛔ rules is what made the truncation defect invisible, and adding a
fourth to it would have deepened exactly that.
