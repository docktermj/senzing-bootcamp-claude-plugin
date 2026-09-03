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

## Root cause CORRECTED, and the spec is not implemented (2026-09-03)

⛔ **This spec's root cause is wrong, and its central measurement does not reproduce.** Attempting
the maintainer's chosen fix (the settled-signal route) surfaced the real cause, which is far worse
and changes what the fix has to be. The spec stays **open**; what shipped is only the part the
maintainer approved outright.

### What does not reproduce

The spec claims 30 000 ms "has not converged" while 120 000 ms is byte-identical. Re-measured on
the same data and machine, five captures per budget:

| budget | five captures |
|---|---|
| 30 000 ms | **1 distinct** image |
| 120 000 ms | **1 distinct** — and the *same* image as 30 s |
| 300 000 ms | **2 distinct** |

So the deadline does not select the layout, and lengthening it made reproducibility **worse**.
⚠️ Real time is nearly flat across budgets — **0.6 s at 30 s, 0.7 s at 300 s** — because virtual
time advances as fast as the page allows, so "raise the budget" costs almost nothing and buys
almost nothing. The spec's own 5,326-pixel figure was taken on a day the machine was under load
from concurrent Senzing work; the variation is load-dependent, not budget-dependent.

### The real cause

**The force layout runs about five of the ~300 ticks it needs.** Instrumented through
`capture_screenshots.py`'s own path, on the 85-entity Truth Set, with the tick count rendered
into the captured PNG and read back from the image: **TICKS 5**. Under `--dump-dom` at budgets
from 5 s to 300 s the count was 2–3. d3's simulation is driven by `requestAnimationFrame`, and
headless virtual time does not advance it — so the budget is irrelevant by construction, and the
2-vs-3-vs-5 spread is a race, which is the run-to-run variation.

The Entity Graph in every recap is therefore **not** a picture of a settled layout captured a bit
early. It is a picture of a layout that has barely started: nodes sit near their initial
phyllotaxis positions, which look plausibly spread out, which is why this was never noticed. The
visual signature is the one `module-completion.md` already tells the reader to look for — nodes
clumped rather than spread — except the guidance frames it as an occasional mishap rather than
what always happens.

⚠️ **This does not invalidate the occlusion measurement in
`entity-graph-node-occludes-a-neighbors-label-at-small-n`.** That comparison held layout fixed and
verified it (all 85 node transforms identical, layout-drift indicator 0), so the 1,713 covered
glyph pixels are real *at the layout the plugin actually captures* — which is the layout that
ships.

### Why the chosen fix cannot be finished without a decision

Driving the layout to completion synchronously (`simulation.tick()` in a loop, which advances the
physics without dispatching events) makes the signal reachable and the render **fully
deterministic** — 5 of 5 captures byte-identical, signal set even at a 3 s budget. But it exposes
two further problems, each masked by the previous one:

1. **Nothing bounds the layout.** `forceCenter` centers the centroid and constrains nothing, so
   the settled 85-entity layout spreads far outside 1440×900 and **most nodes end up off-canvas** —
   losing more of the graph than the clump it replaced. The unsettled layout was accidentally
   mitigating this by never expanding.
2. **Fitting it makes the labels unreadable.** Adding a fit-to-extent transform (the app already
   has `d3.zoom` on the root group) brings all 85 nodes on-canvas, still deterministic — and
   shrinks the 10 px labels to 2–3 px smudges.

So at 85 entities, "settled", "all nodes visible" and "labels legible" cannot all hold in one
1440×900 screenshot. That is a design decision — it touches `LABEL_AUTO_OFF`, and therefore the
already-implemented `visualization-legibility-at-production-scale` — not a defect repair, and it
is the maintainer's call. Both prototypes were reverted rather than shipped.

### What shipped, and what did not

**Shipped** (the maintainer approved INV-298 outright, and Step 5.5 requires citing a minted ID at
the sites it binds):

- the settled signal in the Python reference — cleared as a layout begins, set on d3's `end`
  event, set immediately for an empty graph, and cleared again when a drag restarts the layout;
- **INV-298**, registered and indexed under *Visualization and screenshots*;
- the rule stated in `visualization-api-reference.md`, where it binds every language
  implementation (INV-002/INV-090) — including the reason it must be a DOM attribute rather than a
  JS variable, since the reference's own simulation lives in a top-level `let` that never reaches
  `window`.

**Not shipped, and why:** the capture side. Waiting on the signal is only useful once the signal
can be reached, and reaching it requires the presettle — which requires the layout decision above.
Shipping the wait now would make every graph capture report "proceeded unsettled" on every
bootcamp run, which is honest but is a warning about a defect nobody can act on yet.

## Invariants introduced

- `INV-298` — A visualization view that **animates** to its final layout MUST expose a settled
  signal the capture can wait on: remove `data-graph-settled` from the document element when a
  layout begins, set it to `1` at final positions (immediately where there is nothing to lay out);
  a screenshot of an animated view is taken after that signal rather than on a fixed budget alone,
  and a capture proceeding without it MUST report that it did (recorded in `specs/INVARIANTS.md`,
  approved by the maintainer 2026-09-03).

## Second pass — INV-298's reporting half shipped (2026-09-03)

The first pass registered INV-298 and made the renderer emit the signal, but nothing consumed
it: `capture_screenshots.py` had **zero** references to `data-graph-settled` and still captured
on the fixed budget in silence. ⛔ **That left the plugin out of compliance with an invariant it
had just registered** — the reverse of the usual failure, where a rule ships with no invariant.
Here the ruleset asserted something untrue about the product, and
`test_any_language_contract_complete` could not see it because the rule *was* stated in the
contract; nothing checked the capture obeyed it.

Closed the half that needs no layout decision:

- **Chrome CLI** — reads the signal from the **same invocation** as the screenshot
  (`--dump-dom` rides along with `--screenshot`, verified), so the record can never describe a
  different render than the image it labels.
- **Playwright** — `wait_for_function` on the attribute, bounded by the tab's budget, replacing a
  flat `wait_for_timeout(2500)` that was *shorter* than the CLI path's budget.
- **Selenium** — polls the attribute to the same deadline; the 2.5 s sleep stays as the fallback
  for a page that reports nothing.
- **stderr** — an animated tab captured without the signal is reported, naming INV-298, and
  saying plainly not to re-run expecting a different result and why.
- **the tab manifest** — a per-tab `settled` field (`settled` / `unsettled` / `unknown` / `n/a`),
  which graduation's coverage check already reads, so a reader chasing a clumped-looking graph can
  tell an unfinished layout from a genuine result without re-running anything.

⛔ **`unsettled` and `unknown` are kept apart.** An animated tab starts at `unknown` and only a
backend that actually read the attribute may downgrade it, so a DOM-blind backend
(`wkhtmltoimage`) is never reported as having found an unfinished layout — that would blame the
artifact for the instrument, the reverse of INV-129. ⚠️ The first version of the guard for this
asserted only that the constants and the message existed in the source, which **survived the
exact mutation it was written to catch**: flipping the default from `unknown` to `unsettled` left
all ten tests green, because the Chrome backend overwrites the default before anything observes
it. Replaced with a behavioral assertion that substitutes a DOM-blind backend.

⚠️ **Two existing guards caught a real robustness gap.** `test_snapshot_and_capture_fidelity` and
`test_windows_browser_discovery` mock `subprocess.run`, so `.stdout` was a `MagicMock` and the
regex raised — which in production would fail a capture that had already succeeded, against the
best-effort contract (INV-122). The read is now defensive and leaves the state **`unknown`** when
stdout cannot be read: "we could not look" is not "the layout was unfinished".

**Still open, and why.** The wait half only bites once the signal is reachable, and reaching it
needs the presettle — which needs the layout decision recorded above (settled + all-nodes-visible
+ legible labels cannot all hold for 85 entities in one 1440×900 shot). So the spec's acceptance
criteria — two byte-identical captures at Truth Set density — are **not** met, and this spec is
**not** recorded as implemented. What today's change does is make the defect visible on every
capture instead of silent.

## Implemented (2026-09-03), on the maintainer's layout decision

**Decision:** presettle → fit → labels off for capture above ~40 nodes, interactive untouched.

⚠️ **The spec's title and root cause remain wrong and are left standing as written**, with the
correction above: the budget was never the cause. Implemented against the corrected diagnosis.

### Criteria walk

- **Two captures at Truth Set density byte-identical** — ✅ 3 of 3 identical, then 2 of 2 after the
  label fix, on 159 records → 85 entities. The manifest reads `settled` and the unsettled warning
  is silent.
- **The same near the subgraph threshold (400), or the guidance states why not** — ✅ by
  construction rather than by measurement, and the distinction matters: determinism no longer
  depends on node count *or* on the budget, because the layout is advanced in a **synchronous
  loop** whose length comes from the simulation's own `alphaMin`/`alphaDecay`. There is no race
  left to lose. ⚠️ **Not runtime-verified above 400 entities** — the Truth Set yields 85, and this
  environment has no dataset that reaches the `GRAPH_SUBGRAPH_DEFAULT_ABOVE` boundary; above it the
  app opens in relationship-subgraph mode, which reduces the node count rather than raising it.
- **A small graph is not made slower** — ✅ and it is now *faster*: the capture no longer waits at
  all. An 85-entity capture completes in **0.7 s** real time, the same as before, and nothing waits
  out a budget.
- **`module-completion.md` no longer credits a settle budget** — ✅ the sentence *"the helper gives
  animated tabs a longer settle budget"* is gone (0 occurrences) and replaced by what actually
  happens, citing INV-298/INV-299. Asserted by
  `test_module_completion_no_longer_credits_a_settle_budget`.
- **Negative control** — ✅ six, each restoring green: presettle loop removed, fit call removed,
  capture ceiling raised above the interactive one, ceiling not routed through the shared
  auto-off, fit floor restored to 0.2, and the capture no longer requesting the render. ⚠️ The
  fit control initially failed to fire, because the guard asserted `fitToExtent` was **defined**
  rather than **called** — a guard certifying a definition. Strengthened, then it fired.
- **Cross-platform and language-agnostic** — ✅ SVG/JS plus a query parameter; the rule is stated
  in `visualization-api-reference.md`, where it binds every implementation (INV-002/INV-090).

### What the implementation added beyond the decision

⛔ **Both label sets, not just the names.** The first pass hid only `.node-labels` and left the
**match-key edge labels** as unreadable smudges in the fitted image — visible on inspection of the
artifact, not in any assertion. The ceiling now flows through `addGraphControls`, which owns the
auto-off for both sets, so the on-screen toggles also agree with what was drawn. That reuse is why
the app's own explanatory note (*"Labels hidden — 85 entities would overlap. Use the toggles to
show them."*) appears correctly in the captured image.

⚠️ **The fit's scale floor had to drop from 0.2 to 0.05.** A settled 85-entity layout needs well
under 0.2, and the old floor would have clamped it and left nodes off-canvas — the defect the fit
exists to remove.

## Invariants introduced

- `INV-299` — A screenshot of an animated view MUST be produced by a **capture-oriented render**,
  requested explicitly (`?capture=1`), which drives the layout to completion **synchronously**,
  **fits** it inside the viewport, and **suppresses on-canvas labels above a capture ceiling lower
  than the interactive one**; the interactive view MUST be unaffected (recorded in
  `specs/INVARIANTS.md`, approved by the maintainer 2026-09-03).
