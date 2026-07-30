# `response_schemas` documents nesting well below the top level, including all of `MATCH_INFO`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Three shipped sites tell the guide that `get_sdk_reference(topic='response_schemas')` stops
at a method's top-level shape, and two of them name **`MATCH_INFO`** as the specific thing
it cannot reach. On server 1.32.2 that is false, and `MATCH_INFO` is documented in more
depth than almost anything else in the response.

What the plugin says now:

1. `bootcamp-onboarding/ground-rules.md:126-127` — "`response_schemas` documents the
   **top-level** shape per method; for deeper nesting (anything under `MATCH_INFO`), the
   raw-response dump is the authority."
2. `module-07-query-visualize-discover/phase1-query-visualize.md:107-108` — "documents the
   top-level shape per method; for deeper nesting (anything under `MATCH_INFO`), dump one
   raw response and read it before writing the parser."
3. `module-07-query-visualize-discover/phase2b-discover.md:40-42` — "⚠️ **Expect that
   lookup to stop at the top level here.** For the graph methods `response_schemas`
   returns the outer arrays … and **not** the fields inside a link element."

**Site 3 already contradicts itself.** Eleven lines later the same block says the element
fields *are* documented now: "`response_schemas` now documents them itself (re-verified on
MCP server 1.32.2, 2026-07-30)". A reader gets both claims in one screen.

**What the server actually returns**, `get_sdk_reference(topic='response_schemas',
filter='why_entities')` on server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30 —
paths four and five levels deep, all under `MATCH_INFO`:

```text
WHY_RESULTS[].MATCH_INFO.CANDIDATE_KEYS.NAME_KEY[].FEAT_DESC
WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.NAME[].SCORE
WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.NAME[].SCORE_BUCKET
WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.NAME[].ADDITIONAL_SCORES.GNR_FN
WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.ADDRESS[].ADDITIONAL_SCORES.FULL_SCORE
WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[].SCORE_BUCKET
WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[].FTYPE_CODE
WHY_RESULTS[].MATCH_INFO.MATCH_LEVEL_CODE / .WHY_ERRULE_CODE / .WHY_KEY
```

The same call also returned the `find_network`, `find_path` and `why_search` documents,
including `ENTITY_NETWORK_LINKS[].MIN_ENTITY_ID` / `.MAX_ENTITY_ID` — which is site 3's
claim, disproved by the same response that disproves sites 1 and 2.

**Why this matters.** These sites are the plugin's *defensive-parsing* guidance — the rule
that a blank field is a wrong field name before it is absent data. Telling the guide that
the authoritative source stops short of `MATCH_INFO` sends it to dump-and-guess for names
the server will hand over on request, and, worse, teaches that a lookup which *does*
return those paths is not to be trusted. That is the INV-169 failure mode, and this is its
third instance found in one day (after INV-132 and the `flags` topic).

**What is still true and must survive.** The dump is still the authority for what a
*particular installation* returns (INV-080/INV-149), a blank field is still a probable
wrong name, and an empty or shallow `response_schemas` result is still coverage rather
than a failed call (INV-149 — `get_version` and `get_license` both still return `data: []`,
re-verified 2026-07-30). The correction is to the claim about *where the schema stops*,
not to the discipline built on top of it.

## Root cause

The same shape as INV-132: a **negative** claim about server coverage, true when written,
that nothing re-checks. A missing capability is only discovered by trying it again, and no
test can pin "the server still cannot do X" without calling the server. Site 3 shows how
the decay looks in practice — someone verified the *specific* fields and appended a
correction, without noticing the general claim eleven lines above that the correction
falsified.

## Proposed change

Replace the "stops at the top level" premise in all three places. Keep every parsing
discipline built on it.

1. **`ground-rules.md:126-127`** — say that `response_schemas` documents nested paths
   including everything under `MATCH_INFO`, so it is the first place to check a field name;
   the raw dump remains the authority for what *this installation* returns, and for
   anything the schema does not list. Cite the server version and date.
2. **`phase1-query-visualize.md:107-108`** — the same correction, in that file's wording.
   Its surrounding point (wrong field names render blank rather than raising) is correct
   and unchanged.
3. **`phase2b-discover.md:40-42`** — delete the "expect it to stop at the top level"
   opener and fold the block into the correction that already follows it, so the passage
   states one thing. **Keep**: the `MIN_ENTITY_ID` / `MAX_ENTITY_ID` naming trap, the
   "run the lookup and dump anyway" instruction, and the INV-149 empty-is-coverage rule.

## Acceptance criteria

- [ ] No shipped file claims `response_schemas` stops at the top-level shape, or that
      `MATCH_INFO` nesting is beyond it.
- [ ] `phase2b-discover.md`'s block states one position, not two: the "expect it to stop"
      opener is gone and no sentence contradicts the correction that follows.
- [ ] All three sites still require the lookup **and** keep the raw dump as the authority
      for the installation (INV-080/INV-149) — this spec removes a false limit, not a check.
- [ ] The `MIN_ENTITY_ID` / `MAX_ENTITY_ID` naming trap survives in `phase2b-discover.md`.
- [ ] INV-149 is unchanged: an empty or shallow result is still coverage, not failure.
- [ ] **Re-verification clause:** implementing this requires
      `get_sdk_reference(topic='response_schemas', filter='why_entities')` to still return
      paths under `WHY_RESULTS[].MATCH_INFO.*`. If it no longer does, the plugin's original
      claim is right again and this spec must be re-triaged rather than implemented.
- [ ] `tests/test_partial_row_and_schema_coverage.py` and `tests/test_mcp_call_contracts.py`
      pass; any assertion quoting the removed wording is updated.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — lines 126-127.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — lines 107-108.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — lines 40-42.
- `tests/` — any assertion pinning the old wording.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 (fifth pass), ledger key
  `response-schemas-stops-at-top-level`
- Verdict: `contradicted`
- MCP evidence: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30 —
  `get_sdk_reference(topic='response_schemas', filter='why_entities')`, quoted above.
- Priority: Medium — nothing breaks today, but the guidance sends the guide away from an
  authoritative source and teaches it to distrust correct data.
- Upstream: not applicable — the server is right; the plugin is stale.
- Related specs: `specs/sdk-reference-carries-signatures-under-every-topic.md` (the same
  defect class, same day, adjacent claim), `specs/network-link-fields-and-uncovered-response-schemas.md`,
  `specs/confirm-json-data-and-network-link-response-paths.md`.

## Deviations from this spec, and why (2026-07-30)

- **A fourth site, which the spec missed.**
  `module-03b-truthset-visualization/visualization-api-reference.md:325-330` carried the same
  stale premise in its own words — "**The graph methods stop at the top level** … verified
  2026-07-26 … `ENTITY_NETWORK_LINKS[]` is described as 'Network link details between
  entities' with **no element fields**". It was found by `grep` after the three named sites
  were fixed, and corrected the same way. Notable for how it survived: the 2026-07-29 pass
  that closed this gap updated **INV-149 and the test** — `tests/test_partial_row_and_schema_coverage.py`'s
  docstring says outright that the old premise "was true on 2026-07-26 and is false on
  1.32.1" — but never updated the contract file the test guards. A correction applied to the
  rule and its test, but not to the prose, leaves the prose looking reviewed.
- **The rewrite of `phase2b-discover.md` briefly dropped a concrete instruction.** Folding the
  self-contradicting block into one position removed "Dump one raw link element and read its
  keys before writing the parser". `test_partial_row_and_schema_coverage.py::test_both_call_sites_send_the_reader_to_a_raw_dump`
  caught it — the test requires that instruction at **both** call sites, which is the right
  requirement. It was restored rather than the test relaxed: the schema says what the method
  documents, the dump says what this installation returned, and losing the second is a real
  regression even when the first improves.
