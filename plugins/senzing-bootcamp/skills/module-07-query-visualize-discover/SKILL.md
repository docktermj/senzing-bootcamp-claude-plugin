---
name: module-07-query-visualize-discover
description: Bootcamp Module 7: Query, Visualize, and Discover. Use when the bootcamper starts or resumes Module 7, or needs to query resolved entities, visualize them, and explore results against the business problem.
---

# Module 7: Query, Visualize, and Discover

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, no direct SQL, file placement, checkpointing). Execute every numbered step and
sub-step one at a time, in order. Never skip, combine, or abbreviate a step containing a 👉
question. This has the same absolute precedence as a ⛔ mandatory gate.

**First:** Read `config/bootcamp_progress.json`, then (per ground-rules) show the module start
banner, journey map, and before/after framing before any module work.

**Before/After:** Your data is loaded and entities are resolved, but you haven't examined the
results yet. After this module you'll have query programs that answer your business questions,
visualizations of your resolved entities, and (optionally) a tour of Senzing's advanced
discover capabilities (why, how, relationship networks).

**Prerequisites:**

- ✅ Module 6 complete (all sources loaded, single or multi-source).
- ✅ No critical loading errors.

**Success indicator:** ✅ Query programs created and tested + queries answer the business
problem + visualizations offered (entity graph and results dashboard) + Discover phase
completed or explicitly skipped.

## No direct SQL (module-critical)

This module is all about examining resolved entities. NEVER generate direct SQL against the
Senzing database (`database/G2C.db`) or its internal tables (`RES_ENT`, `OBS_ENT`,
`DSRC_RECORD`, `LIB_FEAT`, `RES_REL`, etc.). Every entity operation goes through the SDK:

- **Search, get entity, why-matched, how-built, network, path** → generate SDK code via
  `get_sdk_reference` (flags and method signatures) plus `sdk_guide` / `reporting_guide`
  (topic `entity_views` for get/why/how patterns, topic `graph` for network/path patterns).
- **Counts, stats, quality, reporting and visualization data** → `reporting_guide` (topics
  `reports`, `quality`, `evaluation`, `dashboard`, `graph`).

Reconciliation note: the Kiro source referred to `search_by_attributes`, `get_entity`,
`why_entities`, `how_entity`, `why_records`, `find_network`, `find_path`, and
`get_entity_by_record_id` as if they were callable tools. The current Senzing MCP server does
NOT expose direct entity-query tools. These are SDK **methods**: the agent generates SDK code
that calls them, sourcing flags and signatures from `get_sdk_reference` and code patterns from
`sdk_guide` / `reporting_guide`. Never fabricate SDK method names; always confirm via MCP.

## Error handling

When the bootcamper hits an error during this module:

1. **SENZ error code** (message contains `SENZ` + digits, e.g. `SENZ2027`): call
   `explain_error_code(error_code="<code>", version="current")` and present the explanation and
   recommended fix. If it returns nothing, continue to step 2.
2. Look up the symptom via `search_docs`, then present the matching fix (the full
   `common-pitfalls` reference and its Troubleshooting-by-Symptom table are a later porting
   phase).

## Phases

- **Phase 1: Query and Visualize** (steps 1–3d): `phase1-query-visualize.md`
- **Phase 2a: Discover, Part A** (steps 4a–4c): `phase2-discover.md`
- **Phase 2b: Discover, Part B** (steps 4d–4e): `phase2b-discover.md`

Read `current_step` from `config/bootcamp_progress.json` (an integer, or a sub-step string like
`"3b"` or `"4a"`) and resume at the right phase and sub-step. Do not re-run completed steps.
For the Discover phase, also check `module_7_query.steps.<key>` for which 4x sub-steps are
already checkpointed.

## Module position

Module 7 is the end of the Core track. The Query Completeness Gate at the end of Phase 1 is the
module transition: Path A (full bootcamp) proceeds to Module 8 (Performance Testing); Paths B/C
(shorter paths) may stop here with working query programs. Preserve that gate exactly.
