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

When step-3 validation rejects a payload, append the **verbatim** returned text to a
`validation_rejections` array on the same checkpoint, and record `mapper_source` once the mapper
exists (`mapping_workflow` or `entity_specification`, with the reason when it is the latter):

```json
{"data_source":"NOMINO-RISK","current_step":3,"validation_rejections":["<raw rejection text, unedited>"],"mapper_source":"entity_specification","mapper_source_reason":"step-3 validation rejected twice with a truncated error naming no field"}
```

Keep the rejection text unedited — truncating or summarising it destroys the only evidence the
upstream defect can be diagnosed from.

## File placement during the workflow

`mapping_workflow` downloads workflow resources and later produces output into a workspace
directory. Override any MCP-suggested `/tmp/` paths to project-local paths. Place files per the
ground-rules file-placement contract:

- Reusable resources at download time: transformation/workflow `.py` scripts → `src/`; the
  entity specification (`senzing_entity_specification.md`) → `docs/reference/`; other reference
  `.md` → `docs/`; config JSON → `config/`; data → `data/`.
- **Transient run artifacts stay in the workspace while the run is in progress:** the workflow
  reads and writes them for its own use. Do NOT relocate, delete, or redirect these mid-run:
  `profile_report.md`, `schema_hints.md`, `JOURNAL.md`, and generated JSONL output.
- **After the run for a source completes (after the iterate/finalize step), relocate the
  transient artifacts to their durable homes:** mapping-phase Markdown (`profile_report.md`,
  `schema_hints.md`, `JOURNAL.md`) → `docs/mapping/`; mapping working data
  (`*_mapping_spec.json`, the per-source `{source}_sample.jsonl`, intermediate analyzer JSONL)
  → `data/mapping/`. Final transformed, load-ready JSONL stays in `data/senzing-ready/`.
- If a downloaded file matches no placement rule, leave it in the workspace and surface it as a
  warning rather than inventing a destination. If the plugin write-gate blocks a write, leave
  the file in the workspace and report it: do not retry against a different location.

The plugin's PreToolUse write-gate enforces the temp-path and secret rules; file-type placement
is your responsibility. (The Kiro `organize_mapping_files.py` and `generate_docs_index.py`
scripts are a later porting phase: place files directly per the contract above for now.)

## Calling `mapping_workflow` correctly (⛔ read before step 8)

Verified against the live tool schema on 2026-07-26. Three details the workflow **cannot run
without** — each one was wrong or missing here before, and each fails at the first call rather than
degrading.

1. ⛔ **`start` requires BOTH `file_paths` and `data.workspace_dir`.** The tool's own contract:
   "The call WILL FAIL without both", and "do NOT assume `/tmp` exists". Pass the project-local
   mapping directory, which is where this bootcamp already keeps mapping working data (INV-050) —
   never `/tmp`, never a home-relative path:

   ```text
   mapping_workflow(action='start',
                    file_paths=['data/raw/<source>.csv'],
                    data={'workspace_dir': 'data/mapping'})
   ```

   This is the same rule as the file-placement contract above, expressed as a parameter: the
   workspace is where the tool writes its scripts, reference docs, mapper code and outputs, so
   pointing it at `data/mapping/` is what keeps those files inside the project.

2. ⛔ **There are exactly five actions: `start`, `advance`, `back`, `status`, `reset`.** Nothing
   else is valid. Every step below advances with **`action='advance'`**; the step's data goes in
   `data` (or the typed `payload`), and its field names are **not** action names. Five field names
   were previously written as actions here — `profile_summary`, `entity_plan`, `schema_mappings`,
   `paths`, `verdict` — which the server rejects.

3. **Echo the returned `state` verbatim on every call after `start`.** Each response carries an
   opaque `state` object; pass it back exactly, never reconstructed from memory or from this
   bootcamp's own checkpoint file. (The checkpoint above is for *bootcamper-facing resume*, not a
   substitute for the server's state.) If the state is lost, restart with `action='start'`.

**If a step's guidance arrives truncated mid-sentence, suspect the client read cap before the
server.** The tool embeds each step's advance schema verbatim in `instructions` and keeps any single
step under 64 KB, and its contract warns that a smaller read cap "silently TRUNCATES step guidance
mid-text and **reads as a server bug**." So a truncated step — including a step-3 rejection naming no
field — is a read-cap symptom first and an upstream defect second. Check that before invoking the
INV-125 fallback, and say which cause you concluded; INV-125 requires recording the raw failure, and
a documented cause is part of that record.

### This module's steps vs. the workflow's steps

The workflow has **8 steps: 4 core mapping steps (1–4) plus 4 optional sandbox steps (5–8)**. This
phase covers the four core steps across module steps 8-18, so **the two numbering schemes are not
the same** and only four `advance` calls happen in Phase 2:

| This module | Workflow step | Advances with |
|---|---|---|
| 8 Start | — | `action='start'` (see above) |
| 9 Profile | 1 profile_source_data | `action='advance'`, `data={'profile_summary': [...]}` |
| 10 Plan | 2 plan_entity_structure | `action='advance'`, `data={'master_schemas': [...], 'support_schemas': [...]}` |
| 11 Map | 3 map_fields | `action='advance'`, `data={'schema_mappings': [...]}` |
| 12-16 | 4 generate_validate | **one** `advance` at step 15, `data={'verdict': ...}` |
| 17-18 | — | no advance; `rework_*` verdicts route back |
| 18a | 5 detect_environment | the menu returned by step 15's advance; answering it may enter Phase 3 |
| Phase 3 (21-26) | 6-8 | the optional sandbox test load — see `phase3-test-load.md` |

Steps 12, 13, 14 and 16 do **not** advance the workflow — they are work performed *inside* workflow
step 4 (generate sample JSON, lint, write and run the mapper, analyze output) before its single
verdict advance. Workflow steps 5-8 are optional: step 15's `approve` returns the Step 5 menu, and
step 18a is where it is answered.

## Workflow (per data source)

### 8. Start

Call `mapping_workflow` with `action='start'`, `file_paths` naming the source file from
`data/raw/` or `data/samples/`, and `data={'workspace_dir': 'data/mapping'}` — **both parameters
are required and the call fails without either** (see the call contract above). Override any
`/tmp/` paths to project-local. Tell the user: "Starting mapping for [source]. I'll walk through
each step and explain what I find."

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

Run the profiler, then summarize columns/types/completeness/quality. Advance workflow step 1 with
`action='advance'`, carrying `profile_summary` (one entry per source schema, each with
`schema_name`, `record_count`, `field_count`) in `data`.

⛔ **Profile sanity check — interpret the field count, never just report it.** Before presenting
anything, check whether the profile is *plausible*: roughly **more than 100 fields, or more than 50
distinct field patterns**, is not a wide source — it is a signal that the source is shaped like a
document rather than a table. Report the likely cause instead of the raw number.

The usual cause is **dynamic keys — the source using data values as attribute names**, so each
record contributes new "fields" that are really values. When the count is implausible:

1. **Look for dynamic/unbounded keys:** many root keys appearing in only one or two records each,
   especially keys that are purely numeric or otherwise value-shaped. Report the count and a
   sample, not the full column table.
2. **Cross-check for redundancy:** check whether those key *names* also appear as **values**
   elsewhere in the same record (e.g. matching an ID field the record already carries). If they do,
   say so — that redundancy is precisely what makes dropping them lossless, and it is the
   difference between a safe pre-process and silent data loss.
3. **Recommend the sanctioned route explicitly:** pre-process to strip the dynamic keys, then
   **re-profile**. Name it as the expected next step; do not leave the bootcamper to infer that
   pre-processing is allowed.
4. **Require before/after proof:** show the removed data is redundant *before* dropping it, and
   that record counts and preserved features are unchanged *after*. Without that proof,
   pre-processing is silent data loss — worse than an unmappable profile.

This is a **finding, not a gate**: genuinely wide sources exist. Report, recommend, and let the
bootcamper decide — never block mapping on a field count.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Present a full column table with types, sample values, completeness %, and
>   what each means for mapping (maps to Senzing / will skip / needs attention). Explain the
>   key takeaway. **Exception — when the sanity check above fires, do NOT print the full table**
>   (a 1,373-row column table is noise precisely when the bootcamper most needs to understand
>   what happened): show the diagnosis, a sample of the offending keys, and the recommendation.
> - **Concise:** Present one summary line: N columns detected, X% overall completeness, and key
>   issues only (e.g., "12 columns, 94% complete, 2 fields need attention"). When the sanity check
>   fires, lead with the diagnosis rather than the count — "1,373 fields detected, which almost
>   certainly means dynamic keys rather than a genuinely wide source" beats a bare number.

**Checkpoint:** write step 9.

### 10. Plan

Identify entity type (person/org/both), structure (flat/nested), relationships. Advance workflow
step 2 with `action='advance'`, carrying `master_schemas` (at least one, each with `schema_name`,
`data_source` in UPPERCASE, `record_type`, `record_id_source`) and `support_schemas` (lookups,
relationships, children) in `data`. Tell the user: explain the entity type decision, which fields
map vs. skip and why.

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

Map fields to Senzing attributes, then advance workflow step 3 with `action='advance'`, carrying
`schema_mappings` in `data` (per schema, a `field_mappings` list whose entries each declare a
`disposition` — `feature`, `payload`, `ignore`, `derived`, or `extract`). NEVER guess
attribute names. For non-Latin data: `search_docs(query="globalization")`. Tell the user: show
the mapping table with reasoning for each decision and a confidence score.

⛔ **Shared-feature collision check (cross-source).** After mapping a source, compare its feature
targets against the sources already mapped. When **two or more sources send different source fields
to the same Senzing feature**, stop and confirm the two fields measure the *same quantity* — not
merely the same *kind* of thing. Ask one 👉 question naming both fields and the feature (its wording
is necessarily specific to the collision, so it is not a pinned question), and record the answer
with the mapping rationale.

This is the one check the validation scripts structurally **cannot** perform: they each see a single
source, and the defect only exists in the relationship between two. Watch **date** and **identifier**
features hardest, where near-miss semantics are the norm — "year established" vs. "incorporation
filing date" are both plausible `REGISTRATION_DATE` candidates and mean different things; `BID` vs.
`EFX_ID` are both identifiers and are not the same identifier. If they measure different things,
route one to payload instead of the shared feature. Getting this wrong does not produce an error —
it produces silently suppressed merges that only the post-load match-key audit will reveal.

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
>    authoritative check **for what it actually measures** — conformance to the *recommended*
>    schema, which is not the same question as "will this data load and resolve" (see the ⛔
>    conformance block below). It is **sufficient to proceed**: when the verbatim/routing scripts
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

⛔ **Separate structural invalidity from conformance-to-recommendation before acting on the
analyzer's output.** The analyzer's exit code alone is NOT the gate — its findings fall into two
kinds, and only one of them blocks:

- **Structural invalidity — blocking.** Malformed JSON, a missing `DATA_SOURCE`, an unparseable
  record. The data cannot load. Fix it before proceeding.
- **Conformance to the recommended schema — informational.** The record loads and resolves, but
  does not use the shape Senzing now recommends. Report it as a notice. It is **never** a reason
  to remap a source.

The observed instance of the second kind is the older **flat** format: feature attributes at the
record root, with a per-feature root sub-list (`NAMES`, `ADDRESSES`, `IDENTIFIERS`) wherever a
feature repeats. A source with no repeating feature is in this shape with no sub-list at all.
Against such a source the analyzer returns a non-zero exit with errors of the form:

```text
Line 1: Missing or non-array FEATURES
Line 1: Feature attribute 'RECORD_TYPE' must be inside FEATURES array
```

— hundreds per source, plus the warning `No NAME features found`.

**That data is supported.** The Senzing Entity Specification, § "Recommended JSON schema", says so
in as many words:

> "In prior versions we allowed a flat JSON structure with a separate sub-list for each feature
> that had multiple values. **While we still support that**, we now recommend the following JSON
> schema that has just one list for all features."

Re-confirm that statement from the MCP server this session rather than trusting this file
(`search_docs(category='data_mapping')`, or `download_resource(filename='senzing_entity_specification.md')`) —
INV-080 applies to this claim as much as to any attribute name.

**Do not assume a source's shape from its provenance.** CORD ships both forms: verified against the
MCP server, London/`GLOBALDATA` returns a `FEATURES` array while Las Vegas/`PPP_LOANS` returns flat
root attributes. Read the actual records.

⚠️ **Why the analyzer is not wrong, and still must not block.** The same specification section's
*Schema Validation Rules* state `FEATURES (required, array)`. The analyzer applies the
**recommended** schema's rules; the prose above grants continued support for the **legacy** shape.
Both statements are true, and they answer different questions. The analyzer measures conformance;
the gate this module needs is loadability.

**`No NAME features found` does not mean the names are missing.** It is an artefact of the analyzer
not looking inside the sub-list — it reports `NAMES` and `ADDRESSES` as *payload* attributes and
skips feature analysis entirely. Names in sub-list records are extracted normally at load. This is
the single most misleading line in the report, because a bootcamper cannot tell "the analyzer did
not look there" from "there are no names", and the natural conclusion is that the source is unusable.

**When the analyzer and the specification disagree, resolve it empirically — do not pick a
document.** Load **one** unmodified record and inspect the features Senzing extracted. If they come
back extracted, the data is loadable and every finding of this kind is conformance advice. Record
the probe's result and the conclusion you drew in that source's
`config/mapping_state_[datasource].json` (INV-125 already requires recording the raw failure and the
concluded cause). Module 5's own test load (`phase3-test-load.md`) is the same instrument one phase
later — this is that check, run early and on a single record.

⛔ **Never hand-write a mapper to convert a supported format into the recommended one in order to
clear this finding.** That is real work — five sources in the reported session — spent to satisfy a
notice. Converting is a legitimate *optional* improvement, on the grounds that new Senzing work
should target the recommended shape; offer it that way, never as remediation of a defect, and never
as a precondition for continuing.

⛔ **When `mapping_workflow`'s step-3 validation rejects the payload without an actionable
reason.** The block above handles a validator that is *unavailable*; this handles one that runs and
rejects unusably. Treat a rejection as **unactionable** when its text names no field and carries no
line or pointer the payload could be corrected against — a truncated error string is the observed
case.

1. **Bound the retry at two.** After two unactionable rejections for the same source, stop. A third
   attempt is guesswork with no convergence signal, and guessing costs the bootcamper more than the
   documented path saves.
2. **Capture the evidence first.** Before falling back, write the raw rejection text **verbatim**
   into that source's `config/mapping_state_[datasource].json` (a `validation_rejections` array).
   It is the only diagnostic the upstream fix has, and it is otherwise lost when the session ends.
3. **Ask, do not decide.** Present this pinned 👉 question (INV-051/INV-056, numbered, no "or"):

   👉 **The mapping validator rejected this source twice without saying why. How would you like to proceed? Reply with a number:**

   1. **Write the mapper against the Senzing Entity Specification** *(recommended)* — all three quality gates still run.
   2. **Try the mapping workflow once more** — it may succeed with a different payload.
   3. **Skip this source** — continue with the sources that mapped successfully.

   *(Internal: end the turn on this question and wait — INV-007.)*

4. **On option 1, the fallback is bounded, not a free hand.** State plainly what still holds:
   - Attribute names come from the Senzing Entity Specification in `docs/reference/` (see
     "Entity specification reference" below) — **never** from training data or memory. The
     "NEVER hand-code or guess Senzing attribute names" rule at the top of this phase is
     unchanged: reading the specification is not guessing (INV-080).
   - **All three quality gates still run**, with the same availability-aware handling as above.
   - The ⛔ cross-source shared-feature collision check still runs — it is cross-source, and the
     validator never performed it anyway.
   - The mapping is still only **structurally** validated; Data processing's match-key audit
     remains the semantic check (INV-117).
5. **Record how each mapper was produced.** Note the fallback and its reason in the source's
   mapping-state checkpoint and in its `docs/mapping/` write-up, so a reader of the deliverable can
   tell which sources went through `mapping_workflow` and which did not.

`mapping_workflow` remains the default and documented path. Never offer this fallback
pre-emptively — only after two unactionable rejections of the same source.

⛔ **These gates are structural, not semantic — say so; do not let green be mistaken for correct.**
Every check above validates **one source at a time** and asks whether the output is *well-formed*:
the analyzer checks structure against the Entity Specification, the verbatim check that values were
not altered, the routing report that fields reached a feature, the quality score completeness and
format. **None of them evaluates whether a field means what the feature means**, and none compares
how two sources populate the *same* feature. A mapping can pass all of them and still be wrong in
the way that matters most — telling Senzing two things conflict when they do not, which suppresses
legitimate merges.

Tell the bootcamper this plainly when reporting a passing result: the mapping is **structurally
valid**, and it is not **semantically validated** until data is loaded and the match keys are read.
Data processing's match-key audit is where that happens. A bootcamper who hears "all gates green"
and infers "the mapping is correct" has been misled by omission.

**Checkpoint:** write step 11.

### 12. Generate starter code

This step does **not** advance the workflow — generating the sample JSON and starter mapper is work
performed inside workflow step 4, which advances once at step 15 with its verdict (see the call
contract above). Tell the user: show a sample target JSON record so they see the output format.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show a sample target JSON record with annotations explaining the structure
>   (which fields became which Senzing attributes, how DATA_SOURCE and RECORD_ID are set, nested
>   vs. flat layout).
> - **Concise:** State the output file path and format only (e.g., "Output:
>   data/senzing-ready/customers.jsonl: one JSON record per line").

After `mapping_workflow` generates output files into the workspace, place them into the correct
project subdirectories per the file-placement guidance above (`.py` → `src/`, transformed JSONL
→ `data/senzing-ready/`, mapping docs → `docs/mapping/`, etc.). Regenerating a `docs/README.md`
docs index is a later porting phase: skip it for now.

**Checkpoint:** write step 12.

### 13. Build the transformation program

Use `generate_scaffold` or the mapping workflow output as the foundation. Handle: input
reading, field mapping, type conversion, cleansing, `DATA_SOURCE`/`RECORD_ID`, and error
handling. Save to `src/transform/transform_[name].[ext]`. Tell the user: the file path, what it
reads/writes, and what it handles.

**Keep JSON handling dependency-free.** This is usually the first Java the bootcamp generates, and
the bootcamp compiles with plain `javac` and never sets up Maven or Gradle — so the mapper must not
depend on an external JSON library (a scaffold importing `javax.json` will not compile as written).
Write the reader here so it needs only the standard library, and **reuse this same reader in later
modules** rather than re-deriving one per module: Data processing's loading program expects it. Full
rationale, and the rule that replacing the JSON library is safe while altering SDK calls is not, are
in `../module-02-sdk-setup/SKILL.md` → "The launch environment".

**Checkpoint:** write step 13.

### 14. Test

Run on 10-100 records from `data/samples/`. Validate with
`analyze_record(workspace_dir='data/mapping')` — ⛔ `workspace_dir` is a **required** parameter on
this tool as well, and it is where the analyzer script and its reports are written, so it takes the
same project-local mapping directory as the workflow. Tell the user: pass/fail, output file path,
sample record, any observations.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show pass/fail result, the output file path, a sample transformed record, and
>   any observations (warnings, skipped records, format issues).
> - **Concise:** Show pass/fail result and the output file path only (e.g., "✅ Pass: output:
>   data/senzing-ready/customers_sample.jsonl").

**Checkpoint:** write step 14.

### 15. Quality analysis

Run on 1000+ records. Evaluate feature distribution, coverage, quality scores. This is workflow
step 4's single advance: `action='advance'`, carrying `verdict` in `data` — `approve`,
`rework_mapping`, or `rework_code` — plus `output_path` and `records_output`. A `rework_*` verdict
is what routes step 17's iterate path. On `approve`, the response carries the workflow's Step 5
(`detect_environment`) menu; keep its `state` and handle that menu at **step 18a**, after this
source's mapper is written, reviewed and documented — not here. Tell the user: overall score, per-feature coverage with what
it means for matching, any issues found.

> **Presentation (conditional on `mapping_verbosity`):**
>
> - **Verbose:** Show the overall quality score, per-feature coverage breakdown with matching
>   implications (e.g., "NAME coverage 98%: strong for matching" / "ADDR coverage 42%: may
>   reduce match accuracy"), and all issues found with explanations.
> - **Concise:** Show the overall quality score, a count of mapped vs. unmapped fields, and
>   warnings only (e.g., "Quality: 85/100. 8 mapped, 3 unmapped. ⚠️ Low address coverage may
>   affect matching.").

**Offer visualization:** Pin the offer verbatim:

> 👉 **Would you like a web page showing the quality analysis (coverage charts and the field mapping summary)?**

If yes, generate a self-contained HTML page and save it to
`docs/visualizations/mapping_[name]_quality.html`.

**Checkpoint:** write step 15.

### 16. Review

Confirm with the user: output format correct, quality acceptable, ready for production or needs
adjustment.

**Iterate vs. proceed decision gate:** After presenting quality results, guide the decision and
close the turn on one 👉 question:

- **Quality ≥80% and all critical fields mapped:** "Quality looks strong. Ready to proceed to
  loading (Data processing)."
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
> `file_path` to the `data/senzing-ready/` output.

**Checkpoint:** write step 17.

### 18. Save and document

- Program in `src/transform/`.
- Docs in `docs/mapping/mapping_[name].md` (field mappings, logic, quality, how to run).
- Sample output in `data/senzing-ready/[name]_sample.jsonl`.
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

### 18a. Step 5 `detect_environment` menu handling (the optional-sandbox decision)

The `approve` verdict at step 15 advances workflow step 4, and the response to that advance carries
the workflow's **Step 5 (`detect_environment`)** with a four-option menu. Handle it **here**, once
this source's mapper is written, run, reviewed and documented (steps 12–18) — not at the moment the
response arrives.

⛔ **Why the placement matters.** This block previously sat under step 11 (Map), and
`phase3-test-load.md` pointed at step 11 as its entry. Both were wrong in the same direction:
choosing `test_load` there entered Phase 3 before the transformation program existed, so Phase 3's
step 22 had no "Phase 2 transformation output" to sample, and Phase 3's step 26 closes the module —
which would have skipped steps 12–18 entirely, including the transform code INV-042/INV-043 require
and step 19's mandatory per-source `docs/mapping/{source_name}_mapper.md` gate. Entering from 18a,
every prerequisite Phase 3 assumes is already on disk.

Do NOT stop at the menu: explain it and relay a recommendation so the bootcamper never hits a dead
end.

**`mapping_workflow` Steps 5–8 are optional sandbox validation** (Phase 3). They let you
trial-load the mapped source into a throwaway sandbox to preview entity resolution. They are
NOT the production load: the real load happens in **Data processing**. The four options are:

- **skip:** skip the per-source sandbox test load and move on. **Recommended when one or
  more unmapped sources remain.**
- **test_load:** run the optional sandbox test load (enters Phase 3) for this source.
- **load+resolve:** run the optional sandbox test load and resolve entities (enters Phase 3)
  for this source.
- **done:** finish the mapping workflow for this source without a sandbox test load.

**Multi-source continuation (recommended path):** When one or more unmapped sources remain,
recommend **skip**: the real load is deferred to Data processing, so a per-source sandbox test load
adds little here — and automatically continue to the next unmapped source (step 19) by starting its
own `mapping_workflow` run. Tell the bootcamper: "Steps 5–8 are an optional sandbox preview; since
you still have sources to map and the real load happens in Data processing, I'll skip the per-source
test load and move on to the next unmapped source."

**Explicit choice is preserved:** If the bootcamper explicitly chooses **test_load** or
**load+resolve**, follow that path into Phase 3 (`phase3-test-load.md`) unchanged. The real
production load still happens in Data processing regardless.

**Checkpoint:** write step 18a.

### 19. Repeat for remaining data sources

Each source gets its own transformation program and its own `mapping_workflow` run.

> **Mandatory internal gate (do not render to the bootcamper):** BEFORE writing the module
> completion checkpoint, list ALL files in `data/senzing-ready/` and verify that EACH has a
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

### 20. Module completion and transition

Once all sources are mapped, **complete the module** — this is Module 5's completion site whenever
the optional Phase 3 was not taken. Run the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md`: present the end-of-module summary (INV-032), append
the name-based Module 5 recap section to `docs/bootcamp_recap.md` (INV-085), show the
`✅ Module complete: Data Quality, Mapping, and Transformation` line (INV-079), and end the turn on the pinned
transition 👉 question naming the **next selected module** from `selected_modules` (INV-076 / INV-079):

👉 **Are you ready to move on to the next module: {next module name}?**

*(Internal: end the turn on this question and wait.)*

Do **not** choose the next module by re-checking SDK state — `selected_modules` already fixes the
order (SDK setup precedes Data Quality, Mapping, and Transformation; Data processing follows it). **Run Module
Completion exactly once:** if the bootcamper took Phase 3 and its step 26 already completed the
module (`data_quality_mapping` is already in `modules_completed`), skip completion here and present
only the transition.

**Checkpoint:** write step 20.
