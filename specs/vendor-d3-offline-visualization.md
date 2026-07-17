# Vendor D3 so the Truth-Set visualization works offline

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Module 3 visualization (INV-038, "ALWAYS sees") and its "self-contained"
snapshot both load D3 from a public CDN. In an offline, air-gapped, or
proxy-restricted environment the graph renders blank, and the saved snapshot the
Bootcamper is told to keep also fails to render later. This is an INV-004
(production-ready) durability risk and an INV-003 coherence gap: the snapshot is
documented as "self-contained" but is not.

## Root cause (confirmed)

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:217` — the live page
  references `https://d3js.org/d3.v7.min.js`.
- `senzing_viz_server.py:455-456` — the snapshot embeds the data but still emits
  the same external `<script src="https://d3js.org/…">` tag.
- `senzing_viz_server.py:440` — `write_snapshot` is documented as "a
  self-contained HTML snapshot with data embedded (no server needed)," which
  contradicts the CDN dependency: it is self-contained for *data* but not for the
  *renderer*.
- D3 is not vendored anywhere in the plugin. This is also a second external host
  beyond `mcp.senzing.com` (the only host the network-access note mentions).

## Proposed change

Remove the runtime network dependency for rendering:

- Vendor a pinned D3 v7 build inside the plugin (e.g.
  `plugins/senzing-bootcamp/scripts/vendor/d3.v7.min.js`) and have
  `senzing_viz_server.py` inline it into both the live page and the snapshot
  (read the vendored file and emit it in a `<script>` block), so neither requires
  the CDN.
- If inlining the full library is undesirable for the live server, at minimum
  inline it for the snapshot (the durable artifact), and fall back to the CDN only
  when the vendored copy is absent.
- Update the `write_snapshot` docstring so "self-contained" is accurate.
- Keep the renderer python3-only with no new runtime dependency (INV-052); the
  vendored `.js` is a static asset, not a new interpreter requirement.

## Acceptance criteria

- [ ] With no network access, the Module 3 live visualization and the saved snapshot both render the Truth-Set graph.
- [ ] The snapshot HTML contains the D3 source inline (no external `d3js.org` `<script src>`), and `write_snapshot`'s docstring accurately describes it as self-contained.
- [ ] The only external host the plugin needs at runtime remains `mcp.senzing.com`; the visualization needs none.
- [ ] The renderer stays python3-only with no added runtime dependency (INV-052).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — inline the vendored D3 for the live page (`:217`) and the snapshot (`:455-456`); fix the `write_snapshot` docstring (`:440`).
- `plugins/senzing-bootcamp/scripts/vendor/d3.v7.min.js` — **new**; pinned, vendored D3 v7 asset.

## Source

- Invariant audit, 2026-07-17 (deep-dive over the plugin), INV-004/INV-038 coherence finding — the "self-contained" snapshot depends on the D3 CDN.
- Priority: Low (works online; fails offline).
- Related specs: `fix-truthset-snapshot-empty.md` (same snapshot artifact). Bears on INV-004, INV-038, INV-052, INV-003.

## Invariants introduced

- `INV-071` — The bundled visualization (`scripts/senzing_viz_server.py`) MUST render with no
  network access: D3 is vendored inside the plugin (`scripts/vendor/d3.v7.min.js`) and inlined
  into both the live page and the standalone snapshot, with the `d3js.org` CDN referenced only as
  a fallback when the vendored asset is missing (recorded in `specs/INVARIANTS.md`; hardens
  INV-004/INV-038).
