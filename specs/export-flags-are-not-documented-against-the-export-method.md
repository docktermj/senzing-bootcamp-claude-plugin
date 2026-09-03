# Export flags are not documented against the export method they are passed to

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`build_model` builds an explicit flag set for `export_json_entity_report`, deliberately
avoiding the `SZ_EXPORT_DEFAULT_FLAGS` composite. Five of its six members are
`SZ_ENTITY_INCLUDE_*` flags whose `applies_to` — per the server that owns the fact —
does **not** list `export_json_entity_report`.

If those five are genuinely not honored on the export stream, the export build returns
entities with no name and no records: every Bootcamper running Module 7 against **their
own datastore** gets a blank or near-empty visualization, with no error. The Truth Set
path is unaffected, because `--records` takes the per-record route with the broad
`SZ_ENTITY_DEFAULT_FLAGS` — so the failure would be invisible to every walkthrough that
uses the Truth Set, which is all of them.

⚠️ **This is a live-engine question and this machine cannot answer it.** There is no
loaded datastore here, and the suite is offline (INV-108). What follows is what the
server documents, not what an engine did.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1871-1878` requests:

```python
export_flags = (
    SzEngineFlags.SZ_EXPORT_INCLUDE_ALL_ENTITIES
    | SzEngineFlags.SZ_ENTITY_INCLUDE_ENTITY_NAME
    | SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_DATA
    | SzEngineFlags.SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
    | SzEngineFlags.SZ_ENTITY_INCLUDE_ALL_RELATIONS
    | SzEngineFlags.SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
)
```

`get_sdk_reference(topic='flags', filter=<each>)` — server 1.35.4, 2026-09-01 — returns
`applies_to` lists that include `export_json_entity_report` for **one** of the six:

| Flag | `applies_to` includes `export_json_entity_report` |
|---|---|
| `SZ_EXPORT_INCLUDE_ALL_ENTITIES` | yes |
| `SZ_ENTITY_INCLUDE_ENTITY_NAME` | no |
| `SZ_ENTITY_INCLUDE_RECORD_DATA` | no |
| `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO` | no |
| `SZ_ENTITY_INCLUDE_ALL_RELATIONS` | no |
| `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO` | no |

The five all come from `source_file: docs-flags-4-flags_get_entity.md` and list the
`get_entity` / `why_*` / `find_*` family instead.

**Two readings, and the evidence does not separate them.** Either (a) `applies_to` is
scoped to the doc page each flag is documented on and the entity-content flags work on
export anyway, or (b) the export method honors only what the export page documents. The
strongest evidence for (a) is that `SZ_ENTITY_DEFAULT_FLAGS` — a composite **whose
members are those same five** — *does* list `export_json_entity_report`, which is hard to
explain if its members are inert there. Nothing available offline settles it.

**What the owner route does say**, and it is the part that matters:
`get_sdk_reference(topic='response_schemas', filter='export_json_entity_report',
language='python')` documents every path `Model._absorb` reads —
`RESOLVED_ENTITY.ENTITY_ID`, `.ENTITY_NAME`, `.RECORDS[]` (with `DATA_SOURCE`,
`RECORD_ID`, `MATCH_KEY`, `ERRULE_CODE`, `MATCH_LEVEL_CODE`) and `RELATED_ENTITIES[]` —
and attaches `requires_flags` to **none** of them. The only flag-gated paths in the whole
export document are the `MATCH_KEY_DETAILS` subtree (`SZ_INCLUDE_MATCH_KEY_DETAILS`).

So the export response schema describes those fields as part of the export document
rather than as flag-gated additions, which is consistent with reading (a) but is not the
same claim as "these five flags are honored".

## Proposed change

Pick one, maintainer's call — this is a shipped-behavior decision, and the existing spec
`the-export-flag-set-is-coupled-to-absorb-with-nothing-connecting-them` explicitly said
"do not revert to `SZ_EXPORT_DEFAULT_FLAGS`", so it is not a decision to take silently:

1. **Use `SZ_EXPORT_INCLUDE_ALL_ENTITIES | SZ_ENTITY_DEFAULT_FLAGS`** (i.e.
   `SZ_EXPORT_DEFAULT_FLAGS`). Correct under both readings: `SZ_ENTITY_DEFAULT_FLAGS` is
   documented for export, and its `response_paths` are exactly the four `_absorb` reads.
   Costs the production caution the server attaches to `*_DEFAULT_FLAGS` composites
   ("membership may change between Senzing versions… no error is raised"), which for a
   teaching model reading four tolerant `.get()` paths is a widening risk, not a
   narrowing one.
2. **Keep the explicit list** and accept reading (a). Costs nothing if (a) holds and
   breaks every own-datastore Module 7 run if (b) does.
3. **Settle it on a live engine first**, then do 1 or 2 on evidence. This is the only
   option that produces a fact rather than a bet, and it needs a machine with a loaded
   datastore.

Until it is settled the flag set is unchanged (option 2 by default), with the
contradiction recorded in place at `senzing_viz_server.py:1873` as an `MCP-NEGATIVE`
marker so `coverage_reports.py negatives` re-asks it.

## Acceptance criteria

- [ ] The chosen flag set is justified at the site by what the **export** route
      documents, not by what the `get_entity` flag pages document.
- [ ] Whatever ships, `Model._absorb`'s field reads and the export flag set stay coupled
      by a test that fails when they drift (already in place —
      `tests/test_visualization_model_build_scales.py::EveryAbsorbedFieldIsAccountedFor`).
- [ ] The `MCP-NEGATIVE` marker at the flag set is resolved or re-dated against the
      server current at implementation time, never re-stamped without re-asking.
- [ ] **Not runtime-verifiable here.** Confirming which reading is correct needs a live
      engine with a loaded datastore; this environment has `libSz.so` but no datastore.
      The criterion is that the decision records which of the three options was taken and
      on what evidence.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the `export_flags` set at
  `build_model`, and the `MCP-NEGATIVE` marker recording the contradiction.
- `tests/test_visualization_model_build_scales.py` — the coupling tripwire, if the flag
  set changes.

## Source

- Feedback: none — self-observed while implementing
  `the-export-flag-set-is-coupled-to-absorb-with-nothing-connecting-them` (2026-09-01;
  `Source: self-observed (assistant retrospective)`). Found by re-verifying that spec's
  Senzing facts per `implement-spec` Step 3.3, which is the step that exists for this.
- Priority: Medium — no bootcamper has hit it, and nothing on the Truth Set path can. It
  is Medium rather than Low because the failure it risks is silent, total, and lands only
  on the Bootcamper's own data, which is the deliverable Module 7 exists for.
- MCP re-check: server 1.35.4, 2026-09-01 — **server now contradicts the plugin**
  (documented applicability, not observed behavior). Tools:
  `get_capabilities`; `get_sdk_reference(topic='flags', filter=…)` for each of the six
  flags; `get_sdk_reference(topic='response_schemas', filter='export_json_entity_report',
  language='python')`.
  `owner-checked: get_sdk_reference(topic='response_schemas',
  filter='export_json_entity_report', language='python')` — documents all four paths
  `_absorb` reads as export response fields and carries `requires_flags` **only** on the
  `MATCH_KEY_DETAILS` subtree, so the export document itself does not mark the fields this
  model needs as flag-gated.
- Upstream: **sent 2026-09-02 via `submit_feedback` (`question`, anonymous)**, on the
  maintainer's explicit approval of the exact text. Filed as a question rather than a bug:
  the contradiction in the documentation is demonstrable from the server's own responses,
  but no wrong *behavior* was observed — this machine has no loaded datastore, so which
  reading is correct could not be settled by running the export. The message quotes both
  sides, gives a two-call reproduction (`SZ_ENTITY_DEFAULT_FLAGS` vs
  `SZ_ENTITY_INCLUDE_RECORD_DATA`, compare `applies_to`), notes that the production guidance
  cannot be followed for the export methods under reading (b), and carries the
  `response_schemas` evidence for (a). ⚠️ **Submissions are anonymous and cannot be followed
  up**; a reply, if any, would have to come through `support@senzing.com`.
- Related specs: `the-export-flag-set-is-coupled-to-absorb-with-nothing-connecting-them`,
  `the-viz-server-header-describes-only-one-of-its-two-build-paths`
