# Record two now-confirmed response-shape facts: `JSON_DATA` is `get_record`-only, and network links key `MIN_/MAX_ENTITY_ID`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two `response_schemas` coverage defects were hit in one session. Both were reported upstream to
Senzing; both leave a plugin-side gap that a bootcamper pays for again on the next run.

### 1. `get_entity`'s schema documents paths that method cannot return

`get_sdk_reference(topic='response_schemas', filter='getEntity')` lists per-record source-value paths
under the get_entity response, including:

```text
RESOLVED_ENTITY.RECORDS[].JSON_DATA.ADDR_CITY
RESOLVED_ENTITY.RECORDS[].JSON_DATA.PRIMARY_NAME_FIRST
RESOLVED_ENTITY.RECORDS[].JSON_DATA.DATE_OF_BIRTH
```

An evidence viewer written against those documented paths printed
`(no JSON_DATA returned for this record)` for **every** record — the silent-blank failure mode, since
a wrong path yields null rather than an error. The flag reference explains why:

```text
get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_JSON_DATA')
  -> applies_to: ["get_record"]
     "Member of SZ_RECORD_DEFAULT_FLAGS."
```

Both halves re-confirmed against the live server at triage time. This is the exact failure mode
INV-115's dump-first rule exists to prevent — except here **the wrong path came from the
authoritative reference**, which is where a reader is told to go instead of guessing. Following it
produced a viewer reporting "no data" against a database with 92,394 records loaded. The fix was a
second per-record `getRecord` call, which also has a performance consequence worth knowing before
designing a viewer over a large entity set.

### 2. The network-link endpoint keys are now confirmed

The plugin's visualization reference already flags this as a known unknown:

> a bootcamp session reported that parsing `ENTITY_NETWORK_LINKS` entries with the `ENTITY_ID` /
> `RELATED_ENTITY_ID` pairing used elsewhere yielded `None` for **both** endpoints while `MATCH_KEY`
> rendered correctly … That observation is **not MCP-confirmable** — it is not in `response_schemas`
> and not in the indexed documentation.

It can now be confirmed. Dumping a real link element from `findNetwork` on SDK 4.3.3 gave:

```text
link element keys: [MIN_ENTITY_ID, MAX_ENTITY_ID, MATCH_LEVEL_CODE, MATCH_KEY, ERRULE_CODE, IS_DISCLOSED, IS_AMBIGUOUS]
```

The endpoints are carried under **normalized low-to-high keys `MIN_ENTITY_ID` / `MAX_ENTITY_ID`**.
The earlier bootcamp report was accurate.

## Root cause

**The upstream cause is MCP-server coverage and is not fixable here.** For (1),
`response_schemas` for `get_entity` includes `JSON_DATA.*` paths gated behind a `get_record`-only
flag, so the documented paths are unobtainable from the documented method under any flag combination —
an unobtainable documented path is worse than an undocumented one. For (2), the `find_network` entry
stops at the outer arrays. Both were sent via `submit_feedback` (category `bug`) on 2026-07-28.

**The plugin-side gap is that neither fact is recorded where a reader will need it.**

- `JSON_DATA` appears **nowhere** in the plugin (confirmed by grep across all skills and scripts), so
  a bootcamper building an evidence or record viewer reaches for the reference, gets the documented
  paths, and re-derives the whole failure. The plugin's response-shape trap list
  (`module-03b-truthset-visualization/visualization-api-reference.md:239-249`, "MCP-confirmed response
  paths", and its silent-blank asymmetry note at `:251-259`) is exactly where this belongs and does not
  mention it.
- For the link keys, `specs/network-link-fields-and-uncovered-response-schemas.md` **deliberately left
  one acceptance criterion unmet** and said so: documenting the endpoint keys "needs a live engine
  with loaded data, which the implementation environment does not have … To close the criterion
  properly, someone with a loaded engine should dump one link element, confirm the keys, and promote
  the caution to a documented field list marked verified-when." That dump has now happened. The
  caution at `visualization-api-reference.md:268-273` still reads "not MCP-confirmable … never the
  field names to code against", and `module-07-query-visualize-discover/phase2b-discover.md:40-47`
  still routes readers to "a reported session found both endpoints blank".

Filed as one spec because both are the same edit to the same file — promoting a live-dump-confirmed
response-shape fact into the plugin's trap reference — and because the upstream half of each is
already filed and out of scope here.

## Proposed change

1. **Promote the link-endpoint keys to a documented field list.** In
   `visualization-api-reference.md`, extend the `find_network_*` row of the MCP-confirmed paths table
   (`:239-249`) so `ENTITY_NETWORK_LINKS[]` documents its element shape — endpoints under
   `MIN_ENTITY_ID` / `MAX_ENTITY_ID` (normalized low-to-high), alongside `MATCH_LEVEL_CODE`,
   `MATCH_KEY`, `ERRULE_CODE`, `IS_DISCLOSED`, `IS_AMBIGUOUS` — marked **confirmed by live dump on SDK
   4.3.3, 2026-07-28**, and explicitly *not* MCP-sourced, since `response_schemas` still does not
   carry it (INV-149's marking discipline).

2. **Keep the dump rule primary.** Documenting the keys must not weaken the instruction to dump one
   element before parsing (INV-115/INV-149) — the keys are now a documented expectation to check
   against, not a license to skip the dump. Reduce the `:268-273` caution to a pointer at the
   documented list plus the dump requirement, rather than deleting the warning: the failure mode
   (endpoints blank, `MATCH_KEY` renders, row reads as real) is still the reason the rule exists
   (INV-148).

3. **Record the `JSON_DATA` constraint in the same trap reference.** State that per-record source
   values (`JSON_DATA.*`) are **not** obtainable from the `get_entity` family — the producing flag
   `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA` has `applies_to: ["get_record"]` and is a member of
   `SZ_RECORD_DEFAULT_FLAGS` — so a viewer needing them makes a second `get_record` call per record,
   at one extra SDK call per record. Note that `response_schemas` for `get_entity` lists those paths
   anyway, so the reference itself will mislead here: this is the one place the plugin must say the
   authoritative source is wrong, and why.

4. **Name the obtainable alternative.** The same `get_entity` schema documents
   `RESOLVED_ENTITY.RECORDS[].FEATURES.<TYPE>[].ATTRIBUTES.*` (e.g. `ATTRIBUTES.ADDR_CITY`,
   `ATTRIBUTES.PRIMARY_NAME_FIRST`) — per-record attribute values reachable from the entity family. At
   implementation time, confirm which entity-family flag produces `RECORDS[].FEATURES` and whether it
   supplies what a record viewer needs; if it does, that is the one-call path and the per-record
   `get_record` becomes the fallback rather than the answer. Do not assert this without confirming it
   (INV-080).

5. **Update `phase2b-discover.md:40-47`** to point at the now-documented element fields while keeping
   its dump-first ⚠️ and its partial-row ⛔ intact.

## Acceptance criteria

- [ ] `visualization-api-reference.md`'s MCP-confirmed paths table documents `ENTITY_NETWORK_LINKS[]`
      element fields including `MIN_ENTITY_ID` / `MAX_ENTITY_ID`, marked as confirmed by live dump on
      SDK 4.3.3 and explicitly not MCP-sourced — closing the criterion
      `network-link-fields-and-uncovered-response-schemas` left open.
- [ ] The instruction to dump one link element before parsing survives, and the partial-row rule
      (INV-148) is still stated with its failure shape.
- [ ] The trap reference states that `JSON_DATA.*` is unobtainable from the `get_entity` family, names
      the `get_record`-only flag and its `applies_to`, and warns that `response_schemas` for
      `get_entity` lists the paths regardless.
- [ ] The per-record cost of the `get_record` route is stated, so a viewer over a large entity set is
      designed knowing it.
- [ ] Whether `RECORDS[].FEATURES.<TYPE>[].ATTRIBUTES.*` supplies per-record source values from the
      entity family is confirmed against the MCP server at implementation time and documented as
      confirmed or ruled out — not asserted from this spec (INV-080).
- [ ] `phase2b-discover.md` points at the documented element fields without losing its dump-first or
      partial-row rules.
- [ ] A relationship-network rendering built from this guidance shows both endpoint ids populated.
- [ ] Every fact added is marked with how it was established — MCP-sourced or dump-confirmed with SDK
      version and date (INV-080, INV-149).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): response
      field names are language-independent JSON, and the contract binds a visualization server in any
      language (INV-090/INV-124).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the MCP-confirmed paths table (`:239-249`), the silent-blank asymmetry note (`:251-259`), and the
  link-endpoint caution (`:261-273`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — the
  lookup/caution block (`:33-47`).
- `tests/test_partial_row_and_schema_coverage.py` — it currently asserts **no** specific endpoint
  field name by design; update it to assert the documented, dump-marked field list while keeping the
  dump-discipline assertions.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "response_schemas lists JSON_DATA under
  get_entity, but the flag producing it is get_record-only" (2026-07-28, Module Data processing,
  Priority Medium) **merged with** → "response_schemas omits ENTITY_NETWORK_LINKS element fields — now
  confirmed as MIN_ENTITY_ID / MAX_ENTITY_ID" (2026-07-28, Module Query, Visualize and Discover,
  Priority Low). Both `Source: self-observed (assistant retrospective)`; `Routing: mcp-server`;
  `Upstream: sent 2026-07-28 via submit_feedback (category bug), anonymous — no follow-up possible`.
  Merged because the upstream half of each is already filed and the plugin-side half of each is the
  same edit to the same trap reference.
- Priority: Medium
- Related specs: `specs/network-link-fields-and-uncovered-response-schemas.md` (**this closes its
  deliberately-unmet acceptance criterion** — INV-148/INV-149),
  `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115),
  `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132),
  `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/export-related-entities-is-flag-conditional.md` (the third response-shape finding from the
  same session)
