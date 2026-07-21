# Module 3, Phase 1: Verification Pipeline (steps 1–8)

Follow `../bootcamp-onboarding/ground-rules.md`. Execute every numbered step one at a time, in
order; never skip, combine, or abbreviate a step containing a 👉 question. `🛑`/`⛔` are internal
directives, never rendered; signal a stop by ending the turn on the single 👉 question and
waiting. This sequential rule has the same precedence as a mandatory gate; no internal reasoning
overrides it.

## Opt-Out Gate

Before starting Module 3 steps, check whether the bootcamper has explicitly requested to skip.

**Trigger phrases:** "skip verification", "I've already verified", "skip module 3".

**If triggered:**

1. Record the skip in `config/bootcamp_progress.json`:

   ```json
   {"module_3_verification": {"status": "skipped", "reason": "bootcamper_opted_out"}}
   ```

2. Display this warning:

   ```text
   ⚠️ Skipping system verification. If you encounter issues in later modules
   (data loading failures, SDK errors), Module 3 can help diagnose them.
   Say "run verification" at any time to come back.
   ```

3. Update gate 3→4 to "skipped" and proceed to the next selected module.

> **The visualization is a separate module.** System Verification produces **no** visualization —
> the guaranteed Truth Set web-app "wow moment" is delivered by the selectable **Truth Set
> visualization** module (`truthset_visualization`), a separate, standalone module run **next**
> whenever selected (always in Core; in Customized only if chosen). Skipping System Verification
> does NOT skip that module, and System Verification does not offer a standalone TruthSet demo of
> its own.

**If NOT triggered:** proceed with Module 3 normally (default path).

## Agent Rules

The following rules are mandatory for the agent executing this module:

1. **Synthetic verification data only:** verify with a small set of **synthetic records** you
   generate in Step 2 — designed to resolve deterministically into a known number of entities.
   System Verification MUST NOT acquire, load, or visualize the Senzing TruthSet, nor use CORD,
   Las Vegas, London, or Moscow. (The TruthSet belongs exclusively to the separate, standalone
   **Truth Set visualization** module.) Offer no dataset choice to the bootcamper.
2. **Database path:** the Senzing database is at `database/G2C.db`. All SDK initialization and
   database operations MUST reference this path.
3. **No dataset choice:** do not present any dataset selection prompt, menu, or question. The
   generated synthetic data is the only data used for verification in this phase.
4. **All checks execute regardless of failures:** if any step fails, continue executing all
   subsequent steps. No short-circuiting. The Verification Report MUST include the status of
   every check.
5. **Artifact isolation:** all verification artifacts (scripts and data files) MUST be created
   within `src/system_verification/`. No verification files outside it.
6. **Timeouts enforced:** every step MUST enforce its defined timeout. If a process exceeds its
   timeout, terminate it immediately and record a fail.
7. **MCP as source of truth:** all Senzing facts (SDK method/attribute names, config options,
   error codes) and all generated SDK/loading/query code come from the MCP server tools, never
   from training data. The synthetic records' expected resolution is known **by construction**
   (you design them to merge), so Step 7 validates against that design, not against an MCP
   expected-results set.
8. **Overwrite on re-run:** if the module is re-run, overwrite all existing artifacts in
   `src/system_verification/`. The database cleanup ensures a clean slate.
9. **No orphaned processes:** System Verification starts no web service; the separate Truth Set
   visualization module starts and terminates its own web service within its own phases.
10. **Progress persistence:** every step MUST write its checkpoint to
    `config/bootcamp_progress.json` immediately upon completion, before proceeding.

### Step 1: MCP Connectivity Check

Verify MCP server connectivity before code generation operations.

1. Call `search_docs(query="Senzing SDK initialization")` with a 10-second timeout.
2. **If a response is received** (including empty results): MCP connectivity confirmed. Proceed
   silently; do not display connectivity status to the bootcamper.
3. **If the call fails** (timeout or error): retry `search_docs` once with the same 10-second
   timeout.
4. **If the retry succeeds:** proceed silently.
5. **If the retry fails:** display troubleshooting steps:
   - Verify internet connectivity.
   - Test the `mcp.senzing.com:443` endpoint.
   - Allowlist the endpoint if behind a corporate proxy.
   - Restart the MCP connection for the senzing server in Claude Code.
   - Verify DNS resolution.

   Block all further module progress until the bootcamper says "retry" and the connectivity
   check passes.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "mcp_connectivity": {"status": "passed", "duration_ms": <elapsed>}
    }
  }
}
```

### Step 2: Generate Synthetic Verification Records

Generate a small set of **synthetic** records designed to resolve deterministically into a known
number of entities, so verification proves entity resolution works **without touching the Senzing
TruthSet**. The records are the agent's own composition — no MCP TruthSet fetch, no sanctioned
fallback source, no CORD substitute. Keep them obviously synthetic and PII-free (invented
names/addresses).

1. **Compose the records (by construction).** Write at least 4 records to
   `src/system_verification/verification_data.jsonl` (one JSON object per line, overwrite any
   existing file), using **Senzing Entity Specification** attribute names. If unsure of the exact
   attribute names, confirm them via the MCP server (`search_docs` / `mapping_workflow`) — never
   guess (INV-080). Design them so resolution is deterministic and known in advance:
   - **A merge cluster:** 2–3 records for the **same** synthetic person, sharing enough features
     (matching full name + date of birth + address, with only trivial variation) that Senzing
     resolves them into **one** entity.
   - **At least one distractor:** 1+ record for a **different** synthetic person that must stay a
     **singleton** (its own entity).
   - Give every record a `DATA_SOURCE` of `VERIFY` (one synthetic source code is enough) and a
     unique `RECORD_ID`.
2. **Record the expected outcome** (by construction) for Step 7 to validate against — e.g. "4
   records → 2 entities, one entity with 3 constituent records". These figures come from the
   records you just wrote; never fetch them from anywhere.

**Checkpoint:** write to `config/bootcamp_progress.json` (a data-prep marker, not one of the
report's verification checks):

```json
{"module_3_verification": {"synthetic_data": {
  "status": "generated", "records": <record_count>, "data_source": "VERIFY",
  "expected_entities": <entity_count>, "expected_merge_record_count": <largest_cluster_size>}}}
```

### Step 3: SDK Initialization

Verify the Senzing SDK initializes correctly and connects to the database.

1. Generate an SDK initialization script using `generate_scaffold(workflow='initialize')` in the
   bootcamper's chosen language.
2. Save the generated code to `src/system_verification/verify_init.[ext]` where `[ext]` matches
   the chosen-language file extension (`.py`, `.java`, `.cs`, `.rs`, `.ts`).
3. Execute the initialization script with a 30-second timeout.
4. **If the script exits with code 0 and produces no SENZ error codes:** report pass; the SDK
   connected to the database at `database/G2C.db`.
5. **If the script exits non-zero or produces a SENZ error code:** report fail. Call
   `explain_error_code` for any SENZ codes. Generate a Fix_Instruction referencing Module 2
   remediation steps.
6. **If the script does not complete within 30 seconds:** terminate the process. Report fail
   with a timeout Fix_Instruction advising a check of database accessibility and system
   resources.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "sdk_initialization": {"status": "passed|failed", "duration_ms": <elapsed>}
    }
  }
}
```

### Step 4: Code Generation

Verify the MCP server can generate a full pipeline script in the chosen language.

1. Call `generate_scaffold(workflow='full_pipeline')` in the bootcamper's chosen language.
2. Save the generated code to `src/system_verification/verify_pipeline.[ext]` where `[ext]` is
   the standard file extension for the chosen language.
3. **Validate the generated file:**
   - Confirm it contains at least 1 line of non-whitespace content.
   - Confirm it includes at least one language-appropriate structural element: an import
     statement, a function definition, or a class declaration.
4. **If validation passes:** report pass for code generation.
5. **If the generator returns an empty response, an error, or does not respond within 30
   seconds:** report fail with a Fix_Instruction advising a check of MCP connectivity to
   `mcp.senzing.com:443`, then retry.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "code_generation": {"status": "passed|failed", "file": "verify_pipeline.[ext]"}
    }
  }
}
```

### Step 5: Build/Compile

Verify the generated code compiles or passes syntax checking. Enforce a 120-second timeout for
all build commands.

| Language | Build Command |
|----------|--------------|
| Python | `python3 -m py_compile src/system_verification/verify_pipeline.py` |
| Java | `javac src/system_verification/verify_pipeline.java` |
| C# | `dotnet build src/system_verification/` |
| Rust | `cargo build --manifest-path src/system_verification/Cargo.toml` |
| TypeScript | `tsc src/system_verification/verify_pipeline.ts --noEmit` |

1. Execute the build command for the chosen language.
2. **If the build exits with code 0:** report pass.
3. **If the build fails** (non-zero exit code): report fail including the first 50 lines of
   compiler error output. Generate a Fix_Instruction identifying common causes (missing SDK
   libraries, incorrect PATH, missing build tools).
4. **If the build does not complete within 120 seconds:** terminate the process. Report fail
   with a timeout Fix_Instruction suggesting a check for dependency-resolution issues or
   network-dependent build steps.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "build_compilation": {"status": "passed|failed", "duration_ms": <elapsed>}
    }
  }
}
```

### Step 5a: Register the Synthetic Data Source Code

Register the synthetic verification data's source code(s) in the Senzing configuration
**before** loading, so Step 6 does not fail with `SENZ2207: Data source code [...] does not
exist`. The default config seeded in Module 2 has no data sources registered, yet
the load below references the code(s) the Step 2 records carry, which must exist
first — so without this step every Module 3 run hits SENZ2207 on the first load attempt.

1. **Determine the source codes to register.** Collect the distinct `DATA_SOURCE`
   values present in the synthetic verification data
   (`src/system_verification/verification_data.jsonl` from Step 2) — normally just
   **VERIFY**. Never register a code that is not present in the data.
2. **Generate the registration code from the MCP server** (Agent Rule 7 — never
   hand-write it): call `sdk_guide(topic='configure')` (and `generate_scaffold` if
   it exposes a data-source registration workflow) in the language read from
   `programming_language` in `config/bootcamp_preferences.yaml` (never a hardcoded
   default). Save the result to
   `src/system_verification/register_data_sources.[ext]` (Agent Rule 5 — artifact
   isolation; INV-018). The generated code MUST:
   - Load the current default Senzing configuration.
   - Register each data source code from step 1 in that configuration.
   - Set the updated configuration as the new default, so `verify_pipeline` and every
     later SDK session see the codes. Use the exact config classes/methods returned by
     `sdk_guide`/`generate_scaffold` — never hardcode SDK names from memory.
   - Be **idempotent:** a code that is already registered is treated as success,
     not an error, so re-running Module 3 or resuming mid-module still passes.
3. **Build the registration code if the language requires it** (compiled languages
   — Java, C#, Rust, TypeScript), using the same per-language build command as
   Step 5. Enforce a 120-second build timeout.
4. **Execute** `register_data_sources.[ext]` with a 60-second timeout.
5. **If it completes with exit code 0:** report pass listing the source codes now
   registered, and record them in `config/data_sources.yaml` (INV-050).
6. **If it fails:** capture the error output, call `explain_error_code` for any
   SENZ codes, and report fail with remediation. Per Agent Rule 4, continue to
   Step 6 regardless; Step 6 keeps its generic SENZ handling as a fallback.
7. **If it does not complete within 60 seconds:** terminate the process and report
   fail with a timeout note.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "data_source_registration": {"status": "passed|failed", "sources_registered": ["VERIFY"]}
    }
  }
}
```

### Step 6: Data Loading

Execute the verification script to load the synthetic verification data
(`src/system_verification/verification_data.jsonl` from Step 2) into Senzing. The `VERIFY`
data source code was registered in Step 5a, so the load runs against a config that already
knows it; the SENZ handling below remains as a fallback.

1. Execute the generated `verify_pipeline.[ext]` script with a 120-second timeout, pointing it
   at `src/system_verification/verification_data.jsonl`.
2. **While executing:** display a progress indicator updated at least every 5 seconds showing
   records processed out of total expected.
3. **If the script completes with exit code 0:** confirm the number of records loaded exactly
   matches the synthetic record count generated in Step 2.
4. **If the record count matches:** report pass with the number of records loaded.
5. **If the script encounters an error:** capture error output, call `explain_error_code` for
   any SENZ codes, and report fail with remediation guidance.
6. **If fewer records load than expected without error:** report fail identifying records loaded
   versus expected. Instruct the bootcamper to check the synthetic data file integrity.
7. **If the script does not complete within 120 seconds:** terminate the process. Report fail
   indicating execution timed out.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "data_loading": {"status": "passed|failed", "records_loaded": <count>}
    }
  }
}
```

### Step 7: Deterministic Results Validation

Validate that entity resolution produced the outcome you defined **by construction** in Step 2.
Each validation check has a 30-second timeout.

1. Recall the expected outcome recorded in Step 2 (`module_3_verification.synthetic_data`): the
   expected entity count, the record IDs designed to **merge** into one entity, and the
   distractor record(s) designed to stay **singletons**. These come from the records you wrote,
   not from the MCP server.
2. Query the resolved entities (generate the query/report SDK code via `get_sdk_reference` +
   `sdk_guide`, or use `reporting_guide` for counts; never direct SQL) and perform the following
   validation checks. Execute ALL checks regardless of whether earlier checks pass or fail:

   **a) Entity count:**
   - Verify the total number of resolved entities equals the expected entity count from Step 2.

   **b) Merge cluster resolves to one entity:**
   - Verify the 2–3 records designed to match resolve to the **same** single entity ID.

   **c) Cross-record resolution:**
   - Verify the resolved entity count is strictly less than the total record count loaded,
     confirming that the merge cluster collapsed rather than every record loading as a singleton.

   **d) Distractor stays a singleton:**
   - Verify the distractor record(s) resolve to their own entity, separate from the merge cluster.

3. **If all checks pass:** report pass with the entity count and confirmation of the merge.
4. **If any check fails:** report fail listing each failed check with expected versus actual
   values. Suggest re-running data loading or checking that the synthetic data file was loaded
   completely.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "results_validation": {"status": "passed|failed", "entities": <count>, "matches_verified": <count>}
    }
  }
}
```

### Step 8: Database Operations

Verify read, write, and search operations against the Senzing database. Each operation has a
30-second timeout. Perform all operations through generated Senzing SDK code (via
`get_sdk_reference` + `sdk_guide`), never direct SQL against `database/G2C.db`.

1. **Verify write count:**
   - Confirm the record count returned by the Senzing engine matches the synthetic record count
     established during data loading (Step 6).
2. **Verify read by entity ID:**
   - Retrieve the merge-cluster entity (from Step 7) by its entity ID.
   - Confirm the response contains at least: the entity ID, one constituent record key (data
     source and record ID pair), and one name attribute from the original synthetic input.
3. **Verify search by attributes:**
   - Perform a search-by-attributes query using name and address attributes from one of the
     synthetic records.
   - Confirm the expected entity appears in the search results.
4. **If all operations succeed within 30 seconds each:** report pass with operations tested.
5. **If any operation fails or times out:** report fail identifying which operation failed
   (write, read, or search), the error received, and a Fix_Instruction referencing database
   configuration from Module 2.

**Checkpoint:** write to `config/bootcamp_progress.json`:

```json
{
  "module_3_verification": {
    "checks": {
      "database_operations": {"status": "passed|failed", "ops_tested": ["write", "read", "search"]}
    }
  }
}
```

**Agent behavior:** after Step 8 completes, proceed to Phase 2 (Report and Close) without asking
whether the bootcamper wants to continue: load `phase2-report-close.md`. That phase records System
Verification, purges the synthetic `VERIFY` data, and asks the single transition question to the next
selected module. When the **Truth Set visualization** is selected (`truthset_visualization` in
`selected_modules`; always true in Core), that next module is the separate, standalone Truth Set
visualization module (`../module-03b-truthset-visualization/`) — a first-class module (INV-086/INV-087)
that opens with its own module-start apparatus, then acquires and loads the Senzing Truth Set itself
and visualizes it. When it is not selected, the next module is Data collection.

## Success Criteria

System Verification is successfully complete when ALL of the following are true:

- All 8 System Verification checkpoint entries report "passed" status (`mcp_connectivity`,
  `sdk_initialization`, `code_generation`, `build_compilation`, `data_source_registration`,
  `data_loading`, `results_validation`, `database_operations`).
- The Verification Report is persisted to `config/bootcamp_progress.json` with a valid ISO 8601
  timestamp.
- The synthetic verification records are purged from the database (zero `VERIFY` entities remain).
- The gate 3→4 status is updated to "completed".
- The `## System verification` recap section is appended to `docs/bootcamp_recap.md` (the
  consolidated recap replaced the separate `docs/bootcamp_journal.md`; the narrative lives in the
  section's `### Journal` subsection).

(The Truth Set visualization module — run next when selected — owns its own `web_service`/`web_page`
checks, standalone snapshot, web-service termination, TruthSet purge, and `## Truth Set
visualization` recap section; see `../module-03b-truthset-visualization/`.)
