# Verify SDK parameter shapes and flag-family semantics before writing code

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three separate SDK-usage failures in one session, all in code the plugin told the assistant to write,
all sharing one gap: the plugin's pre-code lookup discipline covers **method names, flag names, and
response shapes** — but not **parameter shapes** or **what a flag family actually controls**.

**1. `SZ_EXPORT_ALL_FLAGS` is absent from the Python binding.** Writing the phase D entity export,
a composite `SzEngineFlags.SZ_EXPORT_ALL_FLAGS` was the natural reach for "give me everything" — by
analogy with `SZ_ENTITY_DEFAULT_FLAGS`. It raised `AttributeError` on the installed SDK (4.3.3 /
build 4.3.3.26191). Recovery was by introspecting `dir(SzEngineFlags)` at runtime and OR-ing the
individual `SZ_EXPORT_INCLUDE_*` flags by hand. This one fails loudly, so it costs a debugging cycle
rather than producing a wrong answer — but it is avoidable, and every bootcamper writing an export
will look for that constant.

⚠️ **Corrected 2026-07-26.** This finding was originally filed, and originally written up here, as
"`SZ_EXPORT_ALL_FLAGS` does not exist". That generalization is wrong.
`get_sdk_reference(topic='flags', filter='export_json_entity_report')` returns the constant with
`applies_to: ["export_json_entity_report", "export_csv_entity_report"]` and the description "All
export flags combined", sourced from the **Java SDK's flag enum**. So the composite *is* documented
for the export methods; it is the **Python** binding's `SzEngineFlags` that lacks it — which is
exactly what the `AttributeError` was telling us. The observation was real; only the conclusion drawn
from it was too broad. The correct rule is per-binding availability, not non-existence, and that is
what the rest of this spec now asks for.

**2. `SZ_EXPORT_INCLUDE_*` flags alone produce rows containing only `{"ENTITY_ID": n}`.** After
OR-ing the six `SZ_EXPORT_INCLUDE_*` flags (single-record, multi-record, disclosed, possibly-same,
possibly-related, name-only), the export ran successfully and wrote one JSON object per entity — each
containing **nothing but `ENTITY_ID`**. No error. The two flag families do different jobs:
`SZ_EXPORT_INCLUDE_*` selects *which entities* appear; `SZ_ENTITY_INCLUDE_*` (`ENTITY_NAME`,
`RECORD_SUMMARY`, `RECORD_DATA`, `RECORD_MATCHING_INFO`, …) selects *what detail each row carries*.
A successful export of 4,587 rows with no usable fields is another looks-like-it-worked failure; it
was caught only because one raw row was dumped before the parser was written — which is exactly what
INV-115 prescribes, and the reason it cost minutes instead of a whole validation pass.

**3. Python `find_network_by_entity_id` takes `List[int]`, not the entity-IDs JSON document.** For the
Discover-phase relationship-network demonstration, the call was made as
`find_network_by_entity_id(json.dumps({"ENTITIES": [{"ENTITY_ID": 300418}, …]}), …)` — the JSON
document shape the flags documentation and the Java/C# signatures imply. The Python SDK rejected it:

```text
SzSdkError: value {"ENTITIES": [...]} has type str, should be a list of int(s) - expected:
find_network_by_entity_id(entity_ids: List[int], max_degrees: int, build_out_degrees: int,
build_out_max_entities: int, flags: int)
```

Passing a plain `[300418, 501752, 500174]` worked. (Credit where due: the SDK's error message names
the expected signature outright, so recovery was immediate.) Every bootcamper doing step 4d in Python
will hit this.

## Root cause

The plugin's MCP-first discipline has a shape-sized hole.

- **INV-115** (`specs/lookup-sdk-response-schemas-before-parsing.md`) requires looking up the
  **response** structure via `get_sdk_reference(topic='response_schemas', filter='<method>')` before
  parsing. It says nothing about the call's **inputs**.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md:26-35`
  faithfully implements INV-115 for step 4d — it requires both
  `get_sdk_reference(topic='flags', filter='find_network')` **and**
  `get_sdk_reference(topic='response_schemas', filter='find_network')` before generating the call —
  and then at `:44-46` says only "call `find_network` with a set of related entity IDs (at least 2–3
  entities from the relationship clusters in step 4a)". `topic='flags'` covers flags;
  `topic='response_schemas'` documents the response. **Neither covers the parameter shape**, so the
  reader's only remaining source is the cross-language documentation, whose JSON-document form is
  wrong for Python. The lookups were performed correctly and still could not have prevented this.
- Nothing anywhere states that `SZ_EXPORT_INCLUDE_*` and `SZ_ENTITY_INCLUDE_*` answer different
  questions, so OR-ing one family and getting a valid-but-empty result looks like a data problem
  rather than a flags problem.

**Upstream component (Senzing MCP server), not fixable in this repository:**

- `reporting_guide(topic='export')` does not name the export composites that actually exist, nor state
  that no all-inclusive export composite does.
- `get_sdk_reference` has no topic covering **parameter** shapes — only `flags` and
  `response_schemas`. This is the whole class: extending it would close all three findings at the
  source.

## Proposed change

Two tracks: what this repository can fix now, and what to request upstream.

**Plugin-side (this repo)**

1. **Extend the pre-code lookup rule from responses to signatures.** Where INV-115 requires looking up
   the response schema before parsing, add the symmetric requirement: before **calling** an SDK
   method, confirm its **parameter shape** for the bootcamper's chosen language — and when the MCP
   reference does not cover it, introspect the installed binding (e.g. `help()`/`inspect.signature`,
   `dir()` on the flags enum) rather than inferring from cross-language documentation or an example
   snippet. Note explicitly that **cross-language documentation is not authoritative for parameter
   shapes**: the same method takes a JSON document in one binding and a native list in another.

2. **Fix step 4d concretely.** In `phase2b-discover.md`, state that the Python binding takes a plain
   list of ints (`find_network_by_entity_id(entity_ids: List[int], max_degrees, build_out_degrees,
   build_out_max_entities, flags)`) and that the entity-IDs JSON-document form implied by the
   cross-language docs is **not** the Python shape. Add the same caution for `find_path_by_entity_id`.
   Keep it language-agnostic in framing (INV-002): the rule is "confirm the shape for your binding",
   with Python's given as the known-divergent case.

3. **Document the two export flag families where the export is written.** In
   `module-06-data-processing/phaseD-validation.md` (and anywhere else the bootcamp writes an export),
   state plainly:
   - `SZ_EXPORT_INCLUDE_*` chooses the **row set** (which entities appear);
   - `SZ_ENTITY_INCLUDE_*` chooses the **columns** (what detail each row carries);
   - an export with only the former is **valid but empty** — it will succeed and produce rows
     containing only `ENTITY_ID`;
   - a composite's **availability is per-binding**: `SZ_EXPORT_ALL_FLAGS` is documented for the
     export methods but is absent from the Python binding's `SzEngineFlags`, so confirm a composite
     exists on the bootcamper's binding before reaching for it — enumerate via the MCP tools or
     introspect the flags enum. Do **not** state that the constant does not exist.

   A worked flag expression makes this unmissable; include one, marked as MCP-confirmed at the time of
   writing and to be re-confirmed per session (INV-080).

4. **Require a raw-row dump before writing an export parser.** INV-115's defensive practice is what
   caught finding 2. Make it explicit for bulk exports: dump one raw row and confirm the fields the
   parser expects are present **before** parsing the whole file. Cheap, and it converts a whole wasted
   validation pass into one line of output.

**Upstream (Senzing MCP server) — request, track, do not block on**

- Have `reporting_guide(topic='export')` name the export composites available **per language
  binding**, together with the `SZ_EXPORT_INCLUDE_*` (row set) vs `SZ_ENTITY_INCLUDE_*` (per-row
  detail) distinction. `SZ_EXPORT_ALL_FLAGS` is documented for the export methods but is absent from
  the Python `SzEngineFlags` in 4.3.3, so a reader who trusts the flag reference gets an
  `AttributeError`. A one-line note that the constant is Java-side only, plus a pointer to
  `SZ_EXPORT_DEFAULT_FLAGS` as the Python starting point, would close finding 1.
- Have `reporting_guide(topic='graph')` show a runnable Python `find_network_by_entity_id` /
  `find_path_by_entity_id` call with actual argument types.
- **Extend `get_sdk_reference` to cover parameter shapes**, not just responses and flags. This fixes
  the class rather than the three instances, and is the request worth pressing.

File these via `submit_feedback` so they reach the MCP server maintainers, and record in the spec's
implementation notes that the plugin-side guidance is the interim mitigation, to be trimmed once the
MCP server covers parameter shapes.

## Acceptance criteria

- [ ] The guidance requires confirming an SDK method's parameter shape for the chosen language before
      calling it, and names binding introspection as the fallback when the MCP reference does not
      cover it.
- [ ] The guidance states that cross-language documentation is not authoritative for parameter shapes.
- [ ] `phase2b-discover.md` step 4d states the Python parameter shapes for
      `find_network_by_entity_id` and `find_path_by_entity_id`, and that the JSON-document form is
      wrong for Python — while staying framed language-agnostically (INV-002).
- [ ] Phase D's export guidance states the `SZ_EXPORT_INCLUDE_*` (rows) vs `SZ_ENTITY_INCLUDE_*`
      (columns) split, that only the former yields rows containing just `ENTITY_ID`, and that
      `SZ_EXPORT_ALL_FLAGS` is documented for the export methods yet absent from the Python binding —
      qualified by binding, never asserted as non-existent (INV-080).
- [ ] A worked, MCP-confirmed flag expression for a detail-carrying export appears in the guidance,
      marked for per-session re-confirmation (INV-080).
- [ ] Writing an export parser is preceded by dumping one raw row and confirming the expected fields
      are present (INV-115).
- [ ] Upstream requests are filed via `submit_feedback` for: export composites in
      `reporting_guide(topic='export')`, a runnable graph call in `reporting_guide(topic='graph')`,
      and parameter-shape coverage in `get_sdk_reference`.
- [ ] No flag name, composite, or signature is asserted from training data — every one is
      MCP-sourced or introspected from the installed SDK (INV-080).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — extend the pre-code lookup
  rule from response schemas to parameter shapes and flag-family semantics.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — Python
  parameter shapes for the graph methods at step 4d (`:26-46`).
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — the two export
  flag families, the per-binding composite-availability note, the worked flag expression, and the
  raw-row dump requirement.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — align its export-flag guidance with the flag-family split.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "`SZ_EXPORT_ALL_FLAGS` does not exist in SDK
  4.3.3" (2026-07-26, Module Data processing; `Source: self-observed (assistant retrospective)`)
  — entry title quoted verbatim for traceability; its claim is corrected in finding 1 above (the
  constant exists for the export methods, absent from the Python binding).
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "`export_json_entity_report` with only
  `SZ_EXPORT_INCLUDE_*` flags returns bare `{\"ENTITY_ID\": n}`" (2026-07-26, Module Data processing;
  `Source: self-observed (assistant retrospective)`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Python `find_network_by_entity_id` takes
  `List[int]`, not the entity-IDs JSON document" (2026-07-26, Module Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium (all three entries)
- Related specs: `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — the invariant this
  extends from responses to inputs), `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/match-key-audit-cannot-read-related-entities-from-export.md` (the same phase D export work),
  `specs/java-scaffold-json-dependency-gap.md` and
  `specs/mapping-workflow-truncated-validation-errors.md` (other upstream MCP-server findings).

## Invariants introduced

- `INV-132` — Before calling a Senzing SDK method, its parameter shape MUST be confirmed for the
  Bootcamper's binding; cross-language documentation is not authoritative for argument types, and a
  flag family's meaning and a composite's availability MUST likewise be confirmed per binding
  (recorded in `specs/INVARIANTS.md`).

## Correction applied (2026-07-26)

This spec previously asserted, in five places, that `SZ_EXPORT_ALL_FLAGS` does not exist — including
in an acceptance criterion, which would have put a Senzing falsehood into bootcamper-facing guidance
(INV-080 forbids that as firmly as a guess). MCP
(`get_sdk_reference(topic='flags', filter='export_json_entity_report')`) shows the constant is
documented for `export_json_entity_report` / `export_csv_entity_report`, sourced from the Java SDK
flag enum; the **Python** binding lacks it, which is what produced the reported `AttributeError`.

All five are now corrected to the per-binding rule: finding 1's heading and body, the
proposed-change bullet, the upstream request wording, the acceptance criterion, and the
affected-files description. The original feedback entry title is quoted verbatim under `## Source`
for traceability, annotated as corrected. The shipped guidance
(`ground-rules.md`, `phaseD-validation.md`) already stated the per-binding rule, and
`tests/test_sdk_parameter_shapes.py` asserts neither file ever denies the constant outright — so the
code never carried the error, only this document did.
