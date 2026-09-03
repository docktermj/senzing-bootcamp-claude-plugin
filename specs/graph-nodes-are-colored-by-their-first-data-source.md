# Graph nodes are colored by their first data source, so cross-source entities render as single-source

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 7's results app, built on the shipped reference server as step 3c instructs, rendered
**1,951 cross-source entities in the single-source `GLEIF` color** — with a legend that positively
implied they were GLEIF-only. The headline result of the entire bootcamp, vendors found in more than
one system, was invisible in the tab built to show it.

⛔ **It does not look broken.** The graph renders, the legend is populated, every count is correct,
and the picture is simply wrong. Step 3c states the operative risk itself — *"the bootcamper cannot
tell a bad default from bad data"* — and then ships a default that fails exactly that test. A guide
who follows the instruction to model on the reference server, and who does not independently check
what the colors encode, hands over a keepsake that understates the result.

## Root cause

**One node, many sources, and the renderer takes the first one.**
`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:921-923`:

```javascript
node.append("circle").attr("r",radius).attr("fill",function(d){return color(d.data_sources[0]);})
  .attr("stroke",function(d){return srcStrokeW(d.data_sources[0])?srcStroke(d.data_sources[0]):null;})
  .attr("stroke-width",function(d){return srcStrokeW(d.data_sources[0])||null;});
```

`d.data_sources[0]` is the first entry of a sorted list, so a node's color is decided by whichever
of its sources sorts first — `GLEIF` for every cross-source entity in this dataset. Fill, stroke and
stroke width all read index `0`, so the entire visual encoding of a multi-source entity is the
identity of one arbitrary member of its source set.

**On the Truth Set this is invisible**, which is why it survived. Most Truth Set entities sit in a
single source, so `data_sources[0]` *is* the entity's source and the encoding looks correct — the
scale-principle trap `visualization-api-reference.md` already warns about, reached through a
different door.

**This is not what `source-colors-from-discovered-data-sources` fixed.** That spec (implemented)
corrected *which colors exist* — the palette was keyed to the Truth Set's source names, so a
bootcamper's own sources all fell through to one fallback. `color_for_sources(...)` at `:1445` now
allocates over discovered sources. It never touched *which of an entity's sources selects the
color*, so a correct palette is now applied to the wrong member.

**A second, smaller defect in the same tab: the payload is uncapped.** `Model.graph()` at `:472-485`
returns `nodes = list(self.entities.values())` — every entity, 5,678 of them here, 3,692 of which
are unconnected singletons — and `write_snapshot` embeds that payload whole (`:1700`,
`"graph": model.graph()`).

⚠️ **The rendering half of this is already fixed and must not be re-specced.** `visualization-legibility-at-production-scale`
(implemented) added the scale-aware subgraph default: `GRAPH_SUBGRAPH_DEFAULT_ABOVE=400` at `:826`,
applied at `:874`, with the explanatory note at `:1019-1021` — so above 400 entities the tab already
opens on the relationship subgraph rather than the hairball. What that fix did **not** do is bound
the payload: the client filters what it draws, the server still ships every node, and the
self-contained snapshot carries all of them. So the remaining defect is size and portability of the
artifact, not legibility of the view.

## Proposed change

Specify both as **behavior** in `visualization-api-reference.md` so a server in any language inherits
them (INV-002/INV-090/INV-104), then implement in the Python reference.

1. **Color a node by its source *combination*, not by one member.** The key is the entity's sorted
   source set (`GLEIF|LEI`, not `GLEIF`), so a cross-source entity is visually distinct from every
   single-source entity. Where an entity has one source the key degenerates to that source and Truth
   Set behavior is unchanged — which is the property that makes this safe to ship.
2. **Put combinations in the legend**, labeled as combinations, so the encoding is readable rather
   than merely different. A color a viewer cannot name is not an improvement.
3. ⛔ **Allocate every key in one pass.** Two separate `colorForSources()` calls each restart at the
   top of the palette and reproduce the collision this fixes — the failure the reporter hit while
   fixing it by hand. The allocation is one call over the full key set, and a test should pin that
   two keys never share a color.
4. **Fix stroke and stroke width with the fill.** All three read `data_sources[0]`; leaving two of
   them on the first-source rule would keep a partial version of the same misencoding.
5. **Bound the graph payload, and report the bound.** Cap the node set the endpoint emits, rank
   candidates by **source span first** (entities spanning most sources are the ones worth seeing)
   then connectivity, and carry the total and the cap in the payload so the UI can state what it is
   showing rather than implying it is everything. The existing subgraph note at `:1019-1021` is the
   model for the wording.

## Acceptance criteria

- [ ] A multi-source entity renders in a color distinct from every single-source entity's color,
      asserted on a fixture with at least two sources and a genuine cross-source entity.
- [ ] Fill, stroke and stroke width are all derived from the source-combination key; no rendering
      path reads `data_sources[0]`.
- [ ] The legend lists combination entries and labels them as combinations.
- [ ] Color allocation happens in a single pass and no two distinct keys collide — pinned by a test,
      since the two-call collision is the specific error made while fixing this by hand.
- [ ] **Truth Set output is unchanged** — verified by rendering it before and after, since the
      degenerate single-source case is the compatibility guarantee this rests on.
- [ ] `/api/graph` reports `total` and whether a cap was applied; the UI states what it is showing.
- [ ] The snapshot embeds the capped set, and the file is measurably smaller on a
      multi-thousand-entity fixture.
- [ ] The behavior is stated in `visualization-api-reference.md` so a non-Python implementation
      inherits it (INV-090/INV-124), not only in the Python reference.
- [ ] Verified against a **production-scale** dataset (thousands of entities, real multi-source
      overlap), not the Truth Set — both defects pass every check the Truth Set can run.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — node rendering (`:921-923`), the color
  helpers (`:796-803`), the allocation call (`:1445`), `Model.graph()` (`:472-485`), and the
  snapshot payload (`:1700`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the color-encoding and graph-payload contract.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  step 3c, which points at the reference server.
- `tests/` — combination coloring, palette-collision, Truth Set invariance, payload cap.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Module 7 visualization inherits Truth Set scale defaults that misrepresent real data" (2026-08-16, Module Query, Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: **High.** It silently misreports the bootcamp's headline finding in the artifact built to present it, on every dataset whose entities span sources — which is every dataset the bootcamp is for. Both the recap keepsake and the live app carry it.
- MCP re-check: **n/a (no Senzing fact).** Both defects are in the plugin's own reference server — a rendering rule and a payload shape it authors. No SDK method, flag or response schema is asserted; `data_sources` is a field the plugin builds itself in `Model`. No absence about the server is relied on. Server **1.32.9** (`get_capabilities`, 2026-08-16) recorded for this run.
- Upstream: not applicable — routed `plugin`.
- Related specs: `specs/source-colors-from-discovered-data-sources.md` (implemented; fixed which colors exist, not which one a node gets — the nearest prior art and the reason this survived), `specs/visualization-legibility-at-production-scale.md` (implemented; shipped the subgraph default that already covers the legibility half of the report), `specs/relationship-network-edge-color-and-legend-filter.md`, `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md`, `specs/visualization-contract-and-reference-server-disagree-on-record-fields.md`, and INV-090, INV-104, INV-124.

## One narrowing of the feedback entry

The entry reports two defects and asks for both to be moved into the shipped server. Its first —
*"the graph endpoint emits every entity … an unreadable hairball"* — is **half-shipped already**:
`GRAPH_SUBGRAPH_DEFAULT_ABOVE=400` has defaulted the tab to the relationship subgraph since
`visualization-legibility-at-production-scale` landed, with a note stating what is shown. The
reporter's app was ported to Java from the Python reference and may predate or omit that default.
What genuinely remains from that half is the **payload and snapshot size**, which the client-side
default does not address, and it is carried here as the smaller of the two changes. The color defect
is untouched by any implemented spec and is the reason this spec exists.

## Deviations from this spec, and why (2026-08-17)

1. ⛔ **"Truth Set output is unchanged" is not literally achievable, and asserting it would have
   been asserting the defect.** The precise guarantee — the one the spec's own proposed change 1
   states — is that **single-source** entities are unchanged, because the combination key
   degenerates to the bare source code. Truth Set entities that genuinely span sources now render
   in a combination color, which is the fix working, visible there too. What is asserted instead
   is the checkable form: the Truth Set's source names keep their **preferred** palette
   assignments when combination keys are added to the allocation, so no single-source entity
   changes appearance.

2. **The graph cap is `GRAPH_NODE_CAP = 1500`.** The spec requires a bound and a report but names
   no number. 1500 sits well above the `GRAPH_SUBGRAPH_DEFAULT_ABOVE = 400` threshold at which the
   client already switches to the relationship subgraph, so the cap bounds payload and snapshot
   size without changing what any current view draws.

3. ⚠️ **Not verified against a production-scale dataset**, which is the spec's ninth criterion.
   This environment has no Senzing engine and no multi-thousand-entity corpus, so the cap, the
   ranking and the combination coloring are verified on synthetic models carrying the reported
   shape (two sources, a genuine cross-source entity; 61 entities with a 2- and a 3-source
   member). ⛔ **The snapshot-size criterion is therefore implemented but unmeasured:** the cap is
   asserted to be applied at both the endpoint and the snapshot payload by reading the call sites,
   and the cap's behavior is tested directly, but no snapshot was rendered before and after on a
   large fixture. That measurement needs `dry-run`.

4. **`tests/test_brand_sync.py` needed updating** — not in `## Affected files`, but required: it
   pinned the node's stroke expression as the literal `d.data_sources[0]` form this spec replaces.
   Its stated criterion (swatch and mark must agree for one key) is unchanged and still asserted;
   only the expression it pins moved to `srcKeyOf(d)`.

## Citation correction (2026-09-02)

This spec cited **INV-124** as part of the reason the visualization contract binds every language. It does not: INV-124 governs the **tab hooks the recap capture depends on** (`tab-<id>`, `navbtn-<id>`, `activate()`, deep-linking), and its "in whichever language it is generated" clause scopes *its own* subject. The rules that carry the any-language claim are **INV-002** (the SBCP is language-agnostic) and **INV-090** (the server is built in the chosen language, modeled on the `visualization-api-reference.md` contract). Corrected in place because implementing this spec copied the wrong trio into shipped text, where a reader following the citation reached a rule about tab ids (`specs/inv-124-is-cited-as-the-any-language-rule-it-is-not.md`).
