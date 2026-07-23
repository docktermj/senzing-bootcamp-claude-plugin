# Don't ask the bootcamper Phase C load questions about data the agent generated itself

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In Data processing (Module 6), Phase C (multi-source orchestration), the agent poses two generic
open questions:

> 👉 **Are there load-order dependencies between your data sources?** (Step 13)

> 👉 **Which loading strategy would you like? Reply with a number:** (1) Sequential, (2) Parallel,
> (3) Hybrid. (Step 15)

Both assume the bootcamper knows the structure of the data. But when the business scenario and its
data were **agent-generated** (the bootcamper accepted the Business Case Offer in Module 1 and the
agent chose the CUSTOMERS/REFERENCE/WATCHLIST Truth Set sources), the agent already has full
knowledge of the data and there are no real load-order dependencies. The bootcamper is forced to
guess answers to questions about data they never authored.

## Root cause

Phase C's questions are unconditional — they never branch on data provenance:

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:27` (Step 13,
  dependencies) and `:49-53` (Step 15, loading strategy) are asked of every bootcamper. Phase C
  reads only `mapping_status`, `quality_score`, `load_status`, and the derived `fast_pathed` flag
  (`phaseC-multi-source.md:6-8`, `:13`, `:62`) — never the underlying provenance.

Provenance **is** recorded but not consulted here:

- Module 4 writes a `provenance` field into `config/data_sources.yaml` with values
  `cord`/`own`/`free_data`/`synthesized`/`unknown`
  (`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:209-220`).
- Module 1 records generated scenarios with provenance `cord`/`synthesized`
  (`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:91-94`), and the
  Business Case Offer stamps `docs/business_problem.md` with a `> 🤖 Bootcamp-generated business
  case` marker.
- Only Module 5 consults provenance today, for the fast-path
  (`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md:58`,
  `:71`, `:109` — fast-path offered only for `provenance: cord`). Module 6 uses the derived
  `fast_pathed` boolean but never the underlying `provenance`, and never to skip/auto-answer the
  Phase C questions.

## Proposed change

Make Steps 13 and 15 provenance-aware, following the pattern already implemented for the Phase D
UAT question (`skip-business-user-uat-for-generated-scenario.md`):

- **Agent-generated data** (all loaded sources carry `provenance: cord`/`synthesized` in
  `config/data_sources.yaml`, or the `> 🤖 Bootcamp-generated business case` marker is present in
  `docs/business_problem.md`): the agent should **propose** the answer it already knows rather than
  ask an open question — e.g. state that there are no load-order dependencies between the generated
  sources and recommend a strategy (Sequential for a small dataset), then confirm with a single
  pinned yes/no confirm-style question (INV-056), not the open menu. This keeps the bootcamper in
  control (INV-007 — nothing assumed; a confirm question is still posed) while not asking them to
  re-derive facts the agent authored.
- **Bootcamper-supplied data** (any loaded source with `provenance: own`/`free_data`/`unknown`, or
  no generated marker): ask Steps 13 and 15 exactly as today, pinned verbatim (INV-056), since the
  bootcamper genuinely is the only one who knows the answer.
- State briefly why the proposed answer was pre-filled (INV-012), adding no extra turn beyond the
  one confirm question.

## Acceptance criteria

- [ ] When every loaded source is agent-generated (provenance `cord`/`synthesized`, or the generated marker is present), Steps 13 and 15 present a proposed answer (no dependencies; a recommended strategy) via a single pinned confirm-style question instead of the open dependency/strategy questions.
- [ ] When any loaded source is bootcamper-supplied (`own`/`free_data`/`unknown`, or no marker), Steps 13 and 15 ask the pinned verbatim open questions exactly as today (INV-056).
- [ ] The bootcamper still confirms/overrides the proposal; no answer is silently assumed (INV-007). The pre-fill reason is stated briefly (INV-012) and adds no extra turn.
- [ ] Provenance is read from `config/data_sources.yaml` (the same field Module 5 uses), not re-derived.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — add a provenance guard around Step 13 (`:27`) and Step 15 (`:49-53`), reading `provenance` from `config/data_sources.yaml`.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Agent asks the bootcamper questions about data it generated itself" (2026-07-23, Module: Data processing)
- Priority: Medium
- Related specs: `skip-business-user-uat-for-generated-scenario.md` (same provenance/marker-guard pattern applied to Phase D Step 25 — implemented; follow its approach), `encourage-own-business-case.md` (the generated-scenario marker), `cord-fastpath-load-readiness.md` (Module 5's provenance-driven fast-path).
