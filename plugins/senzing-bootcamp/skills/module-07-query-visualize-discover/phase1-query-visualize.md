# Module 7, Phase 1: Query and Visualize (steps 1–3d)

Follow the ground rules. `🛑`/`⛔` are internal directives, never render them; signal a stop by
ending the turn on the single 👉 question and waiting. On load, read
`config/bootcamp_progress.json` and resume from the first incomplete step; do not re-run
completed steps.

**No direct SQL (see SKILL.md):** all entity queries are generated SDK code
(`get_sdk_reference` + `sdk_guide` / `reporting_guide`); counts, stats, quality, and
visualization data come from `reporting_guide`. Never query `database/G2C.db` tables directly.

## 1. Define query requirements

**First action, before any bootcamper interaction in this step:** read
`docs/business_problem.md`.

**IF** `docs/business_problem.md` exists AND contains at least one success criterion or at
least one non-empty desired-output field:

- Derive between 1 and 10 query requirements from the success criteria and desired outputs in
  the document. Each derived requirement must reference the specific success criterion or
  desired output it addresses.
- Present them with this attribution: "Based on your business problem from Module 1, here are
  the query requirements I've derived:"
- List each requirement with its source (e.g. "From your success criterion about [X]..." or
  "From your desired output format of [Y]...").

👉 **Is there anything you'd like to add or change?**

*(Internal: end the turn on this question and wait.)*

- **Accepts or modifies:** proceed with the confirmed requirements.
- **Rejects all derived requirements:** ask a fresh open-ended question without referencing the
  rejected items: "What questions do you need to answer with your data?"

**ELSE** (file missing, OR both success-criteria and desired-outputs sections are missing or
empty): ask , 

👉 **What questions do you need to answer with your data?**

*(Internal: end the turn and wait.)*

Common queries (guidance for both paths): find duplicates within a source; find cross-source
matches; search for specific entities; get an entity 360 view; retrieve and format resolved
entities.

**Checkpoint:** write step 1 to `config/bootcamp_progress.json`.

## 2. Create query programs

For each query type, create a program in `src/query/` using the bootcamper's chosen language.

Use `generate_scaffold` with `workflow='query'` and the chosen language. For entity-view
patterns (get/why/how), consult `reporting_guide(topic='entity_views', language='<lang>',
version='current')`. For network/path patterns, consult `reporting_guide(topic='graph',
language='<lang>', version='current')`.

**Flags:** when generated query code calls SDK methods that accept flags (`get_entity`,
`get_entity_by_record_id`, `search_by_attributes`, `how_entity`, `why_entities`, `why_records`,
`why_record_in_entity`, `find_network`, `find_path`), look up available flags via
`get_sdk_reference(topic='flags')` (filter by method name) and select the flags matching the
bootcamper's query intent. Explain the choice in one sentence: "I'm using [flag] so we can see
[what it provides]." For visualization-bound queries, include `SZ_INCLUDE_FEATURE_SCORES`
and/or `SZ_INCLUDE_MATCH_KEY_DETAILS`.

**CRITICAL, file placement:** if the generated scaffold uses `/tmp/`, `ExampleEnvironment`, or
any path outside the working directory, override the database path to `database/G2C.db` and
ensure all output files use project-relative paths. No files outside the working directory.

Example query programs (extension depends on chosen language):

- `find_duplicates`: find entities with multiple records.
- `search_entities`: search by name, email, phone.
- `customer_360`: get the complete customer view.
- `query_results`: retrieve and format resolved entities.

**Iterate over records, not entity IDs.** The caller knows the record IDs and data source codes
they loaded, they do NOT know entity IDs (those are internal to Senzing). Query programs
iterate over loaded records (from the input JSONL file or a record manifest) and use
`get_entity_by_record_id(data_source, record_id)` to look up each record's entity. Never
iterate over a guessed range of entity IDs.

**Checkpoint:** write step 2.

## 3. Run exploratory queries

Execute the queries to understand results, using the run command for the chosen language.

**Checkpoint:** write step 3.

### 3a. Present query results and matching concepts

**If entity resolution found zero or very few matches:** this is a valid result, don't assume
something is broken. Tell the bootcamper: "Entity resolution found very few matches. This could
mean: (a) your records are genuinely distinct with no duplicates, (b) the matching criteria
need adjustment, perhaps key fields weren't mapped or data quality is too low, or (c) you're
working with a single source that has no internal duplicates. Let's investigate which one."
Check: are name/address/phone fields populated? Were they mapped correctly in Module 5? Is the
Module 5 data-quality score above 70%? If the data genuinely has no duplicates, that's a valid
finding, document it.

**Matching-concepts reminder.** When presenting results, briefly remind the bootcamper of the
matching concepts from Module 3, a sentence or two each, not a full re-explanation:

- **Features:** the categories of identifying information (NAME, ADDRESS, PHONE, etc.) Senzing
  extracts and compares, and how to read match-key strings like `+NAME+ADDRESS+PHONE`.
- **Confidence scores:** numeric indicators of match strength reflecting how many features
  agreed (higher means more evidence), not absolute probabilities.
- **Cross-source connections:** matches between records from different data sources, revealing
  the same entity exists in multiple systems.

Adapt the reminders to the bootcamper's own data context, reference the feature types, scores,
and data sources present in their current results, not the Module 3 sample data. Then tell
them: "If you'd like a deeper refresher on how Senzing matching works, features, scoring, or
cross-source connections, just ask and I'll walk through it again."

When presenting results from `how_entity` or the `why_*` methods (`why_entities`,
`why_records`, `why_record_in_entity`), ensure the query was called with
`SZ_INCLUDE_FEATURE_SCORES` and/or `SZ_INCLUDE_MATCH_KEY_DETAILS`. These flags provide the
scoring detail needed for informative output. If the query used default flags, note what
additional detail would be available with feature-score and match-key-detail flags.

**Checkpoint:** write step 3a.

### 3b. Quality evaluation

Call `reporting_guide(topic='quality', language='<chosen_language>', version='current')` for
the quality-evaluation methodology, then `search_docs(query='entity resolution quality
evaluation', version='current')` for additional context on interpreting results.

Present a quality summary:

| Indicator | Value | Assessment |
|-----------|-------|------------|
| Entity-to-record ratio | [computed] | [interpretation] |
| Possible matches | [count] ([%] of entities) | [interpretation] |
| Cross-source match rate | [%] | [interpretation] |

**Quality assessment:**

- **Acceptable** (proceed): ratio is reasonable, possible matches < 5%, no split/merge signals.
- **Marginal** (review): possible matches 5–15%, or some split/merge signals detected.
- **Poor** (iterate): possible matches > 15%, clear split/merge patterns, or no matching
  occurring.

Based on the assessment:

- **Acceptable:** "Your entity resolution quality looks good. Let's proceed to visualizations."
- **Marginal:** "I see some potential issues. Let me show you a few specific entities to
  review." (Present examples, then ask whether to proceed or iterate.)
- **Poor:** "The results suggest mapping improvements would help. Here's what I recommend..."
  (Present specific recommendations and offer the Module 5 feedback loop.)

**Module 5 feedback loop (when quality is poor or the bootcamper requests iteration):**

👉 **Would you like to return to Module 5 to refine your data mapping? Your loaded data and query programs will be preserved, after remapping, you'll reload the affected sources and re-evaluate here.**

*(Internal: end the turn on this question and wait.)*

If accepted:

1. Note which data sources need remapping in `config/bootcamp_progress.json` under a
   `quality_iteration` key.
2. Set `current_module` to 5 and `current_step` to the Phase 2 start step.
3. Load the Module 5 skill and begin at its Phase 2. (Module 5 port is a later phase; when it
   lands, route to its Phase 2 entry point.)

**Checkpoint:** write step 3b.

### 3c. Entity graph visualization checkpoint

Follow the Visualization Protocol and offer a visualization for checkpoint
`m7_exploratory_queries` (an entity graph of the resolved results). The visualization data
comes from `reporting_guide(topic='graph', ...)` (network export) and
`reporting_guide(topic='dashboard', ...)` (visualization concepts and data sources); generate
the rendering code in the bootcamper's chosen language.

Inline guidance until the visualization files are ported (later porting phase, the Kiro
`visualization-guide.md` and `visualization-web-service.md` are not yet available):

- Offer the visualization; do not force it. If the bootcamper declines, acknowledge and move on.
- Keep all generated code and output inside the working directory (`src/` for code, `docs/` or
  `data/` for output). Never `/tmp/`.
- Pull the entity/relationship data through generated SDK code and `reporting_guide`, never
  direct SQL.

**Deferred first-visualization guarantee:** if a visualization is generated here AND
`first_visualization` is `owed` in `config/bootcamp_progress.json` (Module 3 was opted out and
the standalone demo declined), also mark the journey-level first-visualization as satisfied by
`module_7_deferred` in `config/bootcamp_progress.json` (idempotent). This is journey-level only
,  it does not change the Module 3 Step 9 gate. (The Kiro `scripts/progress_utils.py` helpers
`is_first_visualization_owed` / `clear_first_visualization_owed` are a later porting phase;
for now update the progress key directly.)

**Checkpoint:** write step 3c.

### 3d. Results dashboard visualization checkpoint

Follow the Visualization Protocol and offer a visualization for checkpoint
`m7_findings_documented` (a results dashboard). Source the dashboard data via
`reporting_guide(topic='dashboard', ...)` and `reporting_guide(topic='reports', ...)`; generate
the rendering code in the chosen language. Same inline guidance and file-placement rules as
step 3c apply (visualization files are a later porting phase).

**Checkpoint:** write step 3d.

## Next: Discover phase (step 4)

The Discover phase introduces advanced Senzing capabilities using concrete examples from the
bootcamper's loaded data. It is opt-in, the bootcamper can decline or exit early at any
demonstration point.

- Load `phase2-discover.md` for steps 4a–4c (data pattern analysis, why analysis, how
  analysis).
- Then load `phase2b-discover.md` for steps 4d–4e (relationship networks, visualization
  suggestions, and Discover Phase Completion).

Steps 4a–4e each checkpoint individually to `config/bootcamp_progress.json`. After the Discover
phase completes or is skipped, return here for the Query Completeness Gate.

## Success criteria

- ✅ Query programs created and tested.
- ✅ Visualizations offered (entity graph and results dashboard).
- ✅ Discover phase completed or explicitly skipped.

## Query Completeness Gate

Before wrapping up the module, confirm:

1. **Query programs created and tested?** At least one query program runs successfully
   against the resolved data.
2. **Visualizations offered?** Both the entity graph and the results dashboard were offered.
3. **Discover phase status?** The Discover phase was either completed (all steps 4a–4e
   checkpointed) or explicitly skipped by the bootcamper.
4. **Ready to proceed?**

Module 7 is the **end of the Core track**. Once the gate is satisfied, run the standard
**Module Completion** process in `../bootcamp-onboarding/module-completion.md` (update progress,
append the Module 7 recap section to `docs/bootcamp_recap.md`, and present the end-of-module
summary). Because this is the last module of the Core track, the completion process ends with
the graduation offer rather than a next-module transition:

👉 **Module 7 complete, and that is the end of the Core track. Would you like to graduate now and generate your production project and recap trophy?**

*(Internal: end the turn on this question and wait.)* On module completion, set `current_step`
to `null` per the ground rules.

- **Affirmative:** invoke the `graduation` skill (GRADUATION banner, recap PDF, and `production/`
  project). See `../graduation/SKILL.md`.
- **Wants to keep exploring first:** stay available for more queries, visualizations, or Discover
  work, and offer graduation again whenever they are ready.
- **Advanced Topics track:** the bootcamper may instead continue to Module 8 (Performance
  Testing). The advanced modules (8-11) are a later porting phase; until they land, offer
  graduation as the close-out for both tracks.

## Integration patterns

After running queries, the bootcamper may ask "how do I use these results in my application?"
Present these common integration patterns and help them choose:

| Pattern | Real-time | Complexity | Best for |
|---------|-----------|------------|----------|
| Batch Report | No | Low | Reports, analytics, data warehouse feeds |
| REST API | Yes | Medium | Web apps, microservices, customer lookup |
| Streaming / Event-Driven | Yes | High | Real-time fraud detection, alerts, Kafka integration |
| Database Sync | No | Medium | Data warehouses, BI tools, legacy system integration |
| Duplicate Detection | No | Low | Data quality initiatives, stewardship, cleanup projects |
| Watchlist Screening | Yes | Medium | Compliance (KYC/AML), risk management |

When the bootcamper asks about integration, use `find_examples(query='REST API')` or
`find_examples(query='batch report')` for implementation patterns, and `generate_scaffold` for
code generation. Always iterate over known record IDs (from loaded data) rather than guessing
entity IDs.

**Key implementation principle:** query programs iterate over loaded records using
`get_entity_by_record_id(data_source, record_id)`: never over a guessed range of entity IDs.
The caller knows the record IDs and data source codes they loaded; entity IDs are internal to
Senzing.

Present the integration options and help the bootcamper choose the pattern that fits their use
case: batch reports, a REST API, streaming events, database sync, or duplicate detection.
