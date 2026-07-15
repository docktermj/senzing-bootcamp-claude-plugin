# Module 5, Phase 2: Data Mapping (steps 8–20)

Continues from Phase 1. Follow the ground rules; `🛑`/`⛔` are internal directives: do not
render them. Signal a stop by ending the turn on the single 👉 question and waiting.

**Iterative process:** Users can jump between steps. The goal is a working transformation
program, not strict sequence.

**Before starting:** Confirm which data source. Track multi-source progress (In Progress /
Complete / Pending).

**MCP-first invariant (this phase especially):** ALL JSON mappings and attribute names come
from the `mapping_workflow` MCP tool. NEVER hand-code or guess Senzing attribute names, and
never reuse mapping output from one source for another. Never guess SDK method signatures: use
`generate_scaffold` / `get_sdk_reference`.

## Skip fast-pathed sources

Before starting the mapping workflow for a source, check its registry entry in
`config/data_sources.yaml`. If `fast_pathed` is `true` and `mapping_status` is `complete`, skip
this source entirely: it has already been routed to Module 6. Proceed to the next unmapped
source.

## Mapping verbosity check (before starting the mapping workflow)

Read `config/bootcamp_preferences.yaml` and check the `mapping_verbosity` key.

- **If `mapping_verbosity` is `null` or absent:**

  👉 **Before we start mapping, which mode would you like? Reply with a number:**

  1. **Verbose mode** — I'll show each mapping step in detail: field detection, attribute selection rationale, transformation preview.
  2. **Concise mode** — I'll map quickly and show only the final mapped record and any warnings.

  *(Internal: end the turn on this question and wait.)* Persist their choice (`verbose` or
  `concise`) to `mapping_verbosity` in `config/bootcamp_preferences.yaml`.

  If the bootcamper skips or doesn't answer directly: default to `verbose`, persist it, and
  say: "Defaulting to verbose mode: say 'switch to concise' anytime if you want less detail."

- **If `mapping_verbosity` is already set to `verbose` or `concise`:** Say "Using your
  [verbose/concise] mapping preference from last time: say 'switch to [other]' if you'd prefer
  [less detail/more detail]" and proceed without waiting.

## Mid-mapping verbosity switch

If the bootcamper says "switch to verbose", "switch to concise", "more detail", "less detail",
or any natural variant indicating they want to change mapping verbosity:

1. Update `mapping_verbosity` in `config/bootcamp_preferences.yaml` to the requested mode.
2. Apply the new mode immediately to all subsequent presentation output.
3. Confirm briefly: "Switched to [verbose/concise] mode.": then continue without interruption.

## Mapping state checkpointing (applies to every step below)

`mapping_workflow` is stateful. Each call returns state that MUST be passed, unchanged, to the
next `mapping_workflow` call for that source: never alter or reconstruct it. After each step,
write a checkpoint to `config/mapping_state_[datasource].json`:

```json
{"data_source":"CUSTOMERS","source_file":"data/raw/customers.csv","current_step":3,"completed_steps":["profile","plan","map"],"decisions":{"entity_type":"PERSON","field_mappings":{"full_name":"NAME_FULL"}},"last_updated":"2026-04-14T10:30:00Z"}
```

On session resume: read the checkpoint, show the user where they left off, restart
`mapping_workflow`, fast-track through decided steps, and resume from the first incomplete step.
**Delete the checkpoint when mapping for that source is complete.**

## File placement during the workflow

`mapping_workflow` downloads workflow resources and later produces output into a workspace
directory. Override any MCP-suggested `/tmp/` paths to project-local paths. Place files per the
ground-rules file-placement contract:

- Reusable resources at download time: transformation/workflow `.py` scripts → `src/`; the
  entity specification (`senzing_entity_specification.md`) → `docs/reference/`; other reference
  `.md` → `docs/`; config JSON → `config/`; data → `data/`.
- **Transient run artifacts stay in the workspace while the run is in progress**: the workflow
  reads and writes them for its own use. Do NOT relocate, delete, or redirect these mid-run:
  `profile_report.md`, `schema_hints.md`, `JOURNAL.md`, and generated JSONL output.
- **After the run for a source completes (after the iterate/finalize step), relocate the
  transient artifacts to their durable homes:** mapping-phase Markdown (`profile_report.md`,
  `schema_hints.md`, `JOURNAL.md`) → `docs/mapping/`; mapping working data
  (`*_mapping_spec.json`, the per-source `{source}_sample.jsonl`, intermediate analyzer JSONL)
  → `data/mapping/`. Final transformed, load-ready JSONL stays in `data/transformed/`.
- If a downloaded file matches no placement rule, leave it in the workspace and surface it as a
  warning rather than inventing a destination. If the plugin write-gate blocks a write, leave
  the file in the workspace and report it: do not retry against a different location.

The plugin's PreToolUse write-gate enforces the temp-path and secret rules; file-type placement
is your responsibility. (The Kiro `organize_mapping_files.py` and `generate_docs_index.py`
scripts are a later porting phase: place files directly per the contract above for now.)

## Workflow (per data source)

### 8. Start

Call `mapping_workflow(action='start')` with the source file from `data/raw/` or
`data/samples/`. Override any `/tmp/` paths to project-local. Tell the user: "Starting mapping
for [source]. I'll walk through each step and explain what I find."

> **Data source registry:** Update the source's `mapping_status` to `in_progress` in
> `config/data_sources.yaml` and set `updated_at`.

> **Per-source mapping requirement:** Each data source **must** complete its own full
> `mapping_workflow` run from start to finish. Do NOT reuse the mapping output, field mappings,
> or mapping specification from one source for another: even if the schemas appear similar.
> Every source gets its own independent `mapping_workflow` execution and its own mapping
> specification markdown (`docs/mapping/{source_name}_mapper.md`). Mapper code may be shared
> across sources if schemas are identical, but mapping documentation is always per-source.

After `mapping_workflow(action='start')` finishes downloading its workflow resources, and
before any further mapping work (profiling, planning, mapping), place the just-downloaded
reusable resources at their policy-correct locations per the file-placement guidance above.

**Checkpoint:** write step 8 to `config/bootcamp_progress.json`.

### 9. Profile

Run the profiler, then summarize columns/types/completeness/quality. Advance with
`action='profile_summary'`.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Present a full column table with types, sample values, completeness %, and
>   what each means for mapping (maps to Senzing / will skip / needs attention). Explain the
>   key takeaway.
> - **Concise:** Present one summary line: N columns detected, X% overall completeness, and key
>   issues only (e.g., "12 columns, 94% complete, 2 fields need attention").

**Checkpoint:** write step 9.

### 10. Plan

Identify entity type (person/org/both), structure (flat/nested), relationships. Advance with
`action='entity_plan'`. Tell the user: explain the entity type decision, which fields map vs.
skip and why.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Explain the entity type decision and rationale. For each field, state whether
>   it maps or is skipped and why (e.g., "phone maps to PHONE_NUMBER: standard contact
>   attribute" / "internal_id skipped: no Senzing attribute match, not useful for
>   resolution").
> - **Concise:** State the entity type and a count of mapped vs. skipped fields without
>   per-field rationale (e.g., "Entity type: Person. 8 fields mapped, 3 skipped.").

**Checkpoint:** write step 10.

### 11. Map

Map fields to Senzing attributes via `mapping_workflow(action='schema_mappings')`. NEVER guess
attribute names. For non-Latin data: `search_docs(query="globalization")`. Tell the user: show
the mapping table with reasoning for each decision and a confidence score.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show the full mapping table with a rationale column explaining each mapping
>   decision and a confidence score per field (e.g., "first_name → NAME_FIRST: standard given
>   name field, confidence: high").
> - **Concise:** Show the mapping table with source field → Senzing attribute only, no
>   rationale column or confidence scores (e.g., "first_name → NAME_FIRST").

> **Availability-aware mapping validation:** `mapping_workflow` advertises three validation
> scripts. Run them by availability: do NOT treat any one as a hard blocking gate.
>
> 1. **`sz_json_analyzer.py` (primary validation):** structural + Entity-Specification
>    validation, currently hosted (HTTP 200). When available, run it and use its result as the
>    authoritative check. It is **sufficient to proceed**: when the verbatim/routing scripts
>    below are unavailable, a passing `sz_json_analyzer.py` result lets you continue.
> 2. **`sz_verbatim_check.py` (verbatim-fidelity, optional/best-effort):** if available, run it
>    and report the result; if unavailable (HTTP 404 / no working inline fallback), tell the
>    bootcamper it is being skipped because the script is unavailable, treat it as
>    optional/best-effort, and proceed: do NOT block on it.
> 3. **`sz_routing_report.py` (routing-coverage, optional/best-effort):** same handling as the
>    verbatim check.
>
> In short: anchor validation on `sz_json_analyzer.py`; degrade the verbatim and routing checks
> to optional/best-effort when their scripts are unavailable, and never leave the bootcamper
> blocked at this step because of a 404.

> **Step 5 `detect_environment` menu handling (after this step's approval):** After a source's
> mapping is approved, `mapping_workflow` returns its Step 5 (`detect_environment`) with a
> four-option menu. Do NOT stop here: explain the menu and relay a recommendation so the
> bootcamper never hits a dead end.
>
> **`mapping_workflow` Steps 5–8 are optional sandbox validation** (Phase 3). They let you
> trial-load the mapped source into a throwaway sandbox to preview entity resolution. They are
> NOT the production load: the real load happens in **Module 6**. The four options are:
>
> - **skip**: skip the per-source sandbox test load and move on. **Recommended when one or
>   more unmapped sources remain.**
> - **test_load**: run the optional sandbox test load (enters Phase 3) for this source.
> - **load+resolve**: run the optional sandbox test load and resolve entities (enters Phase 3)
>   for this source.
> - **done**: finish the mapping workflow for this source without a sandbox test load.
>
> **Multi-source continuation (recommended path):** When one or more unmapped sources remain,
> recommend **skip**: the real load is deferred to Module 6, so a per-source sandbox test load
> adds little here: and automatically continue to the next unmapped source by starting its own
> `mapping_workflow` run. Tell the bootcamper: "Steps 5–8 are an optional sandbox preview; since
> you still have sources to map and the real load happens in Module 6, I'll skip the per-source
> test load and move on to the next unmapped source."
>
> **Explicit choice is preserved:** If the bootcamper explicitly chooses **test_load** or
> **load+resolve**, follow that path into Phase 3 (`phase3-test-load.md`) unchanged. The real
> production load still happens in Module 6 regardless.

**Checkpoint:** write step 11.

### 12. Generate starter code

Advance with `action='paths'`. Tell the user: show a sample target JSON record so they see the
output format.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show a sample target JSON record with annotations explaining the structure
>   (which fields became which Senzing attributes, how DATA_SOURCE and RECORD_ID are set, nested
>   vs. flat layout).
> - **Concise:** State the output file path and format only (e.g., "Output:
>   data/transformed/customers.jsonl: one JSON record per line").

After `mapping_workflow` generates output files into the workspace, place them into the correct
project subdirectories per the file-placement guidance above (`.py` → `src/`, transformed JSONL
→ `data/transformed/`, mapping docs → `docs/mapping/`, etc.). Regenerating a `docs/README.md`
docs index is a later porting phase: skip it for now.

**Checkpoint:** write step 12.

### 13. Build the transformation program

Use `generate_scaffold` or the mapping workflow output as the foundation. Handle: input
reading, field mapping, type conversion, cleansing, `DATA_SOURCE`/`RECORD_ID`, and error
handling. Save to `src/transform/transform_[name].[ext]`. Tell the user: the file path, what it
reads/writes, and what it handles.

**Checkpoint:** write step 13.

### 14. Test

Run on 10-100 records from `data/samples/`. Validate with `analyze_record`. Tell the user:
pass/fail, output file path, sample record, any observations.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show pass/fail result, the output file path, a sample transformed record, and
>   any observations (warnings, skipped records, format issues).
> - **Concise:** Show pass/fail result and the output file path only (e.g., "✅ Pass: output:
>   data/transformed/customers_sample.jsonl").

**Checkpoint:** write step 14.

### 15. Quality analysis

Run on 1000+ records. Evaluate feature distribution, coverage, quality scores. Advance with
`action='verdict'`. Tell the user: overall score, per-feature coverage with what it means for
matching, any issues found.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show the overall quality score, per-feature coverage breakdown with matching
>   implications (e.g., "NAME coverage 98%: strong for matching" / "ADDR coverage 42%: may
>   reduce match accuracy"), and all issues found with explanations.
> - **Concise:** Show the overall quality score, a count of mapped vs. unmapped fields, and
>   warnings only (e.g., "Quality: 85/100. 8 mapped, 3 unmapped. ⚠️ Low address coverage may
>   affect matching.").

**Offer visualization:** "Would you like me to create a web page showing the quality analysis?
It'll have coverage charts and the field mapping summary." If yes, generate a self-contained
HTML page and save it to `docs/mapping/mapping_[name]_quality.html`.

**Checkpoint:** write step 15.

### 16. Review

Confirm with the user: output format correct, quality acceptable, ready for production or needs
adjustment.

**Iterate vs. proceed decision gate:** After presenting quality results, guide the decision and
close the turn on one 👉 question:

- **Quality ≥80% and all critical fields mapped:** "Quality looks strong. Ready to proceed to
  loading (Module 6)."
- **Quality 70-79%:**

  👉 **Quality is acceptable. What would you like to do? Reply with a number:**

  1. Proceed to loading now.
  2. Iterate to improve [specific weak areas] first.

- **Quality <70%:**

  👉 **Quality needs improvement before loading will produce meaningful results. I'd recommend going back to address [specific issues]. What would you like to do? Reply with a number:**

  1. Iterate to improve the data.
  2. Proceed anyway, knowing results may be limited.

*(Internal: end the turn on the applicable question and wait.)*

**Checkpoint:** write step 16.

### 17. Iterate

If issues are found, go back to the relevant step. Retest after changes.

> **Data source registry:** Update the source's `mapping_status` to `complete` in
> `config/data_sources.yaml` and set `updated_at`. If a transformed file was created, update
> `file_path` to the `data/transformed/` output.

**Checkpoint:** write step 17.

### 18. Save and document

- Program in `src/transform/`.
- Docs in `docs/mapping/mapping_[name].md` (field mappings, logic, quality, how to run).
- Sample output in `data/transformed/[name]_sample.jsonl`.
- **Transformation lineage:** Create `docs/mapping/transformation_lineage_[name].md` for this
  data source, covering source file info, transformation program, output file info, field
  mappings, format changes, filters, quality improvements, and before/after record counts. (The
  Kiro `templates/transformation_lineage.md` template is a later porting phase; compose the
  lineage document directly for now.)
- **Entity specification reference:** The Senzing entity specification reference lives only at
  `docs/reference/senzing_entity_specification.md`: a single canonical copy. Do NOT create a
  copy in the `docs/` root; if one exists there, remove it.
- **Per-source mapping specification:** Save a mapping specification markdown to
  `docs/mapping/{source_name}_mapper.md` for this data source. This file is always per-source,
  even when the transformation program is shared. Use this structure:

  ```markdown
  # Mapping Specification: {SOURCE_NAME}

  **Source file:** data/raw/{source_file}
  **Data source name:** {DATA_SOURCE}
  **Entity type:** Person / Organization / Both
  **Generated by:** mapping_workflow

  ## Field Mappings

  | Source Field | Senzing Attribute | Transformation | Notes |
  |---|---|---|---|
  | ... | ... | ... | ... |

  ## Mapping Decisions

  - [Key decisions made during mapping]

  ## Quality Notes

  - [Quality observations specific to this source]
  ```

**Checkpoint:** write step 18.

### 19. Repeat for remaining data sources

Each source gets its own transformation program and its own `mapping_workflow` run.

> **Mandatory internal gate (do not render to the bootcamper):** BEFORE writing the module
> completion checkpoint, list ALL files in `data/transformed/` and verify that EACH has a
> corresponding `docs/mapping/{source_name}_mapper.md`. If any are missing, create them NOW. Do
> NOT write the module completion checkpoint until all mapping specs exist. This is a hard
> requirement: the module is not complete without a per-source mapping specification for every
> transformed data source.

**Per-source completion checkpoint:** Before marking a source as complete, verify that
`docs/mapping/{source_name}_mapper.md` exists for that source. Do not proceed to the next source
or mark the current source done until its mapping specification markdown is saved. When all
sources are mapped, confirm every completed source has its own file. When a source's mapping is
complete, delete its `config/mapping_state_[datasource].json` checkpoint.

**Checkpoint:** write step 19.

### 20. Transition

Once all sources are mapped, choose the next module by whether the Senzing SDK is already set up
: check `config/bootcamp_progress.json` for Module 2 completion before deciding:

- **If Module 2 (SDK Setup) is already complete** (e.g., the bootcamper ran the optional Module
  3 System Verification, which requires a working SDK, or the SDK was installed during
  onboarding): skip Module 2 and transition directly to **Module 6 (Data Processing)** to load
  the mapped data.
- **If Module 2 is not yet complete:** transition to **Module 2 (SDK Setup)**: it is the next
  module that needs the SDK, and loading in Module 6 depends on it.

Close the turn on the transition question, for example:

👉 **Module 5 complete. Ready to move on to [Module 2 (SDK Setup) / Module 6 (Data Processing)]?**

*(Internal: end the turn on this question and wait.)*

**Checkpoint:** write step 20.
