# Keep the visualization legible at production scale: distinguishable match-key labels and a navigable graph

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Pointing the visualization at real resolved data — **2,799 entities, 4,464 relationships** — surfaced
two defects the Truth Set's 84 entities cannot expose.

**Match Keys tab.** Real match keys are long, e.g.
`+NAME+ADDRESS+NATIONAL_ID+OTHER_ID+REGISTRATION_DATE+REGISTRATION_COUNTRY+LEI_NUMBER`. Labels are cut
off from the **left**, so the four highest bars all render as `...ISTRATION_COUNTRY+LEI_NUMBER` and
cannot be told apart. The counts are correct; the labels are unusable — which is worse than omitting
them, because the chart looks fine. A bootcamper reads four indistinguishable rows and cannot learn
the one thing the tab exists to teach: which feature combinations drove their resolutions.

**Entity Graph.** The scale-aware label default worked correctly — labels auto-hid with an
explanatory note. But with 4,464 edges drawn the graph is a dense mesh with no practical way to
locate a specific entity. It conveys shape only.

Module 7 points this app at the bootcamper's own data, which is routinely far larger than the Truth
Set. The plugin's instruction to re-check visual defaults at actual scale is well-founded; there is
no mitigation beyond the label toggle.

## Root cause

Both are defaults measured against an 84-entity dataset, in a contract that binds every
language implementation (INV-090/INV-104/INV-124).

**Match-key labels — a fixed gutter with no truncation and no overflow handling.**
`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1104`:

```javascript
const W=Math.min(720,box.node().clientWidth),barh=26,mm={t:6,r:44,b:6,l:190},H=…;
```

and `:1110-1111` draws the label with `text-anchor: end` at `x = mm.l - 8`:

```javascript
svg.selectAll("text.k").data(items).join("text").attr("class","k").attr("x",mm.l-8)…
  .attr("text-anchor","end")….text(function(z){return z.match_key;});
```

The gutter is a hardcoded 182 px of usable width. There is **no truncation anywhere in the code** —
the full string is emitted, anchored at its right end, and everything past 182 px extends left of
the SVG origin and is clipped by the viewport. That is why the *head* of each key disappears and the
common tail survives: the discriminating prefix is exactly what gets cut. Nothing degrades and
nothing warns.

There is also no way to recover the full key by hovering: the only `<title>` on the tab is on the
bars (`:1117`), and it reads "Show the entities with this match key" — it does not contain the key.

**Graph density — the mode that would help defaults off.** The relationship-subgraph filter already
exists: `visualization-api-reference.md:412` specifies Entity Graph with a
**"Show only entities with relationships"** mode toggle, and the server filters from the same
`/api/graph` payload (`senzing_viz_server.py:742`). Its default is unconditional — off — so at 2,799
entities the first view is the full population. `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md`
made **label** visibility scale-aware; it did not touch which nodes are drawn, so the hairball
survives the label fix that was supposed to address it.

## Proposed change

Specify both as behaviour in `visualization-api-reference.md` so a server in any language inherits
them (INV-090/INV-124), and implement them in the Python reference.

1. **Never render a clipped match-key label.** Fit the label to the gutter deliberately instead of
   letting the viewport cut it:
   - Preserve the **distinguishing prefix** — truncate from the right or middle-ellipsize
     (`+NAME+ADDRESS+NATIONAL_ID…+LEI_NUMBER`), never from the left.
   - Size the gutter from the data — measure the longest key and widen up to a cap — before
     truncating, so short keys are unaffected and long ones lose as little as possible.
   - Guarantee that no two rendered labels are identical unless their keys are identical. This is the
     testable property; the exact ellipsis strategy is not.

2. **Put the full key within reach.** Add a `<title>` (or equivalent hover affordance) carrying the
   complete match key on the label and the bar. The existing bar title is an action description —
   keep it, and add the key.

3. **Make the relationship-subgraph mode's default scale-aware.** Above an entity-count threshold,
   default Entity Graph to the relationship subgraph rather than the full population, with the
   toggle still available to show everything. State the threshold in the contract so every language
   implementation picks the same behaviour — as the label thresholds already are.

4. **Say why, in the same voice as the label note.** When the subgraph default engages, show an
   inline note: "Showing the N entities that have relationships, of M total — use the toggle to show
   all." Without it the bootcamper cannot tell a default from their data (the reasoning that made the
   label note necessary applies unchanged).

5. **Give the dense graph one way to find something.** At production scale, locating a known entity
   is the missing capability. Reuse what exists rather than adding a surface: let a Search / Probe
   result focus that entity in the graph (the app already has `?q=` deep-linking and click-to-detail,
   INV-124). Specify it as behaviour; a find-by-name box is an acceptable alternative.

6. **Re-check the defaults against a production-scale dataset, not the Truth Set.** The verification
   for this spec must use data of a few thousand entities. Both defects pass every check the Truth
   Set can run.

## Acceptance criteria

- [ ] With match keys of 60+ characters, no two bar labels render identically unless the keys are
      identical, and no label is clipped by the chart's viewport.
- [ ] Truncation preserves the leading segments of the key; the removed portion is the tail or
      middle, never the head.
- [ ] Hovering a bar or its label reveals the complete, untruncated match key.
- [ ] Short match keys (Truth Set scale) render in full, unchanged from today.
- [ ] Above the specified entity threshold, Entity Graph opens on the relationship subgraph with an
      inline note naming both counts; below it, on the full population. The toggle still switches
      both ways.
- [ ] A specific entity can be located in the graph from a search result, without scanning visually.
- [ ] Both behaviours are stated in `visualization-api-reference.md` as contract, with the threshold
      given as a number, so a non-Python server (INV-090) implements the same defaults.
- [ ] Verified against a dataset of at least ~2,000 entities and ~4,000 relationships, by opening the
      rendered app — not by unit test alone (INV-129).
- [ ] Existing tab behaviour is otherwise unchanged: drill-down from a match-key bar still lists its
      entities, and counts remain exact.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — Match Keys label-fitting and hover requirements; the scale-aware subgraph default and its
  threshold in the Entity Graph row (`:412`); the search-to-graph focus behaviour.
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `drawMatchKeys` (`:1100-1121`): gutter
  sizing, prefix-preserving truncation, `<title>` with the full key; the graph's subgraph-mode
  default (`:742` and the tab's init) and the scale note.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  step 3c: re-check defaults at the bootcamper's actual scale, naming these two.
- `tests/` — a rendering test over synthetic long match keys asserting label distinctness, and a
  contract test asserting the threshold appears in the any-language contract.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "visualization defaults degrade at real-world
  scale — truncated match-key labels and an unreadable entity graph" (2026-07-26, Module Query,
  Visualize and Discover; `Source: self-observed (assistant retrospective)`; `Routing: plugin`)
- Priority: Medium
- Related specs: `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md` (made label
  defaults scale-aware; this extends the principle to node selection and chart labels),
  `specs/consolidate-truthset-viz-merges-and-network-tabs.md` (established the
  relationship-subgraph toggle this changes the default of),
  `specs/source-colors-from-discovered-data-sources.md` (INV-127 — the same
  tuned-against-the-Truth-Set failure class), `specs/visualization-why-how-and-clickable-histogram.md`,
  `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md` (the match-key drill-down this
  must not disturb)

## Invariants introduced

- `INV-153` — A truncated chart label MUST stay distinguishable, expose its full value on hover, and
  never lose its leading characters; match keys require middle-ellipsis (recorded in
  `specs/INVARIANTS.md`).
- `INV-154` — A legibility-governing visualization default MUST be scale-dependent with the
  threshold stated as a number in the any-language contract (recorded in `specs/INVARIANTS.md`).

## Correction applied during implementation (2026-07-26)

This spec's proposed fix — "truncate from the **right** (or middle-ellipsize)" — is only half
correct, and the obvious reading of it does not work. Right-truncation preserves the prefix, which is
the direction the report asked for, and the four highest bars in the reported dataset **still**
render identically: they share a 52-character prefix and differ only in the final segment. Measured
during implementation, then pinned by `test_head_only_truncation_would_not_pass` so the
plausible-looking fix cannot return. Middle-ellipsis is what distinguishes them, and the contract now
requires it rather than offering it as an alternative.

## Verification limitation

The acceptance criterion asked for verification "against a dataset of at least ~2,000 entities and
~4,000 relationships, by opening the rendered app". Real resolved Senzing output at that scale was
not available in the implementation environment. Instead the shipped expressions were transcribed and
exercised at 84 / 2,799 / 5,000 entities (label distinctness, gutter fit, prefix survival, threshold
behaviour, the no-relationships case), and both changed functions were syntax-checked with
`node --check`. That proves the arithmetic guarantees; it does **not** prove the graph reads better at
2,799 entities. Someone with real resolved data should open the app and confirm the subgraph default
is the right call at that scale.
