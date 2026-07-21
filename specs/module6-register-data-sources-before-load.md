# Module 6 must register DATA_SOURCE codes before loading (SENZ2207 on first load)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 6 (Data processing) is the **real production load** — it loads the bootcamper's
own Senzing-ready data. But the load never registers the data's `DATA_SOURCE` codes in the
Senzing engine config first, so the very first load fails with `SENZ2207` ("data source code
does not exist") for the bootcamper's codes (e.g. `CUSTOMERS`, `VENDORS`) and for fast-pathed
CORD codes. This is the exact failure that Module 3 and Module 3b were given register-before-load
steps to prevent — but the guarantee was never extended to the module that does the actual load.

## Root cause (confirmed)

- No engine-config registration anywhere in Modules 4–7 (grep for `register` /
  `register_data_source` / `SENZ2207` / set-default-config returns nothing but the bootcamp's own
  `config/data_sources.yaml` *registry* and prose about "codes they loaded").
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md:7-18`
  (test load, step 5) and `:33-68` (full load, step 7) run the loading program and handle the
  SENZ9000 license cap, but never register codes before `add_record`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:64` only says
  "unique DATA_SOURCE names match the Module 2 config" — impossible, since Module 2 (SDK setup,
  ordering position 4) runs **before** the bootcamper's data is collected in Module 4, so Module 2
  cannot know those codes. It checks a match against a config that was never populated with them
  (this is finding **M5**, same root cause).
- The Module 5 optional Phase 3 **test load** (`module-05-data-quality-mapping/phase3-test-load.md`)
  likewise loads records with no register-before-load step.
- Contrast the loads that *do* register: `module-03-system-verification/phase1-verification.md:231-279`
  ("Register the Synthetic Data Source Code ... **before** loading, so Step 6 does not fail with
  `SENZ2207`") and `module-03b-truthset-visualization/phase1-visualization.md:92-102`. The plugin's
  own rationale is explicit: "Senzing does not auto-create data source codes, they must be
  registered in the active config first" (`phase1-verification.md:236-237`).
- `INV-083` codifies register-before-load only for the synthetic (Module 3) and Truth-Set
  (Module 3b) loads — the production load in Module 6 is out of its scope, which is itself the gap.

## Proposed change

1. **Add a register-before-load step to Module 6** — in Phase A (build) or at the start of Phase B,
   before both the test load (step 5) and the full load (step 7): collect the distinct `DATA_SOURCE`
   codes present in the data about to be loaded (from the Senzing-ready JSONL in `data/senzing-ready/`
   and/or `config/data_sources.yaml`), register each **idempotently** in the engine config, and set
   it as the new default — mirroring the Module 3 / 3b pattern. Generate the registration code via
   the Senzing MCP tools (`sdk_guide` / `generate_scaffold`), never hand-written, in the language
   read from `programming_language` (INV-080).
2. **Add the same register-before-load step to the Module 5 Phase 3 test load** (`phase3-test-load.md`),
   before it loads records.
3. **Fix `phaseC-multi-source.md:64`** — replace "match the Module 2 config" with a check that the
   codes are registered by the new step (not that Module 2 knew them). (Resolves M5.)
4. **Maintainer decision (surface, do not assume):** whether to **generalize `INV-083`** (or add a new
   invariant) so register-before-load applies to *every* load, not just the synthetic/Truth-Set loads.
   Editing/adding an invariant requires maintainer sign-off per `INVARIANTS.md`; the code fix above
   does not by itself require it and violates no existing invariant.

## Acceptance criteria

- [ ] Before Module 6's test load (Phase B step 5) and full load (step 7), the `DATA_SOURCE` codes present in the data are registered as the default engine config; a first load of the bootcamper's own data does not fail `SENZ2207`.
- [ ] The Module 5 Phase 3 test load registers codes before loading, on the same rule.
- [ ] `phaseC-multi-source.md` no longer claims codes "match the Module 2 config"; it ensures/verifies registration instead.
- [ ] The registration code is MCP-sourced (INV-080), idempotent (re-runs/resumes still pass), and language-parameterized (INV-002).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — add the register-before-load step (build), or reference it.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — register before step 5 (test) and step 7 (full load).
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — fix the `:64` "match the Module 2 config" wording (M5).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — register before the Phase 3 test load.
- `specs/INVARIANTS.md` — only if the maintainer chooses to generalize INV-083 (sign-off required).

## Source

- Final review audit (2026-07-20), findings **H1** (high) and **M5** (medium, merged).
- Priority: High
- Related specs: `module3-synthetic-verification-data.md` / `module3-register-truthset-data-sources.md` (INV-083 register-before-load pattern to mirror), `split-truthset-visualization-into-standalone-module.md`, `mcp-grounding-in-every-skill.md` (INV-080).
