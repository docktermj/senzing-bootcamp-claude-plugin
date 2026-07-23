# Truth Set Visualization, Phase 1: Visualization (steps 1–2)

Follow `../bootcamp-onboarding/ground-rules.md`. `🛑`/`⛔` are internal directives, never
rendered; signal a stop by ending the turn on the single 👉 question and waiting.

**Purpose:** stand up an interactive visualization **web app** that shows the bootcamper a
resolved Senzing **Truth Set**, their "wow moment" with entity resolution. This module owns the
Truth Set end to end — System Verification does not acquire, load, or visualize it.

**Prerequisites:** the Senzing SDK is installed and initialized (Module 2) and the engine is
reachable, and System Verification has run immediately before. This module **acquires and loads the
Truth Set itself** (Step 1 below); it does NOT depend on System Verification having loaded any
data.

## Execution requirement (internal directive)

This module runs when the **Truth Set visualization** is selected — i.e. `truthset_visualization` is
in `selected_modules` (`config/bootcamp_preferences.yaml`). This is **always true in Core**; in
Customized it is true only if the bootcamper chose it (see `SKILL.md`). This phase file is loaded
only when the module is selected; when it is not selected the module does not run at all and System
Verification transitions straight to Data collection.

The visualization is MANDATORY here: it MUST be produced; you must NOT transition to the next module
until it exists and the bootcamper has been shown it. There is NO condition, threshold, or scenario
under which you may then skip it — no session-length, token-budget, redundancy, or time
rationalization is ever valid. Step 2 is unconditional, and this module's completion gate in
`phase2-close.md` re-checks that the visualization artifact exists and refuses to mark the module
complete if it does not (INV-077).

## Module start: Truth Set visualization (present at module start, before Step 1)

The Truth Set visualization is a **first-class, standalone module** (INV-086/INV-087) — so it opens
with the standard module-start apparatus (INV-079/INV-029–031, INV-063), exactly like any module start,
per `../bootcamp-onboarding/ground-rules.md`. Present it **once**, at the start of the module,
immediately before Step 1:

1. **Set `current_module`** to `truthset_visualization` in `config/bootcamp_progress.json` (a single
   quiet write, INV-058), so a resume mid-visualization re-opens the right module.
2. **Module-start banner (INV-079):** name only, no number —

   ```text
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🚀🚀🚀  MODULE: TRUTH SET VISUALIZATION  🚀🚀🚀
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

3. **Journey map (INV-029):** refresh it with `truthset_visualization` now `🔄` current — `System
   verification` `✅`, the remaining `selected_modules` `⬜` upcoming.
4. **Before/After (INV-030):** *Before,* entity resolution is proven on synthetic data but unseen;
   *after,* the bootcamper has watched the Senzing Truth Set resolve in an interactive web app —
   their "wow moment".
5. **Step overview (INV-031):** briefly enumerate this module's steps — acquire the Truth Set →
   register the codes + load → build and serve the visualization → explore it → clean up.
6. **Estimated time (INV-096):** give an honest, range-based estimate (a handful of minutes,
   varying with Truth Set download and render speed), stated as "hard to estimate" if no meaningful
   figure is possible; suppress under the `minimal` verbosity preset, one line under `concise`.
7. **Model/effort (INV-063):** surface the recommended model/effort per ground-rules; it is
   unchanged from System verification (Module 3 tier), so a concise statement (or omit).

Then proceed to Step 1 below. (Its end-of-module summary and `✅ Module complete: Truth Set
visualization` line are presented at this module's close — `phase2-close.md`.)

## Step 1: Acquire, register, and load the Truth Set (self-contained)

This module owns the Truth Set end to end — System Verification (Phase 1) no longer acquires or
loads it. Run these sub-steps **before** starting the web app, so the visualization always has
resolved Truth Set data to show. (Full source/fallback rationale is in `SKILL.md` → "Truth Set
source".)

### 1.1 Acquire the Truth Set (MCP-first, sanctioned fallback)

The Senzing MCP server is the primary and preferred source; it always takes precedence.

1. Call `get_sample_data` and inspect the response for a named Truth Set reference. Classify:
   `available` = a named Truth Set (name matches "TruthSet", or `type: truthset`) with retrievable
   records; `unavailable` = only the CORD collections (Las Vegas, London, Moscow) are present.
2. **Available (primary path):** save the MCP records to
   `src/system_verification/truthset_data.jsonl` (overwrite, one JSON object per line),
   provenance `mcp_primary` (30-second timeout).
3. **Unavailable (fallback path):** fetch the demo Truth Set **DATA only** from the sanctioned
   fallback source — resolve source id `senzing_truthset_demo` from `config/fallback_sources.yaml`,
   never a raw URL — write `truthset_data.jsonl`, provenance `github_fallback`. (If the registry
   file is absent, treat the fallback as unavailable.)
4. **Both unavailable:** report both failures with remediation (verify MCP connectivity; verify
   the fallback is reachable; say "retry"). Then offer a clearly labeled **non-deterministic**
   CORD collection that exercises the visualization but has no ground-truth key:

   👉 **The Truth Set is unavailable. Would you like to visualize a non-deterministic CORD collection (Las Vegas, London, Moscow) instead?**

   *(Internal: end the turn on this question and wait.)* If declined, the visualization cannot be
   produced; record the block and tell the bootcamper how to retry.

Record the source provenance (`mcp_primary` / `github_fallback` / `cord_substitute`) and the
expected record count for the report.

### 1.2 Register the Truth Set data source codes and load

1. Collect the distinct `DATA_SOURCE` values present in `truthset_data.jsonl` (for the standard
   Truth Set: CUSTOMERS, REFERENCE, WATCHLIST; a CORD substitute uses whatever codes its records
   carry). Never register a code that is not present in the data.
2. Generate the registration code from the MCP server (`sdk_guide(topic='configure')`, and
   `generate_scaffold` if it exposes a registration workflow) in the language read from
   `programming_language` in `config/bootcamp_preferences.yaml` — register each code and set the
   updated config as the new default, **idempotently** — then load `truthset_data.jsonl` into the
   Senzing database (generate the loader via `generate_scaffold` / reuse the Module 3 Phase 1
   pipeline pattern; never direct SQL). Registering **before** the load upholds the "register
   before load" guarantee so the load never fails with `SENZ2207`.

Save the load artifacts under `src/system_verification/` (Agent Rule 5). Once the Truth Set is
loaded, continue to Step 2 below to visualize it.

## Step 2: Build and run the visualization server in your chosen programming language

The Truth Set visualization is delivered by a web server **written in the Bootcamper's chosen
programming language** (`programming_language` in `config/bootcamp_preferences.yaml`) — like every
other deliverable in this bootcamp. The shipped `scripts/senzing_viz_server.py` is the **reference
model** for what to build, and `visualization-api-reference.md` (this skill directory) is the
authoritative API/response contract to implement. `senzing_viz_server.py` is **run directly only
when the chosen language is Python**; for any other language it is a model to read, never run.

Whatever the language, the server MUST reproduce the reference's behavior:

- Build the entity model from the loaded records — one `get_entity_by_record_id` call per record,
  requesting the default entity flags (which include all relations) so it never queries the
  database directly. Get the exact SDK method, flag, and attribute names from the Senzing MCP tools
  (`sdk_guide` / `get_sdk_reference` / `generate_scaffold`), never from training data (INV-080).
- Serve the JSON APIs — `/api/stats`, `/api/graph`, `/api/merges`, `/api/search`, `/api/why`,
  `/api/how`, `/api/dashboard`, `/api/overlap`, `/api/matchkeys`, `/api/features` — with the exact
  response shapes in `visualization-api-reference.md`.
- Serve the live D3 v7 page as a **single consolidated, tabbed app** (all tabs in 2.4), and write a
  self-contained standalone HTML snapshot.
- **Render offline (INV-091):** inline the vendored D3 at `scripts/vendor/d3.v7.min.js` into both
  the live page and the standalone snapshot; never fetch from a CDN. (D3 runs in the browser, so
  this holds regardless of the server's language.)
- **Use the Senzing brand (INV-081):** take the palette and typography from the shipped brand
  tokens (`scripts/brand_tokens.py`, mirrored in `senzing_viz_server.py`) — data sources CUSTOMERS
  ember/orange, REFERENCE blue, WATCHLIST gold/amber. A non-Python server cannot import the Python
  module, so replicate the token **values** from the reference; never invent an ad-hoc palette.
- **Map edges correctly:** expose `source`/`target` (from `source_entity_id`/`target_entity_id`)
  **before** `forceLink().links(...)`, preserving node `id`/`entity_id` — omitting this renders an
  empty graph.

Save the generated server and its assets under `src/server/` (INV-050). The Senzing native library
must be importable, so run everything with the project env sourced (the `src/scripts/senzing-env.sh`
/ `senzing-env.bat` created in Module 2): `source src/scripts/senzing-env.sh` on Linux/macOS, or
`src\scripts\senzing-env.bat` on Windows first.

### 2.1 Choose the path

Read `programming_language` from `config/bootcamp_preferences.yaml`:

- **Python** → the reference implementation *is* the server. Resolve `scripts/senzing_viz_server.py`
  (`${CLAUDE_PLUGIN_ROOT}/scripts/senzing_viz_server.py` in a command/hook context, else
  `../../scripts/senzing_viz_server.py` relative to this skill) and run it directly. This is the
  **only** path on which `senzing_viz_server.py` runs.
- **Any other language** → generate the server in that language per the contract above, modeled on
  `senzing_viz_server.py` + `visualization-api-reference.md`, saved under `src/server/`. Do **not**
  run `senzing_viz_server.py`. Generate code via the MCP tools and a generator per your language's
  conventions; never hand-write SDK calls or HTML+JS with file-write tooling.

### 2.2 Always produce the standalone snapshot first (the guarantee)

Before starting the live server, run your server in build-only / snapshot mode to (a) build the
entity model and (b) write a **self-contained standalone HTML snapshot** the Bootcamper keeps even
if they never open the live server. This is the artifact the completion gate checks, so the
visualization is guaranteed to exist (INV-077). Write it to
`docs/visualizations/truthset_verification.html` from `src/system_verification/truthset_data.jsonl`,
titled "Senzing Truth Set - System Verification". For Python, that is:

```bash
python3 <viz-server-path> \
  --records src/system_verification/truthset_data.jsonl \
  --title "Senzing Truth Set - System Verification" \
  --snapshot docs/visualizations/truthset_verification.html \
  --no-serve
```

For any other language, invoke your server's equivalent build-only/snapshot mode (write the same
file, no server started). Confirm the file exists before continuing. If the build fails, do not
proceed to the live server: fix the underlying cause (regenerate faulty code from the MCP tools;
re-run SDK initialization from Module 2 / System Verification; check `config/engine_config.json`)
and retry until the snapshot is written — the module does not complete without it.

**Capture screenshots for the recap (optional, non-blocking).** With the snapshot at
`docs/visualizations/truthset_verification.html`, capture a few screenshots for the recap —
`{html}` = `truthset_verification.html`, `{name}` = `truthset_verification` — per
`../bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots". If no
headless capability is available it skips silently; otherwise keep the 2-3 best and embed them in
this module's recap `Actions Taken`. This is never a 👉 question and never blocks the visualization.

### 2.3 Start the live web app

Start the server as a background process you can stop later in Step 4 (Cleanup), serving the loaded
records on port 8080. For Python:

```bash
python3 <viz-server-path> \
  --records src/system_verification/truthset_data.jsonl \
  --title "Senzing Truth Set - System Verification" \
  --port 8080
```

For any other language, start your server's equivalent. It should report a URL like
`http://localhost:8080`. If port 8080 is in use, use a different port and tell the Bootcamper the
chosen URL.

### 2.4 Verify the endpoints

The app serves the live page at `/` plus JSON APIs. Verify each (10-second timeout):

| Endpoint | Success criteria |
|----------|-----------------|
| `GET /api/stats` | HTTP 200; fields `records_total`, `entities_total`, `multi_record_entities`, `cross_source_entities`, `relationships_total`, `data_sources_total`, `histogram`, `bucket_entities` (per-bucket entity lists for the clickable histogram) |
| `GET /api/graph` | HTTP 200; `nodes` (each: `entity_id`, `entity_name`, `record_count`, `data_sources`, `records`) and `edges` (each: `source_entity_id`, `target_entity_id`, `match_key`, `relationship_type`) |
| `GET /api/merges` | HTTP 200; at least one multi-record entity (2+ records) |
| `GET /api/search?q=Robert Smith` | HTTP 200; `results` array with resolved entities, each carrying `match_key` and `resolution_rule` |
| `GET /api/why?entity_id=<id>` | HTTP 200; real `WHY_RESULTS` (or an `error` field) explaining why the entity's records resolved together |
| `GET /api/how?entity_id=<id>` | HTTP 200; real `HOW_RESULTS` (or an `error` field) explaining how the entity was constructed |
| `GET /api/dashboard` | HTTP 200; `counts`, `histogram`, and `sample_entities` for the results dashboard |
| `GET /api/overlap` | HTTP 200; `sources` + square `matrix` of cross-source shared-entity counts |
| `GET /api/matchkeys` | HTTP 200; `match_keys` (most-frequent first) + `distinct` + `capped` |
| `GET /api/features` | HTTP 200; `features` (per-feature score-bucket counts), `sampled`, `multi_record_total`, `capped` |

The live page is a **single consolidated, tabbed app** — the one visualization artifact (no
separate static pages). All tabs are populated from these APIs; a tab whose data is absent is not
shown:

1. **Entity Graph** (default): D3 v7 force-directed graph of the full entity population. Nodes
   colored by data source (CUSTOMERS ember/orange, REFERENCE blue, WATCHLIST gold/amber), sized by
   record count, edges labeled with match keys, hover tooltip, click-to-detail modal, zoom/pan, and
   a color legend. This is also the cross-source entity-relationship view (it subsumes the former
   `multi_source_results.html`). (Your server MUST perform the edge-key mapping,
   `source_entity_id`/`target_entity_id` → `source`/`target` before `forceLink` — per Step 2's
   intro; omitting it renders an empty graph.)
2. **Relationship Network** (when relationships exist): the subgraph of entities connected by
   relationships (possible matches / disclosed relations), edges colored by relationship type with a
   type legend — distinct from Entity Graph, which shows the full population.
3. **Record Merges:** cards showing each multi-record entity's constituent records, each with
   **Why?** and **How?** actions that call `/api/why` and `/api/how` and render Senzing's
   explanation (match keys, feature scores, construction steps) in a modal.
4. **Merge Statistics:** records-per-entity histogram (1 / 2 / 3 / 4+) with a summary sentence —
   this **is** the entity-size distribution; the bars are **clickable** (backed by `bucket_entities`)
   and drill down to the entities in each bucket, each linking to its **How?** explanation.
5. **Match Keys** (when multi-record entities exist): frequency of the match keys (feature
   combinations) that drove resolutions.
6. **Feature Scores** (when multi-record entities exist): how tightly each feature agreed across
   resolved records, from a capped `why_records` sample; the tab always shows the sample size.
7. **Cross-Source** (when 2+ data sources): overlap heatmap of how many entities each pair of
   sources shares.
8. **Results Dashboard:** headline counts, the records-per-entity histogram, and a sample of the
   largest resolved entities.
9. **Search / Probe:** search by name; results show the resolved entity, its sources, and the
   match key / resolution rule that linked it, plus the same **Why?** / **How?** actions.

Do **not** add redundant tabs — the entity-size distribution is Merge Statistics, and the
cross-source entity-relationship view is Entity Graph (per `visualization-api-reference.md` →
"De-duplication").

### 2.5 Present it and give the guided tour

Tell the bootcamper the app is running and where the saved copy is:

- "Your visualization is running at `http://localhost:8080`, open it in your browser."
- "A saved copy is at `docs/visualizations/truthset_verification.html`, you can open that file
  any time, even after we stop the server."

Then deliver this guided tour as one message (no interactive pauses):

---

🗺️ **What you're looking at:**

- **Entity Graph:** each circle is a resolved entity. Multi-colored clusters and edges show
  records that Senzing linked across data sources, a customer who is also on the watchlist, for
  example. Edge labels (like `+NAME+ADDRESS`) are the match keys: the features Senzing used to
  link them.
- **Merge Statistics:** the histogram shows how many records collapsed into each entity, tall
  bars at 2/3/4+ are where Senzing found duplicates.
- **Search / Probe:** type a name (try "Robert Smith") to see the resolved entity and why it
  matched.
- **More tabs:** the **Results Dashboard** summarizes the run at a glance; **Match Keys** and
  **Feature Scores** show what drove the resolutions; **Cross-Source** (with 2+ sources) maps where
  your sources overlap; **Relationship Network** shows how entities connect. (Point these out
  briefly — one line — under `concise`/`minimal` verbosity, or skip the list.)

---

👉 **Take your time exploring the visualization. Let me know when you're ready to continue.**

*(Internal: end the turn on this question and wait for the bootcamper to confirm they are done
exploring. Do not proceed to Phase 2 (the close) until they respond.)*

**On failure:** report the specific endpoint or step that failed and the fix:

- Port in use → pass a different `--port` and share the new URL.
- Engine/SDK error → re-run SDK initialization (Module 2 / System Verification); confirm `config/engine_config.json`.
- Snapshot not written → the model build failed; read stderr, fix the cause, and re-run 2.2.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "truthset_visualization": {
    "checks": {
      "web_service": {"status": "passed|failed", "port": 8080},
      "web_page": {"status": "passed|failed", "url": "http://localhost:8080/",
                   "snapshot": "docs/visualizations/truthset_verification.html"}
    }
  }
}
```

**Success indicator:** ✅ The standalone snapshot exists at
`docs/visualizations/truthset_verification.html` AND the live app served the four endpoints and
the entity-graph page.

## Fallback: guarantee the snapshot if the live server cannot run

If, after iterating with the MCP tools, the live server cannot be made to serve, you MUST still
produce the standalone snapshot (INV-077): generate a self-contained D3 v7 HTML snapshot — vendored
D3 inlined (INV-091), Senzing brand tokens applied (INV-081), edges mapped `source_entity_id`/
`target_entity_id` → `source`/`target` before `forceLink` — written to
`docs/visualizations/truthset_verification.html`, so the completion gate's guarantee holds. Produce
it with the chosen language's tooling (a generator, not direct HTML+JS file-writes). Only when the
chosen language is **Python** may you fall back to the bundled `senzing_viz_server.py`; for any
other language `senzing_viz_server.py` is never run. The full response schemas and the
search-enrichment specification are in `visualization-api-reference.md`.

When the bootcamper has finished exploring, load `phase2-close.md`.
