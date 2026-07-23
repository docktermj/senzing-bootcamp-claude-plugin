# Reconcile the cross-source visualization offer: Module 6 Step 23 vs. Module 7

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

During Module 6 (Data processing) cross-source validation, Phase D Step 23 offers:

> 👉 **Would you like a web page visualizing the cross-source entity relationships?**

writing `docs/visualizations/multi_source_results.html`. The bootcamper observes that a
*results/relationship visualization* conceptually belongs in Module 7 (Query, Visualize and
Discover), where results exploration lives — not in the data-loading/validation module. They
also note an internal inconsistency: Module 6's own Step 28 already defers the **results
dashboard** to Module 7 Step 3c "to avoid a duplicate offer," yet Step 23 still offers a
cross-source *relationship* visualization in Module 6.

## Root cause

By design, not a defect — but the design now reads as incoherent after the dashboard was
consolidated into Module 7:

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md:56-63`
  (Step 23) offers the cross-source relationship visualization during Module 6 validation and
  writes `docs/visualizations/multi_source_results.html`.
- Same file `:130-133` (Step 28) defers the results dashboard to "Module 7, Step 3c — the
  consolidated visualization gate, where all results visualization lives," and explicitly
  declares the Step 23 cross-source visualization "a distinct offer and is unaffected."
- Module 7's consolidated gate already covers this ground:
  `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:249-256`
  (Step 3c sub-offer (d)) offers a **Cross-source overlap heatmap** ("when 2+ data sources are
  loaded") and a **Relationship network graph**. So a cross-source relationship visualization is
  effectively offered in **two** places — Module 6 Step 23 and Module 7 Step 3c(d).

The consolidation precedent (`consolidate-results-dashboard-offer-in-module7.md`) deliberately
left Step 23 out of scope ("Module 6's cross-source relationship offer (step 23) is unaffected"),
which is exactly the loose end this feedback surfaces.

**Invariant note:** no invariant *requires* the Module 6 Step 23 offer. INV-046 places
visualization in the "query, visualize, and discover" stage as an offer (Module 7); INV-014
makes a declined/removed offer a requested skip; INV-070 keeps any produced HTML under
`docs/visualizations/`; INV-056 keeps any surviving/moved 👉 pinned verbatim. Moving or retiring
the offer stays within all of these.

## Proposed change

Maintainer decision required — two coherent options:

**Option A (recommended): consolidate into Module 7.** Retire the Step 23 standalone offer so all
results/relationship visualization is offered once, in Module 7's Step 3c gate — matching the
dashboard-consolidation precedent. Keep Step 23's cross-source *validation* work (sampling 15–25
multi-source entities, spot-checks). Update the Step 28 note so it no longer describes Step 23 as
"a distinct offer … unaffected." In Module 7 Step 3c, ensure the cross-source relationship view is
covered — sub-offer (d) already lists the cross-source heatmap and relationship network; add a
brief note that this is where the former Module 6 `multi_source_results.html` view now lives (and,
if `consolidate-module7-visualizations-as-truthset-app-tabs.md` lands, it becomes a tab there).

**Option B: keep a validation-time visual, but make the split explicit.** Keep Step 23 but reframe
it as a *validation spot-check* aid (confirming cross-source matches during loading), and add a
one-line note in both Module 6 Step 23 and Module 7 Step 3c distinguishing the validation-time
visual from Module 7's results/relationship visualization — so it no longer reads as a duplicate or
misplaced results offer. Keep the 👉 pinned verbatim (INV-056).

Recommendation: **Option A**, for coherence with the results-dashboard consolidation already done;
Option B is acceptable if a validation-time visual is considered pedagogically valuable at load
time.

## Acceptance criteria

- [ ] The cross-source relationship visualization is not offered as a duplicate: it is offered once (Module 7 Step 3c, Option A) **or** the Module 6 Step 23 and Module 7 Step 3c offers are explicitly distinguished as validation-time vs. results-exploration (Option B).
- [ ] Module 6 Step 28's note no longer contradicts the chosen outcome (it currently states Step 23 is "a distinct offer and is unaffected").
- [ ] Module 6 Step 23's cross-source **validation** work (sampling/spot-checking multi-source entities) is retained regardless of option chosen.
- [ ] Any surviving or moved offer is pinned verbatim (INV-056); any produced HTML stays under `docs/visualizations/` (INV-070); a decline is treated as a requested skip (INV-014).
- [ ] Module 7's Query Completeness Gate and success criteria remain satisfied (visualizations still offered, INV-046).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — Step 23 offer (retire under Option A / reframe under Option B); update the Step 28 coherence note (`:130-133`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — Step 3c sub-offer (d) note that cross-source relationship visualization is covered here (`:249-256`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Cross-source visualization offer placement (Module 6 vs Module 7)" (2026-07-23, Module Data processing (Module 6), Phase D, Step 23)
- Priority: Medium
- Related specs: `consolidate-results-dashboard-offer-in-module7.md` (dashboard-consolidation precedent that left Step 23 in place), `restructure-module7-visualization-offers.md` (the Step 3c gate + sub-offer (d)), `consolidate-module7-visualizations-as-truthset-app-tabs.md` (if adopted, the cross-source view becomes a tab); INV-046, INV-070, INV-056, INV-014
