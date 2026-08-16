# A method's own default-flags composite omits `RECORD_DATA`, so `RECORDS[]` reads empty while the field name is right

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Writing a watchlist-screening query program, the guide called
`search_by_attributes(attributes, SzEngineFlags.SZ_SEARCH_BY_ATTRIBUTES_ALL)` and read
`entity.get("RECORDS", [])` to determine which data sources each result belonged to. It came
back as an **empty list for every result**, including entities known to have 4+ records across
4 sources. The same pattern with `find_network_by_entity_id` under its own
`SZ_FIND_NETWORK_DEFAULT_FLAGS` produced the same empty result. `RECORD_SUMMARY[]` read
correctly under those same flags.

Both failures were silent: valid JSON, no error, and a wrong-looking-but-plausible empty list.
A bootcamper would reasonably conclude "the search found nothing useful" or "my data lacks
that field" rather than "the flags in force do not populate the field I read".

The important part is that **the plugin's existing lookup discipline was followed and did not
prevent it.** INV-115 and `phase1-query-visualize.md` require looking up flags *and*
`response_schemas` before parsing; both lookups were done. Neither surfaces the trap, because
the field name `RECORDS[]` is **correct** — it is simply not populated by the composite these
two methods take *by default*.

## Root cause

`plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`:

1. **Lines 58-64 ("Flags")** tell the guide to look up available flags and "select the flags
   matching the bootcamper's query intent" — but say nothing about the method-specific default
   composites, which apply when the caller passes no flags *or* reaches for the obvious
   "give me everything" constant for that method.
2. **Lines 73-76 ("Defensive parsing")** name exactly one cause for a blank field: *"treat it
   as a probable wrong field name first and absent data second."* This blank had a **third**
   cause the file never names — right field name, right method, flags that do not populate it.
   Following the rule as written sends the reader to re-verify a field name that is already
   correct, and the check passes, which reads as confirmation that the data is absent.

Grep confirms the gap: `SZ_SEARCH_BY_ATTRIBUTES_ALL`, `SZ_FIND_NETWORK_DEFAULT_FLAGS` and the
`RECORDS[]`-vs-`RECORD_SUMMARY[]` distinction appear **nowhere** in the plugin's Markdown.

### What the live server returned

`get_sdk_reference(topic='flags', filter='SZ_SEARCH_BY_ATTRIBUTES_ALL', language='python')` —
server **1.32.2**, verified **2026-07-29** — **confirms the report**:

```json
{"name": "SZ_SEARCH_BY_ATTRIBUTES_ALL",
 "composite_members": ["SZ_SEARCH_INCLUDE_ALL_ENTITIES",
                       "SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES",
                       "SZ_ENTITY_INCLUDE_ENTITY_NAME",
                       "SZ_ENTITY_INCLUDE_RECORD_SUMMARY",
                       "SZ_INCLUDE_FEATURE_SCORES"]}
```

`get_sdk_reference(topic='flags', filter='SZ_FIND_NETWORK_DEFAULT_FLAGS', language='python')`,
same server and date:

```json
{"name": "SZ_FIND_NETWORK_DEFAULT_FLAGS",
 "composite_members": ["SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO",
                       "SZ_ENTITY_INCLUDE_ENTITY_NAME",
                       "SZ_ENTITY_INCLUDE_RECORD_SUMMARY"]}
```

Neither includes `SZ_ENTITY_INCLUDE_RECORD_DATA`. The same response gives the mapping that
makes the consequence exact:

- `SZ_ENTITY_INCLUDE_RECORD_DATA` → `response_paths: ["RESOLVED_ENTITY.ENTITY_ID", "RESOLVED_ENTITY.RECORDS[]"]`
- `SZ_ENTITY_INCLUDE_RECORD_SUMMARY` → `response_paths: ["RESOLVED_ENTITY.ENTITY_ID", "RESOLVED_ENTITY.RECORD_SUMMARY[]"]`

And the contrast that makes it a trap — `SZ_ENTITY_DEFAULT_FLAGS` **does** carry
`SZ_ENTITY_INCLUDE_RECORD_DATA` (its `composite_members` list it explicitly), as does
`SZ_ENTITY_CORE_FLAGS`. So a guide who has internalized "the default flags give me records"
from `get_entity` is correct there and wrong for `search_by_attributes` and `find_network`.

The Python signatures returned alongside confirm these composites are the **implicit** defaults,
not merely the obvious explicit choice:

```text
search_by_attributes(attributes: str, flags: int = <SzEngineFlags.SZ_SEARCH_BY_ATTRIBUTES_ALL: 201340943>, search_profile: str = '') -> str
find_network_by_entity_id(entity_ids: List[int], max_degrees: int, build_out_degrees: int, build_out_max_entities: int, flags: int = <SzEngineFlags.SZ_FIND_NETWORK_DEFAULT_FLAGS: 8589946880>) -> str
```

So omitting the `flags` argument entirely produces the same empty `RECORDS[]`.

## Proposed change

In `phase1-query-visualize.md`:

1. **Extend the "Flags" paragraph** with the method-specific-default rule: a method's own named
   default composite is **not** `SZ_ENTITY_DEFAULT_FLAGS` and may omit entity sub-flags that
   default carries. Before parsing an entity field out of a `search_by_attributes` or
   `find_network` response, read the composite's `composite_members` and confirm the flag that
   populates the field you intend to read is in it — `SZ_ENTITY_INCLUDE_RECORD_DATA` for
   `RECORDS[]`, `SZ_ENTITY_INCLUDE_RECORD_SUMMARY` for `RECORD_SUMMARY[]`. Name the two
   confirmed cases explicitly, with their provenance, so the reader does not have to
   re-derive them.
2. **Add the third cause to "Defensive parsing".** A blank field has three causes, not two:
   wrong field name, absent data, **or a correct field name the flags in force do not
   populate**. State the discriminator: if `response_schemas` confirms the path and a sibling
   field from the same response reads fine, suspect the flags before the data. State the fix —
   OR the missing sub-flag into the composite explicitly
   (`SZ_SEARCH_BY_ATTRIBUTES_ALL | SZ_ENTITY_INCLUDE_RECORD_DATA`) rather than switching to a
   different field.
3. **Say which field answers "which sources is this entity in?"** under the unmodified
   defaults: `RECORD_SUMMARY[]` (which carries `DATA_SOURCE` per source), so a bootcamper who
   only needs source membership need not widen the flags at all.

## Acceptance criteria

- [ ] `phase1-query-visualize.md` states that a method's own default composite may omit
      sub-flags `SZ_ENTITY_DEFAULT_FLAGS` carries, and names
      `SZ_SEARCH_BY_ATTRIBUTES_ALL` and `SZ_FIND_NETWORK_DEFAULT_FLAGS` as confirmed cases
      that omit `SZ_ENTITY_INCLUDE_RECORD_DATA`, with tool/version/date provenance.
- [ ] The defensive-parsing guidance names "correct field name, flags do not populate it" as a
      distinct third cause of a blank, with the sibling-field discriminator and the
      OR-in-the-sub-flag fix.
- [ ] The guidance says `RECORD_SUMMARY[]` is what the unmodified defaults populate for
      source membership.
- [ ] No Senzing fact in the added text is copied from this spec without being re-confirmed
      against the server at implementation time (INV-080).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      the flag composites are SDK-level and identical across bindings; the guidance names no
      OS-specific or language-specific step.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
  — the "Flags" paragraph (~lines 58-64) and "Defensive parsing" (~lines 73-76).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "search_by_attributes and find_network_by_entity_id's own default flags omit RECORDS[], populate RECORD_SUMMARY[] instead" (2026-07-29, Module Query, Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **still reproduces** — server **1.32.2**, 2026-07-29, via
  `get_capabilities` and `get_sdk_reference(topic='flags', filter='SZ_SEARCH_BY_ATTRIBUTES_ALL' | 'SZ_FIND_NETWORK_DEFAULT_FLAGS', language='python')`.
  Both composites confirmed to include `SZ_ENTITY_INCLUDE_RECORD_SUMMARY` and exclude
  `SZ_ENTITY_INCLUDE_RECORD_DATA`; `SZ_ENTITY_DEFAULT_FLAGS` confirmed to include the latter.
- Upstream: already sent 2026-07-29 via `submit_feedback` (`bug`, anonymous), per the entry.
  Not re-filed: this triage adds no fact the original submission lacked (same server version,
  same day).
- Related specs: `specs/lookup-sdk-response-schemas-before-parsing.md` (established INV-115's
  lookup rule — this spec covers the case where that lookup passes and the parse still fails),
  `specs/verify-sdk-parameter-shapes-and-flag-families.md` (flag-family semantics),
  `specs/confirm-json-data-and-network-link-response-paths.md`,
  `specs/network-link-fields-and-uncovered-response-schemas.md`

## Deviations from this spec, and why (2026-07-29)

- **One claim this spec made had never actually been verified — it has been now.** The spec's
  proposed change item 3 asserted that `RECORD_SUMMARY[]` "carries `DATA_SOURCE` per source". That
  was written from reasoning, not from the server: the triage run had checked `topic='flags'` but not
  `topic='response_schemas'`. Confirmed at implementation:
  `get_sdk_reference(topic='response_schemas', filter='search_by_attributes', language='python')`
  documents `RECORD_SUMMARY[].DATA_SOURCE` (string) and `RECORD_SUMMARY[].RECORD_COUNT` (integer)
  (server **1.32.2**, verified **2026-07-29**). Had it not held, the guidance would have shipped a
  fact laundered through a spec file — exactly what INV-080 forbids.
- **The per-method nesting differs, which the spec did not mention.** `search_by_attributes` returns
  `RESOLVED_ENTITIES[].ENTITY.RESOLVED_ENTITY.RECORD_SUMMARY[]`, while `find_network_*` returns
  `ENTITIES[].RESOLVED_ENTITY.RECORD_SUMMARY[]` (same call as above, plus
  `filter='find_network_by_entity_id'`). A reader told only "use `RECORD_SUMMARY[]`" would guess one
  shape and get an empty read on the other method — the very failure mode this spec exists to close
  — so both paths are named in the implemented text.
- **The `find_network` + `RECORDS[]` case is stated as a two-source coverage difference, not as the
  spec's flat "same for `SZ_FIND_NETWORK_DEFAULT_FLAGS`".** `topic='flags'` lists
  `find_network_by_entity_id` in `SZ_ENTITY_INCLUDE_RECORD_DATA`'s `applies_to` (so OR-ing the flag
  in is documented as supported), while `find_network`'s own `response_schemas` entry enumerates only
  `RECORD_SUMMARY[]` under `ENTITIES[].RESOLVED_ENTITY` and does **not** list `RECORDS[]` at all
  (both verified 2026-07-29, server 1.32.2). Per INV-169 both are recorded with their conditions and
  the reader is told to dump one raw response before relying on it, rather than flattening two
  references' differing coverage into one absolute — the error this repo has already had to retract
  twice.
- ⚠️ **An observation outside this spec's scope: `find_network` now HAS a `response_schemas` entry.**
  The implemented spec `network-link-fields-and-uncovered-response-schemas` records that
  `find_network_by_entity_id` had **no** `response_schemas` entry at all, and that
  `ENTITY_NETWORK_LINKS`' `MIN_ENTITY_ID` / `MAX_ENTITY_ID` endpoint keys had to be discovered by
  dumping a raw response. On 1.32.2 the entry exists and documents both keys explicitly
  (verified 2026-07-29). That gap is fixed upstream. Not rewritten here — reporting and proposing is
  the rule for a defect the server has since fixed; retiring that spec's guidance is a separate,
  maintainer-owned decision.

## Invariants introduced

- `INV-179` — Before writing code that reads a field from an SDK response, the guide MUST confirm
  the flag that populates **that field** is present in the composite actually in force (reading its
  `composite_members`), not merely that the field name is correct. A blank field has **three**
  causes, not two: a wrong field name, a correct field name the flags in force do not populate, or
  genuinely absent data. Extends INV-115, whose two-cause wording this corrects. (Recorded in
  `specs/INVARIANTS.md`, 2026-07-29.)
