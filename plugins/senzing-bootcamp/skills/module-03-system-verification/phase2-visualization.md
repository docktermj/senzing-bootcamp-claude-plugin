# Module 3, Phase 2: Entity Resolution Visualization (step 9)

Follow `../bootcamp-onboarding/ground-rules.md`. `🛑`/`⛔` are internal directives, never
rendered; signal a stop by ending the turn on the single 👉 question and waiting.

**Purpose:** stand up an interactive visualization **web app** that shows the bootcamper their
resolved TruthSet, their first "wow moment" with entity resolution.

**Prerequisites:** Phase 1 Steps 1-8 complete (all verification checks passed, TruthSet data
loaded and validated).

## Mandatory execution requirement (internal directive)

Phase 2 visualization is MANDATORY and unconditional whenever Module 3 runs. The visualization
MUST be produced; you must NOT transition to Module 4 until it exists and the bootcamper has been
shown it. There is NO condition, threshold, or scenario under which you may skip it, no
session-length, token-budget, redundancy, or time rationalization is ever valid. Only the
bootcamper may opt out of the entire module at the Phase 1 Opt-Out Gate (before verification
begins); once Module 3 is underway, Step 9 is unconditional. The completion gate in
`phase3-report-close.md` re-checks that the visualization artifact exists and refuses to mark
Module 3 complete if it does not.

## Step 9: Run the bundled visualization web app

The plugin ships a tested, self-contained visualization web app,
`scripts/senzing_viz_server.py`, so the visualization is produced **deterministically every
time**. Do NOT hand-write a server or HTML page for the normal path: run the bundled app. It
builds the entity model from the loaded records (one `get_entity_by_record_id` call per record,
using `SZ_ENTITY_DEFAULT_FLAGS`, which includes all relations, so it never queries the database
directly), then serves the live app plus the four APIs below.

### 9.1 Locate the bundled app

The generator ships with this plugin at `scripts/senzing_viz_server.py`. Resolve it in this
order:

- When Module 3 is reached via a command/hook context, use `${CLAUDE_PLUGIN_ROOT}/scripts/senzing_viz_server.py`.
- Otherwise resolve it relative to this skill directory (this file lives in
  `skills/module-03-system-verification/`, so the script is at `../../scripts/senzing_viz_server.py`).

The Senzing native library must be importable, so run it with the project env sourced (the
`src/scripts/senzing-env.sh` created in Module 2). On Linux/macOS:

```bash
source src/scripts/senzing-env.sh
```

### 9.2 Always produce the standalone snapshot first (the guarantee)

Before starting the live server, run the app in build-only mode to (a) build the entity model
and (b) write a **self-contained standalone HTML snapshot** the bootcamper keeps even if they
never open the live server. This is the artifact the completion gate checks for, so the
visualization is guaranteed to exist:

```bash
python3 <viz-server-path> \
  --records "src/system_verification/customers.jsonl" \
            "src/system_verification/reference.jsonl" \
            "src/system_verification/watchlist.jsonl" \
  --title "Senzing Truth Set - System Verification" \
  --snapshot docs/visualizations/truthset_verification.html \
  --no-serve
```

Success is a `Snapshot written: docs/visualizations/truthset_verification.html` line and exit 0.
Confirm the file exists before continuing. If this build-only run fails (for example the engine
cannot be reached), do not proceed to the live server: fix the underlying error (re-run Step 3
SDK initialization; check `config/engine_config.json`) and retry. The snapshot is the guaranteed
deliverable.

### 9.3 Start the live web app

Start the server as a background process you can stop later in Step 11:

```bash
python3 <viz-server-path> \
  --records "src/system_verification/"*.jsonl \
  --title "Senzing Truth Set - System Verification" \
  --port 8080
```

It prints `Visualization running: http://localhost:8080`. If port 8080 is in use, pass a
different `--port` and tell the bootcamper the chosen URL.

### 9.4 Verify the endpoints

The app serves the live page at `/` plus four JSON APIs. Verify each (10-second timeout):

| Endpoint | Success criteria |
|----------|-----------------|
| `GET /api/stats` | HTTP 200; fields `records_total`, `entities_total`, `multi_record_entities`, `cross_source_entities`, `relationships_total`, `histogram` |
| `GET /api/graph` | HTTP 200; `nodes` (each: `entity_id`, `entity_name`, `record_count`, `data_sources`, `records`) and `edges` (each: `source_entity_id`, `target_entity_id`, `match_key`, `relationship_type`) |
| `GET /api/merges` | HTTP 200; at least one multi-record entity (2+ records) |
| `GET /api/search?q=Robert Smith` | HTTP 200; `results` array with resolved entities, each carrying `match_key` and `resolution_rule` |

The live page renders four tabs, all populated from these APIs:

1. **Entity Graph** (default): D3 v7 force-directed graph. Nodes colored by data source
   (CUSTOMERS blue, REFERENCE green, WATCHLIST amber), sized by record count, edges labeled with
   match keys, hover tooltip, click-to-detail modal, zoom/pan, and a color legend. (The
   edge-key mapping, `source_entity_id`/`target_entity_id` → `source`/`target` before
   `forceLink`, is baked into the bundled app, correct by construction.)
2. **Record Merges**: cards showing each multi-record entity's constituent records.
3. **Merge Statistics**: records-per-entity histogram (1 / 2 / 3 / 4+) with a summary sentence.
4. **Search / Probe**: search by name; results show the resolved entity, its sources, and the
   match key / resolution rule that linked it.

### 9.5 Present it and give the guided tour

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

---

👉 **Take your time exploring the visualization. Let me know when you're ready and I'll continue with cleanup.**

*(Internal: end the turn on this question and wait for the bootcamper to confirm they are done
exploring. Do not proceed to Phase 3 until they respond.)*

**On failure:** report the specific endpoint or step that failed and the fix:

- Port in use → pass a different `--port` and share the new URL.
- Engine/SDK error → re-run Step 3 SDK initialization; confirm `config/engine_config.json`.
- Snapshot not written → the model build failed; read stderr, fix the cause, and re-run 9.2.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
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

## Fallback: hand-build only if the bundled app cannot run

Only if `scripts/senzing_viz_server.py` cannot be located or run (and cannot be repaired) may you
hand-build an equivalent: a Python stdlib HTTP server (`http.server`) serving a single
self-contained D3 v7 page with the same four endpoints and tabs. If you hand-build the graph, you
MUST map each edge to expose `source`/`target` (from `source_entity_id`/`target_entity_id`)
**before** `forceLink().links(...)`, preserving node `id`/`entity_id`, omitting this map is a
silent failure that renders an empty graph. Generate the HTML via a Python generator script
(never write HTML+JS directly with file-write tooling). The full response schemas and the
search-enrichment specification are in `visualization-api-reference.md`. Even on the fallback
path, still write a standalone snapshot to `docs/visualizations/truthset_verification.html` so
the completion gate's guarantee holds.

When the bootcamper confirms they are done exploring, load `phase3-report-close.md`.
