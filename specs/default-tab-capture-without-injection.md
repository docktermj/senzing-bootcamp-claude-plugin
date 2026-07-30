# Capture the default tab without injecting `activate()`, and give the graph a longer budget

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Per-tab screenshot capture injects `activate('<tab>')` into a copy of the page before capturing. That
works for every tab **except the one already active by default** (Entity Graph). Re-activating it
restarts the D3 force simulation partway through the capture window, so the screenshot comes out with
all nodes collapsed into a corner — a plausible-looking but empty graph, **47 KB instead of 227 KB**.

It exits 0 and produces a valid PNG, so nothing flags it. The result is the worst shape for a
keepsake: the recap embeds an image of the bootcamp's headline artifact showing a graph that looks
like it found nothing, and a caption written from the tab name describes a graph the image does not
contain.

## Root cause

**`plugins/senzing-bootcamp/scripts/capture_screenshots.py:227` injects the activation script
unconditionally**, for every requested tab:

```python
script = _ACTIVATE_JS.replace("__TAB__", tab)
```

`_ACTIVATE_JS` (`:110-125`) calls the app's own `activate(target)` and retries until the tab exists.
For a tab that is *not* currently active this is exactly right and is what makes per-tab capture
possible (INV-122/INV-124). For the tab that is **already** active it is a no-op in intent and
destructive in effect: `activate()` re-runs the tab's render path, and the Entity Graph's render
starts a fresh force simulation. The capture then lands during the first frames of that restart,
before the layout has spread.

Two contributing facts:

- **The helper cannot tell which tab is active by default** — it does not parse the page for the
  initially-active tab, so it has no basis for skipping the injection today.
- **One virtual-time budget serves every tab** (`_CHROME_VIRTUAL_TIME_MS = 15000`, `:105`). A
  force-directed layout needs longer to settle than a static table, so even without the restart the
  graph is the tab most likely to be captured mid-animation. The budget was sized for the tabs that
  settle fastest.

## Proposed change

1. **Do not inject for the tab that is already active.** Determine the page's default tab and, when
   the requested tab matches it, capture with no injected script at all. Prefer detecting it from the
   markup (the nav button or tab section the app marks active) over hardcoding a tab id — the tab set
   and its order are contract (`visualization-api-reference.md`), but which one is active first is a
   property of the rendered page, and hardcoding it would silently rot when the default changes.
2. **Fall back safely.** If the default tab cannot be determined, keep today's behavior (inject) — a
   restarted simulation is a bad image, but a tab that never activates is no image at all. Report the
   fallback on stderr so a systematically empty graph is diagnosable.
3. **Give an animated tab a longer virtual-time budget.** Allow a per-tab budget and raise it for the
   force-directed graph, rather than raising it globally and slowing every capture. State the reason
   in a comment: this is a settle-time requirement, not a timeout.
4. **Say both things in the capture guidance.** `module-completion.md` and the visualization contract
   must state that the default tab is captured without injection and that a force-directed tab needs
   longer to settle — otherwise a server generated in another language, or a future capture path,
   reintroduces the defect (INV-090/INV-124).

## Acceptance criteria

- [ ] Capturing the default tab produces no injected `activate()` call for that tab; the other tabs
      still receive one.
- [ ] The default tab is detected from the page rather than hardcoded, and a page whose default tab
      cannot be determined still captures (with the injection) and says so on stderr.
- [ ] The Entity Graph capture shows a spread layout, not nodes collapsed in a corner — verified by
      opening the image (INV-123) and by a file-size floor that a collapsed-graph capture fails.
- [ ] A force-directed tab is captured with a longer virtual-time budget than the static tabs, and the
      budget's purpose is documented where it is set.
- [ ] Every tab still yields one image named after the tab, and an absent tab is still skipped and
      reported (INV-122 unchanged).
- [ ] The capture guidance states the no-injection rule for the default tab and the settle-time
      requirement for an animated tab.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the rule is
      expressed against the contract's tab hooks, which bind a server in any language (INV-124).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — the injection site (`:227`), the
  activation script (`:110-125`), and the budget constant (`:105`): skip injection for the default
  tab, detect it, allow a per-tab budget.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — the capture step: state
  the no-injection and settle-time rules.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the tab-hooks section: note that re-activating the active tab may restart its render.
- `tests/test_capture_tabs.py` — extend: no injection for the default tab, injection for the others,
  fallback reported when the default cannot be determined.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Screenshot guidance should note the default tab
  needs no injected tab switch" (2026-07-28, Module Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`; `Upstream: n/a (plugin-side)`)
- Priority: Medium (not stated by the reporter; assessed from impact — it silently puts an
  empty-looking image of the bootcamp's headline artifact into the permanent keepsake, at exit 0)
- MCP re-check: n/a (no Senzing fact — the defect is in a bundled capture script and the page it
  drives). Server 1.32.1 was current at triage, 2026-07-28.
- Upstream: not applicable
- Related specs: `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-122/INV-123/INV-124
  — the capture contract and the caption rule this defect defeats),
  `specs/embed-every-captured-tab-in-tab-order.md` (INV-146 — the bad image still reaches the recap),
  `specs/windows-headless-browser-discovery-for-screenshots.md` (the sibling capture-path fix),
  `specs/visualization-legibility-at-production-scale.md` (the graph's other scale-dependent defaults)

## Deviations from this spec, and why (2026-07-28)

**The fix is an idempotent `activate()`, not a caller-side skip — because the spec's detection
strategy is impossible and its scope was too narrow.**

`## Proposed change` items 1 and 2 said to determine the page's default tab, skip the injection when
the requested tab matches it, and fall back to injecting (with a stderr note) when the default cannot
be determined — "prefer detecting it from the markup". Two findings at implementation time:

1. **The default tab is not in the markup.** `senzing_viz_server.py`'s `buildNav()` builds the nav at
   runtime and marks index 0 active (`.attr("class", i===0?"active":"")`), so the served HTML contains
   no nav buttons at all and no active marker. A markup probe cannot work, and the "fall back safely"
   branch would have been the only branch ever taken.
2. **The defect is not limited to the injected path.** `applyDeepLink()` calls `activate(tab)` for
   `?tab=<id>`, which is how the **live server** is captured — so a caller-side skip in
   `capture_screenshots.py` would have left the live-capture route still restarting the simulation.
   The spec described only the injection route.

So the guard went into `activate()` itself: called for the tab already active, it returns before
`drawFor()`. That covers the injected route, the deep-link route, and a user clicking the
already-active nav button, and it needs no default-tab detection anywhere. The requirement is stated
in `visualization-api-reference.md` so a server in any language inherits it (INV-090/INV-124) —
which a fix living in the Python capture script could not have achieved.

Item 3 (a longer settle budget for an animated tab) was implemented as specified:
`_virtual_time_ms(tab)` returns 30s for the force-directed tabs and the base 15s for the static ones,
threaded to the Chrome backend through module state rather than a new backend parameter, because
`_BACKENDS` is invoked uniformly and an existing test substitutes two-argument callables for it.

**Acceptance criteria status.** All met except the visual one — "the Entity Graph capture shows a
spread layout, verified by opening the image, and a file-size floor a collapsed-graph capture fails".
That needs a live server with loaded data, which this environment does not have; it is **not
runtime-verified**. What is asserted instead is the mechanism: the early return precedes `drawFor()`,
the contract requires idempotence, and the graph's budget exceeds the static tabs'
(`tests/test_snapshot_and_capture_fidelity.py`). The capture guidance now also tells the reader to
open the graph image and check the nodes are spread, with file size named as the tell.

## Invariants introduced

- `INV-171` — Capture apparatus MUST NOT perturb what it captures: a view-switching function MUST be
  idempotent (no redraw when the view is already shown), the guard MUST live in that function rather
  than in one caller, and animated content MUST be allowed longer to settle than static content
  (recorded in `specs/INVARIANTS.md`).
