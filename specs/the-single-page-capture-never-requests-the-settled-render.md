# The single-page capture never requests the settled render, and is never checked for it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-299 requires a screenshot of an **animated view** to come from a capture-oriented render
(`?capture=1`), and INV-298 requires a capture proceeding without the settled signal to report
that it did. `capture_screenshots.py` honors both on the per-tab paths and on **neither** in
single-page mode:

- `capture_screenshots.py:1299` — the single-page branch builds
  `url = target if is_url else _to_url(str(html))`, with **no `?capture=1`**. Compare `:1301`
  (live server, via `_tab_url`) and `:1307` (file snapshot), which both request it.
- `_settle_expected(tab)` is `tab in _ANIMATED_TABS`, and `_ANIMATED_TABS` is
  `{"graph", "network"}`. The single-page id is `"page"`, so it is **excluded** — the settle
  state is recorded as `n/a` and nothing is reported.

So a single-page capture of a page containing an animated view would get the unsettled ~5-tick
layout **and** be recorded as if no signal were owed. Both halves of the contract are silently
absent on that one path.

⚠️ **Not reachable through any documented use today, which is why this is Low and not High.**
`module-completion.md:233-236` scopes `--single` to *"a single-page HTML deliverable (Data
Quality, Mapping, and Transformation's quality and mapping pages)"*, which "has no tabs" and no
force layout — nothing to settle. The auto-detect fallback at `:1427`
(`if not tabs and not _has_tab_controls(source)`) fires only for a page with **no tab controls**,
so it cannot pick up the tabbed visualization app either. The gap is reachable only by running
`--single` against the viz snapshot, which the guidance tells the reader not to do.

## Root cause

A rule applied to the sites its author was looking at. The capture render was added for the
tabbed app, which is where the defect was measured, and the single-page branch — three lines
above the per-tab one, in the same `if/elif/else` — was not swept. `_ANIMATED_TABS` then encodes
the same omission a second time, because it is a set of *tab ids* and the single-page pseudo-id
was never considered as a member.

⛔ This is the class the audit hunts first, and the class INV-246 exists for: the fix was applied
where the defect was noticed rather than everywhere the rule binds. Two sites, one swept.

## Proposed change

1. **Decide what the single-page path owes**, and record the decision either way. Two coherent
   answers, and this spec does not pick:
   - **Request the render there too.** One-line change; makes the path correct for any future page
     that animates. Costs: the presettle and fit would apply to a page that may have no layout at
     all, where `fitToExtent` returns early (no nodes) and the tick loop never runs — so probably
     harmless, but it should be verified rather than assumed.
   - **State that the path is for static deliverables and assert it.** Keep the code as it is and
     add a guard that a single-page target has no animated view, so the day a quality page gains
     one, something fails loudly instead of shipping an unsettled image.
2. **Whichever is chosen, make `_settle_expected` honest about it.** Today it answers "no signal
   owed" for the single-page id by omission rather than by decision; the reason should be readable
   at the function.
3. ⛔ **Do not simply add `"page"` to `_ANIMATED_TABS`.** That set also drives the virtual-time
   budget and the tab-label lookup; widening it to fix a settle question would change unrelated
   behavior. Ask the settle question separately.

## Acceptance criteria

- [ ] The single-page path either requests the capture render or is asserted to carry no animated
      view, with the decision recorded at the code.
- [ ] `_settle_expected`'s answer for the single-page id is deliberate and explained, not an
      omission.
- [ ] A guard derives the set of capture paths by **scanning** the URL-building branches rather
      than naming the two that were fixed (INV-246) — so a third path added later is covered.
- [ ] Negative control: whichever behavior is chosen, break it and confirm the guard fails.
- [ ] The documented `--single` use (quality and mapping pages) still captures as one image with
      no tab slug, unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — the single-page URL branch and `_settle_expected`
- `tests/` — a guard over the capture paths, derived by scanning

## Source

- Feedback: `/production-readiness-audit`, 2026-09-03 (`Source: self-observed (assistant retrospective)`)
- Priority: **Low** — unreachable through documented use, since `--single` targets tabless pages and the auto-detect fallback excludes tabbed apps. The cost if it is reached is an unsettled image recorded as owing no signal, which is the one combination INV-298 exists to prevent.
- MCP re-check: **n/a (no Senzing fact).** The subject is the plugin's own capture helper. The ~5-tick measurement it rests on is a live-engine observation from 2026-09-03 on SDK 4.4.0 build 4.4.0.26242, recorded in `graph-capture-budget-does-not-converge-at-truth-set-density` and not re-claimed here.
- Upstream: not applicable.
- Related specs: `specs/graph-capture-budget-does-not-converge-at-truth-set-density.md` (implemented 2026-09-03 — the change that swept two of the three paths)
