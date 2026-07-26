# Assign visualization source colors from the data sources actually present

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Building the Module 7 results visualization on the shipped `scripts/senzing_viz_server.py` /
`scripts/brand_tokens.py` reference, the data-source node colors came from a `SOURCE_COLORS` map
keyed by the **Truth Set's** source names (`CUSTOMERS`, `REFERENCE`, `WATCHLIST`). This project's
sources — `PPP_LOANS`, `EQUIFAX`, `NOMINO-RISK` — match none of those keys, so **all three**
silently fell through to the same fallback color. The graph's data-source legend and node coloring
were useless precisely where cross-source structure is the thing worth seeing.

Module 7 is the payoff module, and this reduces its centerpiece to a monochrome hairball for
**every** bootcamper — no bootcamper uses the Truth Set's source names for their own data, by
definition. It fails silently: a graph renders, just uninformative. A bootcamper who did not build
the server themselves cannot distinguish a bad default from genuinely unclustered data.

This is a concrete instance of the "scale principle" warning already in
`visualization-api-reference.md` — defaults chosen against the Truth Set must be re-reviewed for the
bootcamper's real data. That file already requires legends be "generated FROM the data"; the color
assignment needs the same treatment.

## Root cause

`plugins/senzing-bootcamp/scripts/brand_tokens.py:67-72`:

```python
SOURCE_COLORS = {
    "CUSTOMERS": EMBER_CORE,
    "REFERENCE": "#3B6EA5",
    "WATCHLIST": "#C8922A",
}
FALLBACK_COLORS = ["#8b5cf6", "#ec4899", "#0ea5e9", "#a3a34a", "#ef4444", "#14b8a6"]
```

`SOURCE_COLORS` is a name-keyed lookup over three Truth Set sources. Consumption is at
`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:638-639`:

```javascript
const SRC_COLORS=__SRC_COLORS__;
function color(src){return SRC_COLORS[src]||"#8b5cf6";}
```

Every unrecognised source collapses to the single hardcoded literal `#8b5cf6`. There is no
per-source assignment and no distinctness guarantee.

`FALLBACK_COLORS` — the six-color palette that exists for exactly this purpose — is imported into
the server at `senzing_viz_server.py:95` (and inlined as `_FALLBACK_COLORS` at `:82` for the
import-failure path) and then **never used anywhere**. The mechanism to fix this was already
shipped; nothing wired it up. The JS fallback literal `#8b5cf6` happens to equal
`FALLBACK_COLORS[0]`, which is why one source looks correctly colored and the rest look identical to
it.

## Proposed change

Assign colors to the sources that are actually present, at model-build time.

**1. Add a helper to `brand_tokens.py`:**

```python
def color_for_sources(sources):
    """Map the data-source codes actually present to distinct colors.

    Truth Set names keep their preferred assignments; every other source takes the
    next unused color from FALLBACK_COLORS, cycling if there are more sources than
    colors. Ordering is deterministic (sorted) so a rebuild yields the same legend.
    """
```

Rules:

- `SOURCE_COLORS` becomes **preferred assignments, never the sole source of truth** — a source named
  `CUSTOMERS` still gets ember, so the Truth Set visualization is unchanged.
- Every other source takes the next unused color from `FALLBACK_COLORS`, skipping any color already
  claimed by a preferred assignment so two sources cannot collide.
- Assignment is **deterministic** (sort the source codes) so the same data yields the same legend on
  every rebuild — otherwise a re-rendered snapshot or a re-captured screenshot disagrees with the
  recap prose describing it.
- Cycle `FALLBACK_COLORS` when there are more sources than colors, and vary a second visual channel
  (e.g. node stroke) on the second cycle so a 7+-source model stays readable rather than silently
  reusing a color.
- `SIGNAL_GREEN` stays excluded — it is reserved for live/resolved states and is explicitly not a
  categorical data-source color (`brand_tokens.py:20-21`, `:63-66`).

**2. Use it in the shipped server.** Build the source→color map from the discovered source codes when
the entity model is built, and pass that map through the existing `__SRC_COLORS__` substitution
(`senzing_viz_server.py:1124`, via `_script_json`). Then `color(src)` is a straight lookup with no
meaningful fallback path. Keep a last-resort fallback for a source that somehow was not in the model,
but make it visually distinct from every assigned color rather than equal to `FALLBACK_COLORS[0]`.

**3. Mirror it in the import-failure inline fallback** (`senzing_viz_server.py:81-105`) so a server
running without `brand_tokens` behaves the same, per the module's own fallback contract, and keep
`tests/test_brand_sync.py`'s equality assertion satisfied.

**4. Make it contract, not implementation detail.** State in
`module-03b-truthset-visualization/visualization-api-reference.md` — alongside the existing
"legends are generated FROM the data" requirement — that data-source colors are assigned from the
source codes present in the model, and that a name-keyed palette is not acceptable. That is what
makes the rule bind for a visualization server written in any language (INV-090), not just the
bundled Python reference.

## Acceptance criteria

- [ ] A model built from sources that match none of the Truth Set names (e.g. `PPP_LOANS`,
      `EQUIFAX`, `NOMINO-RISK`) renders each source in a **distinct** color, in both the graph nodes
      and the legend.
- [ ] A model built from the Truth Set (`CUSTOMERS`, `REFERENCE`, `WATCHLIST`) renders exactly the
      colors it does today — no visual regression to the Truth Set visualization.
- [ ] A mixed model containing one Truth Set name and two others gives all three distinct colors,
      with no other source assigned the Truth Set name's preferred color.
- [ ] Assignment is deterministic: rebuilding the same model produces the same source→color map, so a
      re-rendered snapshot matches an earlier screenshot and its caption.
- [ ] A model with more sources than `FALLBACK_COLORS` has entries stays legible — colors cycle and a
      second visual channel distinguishes the repeat.
- [ ] `SIGNAL_GREEN` is never assigned as a data-source color.
- [ ] `FALLBACK_COLORS` is actually consumed; no unused palette constant remains, and no hardcoded
      per-source color literal remains in the JS.
- [ ] The behavior is identical whether `brand_tokens` imports successfully or the inlined fallback is
      used; `tests/test_brand_sync.py` passes.
- [ ] `visualization-api-reference.md` states the data-driven color requirement as contract.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      requirement binds any-language visualization servers (INV-090), not only the Python reference.

## Affected files

- `plugins/senzing-bootcamp/scripts/brand_tokens.py` — add `color_for_sources()`; document
  `SOURCE_COLORS` as preferred assignments rather than the full map (`:63-72`).
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — build the source→color map from the
  discovered sources and pass it via `__SRC_COLORS__` (`:1124`); simplify `color(src)` (`:638-639`);
  mirror in the inline fallback (`:81-105`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — state that source colors are assigned from the sources present, alongside the existing
  legend-from-data requirement.
- `tests/test_brand_sync.py` — cover `color_for_sources()` distinctness, determinism, Truth Set
  preference, and the token/inline-fallback equality.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "`brand_tokens.SOURCE_COLORS` only names Truth
  Set sources, so Module 7 graphs render every real data source the same color" (2026-07-26, Module
  Query, Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- Related specs: `specs/apply-senzing-style-guide-to-deliverables.md` (established the brand tokens
  and INV-081), `specs/truthset-viz-graph-label-toggles-and-scale-aware-defaults.md` (the same
  chosen-against-the-Truth-Set defect class for labels),
  `specs/consolidate-module7-visualizations-as-truthset-app-tabs.md`,
  `specs/visualization-server-in-chosen-language.md` (INV-090 — why this must be contract),
  `specs/final-review-doc-coherence.md` (prior brand-token/fallback sync finding).
