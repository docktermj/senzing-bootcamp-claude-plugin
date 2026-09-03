# `build_from_export` is unreachable in the shipped server, and the ledger ticked the criterion anyway

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`visualization-model-build-does-one-get-entity-per-record` (implemented 2026-09-01, `52f3be3`)
added `Model.build_from_export()` to `plugins/senzing-bootcamp/scripts/senzing_viz_server.py`.
**Nothing in the shipped script calls it.**

```text
senzing_viz_server.py:1809   model = Model().build(engine, flags, _iter_record_keys(patterns))
                             ^ the only build call site — the per-record path, unconditionally
senzing_viz_server.py:2134   ap.add_argument("--records", nargs="+", required=True, …)
                             ^ and --records is REQUIRED, so no invocation can reach the export path
```

The only callers are in `tests/test_visualization_model_build_scales.py`. In the shipped artifact
the method is dead code.

**The spec's first acceptance criterion has two halves and only the first was built:**

> - [ ] The reference server **can build** its model from the export stream, **and does so when
>   pointed at a Bootcamper datastore** rather than the Truth Set.

The ledger entry ticks it **✅** with the evidence *"`Model.build_from_export()` added"* — which
establishes the first half and says nothing about the second.

⚠️ **The consequence is a consistency defect between an instruction and the artifact it points at.**
`module-07-query-visualize-discover/phase1-query-visualize.md` now carries ⛔ *"Build the model from
the EXPORT STREAM, not one `get_entity` call per record"*, and three lines above tells the guide to
*"Build it modeled on the shipped Truth Set visualization server"*. A guide that does exactly that —
reads the reference to model on it — finds a server whose only reachable build path is the one the
instruction forbids, with the sanctioned path present but wired to nothing.

## Root cause

Two things, and the second is the reason it shipped:

1. **The reference server is only ever pointed at the Truth Set.** `--records` is required and the
   Truth Set path is correct there, so there was no obvious place to call the new method — and no
   route was added.
2. **The criterion walk accepted the method's existence as the whole criterion.** This is the
   failure `implement-spec` Step 4 documents twice and warns about in bold: *"a criterion that names
   a file, a module, or a second consumer is checked against that file — open it and look — not
   against the change you remember making."* Here the second consumer is the server's own `main()`,
   and it was never opened.

## Proposed change

Pick one, and record which — they are genuinely different products:

1. **Make the reference demonstrate the strategy it now mandates.** Relax `--records` to optional
   and build from the export stream when it is omitted, keeping the per-record path for the Truth
   Set. Module 7's "model it on this" then points at a server that does what the instruction says,
   and the method stops being dead code. ⚠️ Existing invocations keep working — this only adds a
   route.
2. **Declare it a reference implementation for the guide to copy**, exercised by tests rather than
   by the CLI — and then **correct the ledger**: criterion 1's second half is not met, and the entry
   must say so rather than ticking it.

⛔ **Do not leave it as it is.** Dead code in a shipped script that an instruction tells a reader to
model on is the worst of the three: the reader cannot tell whether the method is the sanctioned path
or an abandoned one.

## Acceptance criteria

- [ ] `build_from_export` is either reachable from the shipped server, or documented as a
      copy-me reference with the ledger corrected to match.
- [ ] The Truth Set path is unchanged and still the default for the Truth Set.
- [ ] Module 7's instruction and the reference server no longer disagree about which build strategy
      is sanctioned.
- [ ] If option 1 is taken: a repo-level test asserts the export path is selected when no records
      file is supplied, and the per-record path when one is. Negative-controlled.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      choice of build strategy is binding-independent.

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `build_model` (`:1798-1809`) and the
  argument parser (`:2133-2144`).
- `specs/IMPLEMENTED.md` — the `visualization-model-build-does-one-get-entity-per-record` entry's
  criterion 1, if option 2 is taken.
- `tests/test_visualization_model_build_scales.py` — the selection test, if option 1 is taken.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, checking the call sites of a
  method added earlier the same day (`Source: self-observed (assistant retrospective)`).
- Priority: Medium — nothing a Bootcamper runs is broken today, because the reference is only
  pointed at the Truth Set where the per-record path is correct. What is wrong is that a shipped
  instruction and the artifact it names as the model disagree, and that a ledger entry records a
  criterion as met when half of it is not.
- MCP re-check: **n/a (no Senzing fact)** — the export API itself was verified against server 1.35.3
  on 2026-09-01 when the method was written; this spec is about whether anything calls it.
- Upstream: not applicable
- Related specs: `visualization-model-build-does-one-get-entity-per-record.md` — the implementation
  this audits.

## Deviations from this spec, and why (2026-09-01)

**Option 1 was taken:** `--records` is now optional, and `build_model` builds from the export stream
when it is omitted. Existing invocations are unaffected — passing `--records` keeps the per-record
Truth Set behavior exactly as before.

**One thing the spec did not anticipate: wiring the call exposed a second instruction/reference
disagreement, of the same class.** The obvious wiring is
`build_from_export(engine, SzEngineFlags.SZ_EXPORT_DEFAULT_FLAGS)` — and Module 7's own new rule,
shipped an hour earlier, says ⚠️ *"Do not pin a `*_DEFAULT_FLAGS` composite into the export call."*
Doing the obvious thing would have made the reference contradict the instruction pointing at it,
which is the defect this spec exists for, reproduced while fixing it.

The export call therefore requests exactly what `_absorb` reads:

    SZ_EXPORT_INCLUDE_ALL_ENTITIES | SZ_ENTITY_INCLUDE_ENTITY_NAME
  | SZ_ENTITY_INCLUDE_RECORD_DATA | SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
  | SZ_ENTITY_INCLUDE_ALL_RELATIONS | SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO

Verified against server **1.35.3, 2026-09-01**: `get_sdk_reference(topic='flags',
filter='SZ_EXPORT_DEFAULT_FLAGS')` returns `composite_members: ["SZ_EXPORT_INCLUDE_ALL_ENTITIES",
"SZ_ENTITY_DEFAULT_FLAGS"]` with the standing production caution that a DEFAULT composite's
membership may change between versions with no error raised. ⚠️ **Every flag name was additionally
checked against the installed SDK enum** (`senzing.SzEngineFlags`, 4.4.0.26242) — a runtime check,
not a documentation one, because a flag that does not exist fails at call time and nothing offline
would catch it.

**The per-record path still uses `SZ_ENTITY_DEFAULT_FLAGS` and was deliberately left alone.** Module
7's rule is scoped to the **export call**; changing the Truth Set path's flags is a different
decision with its own risk, and this spec does not make it.

⚠️ **Not runtime-verified.** The export path has not been executed against a live engine — this
environment has an SDK but no loaded datastore. What is verified: the call graph reaches it from the
shipped entry point, `--records` is optional, the flag names exist in the installed enum, and both
build paths produce identical models against a fake engine. Running it needs `dry-run` phase 3.
