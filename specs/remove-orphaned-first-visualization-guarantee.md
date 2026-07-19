# Remove the orphaned "deferred first-visualization guarantee"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Modules 6 and 7 carry a "Deferred first-visualization guarantee" that clears a
`first_visualization: owed` marker in `config/bootcamp_progress.json`, described as set when
"Module 3 was opted out and the standalone demo declined." But **nothing sets that marker anymore**,
and the "standalone demo" it references was removed — so the mechanism is dead and its precondition
is self-contradictory.

## Root cause

The `module3-synthetic-verification-data` rework simplified Module 3's opt-out gate: it removed
both the `first_visualization: owed` marker write and the standalone TruthSet demo offer
(`skills/module-03-system-verification/phase1-verification.md` now states System Verification
"does not offer a standalone TruthSet demo of its own"). The **readers/clearers** in Modules 6 and
7 were left behind:

- `skills/module-06-data-processing/phaseD-validation.md` — the "Deferred first-visualization
  guarantee" block (clears the marker to `module_6_deferred`).
- `skills/module-07-query-visualize-discover/phase1-query-visualize.md` — the "Deferred
  first-visualization guarantee" block (marks `module_7_deferred`).

A plugin-wide grep confirms **no code or skill sets `first_visualization: owed`**. Under the
customizable-module design, whether a workstation-verification visualization is produced is
governed solely by whether the **Truth Set visualization** module is selected (INV-077) — a
deselection is the bootcamper's explicit choice — so the journey-level "guarantee" is obsolete,
not merely dormant.

## Proposed change

Remove both dead "Deferred first-visualization guarantee" blocks (Module 6 and Module 7). Leave
the modules' normal, still-valid visualization offers (the Module 6 results dashboard, the Module 7
entity graph) untouched. No `first_visualization` bookkeeping remains anywhere. This upholds
INV-077 (module selection governs the visualization) with no dead mechanism or false precondition.

## Acceptance criteria

- [ ] Neither Module 6 nor Module 7 references `first_visualization`, `owed`, `module_6_deferred`, `module_7_deferred`, or a "standalone demo declined" precondition.
- [ ] The Module 6 results-dashboard offer and Module 7 entity-graph offer are unchanged and still function.
- [ ] A plugin-wide grep for `first_visualization` returns nothing; no dangling reference remains.
- [ ] The workstation-verification visualization guarantee remains governed by INV-077 (Truth Set visualization module selection).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — remove the deferred-guarantee block.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — remove the deferred-guarantee block.

## Source

- Audit (deep-dive conformance/coherence review), 2026-07-19 — finding #2 (MAJOR; introduced by the Module 3 rework).
- Priority: High.
- Related specs: `module3-synthetic-verification-data.md` (removed the setter), `customizable-module-selection.md` (INV-077 governs the visualization).
