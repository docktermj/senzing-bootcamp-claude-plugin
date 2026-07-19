# Module 3, Phase 3: Report and Close (steps 10–12)

Continues from Phase 2. Follow `../bootcamp-onboarding/ground-rules.md`; `🛑`/`⛔` are internal
directives, never rendered.

> **Pre-advancement verification (agent self-check, internal directive):**
>
> **This check applies only when the Truth Set visualization is selected** (`truthset_visualization`
> in `selected_modules`; always true in Core). When it is **not** selected, Phase 2 was skipped:
> `web_service`/`web_page` are `"skipped"`, no snapshot is required, and you may advance once the
> non-visualization checks pass (Step 10). Otherwise, before offering to advance to Module 4 or
> marking Module 3 complete, the agent MUST verify BOTH the checkpoints and the artifact on disk:
>
> - In `config/bootcamp_progress.json`: `module_3_verification.checks.web_service.status` =
>   `"passed"` and `module_3_verification.checks.web_page.status` = `"passed"`.
> - **The visualization artifact actually exists on disk:** the standalone snapshot written by
>   the bundled app (`docs/visualizations/truthset_verification.html`) is present and non-empty.
>   This is the hard guarantee that the visualization always happened, a checkpoint alone is not
>   sufficient.
> - **The snapshot reflects the loaded Truth Set, not an empty template:** the bundled app's
>   build-only run (9.2) MUST have reported `records_total > 0` on its `Entity model built: …`
>   line, consistent with the Truth Set record count loaded in Step 9 setup (9s.2). A snapshot
>   built from zero records is a blank page and does NOT satisfy INV-077.
>
> If the checkpoints are missing OR the snapshot file does not exist OR the snapshot was built
> from zero records, the agent MUST execute Step 9 immediately (load `phase2-visualization.md`)
> and run the bundled app's build-only snapshot step (9.2) — whose `--records` file
> (`src/system_verification/truthset_data.jsonl`) matches the Truth Set loaded in Step 9 setup
> (9s.2) — so the artifact exists AND is non-empty. Do NOT offer advancement. Do NOT ask the
> module-transition question. Do NOT save progress. Produce the visualization first.

## Step 10: Verification Report Generation

**Visualization completeness (when selected):** when the **Truth Set visualization is selected**
(`truthset_visualization` in `selected_modules`; always true in Core), confirm that
`config/bootcamp_progress.json` contains BOTH `web_service` and `web_page` checkpoint entries
under `module_3_verification.checks` — the visualization module's own checks, tracked **separately
from** the System Verification report below. If either entry is missing or has `"status": "failed"`:

- If missing: STOP. Do not close the module. Return to Step 9 and execute it fully by loading
  `phase2-visualization.md`.
- If failed: note the failure and proceed (failed is different from skipped/missing; it means the
  step was attempted).

When the Truth Set visualization is **not** selected, no `web_service`/`web_page` entries are
expected: proceed with the report.

Generate a structured summary of the System Verification checks.

1. Compile the results from the 8 System Verification checkpoint entries (`mcp_connectivity`,
   `sdk_initialization`, `code_generation`, `build_compilation`, `data_source_registration`,
   `data_loading`, `results_validation`, `database_operations`) into a single Verification Report.
   (The Truth Set visualization is a separate module; its `web_service`/`web_page` checks and the
   visualization artifact are guaranteed by the pre-advancement self-check above, not compiled
   into this report.)

2. For each check, record:
   - Pass or fail status
   - Duration in milliseconds (where applicable)
   - Any relevant metadata (record counts, entity counts, file paths, ports)

3. **If ALL checks passed:** display a success banner:

   ```text
   ╔══════════════════════════════════════════════════════════╗
   ║  ✅ SYSTEM VERIFICATION COMPLETE                        ║
   ║                                                         ║
   ║  All checks passed. Your environment is verified and    ║
   ║  ready for subsequent modules.                          ║
   ╚══════════════════════════════════════════════════════════╝
   ```

4. **If ANY checks failed:** display a failure summary listing each failed check with its
   Fix_Instructions:

   ```text
   ⚠️  SYSTEM VERIFICATION: FAILURES DETECTED

   Failed checks:
   • <check_name>: <error_summary>
     Fix: <Fix_Instruction>

   Please resolve the issues above and re-run Module 3.
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

6. **If all checks passed:** proceed to Step 11 (Cleanup).
7. **If any checks failed:** do NOT proceed to cleanup. Advise the bootcamper to fix the issues
   and re-run Module 3 from the beginning.

**Checkpoint:** write step 10 to `config/bootcamp_progress.json`.

## Step 11: Cleanup

Terminate test services and clean up verification data from the database.

**No separate confirmation gate:** the bootcamper already confirmed they were done exploring at the
end of the Truth Set visualization (Phase 2, Step 9.5), so proceed directly to cleanup — do NOT
re-ask (INV-006). (When the Truth Set visualization did not run, there was no web server and
nothing to confirm.)

1. **Terminate the web service:**
   - Send a termination signal to the verification web service process.
   - Wait up to 5 seconds for the process to exit and release the bound port.
   - If it does not terminate within 5 seconds: force-stop the process and warn the bootcamper
     that the port may need manual release.

2. **Display the test-only artifact message:**

   ```text
   ℹ️  All files in src/system_verification/ are test-only artifacts.
      Real project work begins in subsequent modules.
      These files are retained for reference.
   ```

3. **Purge verification data from the database:**
   - Remove the synthetic `VERIFY` records loaded in Phase 1 — and, when the Truth Set
     visualization ran, its Truth Set records (CUSTOMERS/REFERENCE/WATCHLIST, or the CORD
     substitute's codes) — from the Senzing database, using generated Senzing SDK code (via
     `get_sdk_reference` + `sdk_guide`); never direct SQL against `database/G2C.db`.
   - After purge, verify zero `VERIFY` (and, if applicable, Truth Set) entities remain while
     preserving any other database state.
   - If the purge fails: report a fail status identifying which records could not be removed.
     Provide a Fix_Instruction advising the bootcamper to re-run cleanup or manually reset the
     database.

4. **Retain verification artifacts:** all generated files in `src/system_verification/` remain in
   place for reference.

**Checkpoint:** write step 11 to `config/bootcamp_progress.json`.

## Step 12: Module Close

Complete the module(s) using the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md`. This skill directory hosts **two** selectable
modules — **System verification** (Phase 1/3, always recorded) and, when it ran, **Truth Set
visualization** (Phase 2). Record BOTH as first-class modules, in the order the bootcamper
experienced them (System verification first, then Truth Set visualization), so neither depends on
graduation's reconcile backfill (INV-085/INV-086):

1. **Update progress state.** Add `system_verification` to `modules_completed` (a module name
   token, not a number). **When the Truth Set visualization ran** (`truthset_visualization` in
   `selected_modules` and Phase 2 executed), also add `truthset_visualization` to
   `modules_completed`, placed after `system_verification`. Set gate 3→4 status to "completed" and
   `current_step` to `null`. All idempotent (do not duplicate).
2. **Append the recap section(s)** to `docs/bootcamp_recap.md`, name-based and append-only (INV-085);
   the narrative goes in each section's `### Journal` subsection (the consolidated recap replaces
   the separate journal file):
   - `## System verification — {timestamp}` (Information Shared, Questions & Responses, Actions
     Taken, Journal): capture that all 8 checks passed against the synthetic `VERIFY` data.
   - **When the Truth Set visualization ran:** also `## Truth Set visualization — {timestamp}` (same
     four subsections): capture the Truth Set acquisition/load, the interactive visualization and
     standalone snapshot, and — if screenshots were captured — the embedded
     `![…](docs/visualizations/…png)` image(s) in Actions Taken.
3. Present the end-of-module summary (accomplished, files produced, why it matters, what's next).
4. **Transition to the next module:** ask the single transition question; on an affirmative reply,
   produce the next module's start banner, journey map, before/after framing, and step overview per
   the ground rules.

👉 **Are you ready to move on to the next module: {next module name}?**

*(Internal: end the turn on this question and wait.)*

**Checkpoint:** write step 12 to `config/bootcamp_progress.json`.

**Success indicator:** ✅ System verification passed or explicitly skipped by the bootcamper. All 8
System Verification checks passed — the visualization checks (`web_service`/`web_page`) belong to
the separate Truth Set visualization module and count only when it is selected — database purged of
the synthetic `VERIFY` data (and the Truth Set data when the visualization ran) + web service
terminated (when it ran) + Module 3 completion recorded in the progress file.
