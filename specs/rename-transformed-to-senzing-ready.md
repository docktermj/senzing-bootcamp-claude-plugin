# Rename the mapping-output directory `data/transformed` to `data/senzing-ready`

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 5 writes its Senzing-Entity-Specification-compliant mapping output to
`data/transformed/`. The bootcamper asked to rename it to `data/senzing-ready/` because
the name should describe what the data *is* (ready to load into Senzing) rather than what
was done to it (transformed) — `senzing-ready` is easier to comprehend and aligns with the
"Senzing-ready data" language already used elsewhere.

## Root cause

Not a defect — `data/transformed` is the mapping-output convention throughout the plugin
and is pinned in the layout invariant:

- Layout tree: `specs/INVARIANTS.md` INV-050 lists `data/transformed/` ("Senzing-mapped
  JSONL output").
- Skill references (from `grep -rn "data/transformed"`):
  - `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` (7 references — the mapper output paths),
  - `plugins/senzing-bootcamp/skills/module-06-data-processing/SKILL.md` (2), `.../phaseA-build-loading.md` (1), `.../phaseC-multi-source.md` (1) — downstream loaders read the mapped output,
  - `plugins/senzing-bootcamp/skills/graduation/SKILL.md` (1),
  - `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` (1).

INV-040/INV-041 already speak of "Senzing-ready" data conceptually, so the rename brings
the directory name into line with existing terminology.

## Conflict with invariants (reconcile, don't silently override)

- **INV-050** pins the project layout tree, which contains `data/transformed/`. Renaming
  the directory changes that tree — a **meaning change**. The implementing session must
  update the INV-050 tree to `data/senzing-ready/` (with the same "Senzing-mapped JSONL
  output" comment) and record the reconciliation per the invariants-maintenance rules.

## Proposed change

- Rename the mapping-output directory from `data/transformed` to `data/senzing-ready`
  everywhere it appears: the Module 5 mapping phase (`phase2-data-mapping.md` mapper/output
  paths and any `data/transformed` mentions in that module), the Module 6 loaders that read
  the mapped output (`module-06` SKILL/phaseA/phaseC), graduation (`graduation/SKILL.md`),
  and the visualization server (`scripts/senzing_viz_server.py`).
- Update INV-050's layout tree to `data/senzing-ready/`.
- Check `ground-rules.md` file-placement rules and any `docs/modules/` reference material
  for `data/transformed` and update them too, so the plugin is internally consistent
  (INV-003).
- No migration of existing bootcamper projects is required — this is a change to the
  plugin's convention for new runs.

## Acceptance criteria

- [ ] A repo-wide `grep -rn "data/transformed"` across `plugins/senzing-bootcamp/` returns no bootcamper-facing occurrences; the mapping output is written to and read from `data/senzing-ready/` consistently across Modules 5 and 6, graduation, and the viz server.
- [ ] INV-050's layout tree shows `data/senzing-ready/` (not `data/transformed/`), reconciled per the invariants-maintenance rules.
- [ ] Module 6 loaders read from `data/senzing-ready/`; nothing still points at `data/transformed/` (no broken path).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — mapper/output paths (7 references).
- `plugins/senzing-bootcamp/skills/module-06-data-processing/SKILL.md`, `.../phaseA-build-loading.md`, `.../phaseC-multi-source.md` — loader input paths.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — reference to the mapped-output directory.
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — data path.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` and `docs/modules/*` — any file-placement references (verify with grep).
- `specs/INVARIANTS.md` — update INV-050's layout tree.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Rename `data/transformed` to `data/senzing-ready`" (2026-07-18, Module: data_quality_mapping).
- Priority: Medium.
- Related specs: `layout-tree-reconciliation.md` (INV-050/INV-070 layout work). Supersedes the `specs/todo.md` line "Rename /docs/transformed/ to docs/senzing-ready/".

## Invariants introduced

- `INV-084` — Module 5's Senzing-ready mapping output is written to `data/senzing-ready/` and read from there by all consumers, never the former `data/transformed/`; the INV-050 tree is updated to match (recorded in `specs/INVARIANTS.md`).
