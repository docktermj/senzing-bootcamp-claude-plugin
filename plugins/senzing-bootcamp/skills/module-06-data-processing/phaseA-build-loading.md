# Module 6, Phase A: Build Loading Program (steps 1–4)

Follow the ground rules. `🛑`/`⛔` are internal control directives, never render them; signal
a stop by ending the turn on the single 👉 question and waiting. All loading, redo, and query
code comes from the MCP tools (`generate_scaffold` / `sdk_guide`), never hand-written.

## Before Loading: pre-load checks

Complete these three checks before starting step 1.

### Conditional workflow, check Phase 3 status

Read `config/data_sources.yaml` and check `test_load_status` per source:

- **`complete`**, Phase 3 was done in Module 5. Acknowledge: "You already test-loaded this
  source in Module 5 Phase 3 and saw [entity_count] entities. Module 6 builds on that with
  production-quality loading, error handling, progress tracking, throughput optimization, redo
  processing, and incremental strategies." Skip the basic test-load step and go straight to the
  production loading workflow.
- **`skipped` or missing**, include a brief test-load step: run a quick load of 10–100 records
  to verify the data loads before production concerns, then set `test_load_status: complete`.

**Phase 3 results integration:** if `test_load_status` is `complete` for multiple sources, use
`test_entity_count` to estimate total volume and plan resource allocation, use Phase 3 quality
assessments to inform load order (higher quality → stronger baseline), and note any issues
found during Phase 3 that may affect orchestration.

### Pre-load data freshness check (advisory only)

If the bootcamper is using CORD sample data (downloaded via `get_sample_data`), remind them to
confirm their data files haven't changed since download. This is advisory only, never block
loading. If they are using their own data, skip silently. (The Kiro CORD-freshness helper
`scripts/cord_metadata.py` is a later porting phase; give the reminder inline for now.)

### Anti-pattern check

Call `search_docs(query="loading", category="anti_patterns", version="current")`. Key pitfalls:
bulk-loading issues, threading problems, redo processing, load-order dependencies.

## 1. Assess production record volume

👉 **How many records do you expect to load in a production system?**

*(Internal: end the turn on this question and wait.)*

Example ranges to help answer:

1. Fewer than 500, demo/evaluation
2. 500 to 500,000, small production
3. 500,000 to 10,000,000, medium production
4. 10,000,000+, large production

**Classify and persist the tier.** Map the answer to a tier, `demo` (<500), `small`
(500–500K), `medium` (500K–10M), `large` (10M+). If the reply is a bare option number (1–4),
select that tier directly. If it is free text, parse the number and classify. If it is
unparseable, ask ONE clarifying follow-up presenting the four numbered tiers, then classify; if
still unparseable, default to `demo` and tell the bootcamper demo/evaluation was selected as
the default. Persist `production_volume` (`tier` and `raw_value`) to
`config/bootcamp_preferences.yaml` and checkpoint step 1 to `config/bootcamp_progress.json`.
(The Kiro helpers `answer_binding.py` / `volume_utils.py` encode this parsing and persistence;
the script port is a later phase, apply the logic inline for now.)

**License framing (default + expansion paths).** After the tier is classified, present
licensing as a default the bootcamper already has, never as a hard cap:

- Frame the built-in evaluation license as the default they already have. Present the expansion
  paths, apply an existing license, request one through the external channel
  (<support@senzing.com>), and, when available, request one in-flow via the Senzing MCP server
 , before any mention of downsizing. Downsizing (sampling or a smaller subset) is one option
  among these, not the only path.
- Source the record capacity and validity period from a Senzing MCP tool this session and
  present exactly what it returns. If a value is unavailable or the MCP server can't be reached,
  omit the figure and say it is currently unavailable, never substitute a remembered figure.
- Gate the in-flow path as Module 1 does: check `submit_feedback` availability via
  `get_capabilities` (wait up to 30s), and omit the in-flow path when it is unavailable, errors,
  or does not respond. If the bootcamper already has a license (`license` set in
  `config/bootcamp_preferences.yaml`), route them to the apply-an-existing-license path and omit
  the in-flow option. Refer to the Senzing MCP server by name only, never a URL.

**Checkpoint:** write step 1 to `config/bootcamp_progress.json`.

## 2. Identify the input data

Determine where the Senzing-formatted JSON records are for the first data source:

- Output from a transformation program (Module 5), in `data/senzing-ready/`
- Direct Entity Specification-compliant data files
- Database query results or API responses

Update the source's `load_status` to `loading` in `config/data_sources.yaml` and set
`updated_at`.

**Checkpoint:** write step 2.

## 3. Create the production loading program

Help the bootcamper build a complete, production-quality loading program for this source. All
generated code must follow the coding standards for the chosen language. (Full
`CODE_QUALITY_STANDARDS` reference is a later porting phase; apply clean-code conventions for
the language for now.)

**Volume-aware scaffold.** Read `production_volume` from `config/bootcamp_preferences.yaml`:

- **`medium` or `large`:** call `generate_scaffold(language='<chosen_language>',
  workflow='add_records', version='current', record_count=<raw_value>)` for threaded loading
  patterns. Add a code comment stating the tier and the architecture recommendation
  (multi-threaded with a thread pool for medium; distributed/queue-based for large).
- **`demo`, `small`, or missing:** call `generate_scaffold(language='<chosen_language>',
  workflow='add_records', version='current')` without `record_count`. Add a code comment
  stating the tier (or "no volume selection found") and that single-threaded loading is
  recommended.

Do not use inline examples, they may use outdated SDK patterns. Customize the scaffold with
the bootcamper's file path, data source name, and progress reporting. If the scaffold uses
`/tmp/`, `ExampleEnvironment`, or any path outside the working directory, override the database
path to `database/G2C.db` and keep all output files project-relative.

The program must include production-quality features:

- **Robust error handling:** per-record error logging with record ID, error code, and message.
  Failed records go to `logs/loading_errors.json` without stopping the load.
- **Progress tracking with throughput reporting:** display progress every N records (e.g. every
  100 or 1000) showing records loaded, error count, elapsed time, and records/second.
- **Statistics reporting:** at completion, report total attempted, loaded, failed, duration,
  throughput, and error summary.
- SDK initialization, record-loading loop, and proper cleanup.

**Save the program** in `src/load/` with a clear name (e.g.
`src/load/load_customer_db.[ext]`).

**Checkpoint:** write step 3.

## 4. Use MCP tools for code generation

Call `generate_scaffold` with workflow `add_records` and the chosen language for version-correct
SDK code. Call `sdk_guide(topic='load')` for platform-specific loading patterns.

**Checkpoint:** write step 4.

## SQLite volume pre-load check (stop-and-confirm heads-up, not a mandatory gate)

Run this once at the end of Phase A, immediately before the Phase B load begins. This is a
stop-and-confirm heads-up, NOT a mandatory gate, the bootcamper may always proceed on SQLite.

1. **Read inputs** from `config/bootcamp_preferences.yaml`: `production_volume.tier`,
   `production_volume.raw_value`, and `database_type`. If any value is missing/unreadable, treat
   it as indeterminate, do not fail; fall back to the existing advisory behavior and continue
   to the load.
2. **Decide whether it was already decided.** If a `sqlite_volume_prompt` marker in preferences
   is `decided: true` and its `tier`/`raw_value` match the current selection (or an applicable
   Module 4 SQLite load-time decision covers this same load), skip the prompt and proceed.
3. **Prompt only when it matters.** Present the prompt only when the tier is `medium` or `large`
   AND the database is SQLite AND it was not already decided. For demo/small tiers, any
   non-SQLite engine, indeterminate inputs, or an already-recorded choice: say nothing new about
   volume/SQLite and proceed to the Phase B load.
4. **When prompting**, explain that SQLite entity resolution slows as the database grows and
   present two choices, then end the turn and wait (internal stop), do not start the load yet:
   - **Migrate to PostgreSQL:** record `sqlite_volume_prompt` = `{decided: true, choice:
     "migrate", tier, raw_value}` in preferences, then hand off to the database-migration
     guidance (PostgreSQL migration is a production follow-up; see the graduation migration checklist). Do not restate migration steps here.
   - **Proceed on SQLite:** record `sqlite_volume_prompt` = `{decided: true, choice: "proceed",
     tier, raw_value}` in preferences, then continue to the Phase B load. Do not re-present this
     prompt for the same load.

*(Internal: when this heads-up fires, end the turn on the two-choice question and wait.)* Use
only synthetic/persisted values, never echo credentials or connection strings. (The Kiro
helpers `volume_utils.py`, `preferences_utils.py`, `load_time_warning.py`, and the migration
guide are later porting phases; apply the logic inline and refer to the graduation migration checklist for PostgreSQL migration for
now.)

Proceed to Phase B (`phaseB-load-first-source.md`).
