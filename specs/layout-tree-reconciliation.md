# Reconcile the generated-project layout with the INV-050 tree

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-050 pins the exact directory layout the generated Bootcamp project MUST
follow. The skills drift from that tree in **both** directions: they write to
paths the tree does not contain, and the tree lists paths no skill ever creates.
This makes INV-050 non-testable as written and is a concrete INV-003 consistency
gap.

## Root cause (confirmed)

Paths the skills use that are **not in the INV-050 tree:**

- `src/resources/` — `skills/bootcamp-onboarding/ground-rules.md:90-91`,
  `skills/module-02-sdk-setup/SKILL.md:588`.
- `data/mapping/` — `ground-rules.md:90-91`, `module-02-sdk-setup/SKILL.md:588`,
  `skills/module-05-data-quality-mapping/phase2-data-mapping.md:82,84`.
- HTML dashboards written to `docs/` root instead of `docs/visualizations/`:
  `skills/module-06-data-processing/phaseD-validation.md:57,115,117`
  (`docs/results_dashboard.html`, `docs/multi_source_results.html`). Module 3
  correctly uses `docs/visualizations/` (`phase2-visualization.md`).
- Naming mismatch (**tree side resolved 2026-07-17 by the maintainer**): the tree now
  lists the unambiguous pattern `docs/stakeholder_summary_module{n}.md` (was
  `stakeholder_summary_module1.md`) — the `_module{n}` family this spec recommended.
  Module 6 already conforms — `docs/stakeholder_summary_module6.md`
  (`skills/module-06-data-processing/phaseD-validation.md:166`). The **only**
  remaining mismatch is Module 1, which still writes `docs/stakeholder_summary.md`
  (`skills/module-01-business-problem/phase2-document-confirm.md:124`) — no
  `_module1` suffix, so it does not fit the pattern. Closing this now needs a skill
  edit to Module 1, not a further tree change.

Tree elements **no skill ever creates** (dead entries):
`config/session_log.jsonl`, `config/visualization_tracker.json`, `data/backups/`,
`docs/completion_summary.md`, `monitoring/`, `tests/`, `src/server/` (the viz
server ships as a plugin script, `scripts/senzing_viz_server.py`, so the project's
`src/server/` is never populated). `monitoring/` and `tests/` correspond to the
unbuilt Modules 8–11.

The single "create the layout" step (`module-02-sdk-setup/SKILL.md:587-589`)
creates only a subset and adds the two non-tree dirs above.

## Proposed change

Make the tree and the skills agree (INV-050 is the contract; prefer minimal moves):

- **Route stray paths into the tree**, or add them to the tree if they are
  legitimately needed: decide `src/resources/` and `data/mapping/` — either add
  both to the INV-050 tree, or reroute (mapping working data → `data/temp/` or
  `docs/mapping/`; resources → an existing `src/` subdir). Standardize generated
  HTML dashboards to `docs/visualizations/` (fix `module-06-…/phaseD-validation.md:57,115,117`).
- **Reconcile the stakeholder-summary name:** the tree now pins the
  `stakeholder_summary_module{n}.md` family (done by the maintainer) and Module 6
  already conforms. Remaining action: rename Module 1's output from
  `stakeholder_summary.md` to `stakeholder_summary_module1.md`
  (`module-01-business-problem/phase2-document-confirm.md:124`) so it fits the
  pattern. No further tree change is needed for this item.
- **Resolve dead tree entries:** either wire them up or annotate them in the tree
  as future/porting-phase (`monitoring/`, `tests/`, `src/server/` tie to Modules
  8–11; `config/session_log.jsonl`, `config/visualization_tracker.json`,
  `data/backups/`, `docs/completion_summary.md` are unused today).
- Update the layout-creation step (`module-02-sdk-setup/SKILL.md:587-589`) to
  create exactly the tree's directories.

Coordinate with `todo.md`'s existing idea ("Rename `docs/transformed/` to
`docs/senzing-ready/`") — note the physical dir today is `data/transformed/`
(consistent), and "Senzing-ready" is only terminology.

## Acceptance criteria

- [ ] Every path a skill instructs the guide to create exists in the INV-050 tree, and every non-annotated tree entry is created by some skill (both directions verified).
- [ ] Generated HTML visualizations are written under `docs/visualizations/` in every module (no `docs/`-root dashboards).
- [ ] The stakeholder-summary filename follows the `stakeholder_summary_module{n}.md` family across the tree and both modules — the tree pattern is already in place (done); Module 1 is renamed to `stakeholder_summary_module1.md` (Module 6's `stakeholder_summary_module6.md` already conforms).
- [ ] Dead tree entries are either produced by a skill or explicitly annotated as future/porting-phase in the INV-050 tree.
- [ ] The layout-creation step creates exactly the tree's directory set.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — file-placement contract (`src/resources/`, `data/mapping/`).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — layout-creation step (`:587-589`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — `data/mapping/` usage.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — dashboard paths (`:57,115,117`) and `stakeholder_summary_module6.md`.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — `stakeholder_summary.md` name (`:124`).
- `specs/INVARIANTS.md` — INV-050 tree: add legitimately-needed dirs and/or annotate future entries (in-place clarification, no meaning change).

## Source

- Invariant audit, 2026-07-17 (deep-dive over the plugin), INV-050 finding — bidirectional drift between the pinned tree and the skills.
- Re-evaluated 2026-07-17 after two maintainer tree edits: the INV-050 stakeholder entry went `stakeholder_summary_module1.md` → `stakeholder_summary_module.md` → `stakeholder_summary_module{n}.md` (the recommended unambiguous pattern). The **tree side** of the stakeholder-summary finding is now resolved; the only remaining stakeholder-summary work is the Module 1 skill rename to `stakeholder_summary_module1.md`. All other findings (`src/resources/`, `data/mapping/`, `docs/`-root dashboards, dead tree entries) are unchanged by the edits and remain open.
- Priority: Medium.
- Related specs: `todo.md` (`docs/transformed`→`senzing-ready` idea, adjacent). Bears on INV-017, INV-018, INV-050.

## Invariants introduced

- `INV-070` — Every generated HTML visualization the bootcamp produces MUST be written under the
  generated project's `docs/visualizations/` directory, never the `docs/` root or another `docs/`
  subdirectory (recorded in `specs/INVARIANTS.md`; hardens INV-050).
