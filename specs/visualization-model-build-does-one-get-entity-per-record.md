# The visualization model is built one `get_entity` call per record, which does not scale to Module 7 volumes

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py` builds its model by reading a records file
and calling the engine once per record. Its own header says so (`:47`):

> *Data source: `get_entity_by_record_id` with `SZ_ENTITY_DEFAULT_FLAGS`*

and the call site is `:310` (`get = engine.get_entity_by_record_id`).

That is correct and fast at the Truth Set's scale. **Module 7 then points the same design at the
Bootcamper's own data** — `module-07-query-visualize-discover/phase1-query-visualize.md:607` says to
*"Build it modeled on the shipped Truth Set visualization server"* — and on the reporting run that
meant **19,584 round trips to build one page**.

Rebuilding the model on the export stream built it in **~15 seconds** on the same data. The change
was small because each export row carries the same shape a `get_entity` response does, so the
absorbing code needed no modification.

**There is a correctness gain as well as a speed one, and it is the more durable argument.** The
records-file build can only see entities that have a record in the file it was handed. The export
stream yields **every resolved entity** — including embedded-master records a mapper emitted that
appear in no input file. So the records-file build can silently under-represent the very
multi-source resolution Module 7 exists to show.

## Root cause

`senzing_viz_server.py` was written for the Truth Set (84 entities), where per-record fetching is
the simplest correct thing. Module 7 reuses it by instruction rather than by parameter, so the
scale assumption travels with the design into a context that breaks it, and nothing in the reference
or in Module 7's instruction marks the build strategy as the part that must change.

## Proposed change

1. **Give the reference server an export-stream build path**, and prefer it when the target is the
   Bootcamper's own datastore rather than the Truth Set. Verified against the live server
   (1.35.3, 2026-09-01), the Python surface is:
   `export_json_entity_report(flags: int = SZ_EXPORT_DEFAULT_FLAGS) -> int` on `SzEngine`, which
   returns an export **handle**; rows are then fetched and the handle closed. ⚠️ **Method names
   differ per binding** — Java `exportJsonEntityReport`, C# `ExportJsonEntityReport`, Rust and
   Python `export_json_entity_report`, TypeScript `exportJsonEntityReport` — and the flags argument
   type differs too (`Set<SzFlag>` in Java, `int` in Python). A guide writing this in the
   Bootcamper's chosen language MUST take the signature from
   `get_sdk_reference(topic='parameters', filter='export_json_entity_report', language=<binding>)`
   rather than translating the Python one (INV-002).
2. **Keep the records-file path** for the Truth Set, where it is correct and needs no export
   handle. This is a second build strategy, not a replacement.
3. **Say in Module 7 which strategy applies**, so "model it on the Truth Set server" does not carry
   the Truth Set's scale assumption into a 19,584-record datastore.
4. ⚠️ **Do not pin a flags composite into the guidance.** `get_sdk_reference` cautions that
   `*_DEFAULT_FLAGS` composites are for getting started rather than production and that their
   membership may change between versions; the export call should request the flags whose output
   the model actually consumes.

## Acceptance criteria

- [ ] The reference server can build its model from the export stream, and does so when pointed at
      a Bootcamper datastore rather than the Truth Set.
- [ ] The Truth Set path is unchanged and still builds from the records file.
- [ ] Module 7's "model it on the shipped server" instruction names which build strategy applies to
      the Bootcamper's own data.
- [ ] The export call's signature is taken from the server per binding, not translated — the
      guidance says so and names the route.
- [ ] ⚠️ **Not runtime-verifiable here**: "builds a 19,584-record model in ~15 seconds" needs a live
      engine with a loaded datastore of that size. The criterion is that the export path exists and
      is preferred, plus a test asserting the guidance; the timing claim stays the reporter's
      observation with its conditions (plugin 0.5.2, macOS 26.5.2, 2026-08-26).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the model build (`:47` header, `:310`
  call site).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — :607.
- `tests/test_visualization_model_build_scales.py` (new) — the guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, entry *"Visualization server model build does one
  getEntity per record, which does not scale to Module 7 volumes"*, 2026-08-26, module **Query,
  Visualize and Discover**, priority **Medium**, `Source: self-observed (assistant retrospective)`,
  plugin 0.5.2, macOS 26.5.2.
- Priority: Medium — every Module 7 Bootcamper with real data meets it, and it worsens with dataset
  size, which is the direction the module steers toward.
- MCP re-check: server **1.35.3**, 2026-09-01 — **confirmed.** `get_sdk_reference(topic='parameters',
  filter='export_json_entity_report', language='python')` returns
  `export_json_entity_report(flags: int = <SzEngineFlags.SZ_EXPORT_DEFAULT_FLAGS: 3734497>) -> int`
  on `SzEngine`, with `native_names` for all five bindings and an explicit warning that the flags
  argument type differs across them. The export API the reporter used exists and is current.
  owner-checked: n/a — this spec asserts no absence.
- Upstream: not applicable — the server is correct; the reference implementation is what needs the
  second build path.
- Related specs: `visualization-server-in-chosen-language.md` (the same server, the binding
  question).
