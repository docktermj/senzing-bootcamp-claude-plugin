# Module 6, Phase D: Validation (steps 21–28)

Continues from Phase B (single source) or Phase C (multi-source). Follow the ground rules;
`🛑`/`⛔` are internal control directives. Entity queries use SDK code generated via
`generate_scaffold` / `get_sdk_reference`, never direct SQL against `database/G2C.db`. Counts
and stats come from `reporting_guide`.

## Single-source validation (always)

## 21. Validate match accuracy

Review the entity resolution results:

- Query a sample of known records (SDK method `get_entity_by_record_id`) to check how they
  resolved
- Look for expected matches, are records that should match resolving to the same entity?
- Look for false positives, are unrelated records being incorrectly merged?
- Look for false negatives, are records that should match resolving to separate entities?
- If match accuracy is poor, revisit data quality (Module 5) or mapping before proceeding

Use `generate_scaffold(language='<chosen_language>', workflow='query', version='current')` to
generate SDK code that retrieves sample entities for review. Use
`get_sdk_reference(topic='functions', filter='why_entities', version='current')` to explain why
records matched. (There is no direct entity-query MCP tool, entity lookup and why-matched are
done through generated SDK code.)

**Checkpoint:** write step 21.

## 22. Run basic UAT for single-source

Validate that the loaded data meets business expectations:

- Verify record counts, does the number of loaded records match expectations? (Use
  `reporting_guide` for counts.)
- Spot-check entity resolution, pick 5–10 known entities and confirm they resolved correctly
- Document any issues found in `docs/uat_results.md`
- If critical issues are found, fix and reload before proceeding

**Checkpoint:** write step 22.

## Cross-source validation (conditional, 2+ sources loaded)

Only present steps 23–27 when the bootcamper has loaded 2 or more data sources. For
single-source bootcampers, skip directly to step 28 (Document results).

## 23. Validate cross-source results

Validate: record counts match expectations, cross-source entities exist, no unexpected data
loss, error logs clean. Use `reporting_guide(topic='graph', version='current')` for
network-graph patterns.

Sample 15–25 entities that contain records from multiple data sources and verify they represent
the same real-world person or organization. Check cross-source matches and spot-check
single-source entities to confirm no cross-source matches were missed.

Offer to visualize the cross-source entity relationships as a web page. Pin the offer verbatim:

> 👉 **Would you like a web page visualizing the cross-source entity relationships?**

If accepted, save to `docs/visualizations/multi_source_results.html`, then capture screenshots for
the recap (`{html}` = `multi_source_results.html`, `{name}` = `multi_source_results`) per
`../bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots" — skip
silently if no headless capability, otherwise embed the 2-3 best in this module's recap.

**Checkpoint:** write step 23.

## 24. Validate cross-source results quality

Use `reporting_guide(topic='evaluation', version='current')` for the 4-point ER evaluation
framework and `reporting_guide(topic='quality', version='current')` for precision/recall
metrics.

Validate: match accuracy (query known records via the generated SDK code / SDK method
`get_entity_by_record_id`), false positives (incorrect merges), false negatives (missed
matches), data completeness. If accuracy is poor, revisit Module 5 mapping.

**Checkpoint:** write step 24.

## 25. Execute UAT with business users

Offer to involve business users in testing the cross-source results.

- **Yes:** share cross-source match examples, collect feedback, document in
  `docs/uat_results.md`.
- **No:** spot-check 5–10 cross-source entities and document findings in `docs/uat_results.md`.

**Checkpoint:** write step 25.

## 26. Get stakeholder sign-off

Create `docs/results_validation.md` with match-quality metrics (true/false positive/negative
rates) and business validation results (test cases passed, issues, resolution plan).

**Checkpoint:** write step 26.

## 27. Document validation results

Save all findings to `docs/results_validation.md`: total records loaded, entities created,
cross-source match rate, UAT results, stakeholder feedback/sign-off status. This becomes the
validation baseline before Module 7.

Update `docs/loading_strategy.md` with: final load order and rationale, per-source statistics,
cross-source match summary, issues and resolutions, recommendations for future loads.

**Checkpoint:** write step 27.

## Document results and complete (always)

## 28. Document results and offer visualization

Record the validation findings:

- Save validation results to `docs/results_validation.md`
- Include: total records loaded, entities created, match rate, any issues found and their
  resolution
- This becomes the baseline for comparison

**Mandatory visualization offer (internal gate).** You MUST offer the results dashboard before
proceeding to the Decision Gate, do not skip it. Pin the offer verbatim:

> 👉 **Would you like a results dashboard showing entity counts, match statistics, and sample resolved entities?**

- **Yes:** generate the HTML dashboard and save to `docs/visualizations/results_dashboard.html`,
  then capture screenshots for the recap (`{html}` = `results_dashboard.html`, `{name}` =
  `results_dashboard`) per `../bootcamp-onboarding/module-completion.md` → "Capturing visualization
  screenshots" — skip silently if no headless capability, otherwise embed the 2-3 best in the recap.
- **No / not now:** acknowledge and proceed.
- **Unsure:** briefly explain the value, then wait for their decision.

*(Internal: end the turn on the dashboard offer question and wait.)*

**Deferred first-visualization guarantee:** after generating the dashboard, if
`first_visualization` is `owed` in `config/bootcamp_progress.json` (Module 3 was opted out and
the standalone demo declined), also clear that owed marker (set it to satisfied by
`module_6_deferred`). Check whether it is owed first; the clear is idempotent. This is the
journey-level guarantee only, it does not change the Module 3 gate. (The Kiro helper
`scripts/progress_utils.py` and `visualization-guide.md` are later porting phases; apply the
clear inline for now.)

**Checkpoint:** write step 28.

## Recovery from failed load

If loading fails partway through:

1. **Check what loaded**, query known RECORD_IDs (via generated SDK code) to see if they exist.
2. **Decide, wipe and restart vs. resume:**
   - **Wipe and restart:** restore from the `database/G2C.db` backup, fix the issue, re-run.
   - **Resume:** modify the loading program to skip already-loaded records.
3. **If the database is corrupted**, restore from backup. If no backup, delete
   `database/G2C.db` and re-run the Module 2 config.
4. **Common causes:** disk full, out of memory, invalid records, network timeout.

(The Kiro backup/restore helper `scripts/restore_project.py` is a later porting phase; restore
from your own `database/G2C.db` backup for now.)

### Multi-source recovery (Phase C)

If a source fails during orchestration, present three options:

1. **Skip and continue:** mark it failed, continue with remaining sources.
2. **Retry after fix:** pause, fix the issue, retry the failed source.
3. **Restore and restart:** restore from backup, fix, restart orchestration.

## Iterate vs. proceed decision gate

- **UAT ≥90% and match accuracy ≥90%:** "Results look strong. Ready to proceed to Module 7."
- **UAT 80–89%:** "Most tests pass but there are gaps. Iterate or move forward?"
- **UAT <80%:** "Results need improvement, suggest going back to Module 5."

## Stakeholder summary

After validation, always produce a one-page executive summary — no question (INV-012) —
following the Module 6 guidance, and save it to `docs/stakeholder_summary_module6.md`. Announce
it as a produced file in the end-of-module summary's "Files produced" list (INV-032). (The Kiro
`templates/stakeholder_summary.md` port is a later phase; compose the summary directly for now.)

## Success criteria

- ✅ Loading program generated with production-quality error handling, progress tracking, and
  statistics
- ✅ At least one data source fully loaded with error rate < 1%
- ✅ Redo queue drained after loading
- ✅ Loading statistics documented in `docs/loading_strategy.md`
- ✅ Match accuracy reviewed (sample entities checked for false positives/negatives)
- ✅ Results validation documented in `docs/results_validation.md`
- ✅ Loading program saved in `src/load/`

**Additional criteria when 2+ sources loaded:**

- ✅ All sources loaded (or failures documented) with error rate < 1% per source
- ✅ Dependencies respected, cross-source matches reviewed
- ✅ Orchestrator program saved in `src/load/orchestrator.[ext]`
- ✅ Cross-source match accuracy validated
- ✅ UAT executed, results in `docs/uat_results.md`
- ✅ Stakeholder sign-off obtained

## Advanced reading

- After completing Module 6, ask about record updates, deletions, entity re-evaluation, and redo
  processing, use `search_docs` and `get_sdk_reference` for current guidance for production
  systems where source data changes over time.
- For production systems that receive ongoing data, ask about incremental loading patterns, use
  `search_docs` and `generate_scaffold` for current guidance on adding new records to an existing
  database, processing redo records after incremental loads, and monitoring pipeline health.

(The Kiro multi-source reference `data-processing-reference.md` and the user reference
`docs/modules/MODULE_6_DATA_PROCESSING.md` are later porting phases.)

## Module completion and transition to Module 7

Follow the Decision Gate above to frame readiness. When results are ready, run the standard
**Module Completion** process in `../bootcamp-onboarding/module-completion.md` (update progress,
append the Module 6 recap section to `docs/bootcamp_recap.md`, and present the end-of-module
summary), then close the module:

👉 **Are you ready to move on to the next module: {next module name}?**

*(Internal: end the turn on this question and wait.)* On completion, set `current_step` to
`null` in `config/bootcamp_progress.json` and, on an affirmative reply, produce the Module 7
start banner, journey map, and before/after framing per the ground rules.

**Success indicator:** ✅ All data sources loaded + redo records processed + no critical errors +
entity resolution results validated + results documented in `docs/results_validation.md`.
