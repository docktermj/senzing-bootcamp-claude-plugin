# Module 6 must load/validate fast-pathed CORD sources from their registry file_path

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The CORD fast-path (INV-040/041) lets a CORD / already-Senzing-ready source skip Module 5 mapping:
`phase1-quality-assessment.md` step 5a sets `mapping_status: complete` + `fast_pathed: true` and
**keeps `file_path` pointing at the original `data/raw/` file** (no transformation). But Module 6
has zero awareness of that: it assumes every load-ready file lives in `data/senzing-ready/`.

- The Phase C conditional gate counts sources with `mapping_status: complete`
  (`phaseC-multi-source.md:6`), so a fast-pathed CORD source participates in multi-source orchestration.
- Phase C step 16 pre-load validation then requires "all JSONL files exist in `data/senzing-ready/`"
  (`phaseC-multi-source.md:48`) — the fast-pathed source's file is in `data/raw/`, so it is falsely
  flagged missing and the agent is told to "Fix failures before proceeding."
- Phase A's "Identify the input data" list (`phaseA-build-loading.md:86`) only names
  `data/senzing-ready/` as mapped-output, never the fast-pathed raw file.

A plugin-wide grep confirms Module 6 contains **zero** references to `fast_pathed` or `data/raw`.
So the CORD fast-path — an invariant behavior (INV-040) — breaks at load time. (INV-003 coherence.)

Bundled minor (`C2`): `phase1-quality-assessment.md:56-58` had a backwards "Module 2 (SDK setup)"
reference and promised *any* Entity-Specification-compliant source could "proceed directly to Module
6," but the fast-path is CORD-only (step 6: "Never present the fast-path offer for sources with
provenance other than `cord`"), so a non-CORD compliant source still goes through Phase 2 mapping.

## Root cause

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:48` — validation hardcodes `data/senzing-ready/`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md:84-88` — input-location list omits fast-pathed `data/raw/` sources.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md:56-58` — backwards module ref + over-broad "directly to loading" promise.

## Proposed change

1. **Phase A step 2:** resolve each source's load file from its registry `file_path` in
   `config/data_sources.yaml` rather than assuming a fixed directory — `data/senzing-ready/` for
   mapped sources, `data/raw/` for `fast_pathed: true` CORD / already-Senzing-ready sources.
2. **Phase C step 16:** validate each source's load file at its registry `file_path`
   (senzing-ready for mapped; raw for fast-pathed) is present and non-empty.
3. **Module 5 step 5 classification:** drop the backwards "Module 2" reference and scope the
   direct-to-loading promise to CORD/fast-pathed sources; other compliant sources continue to Phase 2.

## Acceptance criteria

- [x] Module 6 (Phase A input + Phase C step-16 validation) resolves each source's load file from its registry `file_path`, honoring `data/raw/` for `fast_pathed: true` sources.
- [x] A fast-pathed CORD source is no longer falsely flagged "missing" by Phase C pre-load validation.
- [x] Module 5's compliance classification no longer references "Module 2 (SDK setup)" nor overpromises direct-to-loading for non-CORD compliant sources.
- [x] Upholds the CORD fast-path (INV-040/041); consistent with INV-084 (mapped output in `data/senzing-ready/`). No new invariant — Module 6 is brought into line with existing INV-040.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md`
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`

## Source

- Audit (fourth deep-dive, final review), 2026-07-19 — CORD fast-path load-readiness coherence gap; maintainer chose "fix all verified findings".
- Priority: Medium.
- Related specs: `specs/rename-transformed-to-senzing-ready.md`.
