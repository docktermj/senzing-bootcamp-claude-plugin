# Module 3, Phase 2: Report and Close (steps 9–11)

Continues from Phase 1 (`phase1-verification.md`). Follow `../bootcamp-onboarding/ground-rules.md`;
`🛑`/`⛔` are internal directives, never rendered. This closes **System Verification** only; the Truth
Set visualization is a separate, standalone module that runs next when selected and has its own close.

## Step 9: Verification Report Generation

Generate a structured summary of the System Verification checks.

1. Compile the results from the 8 System Verification checkpoint entries (`mcp_connectivity`,
   `sdk_initialization`, `code_generation`, `build_compilation`, `data_source_registration`,
   `data_loading`, `results_validation`, `database_operations`) into a single Verification Report.
   (The Truth Set visualization is a separate, standalone module; its `web_service`/`web_page`
   checks and the visualization artifact belong to that module's own close, not this report.)

2. For each check, record:
   - Pass or fail status
   - Duration in milliseconds (where applicable)
   - Any relevant metadata (record counts, entity counts, file paths, ports)

3. **If ALL checks passed:** display a success banner:

   ```text
   ╔══════════════════════════════════════════════════════════╗
   ║  ✅ SYSTEM VERIFICATION COMPLETE                         ║
   ║                                                          ║
   ║  All checks passed. Your environment is verified and     ║
   ║  ready for subsequent modules.                           ║
   ╚══════════════════════════════════════════════════════════╝
   ```

4. **If ANY checks failed:** display a failure summary listing each failed check with its
   Fix_Instructions:

   ```text
   ⚠️  SYSTEM VERIFICATION: FAILURES DETECTED

   Failed checks:
   • <check_name>: <error_summary>
     Fix: <Fix_Instruction>

   Please resolve the issues above and re-run system verification.
   ```

5. **Persist the report** to `config/bootcamp_progress.json` with the following structure:

   ```json
   {
     "module_3_verification": {
       "timestamp": "<ISO 8601 timestamp>",
       "status": "passed|failed",
       "checks": {
         "mcp_connectivity": {"status": "passed|failed", "duration_ms": 0},
         "sdk_initialization": {"status": "passed|failed", "duration_ms": 0},
         "code_generation": {"status": "passed|failed", "file": "verify_pipeline.[ext]"},
         "build_compilation": {"status": "passed|failed", "duration_ms": 0},
         "data_source_registration": {"status": "passed|failed", "sources_registered": ["VERIFY"]},
         "data_loading": {"status": "passed|failed", "records_loaded": 0},
         "results_validation": {"status": "passed|failed", "entities": 0, "matches_verified": 0},
         "database_operations": {"status": "passed|failed", "ops_tested": ["write", "read", "search"]}
       },
       "fix_instructions": []
     }
   }
   ```

   - The `timestamp` field SHALL use ISO 8601 format (e.g., `2026-05-13T10:30:00Z`).
   - The `fix_instructions` array SHALL contain one entry per failed check, each with the check
     name and remediation text.
   - If verification was interrupted, mark unexecuted checks as `"status": "skipped"`.

   Verification runs against synthetic data that is deterministic **by construction** (Step 2), so
   there is no external Truth Set provenance to record for System Verification.

6. **If all checks passed:** proceed to Step 10 (Cleanup).
7. **If any checks failed:** do NOT proceed to cleanup. Advise the bootcamper to fix the issues
   and re-run Module 3 from the beginning.

**Checkpoint:** write step 9 to `config/bootcamp_progress.json`.

## Step 10: Cleanup

Clean up the synthetic verification data from the database. System Verification starts no web service,
so there is nothing to terminate here (any web service belongs to the separate Truth Set
visualization module, which stops its own at its close).

1. **Display the test-only artifact message:**

   ```text
   ℹ️  All files in src/system_verification/ are test-only artifacts.
      Real project work begins in subsequent modules.
      These files are retained for reference.
   ```

2. **Purge verification data from the database:**
   - Remove the synthetic `VERIFY` records loaded in Phase 1 from the Senzing database, using
     generated Senzing SDK code (via `get_sdk_reference` + `sdk_guide`); never direct SQL against
     `database/G2C.db`.
   - After purge, verify zero `VERIFY` entities remain while preserving any other database state.
   - If the purge fails: report a fail status identifying which records could not be removed.
     Provide a Fix_Instruction advising the bootcamper to re-run cleanup or manually reset the
     database.

3. **Retain verification artifacts:** all generated files in `src/system_verification/` remain in
   place for reference.

**Checkpoint:** write step 10 to `config/bootcamp_progress.json`.

## Step 11: Module Close

Complete **System Verification** using the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md`. This module records only itself; the Truth Set
visualization is a separate, standalone module that records itself at its own close
(INV-085/INV-086/INV-087):

1. **Update progress state.** Add `system_verification` to `modules_completed` (a module name token,
   not a number). Set gate 3→4 status to "completed", `current_module` to the next module in
   `selected_modules`, and `current_step` to `null`. All idempotent (do not duplicate).
2. **Append the recap section** to `docs/bootcamp_recap.md`, name-based and append-only (INV-085):
   `## System verification — {timestamp}` (Information Shared, Questions & Responses, Actions Taken,
   Journal) — capture that all 8 checks passed against the synthetic `VERIFY` data. The narrative goes
   in the `### Journal` subsection (the consolidated recap replaces the separate journal file).
3. **Present the completion line + end-of-module summary** (INV-032): `✅ Module complete: System
   verification` and its four-part summary, per `module-completion.md` Step 3.
4. **Transition to the next module:** ask the single transition question; on an affirmative reply,
   produce the next module's start banner, journey map, before/after framing, and step overview per
   the ground rules. (When the Truth Set visualization is selected, the next module is it; otherwise
   it is Data collection.)

👉 **Are you ready to move on to the next module: {next module name}?**

*(Internal: end the turn on this question and wait.)*

**Checkpoint:** write step 11 to `config/bootcamp_progress.json`.

**Success indicator:** ✅ System verification passed or explicitly skipped by the bootcamper. All 8
System Verification checks passed + database purged of the synthetic `VERIFY` data +
`system_verification` completion recorded in the progress file and recap. (The visualization checks
`web_service`/`web_page`, the Truth Set purge, and web-service termination belong to the separate
Truth Set visualization module's close.)
