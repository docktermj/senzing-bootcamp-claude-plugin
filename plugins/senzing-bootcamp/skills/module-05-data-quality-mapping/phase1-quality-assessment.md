# Module 5, Phase 1: Quality Assessment (steps 1–7)

Verify data sources against the Entity Specification. Follow the ground rules. `🛑`/`⛔` are
internal directives: do not render them; signal a stop by ending the turn on the single 👉
question and waiting.

## 1. List the agreed-upon data sources

Recap the data sources identified during the business problem discussion. Review
`docs/business_problem.md` for the list.

**Checkpoint:** write step 1 to `config/bootcamp_progress.json`.

## 2. Request sample data

For each data source, ask the user to place sample files in `data/raw/` or `data/samples/`:

- CSV files (first 10-20 rows)
- JSON samples
- Database schema with sample values
- Screenshots of data tables
- Text descriptions of fields and data types

**Checkpoint:** write step 2.

## 3. Understand the Senzing Generic Entity Specification

Call `download_resource(filename="senzing_entity_specification.md")` to retrieve the current
Senzing Generic Entity Specification. Use this as the authoritative reference for all attribute
names, types, and structures in this step and every subsequent step. Save the downloaded
specification to the single canonical copy at `docs/reference/senzing_entity_specification.md`
(do not create duplicate copies elsewhere).

**Checkpoint:** write step 3.

## 4. Compare each data source with the Entity Specification

Using the Entity Specification retrieved in Step 3 as the reference, compare each data source's
fields against the specification's attribute names. For each data source provided:

- Identify which fields map directly to attributes defined in the Entity Specification.
- Identify fields that need transformation (e.g., combining or splitting fields to match the
  specification's expected structure).
- Identify fields with non-standard names that correspond to attributes in the Entity
  Specification.
- Note any missing critical fields defined in the Entity Specification.
- Check if `DATA_SOURCE` and `RECORD_ID` are present or can be derived.

**Checkpoint:** write step 4.

## 5. Categorize each data source

(Using the Entity Specification retrieved in Step 3 as the source of truth for what constitutes
compliant attribute names.)

- **Entity Specification-compliant:** Data already uses attribute names and structures that
  match the Entity Specification. CORD sources (the already-Senzing-ready fast-path class) are
  eligible for the fast-path (Step 5a, offered only for `provenance: cord`) — route directly to
  Module 6 (loading), skipping mapping. Other compliant sources, including non-CORD data that
  looks Senzing-ready, continue to Phase 2, which confirms compliance and records lineage before
  loading.
- **Needs mapping:** Data uses different field names or structures than those defined in the
  Entity Specification. Continue to Phase 2 (data mapping).
- **Needs enrichment:** Data is missing critical attributes. Discuss with the user whether
  additional data sources can provide the missing information.

**Checkpoint:** write step 5.

## 5a. Senzing-readiness check and fast-path offer (CORD sources only)

For each source where `provenance` is `cord` in `config/data_sources.yaml` (that is, a source
obtained via the `get_sample_data` MCP tool in Module 4):

1. **Obtain the Senzing schema definition:** Reuse the Senzing Generic Entity Specification
   already retrieved in Step 3: do not download it again. From that same MCP-sourced
   specification, extract the list of required top-level structural indicators for a
   Senzing-loadable record (e.g., presence of a FEATURES array, DATA_SOURCE, RECORD_ID).

   ⛔ **Loadable is a wider test than "has a FEATURES array".** The same specification states that
   the older shape — "a flat JSON structure with a separate sub-list for each feature that had
   multiple values" — is **still supported**. Treat **both** forms as Senzing-ready:

   - the recommended **`FEATURES` array**; or
   - the legacy **flat structure**: feature attributes at the record root
     (`BUSINESS_NAME_ORG`, `RECORD_TYPE`, …), with a per-feature root sub-list (`NAMES`,
     `ADDRESSES`, `IDENTIFIERS`) wherever a feature repeats. A source with no repeating feature is
     in this shape with no sub-list at all — flat root attributes only.

   **CORD ships both, so neither may be assumed.** Verified against the MCP server this session:
   London/`GLOBALDATA` returns a `FEATURES` array, while Las Vegas/`PPP_LOANS` returns flat root
   attributes. Requiring `FEATURES` alone classifies the legacy-shaped sources as not-ready and
   sends data that already loads and resolves through a mapping phase it does not need. Sample the
   actual records rather than assuming a dataset's shape, and confirm the still-supported statement
   from the specification you retrieved (INV-080), not from this file.

2. **Perform the readiness check:** Examine up to 100 sample records from the source file. For
   each record, verify:
   - The record is valid JSON.
   - The record contains the structural indicators identified from the Entity Specification
     (top-level keys, array structures).
   - DATA_SOURCE and RECORD_ID are present or derivable.

   If ALL sampled records pass, classify as Senzing-ready. If ANY sampled record fails,
   classify as not Senzing-ready. (The Kiro `check_cord_readiness.py` helper is a later porting
   phase; perform the check directly against the sampled records for now.)

   **A stronger check, when the engine is available: ask Senzing how it reads the record.** The
   structural test above confirms the *shape*; it cannot tell you whether an attribute name will
   actually participate in matching. `getRecordPreview` returns Senzing's own interpretation of a
   record **without loading it**, which answers that directly — and it beats reading field names
   against the specification by eye. Obtain the call for the bootcamper's binding from MCP
   (`get_sdk_reference(topic='parameters', filter='getRecordPreview')`; the method name and argument
   types differ per binding — INV-132) rather than writing it from memory.

   ⛔ **Preview requires the record's `DATA_SOURCE` code to be registered first, even though it
   writes nothing.** This is counter-intuitive and it is why the check fails where it is most natural
   to run: registration belongs to the loading phase, so a readiness check reaching for preview
   before registration gets

   ```text
   SENZ2207|Data source code [<CODE>] does not exist
   ```

   The prerequisite is **not** documented on the method — verified 2026-07-30 on MCP server 1.32.2,
   `get_sdk_reference(topic='parameters', filter='getRecordPreview')` returns one signature per
   binding — `get_record_preview(record_definition, flags)` in Python — with no mention of it.
   (The same call also returns `get_record`, which the filter matches too; that is a second
   *method*, not a second overload.) So the order is: register the source code(s) — taking the
   registration code from `sdk_guide(topic='configure')`, never hand-written (INV-080) — then preview.
   Registration is idempotent and the loading phase needs it anyway, so doing it here costs nothing.

   On `SENZ2207`, call `explain_error_code('SENZ2207')` first as always (INV-080): unlike some codes,
   its own resolution steps *do* name the fix — register the code, confirm the registered list, mind
   that codes are case-sensitive and conventionally UPPERCASE, and reinitialize afterwards — so do not
   restate them here, just follow them.

   **Optional and non-blocking.** If the engine is not available, or registration has not happened
   and you would rather not do it at this point, skip the preview and keep the structural check
   (INV-048). Say which check ran, so "Senzing-ready" never implies a stronger test than was
   performed. The prerequisite applies wherever a preview-based check is used, not only to the CORD
   sources this step covers.

3. **Record the result:** Set the source's `senzing_ready` field in `config/data_sources.yaml`
   to `true` or `false` and update `updated_at`.

4. **If Senzing-ready: present the fast-path offer:**

   👉 **Your CORD source [SOURCE_NAME] is already in Senzing-loadable form (it has the correct JSON structure with DATA_SOURCE, RECORD_ID, and properly structured features). Would you like to skip the mapping phase and proceed directly to loading in the Data processing module?**

   *(The wording holds for both supported shapes — "properly structured features" covers a
   `FEATURES` array and the still-supported per-feature sub-lists alike.)*

   *(Internal: end the turn on this question and wait.)*

   - **If confirmed:** Set `mapping_status: complete` and `fast_pathed: true` in the registry.
     Keep `file_path` pointing at the original `data/raw/` file. Record a data-lineage entry
     (see below). Route the source to Module 6.
   - **If declined:** Continue through the normal quality assessment and mapping workflow for
     this source.

5. **If NOT Senzing-ready or MCP unavailable:** Continue through the normal quality assessment
   and mapping workflow. Do NOT present the fast-path offer.

6. **Non-CORD sources:** Skip this step entirely. Never present the fast-path offer for sources
   with provenance other than `cord`.

**Fast-path data-lineage entry:** Record a lineage entry ONLY for a source that was explicitly
fast-pathed (the bootcamper confirmed the offer above). Never record one for a source that went
through normal mapping or that was never offered the fast-path. Add the entry to the
`transformations` section of `docs/mapping/data_lineage.yaml`, keyed by the source's
DATA_SOURCE name. Because no transformation occurred, the entry records the original `data/raw/`
file as both input and output with equal record counts:

```yaml
transformations:
  CORD_LAS_VEGAS:
    source_file: data/raw/cord-las-vegas.jsonl
    transformation_script: null  # No transformation: fast-pathed
    output_file: data/raw/cord-las-vegas.jsonl  # Same file
    records_in: 8421
    records_out: 8421
    records_rejected: 0
    quality_score: null  # Quality assessment skipped
    fast_pathed: true
    fast_path_reason: "CORD source already in Senzing-loadable form"
```

**Invariants:** every fast-path lineage entry MUST satisfy: `source_file == output_file` (the
original `data/raw/` file, unchanged); `records_in == records_out`; `records_rejected: 0`;
`transformation_script: null`; `fast_pathed: true`.

**Non-blocking:** If writing the data-lineage entry fails, allow the fast-path to proceed
anyway: route the source to Module 6 and log the lineage failure so it can be retried later. A
lineage write failure MUST NOT block the fast-path.

**Checkpoint:** write step 5a.

## 6. Assess data quality and apply thresholds

For each data source, compute a quality score based on field completeness, format consistency,
and duplicate rate.

⛔ **Define "present" this way — do not re-invent it.** Completeness feeds the score that gates this
module, so the presence test is part of the measurement, not an implementation detail. A field value
is **present** unless it is:

- absent — the key is missing from the record — or `null`;
- an empty or whitespace-only string;
- an empty container (a list, dict, set or tuple of length 0);
- a container whose every element is itself empty by these rules (e.g. `[""]`, `[{}]`, `[null]`).

Everything else is present. Two consequences to get right:

- **`false`, `0` and `0.0` count as PRESENT.** They are values, not absences. A truthiness test
  (`if value:`) is wrong: it silently reports real data as missing.
- **Presence is a property of the VALUE, never of the key.** Testing "does the record have this
  field?" reports 100% coverage for a field that is an empty array in every record — which is
  exactly how one bootcamp reported `IDENTIFIER_LIST` coverage as **100%** when the true figure was
  **0%**, on the field family that supplies exclusive identifiers, feeding the number straight into
  the mapping decision.

⛔ **Sanity-check any 0% or 100% figure before it routes the gate.** A field family reporting
*exactly* full or *exactly* zero coverage across every record is the signature of a presence test
measuring the wrong thing. Print one sample value for that field and confirm the figure against it
before reporting. Treat a suspiciously uniform result as a probable measurement failure first and a
real finding second — the same discipline INV-115 applies to blank parsed SDK fields, applied here to
profiling.

⛔ **Measure completeness PER RECORD against the features that apply to that record's
`RECORD_TYPE` — never as one average per feature across the whole source.** A feature that does not
apply to a record is not missing data, and averaging it in penalizes the source for data that could
not exist.

This is not a corner case. Mixed person/organization sources are the norm in KYC, AML, sanctions
screening, vendor MDM and beneficial-ownership work — several of this bootcamp's headline use cases.
One sanctions list with **NAME and ADDRESS on 100% of records** scored **52% completeness / 69%
overall** — squarely in "recommend fixing before mapping" below — because person-oriented features
(DOB at 32%, and others like passport and gender) were averaged across a source where **71 of 110
records are ORGANIZATIONS**. Rescoring each record against the features applicable to its own type
gave **97%**. Trusting the first figure would have sent the bootcamper to remediate data with nothing
wrong with it.

**Derive applicability from the Entity Specification, not from a list in this file.** The
specification states the type in its own wording, so `search_docs(query='what features to map',
category='data_mapping')` answers it directly — read the feature's description and section heading:

| What the specification says | Applies to |
|---|---|
| `DOB` — "**Person** date of birth" | PERSON |
| `NATIONALITY` / `CITIZENSHIP` / `PLACE_OF_BIRTH` — "**Person** …" | PERSON |
| `NAME` (person) — "Personal names… `NAME_FIRST`, `NAME_LAST`" | PERSON |
| `REGISTRATION_DATE` / `REGISTRATION_COUNTRY` — section heading "**(organizations)**" | ORGANIZATION |
| `NAME` (organization) — "Organization legal or trade name… `NAME_ORG`" | ORGANIZATION |
| `ADDRESS`, `PHONE`, `EMAIL`, identifiers | either — do not exclude these |

(Verified against MCP server 1.32.2, 2026-07-30. Re-read it for the source you are assessing rather
than trusting this table — it is an illustration of *how the specification marks type*, not a
substitute for asking, and it is deliberately partial: features not listed here still have to be
checked the same way, INV-080.)

**Records with no `RECORD_TYPE`.** The specification calls `RECORD_TYPE` *"Recommended"*, not
required, and says to leave it blank when the type is unknown — so a record may legitimately have
none. Score those against the features that apply to **any** type, and **report how many records were
scored that way**. A source where most records carry no `RECORD_TYPE` is itself a finding worth
raising (it also forgoes the cross-type resolution protection the specification says `RECORD_TYPE`
provides), and it must not be hidden inside an aggregate.

⛔ **Extend the uniformity sanity-check above with this case: a low completeness score on a source
whose NAME and ADDRESS coverage is high is a probable applicability error, not a data problem.**
Check the record-type mix before reporting the score or routing anyone to remediation. The presence
rules above are unchanged — they decide whether a *value* is there; this decides whether the feature
belonged in the denominator at all.

Use these thresholds to guide the decision:

- **≥80% quality score** → Proceed to Phase 2 (mapping). Data quality is strong enough for
  meaningful entity resolution.
- **70-79% quality score** → Warn the user. Quality gaps exist: suggest specific fixes (fill
  nulls, standardize formats, deduplicate within source). Proceed to Phase 2 if the user
  accepts the risk, but document the quality gaps.
- **<70% quality score** → Strongly recommend fixing data quality before mapping. Entity
  resolution results will be poor. Help the user identify the biggest quality issues and create
  a remediation plan. Only proceed if the user explicitly chooses to continue.

**What this score does not measure.** It scores completeness, format consistency, and duplicate
rate — all *structural* properties of one source in isolation. It says nothing about whether a
field will be mapped to a feature that **means** the same thing, and nothing about how two sources
will interact once resolved. A source can score 86% and still carry a mapping that suppresses
legitimate merges. Present the number as "the data is clean enough to map", never as "the mapping
will be correct" — semantic correctness is only established after loading, by the match-key audit
in Data processing.

**If the field list itself looks implausible, this score is not yet meaningful.** The dynamic-key
sanity check (>~100 fields or >50 distinct field patterns — INV-118) runs on the `mapping_workflow`
profile in Phase 2 step 9, *after* this step, so on the first pass you will not have its verdict
here. Two consequences:

- **Now:** if the field list you compared against the Entity Specification in step 4 already looks
  implausibly wide, say so, treat this score as provisional, and expect step 9 to confirm it.
- **On return from Phase 2 step 9:** when that check trips, re-run this step after pre-processing
  and re-profiling rather than keeping the first score — a score averaged over hundreds of phantom
  fields is not meaningful, and it is this score that routes the gate below.

Present the assessment clearly:

```text
Data Quality Assessment:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: CUSTOMERS_CRM
  Field completeness:  82%  (name: 99%, phone: 75%, email: 68%)
  Format consistency:  90%
  Duplicate rate:       3%
  Overall quality:     78%  ⚠ Acceptable — some gaps (see below)

Source: VENDORS_LEGACY
  Field completeness:  45%  (name: 90%, phone: 20%, email: 15%)
  Format consistency:  55%
  Duplicate rate:      12%
  Overall quality:     42%  ⚠ Recommend fixing before mapping
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

⛔ **The status label MUST match the band above** — `✅` only at ≥80%, `⚠ Acceptable — some gaps`
at 70-79%, `⚠ Recommend fixing before mapping` below 70%. Derive the label from the computed score
rather than copying one from this example; a `✅` beside a 78% tells the bootcamper the gate said
"proceed" when it is about to ask them to choose.

> **Data source registry:** After computing the quality score, update the source's
> `quality_score` field in `config/data_sources.yaml` and set `updated_at`. If the score is
> below 70, add an `issues` list entry describing the quality concern.

**Checkpoint:** write step 6.

**Visualization checkpoint:** Offer a visual of the quality assessment (coverage bars per
source, per-field completeness). Pin the offer verbatim:

> 👉 **Would you like a visual of the quality assessment (coverage bars and per-field completeness)?**

If the bootcamper accepts, generate a self-contained HTML page and save it to
`docs/visualizations/` (INV-070). (The full Visualization Protocol / `visualization-guide` is a later
porting phase; offer directly for now.)

⛔ **This page is a bootcamper-facing visual deliverable, so the four rules below bind it** — it is
saved, kept, and shareable, exactly like the Truth Set app's snapshot. See
`../bootcamp-onboarding/ground-rules.md` → "Visual deliverables (Senzing brand)" for the first two
and `../module-03b-truthset-visualization/visualization-api-reference.md` → "Rendering contract" for
the third; both are the statements of record, so read them rather than reconstructing the rules here.

1. **Brand tokens, not an ad hoc palette** (INV-081): take colours and typography from
   `${CLAUDE_PLUGIN_ROOT}/scripts/brand_tokens.py`, degrading gracefully if the module cannot be
   imported.
2. **Renders offline** (INV-081/INV-091): **no CDN, no web font, no remote script.** If you need a
   charting library, inline the vendored `${CLAUDE_PLUGIN_ROOT}/scripts/vendor/d3.v7.min.js`; plain
   HTML/CSS bars need no library at all and are the better default here. A `<script src="https://…">`
   makes the page render blank on an air-gapped workstation — which Senzing evaluations frequently
   are — with no error anywhere.
3. **Escape every value that came from the data** (INV-106): field names, sample values and source
   names are the bootcamper's own strings. Escape them for the context they land in — HTML text,
   attribute, and, if you embed a JSON payload in an inline `<script>`, `<`, `>` and `&` as their
   `\uXXXX` escapes, since a value containing `</script>` otherwise breaks out of the script block in
   an artifact that gets kept and shared.
4. **Verify the rendered page, not the exit status** (INV-129): open it and confirm the bars and the
   per-field numbers actually drew. Best-effort and non-blocking, like every check in this module.

## 7. Summarize findings and save the evaluation report

Create `docs/data_source_evaluation.md`:

```markdown
# Data Source Evaluation Report

**Date:** [Current date]
**Project:** [Project name]

## Summary
- Total data sources: [count]
- Entity Specification-compliant: [count]
- Needs mapping: [count]
- Needs enrichment: [count]

## Data Source Details

### Data Source 1: [Name]
**Status:** [Entity Specification-compliant / Needs mapping / Needs enrichment]
**Location:** `data/raw/[filename]`
**Records:** ~[count]
**Fields:** [count] columns

**Evaluation:**
- [Field analysis]
- [Entity Specification compliance notes]

**Reason:** [Why it needs mapping or is compliant]

**Next step:** [Phase 2 (mapping) / Data processing (loading)]

### Data Source 2: [Name]
[Same structure]

## Mapping Priority
1. [Data source] - [Reason for priority]
2. [Data source] - [Reason for priority]
```

### Quality gate: iterate vs. proceed

After presenting the quality assessment, guide the user's decision. Ask exactly one 👉 question
to close the turn:

- **Quality ≥80%:** "Your data quality is strong. Let's continue to mapping."
- **Quality 70-79%:** "Your data quality is acceptable but has some gaps. You can continue to
  mapping now, or improve the weakest fields first."

  👉 **Your data quality is acceptable but has some gaps. What would you like to do? Reply with a number:**

  1. Improve the weakest fields first.
  2. Continue to mapping now.

- **Quality <70%:** "Your data quality needs attention before mapping will produce good
  results. I'd recommend focusing on [specific issues: e.g., filling missing phone numbers,
  standardizing address formats]."

  👉 **Your data quality needs attention before mapping will produce good results. What would you like to do? Reply with a number:**

  1. Work on improving the data first.
  2. Proceed anyway, knowing the results may be limited.

*(Internal: end the turn on the applicable question and wait.)*

**Success indicator:** ✅ All data sources categorized + `docs/data_source_evaluation.md`
created.

**Checkpoint:** write step 7.
