# Fold Module 7's static visualizations into the Truth-Set-style app as tabs

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 7's visualization gate (Step 3c) produces several **separate static HTML pages** —
`docs/visualizations/cross_source_heatmap.html`, `multi_source_results.html`,
`relationship_network.html`, and `results_dashboard.html` — each behind its own pinned 👉
question, alongside the interactive Truth-Set-style app (Entity Graph, Record Merges, Merge
Statistics, Search/Probe tabs). The bootcamper asks that these views instead be folded into the
one interactive app as **additional tabs**, de-duplicating anything the existing tabs already
show, so the payoff is a single cohesive "wow" artifact rather than a scatter of static pages —
and so three of Module 7's separate sub-offer questions can be retired:

- "Would you like a visualization of the resolved entities as an entity graph?"
- "Would you like a results dashboard showing entity counts, match statistics, and sample resolved entities?"
- the cross-source overlap heatmap / relationship network graph suggestions.

## Root cause

By design — the current Step 3c gate offers each visualization as its own question and separate
artifact:

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:208-272`
  (Step 3c) offers (a) Truth-Set-style interactive view (`truthset_style_view`), (b) entity graph
  (`entity_graph`), (c) results dashboard (`results_dashboard.html`), and (d) data-specific
  suggestions — cross-source overlap heatmap, entity-size distribution, relationship network,
  match-key frequency, feature-score distribution (`:249-263`) — each a distinct pinned 👉 and a
  separate static page.
- The interactive app (sub-offer (a)) is built modeled on the shipped reference server and the
  shared contract: `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` and
  `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`.
  It currently renders **four tabs** — Entity Graph, Record Merges, Merge Statistics, Search/Probe
  (`module-03b-truthset-visualization/phase1-visualization.md:219-232`; endpoints `/api/stats`,
  `/api/graph`, `/api/merges`, `/api/search`, `/api/why`, `/api/how` in
  `visualization-api-reference.md:22-231`). There are no dashboard / cross-source-overlap /
  relationship-network tabs or endpoints, so those views can only exist as separate static pages.

**Invariant note:** **INV-090** is load-bearing — the visualization server is built in the
bootcamper's chosen language, modeled on the reference server **and** the
`visualization-api-reference.md` contract. Any new tab needing data (results dashboard,
cross-source overlap, relationship network) MUST have its endpoint/response shape added to **both**
the reference server and the contract, or language-native servers silently diverge. Also:
INV-091 (offline vendored D3, no CDN), INV-081 (`brand_tokens` palette/typography), INV-070 (any
HTML written under `docs/visualizations/`). The entity graph tab already exists, so
`multi_source_results.html` (cross-source entity relationships) is largely **subsumed** by it —
de-duplicate rather than add a redundant tab. Snapshot wrinkle (per
`snapshot-static-search-results` / `visualization-why-how-and-clickable-histogram`): tabs whose
data can be pre-computed (dashboard counts, heatmap, network from the export) render offline in the
standalone snapshot; any live-SDK-only view degrades gracefully there.

**Completeness-gate reconciliation:** `restructure-module7-visualization-offers.md` requires the
entity graph and results dashboard to still be *offered* for the Query Completeness Gate
(`phase1-query-visualize.md:304-315`) and success criteria (`:296-302`). Folding them into the
Truth-Set-style app means the umbrella 👉 ("additional visualizations?") plus the single
Truth-Set-style tabbed offer becomes that offer; the gate/success-criteria wording must be updated
so it no longer asserts separate entity-graph and results-dashboard offers.

## Proposed change

1. **Extend the shared contract and reference server (INV-090).** Add tabs + backing endpoints for:
   - **Results dashboard** — entity counts, match statistics, sample resolved entities (source via
     `reporting_guide(topic='dashboard'/'reports', ...)`); can reuse/extend `/api/stats`.
   - **Cross-source overlap heatmap** — which sources share the most resolved entities (offer only
     when 2+ sources loaded).
   - **Relationship network** — how entities connect through shared attributes / disclosed
     relationships (source via `find_network_by_entity_id` / relationship-inclusion export, as the
     existing `/api/graph` edge-discovery contract already describes).

   Document each new endpoint and JSON response shape in
   `module-03b-truthset-visualization/visualization-api-reference.md` and implement them in
   `scripts/senzing_viz_server.py` (the Python reference), confirming any SDK method/flag names via
   the Senzing MCP tools (INV-080).
2. **Render as tabs**, styled from `brand_tokens` (INV-081), offline with vendored D3 (INV-091). The
   entity-graph tab subsumes `multi_source_results.html`; do not add a redundant cross-source
   entity-relationship page.
3. **Retire the separate Module 7 sub-offers** in `phase1-query-visualize.md` Step 3c: sub-offer
   (b) entity graph and (c) results dashboard, and the heatmap/relationship-network entries of
   sub-offer (d), become tabs of the single Truth-Set-style app (sub-offer (a)). Keep sub-offer
   (d)'s genuinely distinct chart suggestions that are not tab-shaped (e.g. entity-size
   distribution, match-key frequency, feature-score distribution) as an optional catalog, or route
   them into tabs too — maintainer's call, noted below.
4. **Reconcile the completeness gate / success criteria** (`:296-315`) so "entity graph and results
   dashboard offered" is satisfied by the tabbed-app offer, not separate questions; keep the
   umbrella gate pinned verbatim (INV-056) and `m7_visualizations` checkpoint recording accurate.
5. **Scope decision (surface, do not silently decide):** the contract is shared (INV-090) with the
   Module 3b Truth Set visualization. Decide whether the new tabs appear only in the Module 7
   chosen-data instance or also in the Module 3b Truth Set app. Adding them to the shared contract
   is cleanest but expands Module 3b's scope — call this out for the maintainer.

## Acceptance criteria

- [ ] The Truth-Set-style app exposes the results dashboard, cross-source overlap heatmap, and relationship network as **tabs**, sourced from documented endpoints; `multi_source_results.html` is not re-produced as a separate page (subsumed by the entity-graph tab).
- [ ] Module 7 Step 3c no longer asks the separate entity-graph and results-dashboard 👉 questions, nor the cross-source-heatmap/relationship-network sub-offer; those views are reached as tabs of the single Truth-Set-style offer.
- [ ] `visualization-api-reference.md` documents every new endpoint/response shape so a language-native server can replicate it (INV-090); `senzing_viz_server.py` implements the reference version.
- [ ] All new tabs use `brand_tokens` (INV-081) and render offline with vendored D3 (INV-091); no new network dependency; any produced HTML stays under `docs/visualizations/` (INV-070).
- [ ] The static snapshot still builds and degrades gracefully for any live-only view.
- [ ] Module 7's Query Completeness Gate and success criteria are reconciled — entity graph and results dashboard count as offered via the tabbed-app offer (INV-046); the umbrella gate stays pinned verbatim (INV-056).
- [ ] SDK method/flag names are confirmed via the Senzing MCP tools (INV-080), not training data.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — document the new dashboard / cross-source-overlap / relationship-network endpoints and response shapes (INV-090 contract).
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — reference implementation of the new tabs + endpoints; snapshot degradation.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — tab descriptions / endpoint verification table (`:219-232`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — retire sub-offers (b)/(c) and the heatmap/network part of (d); reconcile the completeness gate/success criteria (`:208-315`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Consolidate Module 7 static visualizations into the Truth-Set-visualization app as tabs" (2026-07-23, Module Query, Visualize and Discover (Module 7) / Truth Set visualization)
- Priority: Medium
- Related specs: `visualization-why-how-and-clickable-histogram.md` (also adds tabs/endpoints to the same app + contract — coordinate to avoid collision), `restructure-module7-visualization-offers.md` (the Step 3c gate whose sub-offers this retires; completeness-gate reconciliation), `visualization-server-in-chosen-language.md` (INV-090/091), `truthset-visualization-full-apparatus.md`, `snapshot-static-search-results.md`, `cross-source-visualization-offer-module6-vs-module7.md`; INV-090, INV-091, INV-081, INV-070, INV-046, INV-056, INV-080

## Invariants introduced

- `INV-104` — The bootcamp's results / entity-resolution visualizations MUST be delivered as ONE consolidated, tabbed interactive app (built per INV-090 from `visualization-api-reference.md`), never as separate static HTML pages; the entity graph, relationship network, results dashboard, cross-source overlap, match-key frequency, and feature-score views are tabs (a tab is shown only when its data exists, no redundant tab duplicates another), and Module 7 offers the single app via one pinned gate that counts as offering the entity graph and results dashboard for INV-046 (recorded in `specs/INVARIANTS.md`).
