# Consolidate the results-dashboard offer into Query, Visualize & Discover

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 6 (Data Processing), Phase D, Step 28 asks a mandatory pinned question:

> 👉 **Would you like a results dashboard showing entity counts, match statistics, and sample resolved entities?**

The bootcamper feels a visualization/exploration feature belongs in the module whose entire purpose
is querying and visualizing results — **Query, Visualize & Discover** (Module 7) — not at the tail
end of the data-loading module.

## Root cause

`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:113-136` (Step 28)
presents the dashboard offer as a "mandatory visualization offer (internal gate)" and writes
`docs/visualizations/results_dashboard.html`.

**Coherence finding that reinforces the feedback:** Module 7 **already offers a results dashboard**.
`plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:197-209`
(Step 3d) pins "👉 **Would you like a results dashboard visualizing the findings?**". So the bootcamp
offers a results dashboard **twice** — once at the end of Module 6 and again in Module 7. The fix is
therefore consolidation, not merely a move.

## Proposed change

1. **Remove** the results-dashboard offer from Module 6 Phase D Step 28 (and its "mandatory
   visualization offer (internal gate)" framing). Keep Step 28's "document results" work
   (`docs/results_validation.md`) and the Iterate-vs-proceed Decision Gate intact.
2. **Enrich Module 7 Step 3d** so the single remaining offer covers what Step 28 promised — entity
   counts, match statistics, and sample resolved entities — still pinned verbatim (INV-056), still
   writing `docs/visualizations/results_dashboard.html` (INV-070), still capturing screenshots per
   `../bootcamp-onboarding/module-completion.md`.
3. **Reconcile cross-references** that assumed the Module 6 offer exists:
   `remove-orphaned-first-visualization-guarantee.md:42` ("Module 6 results-dashboard offer ...
   unchanged and still function") and `drop-checklist-and-summary-gates.md:45` (Step 28 made a
   mandatory internal gate). Note the change so those specs stay coherent.

## Acceptance criteria

- [ ] The results-dashboard offer is presented **once**, in Module 7 (Step 3d), covering entity counts, match statistics, and sample resolved entities; Module 6 Phase D no longer offers a results dashboard.
- [ ] Module 6 Step 28 still documents results (`docs/results_validation.md`) and its Iterate-vs-proceed Decision Gate is unchanged.
- [ ] Module 7 Step 3d still writes `docs/visualizations/results_dashboard.html` (INV-070) and captures screenshots per module-completion.
- [ ] Specs/invariants that assumed the Module 6 offer are reconciled; no other Module 6 visualization offer (the cross-source graph, `phaseD-validation.md:56-63`) is affected.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — remove the Step 28 dashboard offer; keep results documentation and the Decision Gate.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — enrich Step 3d to cover entity counts / match statistics / sample resolved entities.
- `specs/remove-orphaned-first-visualization-guarantee.md`, `specs/drop-checklist-and-summary-gates.md` — cross-reference note (coherence).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Move the results-dashboard offer to Query, Visualize & Discover" (2026-07-20, Module 6)
- Priority: Medium
- Related specs: `capture-visualization-screenshots-for-recap.md`, `remove-orphaned-first-visualization-guarantee.md`, `drop-checklist-and-summary-gates.md`
