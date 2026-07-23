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
- Present them with this attribution: "Based on your business problem, here are
  the query requirements I've derived:"
- List each requirement with its source (e.g. "From your success criterion about [X]..." or
  "From your desired output format of [Y]...").

👉 **Is there anything you'd like to adjust?**

*(Internal: end the turn on this question and wait.)*

- **Accepts or modifies:** proceed with the confirmed requirements.
- **Rejects all derived requirements:** ask the fresh open-ended question below (the same 👉
  question as the ELSE branch), without referencing the rejected items.

**ELSE** (file missing, OR both success-criteria and desired-outputs sections are missing or
empty): ask the fresh open-ended question:

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
Check: are name/address/phone fields populated? Were they mapped correctly during Data quality &
mapping? Is the data-quality score above 70%? If the data genuinely has no duplicates, that's a valid
finding, document it.

**Matching-concepts reminder.** When presenting results, briefly remind the bootcamper of the
matching concepts introduced earlier in the bootcamp, a sentence or two each, not a full re-explanation:

- **Features:** the categories of identifying information (NAME, ADDRESS, PHONE, etc.) Senzing
  extracts and compares, and how to read match-key strings like `+NAME+ADDRESS+PHONE`.
- **Confidence scores:** numeric indicators of match strength reflecting how many features
  agreed (higher means more evidence), not absolute probabilities.
- **Cross-source connections:** matches between records from different data sources, revealing
  the same entity exists in multiple systems.

Adapt the reminders to the bootcamper's own data context, reference the feature types, scores,
and data sources present in their current results, not the earlier sample data. Then tell
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

Explain first, as a statement: their loaded data and query programs will be preserved; after
remapping, they'll reload the affected sources and re-evaluate here. Then end the turn on this
single question:

👉 **Would you like to return to the Data quality & mapping module to refine your data mapping?**

*(Internal: end the turn on this question and wait.)*

If accepted:

1. Note which data sources need remapping in `config/bootcamp_progress.json` under a
   `quality_iteration` key.
2. Set `current_module` to `data_quality_mapping` (Module 5's name token — `current_module` holds
   a name token, never a catalog number, per INV-086) and `current_step` to the Phase 2 start step.
3. Load the Module 5 skill and begin at its Phase 2. (Module 5 port is a later phase; when it
   lands, route to its Phase 2 entry point.)

**Checkpoint:** write step 3b.

### 3c. Visualization offers (single gate)

All of this module's visualization offers are consolidated under one decision point here, after
the query results (3a) and quality evaluation (3b) are in hand. The Discover-phase opt-in in
step 4 is asked **independently** of this decision and covers only the why/how/network
demonstrations — it is not gated on, or bundled with, the visualization choice.

First, pin the umbrella offer verbatim:

> 👉 **Would you like to consider additional visualizations of your data?**

*(Internal: end the turn on this question and wait.)*

- **Declines:** skip every visualization sub-offer below and continue to "Next: Discover phase
  (step 4)". The umbrella question itself is the visualization offer for the Query Completeness
  Gate — checkpoint `m7_visualizations` as `{"offered": true, "accepted": false}` under
  `module_7_query`.
- **Accepts:** present each sub-offer below, each as its own pinned 👉 question, in order
  (a)→(d). A decline on any individual sub-offer is acknowledged and skipped (INV-014).
  Checkpoint `m7_visualizations` as `{"offered": true, "accepted": true}` plus the per-sub-offer
  results.

Common inline guidance for every sub-offer (until the Kiro `visualization-guide.md` /
`visualization-web-service.md` are ported): keep all generated code and output inside the working
directory (`src/` for code, HTML → `docs/visualizations/`, other output → `docs/` or `data/`;
never `/tmp/`); pull entity/relationship/report data through generated SDK code and
`reporting_guide`, never direct SQL; render every generated visualization offline (inline the
vendored D3 asset, no CDN) with palette/typography from `scripts/brand_tokens.py` (INV-081); after
generating an HTML visualization, capture screenshots
for the recap per `../bootcamp-onboarding/module-completion.md` → "Capturing visualization
screenshots" (skip silently with no headless capability, otherwise embed the 2-3 best in this
module's recap).

#### (a) Truth-Set-style interactive view

> 👉 **Would you like a Truth-Set-style interactive visualization of your own resolved data?**

Build it modeled on the shipped Truth Set visualization server (`scripts/senzing_viz_server.py`)
and the `../module-03b-truthset-visualization/visualization-api-reference.md` contract, in the
bootcamper's chosen programming language (INV-090), pointed at the bootcamper's loaded data
instead of the Truth Set. Render offline with the vendored D3 asset (INV-091) and take palette /
typography from `scripts/brand_tokens.py` (INV-081). `{name}` = `truthset_style_view`.

#### (b) Entity graph

> 👉 **Would you like a visualization of the resolved entities as an entity graph?**

The visualization data comes from `reporting_guide(topic='graph', ...)` (network export) and
`reporting_guide(topic='dashboard', ...)`; generate the rendering code in the chosen language,
rendered offline (inline the vendored D3 asset, no CDN) with palette/typography from
`scripts/brand_tokens.py` (INV-081). `{name}` = `entity_graph`.

#### (c) Results dashboard

> 👉 **Would you like a results dashboard showing entity counts, match statistics, and sample resolved entities?**

This is the bootcamp's single results-dashboard offer (Module 6 no longer offers one; it lives
here, where results visualization belongs). Source the data via
`reporting_guide(topic='dashboard', ...)` and `reporting_guide(topic='reports', ...)`; generate
the rendering code in the chosen language and save the HTML to
`docs/visualizations/results_dashboard.html` (INV-070), rendered offline (inline the vendored D3
asset, no CDN) with palette/typography from `scripts/brand_tokens.py` (INV-081).
`{name}` = `results_dashboard`.

#### (d) Data-specific visualization suggestions

Suggest at least two visualizations tailored to the bootcamper's data structure and resolution
results. Base the selection on the results and quality evaluation already gathered in steps 3a/3b
and on `config/data_sources.yaml` (number of sources, and whether multi-record / cross-source
entities are present) — this offer no longer depends on the Discover-phase pattern analysis,
which may not have run.

Visualization catalog, select based on the bootcamper's data:

- **Cross-source overlap heatmap:** suggest when 2+ data sources are loaded. Reveals which
  sources share the most resolved entities. Framing: "Since you have records from [Source A] and
  [Source B], a cross-source overlap heatmap would show which sources share the most resolved
  entities, helping you see where your data sources agree."
- **Entity size distribution chart:** suggest for any data. Shows records per entity (singletons
  vs. small merges vs. large merges).
- **Relationship network graph:** suggest when the results show disclosed relationships. Shows
  how entities connect through shared attributes.
- **Match key frequency analysis:** suggest when multi-record entities exist. Shows which feature
  combinations (match keys) drive the most resolutions. Framing: "A match key frequency chart
  would show which feature combinations, like NAME+ADDRESS or NAME+DOB, are driving the most
  resolutions in your data."
- **Feature score distribution:** suggest when multi-record entities exist. Shows how closely
  features match across resolved records — whether merges are near-exact or fuzzy. Framing: "A
  feature score distribution would show how tightly your resolved records match."

Selection logic: suggest at least 2 relevant to the bootcamper's specific data; do not suggest
visualizations that require patterns not present (no cross-source heatmap with one source; no
relationship network graph with no relationships; no match-key or feature-score views with no
multi-record entities; the entity size distribution chart is always applicable). For each,
explain concretely what it would reveal about their actual data (reference their real sources and
counts). When the bootcamper selects one, generate it in their chosen language, sourcing data via
`reporting_guide(topic='dashboard', ...)` / `reporting_guide(topic='graph', ...)`. On decline,
acknowledge and move on. `{name}` = `viz_suggestion_<slug>`.

**Checkpoint:** write step 3c to `config/bootcamp_progress.json`, recording `m7_visualizations`
(offered/accepted and which sub-offers were accepted, e.g. `{"offered": true, "accepted": true,
"truthset_style": false, "entity_graph": true, "results_dashboard": true, "suggestions_offered": 2}`).
The former separate `m7_exploratory_queries` (entity graph) and `m7_findings_documented`
(dashboard) checkpoints are subsumed here.

## Next: Discover phase (step 4)

The Discover phase introduces advanced Senzing capabilities using concrete examples from the
bootcamper's loaded data. It is opt-in and **independent of the visualization decision above** —
ask it whether or not the bootcamper wanted additional visualizations. The bootcamper can decline
or exit early at any demonstration point.

- Load `phase2-discover.md` for steps 4a–4c (data pattern analysis, why analysis, how
  analysis).
- Then load `phase2b-discover.md` for step 4d (relationship networks) and Discover Phase
  Completion. (The former step 4e data-specific visualization suggestions have moved to the
  step-3c visualization gate, sub-offer (d).)

Steps 4a–4d each checkpoint individually to `config/bootcamp_progress.json`. After the Discover
phase completes or is skipped, return here for the Query Completeness Gate.

## Success criteria

- ✅ Query programs created and tested.
- ✅ Visualizations offered (the single "additional visualizations?" gate in step 3c was
  presented; entity graph, results dashboard, Truth-Set-style view, and data-specific
  suggestions were available when accepted).
- ✅ Discover phase completed or explicitly skipped.

## Query Completeness Gate

Before wrapping up the module, confirm:

1. **Query programs created and tested?** At least one query program runs successfully
   against the resolved data.
2. **Visualizations offered?** The step-3c visualization gate was presented (the umbrella
   "additional visualizations?" question) — this counts as offered whether the bootcamper
   accepted or declined it.
3. **Discover phase status?** The Discover phase was either completed (all steps 4a–4d
   checkpointed) or explicitly skipped by the bootcamper.
4. **Ready to proceed?**

Module 7 is the **last content module before graduation** (required in every path). Once the gate
is satisfied, run the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md` (update progress, append the Module 7 recap section
to `docs/bootcamp_recap.md`, and present the end-of-module summary). Because this is the last
content module, the completion process ends with the graduation offer rather than a next-module
transition:

👉 **Would you like to graduate now and generate your production project and recap?**

*(Internal: end the turn on this question and wait.)* On module completion, set `current_step`
to `null` per the ground rules.

- **Affirmative:** invoke the `graduation` skill (GRADUATION banner, recap PDF, and `production/`
  project). See `../graduation/SKILL.md`.
- **Wants to keep exploring first:** stay available for more queries, visualizations, or Discover
  work, and offer graduation again whenever they are ready.
- **Production-hardening:** graduation is the close-out for everyone. Production-hardening
  (performance, security, monitoring, deployment) is delivered through the graduation production
  project and migration checklist, not as separate numbered modules.

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
