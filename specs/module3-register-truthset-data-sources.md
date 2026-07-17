# Register the TruthSet data sources before Module 3's data-loading step

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Every Module 3 run loads the Senzing TruthSet (CUSTOMERS, REFERENCE, WATCHLIST)
at Step 6 (Data Loading), but the default engine config seeded earlier has **no
data sources registered**. So the very first load attempt fails for every
bootcamper with:

```text
SENZ2207: Data source code [CUSTOMERS] does not exist
```

(likewise for REFERENCE and WATCHLIST). This is not a data-dependent edge case:
the TruthSet is the only dataset used in this module and its three source codes
are fixed and known in advance, so 100% of Module 3 runs hit it on the first
pass and must recover ad hoc (a hand-rolled `register_data_sources` step via
`SzConfig.register_data_source` + `sdk_guide(topic='configure')`) before the load
succeeds.

## Root cause (confirmed)

`plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`
has no data-source registration anywhere in the pipeline. The steps run:

- Step 3 — SDK Initialization (`:220-249`)
- Step 4 — Code Generation: `generate_scaffold(workflow='full_pipeline')` → saves
  `src/system_verification/verify_pipeline.[ext]` (`:250-276`)
- Step 5 — Build/Compile (`:278-310`)
- **Step 6 — Data Loading**: executes `verify_pipeline.[ext]` directly against the
  seeded config (`:312-339`)

Nothing between Steps 3 and 6 calls `register_data_source` for CUSTOMERS /
REFERENCE / WATCHLIST or commits a new default config that carries them. A
repo-wide grep for `register_data_source` / `SENZ2207` under
`skills/module-03-system-verification/` returns nothing — the generated
`full_pipeline` scaffold assumes the sources already exist, and the config seeded
in Module 2 is empty of data sources. Step 6 only documents SENZ error handling
generically (`:322-323`, `explain_error_code`), so the always-true precondition is
handled as a surprise error instead of a prerequisite step.

## Proposed change

Add an explicit data-source registration step to `phase1-verification.md` that
runs **before** Step 6's data load — e.g. a new "Step 5a: Register TruthSet Data
Sources" between Build (Step 5) and Data Loading (Step 6), or as an explicit
sub-step at the head of Step 6 executed before `verify_pipeline` runs:

- Register the TruthSet source codes **CUSTOMERS, REFERENCE, WATCHLIST** via
  `SzConfig.register_data_source` and commit the resulting config as the new
  default (`SzConfigManager` set-default / register-config flow), so the load runs
  against a config that already knows the three codes.
- **Generate the registration code from the MCP server**, not by hand — per Agent
  Rule 7 "MCP as source of truth" (`phase1-verification.md:100`): obtain it via
  `sdk_guide(topic='configure')` / `generate_scaffold` in the bootcamper's chosen
  language, so it stays correct and language-agnostic. Save it under `src/` (e.g.
  `src/system_verification/register_data_sources.[ext]`, per INV-018).
- Make the step idempotent: registering an already-present source code must not
  fail the step (re-running Module 3 or resuming mid-module must still succeed).
- Add a checkpoint to `config/bootcamp_progress.json` recording the registration
  outcome (mirroring the existing per-step checkpoints), and reflect the newly
  registered sources in `config/data_sources.yaml` (INV-050).
- Keep Step 6's generic SENZ error handling as a fallback, but SENZ2207 for the
  three TruthSet codes must no longer occur on the first pass.

This preserves the mandatory TruthSet visualization (INV-038): the load that feeds
it now succeeds on the first attempt.

## Acceptance criteria

- [ ] A fresh Module 3 run against a newly seeded (empty) default config loads the
      TruthSet at Step 6 without any SENZ2207 for CUSTOMERS/REFERENCE/WATCHLIST on
      the first attempt — no ad-hoc registration recovery required.
- [ ] The registration step commits a new default config containing the three
      TruthSet source codes before the load runs, and records the outcome in
      `config/bootcamp_progress.json` and `config/data_sources.yaml`.
- [ ] The registration code is produced via the Senzing MCP server (not
      hand-written) and lives under `src/` (INV-018).
- [ ] Re-running Module 3 (sources already registered) does not fail the step
      (idempotent).
- [ ] The mandatory TruthSet web-app visualization (INV-038) still runs, now fed by
      a first-attempt-successful load.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic across every
      supported language (Python/Java/C#/Rust/TypeScript) — the registration code is
      MCP-generated per the chosen language (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`
  — add the data-source registration step (register CUSTOMERS/REFERENCE/WATCHLIST +
  commit a new default config, MCP-generated) before Step 6's data load; add its
  progress checkpoint; keep Step 6's generic SENZ handling as a fallback.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Module 3 Step 6 always hits
  SENZ2207 because TruthSet data sources are never registered first" (2026-07-17,
  Module 3)
- Priority: Medium
- Related specs: none (no existing spec covers Module 3 data-source registration).
  Upholds INV-038 (mandatory TruthSet visualization); respects INV-018 (code under
  `src/`) and INV-050 (project layout).

## Invariants introduced

- `INV-068` — Module 3 MUST register the TruthSet data source codes (CUSTOMERS,
  REFERENCE, WATCHLIST for the standard TruthSet, or the codes present in the
  acquired data for the Step 2a substitute) and commit them as the default engine
  config **before** the Step 6 data load runs, so the load never fails with
  SENZ2207 for those codes on the first attempt (recorded in `specs/INVARIANTS.md`).
