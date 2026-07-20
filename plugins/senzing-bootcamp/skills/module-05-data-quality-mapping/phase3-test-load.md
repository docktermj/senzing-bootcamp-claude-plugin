# Module 5, Phase 3: Test Load and Validate (Optional) (steps 21–26)

Continues from Phase 2. Follow the ground rules; `🛑`/`⛔` are internal directives: do not
render them. Signal a stop by ending the turn on the single 👉 question and waiting.

> **This phase is optional.** Bootcampers who prefer to write custom loading programs can skip
> Phase 3 and proceed directly to Data processing. Phase 3 uses `mapping_workflow` steps 5–8 to give
> immediate feedback on ER quality without leaving Data quality & mapping.

> **Entry from the Step 5 `detect_environment` menu:** Phase 3 is entered from the
> `detect_environment` menu handled in `phase2-data-mapping.md` (step 11). When the bootcamper
> explicitly chooses **test_load** or **load+resolve** at that menu, follow the workflow below
> (`mapping_workflow` steps 5–8, Steps 21–26) unchanged. When sources remain unmapped, the
> Phase 2 guidance instead recommends **skip** and continues to the next source: the real
> production load is still deferred to Data processing in either case.

**Before starting Phase 3:** The Senzing SDK must be installed and configured (SDK setup). If it
is not yet set up, inform the bootcamper: "Phase 3 requires the Senzing SDK (from SDK setup). You can
skip Phase 3 and proceed to Data processing, or complete SDK setup first and return here." If the
bootcamper chooses to skip, update the data source registry with `test_load_status: skipped`
for each source and proceed to Data processing.

## Workflow (per data source that completed Phase 2)

### 21. SDK environment detection

Call `mapping_workflow(action='advance')` to advance to step 5 (SDK environment detection). The
workflow checks whether the Senzing SDK is installed and a database is configured. If detection
fails, offer to skip Phase 3 or return to Module 2. (Pass the exact `mapping_workflow` state
from Phase 2 unchanged; checkpoint to `config/mapping_state_[datasource].json` after this step.)

**Checkpoint:** write step 21 to `config/bootcamp_progress.json`.

### 22. Test data loading

Advance through `mapping_workflow` step 6: load test data into a fresh SQLite database. This
loads a sample from the Phase 2 transformation output to verify the mapping produces valid
Senzing records.

**Checkpoint:** write step 22.

### 23. Validation report generation

Advance through `mapping_workflow` step 7: generate a validation report covering record counts,
feature coverage, and data quality metrics for the test load.

**Checkpoint:** write step 23.

### 24. Entity resolution evaluation

Advance through `mapping_workflow` step 8: evaluate entity resolution results from the test
load. Present match counts, entity counts, and quality assessment to the bootcamper. Explain
what the numbers mean: how many records resolved into how many entities, what the deduplication
rate suggests about data quality, and whether the mapping is producing good results.

**Checkpoint:** write step 24.

#### 24a. Capture ER statistics

After evaluating entity resolution results, capture the current statistics to a JSON file for
comparison tracking. Query the following counts through the Senzing SDK: never with direct SQL
against `database/G2C.db`. Per the ground-rules MCP routing, get counts/stats via
`reporting_guide`, or generate SDK code with `generate_scaffold` / `find_examples` and run it:

- **entity_count:** total resolved entities
- **record_count:** total records loaded
- **match_count:** number of matches (records that resolved together)
- **possible_match_count:** number of possible matches flagged
- **relationship_count:** number of disclosed relationships

Save the statistics to `config/er_current_{datasource}.json` (datasource name lowercased):

```json
{
  "datasource": "CUSTOMERS",
  "entity_count": 847,
  "record_count": 1000,
  "match_count": 153,
  "possible_match_count": 12,
  "relationship_count": 45,
  "captured_at": "2026-04-20T14:30:00Z"
}
```

#### 24b. Baseline detection

Check whether a baseline file exists at `config/er_baseline_{datasource}.json` (lowercase
datasource name).

- **If no baseline exists:** This is the first test load for this data source. Save the current
  statistics as the baseline:

  ```text
  No baseline found for {DATASOURCE}. Saving current statistics as your first baseline.
  ```

  Copy `config/er_current_{datasource}.json` to `config/er_baseline_{datasource}.json`. Inform
  the bootcamper that future test loads will compare against this baseline so they can see how
  mapping changes affect entity resolution quality.

- **If a baseline exists:** Proceed to step 24c (comparison).

#### 24c. Compare against baseline

When a baseline exists, compute the diff between `config/er_baseline_{datasource}.json` and
`config/er_current_{datasource}.json` and present it. (The Kiro `compare_results.py` helper is a
later porting phase; compute the per-metric deltas directly for now.) Show per-metric deltas
(entities gained/lost, matches gained/lost) and an overall quality assessment (improved,
degraded, or unchanged). Explain what the changes mean:

- **Fewer entities + more matches** → better deduplication, mapping improvement
- **More entities + fewer matches** → less deduplication, possible mapping regression
- **Unchanged** → mapping change had no measurable impact on ER quality

#### 24d. Accept or reject new baseline

> **Only present this gate when a prior baseline existed** (i.e., this is not the first test
> load). On the first test load, the baseline is saved automatically in step 24b without asking.

👉 **Your mapping change resulted in [quality_assessment]. What would you like to do? Reply with a number:**

1. Accept these results as your new baseline.
2. Iterate on the mapping and try again.

*(Internal: end the turn on this question and wait.)*

- **If accepted:** Copy `config/er_current_{datasource}.json` to
  `config/er_baseline_{datasource}.json`. Confirm: "New baseline saved. Future test loads will
  compare against these results."
- **If rejected:** Keep the existing baseline unchanged. Inform the bootcamper they can return
  to Phase 2 to adjust their mapping and re-run Phase 3 to see updated results.

After `mapping_workflow` steps 5–8 generate output files into the workspace, place them into the
correct project subdirectories per the file-placement guidance in `phase2-data-mapping.md`.

### 25. Present results and decision gate

Present the Phase 3 results summary for this data source: records loaded, entities created,
deduplication rate, quality assessment, and any issues found. Then pin the decision-gate question
verbatim:

👉 **Are you ready to proceed?** (respond yes or no)

*(Internal: end the turn on this question and wait.)*

> **Data source registry:** Update the source's `test_load_status` to `complete` and
> `test_entity_count` to the entity count from the test load in `config/data_sources.yaml`. Set
> `updated_at`.

**Checkpoint:** write step 25.

### 26. Module completion and shortcut path decision

After all sources have completed (or skipped) Phase 3, run the standard **Module Completion**
process in `../bootcamp-onboarding/module-completion.md` (update progress, append the Module 5
recap section to `docs/bootcamp_recap.md`, and present the end-of-module summary). Then present
the decision gate below.

Data processing is the next module by default. The shortcut path is only
taken when the bootcamper explicitly requests it (skipping a module requires a bootcamper
request, per the ground rules):

- **Shortcut path (→ Query, Visualize and Discover):** For simple use cases: single data source, small dataset
  (≤1000 records), no production requirements: the Phase 3 test load results may be sufficient.
  The bootcamper can proceed directly to Query, Visualize and Discover and skip
  Data processing.
- **Full path (→ Data processing):** For production requirements, multiple data sources, datasets
  exceeding 1000 records, or when the bootcamper wants to learn production-quality loading
  patterns: recommend the full Data processing path.

👉 **Which path would you like to take? Reply with a number:**

1. Shortcut path — go directly to Query, Visualize and Discover.
2. Full path — continue to Data processing for production-quality loading.

*(Internal: end the turn on this question and wait.)*

> **If the bootcamper chooses the shortcut path:** Update `config/bootcamp_progress.json` to
> mark Module 6 as skipped with reason `shortcut_path`:
>
> ```json
> {
>   "modules_skipped": {
>     "6": { "reason": "shortcut_path", "skipped_at": "<timestamp>" }
>   }
> }
> ```

> **Data source registry:** If Phase 3 was skipped for any source, update that source's
> `test_load_status` to `skipped` in `config/data_sources.yaml`. Set `updated_at`.

> **Optional: baseline status summary (advisory, non-blocking):** On Phase 3 completion you
> MAY surface which data sources still lack an ER baseline (compare the set of
> `config/er_baseline_*.json` files against the mapped sources). It is read-only, never blocks
> the workflow, and never creates, modifies, or deletes a baseline. (The Kiro
> `baseline_status.py` helper is a later porting phase; report coverage directly if you choose
> to.)

**Checkpoint:** write step 26.

## Phase 3 session resume

On session resume during Phase 3, read both the mapping state checkpoint
(`config/mapping_state_[datasource].json`) and `config/bootcamp_progress.json` to determine
which Phase 3 steps (21–26) completed. Restart `mapping_workflow` and fast-track through
completed steps (5–8). If the test load (step 22) completed but evaluation (step 24) did not,
re-run evaluation without reloading. If the session was interrupted before the decision gate
(step 26), present the Phase 3 results again and resume from the decision gate.

## Rules

- NEVER hand-code attribute names: use `mapping_workflow`.
- NEVER guess method signatures: use `generate_scaffold` / `get_sdk_reference`.
- NEVER save to `/tmp/`: all files project-relative per the ground-rules file-placement
  contract.
- Never generate direct SQL against `database/G2C.db`: all data access goes through Senzing
  SDK methods (counts/stats via `reporting_guide`).
- Always validate with `analyze_record` before loading.

## Success criteria

- ✅ Test load completed for each data source (or explicitly skipped).
- ✅ Entity resolution results reviewed (deduplication rate, quality assessment).
- ✅ Decision gate completed (shortcut path or proceed to Data processing).

## Interpreting `analyze_record` results

Structural errors from `analyze_record` (e.g., flat format instead of a FEATURES array, missing
required fields) can leave the Feature Analysis table empty with headers but no rows. This is
expected, not a bug: feature analysis is skipped when structural errors block feature
extraction. Fix the structural errors listed above the table in the transformation program,
then re-validate.

## Encoding

- Detect encoding in the profiling step. Convert to UTF-8 in the transformation program.
- Non-Latin scripts: `search_docs(query="globalization", category="globalization")`.
- Strip the UTF-8 BOM from Windows CSV files. JSON libraries handle special character escaping.

## Hooks

In the Claude Code plugin, bootcamp hooks ship with the plugin: there is no manual hook-install
step (this replaces the Kiro `install_hooks.py` / `.kiro/hooks/` workflow). The plugin's Stop
hook is a safety net for the closing 👉 question; you still own that question on every yielding
turn (see the ground rules).
