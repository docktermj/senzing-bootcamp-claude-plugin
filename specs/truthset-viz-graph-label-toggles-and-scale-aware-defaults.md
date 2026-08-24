# Make graph labels toggleable and their defaults scale-aware, not tuned to the Truth Set's size

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Three reports, one underlying defect: the graph tabs hardcode a single label configuration chosen
against a 159-record dataset.

1. **Labels overlap and are unreadable** (High). In the Entity Graph, node/entity name labels overlap
   when nodes cluster. "It makes exploring the graph harder to trust — the bootcamper can't clearly
   tell which records actually matched when labels overlap."
2. **No way to control label density** (Medium). With 84 entities and 71 relationships, edge
   match-key labels always render and overlap heavily. The bootcamper asked for **independent** on/off
   toggles for (a) node entity-name labels and (b) edge match-key labels, in both Entity Graph and
   Relationship Network — so they can declutter for an overview pass or drill into detail without
   switching tabs.
3. **The default does not survive reuse** (Medium, self-observed). The same app, reused unchanged for
   Module 7's Customer 360 data (**3,986 entities, 1,040 edges**), rendered roughly a thousand
   overlapping edge labels and the Entity Graph became an unreadable hairball. The bootcamper cannot
   tell this is a default problem — "it just looks like their data is too messy to visualize."

Worth recording from the same report: the reuse otherwise went *well*. The server was already
parameterized (`--records`, `--title`, `--snapshot`, `--port`) with no hardcoded data sources, so all
nine tabs worked on new data immediately. **Only the visual defaults failed to travel.**

## Root cause

The visualization contract fixes one label configuration and provides no user control and no
scale sensitivity.

- `phase1-visualization.md:231` specifies the Entity Graph as "…sized by record count, **edges
  labeled with match keys, hover tooltip**, click-to-detail modal, zoom/pan, and a color legend" —
  edge labels unconditionally on, node labels only as a hover `<title>` tooltip, no toggles, no
  collision handling.
- `phase1-visualization.md:236-238` specifies Relationship Network as "edges colored by relationship
  type with a type legend" — same omission.
- `visualization-api-reference.md:314-324` (the tab table) and `:53-93` (`/api/graph`) describe the
  data and the tab list; neither mentions label visibility, so nothing in the contract varies with
  dataset size.
- The reference implementation follows suit: per the reported session, `HtmlTemplate.java:274`
  hardcoded `checked` on the edge-label checkbox — correct for 84 nodes, wrong an order of magnitude
  up.

Because `phase1-query-visualize.md:203-206` explicitly directs Module 7 to build its results app
"modeled on the shipped Truth Set visualization server … pointed at the bootcamper's loaded data
instead of the Truth Set", every default chosen against the 159-record Truth Set is inherited at
production scale. That reuse is the plugin's stated intent, so it is the spec's job to make the
defaults travel.

## Proposed change

1. **Independent label toggles, required.** Specify separate show/hide controls for **node (entity
   name) labels** and **edge (match-key / relationship-type) labels** in both the Entity Graph and
   Relationship Network tabs. Two independent dials, not one combined control.
2. **Scale-dependent defaults.** Specify label visibility as a function of graph size rather than a
   fixed value: both label sets default **off above a node-count threshold** (~150 nodes), on below
   it. State the threshold in the contract so every language implementation picks the same behavior.
3. **Say why they started off.** When labels default off, show a short inline note ("Labels hidden —
   3,986 entities; use the toggles above to show them"). Without it the bootcamper reads a
   label-less graph as broken rather than as a deliberate default.
4. **Implementation note that bit the reference build:** an unchecked checkbox does not fire
   `onchange`, so the corresponding hide-class MUST be applied explicitly at init, not left to the
   event handler. Language-agnostic front-end behavior; belongs in the shared contract.
5. **Label legibility when labels ARE shown.** Address the original High-priority report: require
   on-canvas node labels to avoid unreadable overlap — a label-collision/overlap-avoidance pass, or
   truncation, or showing labels only above a zoom level. Hover-only tooltips are not sufficient,
   since the complaint is that the bootcamper cannot tell which records matched without hovering each
   node in turn.
6. **A general principle for the spec.** Add: *any default chosen while developing against the Truth
   Set MUST be reviewed for its behavior at 100× scale, because the same app is reused for
   production-scale data (`phase1-query-visualize.md:203`).* This is the durable fix — it catches the
   next scale-sensitive default, not just this one.
7. **Consider (not required): a "relationships/multi-record only" filter.** On the reported Customer
   360 dataset 99.6% of nodes were singletons, so a default view of only entities with relationships
   or multiple records would be far more informative. Worth offering as a graph filter; the Truth Set
   never exercised this case.

## Acceptance criteria

- [ ] `visualization-api-reference.md` and `phase1-visualization.md` require independent node-label
      and edge-label visibility toggles in both Entity Graph and Relationship Network.
- [ ] Label defaults are specified as scale-dependent with a stated node-count threshold (~150), not
      as a fixed always-on/always-off value.
- [ ] When labels default off, an on-screen note states why and points at the toggles.
- [ ] The spec requires overlap-avoidance (collision layout, truncation, or zoom-gated labels) for
      on-canvas node labels; hover-only tooltips do not satisfy it.
- [ ] The spec carries the init-time note that an unchecked toggle fires no `onchange`, so its render
      state must be applied explicitly at load.
- [ ] The spec states the general 100×-review principle for any default developed against the Truth
      Set.
- [ ] Rendering the same app against both a ~150-node and a ~4,000-node dataset produces a readable
      first view in both cases with no code change.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): stated as
      rendering requirements over `/api/graph`, with no dependency on the Java or Python reference
      build, and offline via the vendored D3 asset (INV-091).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — Entity
  Graph and Relationship Network tab descriptions (lines ~229-238): toggles, scale-dependent
  defaults, overlap avoidance
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  tab table (lines ~314-324) and a new rendering-defaults subsection carrying the threshold, the
  init-state note, and the 100×-review principle
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  lines ~203-224: the reuse instruction should point at the scale-aware defaults, since this is the
  path where the failure appeared
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the reference implementation Module 7 is
  modeled on must implement the toggles and the threshold

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_03.md` → "Entity Graph node labels overlap and are hard
  to read" (2026-07-24, Truth Set visualization, **High**)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Independent toggles for node labels and
  edge-attribute labels in Entity Graph / Relationship Network" (2026-07-24)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Make visualization defaults scale-aware, not
  tuned to the Truth Set's size" (2026-07-25, self-observed)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Bake this session's Truth Set visualization
  polish into the module spec as the default baseline" (2026-07-24) — point 7
- Priority: High (the label-overlap report), Medium (toggles, scale-awareness)
- Related specs: `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md`,
  `specs/vendor-d3-offline-visualization.md`, `specs/visualization-server-in-chosen-language.md`,
  `specs/relationship-network-edge-color-and-legend-filter.md`
