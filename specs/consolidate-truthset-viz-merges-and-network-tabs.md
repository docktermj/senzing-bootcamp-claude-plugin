# Fold Record Merges and Relationship Network into the tabs that subsume them

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two bootcamper requests, one theme: the Truth Set visualization ships eight tabs, two of
which duplicate content another tab already carries.

1. **Record Merges is a subset of Search / Probe.** Comparing the two response schemas at the
   bootcamper's request: for any entity present in both, Search / Probe's per-entity result is
   a strict superset. Record Merges shows entity name, record count, and one entity-level match
   key; Search / Probe shows all of that **plus** per-record match keys and feature scores. The
   one thing Record Merges uniquely offers is browsing *all* merged entities with no query,
   versus Search / Probe needing a name to look up.
2. **Relationship Network is a filtered view of Entity Graph.** Both are driven by the same
   `/api/graph` data; Relationship Network is the subgraph of entities that have relationships.
   The bootcamper asked for a toggle on Entity Graph — all entities vs. relationship subgraph
   only — after which the standalone tab is redundant.

Both were then **implemented and verified live** during the bootcamp, and the bootcamper
reviewed the six-tab result and reported it looks great, asking for a record of the changes so
they could be ported. That implementation record is reproduced under "Proposed change" below;
it is the reference implementation for this spec, not a new design.

The changes were made in a project-local copy (`src/server/senzing_viz_server_custom.py`), so
the shipped plugin is unchanged and no other bootcamper has them.

## Root cause

Not a defect — a design-simplification request against the visualization contract.

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:637` declares all eight tabs:

  ```javascript
  const ALL_TABS=[["graph","Entity Graph"],["network","Relationship Network"],["merges","Record Merges"],["stats","Merge Statistics"],["matchkeys","Match Keys"],["features","Feature Scores"],["overlap","Cross-Source"],["probe","Search / Probe"]];
  ```

  with the sections at `:626-633`, applicability at `:649`, dispatch at `:655-656`, and the
  `drawNetwork()` / `drawMerges()` renderers.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md:397-405`
  is the tab inventory that mandates them.

Note that the same file already carries a **"De-duplication (required)"** rule
(`visualization-api-reference.md:407-420`) — "Do NOT add a tab whose content is derivable from
another tab's endpoint. When two candidate tabs share their aggregates, **they are one tab.**"
— and applies it to remove a former Results Dashboard tab. But it explicitly rules the other
way on this one:

> - The **Relationship Network** tab *is* distinct (the related-entity subgraph emphasizing
>   relationship type), not a second full-population graph.

So this change is not merely a code edit: it **reverses a documented ruling** in the contract.
The bootcamper's live implementation is the evidence that reverses it — a mode toggle keeps the
relationship-type styling and legend filter that made the tab distinct, while removing the
second copy of the graph.

## Proposed change

Port the bootcamper's verified implementation into the shipped script and the contract.

**1. Remove the Record Merges tab** (`senzing_viz_server.py`)

Delete its HTML section (`:628`), its `ALL_TABS` entry (`:637`), and its `drawMerges()`
renderer. **Keep `/api/merges`** — Search / Probe's pre-verified example-query chips already
fetch it independently of the removed tab, and it is covered by
`tests/test_viz_endpoint_sync.py`. Removing the route would break the chips.

To preserve the tab's one unique capability (browse all merges with no query), add a
**"Show all merged entities"** affordance to Search / Probe that lists `/api/merges` results
with no query entered, so the no-query browse path is not lost. Search / Probe's richer
per-entity rendering then covers everything Record Merges showed.

**2. Replace the Relationship Network tab with a mode on Entity Graph**

Delete its HTML section (`:627`), its `ALL_TABS` entry, its `tabApplicable` case (`:649`) and
`drawFor` case (`:656`), and its `drawNetwork()` renderer. Fold its behavior into a rewritten
`drawGraph()` parameterized by a `graphMode` variable (`"all"` | `"network"`), both modes
served by the same `/api/graph` endpoint. Carry over, unchanged:

- filtering to the relationship subgraph,
- edge coloring/dashing by `relationship_type`,
- the click-to-filter relationship-type legend (established by
  `relationship-network-edge-color-and-legend-filter.md` — this must not regress).

**3. Add the toggle**

"Show only entities with relationships", added to Entity Graph's existing control panel
(`addGraphControls`), rendered **only when `relationships_total > 0`** — the same condition
that used to gate the tab's visibility. Toggling sets `graphMode` and re-runs `drawGraph()`.

**4. Update the contract** (`visualization-api-reference.md`)

- Remove the Record Merges and Relationship Network rows from the tab inventory (`:397-405`);
  the app is six tabs: Entity Graph, Merge Statistics, Match Keys, Feature Scores,
  Cross-Source, Search / Probe.
- Document the Entity Graph mode toggle, including its `relationships_total > 0` condition.
- **Rewrite the de-duplication bullet at `:418-419`** so the ruling matches: the relationship
  subgraph is a *mode of* Entity Graph, not its own tab. Add the Record Merges finding as a
  worked application of the same rule (a tab whose per-entity fields are a subset of another
  tab's is not a second tab), and record that the no-query browse capability moves to
  Search / Probe rather than being dropped.
- Update the endpoint/tab cross-reference at `:559-560`.

**5. Keep the two paths in sync**

The live server and the standalone snapshot are generated from the same source, so both become
six-tab. Confirm the snapshot builds and its tab set matches the server's — see
`specs/rebuild-viz-snapshot-after-customization.md`, which makes that comparison a gate.

Verified by the bootcamper against 159 records / 84 entities / 71 relationships: six tabs
served instead of eight, the toggle wired to `drawGraph()`, `/api/stats` and `/api/graph` still
HTTP 200 with the same model, and the standalone snapshot still building.

## Acceptance criteria

- [ ] The live app and the standalone snapshot each serve exactly six tabs: Entity Graph,
      Merge Statistics, Match Keys, Feature Scores, Cross-Source, Search / Probe.
- [ ] Entity Graph shows a "Show only entities with relationships" toggle when
      `relationships_total > 0`, and no toggle when it is `0`.
- [ ] With the toggle on, the graph renders the relationship subgraph with edges colored/dashed
      by `relationship_type` and a click-to-filter relationship-type legend — identical to what
      the removed Relationship Network tab rendered (no regression of
      `relationship-network-edge-color-and-legend-filter.md`).
- [ ] With the toggle off, the graph renders the full entity population exactly as before.
- [ ] `/api/merges` still responds and Search / Probe's pre-verified example-query chips still
      work; `tests/test_viz_endpoint_sync.py` passes unchanged with respect to that route.
- [ ] Search / Probe can list all merged entities with no query entered, so the no-query browse
      capability Record Merges uniquely offered is preserved.
- [ ] No tab, section, nav button, or renderer for `merges` or `network` remains in the served
      HTML or the snapshot.
- [ ] `visualization-api-reference.md`'s tab inventory, de-duplication rule, and endpoint/tab
      cross-reference all describe six tabs, and the reversed ruling on Relationship Network is
      stated rather than silently deleted.
- [ ] The offline snapshot still opens with no server and no network (INV-091), and the
      completion-gate artifact check (INV-077) still passes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      contract change applies to a visualization server written in any language (INV-090).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — remove the `merges` and `network`
  tabs (sections `:626-633`, `ALL_TABS` `:637`, `tabApplicable` `:649`, `drawFor` `:655-656`,
  `drawMerges()`, `drawNetwork()`); add `graphMode` to `drawGraph()` and the toggle to
  `addGraphControls`; keep `/api/merges`; add the no-query browse to Search / Probe.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — tab inventory (`:397-405`), de-duplication ruling (`:407-420`), endpoint/tab
  cross-reference (`:559-560`), toggle documentation.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  any guided-tour prose that walks the removed tabs.
- `tests/test_viz_endpoint_sync.py` — assert the six-tab inventory matches the contract, and
  that `/api/merges` remains served and documented.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Consider removing the 'Record Merges' tab
  from the Truth Set visualization — its per-entity info is a subset of 'Search / Probe'"
  (2026-07-25, Module Truth Set visualization; `Source: bootcamper-reported`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add an 'all entities / relationship
  subgraph' toggle to Entity Graph, removing the separate Relationship Network tab"
  (2026-07-25, Module Truth Set visualization; `Source: bootcamper-reported`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Positive feedback — the customized Truth
  Set visualization (Record Merges removed, Entity Graph relationship toggle) looks great"
  (2026-07-25, Module Truth Set visualization; `Source: bootcamper-reported`) — the port-ready
  implementation record for the two entries above.
- Priority: Medium (the confirming entry is filed High; the two defect entries are Medium)
- Related specs: `specs/relationship-network-edge-color-and-legend-filter.md` (behavior that
  must survive the fold), `specs/consolidate-merge-statistics-and-results-dashboard-tabs.md`
  (the prior application of the same de-duplication rule),
  `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md` (the existing graph
  control panel this toggle joins),
  `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md`,
  `specs/rebuild-viz-snapshot-after-customization.md`.
