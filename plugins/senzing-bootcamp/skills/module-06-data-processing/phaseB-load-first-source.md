# Module 6, Phase B: Load First Source (steps 5–11)

Continues from Phase A. Follow the ground rules; `🛑`/`⛔` are internal control directives.
Loading and redo code comes from the MCP tools (`generate_scaffold` / `sdk_guide`), never
hand-written. Back up `database/G2C.db` before loading. The `DATA_SOURCE` codes in this data
were registered in Phase A (step 4a), so the load runs against a config that already knows them
(the loader's generic `SENZ2207` handling remains a fallback).

## 5. Test with sample data (if Phase 3 was skipped)

If the bootcamper did not complete Phase 3 in Module 5, run the loading program on a small
subset first:

- Start with 10–100 records
- Verify the program connects to the engine
- Check that records are being added successfully
- Observe any errors or warnings

If Phase 3 was completed, skip this step, the test load already verified basic loading. Proceed
directly to production loading.

**Checkpoint:** write step 5.

## 6. Observe entity resolution in real time

As records load, Senzing resolves entities automatically:

- Watch the console output for resolution activity
- Note how entities are being formed
- See how new records match or create entities
- This gives immediate feedback on data quality and matching behavior

**Checkpoint:** write step 6.

## 7. Load the full dataset

Run the program on the complete data source with production-quality monitoring:

- Monitor progress and throughput performance
- Watch for error-rate trends (increasing errors may indicate data issues)
- Note loading statistics (time, throughput, error rate)
- If errors exceed 5%, pause and investigate before continuing

**License capacity before loading.** Before warning that the load will stop at the built-in
evaluation limit (a licensing error at the cap), read `license_record_limit` from
`config/bootcamp_progress.json` (the Module 4 license gate at Step 8a persists it after a custom
license is configured) and drive the decision from that effective limit, never a remembered or
hardcoded figure:

- **`0` (no cap), or ≥ the dataset size**, the active license permits the full load: omit the
  evaluation-capacity warning and proceed.
- **Positive and below the dataset size**, the dataset genuinely exceeds the cap: the single
  License Key gate (Module 4, Step 8a) already offered to expand capacity — restate that a larger
  license lets the full load proceed, as a choice, not a wall; do not force downsizing.
- **Absent or null** (no custom license detected), warn that the evaluation license halts the
  load at its cap, confirming the current capacity figure and the exact over-limit error code and
  behavior from the Senzing MCP server at request time. If no figure is returned, say it is
  currently unavailable rather than restating a remembered one.

**Data source registry.** On success, update `load_status` to `loaded` and `record_count` to the
actual loaded count in `config/data_sources.yaml`. On failure, set `load_status` to `failed` and
add an `issues` entry describing the error. Update `updated_at` either way.

**⚠️ SQLite performance note:** on SQLite with single-threaded loading, entity resolution gets
progressively slower as the database grows. For the bootcamp learning experience, recommend
loading ≤1,000 records initially, enough to see meaningful entity resolution without long
waits. If the bootcamper has more data, suggest: "Let's start with the first 1,000 records so we
can see results quickly. Once we validate the results here, we can load the full dataset, or
switch to PostgreSQL for better performance with larger volumes (a production follow-up; see the graduation migration checklist)."

**Checkpoint:** write step 7.

## 8. Save and document the loading program

- Save in `src/load/` with a clear name (e.g. `src/load/load_customer_db.[ext]`); all loading
  programs live in `src/load/`
- Document how to run it (command line, configuration)
- Note any prerequisites or dependencies
- Keep it for future reloads or updates

**Checkpoint:** write step 8.

## 9. Process redo records

After loading completes, drain the redo queue. Redo records are deferred re-evaluations that
refine the entity resolution graph, without processing them, results are incomplete.

Use `generate_scaffold(language='<chosen_language>', workflow='redo', version='current')` for the
redo processing pattern. The loading program (or a separate script) should sequentially process
all pending redos until the queue is empty. If the generated redo scaffold uses `/tmp/`,
`ExampleEnvironment`, or any path outside the working directory, override the database path to
`database/G2C.db`.

Include a code comment explaining that in production, redos are typically handled by an
always-running redo processor that wakes, checks for pending redos, processes them, and sleeps
when the queue is empty.

Tell the bootcamper: "Processing the redo queue now. This refines entity resolution, without
it, some matches would be incomplete."

**Checkpoint:** write step 9.

## 10. Incremental loading strategy

Discuss incremental loading as a production concern distinct from the initial bulk load:

- **Full reload** (what we just did): load all records every time. Simple but slow for large
  datasets.
- **Incremental load** (production pattern): track which records are new or changed since the
  last load; load only deltas. Requires a change-detection mechanism (timestamps, sequence
  numbers, change data capture).
- **Upsert pattern:** use `add_record` with the same `RECORD_ID` to update existing records.
  Senzing re-evaluates entity resolution automatically.
- Help the bootcamper understand when each strategy applies and document the choice in
  `docs/loading_strategy.md`.

**Checkpoint:** write step 10.

## 11. Mark first data source as loaded

Once loading and redo processing are complete, mark this data source as loaded in
`config/data_sources.yaml`.

**Checkpoint:** write step 11.

**Next:** if the bootcamper has 2 or more data sources with `mapping_status: complete`, proceed
to Phase C (`phaseC-multi-source.md`). If only ONE data source, skip Phase C and go directly to
Phase D (`phaseD-validation.md`).
