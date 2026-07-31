# `find_path` returns `ENTITY_PATH_LINKS[]`, `find_network` returns `ENTITY_NETWORK_LINKS[]`, and step 4d warns about neither

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-07-query-visualize-discover/phase2b-discover.md` step 4d introduces `find_network`
and `find_path` together, minutes apart, and carries a detailed warning about **one** trap
between them — that a network link's endpoints are `MIN_ENTITY_ID` / `MAX_ENTITY_ID` rather
than `ENTITY_ID` / `RELATED_ENTITY_ID`. It warns about neither of the two ways the methods
actually diverge.

Verified on server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-31:

```text
get_sdk_reference(topic='response_schemas', filter='why_entities')  →
  find_network document: ENTITY_NETWORK_LINKS[].{MIN_ENTITY_ID, MAX_ENTITY_ID,
                          MATCH_KEY, MATCH_LEVEL_CODE, ERRULE_CODE, IS_AMBIGUOUS,
                          IS_DISCLOSED}
  find_path    document: ENTITY_PATH_LINKS[].{MIN_ENTITY_ID, MAX_ENTITY_ID,
                          MATCH_KEY, MATCH_LEVEL_CODE, ERRULE_CODE, IS_AMBIGUOUS,
                          IS_DISCLOSED}

get_sdk_reference(topic='flags', filter='find_network_by_entity_id')  →
  SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO: applies_to ["find_network_by_entity_id",
                                                     "find_network_by_record_id"]
```

So the **element fields are identical** and the **array name is not**, and the
matching-info flag is network-only. That combination is the trap: everything about the two
responses looks interchangeable except the one key you index by.

**What the Bootcamper sees.** The reporting entry hit exactly the failure the plugin's own
"half-populated row" rule describes (INV-148): a valid 2-degree path rendered with correct
entity names and every edge printed `(link detail not returned)`. Nothing raised. It reads
as "this path has no relationship detail", not as "wrong flags and wrong array name" — and
both were wrong simultaneously.

**Why adjacency is the aggravating factor, not a mitigation.** The closer two APIs look,
the more confidently a reader carries code between them. Step 4d teaches them in one step
and hands the reader a hard-won warning about the endpoint keys, which makes the reused
parser feel pre-validated. The report is candid that step 4d *does* say to look up
`get_sdk_reference(topic='flags', filter='find_path')` separately and that it was not done —
the instruction existed; the specific trap did not.

## Root cause

`phase2b-discover.md:40-53` documents the endpoint-key trap in detail because someone hit
it. Nothing documents the array-name divergence because nobody had hit it yet. A generic
"look it up separately" instruction does not compete with a specific, vivid warning sitting
two lines above it — a reader who has just absorbed one concrete trap reasonably believes
the concrete traps are the ones they have been told about.

## Proposed change

Extend the existing endpoint-key warning in `phase2b-discover.md` step 4d with the
divergence, in the same block, so it is read at the same moment:

- `find_network` returns its edges under `ENTITY_NETWORK_LINKS[]`; `find_path` returns them
  under `ENTITY_PATH_LINKS[]`. The **element fields are the same in both**, which is what
  makes the array name easy to carry across.
- Their matching-info flags are not interchangeable:
  `SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO` has `applies_to` of the two `find_network_*`
  methods only.
- State the consequence plainly: **neither the flags nor the parser can be shared between
  the two calls**, and a shared parser produces a path whose entities render and whose
  edges are all blank.

Cite `get_sdk_reference(topic='response_schemas', filter='find_path')` as the route, with
the server version and date. Keep the existing `MIN_ENTITY_ID` / `MAX_ENTITY_ID` warning
and the "run the lookup and dump anyway" instruction unchanged.

## Acceptance criteria

- [ ] Step 4d states that `find_path` returns `ENTITY_PATH_LINKS[]` and `find_network`
      returns `ENTITY_NETWORK_LINKS[]`, in the same block as the endpoint-key warning.
- [ ] It states that the element fields are identical between the two, since that is what
      makes the array name the only difference a shared parser would miss.
- [ ] It states that `SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO` is `find_network`-only and
      that flags cannot be shared either.
- [ ] The existing `MIN_ENTITY_ID` / `MAX_ENTITY_ID` warning and the dump-anyway
      instruction both survive.
- [ ] **Re-verification clause:** implementing this requires
      `get_sdk_reference(topic='response_schemas', filter='find_path')` to still return
      `ENTITY_PATH_LINKS[]` and `filter='find_network'` to still return
      `ENTITY_NETWORK_LINKS[]`. If the array names have converged, re-triage instead.
- [ ] `tests/test_partial_row_and_schema_coverage.py` passes; a test pins that step 4d
      names both array names, so the next reader cannot lose one.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — the step 4d endpoint-key block.
- `tests/test_partial_row_and_schema_coverage.py` — the new pin.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "find_path returns ENTITY_PATH_LINKS
  where find_network returns ENTITY_NETWORK_LINKS - the divergence is unwarned"
  (2026-07-31, Module: Query, Visualize and Discover; `Source: self-observed (assistant
  retrospective)`)
- Priority: Medium
- MCP re-check: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-31 — **still
  reproduces**, both halves confirmed. Tools: `get_sdk_reference(topic='response_schemas',
  filter='why_entities')` (which returns the find_path and find_network documents together)
  and `get_sdk_reference(topic='flags', filter='find_network_by_entity_id')`.
- Upstream: not applicable — the server documents both shapes correctly; the plugin's
  guidance is what is incomplete.
- Related specs: `specs/response-schemas-now-documents-match-info-depth.md` (the same
  block, corrected 2026-07-30), `specs/confirm-json-data-and-network-link-response-paths.md`.

## Deviations from this spec, and why (2026-07-31)

Re-verification confirmed both halves the spec asserts — server 1.32.2, docs indexed
2026-07-29 11:11 UTC. `get_sdk_reference(topic='response_schemas', filter='find_path')`
still returns `ENTITY_PATH_LINKS[]` and `filter='find_network'` still returns
`ENTITY_NETWORK_LINKS[]`; the array names have **not** converged. Four things shipped that
this spec does not say:

1. **The real root cause was a sentence the spec did not identify.**
   `phase2b-discover.md:41-42` read "For the graph methods `response_schemas` returns the
   outer arrays (`ENTITY_PATHS[]`, `ENTITIES[]`, `ENTITY_NETWORK_LINKS[]`)" — the **network**
   document's key set presented as covering *both* graph methods. `ENTITY_PATH_LINKS[]`
   appeared nowhere in the plugin. So step 4d did not merely fail to warn about the
   divergence; it stated the opposite. That sentence is now per-method.

2. **A second site, in a file this spec does not list.** The "Confirmed paths" table at
   `visualization-api-reference.md:288` listed `find_path_*` as `ENTITY_PATHS[]`,
   `ENTITIES[]` — omitting the links array entirely, while the `find_network_*` row directly
   below carried all seven link fields. Step 4d points readers at that table by name, so
   following the pointer produced *confirmation* that `find_path` has no links array. Fixed
   there too, with this session's provenance; the row's existing `1.32.2, 2026-07-30` stamp
   and the SDK 4.3.3 dump date were left untouched (INV-191).

3. **`SZ_FIND_PATH_INCLUDE_MATCHING_INFO` is named.** The spec says only that the network
   flag is network-only. "Do not use this flag" without naming the right one is unactionable,
   and the server documents a clean counterpart: `applies_to` the two `find_path_*` methods,
   `response_paths` including `ENTITY_PATH_LINKS[]`, and `SZ_FIND_PATH_DEFAULT_FLAGS` carries
   it exactly as `SZ_FIND_NETWORK_DEFAULT_FLAGS` carries the network one. Worth noting for a
   future reader: a caller who leaves the default flags alone gets links populated — the
   reported failure needs the *network* flag OR-ed in explicitly.

4. **`find_network` also returns `ENTITY_PATHS[]`.** Not in the spec, and it is the sharpest
   edge of the trap: the network response contains the word PATH, which reads as licence to
   expect `ENTITY_PATH_LINKS[]` in it. Confirmed this session in both documents'
   `detect_keys`. Stated at the step.

Beyond that, the two documents are identical apart from the links array name — every key in
`ENTITIES[]` and `ENTITY_PATHS[]` matches, and both link elements carry the same seven fields.
That is a stronger claim than "the element fields are identical" and is what the guidance now
makes.
