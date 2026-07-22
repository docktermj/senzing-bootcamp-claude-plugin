# Restructure the Module 7 visualization/exploration offers under one decision point

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In Module 7 (Query, Visualize and Discover) the visualization offers are scattered:
the entity-graph and results-dashboard offers come early (steps 3c/3d), the
cross-source-overlap-heatmap / feature-score-distribution suggestions come late buried
in the Discover chain (step 4e), and the Discover opt-in is positioned as bundled with
the visualization decision. The bootcamper finds this confusing and wants:

1. After the query-requirements adjustment question, one "would you like additional
   visualizations?" gate — if yes, offer (a) a Truth-Set-style view, (b) the entity
   graph, (c) the results dashboard, each its own 👉 question; if no, skip all viz
   offers.
2. The step-4e visualization-suggestions question (heatmap / feature-score
   distribution) moved to be a sub-question under that gate.
3. The Discover-phase opt-in made fully **independent** of the visualization decision.

## Root cause

All five elements are spread across the three Module 7 phase files as a linear chain,
not a single gated branch:

- `phase1-query-visualize.md` — query-requirements adjustment question `:28`;
  entity-graph offer 3c `:175-199` (Q `:180`); results-dashboard offer 3d `:201-218`
  (Q `:206-208`); Discover handoff `:220-232`; Query Completeness Gate `:240-249`
  (asserts both graph and dashboard were offered) and success criteria `:235-238`.
- `phase2-discover.md` — Discover opt-in `:24-37` (Q `:30`).
- `phase2b-discover.md` — step 4e `:111-165` (heatmap `117-120`, feature-score
  `132-135`); 4d→4e transition `:96`; discover-phase completion "all steps 4a–4e"
  `:167-195`.

Step 4e is only reachable via Discover opt-in → 4a→4b→4c→4d→4e, so a bootcamper who
declines the Discover opt-in never sees the heatmap/feature-score suggestions — exactly
the coupling the feedback wants broken.

**Invariant note:** **INV-046** (query always created; visualization and discovery
*offered*) — the restructure stays within it but must preserve: (a) query always
created, (b) both entity graph and results dashboard still *offered* so the Query
Completeness Gate (`:240-249`) and success criteria (`:235-238`) stay satisfied even
when the umbrella answer is "no", and (c) Discover still offered. Also: INV-056 (every
new/moved 👉 pinned verbatim), INV-051/INV-008/INV-009 (umbrella gate branching
formatted correctly; rework the 4d/4e transition menus `:94-97`), INV-070 (moved
visualizations still write to `docs/visualizations/`). Checkpoint keys need
reconciling: 4e checkpoints under `module_7_query.steps.4e` (`:159-165`, `:187`), and
`discover_phase: "completed"` = "all steps 4a–4e" (`:167-195`) plus the gate wording
(`:247`) must be updated so Discover can complete without 4e once 4e moves.

## Proposed change

In `phase1-query-visualize.md`, immediately after the query-requirements adjustment
question:

- Ask once (pinned 👉): "would you like to consider additional visualizations?" — if
  yes, present the Truth-Set-style view, entity-graph, and results-dashboard offers,
  each its own pinned 👉; if no, skip all viz offers. Treat the umbrella decline as
  having *offered* the graph and dashboard so the Query Completeness Gate stays
  satisfied.
- Move the step-4e visualization-suggestions question and its heatmap/feature-score
  content out of the Discover chain to be a sub-question under this umbrella gate.
- Ask the Discover-phase opt-in **independently**, not gated on the viz decision.
- Reconcile the `discover_phase` completion definition and the Query Completeness Gate
  wording so Discover completes without step 4e; move the 4e checkpoint key
  accordingly.

Keep every new/moved question pinned verbatim (INV-056).

## Acceptance criteria

- [ ] After the query-requirements adjustment question, a single "additional visualizations?" gate branches to the Truth-Set-style, entity-graph, and results-dashboard offers; "no" skips them all.
- [ ] The heatmap / feature-score-distribution suggestions are reachable from the visualization gate, not only via the Discover chain.
- [ ] The Discover-phase opt-in is asked independently of the visualization decision.
- [ ] Query code is still always created; entity graph and results dashboard are still offered (completeness gate satisfied even on umbrella "no"); Discover is still opt-in (INV-046).
- [ ] `discover_phase` can complete without step 4e; checkpoint keys and gate wording are reconciled.
- [ ] All new/moved questions are pinned verbatim, unambiguous, numbered where 2+ choices (INV-056/INV-008/INV-051); moved visualizations write to `docs/visualizations/` (INV-070).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — add the umbrella gate + re-parented offers; update completeness-gate wording.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — make the opt-in independent.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — move step 4e out, rework the 4d/4e transition, reconcile discover-phase completion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Restructure Discover-phase visualization/exploration offers in Module 7" (2026-07-22, Module Query, Visualize and Discover)
- Priority: Medium
- Related specs: `specs/consolidate-results-dashboard-offer-in-module7.md` (owns the 3d dashboard offer this re-parents), `specs/pin-visualization-offer-questions.md` (offers must stay pinned verbatim), `specs/capture-visualization-screenshots-for-recap.md`; INV-046, INV-056, INV-070
