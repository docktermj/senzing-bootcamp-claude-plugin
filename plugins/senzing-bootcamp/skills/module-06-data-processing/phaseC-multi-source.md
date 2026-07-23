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

Explain the common dependency patterns: parent-child (load parents first), reference data first,
temporal ordering, or none. If a circular dependency is detected, explain that Senzing resolves
entities as records arrive, load the higher-quality source first.

**First, check the data's provenance.** Read the `provenance` field for each source being loaded
(step 12's inventory) in `config/data_sources.yaml` — the same field Module 5's fast-path uses. If
**every** such source is agent-generated (`provenance: cord` or `synthesized`), or
`docs/business_problem.md` carries the bootcamp-generated marker `> 🤖 Bootcamp-generated business
case`, the agent selected these sources itself and already knows there are no real load-order
dependencies between them. State that briefly (INV-012) and confirm rather than asking an open
question — pin the question verbatim (INV-056) and end the turn on it:

👉 **The generated sources have no load-order dependencies — shall I proceed with none?** (respond yes or no)

*(Internal: end the turn on this question and wait.)* On **yes**, record that there are none; on
**no**, ask the bootcamper to describe the dependencies they see and capture the dependency map.

Otherwise (some source being loaded is bootcamper-supplied — `provenance: own`/`free_data`/`unknown` —
and no generated marker is present), ask a single pinned 👉 question (INV-056) exactly as today and end the turn
on it:

👉 **Are there load-order dependencies between your data sources?**

*(Internal: end the turn on this question and wait.)* On **yes**, capture the dependency map; on
**no**, record that there are none.

Save the resulting dependency map (or the "no dependencies" record) to `docs/loading_strategy.md`.

**Checkpoint:** write step 13.

## 14. Determine load order

Use `quality_score` from `config/data_sources.yaml` to rank sources; update `load_status` as
loading progresses. Apply ordering heuristics (priority order): (1) reference before
transactional, (2) quality-first for a strong entity baseline, (3) attribute-density-first,
(4) volume-first when quality is similar. Present the recommended load order with reasons for
the bootcamper to review.

**Checkpoint:** write step 14.

## 15. Select loading strategy

**First, check the data's provenance** (as in step 13). If **every** source being loaded is
agent-generated (`provenance: cord`/`synthesized` in `config/data_sources.yaml`, or the
`> 🤖 Bootcamp-generated business case` marker is present in `docs/business_problem.md`), the agent
selected these sources and can recommend a strategy from what it knows: for the generated (typically
small) dataset, **Sequential** — safer, easy to debug, with no real gain from parallelism at this
scale. State that briefly (INV-012) and confirm rather than posing the open menu — pin the question
verbatim (INV-056) and end the turn on it:

👉 **I recommend the Sequential loading strategy for this generated dataset — shall I use it?** (respond yes or no)

*(Internal: end the turn on this question and wait.)* On **yes**, record Sequential; on **no**,
present the numbered menu below so the bootcamper chooses (INV-007).

Otherwise (some source being loaded is bootcamper-supplied — `provenance: own`/`free_data`/`unknown` —
and no generated marker is present), present the strategy choices as a neutral lead + numbered list (INV-051),
pinned verbatim (INV-056), and end the turn on the 👉 question:

👉 **Which loading strategy would you like? Reply with a number:**

1. **Sequential** — safer, easier to debug.
2. **Parallel** — faster, uses more resources.
3. **Hybrid** — sequential for dependent sources, parallel for independent.

*(Internal: end the turn on this question and wait.)*

**Checkpoint:** write step 15.

## 16. Pre-load validation checklist

Verify before orchestration: each source's load file exists at its registry `file_path`
(`data/senzing-ready/` for mapped sources; `data/raw/` for `fast_pathed: true` CORD /
already-Senzing-ready sources, which skipped mapping in Module 5) and is non-empty;
each source's DATA_SOURCE code is registered in the engine config (register any not yet
registered, idempotently — per Phase A step 4a; do not rely on Module 2's default config, which
predates data collection); RECORD_IDs unique within each source; a
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
