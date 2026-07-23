# Truth Set Visualization, Phase 2: Report and Close

Continues from Phase 1 (`phase1-visualization.md`). Follow `../bootcamp-onboarding/ground-rules.md`;
`🛑`/`⛔` are internal directives, never rendered.

> **Pre-advancement verification (agent self-check, internal directive):**
>
> Before offering to advance to the next module or marking this module complete, the agent MUST
> verify BOTH the checkpoints and the artifact on disk:
>
> - In `config/bootcamp_progress.json`: `truthset_visualization.checks.web_service.status` =
>   `"passed"` and `truthset_visualization.checks.web_page.status` = `"passed"`.
> - **The visualization artifact actually exists on disk:** the standalone snapshot written by the
>   visualization server (`docs/visualizations/truthset_verification.html`) is present and non-empty. This is
>   the hard guarantee that the visualization always happened; a checkpoint alone is not sufficient.
> - **The snapshot reflects the loaded Truth Set, not an empty template:** the visualization
>   server's build-only run (Phase 1, 2.2) MUST have built the entity model from a non-empty record
>   set (`records_total > 0`), consistent with the Truth Set record count loaded in Step 1
>   (1.2). A snapshot built from zero records is a blank page and does NOT satisfy INV-077.
>
> If the checkpoints are missing OR the snapshot file does not exist OR the snapshot was built from
> zero records, the agent MUST execute Steps 1–2 immediately (load `phase1-visualization.md`) and run
> the visualization server's build-only snapshot step (2.2) — whose `--records` file
> (`src/system_verification/truthset_data.jsonl`) matches the Truth Set loaded in Step 1
> (1.2) — so the artifact exists AND is non-empty. Do NOT offer advancement. Do NOT ask the
> module-transition question. Do NOT save progress. Produce the visualization first.

## Step 3: Visualization completeness check

Confirm that `config/bootcamp_progress.json` contains BOTH `web_service` and `web_page` checkpoint
entries under `truthset_visualization.checks` (this module's own checks). If either entry is missing
or has `"status": "failed"`:

- If missing: STOP. Do not close the module. Return to Phase 1 and execute Steps 1–2 fully by loading
  `phase1-visualization.md`.
- If failed: note the failure and proceed (failed is different from skipped/missing; it means the
  step was attempted).

## Step 4: Cleanup

Terminate the web service and purge the Truth Set data from the database.

**No separate confirmation gate:** the bootcamper already confirmed they were done exploring at the
end of Phase 1 (Step 2.5), so proceed directly to cleanup — do NOT re-ask (INV-006).

1. **Terminate the web service:**
   - Send a termination signal to the visualization web service process started in Phase 1 (2.3).
   - Wait up to 5 seconds for the process to exit and release the bound port.
   - If it does not terminate within 5 seconds: force-stop the process and warn the bootcamper that
     the port may need manual release.

2. **Purge the Truth Set data from the database:**
   - Remove the Truth Set records loaded in Phase 1 (CUSTOMERS/REFERENCE/WATCHLIST, or the CORD
     substitute's codes) from the Senzing database, using generated Senzing SDK code (via
     `get_sdk_reference` + `sdk_guide`); never direct SQL against `database/G2C.db`.
   - After purge, verify zero Truth Set entities remain while preserving any other database state.
   - If the purge fails: report a fail status identifying which records could not be removed, with a
     Fix_Instruction advising the bootcamper to re-run cleanup or manually reset the database.

3. **Retain visualization artifacts:** the standalone snapshot
   (`docs/visualizations/truthset_verification.html`), the generated visualization server under
   `src/server/` (when the chosen language is not Python), and any generated load/registration code
   under `src/system_verification/` remain in place for reference.

**Checkpoint:** write to `config/bootcamp_progress.json`.

## Step 5: Module Close

Complete this module using the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md`. Record it as a first-class module in the order the
bootcamper experienced it (immediately after System verification), so it does not depend on
graduation's reconcile backfill (INV-085/INV-086/INV-087):

1. **Update progress state.** Add `truthset_visualization` to `modules_completed` (a module name
   token, not a number), placed after `system_verification`. Set `current_module` to the next module
   in `selected_modules` and `current_step` to `null`. All idempotent (do not duplicate).
2. **Append the recap section** to `docs/bootcamp_recap.md`, name-based and append-only (INV-085):
   `## Truth Set visualization — {timestamp}` with the four subsections (Information Shared,
   Questions & Responses, Actions Taken, End-of-Module Summary): capture the Truth Set acquisition/load, the
   interactive visualization and standalone snapshot, and — if screenshots were captured — the
   embedded `![…](docs/visualizations/…png)` image(s) in Actions Taken.
3. **Present the completion line + end-of-module summary** (INV-032):
   `✅ Module complete: Truth Set visualization` and its four-part summary, per `module-completion.md`
   Step 3. (This module's module-start banner/journey/before-after/step-overview were already shown at
   its module start in Phase 1, so only its close is presented here.)
4. **Transition to the next module:** ask the single transition question (once), then on an
   affirmative reply produce the next module's start banner, journey map, before/after framing, and
   step overview per the ground rules.

👉 **Are you ready to move on to the next module: {next module name}?**

*(Internal: end the turn on this question and wait.)*

**Checkpoint:** write to `config/bootcamp_progress.json`.

**Success indicator:** ✅ The standalone snapshot exists (built from a non-empty Truth Set) + the
live app served its endpoints + the web service is terminated + the Truth Set data is purged +
`truthset_visualization` is recorded in `modules_completed` with its own recap section.
