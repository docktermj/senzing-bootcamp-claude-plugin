# Third deep-dive: clear minor fixes (garbled question, name-token drift, doc sync, tree labels)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

The third ("be extra picky") deep-dive surfaced a cluster of small, unambiguous defects:

1. **Garbled instruction (F2)** — `module-07-query-visualize-discover/phase1-query-visualize.md`
   had a truncated `ELSE … ask , ` line (dangling comma, no question), leaving the else-branch's
   open-ended question ungrounded.
2. **Unmarked branch question (F1)** — the "Rejects all derived requirements" branch inlined the
   fallback question as a quoted string with no `👉`, so the same question existed once with `👉`
   (else branch) and once without, risking a turn that never ends on the question.
3. **Name-token drift** — the same file said `Set current_module to 5`, but `current_module` holds
   a module **name token** everywhere else (e.g. `phase2-visualization.md:41` sets
   `truthset_visualization`), never a catalog number (INV-086).
4. **Doc sync drift** — `docs/model-selection.md`'s stage table omitted "Bootcamp preparation" from
   the Sonnet/medium row, while its authoritative mirror in `ground-rules.md:239` includes it; the
   table explicitly says "Keep this table in sync with the mirror in `ground-rules.md`".
5. **Mislabeled tree comment** — the INV-050 project-layout tree annotated
   `src/system_verification/` as "Pipeline verification (truth set)", but System verification runs
   on **synthetic** `VERIFY` data and does not touch the Truth Set (INV-086/INV-077); the Truth Set
   belongs to the separate visualization module.
6. **Stale tree entry** — the INV-050 tree listed `docs/bootcamp_journal.md` with no note that the
   consolidated `docs/bootcamp_recap.md` superseded it (INV-085).

## Root cause

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:33-39` — garbled else line + unmarked branch question.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md:164` — `current_module` set to `5` (number, not name token).
- `plugins/senzing-bootcamp/docs/model-selection.md:92` — stage table row missing "Bootcamp preparation".
- `specs/INVARIANTS.md` INV-050 tree — `system_verification/` comment mislabeled "(truth set)"; `bootcamp_journal.md` unannotated.

## Proposed change

Maintainer decision (2026-07-19): **fix the clear minors now.**

1. Rewrite the else-branch so both the "Rejects all" branch and the ELSE branch route to the single
   `👉 What questions do you need to answer with your data?` question (fixes F1 + F2; one
   turn-ending question).
2. `Set current_module to 5` → `Set current_module to data_quality_mapping` (Module 5's name token),
   with a note that `current_module` holds a name token, not a catalog number (INV-086).
3. Add "Bootcamp preparation" to the Sonnet/medium row of `model-selection.md`, matching the
   `ground-rules.md` mirror.
4. INV-050 tree: reword the `system_verification/` comment to "Pipeline verification (synthetic
   VERIFY data) + Truth Set viz artifacts"; annotate `bootcamp_journal.md` as
   "(legacy; superseded by the consolidated bootcamp_recap.md, INV-085)".

**Examined but intentionally not changed — the "hardcoded 500-record" flag.** On close inspection
the built-in-evaluation-license figure in `module-02-sdk-setup/SKILL.md` is already handled
correctly: lines 341/361 caveat it as "the current published value; confirm it against the Senzing
MCP server," instruct retrieving the live value each session, and state "Never substitute a
hardcoded or remembered figure." The `<500` tier boundary in `module-06 phaseA` is an explicitly
illustrative "Example range" for classifying production volume. Neither is a naive hardcode; both
already conform to the MCP-grounding invariants (INV-011-family / tool-first). No change made — the
flag did not survive verification.

## Acceptance criteria

- [x] The garbled `ask , ` line is gone; both branches route to the single `👉` fallback question, and exactly one turn-ending question remains.
- [x] `current_module` is set to the `data_quality_mapping` name token (no catalog number).
- [x] `model-selection.md`'s stage table includes "Bootcamp preparation" in the Sonnet/medium row, matching `ground-rules.md`.
- [x] The INV-050 tree comment for `system_verification/` reflects synthetic VERIFY data (not "truth set"); `bootcamp_journal.md` is annotated as legacy/superseded.
- [x] The 500-record figure is left as-is (already MCP-grounded); the decision is recorded here.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — F1/F2 + name token.
- `plugins/senzing-bootcamp/docs/model-selection.md` — Bootcamp preparation added to the stage table.
- `specs/INVARIANTS.md` — INV-050 tree comment/annotation clarifications.

## Source

- Audit (third deep-dive, "be extra picky"), 2026-07-19 — minor findings; maintainer chose "Fix the clear minors now".
- Priority: Low.
- Related specs: `specs/truthset-visualization-full-apparatus.md`, `specs/align-invariants-cord-and-optin.md`.
