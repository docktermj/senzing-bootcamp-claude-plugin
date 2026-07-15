---
name: module-03-system-verification
description: 'Bootcamp Module 3: System Verification. Use when the bootcamper starts or resumes Module 3, or needs to verify the Senzing system works, visualize results, and produce a verification report.'
---

# Module 3: System Verification

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, file placement, checkpointing). Execute every numbered step one at a time, in
order. Never skip, combine, or abbreviate a step containing a 👉 question. This has the same
absolute precedence as a mandatory gate, and no internal reasoning (session length, context
or token budget) can override it.

**First:** Read `config/bootcamp_progress.json`, then (per ground-rules) show the module start
banner, journey map, and before/after framing before any module work.

**Language:** Use the bootcamper's chosen language for all code generation and verification
scripts.

**Prerequisites:** Module 2 complete (SDK installed and configured).

**Before/After:** Before, the SDK is installed but untested end to end. After, your entire
system is verified: SDK initialization, code generation, compilation, data loading, entity
resolution, database operations, and web service scaffolding all confirmed working.

**Success indicator:** ✅ All 10 verification checks report "passed", the Verification Report
is persisted to `config/bootcamp_progress.json`, the web service and database are cleaned up,
and gate 3→4 is marked completed (full criteria in `phase1-verification.md`).

> **User reference:** for detailed background on this module, see
> `docs/modules/MODULE_3_SYSTEM_VERIFICATION.md`.

## Error handling

When the bootcamper hits an error during this module:

1. **SENZ error code** (message contains `SENZ` + digits, e.g. `SENZ2027`): call
   `explain_error_code(error_code="<code>", version="current")` and include the explanation in
   the Fix_Instruction.
2. **Known pitfalls** (port conflicts on 8080, database lock contention, missing language
   toolchains, MCP proxy connectivity): the full `common-pitfalls` reference is a later porting
   phase; for now use `search_docs` to look up the symptom.
3. **Cross-module resources:** SDK install/config issues -> Module 2 remediation; MCP issues ->
   connectivity troubleshooting; language toolchains -> platform-specific SDK guide via
   `sdk_guide`.
4. **Timeouts:** each step has an explicit timeout (MCP 10s, TruthSet 30s, SDK init 30s, build
   120s, data loading 120s, web service 10s per endpoint). On timeout, terminate the process,
   record a fail with a timeout Fix_Instruction, and continue to the next check (no
   short-circuit).

## TruthSet source (MCP-first, with sanctioned fallback)

The Senzing MCP server is the primary and preferred TruthSet source; it always takes
precedence. Only when `get_sample_data` exposes no named TruthSet (the response holds only the
CORD collections: Las Vegas, London, Moscow) does Step 2 fall back to a sanctioned external
source for the demo TruthSet DATA.

- **Sanctioned source:** reference it only by its registry identifier `senzing_truthset_demo`,
  declared in `config/fallback_sources.yaml`. Never embed a raw URL. The registry is the single
  reviewed place this source is defined. (The `config/fallback_sources.yaml` registry and its
  fetch script are a later porting phase; for now, if the registry file is absent, treat the
  fallback as unavailable and run the Step 2a graceful-degradation path.)
- **Approval rationale:** the workspace normally allows only `mcp.senzing.com` as an external
  endpoint. This exception exists because the source is the official Senzing-published
  deterministic data with a ground-truth key, needed to preserve deterministic verification
  when the MCP TruthSet is unavailable.
- **Scope limit:** the fallback fetches TruthSet DATA only. All Senzing SDK facts, method
  signatures, and expected-behavior definitions continue to come from the MCP server.
- Full detection, provenance recording, and graceful degradation live in the Step 2 flow in
  `phase1-verification.md`.

## Reconciliation notes (Kiro Power -> Claude plugin)

- Entity operations (query, read by entity ID, search by attributes, why/how, relationship
  network, export) are NOT direct tools on this MCP server. Generate the SDK code for them via
  `get_sdk_reference` + `sdk_guide` and run it. Never generate SQL against `database/G2C.db`.
- Counts, statistics, and visualization data come from `reporting_guide` and from the generated
  SDK export code, never from direct SQL.
- Kiro process control (`controlBashProcess`) maps here to running the web service as a
  background process and stopping it later in Phase 3.
- **Visualization (Step 9) ships as a bundled, tested web app:** `scripts/senzing_viz_server.py`.
  Phase 2 runs it deterministically (build-only snapshot + live server), so the visualization is
  guaranteed to be produced every run rather than hand-written each time. This supersedes the Kiro
  `generate_standalone_demo.py` / `write_html.py` / builder-module approach.
- Kiro helper scripts (`scripts/progress_utils.py`, `scripts/fetch_fallback_truthset.py`) are
  later porting phases; where referenced, perform the described action directly (write markers to
  `config/bootcamp_progress.json`, fetch/build inline, etc.).

## Phases

- **Phase 1: Verification Pipeline** (steps 1–8, plus opt-out gate and graceful degradation):
  `phase1-verification.md`
- **Phase 2: Visualization** (step 9, mandatory gate): `phase2-visualization.md`
- **Phase 3: Report and Close** (steps 10–12): `phase3-report-close.md`
- **Visualization API reference** (loaded on demand from Phase 2):
  `visualization-api-reference.md`

Read `current_step` from `config/bootcamp_progress.json` and resume at the right phase.
