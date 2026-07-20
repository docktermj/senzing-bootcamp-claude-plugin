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

**First, check whether there are real stakeholders.** Read `docs/business_problem.md`. If it carries
the bootcamp-generated marker `> 🤖 Bootcamp-generated business case` (the Business Case Offer was
accepted in Module 1), or otherwise records no real stakeholders, there are no business users to
involve — so **do not ask** the involvement question (INV-006/INV-012). State briefly that the
scenario is bootcamp-generated, so you will self-direct the UAT: spot-check 5–10 cross-source
entities and document findings in `docs/uat_results.md`, then proceed to step 26.

Otherwise (a real business problem with stakeholders), offer to involve business users — pin the
question verbatim:

👉 **Would you like to involve business users in testing the cross-source results?** (respond yes or no)

*(Internal: end the turn on this question and wait.)*

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

## 28. Document results

Record the validation findings:

- Save validation results to `docs/results_validation.md`
- Include: total records loaded, entities created, match rate, any issues found and their
  resolution
- This becomes the baseline for comparison

The **results dashboard** (entity counts, match statistics, and sample resolved entities) is offered
in the **Query, Visualize & Discover** module (Module 7, Step 3d), where all results visualization
lives — Module 6 does not offer it, to avoid a duplicate offer. (The cross-source relationship
visualization in step 23 is a distinct offer and is unaffected.)

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

Route on the UAT / match-accuracy results:

- **UAT ≥90% and match accuracy ≥90%:** state "Results look strong." and proceed to the module
  transition question.
- **UAT <80%:** state "Results need improvement — I recommend going back to Data quality & mapping
  to refine the mapping." and proceed to the transition question.
- **UAT 80–89%:** results are mixed, so ask the bootcamper to decide with a single pinned question
  (neutral lead + numbered list, INV-051):

  👉 **Most tests pass but there are gaps. What would you like to do? Reply with a number:**

  1. Iterate now to improve the results before moving on.
  2. Move forward to the next module.

  *(Internal: end the turn on this question and wait.)*

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
