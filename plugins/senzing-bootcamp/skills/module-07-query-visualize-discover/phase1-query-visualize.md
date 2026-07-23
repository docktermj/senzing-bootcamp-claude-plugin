# Module 7, Phase 1: Query and Visualize (steps 1–3c)

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

### 3c. Visualization offer (single gate)

This module's results visualization is delivered as **one** interactive, tabbed app — the same
Truth-Set-style visualization built in the Truth Set module, now pointed at the bootcamper's own
resolved data. It is the single visualization artifact: the entity graph, relationship network,
results dashboard, cross-source overlap heatmap, match-key frequency, and feature-score views are
all **tabs** of this one app, not separate offers or static pages (see the full tab set and the
de-duplication rules in `../module-03b-truthset-visualization/visualization-api-reference.md`).
This is also where Module 6's cross-source relationship view now lives — the Entity Graph,
Cross-Source, and Relationship Network tabs replace the former Module 6 `multi_source_results.html`
static page (Module 6 no longer offers a visualization). Offer it here, after the query results
(3a) and quality evaluation (3b) are in hand. The
Discover-phase opt-in in step 4 is asked **independently** of this decision and covers only the
why/how/network demonstrations — it is not gated on, or bundled with, the visualization choice.

Pin the offer verbatim:

> 👉 **Would you like an interactive visualization of your resolved data — entity graph, relationship network, results dashboard, cross-source overlap, and match/feature analysis, all in one app?**

*(Internal: end the turn on this question and wait.)*

- **Declines:** skip the visualization and continue to "Next: Discover phase (step 4)". This
  question is itself the visualization offer for the Query Completeness Gate (it covers the entity
  graph and results dashboard as tabs) — checkpoint `m7_visualizations` as `{"offered": true,
  "accepted": false}` under `module_7_query`.
- **Accepts:** build and present the app (below), then checkpoint `m7_visualizations` as
  `{"offered": true, "accepted": true, "artifact": "docs/visualizations/<file>.html"}`.

Build it modeled on the shipped Truth Set visualization server (`scripts/senzing_viz_server.py`)
and the `../module-03b-truthset-visualization/visualization-api-reference.md` contract, in the
bootcamper's chosen programming language (INV-090), pointed at the bootcamper's loaded data instead
of the Truth Set. It MUST:

- Serve/render every applicable tab from that contract — Entity Graph, Relationship Network, Record
  Merges, Merge Statistics, Match Keys, Feature Scores, Cross-Source, Results Dashboard, and
  Search / Probe. Tabs whose data is absent are simply not shown (e.g. Cross-Source needs 2+
  sources; Match Keys / Feature Scores need multi-record entities). Do **not** produce separate
  static pages, and do **not** add redundant tabs — the entity-size distribution is Merge
  Statistics and the cross-source entity-relationship view is Entity Graph.
- Keep all generated code and output inside the working directory (`src/server/` for code, HTML →
  `docs/visualizations/`, other output → `docs/` or `data/`; never `/tmp/`); pull
  entity/relationship/report data through generated SDK code and `reporting_guide`, never direct
  SQL.
- Render offline with the vendored D3 asset inlined, no CDN (INV-091), and take palette/typography
  from `scripts/brand_tokens.py` (INV-081).
- Write a self-contained standalone HTML snapshot under `docs/visualizations/` (INV-070); after
  generating it, capture screenshots for the recap per
  `../bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots" (skip
  silently with no headless capability, otherwise embed the 2-3 best in this module's recap).
  `{name}` = `results_visualization`.

**Checkpoint:** write step 3c to `config/bootcamp_progress.json`, recording `m7_visualizations`
(offered/accepted and the artifact path, e.g. `{"offered": true, "accepted": true, "artifact":
"docs/visualizations/results_visualization.html"}`). The former per-visualization checkpoints
`m7_exploratory_queries` (entity graph) and `m7_findings_documented` (dashboard) are subsumed here.

## Next: Discover phase (step 4)

The Discover phase introduces advanced Senzing capabilities using concrete examples from the
bootcamper's loaded data. It is opt-in and **independent of the visualization decision above** —
ask it whether or not the bootcamper wanted additional visualizations. The bootcamper can decline
or exit early at any demonstration point.

- Load `phase2-discover.md` for steps 4a–4c (data pattern analysis, why analysis, how
  analysis).
- Then load `phase2b-discover.md` for step 4d (relationship networks) and Discover Phase
  Completion. (The former step 4e data-specific visualization suggestions are now tabs of the
  step-3c visualization app — Match Keys, Feature Scores, Cross-Source, and Relationship Network.)

Steps 4a–4d each checkpoint individually to `config/bootcamp_progress.json`. After the Discover
phase completes or is skipped, return here for the Query Completeness Gate.

## Success criteria

- ✅ Query programs created and tested.
- ✅ Visualization offered (the single interactive-visualization gate in step 3c was presented; the
  tabbed app — entity graph, relationship network, results dashboard, cross-source overlap, and
  match/feature analysis — was built when accepted).
- ✅ Discover phase completed or explicitly skipped.

## Query Completeness Gate

Before wrapping up the module, confirm:

1. **Query programs created and tested?** At least one query program runs successfully
   against the resolved data.
2. **Visualization offered?** The step-3c visualization gate was presented (the single
   interactive-visualization question, which covers the entity graph and results dashboard as tabs)
   — this counts as offered whether the bootcamper accepted or declined it.
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

*(Internal: end the turn on this question and wait; keep this offer's wording identical to
`../bootcamp-onboarding/module-completion.md` → "Reaching graduation".)* On module completion, set
`current_step` to `null` per the ground rules.

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
