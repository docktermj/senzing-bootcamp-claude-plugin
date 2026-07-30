# Module 5 multi-source mapping: shared workspace + unqualified relocation names collide across sources

Maintain the invariant conditions in @INVARIANTS.md.

## Problem

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
step 8 directs **every** data source's `mapping_workflow` run to use the same, single
workspace directory:

```text
mapping_workflow(action='start',
                 file_paths=['data/raw/<source>.csv'],
                 data={'workspace_dir': 'data/mapping'})
```

— not a per-source subdirectory. Step 19 confirms this is meant to run once per source in
sequence: "Each source gets its own transformation program and its own `mapping_workflow`
run."

Inside the MCP tool's own step 1/2/3 instructions, three working files are written to that
workspace with **fixed, non-source-qualified names**: `profile_report.md`,
`schema_hints.md`, `JOURNAL.md`. The module's file-placement contract in
`phase2-data-mapping.md` ("File placement during the workflow") then relocates them to
their durable home with the **same unqualified names**:

> "mapping-phase Markdown (`profile_report.md`, `schema_hints.md`, `JOURNAL.md`) →
> `docs/mapping/`"

Unlike the per-source mapping specification, which is explicitly named
`docs/mapping/{source_name}_mapper.md` (step 18), these three carry no source qualifier at
either the transient-workspace name or the relocated-destination name.

**Consequence for a real multi-source run** (reproduced live mapping a 6-source KYC
dataset): once source A's run completes and its `docs/mapping/JOURNAL.md` /
`schema_hints.md` / `profile_report.md` are relocated, starting source B's
`mapping_workflow` with the same `workspace_dir: 'data/mapping'` causes the MCP tool to
write **fresh copies at the identical workspace paths** for its own Step 1 profiling.
Two failure modes follow, both real:

1. If source B's run is relocated with the same unqualified destination names, it
   **silently overwrites** source A's `docs/mapping/profile_report.md` /
   `schema_hints.md` / `JOURNAL.md` — losing the durable record of how source A was
   profiled and mapped, with no error and no warning.
2. If the bootcamper/assistant notices and avoids overwriting by renaming at relocation
   time, that renaming is **improvised** — the file gives no naming convention for these
   three files, unlike the `{source_name}_mapper.md` pattern it does specify — so
   different sessions would plausibly invent different conventions.

## Root cause

`phase2-data-mapping.md`, "File placement during the workflow" section
(~lines 79-102) and step 8 (~lines 168-190): the workspace is shared across all sources
by design (a single `data/mapping` directory, confirmed by step 8's own example), but the
relocation naming for `profile_report.md` / `schema_hints.md` / `JOURNAL.md` was written
as if only one source would ever pass through the workspace. The per-source qualifier
that step 18 already applies to `{source_name}_mapper.md` was not extended to these three.

## Proposed change

Qualify all three relocated filenames with the source name, matching the existing
`{source_name}_mapper.md` convention:

- `docs/mapping/{source_name}_profile_report.md`
- `docs/mapping/{source_name}_schema_hints.md`
- `docs/mapping/{source_name}_JOURNAL.md`

Update the "File placement during the workflow" section to state this explicitly, and add
a one-line warning at step 8 (or immediately before step 19's "repeat for remaining data
sources") that the shared `workspace_dir` means these three filenames **must** be
relocated with a source-qualified name before starting the next source's
`mapping_workflow` run — otherwise the next source's Step 1 will overwrite them in place.

## Acceptance criteria

- [ ] `phase2-data-mapping.md`'s file-placement contract names the source-qualified
      destination for `profile_report.md`, `schema_hints.md`, and `JOURNAL.md`.
- [ ] A one-line warning appears at (or near) step 19 stating that these three files must
      be relocated with their source-qualified name before the next source's
      `mapping_workflow(action='start')` call, since all sources share one `workspace_dir`.
- [ ] Cross-platform / language-agnostic: filename qualification is plain string
      formatting, unaffected by OS or the bootcamper's chosen mapper language.
- [ ] A live multi-source run (2+ sources through the same `workspace_dir`) shows both
      sources' relocated files present and distinct in `docs/mapping/`, with neither
      overwritten by the other — this criterion needs a live multi-source
      `mapping_workflow` run to confirm; not runtime-verified by this spec alone.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
  (the "File placement during the workflow" section, and step 19).

## Source

Self-observed during a maintainer-run phase-3 dry-run walk (`.claude/skills/dry-run/`),
mapping a real 6-source KYC dataset (GLEIF mapped first) all sharing one project and one
`workspace_dir='data/mapping'` per step 8's own directive. Not bootcamper-reported.
Date: 2026-07-29.

## Deviations from this spec, and why (2026-07-29)

- **Server re-verification made the problem slightly worse than the spec described.** The three
  fixed workspace filenames were confirmed by running `mapping_workflow(action='start')` (server
  **1.32.2**, 2026-07-29): step 1's instructions name `<workspace_dir>/profile_report.md`,
  `<workspace_dir>/schema_hints.md` and `<workspace_dir>/JOURNAL.md`. Additionally, `JOURNAL.md` is
  specified as **APPEND-ONLY** ("APPEND a short entry … NEVER rewrite the whole file"), so a second
  source's run does not merely overwrite the first source's journal — it **appends its entries onto
  it**, silently interleaving two sources' mapping history in one log. The implemented warning says
  so.
- **The final acceptance criterion is NOT runtime-verified.** "A live multi-source run (2+ sources
  through the same `workspace_dir`) shows both sources' relocated files present and distinct" needs
  two complete `mapping_workflow` runs plus the relocation step, i.e. the bootcamper flow with real
  sources — which this environment does not exercise. The spec already flags this criterion as not
  verifiable by itself. What *was* verified live is the precondition that makes the collision real:
  one shared `workspace_dir` (step 8) and three fixed, non-source-qualified filenames written into
  it by the workflow.

## Invariants introduced

- `INV-177` — When a per-source workflow run writes fixed, non-source-qualified filenames into a
  workspace directory **shared across sources**, every such artifact MUST be relocated to its
  durable home under a **source-qualified** name before the next source's run begins, and any
  guidance naming that shared workspace MUST state the qualifier for every fixed filename the
  workspace receives. Use the `{source_name}_` form already required for
  `docs/mapping/{source_name}_mapper.md`. (Recorded in `specs/INVARIANTS.md`, 2026-07-29.)
