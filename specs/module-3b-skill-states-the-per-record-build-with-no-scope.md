# Module 3b's SKILL.md states the per-record build with no scope

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-289 requires that where a reference implementation is reused by instruction, any part
of it whose correctness depends on the scale or shape of the data it was written against is
named **at the point of reuse** — and the invariant states explicitly that this *"binds
BOTH ends of a reuse, not only the one that changes strategy."*

`module-03b-truthset-visualization/phase1-visualization.md` was brought into line when
INV-289 was registered on 2026-09-02. Its **sibling `SKILL.md` was not**, and that is the
file a guide reads first to orient.

## Root cause

`module-03b-truthset-visualization/SKILL.md` carries both halves of the reuse and scopes
neither:

- `:33` — *"The visualization server is built in the chosen language, **modeled on the
  shipped reference `scripts/senzing_viz_server.py`**"*
- `:118` — the same instruction again, in the phase overview
- `:105` — *"Counts, statistics, and visualization data come from `reporting_guide` and from
  the visualization server's entity-model build (**one `get_entity_by_record_id` per
  record**), never from direct SQL."*

`:105` states the build flatly, as a property of how this module gets its data, with no
indication that it is scoped to the Truth Set. A guide that reads SKILL.md — reuse
instruction and build strategy, adjacent, both unqualified — has everything it needs to
carry a per-record server into Module 7 and nothing telling it not to.

⚠️ **`:105` is not wrong in its own context.** Module 3b *is* the Truth Set, so one call
per record is correct there. INV-289's requirement is that the **scope be named**, which is
exactly what the fix to `phase1-visualization.md` added and what SKILL.md still lacks.

## Proposed change

Add the scope to `:105`, or a pointer to the note now in `phase1-visualization.md:211`.
A pointer is probably right: the full reasoning (round trips, and entities a records-file
build cannot see) belongs at the step that builds, and duplicating it in the overview is
the repetition-that-drifts class.

⛔ **Do not restate the reasoning in both files.** INV-183 puts a rule where it is used;
the overview needs the *fact that a scope exists* and where to read it.

## Acceptance criteria

- [ ] `module-03b/SKILL.md` no longer states the per-record build without indicating it is
      Truth-Set-scoped.
- [ ] The reasoning is stated once, at the step, and referenced from the overview — not
      duplicated.
- [ ] A guard asserts both ends of the module-03b reuse, extending
      `BothEndsOfTheReuseNameTheScaleScope` rather than adding a parallel test.
- [ ] Negative-controlled: removing the scope from SKILL.md fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/SKILL.md`
- `tests/test_visualization_model_build_scales.py`

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-02
  (`Source: self-observed (assistant retrospective)`), sweeping INV-289's sites the day it
  was registered.
- Priority: Medium — the invariant was registered *with* a both-ends clause and is unmet at
  one of its own sites, which is the INV-097 / INV-060 shape (registered, partly
  implemented, invisible to the suite for weeks).
- MCP re-check: n/a (no Senzing fact) — internal consistency between two files in one skill.
- Upstream: not applicable.
- Related specs: `visualization-model-build-does-one-get-entity-per-record`.
