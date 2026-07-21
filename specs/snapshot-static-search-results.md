# Replace the static snapshot's dead search UI with pre-rendered example results

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The standalone Module 3 snapshot (`docs/visualizations/truthset_verification.html`)
renders a Search / Probe tab with a search box and a "Search" button — but the
snapshot is static HTML with no backing API, so those controls do nothing. The
bootcamper wants the dead controls removed and, instead, a fixed set of example
search results hardcoded into the page (e.g. Susan Mooney, Eddie Kusha, and others),
chosen to showcase interesting merges — so nothing in the static file looks
interactive but inert.

## Root cause (confirmed)

The snapshot reuses the live app's full `PAGE` template, which emits the search
input + button unconditionally, and stubs search to always return empty:

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:268-270` — the `#tab-probe`
  section renders `<input id="search-in" …>` and `<button … onclick="doSearch()">Search</button>`.
- `write_snapshot()` (`:458-478`) calls `render_page(title, data_shim=shim)` with the
  same `PAGE` template; the shim monkey-patches `window.fetch` so `/api/search`
  resolves to `{results:[]}` (`:468-474`), and the snapshot payload embeds only
  `stats`, `graph`, `merges` (`:461-465`) — no search index. So `doSearch()`
  (`:363-370`) always shows "No matching entities found." The search UI is inert by
  construction.

## Proposed change

In the snapshot-generation path (`--snapshot` / `--no-serve`) of
`senzing_viz_server.py`:

- On the Search / Probe tab of the **static** page, remove the `<input>` and
  Search button (and the empty-result `doSearch()` wiring for the snapshot).
- Pre-render a fixed set of example search results directly into the page — each
  showing the name searched, the resolved entity, and the match key — chosen to
  showcase interesting merges (e.g. Susan Mooney, Eddie Kusha). Derive the examples
  from the snapshot's own data where possible so they stay truthful to the rendered
  Truth Set.
- Leave the **live** app (served mode) unchanged: it has a working `/api/search`
  backend, so its search box stays functional.

This preserves INV-038 (the guaranteed Truth-Set visualization) and INV-071
(offline render) — it only removes non-functional controls from the static output.

## Acceptance criteria

- [ ] The static snapshot's Search / Probe tab has no search input or Search button (no controls that appear interactive but do nothing).
- [ ] The static snapshot's Search / Probe tab shows a fixed set of pre-rendered example search results (name → resolved entity → match key), including interesting merges.
- [ ] The live served app's search box remains functional and unchanged.
- [ ] The snapshot still renders fully offline (INV-071) and still satisfies the guaranteed-visualization requirement (INV-038).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — snapshot path: strip the search input/button for static output and pre-render example results (`:268-270`, `:458-478`, `:363-370`); keep served-mode search intact.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Style the standalone snapshot per the style guide; replace its dead search UI with hardcoded examples" (2026-07-18, Module 3) — the dead-search-UI portion (the styling portion is covered by `apply-senzing-style-guide-to-deliverables.md`).
- Priority: Medium.
- Related specs: `apply-senzing-style-guide-to-deliverables.md` (snapshot styling, same generation pass), `fix-truthset-snapshot-empty.md` (snapshot content correctness), `vendor-d3-offline-visualization.md` (INV-071 offline render).
