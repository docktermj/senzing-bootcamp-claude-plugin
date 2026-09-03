# The graph tab's capture budget does not converge at Truth Set density

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`capture_screenshots.py` gives animated tabs a longer virtual-time budget than static ones:

```python
_CHROME_VIRTUAL_TIME_MS_ANIMATED = 30000
_ANIMATED_TABS = frozenset({"graph", "network"})
```

At **Truth Set density that budget has not converged**, so the Entity Graph screenshot embedded
in every recap is a picture of a still-moving layout. Measured 2026-09-03 (Senzing SDK **4.4.0**,
build 4.4.0.26242; the full Truth Set — 159 records over CUSTOMERS/REFERENCE/WATCHLIST → **85
entities**, 54 merged, 17 cross-source, 65 relationships; 1440×900):

| virtual-time budget | two captures of the identical snapshot |
|---|---|
| **30 000 ms** (what ships) | **differ by 5,326 pixels** |
| 120 000 ms | **byte-identical, 0 differing pixels** |

The same check at the 2-entity scaffold fixture is byte-identical at 30 s, which is why this was
never seen: the budget is sufficient for a toy graph and insufficient for the dataset the module
actually loads.

**Two costs, and the second is worse than a cosmetic one.**

- **(a) The keepsake is a random draw.** Module 3b's graph is the bootcamp's showpiece and is
  embedded into the recap (INV-146/INV-147). Two runs of the same bootcamp on the same data
  produce materially different images, and neither is the settled layout.
- **(b) The plugin blames the reader for it.** `module-completion.md`'s post-capture check says:

  > ⚠️ **Open the Entity Graph image and check the nodes are spread, not bunched in one corner.**
  > A graph tab whose force simulation was restarted or captured too early produces a valid PNG
  > of an empty-looking graph at exit 0 — the helper gives animated tabs a longer settle budget
  > and the app's `activate()` no longer redraws an already-active tab…

  The reassurance that "the helper gives animated tabs a longer settle budget" is exactly the
  claim this measurement contradicts at real density, and the reader is left to re-run by hand
  with no way to know how long is long enough.

## Root cause

A constant tuned against a fixture much smaller than the shipped dataset. Convergence time grows
with node count — and the 2026-09-02 label-aware collision term (`INV-002/INV-090` graph rules in
`visualization-api-reference.md`) makes each tick's force balance settle more slowly, so the
budget got tighter in the same change that made the labels legible. ⚠️ **That change's own note
says to "verify at the budget your capture actually uses rather than assuming the pre-change
settling time still applies"** — this spec is that verification, and the answer is that the budget
is too small.

`plugins/senzing-bootcamp/scripts/capture_screenshots.py:269-270` — the constant and the tab set.

## Proposed change

1. **Scale the animated-tab budget with node count, or settle deterministically rather than by
   deadline.** Two shapes worth weighing, and this spec deliberately does not pick:
   - raise the budget as a function of the graph's node count (the snapshot knows it — the app
     reads `entities_total`), with a floor at today's 30 s so small graphs do not slow down; or
   - stop guessing: have the app signal settledness (d3's simulation `end` event, or an attribute
     set when `alpha < alphaMin`) and have the capture wait for that signal, which is what
     `_ACTIVATE_JS` already does for tab activation.
   ⚠️ The second is strictly better if the app can be made to expose the signal, because it is
   correct at every density instead of at the densities someone measured. It also binds every
   language implementation (INV-002/INV-090), so it belongs in
   `visualization-api-reference.md` if chosen.
2. **Correct the reassurance in `module-completion.md`.** Whatever the budget becomes, the note
   must not tell the reader the settle budget is handled while a denser graph can still be
   captured mid-flight. Say what to check and what to do when it fails.
3. ⛔ **Do not simply raise the constant to 120 000 and stop.** 120 s converged at 85 entities;
   it says nothing about Module 7, where the same app is reused for production-scale data and the
   node cap is 400 (`GRAPH_SUBGRAPH_DEFAULT_ABOVE`). A fixed number is what created this defect.

## Acceptance criteria

- [ ] Two captures of the same snapshot at Truth Set density (159 records → ~85 entities) are
      byte-identical, demonstrated by running the capture twice and comparing.
- [ ] The same holds at a node count near the subgraph-mode threshold (400), or the guidance
      states the density above which the graph tab is captured in subgraph mode and why that is
      sufficient.
- [ ] A small graph is not made slower than it needs to be — the 2-entity fixture still converges
      and does not wait 120 s for it.
- [ ] `module-completion.md` no longer asserts that the settle budget is handled without saying
      what to do when a capture is visibly unsettled.
- [ ] Negative control: restore the budget to a value that does not converge and confirm the
      determinism check fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — the animated-tab budget
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — only if the settled-signal route is chosen
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — only if a signal becomes contractual
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — the post-capture reassurance
- `tests/` — a determinism guard, gated on a browser being available

## Source

- Feedback: follow-up measurement on `entity-graph-node-occludes-a-neighbors-label-at-small-n`, 2026-09-03 (`Source: self-observed (assistant retrospective)`)
- Priority: **Medium** — no data is wrong and nothing fails; the cost is that the bootcamp's showpiece keepsake is a non-reproducible draw from an unsettled layout, and the shipped guidance tells the reader that this is already handled
- MCP re-check: **n/a (no Senzing fact).** The subject is the plugin's own capture helper and its own renderer. The Truth Set was fetched via `get_sample_data(dataset='truthset', source='list')` on **server 1.36.0, 2026-09-03** for its download URLs and record counts (120 + 22 + 17 = 159); the resolution figures (85 entities, 54 merged, 17 cross-source, 65 relationships) are a live-engine observation on SDK 4.4.0 build 4.4.0.26242, not an MCP claim (INV-080/INV-149).
- Upstream: not applicable — no server behavior is implicated.
- Related specs: `specs/entity-graph-node-occludes-a-neighbors-label-at-small-n.md` (whose fix made settling slower, and whose own note asked for this verification), `specs/visualization-legibility-at-production-scale.md` (the density work this sits beside)
