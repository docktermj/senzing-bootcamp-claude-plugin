# The Entity Graph legend labels per-source participation counts as `Single-source:`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Entity Graph legend's second block is headed `Single-source:` and lists each data
source with a count. On a two-source run those counts were `CRM_CUSTOMERS 65` and
`WEBSTORE_ACCOUNTS 70` against a total of 121 entities, of which 14 drew on both sources.

The arithmetic identifies what the numbers actually are:

```text
65 + 70 − 14 = 121   (inclusion–exclusion over the entity population)
```

They are **participation** counts — every entity drawing on that source, cross-source
entities included. The true single-source figures were 51 and 56.

⛔ **The counts are individually correct and the label is what is wrong**, which is why no
plausibility check catches it. Each figure agrees with the totals shown everywhere else in
the app, so nothing looks inconsistent; a bootcamper reading the legend simply concludes
that 65 entities are CRM-only.

The heading directly above it makes the misreading the natural one:

```text
Entities in more than one source have their own color:
  <combination rows>
Single-source:
  CRM_CUSTOMERS   65
  WEBSTORE_ACCOUNTS 70
```

Two blocks, the first explicitly about multi-source entities, the second labeled
single-source — the pair reads as a partition of the entity population. It is not one:
the 14 cross-source entities are counted in the combination block **and** in both rows
below it.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1160` — `counts` is accumulated by
walking every source on every node:

```javascript
const counts={};(nodes||[]).forEach(function(n){(n.data_sources||[]).forEach(function(s){counts[s]=(counts[s]||0)+1;});});
```

An entity with `data_sources: ["CRM_CUSTOMERS","WEBSTORE_ACCOUNTS"]` increments both, which
is participation by construction. `:1180` then labels the block that renders those counts:

```javascript
l.append("div").attr("class","why").style("margin","6px 0 4px").text("Single-source:");
```

**Everything else about the row is already participation-shaped**, which is why the label
is the defect rather than the computation:

- the tooltip at `:1188` is `"Show only " + s`, a filter over the source, not over
  single-source entities;
- the click handler at `:1190-1196` keeps a node when **any** of its sources is still on
  (`(d.data_sources||[]).some(...)`), so clicking `CRM_CUSTOMERS` shows all 65, including
  the 14 that also carry `WEBSTORE_ACCOUNTS`;
- the swatch is `color(s)`, the per-source color, while a cross-source entity renders in
  its own combination color from `srcKeyOf(n)` — so the swatch beside `CRM_CUSTOMERS 65` is
  not even the color those 14 entities are drawn in.

⚠️ **The heading is also conditional in a way that hides the bug from the simple case.**
`:1180` sits inside `if(combos.length)`, so on a single-source run — or any run where no
entity spans sources — the block has no heading at all and the counts are unlabeled and
correct. The wrong label appears only when cross-source entities exist, which is exactly
the run where participation and single-source diverge, and exactly the run the module is
built to demonstrate.

## Proposed change

1. **Relabel the block `Entities per source:`** and keep the counts as they are. This is
   the option the entry recommends and the one the surrounding code already implements:
   the rows filter by participation, the counts are participation, and only the heading
   disagrees. Recomputing to true single-source counts would instead put the label in
   agreement with the heading and out of agreement with the click behavior, the tooltip
   and the swatch — three changes to avoid one.
2. **Make the two blocks readable as overlapping rather than disjoint.** With the first
   heading still reading "Entities in more than one source have their own color", a reader
   needs one clause telling them the per-source rows include those entities too. Put it in
   the block's own title attribute or as the `why` line, in the app's existing voice.
3. **Do not drop the conditional heading.** When there are no combinations the per-source
   block should still be labeled — the label is correct in that case and its absence is
   only accidentally harmless.

## Acceptance criteria

- [ ] No legend block in the bundled visualization server labels participation counts as
      single-source.
- [ ] The per-source block carries a heading whether or not combination rows are present.
- [ ] The legend states that an entity drawing on more than one source is counted in each
      of its sources' rows, so the two blocks are not read as a partition.
- [ ] On a fixture with a known overlap, the sum of the per-source counts minus the
      combination counts equals the entity total, and the rendered legend does not claim
      those per-source figures are single-source entities.
- [ ] The click-to-filter behavior, the tooltip and the swatch color are unchanged — this
      is a labeling fix, and altering the counts would desynchronize them.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The reference server is Python by INV-090's carve-out for the plugin's own apparatus;
      the rule being fixed is a statement about the legend's meaning and must be carried by
      `visualization-api-reference.md`, which every non-Python bootcamp builds from.

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the legend heading at `:1180`
  and the block it introduces (`:1182-1196`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the legend contract, so a bootcamp building its own server in another language does not
  reproduce the same label.
- `tests/` — guard asserting no legend heading claims single-source over participation counts.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Entity Graph legend labels per-source participation counts as \"Single-source:\"" (2026-08-24, Module Query, Visualize and Discover, step 3c; `Source: self-observed (assistant retrospective)`)
- Priority: Medium — the figures are correct and the conclusion drawn from them is not; nothing on screen contradicts the misreading.
- MCP re-check: n/a (no Senzing fact) — the defect is arithmetic and labeling in the plugin's own bundled server. The entity and source counts come from the loaded data, not from an MCP route.
- Upstream: not applicable — this is plugin code.
- Related specs: `specs/graph-nodes-are-colored-by-their-first-data-source.md` (established the combination-color encoding and the combination rows this block sits beneath), `specs/source-colors-from-discovered-data-sources.md`, `specs/relationship-network-edge-color-and-legend-filter.md`, `specs/source-encoding-collides-past-twenty-four-sources.md`

## The general shape

The combination block was added so that a color a viewer sees always has a row naming what
it means — the comment at `:1161-1163` says exactly that. Adding it gave the pre-existing
per-source list a neighbor, and the heading written to separate the two described the
relationship the author expected rather than the one the code computes. A count's label is
a claim about its denominator, and this one was never the denominator in use.
