---
name: module-03b-truthset-visualization
description: 'Bootcamp module: Truth Set Visualization. Use when the bootcamper starts or resumes the Truth Set visualization module — stand up an interactive web app of the resolved Senzing Truth Set (the "wow moment") after System Verification. A standalone module, separate from System Verification.'
---

# Truth Set Visualization (standalone module)

> **MCP grounding (mandatory — applies to this entire skill).** Every Senzing fact you present —
> SDK method and attribute names, config options, error codes, and entity-resolution specifics —
> MUST come from the Senzing MCP tools, never from training data, memory, or speculation.
> **Pre-response checklist:** if a reply contains any Senzing specific, you MUST have called an MCP
> tool this turn to obtain it; if not, stop and call it first. This has the same precedence as a ⛔
> gate. The full rule and tool routing are the "MCP-first invariant" in
> `../bootcamp-onboarding/ground-rules.md`.

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, file placement, checkpointing). Execute every numbered step one at a time, in
order. Never skip, combine, or abbreviate a step containing a 👉 question. This has the same
absolute precedence as a mandatory gate, and no internal reasoning (session length, context
or token budget) can override it.

This is a **first-class, standalone module** (`truthset_visualization`) — separate from System
Verification, in its own skill directory — with its own full per-module apparatus and its own close
(INV-086/INV-087). It is **not** apparatus-exempt.

**First:** Read `config/bootcamp_progress.json`, then (per ground-rules) show the module-start
banner, journey map, before/after framing, and a brief numbered overview of this module's steps,
before any module work. (The module-start apparatus block is specified in `phase1-visualization.md`.)

**Language:** Read `programming_language` from `config/bootcamp_preferences.yaml` (persisted in
Bootcamp preparation) at each code-generation step (data-source registration, loader). Never fall
back to a hardcoded language. (The bundled visualization web app itself, `scripts/senzing_viz_server.py`,
is a shipped, tested plugin tool — plugin infrastructure like the Python hooks — run deterministically
every time; it is not part of the bootcamper's generated deliverable.)

## Execution requirement (internal directive)

This module runs when **Truth Set visualization** is selected — i.e. `truthset_visualization` is in
`selected_modules` (`config/bootcamp_preferences.yaml`). This is **always true in Core**; in
Customized it is true only if the bootcamper chose it during Bootcamp preparation. It **requires**
System Verification, which runs immediately before it.

- **When selected:** the visualization is MANDATORY. It MUST be produced; you must NOT transition to
  the next module until it exists and the bootcamper has been shown it. There is NO condition,
  threshold, or scenario under which you may then skip it — no session-length, token-budget,
  redundancy, or time rationalization is ever valid. Step 2 is unconditional, and this module's
  completion gate (`phase2-close.md`) re-checks that the visualization artifact exists and refuses
  to mark the module complete if it does not (INV-077).
- **When not selected:** this module does not run at all. System Verification transitions straight
  to Data collection, and no workstation-verification visualization is produced (the bootcamper
  deselected it).

**Prerequisites:** the Senzing SDK is installed and initialized (Module 2), the engine is reachable,
and System Verification has completed (or was run) — this module does NOT depend on System
Verification having loaded any data; it **acquires and loads the Truth Set itself** (Step 1 in
`phase1-visualization.md`).

## Error handling

When the bootcamper hits an error during this module:

1. **SENZ error code** (message contains `SENZ` + digits, e.g. `SENZ2027`): call
   `explain_error_code(error_code="<code>", version="current")` and include the explanation in the
   fix guidance.
2. **Known pitfalls** (port conflicts on 8080, database lock contention, MCP proxy connectivity):
   use `search_docs` to look up the symptom.
3. **Timeouts:** TruthSet acquisition 30s, SDK/load per `phase1-visualization.md`, web service 10s
   per endpoint. On timeout, terminate the process, record the failure, and follow the phase's
   failure guidance.

## Truth Set source

The Senzing MCP server is the primary and preferred TruthSet source; it always takes precedence.
Only when `get_sample_data` exposes no named TruthSet (the response holds only the CORD collections:
Las Vegas, London, Moscow) does this module (Step 1) fall back to a sanctioned external source
for the demo TruthSet DATA.

- **Sanctioned source:** reference it only by its registry identifier `senzing_truthset_demo`,
  declared in `config/fallback_sources.yaml`. Never embed a raw URL. The registry is the single
  reviewed place this source is defined. (The `config/fallback_sources.yaml` registry and its fetch
  script are a later porting phase; for now, if the registry file is absent, treat the fallback as
  unavailable and run the graceful-degradation path in `phase1-visualization.md`, Step 1, 1.1.)
- **Approval rationale:** the workspace normally allows only `mcp.senzing.com` as an external
  endpoint. This exception exists because the source is the official Senzing-published deterministic
  data with a ground-truth key, needed to preserve a deterministic "wow moment" when the MCP TruthSet
  is unavailable.
- **Scope limit:** the fallback fetches TruthSet DATA only. All Senzing SDK facts, method
  signatures, and expected-behavior definitions continue to come from the MCP server.
- Full detection, provenance recording, and graceful degradation live in the Step 1 flow in
  `phase1-visualization.md`.

## Reconciliation notes (Kiro Power -> Claude plugin)

- Entity operations (query, read by entity ID, search by attributes, why/how, relationship network,
  export) are NOT direct tools on this MCP server. Generate the SDK code for them via
  `get_sdk_reference` + `sdk_guide` and run it. Never generate SQL against `database/G2C.db`.
- Counts, statistics, and visualization data come from `reporting_guide` and from the bundled app's
  entity-model build (one `get_entity_by_record_id` per record), never from direct SQL.
- Kiro process control (`controlBashProcess`) maps here to running the web service as a background
  process and stopping it later at this module's close.
- **Visualization (Step 2) ships as a bundled, tested web app:** `scripts/senzing_viz_server.py`.
  This module runs it deterministically (build-only snapshot + live server), so the visualization is
  guaranteed to be produced every run rather than hand-written each time. This supersedes the Kiro
  `generate_standalone_demo.py` / `write_html.py` / builder-module approach.

## Phases

- **Phase 1: Visualization** (Steps 1–3), including the module-start apparatus:
  `phase1-visualization.md`. Acquires and loads the Truth Set itself, then stands up the
  interactive web app and the standalone snapshot. It also frames the bundled viz server as plugin
  infrastructure (not the bootcamper's generated code) and offers an optional language-native stub as
  a learning exercise (Step 3) — the bundled snapshot stays the guaranteed deliverable.
- **Phase 2: Report and Close** (self-check + cleanup + module completion): `phase2-close.md`.
- **Visualization API reference** (loaded on demand from Phase 1): `visualization-api-reference.md`

Read `current_step` from `config/bootcamp_progress.json` and resume at the right phase.

**Success indicator:** ✅ The standalone snapshot exists at
`docs/visualizations/truthset_verification.html` (built from a non-empty Truth Set) AND the live app
served its four endpoints and the entity-graph page; the web service is terminated and the Truth Set
data purged at close; `truthset_visualization` is recorded in `modules_completed` with its own recap
section (INV-085/INV-086/INV-087).
