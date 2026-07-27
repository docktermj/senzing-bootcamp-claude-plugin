# Capture one screenshot per visualization tab, and derive every caption from the image

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Reviewing `docs/bootcamp_recap.pdf`, the bootcamper reported that the visualization
screenshots were wrong in two ways. Both reports were verified, and both are correct — they
are two distinct defects, plus a third found while confirming them.

**(a) The Truth Set visualization section contains zero screenshots.** Only three PNGs existed
in `docs/visualizations/`, all named `results_visualization-*` and all referenced by the Query,
Visualize and Discover section. No `truthset_verification-*` PNG was ever produced, so
graduation's "backfill orphaned screenshots" safety net found nothing to backfill and the
section shipped with no images at all.

**(b) The three Query, Visualize and Discover screenshots are all the same tab.** Inspecting
the PNGs directly confirmed all three show the **Entity Graph** tab, differing only in browser
window size.

**(c) The captions asserted tab content that was never verified.** The recap's embedded image
lines read "Cross-source overlap and match-key frequency tabs" and "Search/Probe with a
verified example query chip" for two images that both show the Entity Graph. Only the first
caption was accurate. The assistant inferred the captures were tab-diverse because the
visualization contract describes the app in terms of tabs, and never opened the PNGs.

The capture step had exited **0** and written three files, which is why nothing looked wrong.

Defect (c) is the more serious half. A missing screenshot is a visible gap; a caption that
confidently describes content the image does not contain is a false statement in a permanent
artifact the bootcamper is explicitly encouraged to share with their team. It is the exact
failure mode INV-115 targets — never render the unverified as verified — applied to images
instead of parsed SDK fields.

## Root cause

**(b)** `plugins/senzing-bootcamp/scripts/capture_screenshots.py:45-49`:

```python
_VIEWS = [
    (1280, 800, "wide"),
    (1280, 1600, "tall"),
    (1024, 768, "compact"),
]
```

Every backend (`_capture_playwright`, `_capture_selenium`, `_capture_chrome_cli`,
`_capture_wkhtmltoimage`) zips its output paths against `_VIEWS` and re-loads the same URL per
viewport. The script has **no interaction step at all**, so it cannot click a tab and can only
ever capture whichever tab is active by default. Tab diversity was never achievable. Output is
named `{name}-1.png` … `{name}-3.png` (`:71-72`), which encodes nothing about content.

**(a)** `phase1-visualization.md:186-191` does invoke the capture for the Truth Set snapshot,
and `graduation/SKILL.md:267-282` backfills orphaned PNGs by matching base names. But the
backfill only maps PNGs that **exist** — "For any PNG **not already referenced** by an
`![...](...)` image line". Nothing checks the converse: that a module which produced a
visualization has at least one image in its section. A capture that produced no files is
indistinguishable from a module that produced no visualization.

**(c)** `bootcamp-onboarding/module-completion.md:151-155` says to "review the shots, keep the
**2-3 most representative**" and embed them as `![caption](...)`. Nothing requires the caption
to be derived from the image, and with content-free filenames (`{name}-1.png`) there is nothing
in the filename to derive it from either. The instruction permits a caption written from the
plan rather than the artifact.

## Proposed change

Ported from the bootcamper's verified implementation (`src/scripts/capture_tabs.py`, 164 lines,
and the deep-linking added to their viz server). It uses only plain headless Chrome — the
lowest-capability backend the script already supports — so **no Playwright/Selenium dependency
is added** (INV-052/INV-066 preserved).

**1. Make capture tab-aware.**

Replace per-viewport capture with per-tab capture. Accept a list of tab identifiers and produce
one PNG per tab. The app's tabs are elements with stable IDs (`tab-graph`, `tab-stats`,
`tab-matchkeys`, `tab-features`, `tab-overlap`, `tab-probe`) and nav buttons `navbtn-<tab>`
(`senzing_viz_server.py:661-665`), and the app exposes `activate(<tab>)`. Two modes:

- `--url http://localhost:<port>` — live server; relies on the deep-linking in step 2.
- `--html path/to/snapshot.html` — static snapshot; write a temp sibling copy with a script
  injected before `</body>` that calls the app's own `activate(<tab>)` (falling back to
  clicking `#navbtn-<tab>`), retrying every 100 ms up to 60 times so it runs after the app's
  async init settles. Delete the temp copies afterwards.

Chrome invocation, verified working:
`--headless=new --disable-gpu --no-sandbox --hide-scrollbars --window-size=1440,900
--virtual-time-budget=15000 --screenshot=<out>`. The virtual-time budget is what lets the D3
layout and the `/api/*` fetches finish before the frame is captured — without it the capture
races the render.

Keep the existing offline guarantee (`_is_local_target`, INV-091) and the exit-2 "no headless
capability" degradation unchanged.

**2. Name every capture after its tab.**

Output `<name>-<tab>.png` (e.g. `results_visualization-entity-graph.png`) instead of
`<name>-<n>.png`. This is the load-bearing part: **a tab-named file makes a drifting caption
structurally hard**, and it lets graduation's backfill map images to sections and tabs
deterministically instead of by guesswork.

**3. Derive the caption from the capture, not the plan.**

In `module-completion.md`'s "Capturing visualization screenshots" procedure, replace "review
the shots, keep the 2-3 most representative" with an explicit requirement: **each image must be
opened and described from what it actually shows**, and the caption must name the tab from the
filename. Prefer generating the caption from the tab identifier outright — that removes the
opportunity to invent one. State plainly that a caption asserting content not visible in the
image is a defect of the same class INV-115 forbids.

**4. Capture Search / Probe against the live server.**

The static snapshot's search needs the running engine
(`specs/snapshot-static-search-results.md`), so a snapshot capture of that tab shows an empty
box. Use the live server with `?q=` for it. If only a snapshot is available — e.g. the Truth
Set data has been purged at module close — either omit that tab or caption it explicitly as the
inactive state. **Never imply a result set that was not captured.**

**5. Add `?tab=` / `?q=` deep-linking to the visualization app.**

Add `applyDeepLink()` to `senzing_viz_server.py`, awaited at the end of `init()` (`:1076`). It
reads `location.search`, activates `?tab=<id>` when that tab is applicable and present, and for
`?q=<query>` fills the search box and runs `doSearch()` (defaulting the tab to `probe` when `q`
is given without `tab`). Worth having independently of screenshots — it makes any view of the
app a shareable URL — and it is what allows the live Search / Probe tab to be captured showing
real results. Document it in `visualization-api-reference.md`.

**6. Verify at render time, in graduation.**

Extend the Step 1 screenshot handling (`graduation/SKILL.md:267-282`) to warn — never block
(INV-048) — when:

- a module that produced a visualization has **no** image line in its recap section; or
- two embedded images in one section are byte-identical, or share identical dimensions from a
  single page load (the signature of viewport-variant capture).

## Acceptance criteria

- [ ] `capture_screenshots.py` (or its successor) accepts a list of tab identifiers and writes
      one PNG per tab, named `<name>-<tab>.png`.
- [ ] Captures of a six-tab app produce six visibly different images; no two are byte-identical
      and each shows the tab its filename names (verified by opening them).
- [ ] Tab capture works against both a live `localhost` URL and a static snapshot file, using
      only plain headless Chrome — no new Playwright/Selenium dependency, and exit 2 with the
      existing message when no headless backend exists (INV-052/INV-066).
- [ ] Non-local targets are still refused (INV-091), and temp snapshot copies are deleted.
- [ ] The app honors `?tab=<id>` and `?q=<query>`, and `?q=` without `?tab=` lands on
      Search / Probe with the query run.
- [ ] The Truth Set visualization module produces at least one `truthset_verification-<tab>.png`
      on a run where a headless backend exists, and the recap's Truth Set section embeds it.
- [ ] Every embedded caption names the tab shown in its image; no caption asserts content absent
      from the image.
- [ ] Search / Probe is captured against the live server, or its caption states it is the
      inactive/empty state — never an implied result set.
- [ ] Graduation warns (exit 0, PDF still written) when a visualization-producing module's
      section has no image, or when two images in one section are byte-identical or same-sized
      from one page load.
- [ ] Graduation's backfill maps `<name>-<tab>.png` files to sections deterministically and
      stays append-only and idempotent (INV-085).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — tab
      IDs are part of the visualization contract, so a server in any language (INV-090) is
      capturable.

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — replace `_VIEWS`/`_out_paths`
  per-viewport capture with per-tab capture and tab-named output; add `--url`/`--html` modes and
  the injected-`activate()` path for snapshots.
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — add `applyDeepLink()`, awaited in
  `init()` (~`:1076`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — pass tab
  identifiers to the helper; require captions derived from the opened image / tab name
  (`:129-157`, and the summary rule at `:97`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  capture per tab (`:186-191`); capture Search / Probe against the live server before teardown.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — document stable tab IDs as contract, and `?tab=`/`?q=` deep-linking.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
  — capture per tab at the visualization step (3c).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — tab-aware backfill and the
  render-time warnings (`:267-282`).
- `tests/` — a new test asserting distinct per-tab output names and that the contract's tab IDs
  match the server's.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Recap PDF screenshots are viewport variants
  of one tab, not per-tab captures — and the Truth Set section has none at all" (2026-07-26,
  Module Graduation, root cause in Truth Set visualization and Query, Visualize and Discover;
  `Source: bootcamper-reported`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Positive feedback — the improved recap PDF,
  with the full implementation record for porting upstream" (2026-07-26, Module Graduation;
  `Source: bootcamper-reported`) — items 1 and 2 of its port list are the reference
  implementation for this spec.
- Priority: High
- Related specs: `specs/capture-visualization-screenshots-for-recap.md` (established the
  capture), `specs/enforce-screenshot-embed-and-backfill.md` (established the embed and the
  backfill safety net), `specs/snapshot-static-search-results.md` (why Search / Probe needs the
  live server), `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — the
  don't-render-the-unverified rule this extends to images),
  `specs/artifact-level-verification-for-deliverables.md`,
  `specs/consolidate-truthset-viz-merges-and-network-tabs.md` (changes which tabs exist).

## Invariants introduced

- `INV-122` — Visualization screenshots MUST be one image per tab, named after the tab; an absent
  tab MUST be skipped and reported, never captured under its name (recorded in
  `specs/INVARIANTS.md`).
- `INV-123` — Every screenshot caption MUST be derived from the opened image and its tab, never
  from the contract or the capture plan (recorded in `specs/INVARIANTS.md`).
- `INV-124` — A visualization server in any language MUST expose the contract's tab ids,
  `activate(<id>)`, and `?tab=`/`?q=` deep-linking applied after nav construction (recorded in
  `specs/INVARIANTS.md`).
