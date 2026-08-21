# The profiler's multi-file output collision is fixed upstream, and the fix makes `profile_report.md` a conditional filename that INV-177 still states as fixed

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-05-data-quality-mapping/phase2-data-mapping.md:421-428` warns of a profiler limitation that
**no longer exists**, and prescribes a workaround that is now the server's own behavior:

> **For a multi-file source, the emitted commands write to the same output path.** A
> `mapping_workflow(action='start', file_paths=[…, …])` returned two `sz_schema_generator.py`
> invocations both using `-o <workspace_dir>/profile_report.md`. Run as issued, **only the second
> file's profile survives** […] **Profile each input to its own path** (`profile_report_<stem>.md`)
> and concatenate […]

The entry is dated *"Observed 2026-07-27 on SDK 4.3.3.26191; reported upstream 2026-07-31 and **not
re-run since**, so check whether they still apply rather than assuming"* — and it names its own
retirement condition: *"the numeric-value entry later in this file is the precedent for retiring one
once the server fixes it."*

Two costs, and the second is the one that bites:

1. The guide spends work routing around a defect that is gone.
2. The prescribed workaround now **reintroduces** the very collapse the entry warns about. The
   server already writes one report per input file; a guide that follows the instruction to
   "concatenate" them into a single `profile_report.md` recreates the single-schema file whose
   silent wrongness the entry exists to prevent.

## Root cause

The server changed profile-report naming to depend on the **number of input files**, and the plugin
still describes the pre-change behavior.

Verified against the live tool, **MCP server 1.33.0, 2026-08-21**, workspace
`/home/senzing/senzing-bootcamp-dryrun/data/mapping`:

`mapping_workflow(action='start', file_paths=['…/crm.csv', '…/orders.csv'], data={'workspace_dir': …})`
returned two commands writing to **distinct, per-stem paths**:

```text
… sz_schema_generator.py …/crm.csv    -o …/data/mapping/profile_report_crm.md
… sz_schema_generator.py …/orders.csv -o …/data/mapping/profile_report_orders.md
```

The same call with a **single** file returned the unsuffixed name:

```text
… sz_schema_generator.py …/crm.csv -o …/data/mapping/profile_report.md
```

So the collision is fixed, and the filename is now **conditional**: `profile_report.md` for one
input, `profile_report_<stem>.md` per input for more than one.

That conditionality reaches a second place. **INV-177** states the mechanism as unconditional:

> `mapping_workflow` writes `profile_report.md`, `schema_hints.md` and `JOURNAL.md` into the single
> `workspace_dir` under fixed names […] re-confirmed unchanged on server 1.32.9, 2026-08-13

True for a single-file start, which is the plugin's documented path
(`phase2-data-mapping.md:128` passes `file_paths=['data/raw/<source>.csv']`; `:365` says
"`file_paths` naming the source file"). **Not** true for the multi-file start the stale entry itself
contemplates: there the workspace receives `profile_report_crm.md` and `profile_report_orders.md`,
neither of which any relocation rule names. The relocation contract at `:90-101` and `:1346-1347`
lists exactly `profile_report.md`, so those files are left behind in the shared `data/mapping`
workspace un-relocated and un-source-qualified — which is precisely the overwrite INV-177 exists to
prevent, arriving through a filename the invariant does not cover.

⚠️ **Server-side inconsistency, observation-only (INV-080).** At 1.33.0 the step-1 *prose* still
hardcodes the unsuffixed name in both places it names a report — *"the profiler writes a detailed
markdown report to `<workspace_dir>/profile_report.md`"* and *"Read
`<workspace_dir>/profile_report.md`"* — while the emitted `commands` for a multi-file start write
the suffixed names. For a multi-file source the prose therefore points at a file that is never
created. The plugin cannot fix this; it can only stop depending on the prose. Not reported upstream
from this run (a dry run does not call `submit_feedback`).

## Proposed change

1. **Retire limitation entry 1** at `phase2-data-mapping.md:421-428`, per the precedent the
   surrounding text already names. Replace it with a short dated statement of current behavior:
   one report per input file, `profile_report.md` for a single input and `profile_report_<stem>.md`
   per input for several, verified on server 1.33.0, 2026-08-21. Do **not** invert the note into a
   warning about the new naming — state the behavior and let the relocation rule below carry the
   consequence.
2. **Renumber the remaining limitation** (the headerless-CSV entry, currently 2) and fix the
   "**Two** profiler limitations" lead-in to match.
3. **Extend the relocation contract** at `:90-101` so it covers both shapes: relocate
   `profile_report.md` when one file was profiled, and every `profile_report_<stem>.md` when
   several were, each to `docs/mapping/{source_name}_profile_report[_<stem>].md`. The point is that
   **no profile report is left in the shared workspace**, whatever the server named it.
4. **Add a dated correction note to INV-177** recording that the three-fixed-names premise is
   conditional on the input count, and that the rule binds every profile report the workspace
   receives rather than the literal name `profile_report.md`. The invariant's *rule* is still
   right — only its premise was narrower than stated.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` no longer tells the guide to expect a shared output path for a
      multi-file profile, and no longer instructs concatenating per-file reports into one.
- [ ] The lead-in count and the surviving limitation's number agree.
- [ ] The relocation guidance names both the single-input and multi-input profile-report filenames,
      so a multi-file source leaves no profile report in `data/mapping`.
- [ ] INV-177 carries a dated note that the fixed-filename premise holds for a single-file start
      and that the rule covers `profile_report_<stem>.md` too.
- [ ] A test asserts the relocation guidance covers the suffixed form — stdlib only, no `plugins/`
      import (INV-108), negative-controlled by removing the suffixed mention and confirming failure.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — retire
  limitation 1, renumber the survivor, fix the lead-in count, extend the relocation contract
- `specs/INVARIANTS.md` — dated correction note on INV-177
- `tests/` — new guard for the suffixed-filename relocation coverage

## Source

- Feedback: none — found by `/dry-run` phase 1 re-asking the entry's own "not re-run since" flag
  (2026-08-21, Module 5; `Source: self-observed (assistant retrospective)`)
- Priority: Medium — the stale entry wastes work and its workaround actively reintroduces the
  defect it warns about, but the plugin's mainline single-file path still behaves correctly
- MCP re-check: server 1.33.0, 2026-08-21 — **fixed upstream**. Called
  `mapping_workflow(action='start')` twice, once with two `file_paths` and once with one, reading
  the emitted `commands` array both times; multi-file now writes per-stem paths, single-file still
  writes `profile_report.md`.
- Upstream: not applicable — the plugin-side defect is a stale note; the residual server prose/commands
  mismatch was not filed (a dry run does not call `submit_feedback`)
- Related specs: `specs/module-05-shared-workspace-transient-filename-collision.md` (INV-177's origin)
