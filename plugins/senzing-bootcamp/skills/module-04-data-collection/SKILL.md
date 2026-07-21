---
name: module-04-data-collection
description: "Bootcamp Module 4: Identify and Collect Data Sources. Use when the bootcamper starts or resumes Module 4, or needs to gather source data into data/raw/."
---

# Module 4: Identify and Collect Data Sources

> **MCP grounding (mandatory — applies to this entire skill).** Every Senzing fact you present —
> SDK method and attribute names, config options, error codes, and entity-resolution specifics —
> MUST come from the Senzing MCP tools, never from training data, memory, or speculation.
> **Pre-response checklist:** if a reply contains any Senzing specific, you MUST have called an MCP
> tool this turn to obtain it; if not, stop and call it first. This has the same precedence as a ⛔
> gate. The full rule and tool routing are the "MCP-first invariant" in
> `../bootcamp-onboarding/ground-rules.md`.

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, file placement, checkpointing). Execute every numbered step one at a time, in
order. Never skip, combine, or abbreviate a step containing a 👉 question: this has the same
absolute precedence as a mandatory gate.

**First:** Read `config/bootcamp_progress.json`, then (per ground-rules) show the module start
banner, journey map, before/after framing, a brief numbered overview of this module's steps, and the recommended model/effort nudge (INV-063), before any module work. Read `current_step` and
resume at the right step.

> **User reference:** Detailed background for this module lives in the Kiro Power at
> `docs/modules/MODULE_4_DATA_COLLECTION.md` (the docs port is a later porting phase).

**Prerequisites:** ✅ Module 1 complete (business problem defined, data sources identified).
System verification is optional (a deselectable module); when selected it precedes Data
collection, but Data collection does not require it.

**Before/After:** You have a list of data sources on paper. After this module, the actual data
files are in your project (`data/raw/`), documented, and ready for quality evaluation.

**Purpose:** Collect the actual data files from each identified data source and store them in
the project for analysis and mapping.

**Success indicator:** ✅ Sources collected + files in `data/raw/` OR documented locations +
`docs/data_source_locations.md` created + data collection status tracked.

## Error handling

When the bootcamper hits an error during this module:

1. **SENZ error code** (message contains `SENZ` + digits, e.g. `SENZ2027`): call
   `explain_error_code(error_code="<code>", version="current")` and present the explanation and
   recommended fix. If it returns nothing, continue to step 2.
2. Present the matching pitfall/fix for this module (full `common-pitfalls` reference is a
   later porting phase; for now, use `search_docs` to look up the symptom, then check any
   cross-module troubleshooting once ported).

## License limit and dataset size (canonical framing)

By default, the bootcamper already has Senzing's **built-in evaluation license**: the capacity
that applies when no custom license is configured. Treat it as the default the session already
has, presented as a choice rather than a wall. Before any license-based capacity or sampling
decision, **read `license_record_limit` from `config/bootcamp_progress.json`** (Module 2 writes
it after a custom license is configured) and drive the decision from that effective limit: never from a remembered or hardcoded figure:

- **Present and greater than 0** (custom license with a finite record cap): the effective limit
  is that value. Recommend sampling for license reasons only when the dataset total genuinely
  exceeds it.
- **Present and equal to 0** (custom license with no record cap): the license imposes no cap:   do **not** recommend sampling for license reasons, and support loading the full dataset.
- **Absent or null** (no custom license detected yet): fall back to the **built-in evaluation
  license** the bootcamper already has by default, whose capacity is confirmed via the Senzing
  MCP server at request time (never a hardcoded or remembered figure).

Whenever a dataset is: or might be: larger than the effective limit allows, present that as a
choice, not a wall. The bootcamper can keep their full dataset and expand capacity, or work
with a smaller slice, and downsizing is only ever one option among several, never the only path
forward.

- **Keep the full dataset and expand:** route to the Module 1 licensing paths: apply an
  existing license, request one through the external channel, or (when available) request one
  in-flow via the Senzing MCP server. Use the Module 1 Phase 1 discovery flow (Steps 5a–5e in
  `../module-01-business-problem/phase1-discovery.md`) for the tool-availability checks and
  branching; do not duplicate that logic here.
- **Work with a smaller slice (optional):** sampling, a CORD subset, or a smaller substitute
  dataset.

Sampling also stays available for **non-license** reasons: a very large or unwieldy file (for
example, >1GB) or faster iteration: independent of the effective limit. Retrieve any specific
record-capacity or validity figure from the Senzing MCP server at request time, exactly as the
Module 1 flow does. If the MCP server does not return a figure or cannot be reached, omit the
number and say the current value is unavailable from the MCP server: never restate a
remembered or hardcoded figure here.

## Workflow

`🛑`/`⛔` are internal control directives: never render them; signal a stop by ending the turn
on the single 👉 question and waiting.

### 1. Review identified data sources

Recap the data sources identified in Module 1. Review `docs/business_problem.md` for the
complete list.

**Checkpoint:** write step 1 to `config/bootcamp_progress.json`.

### 2. For each data source, collect the data

First, ask how the bootcamper wants to provide the data for a given source — pin this question
verbatim (INV-051), never joining the choices with "or":

👉 **How would you like to provide the data for this source? Reply with a number:** (1) upload a
file, (2) provide a URL or file path, (3) connect to a database, (4) use an API endpoint.

*(Internal: end the turn on this question and wait.)*

**If the bootcamper doesn't have their own data** or wants free data to practice with,
recommend CORD data as the primary alternative:

> "Senzing provides **CORD (Collections Of Relatable Data)**: curated, real-world-like
> datasets designed specifically for entity resolution evaluation. These are the best option
> for learning with realistic data patterns.
>
> I can pull CORD datasets (Las Vegas, London, Moscow) using the `get_sample_data` tool: these
> are ready-to-use Senzing JSONL files.
>
> Learn more about CORD: <https://senzing.com/senzing-ready-data-collections-cord/>"

Use `get_sample_data(dataset='list')` to show available CORD datasets. Present the
`download_url` from the response so the bootcamper can download the full JSONL file.

**If the bootcamper declines CORD data** or needs something different, offer secondary options:

> "If CORD doesn't meet your needs, there are other options:
> - **Free raw data:** A curated collection of 35+ free data sources at
>   <https://github.com/docktermj/senzing-bootcamp-free-data>: these include raw samples
>   (great for practicing mapping) and pre-mapped files.
> - **Synthesized test data:** I can generate custom test data tailored to your specific
>   scenario."

Then proceed with the appropriate option:

**Option A: Bootcamper uploads files**

- Ask for data files (CSV, JSON, Excel, etc.).
- Files can be dragged into the chat or uploaded.
- Save uploaded files to `data/raw/[datasource_name].[extension]`.
- Example: `data/raw/customer_crm.csv`, `data/raw/vendor_api.json`.

**Option B: Bootcamper provides URL/location**

- Ask for the URL or file path where data resides.
- Document the location in `docs/data_source_locations.md`.
- If accessible, download/copy data to `data/raw/`.
- If not accessible (requires credentials, VPN, etc.), document the access method.

**Option C: Database connection**

- Ask for database connection details.
- Document the connection string (without passwords) in `docs/data_source_locations.md`.
- Store sample query results in `data/raw/[datasource_name]_sample.csv`.
- Document the query used to extract data.

**Option D: API endpoint**

- Ask for the API endpoint URL and authentication method.
- Document API details in `docs/data_source_locations.md`.
- Store a sample API response in `data/raw/[datasource_name]_sample.json`.
- Document the API call used.

**Handling different data formats:**

Not all data arrives as CSV. Common formats and how to handle them:

- **Excel (.xlsx):** Convert to CSV first. Most languages have libraries for this (e.g.,
  `openpyxl` for Python, Apache POI for Java). Save the CSV to `data/raw/`.
- **Parquet / Avro:** Use language-appropriate libraries to read and convert to CSV or JSON.
  These formats are common in data lake exports.
- **XML:** Parse and flatten to JSON or CSV. Use `find_examples(query='XML data loading')` for
  patterns.
- **Database exports (SQL dump):** Extract the relevant tables to CSV using the database's
  export tools.
- **API pagination:** If the API returns paginated results, document the pagination strategy
  and write a collection script in `src/scripts/` that fetches all pages and saves to
  `data/raw/`.
- **Real-time streams (Kafka, etc.):** For the bootcamp, capture a snapshot to a file. Document
  the stream details for production use (a production follow-up; see the graduation migration checklist).

For any non-CSV/JSON format, the goal is to get the data into a flat file in `data/raw/` that
Module 5 can evaluate.

> **Data Source Registry:** After collecting each data source file, record it in a registry at
> `config/data_sources.yaml` so later modules can track it. If the file doesn't exist, create
> it with `version: "1"` and an empty `sources:` mapping first. For each source set: `name`,
> `file_path`, `format`, `record_count` (if known, else null), `file_size_bytes`,
> `quality_score: null`, `mapping_status: pending`, `load_status: not_loaded`, `added_at` and
> `updated_at` to the current ISO 8601 timestamp. If an entry already exists for that
> DATA_SOURCE key, update it and set `updated_at`. *(The Kiro registry helpers are a later
> porting phase; write/update the YAML directly for now.)*

> **Data File Validation:** After each file is saved to `data/raw/`, sanity-check it (readable,
> non-empty, expected format/encoding, plausible record count) and update the registry with the
> results. Present the outcome to the bootcamper. If all checks pass, confirm the file is ready
> and move on to the next data source. If any check fails, show the failure details and
> remediation guidance, then help the bootcamper resolve the issue (re-upload, convert format,
> fix encoding, etc.) before proceeding. Re-check after each fix attempt until the file passes.
> *(The Kiro `validate_data_files.py` validator is a later porting phase; perform the checks
> directly for now.)*

> **CORD Metadata Capture:** If the bootcamper chose their own data instead of CORD data, skip
> this. Otherwise, after CORD data has been downloaded via `get_sample_data` and validated,
> capture a metadata snapshot (dataset name, file paths, a content hash or size/mtime) so
> Module 6 can detect if files changed between download and load time. Store it in
> `config/cord_metadata.yaml`. *(The Kiro `cord_metadata.py` helper is a later porting phase;
> record the snapshot directly for now.)*

> **CORD Provenance Recording:** After each data source file is collected and its registry
> entry created/updated in `config/data_sources.yaml`, set the `provenance` field based on the
> data origin:
>
> - `cord`: source obtained via the `get_sample_data` MCP tool
> - `own`: bootcamper's own data (uploaded, URL, database, or API)
> - `free_data`: data from the free-data GitHub repository
> - `synthesized`: generated test data
> - `unknown`: origin cannot be determined
>
> Set `updated_at` to the current ISO 8601 timestamp when writing provenance. A source with
> `provenance: unknown` is never eligible for the fast-path.

**Checkpoint:** write step 2 to `config/bootcamp_progress.json`.

### 3. Verify data was received

```bash
# Linux / macOS
ls -lh data/raw/
head -5 data/raw/customer_crm.csv
head -5 data/raw/vendor_api.json
```

```powershell
# Windows (PowerShell)
Get-ChildItem data\raw\ | Format-Table Name, Length
Get-Content data\raw\customer_crm.csv -TotalCount 5
Get-Content data\raw\vendor_api.json -TotalCount 5
```

**Checkpoint:** write step 3 to `config/bootcamp_progress.json`.

### 4. Document data source locations

**Data Collection Checklist:** Always create a structured checklist in the project — no question
(INV-012). Create `docs/data_collection_checklist.md` with a Data Inventory Table (one row per
data source) and a Validation Checklist, and guide the bootcamper to fill in one row per source
and complete the checklist before Module 5. Announce it as a produced file in the Step 9
end-of-module summary's "Files produced" list (INV-032). *(The Kiro
`templates/data_collection_checklist.md` port is a later porting phase; compose the checklist
directly for now.)*

Also create or update `docs/data_source_locations.md`:

````markdown
# Data Source Locations

## Data Source 1: Customer CRM
- **Type**: CSV file
- **Location**: `data/raw/customer_crm.csv`
- **Original Source**: Uploaded by user from local system
- **Last Updated**: 2025-01-17
- **Record Count**: ~50,000 records
- **Access Method**: One-time upload

## Data Source 2: Vendor API
- **Type**: JSON API
- **Location**: Sample data in `data/raw/vendor_api_sample.json`
- **Original Source**: https://api.vendor.com/v1/suppliers
- **Last Updated**: 2025-01-17
- **Record Count**: ~5,000 records
- **Access Method**: API call with Bearer token authentication
- **API Documentation**: https://api.vendor.com/docs
- **Sample API Call**:
  ```bash
  # Linux / macOS
  curl -H "Authorization: Bearer $API_TOKEN" \
       https://api.vendor.com/v1/suppliers?limit=100
  ```

  ```powershell
  # Windows (PowerShell)
  Invoke-RestMethod -Headers @{Authorization="Bearer $env:API_TOKEN"} `
    -Uri "https://api.vendor.com/v1/suppliers?limit=100"
  ```

## Data Source 3: Legacy Database

- **Type**: PostgreSQL database
- **Location**: Sample data in `data/raw/legacy_db_sample.csv`
- **Original Source**: postgresql://dbserver.company.com:5432/legacy_db
- **Last Updated**: 2025-01-17
- **Record Count**: ~200,000 records
- **Access Method**: Database query (requires VPN)
- **Sample Query**:

  ```sql
  SELECT customer_id, name, address, phone, email
  FROM customers
  WHERE active = true
  LIMIT 1000;
  ```

````

The SQL above documents the bootcamper's own external source system, not the Senzing database.
Never generate SQL against `database/G2C.db`.

**Checkpoint:** write step 4 to `config/bootcamp_progress.json`.

### 5. Handle sensitive data appropriately

- Remind the bootcamper about data privacy (the Kiro `security-privacy` steering reference is a
  later porting phase; use `search_docs` for Senzing's guidance in the meantime).
- If data contains PII, suggest anonymizing for testing.
- Ensure `.gitignore` excludes `data/raw/*` to prevent committing sensitive data.
- Document any data handling requirements in `docs/security_compliance.md`.

**Checkpoint:** write step 5 to `config/bootcamp_progress.json`.

### 6. Create sample files if needed

A smaller working file can be useful in two situations: a very large dataset (e.g., >1GB) that
is unwieldy to handle, or a dataset larger than the effective record limit allows. In **both**
cases sampling is one option, not a requirement.

If the dataset may exceed the effective record limit, apply the canonical framing at the top of
this module: **read `license_record_limit` from `config/bootcamp_progress.json`** and drive the
decision from that effective limit. When it is `0` (no cap) or greater than or equal to the
dataset size, do **not** recommend sampling for license reasons: support loading the full
dataset. When it is absent or null, fall back to the built-in evaluation capacity confirmed via
the Senzing MCP server. When the dataset genuinely exceeds the effective limit, the bootcamper
can keep their full dataset and expand capacity via the Module 1 licensing paths, or work with
a smaller slice. Do not steer them to a smaller substitute as the only path. Defer the
licensing-path availability checks and any capacity figure to the Module 1 Phase 1 discovery
flow (Steps 5a–5e in `../module-01-business-problem/phase1-discovery.md`) and the Senzing MCP
server.

**If the bootcamper chooses to work with a smaller slice:**

- Create smaller sample files (sampling, a CORD subset, or a smaller substitute dataset).
- Save samples to `data/samples/[datasource_name]_sample.[extension]`.
- Document the sampling method (first N records, random sample, etc.).
- Ensure the sample is representative of the full dataset.

**If the bootcamper chooses to keep the full dataset:** continue the collection workflow with
the complete files: there is no requirement to reduce the dataset.

**Checkpoint:** write step 6 to `config/bootcamp_progress.json`.

### 7. Verify data quality at a glance

Each file was already validated in step 2 and the results are stored in the registry. Review
`config/data_sources.yaml` and check the `validation_status` and `validation_checks` fields for
each data source entry. Confirm every source shows `validation_status: passed`. If any source
shows `validation_status: failed`, revisit that data source and resolve the failing checks
before proceeding.

**Checkpoint:** write step 7 to `config/bootcamp_progress.json`.

### 8. Update data source tracking

```markdown
Data Source Collection Status:
- ✅ Customer CRM - Collected (data/raw/customer_crm.csv)
- ✅ Vendor API - Sample collected (data/raw/vendor_api_sample.json)
- ⬜ Legacy Database - Pending (requires VPN access)
```

**Checkpoint:** write step 8 to `config/bootcamp_progress.json`.

### 8a. Record-count license back-fill (after all sources are collected)

Infer the real record total from `config/data_sources.yaml`. If the collected total exceeds the
built-in evaluation limit and Module 1 license guidance was skipped or deferred, surface the
**existing** Module 1 Steps 6b–6e license guidance now: using the canonical framing at the top
of this module and the Senzing MCP server for any capacity/validity figure: then update the
same `license` / `license_guidance_deferred` markers Module 1 uses. If guidance was already
delivered, or the total is at or below the limit, do not re-present guidance. If the total
cannot be computed, note the warning and continue on Module 1's prose-count behavior. This step
is non-blocking: always proceed to Step 8b regardless of the outcome. *(The Kiro
`record_count_backfill.py` helper is a later porting phase; compute the total from the registry
directly for now.)*

**Checkpoint:** write step 8a to `config/bootcamp_progress.json`.

### 8b. SQLite load-time warning (collection-time heads-up)

This is a *time/performance* heads-up, deliberately **distinct** from the license-capacity
sampling framing at the top of this module: it judges the Module 6 SQLite load time from the
actual collected dataset and fires even when the effective license imposes no record cap. It is
**not a mandatory gate**: the bootcamper may always proceed on SQLite with the full dataset.
Run this once at the end of collection, immediately before the Step 9 transition. Every part is
non-blocking: any failure or indeterminate input continues the Module 4 flow.

1. **Read the persisted inputs.** Read the registry from `config/data_sources.yaml` and
   `database_type` from `config/bootcamp_preferences.yaml`. Compute the collected total record
   count from the registry. If the registry cannot be read or parsed, treat the total as
   indeterminate: do not fail.

2. **Decide whether to warn.** Warn only when the database is SQLite **and** the collected total
   is above the load-time threshold. Otherwise (total at or below the threshold, any non-SQLite
   engine, or indeterminate inputs) say nothing about load time and continue to the Step 9
   transition.

   - **Warn:** consult the **Senzing MCP server** at request time for the timing figures
     (expected throughput, throughput degradation, expected load duration, redo-phase
     duration). Any figure the server does not return, or that errors, stays unavailable: never
     substitute a remembered number. Present a load-time warning built from what the server
     returned, then end the turn on the question below and wait for the bootcamper's choice.

   👉 **Loading all collected records into SQLite may take a while. How would you like to proceed? Reply with a number:**

   1. Load all records into SQLite.
   2. Sample down to a smaller record count.
   3. Switch to an alternative database like PostgreSQL.

   *(Internal: end the turn on this question and wait.)*

3. **Act on the choice.** Sampling is offered here as one option among proceeding and switching
   databases: not the only path.

   - **Load all collected records on SQLite:** first obtain an **explicit confirmation** that
     the bootcamper accepts the expected load time before continuing with the full dataset. Then
     record the decision (sub-step 4) and continue to Step 9.
   - **Sample down to a smaller record count:** ask which sampling strategy to use **before**
     creating the sample: offer first-N records, random-N records, and an
     entity-resolution-demonstrating strategy that preserves cross-source overlaps and known
     match clusters; also accept a bootcamper-described strategy. Validate the target record
     count (a positive integer strictly less than the collected total) and re-ask until valid.
     Create the sample with the chosen strategy, write it under `data/samples/`, and document
     the strategy and target in a sample manifest. Then record the decision (sub-step 4).
   - **Switch to an alternative database (e.g. PostgreSQL):** route the bootcamper to the
     database-migration guide (the Kiro `docs/guides/DATABASE_MIGRATION.md` guide is a later
     porting phase). Do not inline or restate the migration steps here. Then record the decision
     (sub-step 4).

4. **Record the decision.** Write a load-decision marker capturing the choice
   (`proceed`, `sample`, or `switch_db`) keyed to the collected dataset identity, so the
   Module 6 SQLite heads-up does not redundantly re-ask about this same load.

Refer to the Senzing MCP server by name only (never a URL). Use only synthetic/persisted values
: never echo credentials or connection strings. *(The Kiro `volume_utils` and
`load_time_warning` helpers, and the shared marker/identity logic, are a later porting phase;
apply the behavior directly for now.)*

**Checkpoint:** write step 8b to `config/bootcamp_progress.json`.

### 9. Module completion and transition to Module 5

Run the standard **Module Completion** process in `../bootcamp-onboarding/module-completion.md`
(update progress, append the Module 4 recap section to `docs/bootcamp_recap.md`, and present the
end-of-module summary), then ask the single transition question:

"Great! Now that we have the data files, let's evaluate each one to see if it needs mapping or
if it's already in the right format for Senzing."

👉 **Are you ready to move on to the next module: {next module name}?**

**Checkpoint:** write step 9 to `config/bootcamp_progress.json`. On module completion set
`current_step` to `null`.

## Agent behavior

- Be patient with file uploads: they may take time.
- Provide clear instructions for each data source type.
- Help the bootcamper create sample files if full datasets are too large.
- Remind about data privacy and security.
- Verify files are accessible before proceeding.
- Document everything in `docs/data_source_locations.md`.
- **If the bootcamper doesn't have data or asks about free data sources**, follow the data
  recommendation hierarchy: (1) recommend CORD data first via the `get_sample_data` MCP tool
  (Las Vegas, London, Moscow datasets) with reference to
  <https://senzing.com/senzing-ready-data-collections-cord/>; (2) if CORD is declined, recommend
  <https://github.com/docktermj/senzing-bootcamp-free-data> for raw samples and additional
  sources; (3) offer synthesized test data generation only as a last resort after CORD and
  free-data options are declined.
