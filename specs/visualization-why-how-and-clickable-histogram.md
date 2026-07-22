# Add why/how explainability and clickable histogram drill-down to the Truth Set visualization

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The live Truth Set visualization shows *that* records merged (match key, resolution
rule) but not the full "why" (why two entities/records are considered a match) or
"how" (how an entity was constructed from its records) explanations Senzing can
provide, and the Merge Statistics histogram bars are static. The bootcamper asked for
two enhancements:

1. A "Why?"/"How?" action per entity in the **Record Merges** tab and per result in
   **Search / Probe**, surfacing Senzing's why/how explanations.
2. Clickable **Merge Statistics** histogram bars (1 / 2 / 3 / 4+ records per entity)
   that list the entities in each bucket.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py` exposes four read endpoints —
`/api/stats`, `/api/graph`, `/api/merges`, `/api/search` (docstring `12-16`, dispatch
`465-476`); there is no `/api/why` or `/api/how`. The engine is held live for the
server's lifetime (`483-494`, `649-650`), and `/api/search` already calls
`search_by_attributes` at request time (`205-208`) — so new endpoints would follow the
same live-engine pattern. `drawMerges` (`362-367`) renders cards with no action;
`doSearch` (`382-389`) shows only `match_key` + `resolution_rule` (`Model.search`
`224-226`); `drawHist` (`368-381`) is a plain D3 join with no `.on("click")`; and
`/api/stats` returns only bucket counts (`Model.stats` `163-176`), no per-bucket entity
lists. The API contract
`module-03b-truthset-visualization/visualization-api-reference.md` defines only those
four endpoints; the four tabs are described in `phase1-visualization.md:214-224`.

**Invariant note:** **INV-090** is load-bearing — the viz server is built in the
bootcamper's chosen language, modeled on the reference server **and** the
`visualization-api-reference.md` contract. Any new `/api/why` / `/api/how` endpoint (and
any `/api/stats` change for histogram drill-down) MUST be added to **both** the
reference server and the api-reference contract, or the language-native servers
silently diverge. Also: INV-091 (offline vendored D3, no new CDN), INV-077 (viz still
produced when selected; snapshot must still build), INV-081 (new UI uses
`brand_tokens`), INV-080 (SDK method/flag names confirmed via MCP). Snapshot wrinkle:
the static snapshot has no live backend (`fetch` monkey-patched, search stubbed —
`write_snapshot` `608-614`), so live-SDK why/how will not work there; the spec must
define graceful degradation, consistent with `snapshot-static-search-results`.

## Proposed change

1. Add `/api/how?entity_id=<id>` (`SzEngine.how_entity_by_entity_id`) and `/api/why`
   (`why_entities` / `why_records` / `why_record_in_entity`) endpoints to the reference
   server, calling the SDK at request time like `/api/search`. Confirm exact method and
   flag names via the Senzing MCP tools (INV-080).
2. Add a "Why?"/"How?" action per entity card in Record Merges and per result in
   Search / Probe that calls the endpoint and renders the explanation (match keys,
   feature scores, resolution rule) in a modal or expandable panel styled from
   `brand_tokens` (INV-081).
3. Make Merge Statistics histogram bars clickable — extend `/api/stats` (or add
   `/api/entities?bucket=`) so each bar lists the entities in its bucket, linking back
   to the Record Merges card / the same why/how action.
4. Update `visualization-api-reference.md` with the new endpoints and response shapes
   so any language-native server can replicate them (INV-090).
5. Define snapshot degradation: pre-render an example why/how or hide the action in the
   static file, keeping it offline (INV-091) and keeping the snapshot build intact
   (INV-077).

## Acceptance criteria

- [ ] The live visualization exposes why/how explanations via new documented endpoints, reachable from a per-entity action in Record Merges and a per-result action in Search / Probe.
- [ ] Merge Statistics histogram bars are clickable and list the entities in each bucket.
- [ ] `visualization-api-reference.md` documents every new/changed endpoint so a language-native server can replicate it (INV-090).
- [ ] All new UI uses `brand_tokens` (INV-081) and renders offline with vendored D3 (INV-091); no new network dependency.
- [ ] The static snapshot still builds and degrades gracefully — why/how pre-rendered or hidden (INV-077).
- [ ] SDK method and flag names are confirmed via the Senzing MCP tools (INV-080), not training data.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — new endpoints + `Model` methods; `drawMerges`/`doSearch` actions; `drawHist` click handling; snapshot degradation.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — document the new endpoints/response shapes (INV-090 contract).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — tab descriptions / endpoint verification table (`:207-224`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add 'why'/'how' explainability and clickable histogram bars to the Truth Set visualization" (2026-07-22, Module Truth Set visualization)
- Priority: Medium
- Related specs: `specs/visualization-server-in-chosen-language.md`, `specs/truthset-visualization-full-apparatus.md`, `specs/snapshot-static-search-results.md`, `specs/vendor-d3-offline-visualization.md`; INV-090, INV-091, INV-077, INV-081, INV-080
