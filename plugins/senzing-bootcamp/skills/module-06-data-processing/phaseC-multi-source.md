# Module 6, Phase C: Multi-Source Orchestration (conditional, 2+ sources, steps 12–20)

Continues from Phase B. Follow the ground rules; `🛑`/`⛔` are internal control directives.
Orchestrator and redo code comes from the MCP tools, never hand-written.

**Conditional gate.** Read `config/data_sources.yaml` and count sources with `mapping_status:
complete`. If there is only ONE data source, skip Phase C entirely and proceed to Phase D
(`phaseD-validation.md`). Only present these steps when the bootcamper has 2 or more sources to
load.

## 12. Inventory all data sources

Read `config/data_sources.yaml` for `quality_score`, `mapping_status`, and `load_status` per
source. Enumerate every data source. For each: source name / DATA_SOURCE identifier, record
count, quality score, mapping status, loaded status. Present a summary table so the bootcamper
can review and confirm the list is complete.

**Checkpoint:** write step 12.

## 13. Analyze dependencies

Ask about data source dependencies. Common patterns: parent-child (load parents first),
reference data first, temporal ordering, or no dependencies. If a circular dependency is
detected, explain that Senzing resolves entities as records arrive, load the higher-quality
source first. Save the dependency map to `docs/loading_strategy.md`.

**Checkpoint:** write step 13.

## 14. Determine load order

Use `quality_score` from `config/data_sources.yaml` to rank sources; update `load_status` as
loading progresses. Apply ordering heuristics (priority order): (1) reference before
transactional, (2) quality-first for a strong entity baseline, (3) attribute-density-first,
(4) volume-first when quality is similar. Present the recommended load order with reasons for
the bootcamper to review.

**Checkpoint:** write step 14.

## 15. Select loading strategy

Present the options: **Sequential** (safer, easier to debug), **Parallel** (faster, more
resources), **Hybrid** (sequential for dependent sources, parallel for independent).

**Checkpoint:** write step 15.

## 16. Pre-load validation checklist

Verify before orchestration: each source's load file exists at its registry `file_path`
(`data/senzing-ready/` for mapped sources; `data/raw/` for `fast_pathed: true` CORD /
already-Senzing-ready sources, which skipped mapping in Module 5) and is non-empty;
unique DATA_SOURCE names match the Module 2 config; RECORD_IDs unique within each source; a
database backup of `database/G2C.db` exists; sufficient disk space (~2x per source); the
Module 6 loading program works as a template. Fix failures before proceeding.

**Checkpoint:** write step 16.

## 17. Create orchestrator program

Use `generate_scaffold(language='<chosen_language>', workflow='add_records', version='current')`
and `find_examples(query="multi-source")` for patterns. Override any `/tmp/` or
`ExampleEnvironment` paths to `database/G2C.db`. Save to `src/load/orchestrator.[ext]`.

Must handle: ordered loading with dependency enforcement, parallel execution if selected,
per-source progress/error tracking with error isolation, statistics aggregation, and a
completion summary.

**Production orchestration patterns to include:**

- **Retry with exponential backoff:** when a source fails to load, retry with increasing delays
  (1s, 2s, 4s, 8s) up to a configurable maximum. Log each retry attempt.
- **Partial success handling:** if some sources succeed and others fail, mark successful sources
  as loaded and report failed sources with error details. Do not roll back successful loads when
  one source fails.
- **Error isolation:** errors in one source's loading must not affect other sources. Each source
  loads in its own error boundary.
- **Orchestrator health monitoring:** track overall health, elapsed time, sources completed vs.
  remaining, error rate across all sources. Log periodic health summaries.

**Checkpoint:** write step 17.

## 18. Test orchestrator with sample data

Test the orchestrator with 10–100 records per source. Verify: sources load without errors,
dependencies respected, progress tracking works, error handling triggers correctly. Report the
sample-data test results and let the bootcamper know the orchestrator is ready for the full
dataset.

**Checkpoint:** write step 18.

## 19. Run full orchestration

Run on the complete dataset. Monitor per-source progress, error rates, overall completion, and
elapsed/estimated time. If slow, suggest reducing parallelism.

**⚠️ SQLite note:** if total records exceed 1,000, recommend loading a subset first to validate
cross-source matching, then load more or switch to PostgreSQL (a production follow-up; see the graduation migration checklist).

**Checkpoint:** write step 19.

## 20. Coordinated redo queue processing

Drain the redo queue, critical after multi-source loading for cross-source match refinement.
Use `generate_scaffold(language='<chosen_language>', workflow='redo', version='current')` and
override paths to `database/G2C.db`.

**Production redo patterns:**

- Process redos after all sources are loaded (not between sources) to minimize redundant
  re-evaluations
- Monitor redo queue depth during processing, a growing queue may indicate data-quality issues
- Log redo processing statistics: total redos processed, duration, entities affected

Tell the bootcamper: "Processing the redo queue now. This refines cross-source entity resolution.
Without it, some matches between your sources would be incomplete."

**Checkpoint:** write step 20.

Proceed to Phase D (`phaseD-validation.md`).
