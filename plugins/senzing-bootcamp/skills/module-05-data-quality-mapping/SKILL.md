---
name: module-05-data-quality-mapping
description: 'Bootcamp Module 5: Data Quality & Mapping. Use when the bootcamper starts or resumes Module 5, or needs to assess data quality and map records to the Senzing Entity Specification.'
---

# Module 5: Data Quality & Mapping

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, file placement, checkpointing). Execute every numbered step one at a time, in
order. Never skip, combine, or abbreviate a step containing a 👉 question: this has the same
absolute precedence as a ⛔ mandatory gate, and no internal reasoning can override it.

**First:** Read `config/bootcamp_progress.json`, then (per ground-rules) show the module start
banner, journey map, before/after framing, and a brief numbered overview of this module's steps, before any module work.

**Before/After:** You have raw data files but don't know if Senzing can use them directly.
After this module, each source is scored for quality, categorized, and transformed into
Senzing JSON: validated and ready to load.

**Prerequisites:** ✅ Module 4 complete (data sources collected, files in `data/raw/`).

**Success indicator:** ✅ Each data source evaluated (sources evaluated, mapped) +
transformation programs tested + output validated with quality >70%.

## Reference notes

- **Quality scoring methodology:** When a bootcamper asks how a score was calculated, what
  each dimension measures, or what a threshold means, explain it directly using the dimension
  definitions in Phase 1 (field completeness, format consistency, duplicate rate). The
  standalone `QUALITY_SCORING_METHODOLOGY` guide is a later porting phase; for now use
  `search_docs` for any Senzing-specific quality guidance.
- **Multi-language data:** If a source contains non-Latin characters (Chinese, Arabic,
  Cyrillic, etc.), call `search_docs(query="globalization")` for current guidance on UTF-8
  encoding, non-Latin character support, cross-script name matching, and multi-language data
  quality best practices. Never answer from training data.

## Error handling

When the bootcamper hits an error during this module:

1. **SENZ error code** (message contains `SENZ` + digits, e.g. `SENZ2027`): call
   `explain_error_code(error_code="<code>", version="current")` and present the explanation and
   recommended fix. If it returns nothing, continue to step 2.
2. Present the matching pitfall/fix for this module (full `common-pitfalls` reference is a
   later porting phase; for now, use `search_docs` to look up the symptom).

## Phases

- **Phase 1: Quality Assessment** (steps 1–7): `phase1-quality-assessment.md`
  (includes a Senzing-readiness check and fast-path-to-loading offer for eligible sources).
- **Phase 2: Data Mapping** (steps 8–20): `phase2-data-mapping.md`.
- **Phase 3: Test Load and Validate (Optional)** (steps 21–26): `phase3-test-load.md`.

Read `current_step` from `config/bootcamp_progress.json` and resume at the right phase. During
mapping, also read any `config/mapping_state_[datasource].json` checkpoint to resume a
per-source `mapping_workflow` run where it left off.
