# Make the Relationship Network legend functional: visibly distinct edge colors and click-to-filter

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In the Relationship Network tab, the legend showed three relationship types — "possibly the same
entity", "possibly related", and "disclosed" — but **nothing in the graph itself appeared to use those
colors**. The legend read as decorative rather than functional.

The bootcamper's words: "It's confusing without it — the legend colors feel decorative rather than
functional right now." They also asked that clicking a relationship type in the legend filter the
graph to show only edges of that type.

## Root cause

The contract names the requirement but does not make it verifiable, and specifies no legend
interactivity.

- `visualization-api-reference.md:317` — Relationship Network is specified as "the subgraph of
  entities connected by relationships, **edges colored by relationship type**".
- `phase1-visualization.md:236-238` — same wording: "edges colored by relationship type with a type
  legend".
- `visualization-api-reference.md:60-67, 86-89` — `/api/graph` edges carry `relationship_type`, and
  the edge-discovery guidance says `relationship_type` "reflects the relationship kind (e.g., possible
  match / disclosed / discovered)". **The vocabulary is left open-ended** ("e.g."), with no enumerated
  set and no mapping from type to color.

Two consequences:

1. **No enumerated type→color mapping** means the legend's three labels and the edges' actual
   `relationship_type` values can be built independently and fail to correspond. A legend hardcoded to
   three friendly labels, drawn beside edges whose `relationship_type` values do not match those
   buckets, produces exactly the reported symptom: a legend whose colors appear nowhere in the graph.
2. **No interactivity is specified.** Nothing in the contract requires the legend to be clickable, so
   the filter the bootcamper expected does not exist.

Root cause of the *specific* mismatch in the reported build is **unverified** — it happened in a
session-built Java server not present in this repo, so whether the edges were uncolored, colored from
a different vocabulary, or colored too subtly to distinguish cannot be confirmed from here. The spec
gap above is confirmed and is sufficient to cause it either way.

## Proposed change

1. **Enumerate the relationship-type vocabulary** in `visualization-api-reference.md` for
   `/api/graph`'s `relationship_type` field, confirming the actual Senzing relationship kinds via the
   Senzing MCP server (`search_docs` / `get_sdk_reference`) rather than asserting them — the existing
   "confirm via MCP" note at `visualization-api-reference.md:91-93` already governs this field.
   Give each enumerated type its bootcamper-facing label (e.g. "possibly the same entity", "possibly
   related", "disclosed") so the legend text and the data share one source.
2. **Require a legend built FROM the data, not beside it.** The legend MUST be generated from the
   `relationship_type` values actually present in the rendered edge set — so a type with no edges
   never appears in the legend, and a legend entry always corresponds to visible edges. This is the
   change that makes the reported symptom structurally impossible.
3. **Specify the type→color mapping** from `scripts/brand_tokens.py` (INV-081), and require the colors
   to be **visibly distinguishable** — not color alone: also vary the edge style (e.g. dashed for
   disclosed, solid for possible match) so the distinction survives a monochrome screenshot in the
   recap PDF and is accessible to color-vision-deficient viewers.
4. **Make the legend interactive.** Clicking a relationship type filters the graph to edges of that
   type (and toggles back). Multiple types may be active. Show the active filter state clearly, and
   show a count per type in the legend so the bootcamper knows what they are filtering to before they
   click.
5. **State the same requirement for the Entity Graph's data-source color legend**, which has the
   identical structure (`phase1-visualization.md:229-235`: "Nodes colored by data source … and a
   color legend") and would drift the same way. Generate it from the data sources actually present,
   and make it filter nodes by source.

## Acceptance criteria

- [ ] `/api/graph`'s `relationship_type` has an enumerated vocabulary in
      `visualization-api-reference.md`, MCP-confirmed, each with its bootcamper-facing label.
- [ ] The spec requires the Relationship Network legend to be generated from the `relationship_type`
      values present in the rendered edges — a legend entry can never exist without matching edges.
- [ ] Edge colors come from `scripts/brand_tokens.py` and are paired with a non-color distinction
      (line style), so the types remain distinguishable in a monochrome screenshot.
- [ ] Clicking a legend entry filters the graph to that relationship type and toggles back; active
      filter state and a per-type edge count are visible.
- [ ] The Entity Graph's data-source legend carries the same generate-from-data and click-to-filter
      requirements.
- [ ] Rendering a dataset with only one relationship type shows a one-entry legend, not three.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): stated as
      rendering requirements over `/api/graph`, with no dependency on the Java or Python reference
      build, and works offline in the standalone snapshot (INV-070/INV-091).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  `/api/graph` edge contract (lines ~53-93): enumerate `relationship_type`; tab table (line ~317):
  legend-from-data and click-to-filter requirements
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — Entity
  Graph and Relationship Network tab descriptions (lines ~229-238)
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the reference implementation must
  generate both legends from the data and support filtering
- `plugins/senzing-bootcamp/scripts/brand_tokens.py` — confirm relationship-type edge colors exist as
  tokens; add them if absent

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_12.md` → "Relationship Network legend colors aren't used
  in the graph" (2026-07-23, Truth Set visualization)
- Priority: Medium
- Related specs: `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md` (the other
  graph-rendering gap), `specs/apply-senzing-style-guide-to-deliverables.md` (brand tokens, INV-081),
  `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md`
