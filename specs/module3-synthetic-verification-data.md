# Module 3 System Verification uses synthetic records, not the TruthSet; confine TruthSet + visualization to the Truth Set visualization module

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 3 (System Verification) acquires the Senzing TruthSet via MCP, loads it, validates
results against it, and runs the bundled Truth Set visualization web app (Step 9). But the
TruthSet visualization is *already* its own selectable module (`truthset_visualization`,
Module 3 Phase 2) that runs right after verification — so System Verification duplicates
that module's scope. The bootcamper asked that System Verification not touch the TruthSet
or the visualization at all: instead it should generate a handful of synthetic records
designed to resolve into a single entity and confirm that resolution happens. The
Verification Report should drop `truthset_acquisition`, `web_service`, and `web_page`;
`data_source_registration`, `data_loading`, and `results_validation` should run against
the generated data. All other checks (MCP connectivity, SDK init, code generation,
build/compile, database operations) stay as-is.

Relatedly, the bootcamper reinforced that Module 3's verification/test programs must always
be written in the programming language chosen during Bootcamp preparation (no silent
fallback to another language). No defect was observed this session (Python was used
correctly), but the guarantee should be explicit.

## Root cause

The TruthSet is wired into Phase 1's verification pipeline by design, and Phase 2 depends
on Phase 1 having loaded it:

- **TruthSet acquisition** is Step 2 / graceful-degradation Step 2a:
  `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md:142-218`.
- **Agent Rules** hardcode "TruthSet only / no dataset choice":
  `phase1-verification.md:86-92`.
- **Data-source registration, load, results validation** target the TruthSet: Step 5a
  (`:312-361`), Step 6 (`:363-392`), Step 7 (`:394-431`), Step 8 (`:433-465`).
- **Success criteria** list 11 checks incl. `truthset_acquisition`, `web_service`,
  `web_page`: `phase1-verification.md:472-486`.
- **Verification Report** compiles the same 11 checks and states TruthSet provenance:
  `phase3-report-close.md:49-52`, `:95-105`, `:116-121`.
- **Phase 2 (the visualization module) depends on Phase 1 loading the TruthSet:**
  `phase2-visualization.md:9-10` ("Prerequisites: Phase 1 Steps 1-8 complete … TruthSet
  data loaded and validated") and Step 9.3 builds the entity model "from the loaded
  records" (`:37-39`). So removing the TruthSet from Phase 1 breaks Phase 2's prerequisite
  — the `truthset_visualization` module must then acquire/register/load the TruthSet
  itself.
- **Language** is already required from the bootcamper's choice: `SKILL.md:25-26`
  ("Language: Use the bootcamper's chosen language …") and per-step `[ext]` usage, so
  item 8 is a hardening/confirmation, not a bug.

## Conflict with invariants (must be reconciled, not silently overridden)

- **INV-068** — "Module 3 MUST register the TruthSet data source codes (CUSTOMERS,
  REFERENCE, WATCHLIST …) before the Step 6 data load, so the load never fails with
  SENZ2207." Replacing the TruthSet with synthetic data changes *which* codes are
  registered (the synthetic records' codes), not the underlying guarantee (register the
  verification data's source codes before load). This is a **meaning change** → the
  implementing session must record an amended/new invariant (register the source codes
  present in Module 3's synthetic verification data) and mark INV-068 superseded.
- **INV-038 / INV-077** — the guaranteed Truth Set web-app visualization is delivered by
  the selectable `truthset_visualization` module. This spec does **not** remove that
  guarantee; it *relocates* the TruthSet acquisition/registration/load and the Step 9
  visualization entirely into that module, and removes them from System Verification. The
  "Step 9 is unconditional whenever Module 3 runs" language
  (`phase1-verification.md:74-80`, `:467-470`; `phase2-visualization.md:12-30`) must be
  reconciled so it is tied to the `truthset_visualization` selection, not to System
  Verification.

## Proposed change

1. **Phase 1 uses synthetic deterministic records.** Replace TruthSet acquisition
   (Steps 2/2a) with generation of a small synthetic record set designed to resolve into a
   single entity (e.g. two-plus records for the same person with matching name/DOB/address
   plus at least one distractor), written under `src/system_verification/`. Rewrite the
   Agent Rules (`:86-92`) from "TruthSet only" to "generated synthetic verification data".
2. **Register the synthetic data's source code(s)** (Step 5a) before load, load them
   (Step 6), and validate they resolve to the expected single entity (Step 7). Keep the
   generic SENZ handling. Reconcile INV-068 accordingly.
3. **Drop the TruthSet/visualization checks from System Verification's report:** remove
   `truthset_acquisition`, `web_service`, and `web_page` from the success criteria
   (`phase1-verification.md:472-486`) and the Verification Report (`phase3-report-close.md`).
   Keep `mcp_connectivity`, `sdk_initialization`, `code_generation`, `build_compilation`,
   `data_source_registration`, `data_loading`, `results_validation`, `database_operations`.
4. **Move TruthSet work into the Truth Set visualization module.** Make
   `phase2-visualization.md` self-contained: when `truthset_visualization` is selected, it
   acquires (MCP-first, with the existing sanctioned fallback), registers, and loads the
   TruthSet itself, then visualizes it — since Phase 1 no longer does. Remove the
   dependency on Phase 1's TruthSet load (`phase2-visualization.md:9-10`, `:37-39`) and the
   Step-9-owed/standalone-demo coupling in Phase 1's opt-out gate
   (`phase1-verification.md:37-77`) as needed. INV-077's "produced whenever selected"
   guarantee stays intact.
5. **Language hardening (item 8).** Make Module 3's code-generation and verification-script
   steps explicitly read the chosen `programming_language` from
   `config/bootcamp_preferences.yaml` (persisted in Bootcamp preparation, INV-075) at each
   generation step, so the language never silently falls back to a different one.

## Acceptance criteria

- [ ] System Verification (Phase 1) generates synthetic records that deterministically resolve into a single entity and validates that resolution; it makes no MCP TruthSet fetch, no sanctioned-fallback fetch, and no CORD substitute.
- [ ] The Verification Report and success criteria drop `truthset_acquisition`, `web_service`, and `web_page`; `data_source_registration`, `data_loading`, and `results_validation` run against the generated data; the remaining checks are unchanged.
- [ ] The Truth Set visualization module (`truthset_visualization`) still produces the guaranteed visualization when selected (INV-077), now acquiring/registering/loading the TruthSet itself rather than relying on Phase 1.
- [ ] INV-068 is reconciled (an amended/new invariant records "register the synthetic verification data's source codes before load"); no bootcamper-facing check references a TruthSet inside System Verification.
- [ ] Module 3's generated verification code is written in the language read from `config/bootcamp_preferences.yaml`, never a hardcoded default (item 8).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — replace TruthSet acquisition (`:142-218`) with synthetic-record generation; rewrite Agent Rules (`:86-92`); retarget Steps 5a/6/7/8 (`:312-465`); update success criteria (`:472-486`); reconcile opt-out/Step-9 coupling (`:37-80`, `:467-470`).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — drop `truthset_acquisition`/`web_service`/`web_page` and TruthSet-provenance reporting (`:49-52`, `:95-105`, `:116-121`).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — make the Truth Set visualization module self-contained (acquire/register/load the TruthSet itself); remove the Phase-1-load prerequisite (`:9-10`, `:37-39`).
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — reconcile the module overview, TruthSet-source section, and language note (`:25-26`, `:34-38`, `:61-107`).
- `specs/INVARIANTS.md` — reconcile INV-068 (synthetic verification data) and the INV-038/INV-077 module boundary.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "System Verification (Module 3) should not use the TruthSet at all" (2026-07-18, Module: system_verification); "Module 3 test programs must use the bootcamper's chosen programming language" (2026-07-18, system_verification).
- Priority: Medium.
- Related specs: `module3-register-truthset-data-sources.md` (INV-068, reconciled here), `customizable-module-selection.md` (INV-077, the Truth Set visualization module), `vendor-d3-offline-visualization.md` / `fix-truthset-snapshot-empty.md` (the visualization that now owns the TruthSet).

## Invariants introduced

- `INV-082` — System Verification (Module 3, Phase 1) verifies with synthetic, deterministic-by-construction records and never acquires/loads/visualizes the Truth Set; the Truth Set is used exclusively by the Truth Set visualization module (Phase 2). Supersedes the Truth-Set coupling of INV-038/INV-068 (recorded in `specs/INVARIANTS.md`).
- `INV-083` — In Module 3, the source code(s) of the data about to be loaded MUST be registered as the default engine config before each load (synthetic `VERIFY` in Phase 1; Truth Set codes in Phase 2), so no load fails with `SENZ2207`. Supersedes INV-068 (recorded in `specs/INVARIANTS.md`).
