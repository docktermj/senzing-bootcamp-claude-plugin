# `get_sdk_reference` now carries argument types and flag-family membership under every topic

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin states, in three places, that `get_sdk_reference`'s `flags` and
`response_schemas` topics do not document what a method **takes**. That was true when it
was written. It is false on server 1.32.2.

What the plugin says now:

1. `specs/INVARIANTS.md`, INV-132 — "`get_sdk_reference`'s `flags` and `response_schemas`
   topics document neither the argument types **nor what a flag family selects**".
2. `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:128-129` — "The
   `flags` and `response_schemas` topics cover what a method *returns*, not what it
   *takes*".
3. `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md:67-68`
   — "⛔ **Neither of those topics tells you the ARGUMENT types** — so ask the topic that
   does".

**Both halves of the claim are now wrong**, verified twice on server 1.32.2, docs
indexed 2026-07-29 11:11 UTC, on 2026-07-30.

**Argument types.** `get_sdk_reference(topic='flags', filter='find_network_by_entity_id')`
returned a `method_signatures` block alongside the flag data, carrying every binding's
signature and the divergence warnings:

```text
python:     find_network_by_entity_id(entity_ids: List[int], max_degrees: int,
                                      build_out_degrees: int, build_out_max_entities: int,
                                      flags: int = <SZ_FIND_NETWORK_DEFAULT_FLAGS: 8589946880>) -> str
csharp:     FindNetwork(entityIDs: ISet<long>, …)
typescript: findNetwork(entityIds: number[], maxDegrees: number, buildOutDegree: number, …)
warnings:   "Argument 1 type differs across bindings — csharp: ISet<long>, java: SzEntityIds,
             python: List[int], rust: &[EntityId], typescript: number[]."
```

The same holds for the other named topic: `get_sdk_reference(topic='response_schemas',
filter='get_version')` returned `"data": []` — and still carried
`method_signatures: [{canonical: "get_version", class: "SzProduct", signatures: {python:
["get_version() -> str"], …}}]`. A topic returning *no* data of its own still returned the
signature. The tool's own description states the rule: *"Whenever 'filter' names a method,
the response carries that method's callable signature for every binding NO MATTER WHICH
TOPIC you asked for — so looking up a method's flags also tells you what it takes."*

**Flag-family selection.** Each flag entry now carries `composite_members`, `depends_on`
and `response_paths` — which is precisely "what a flag family selects". From the same
call:

```text
SZ_ENTITY_DEFAULT_FLAGS   composite_members: [SZ_ENTITY_INCLUDE_ALL_RELATIONS,
                            SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES, … 9 members]
                          response_paths: [RELATED_ENTITIES[], RESOLVED_ENTITY.ENTITY_ID,
                            RESOLVED_ENTITY.ENTITY_NAME, RESOLVED_ENTITY.RECORDS[],
                            RESOLVED_ENTITY.RECORD_SUMMARY[]]
SZ_FIND_NETWORK_DEFAULT_FLAGS
                          composite_members: [SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO,
                            SZ_ENTITY_INCLUDE_ENTITY_NAME, SZ_ENTITY_INCLUDE_RECORD_SUMMARY]
                          response_paths: [ENTITIES[], ENTITY_NETWORK_LINKS[], ENTITY_PATHS[]]
```

**Why this matters beyond tidiness.** The routing the plugin gives still works —
`topic='methods'` does return the signature — so nothing breaks today. The harm is that
the plugin tells the guide that data it can see is not there. A guide holding a `flags`
response that *contains* `method_signatures` has been instructed that this topic does not
carry argument types, and the correct reading is to distrust it. Teaching that a correct
source is unreliable is the failure mode INV-169 describes: "stating an over-generalized
absolute is worse than stating nothing". It also costs a second call for an answer
already in hand.

**This is not two conditions (INV-169 check applied).** The signature block appears when
`filter` names a method, which is exactly the case all three sites address — they are
about looking up one method before calling it. The plugin's claim is not narrowly true in
some other condition; it is false in its own use case. The precise rule is *filter-*
dependent, not topic-dependent, and the fix must say so rather than swapping one absolute
for another.

## Root cause

INV-132 was corrected in place on 2026-07-26 when the dry run disproved its original
claim that the reference could not reach parameter shapes at all. That correction added
the `topic='methods'` route but **left the premise clause standing** — the sentence
explaining *why* the other topics were insufficient was never re-checked, because the
correction was about where to go, not about what the other topics contain. The two
shipped echoes were written from the invariant and inherited the stale half.

The underlying reason the claim went stale without notice: nothing re-asks the server
about a *negative* claim. A missing capability is only ever discovered by trying it
again, and no test can pin "the server still cannot do X" without calling the server.

## Proposed change

Replace the false premise in all three places with the filter-dependent rule the server
actually implements. Keep every behavioural instruction that is still correct.

1. **`specs/INVARIANTS.md`, INV-132** — edit the premise clause in place (a clarification
   of fact, not a change of meaning; the MUST is unchanged, so this needs no new ID per
   `INVARIANTS.md`'s own rules). It should say that `get_sdk_reference` returns the
   binding's signature under **any** topic whenever `filter` names a method, and that
   flag entries carry `composite_members` / `depends_on` / `response_paths`. Add the
   dated provenance, in the style of the existing in-place corrections there. The
   operative requirement — confirm the parameter shape for the Bootcamper's binding
   before writing a call, and never treat cross-language documentation as authoritative
   — is unaffected and stays exactly as it is; the server's own `warnings` block now
   reinforces it.
2. **`ground-rules.md:128-131`** — replace "cover what a method *returns*, not what it
   *takes*" with the filter rule. `topic='methods'` stays documented as the direct route;
   the addition is that a `flags` or `response_schemas` response already in hand carries
   the signature, so no second call is needed for it.
3. **`phase2b-discover.md:67-68`** — the ⛔ block becomes "these responses carry the
   signature too when `filter` names the method; read the one for the Bootcamper's
   binding". The Python-specific warning that follows it (native collections, not an
   entity-IDs JSON document) is **still correct and must stay** — the server's own
   `warnings` confirm `python: List[int]` against `java: SzEntityIds`.

**What stays everywhere:** the requirement to look the shape up, the per-binding rule,
and the "cross-language documentation is not authoritative" warning. This spec narrows a
false factual premise; it does not relax a single discipline.

**Opportunity, not required by this spec:** wherever the plugin tells the guide to
determine what a composite flag pulls into a response by dumping a raw response, the
flags entry's `response_paths` now answers it directly. Worth a follow-up sweep of the
flag-related guidance; out of scope here to keep this spec to one fix.

## Acceptance criteria

- [ ] No shipped file or invariant states that `flags` or `response_schemas` cannot
      report argument types, or that they do not document what a flag family selects.
- [ ] All three sites state the **filter-dependent** rule: a method-named `filter`
      returns `method_signatures` under any topic. None of them replaces the old absolute
      with a new one.
- [ ] INV-132's MUST is unchanged, its ID is not renumbered, and the in-place correction
      carries its date and server version (1.32.2, 2026-07-30).
- [ ] `phase2b-discover.md`'s Python `List[int]` warning survives the edit.
- [ ] **Re-verification clause:** implementing this requires
      `get_sdk_reference(topic='flags', filter='find_network_by_entity_id')` to still
      return a `method_signatures` block, and `topic='response_schemas', filter='get_version'`
      to still return one alongside an empty `data` array. If either no longer does, this
      spec is wrong — re-triage rather than implement.
- [ ] `tests/test_mcp_call_contracts.py` and `tests/test_sdk_parameter_shapes.py` pass;
      any assertion quoting the removed wording is updated to assert the new rule.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-132's premise clause (in-place correction, no renumber).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — lines 128-131.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md`
  — the ⛔ block at 67-68.
- `tests/test_mcp_call_contracts.py`, `tests/test_sdk_parameter_shapes.py` — any assertion
  pinning the old wording.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 (first run), ledger keys
  `inv132-topics-omit-argument-types` and `inv132-flag-family-selection-undocumented`
- Verdict: `contradicted`
- MCP evidence: `get_capabilities` → server 1.32.2; `search_docs` → docs indexed
  2026-07-29 11:11 UTC; `get_sdk_reference(topic='flags',
  filter='find_network_by_entity_id')` and `get_sdk_reference(topic='response_schemas',
  filter='get_version')`, both 2026-07-30, both returning `method_signatures`. Quoted above.
- Priority: Medium — nothing breaks today; the defect is that the plugin teaches the guide
  to distrust correct data, and costs a redundant call.
- Upstream: not applicable — the server is right here; the plugin is stale.
- Related specs: `specs/verify-sdk-parameter-shapes-and-flag-families.md` (established
  INV-132; this corrects the premise clause that correction left standing),
  `specs/confirm-json-data-and-network-link-response-paths.md`,
  `specs/network-link-fields-and-uncovered-response-schemas.md`.
