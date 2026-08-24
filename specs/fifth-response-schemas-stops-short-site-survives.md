# A fifth "`response_schemas` does not document this" site survived the pass that corrected the other four

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-03b-truthset-visualization/visualization-api-reference.md:321-323` still says:

> Field names *inside* those `CONFIRMATIONS` entries, and the exact `FEATURE_SCORES` path, are
> **not** documented by `response_schemas` — dump a raw response to confirm them. Do not copy
> field names from any prior implementation, this file included.

Both named things are documented, and **this repo already proved it twelve days ago.**
`specs/response-schemas-now-documents-match-info-depth.md` — implemented 2026-07-30, recorded in
`specs/IMPLEMENTED.md` — quotes, from `get_sdk_reference(topic='response_schemas',
filter='why_entities')` on server 1.32.2:

```text
WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[].SCORE_BUCKET
WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[].FTYPE_CODE
WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.NAME[].SCORE_BUCKET
WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.NAME[].ADDITIONAL_SCORES.GNR_FN
```

Those are the `CONFIRMATIONS` field names and the exact `FEATURE_SCORES` path, in the same file's
own evidence. **Re-confirmed on server 1.32.8, docs index 2026-08-11 13:35 UTC, 2026-08-11** — the
same call now also returns the `CONFIRMATIONS[]` members `TOKEN`, `SOURCE`, `SCORE`,
`SCORE_BEHAVIOR`, `CANDIDATE_FEAT_USAGE_TYPE`, `INBOUND_FEAT_*` and `ADDITIONAL_SCORES.*`, and
`FEATURE_SCORES` per family (`NAME[]`, `ADDRESS[]`, `DOB[]`, `PHONE[]`, `RECORD_TYPE[]`).

The same page's `why_entities` table row at `:285` is stale for the same reason: it lists only
"`WHY_RESULTS[]` (carries `MATCH_INFO`), `ENTITIES[]`".

**This is not a server-drift finding.** The server did not change under the plugin; it was already
this deep at 1.32.2. The claim was disproved, corrected in **four** places, and a fifth instance
shipped on. Verdict: **`contradicted`**.

**INV-169 applied.** Not a conditions mismatch — the claim is about what `response_schemas`
documents, and `response_schemas` is exactly the tool asked, with the filter the claim concerns.

## Root cause

**The grep that caught the fourth site could not catch the fifth.** The 2026-07-30 deviation note
records that site four was "found by `grep` after the three named sites were fixed" — it phrased the
premise as "**The graph methods stop at the top level**". Sites 1-3 said "stops at the top-level
shape". This fifth site says none of that: it makes the same claim as a **negative about two named
fields**, with no shared phrase to grep for.

That is the general lesson and it is worth more than the fix. The 2026-07-30 pass already recorded
one instance of this shape — a correction applied to INV-149 and its test but not to the prose those
guard. This is the same failure one level down: a correction applied to four phrasings of a claim,
but not to a fifth phrasing of the same claim. **A negative claim about server coverage cannot be
swept by phrase**, because the phrasing is what varies; it has to be swept by *subject* — every place
the plugin says the server does not document something.

## Proposed change

1. **Replace the sentence at `:321-323`** with the lookup that answers it:
   `get_sdk_reference(topic='response_schemas', filter='why_entities')`, reading the `data[]` entry
   whose `id` is `why_entities`; its `fields[]` carries `path` and `field_type` for the full
   `MATCH_INFO` interior, `CONFIRMATIONS` members and `FEATURE_SCORES` families included.
2. **Keep the instruction that follows it** — "Do not copy field names from any prior
   implementation, this file included" — which is correct and is the reason this page survives being
   wrong. Keep the raw dump as the authority for what *this installation* returns (INV-080/INV-149);
   it moves from primary to fallback, exactly as the 2026-07-30 pass did for the other four sites.
3. **Update the `why_entities` table row at `:285`** to name the interior, dated and explicitly
   partial, in the shape the page already uses at `:290` for `find_network_*`.
4. **Do not touch** the `WHY_KEY_DETAILS` vs `MATCH_KEY_DETAILS` asymmetry, the `JSON_DATA` trap at
   `:294-305`, or the `find_path_*` / `find_network_*` provenance stamps — this spec re-asked
   `filter='why_entities'` only, and INV-191 forbids advancing a stamp for a claim not re-checked.

**Sweep for a sixth.** Before implementing, grep the plugin by *subject* rather than by phrase — for
example `grep -rn "not documented\|undocumented\|does not document\|stops at\|beyond it" plugins/`
— and list every negative claim about MCP coverage found, whether or not it concerns
`response_schemas`. Each one is a fact with a short shelf life and no test can pin it. Fix any that
are stale in the same change, and record the sweep in the implementation entry so the next pass
knows the subject-level sweep has been done once.

**Fallback (INV-125).** None needed: the raw dump the sentence currently mandates becomes the
documented fallback, so no quality gate is removed.

## Acceptance criteria

- [ ] `visualization-api-reference.md:321-323` no longer claims `CONFIRMATIONS` field names or the
      `FEATURE_SCORES` path are undocumented by `response_schemas`.
- [ ] The step names the call and what to extract (`data[].fields[].path`), not merely "ask MCP".
- [ ] "Do not copy field names from any prior implementation, this file included" is retained, and
      the raw dump is retained as the fallback (INV-080/INV-149).
- [ ] The `why_entities` table row at `:285` names the documented interior, dated and marked partial.
- [ ] A **subject-level** sweep for other negative claims about MCP coverage was run, its command
      recorded, and every stale hit fixed in the same change or explicitly listed as re-verified.
- [ ] **Re-verification clause:** implementing this requires
      `get_sdk_reference(topic='response_schemas', filter='why_entities')` to still return paths under
      `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[]` and
      `WHY_RESULTS[].MATCH_INFO.FEATURE_SCORES.*`. If it has shallowed, re-triage instead.
- [ ] The `find_path_*` / `find_network_*` stamps are **not** advanced, and the
      `MATCH_KEY_DETAILS` asymmetry is unchanged (INV-191).
- [ ] `tests/test_partial_row_and_schema_coverage.py` still passes, including
      `test_both_call_sites_send_the_reader_to_a_raw_dump` — the 2026-07-30 pass shows this test
      catches a dropped dump instruction, and it must keep doing so.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — `:285` and `:321-323`.
- `tests/` — only if an assertion pins the removed sentence.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-08-11. Server **1.32.8** (was 1.32.2), docs index
  **2026-08-11 13:35 UTC** (was 2026-07-29 11:11 UTC) — both axes moved, but **this finding does not
  depend on either having moved**: the claim was already false at 1.32.2.
- Tools called: `get_capabilities`, `get_sdk_reference(topic='response_schemas', filter='why_entities')`.
- Verdict: `contradicted`, ledger key `response-schemas-stops-at-top-level`.
- Priority: **Medium.** No Bootcamper is misled into a wrong action — dumping a raw response yields
  correct field names — but the page whose job is to be authoritative about response shapes carries a
  claim this repo disproved and acted on twelve days ago, which is worse for trust than never having
  checked.
- Upstream: not applicable — the server is right; the plugin is stale.
- Related specs: `specs/response-schemas-now-documents-match-info-depth.md` (implemented 2026-07-30;
  corrected sites 1-4 and recorded the fourth as a deviation — **this is the fifth**),
  `specs/confirm-json-data-and-network-link-response-paths.md`,
  `specs/find-path-and-find-network-links-diverge.md`.

## Deviations from this spec, and why (2026-08-11)

**The subject-level sweep the spec required found the site the spec was about only on the second
attempt — which is the spec's own thesis, demonstrated.** The command the spec suggested
(`grep -rn "not documented\\|undocumented\\|..." plugins/`) returned 6 hits and **missed
`visualization-api-reference.md:322`**, because that line reads `are **not** documented` — the
emphasis markers split the phrase. Re-running with emphasis and backticks stripped before matching
returned **18** hits. The sweep that shipped is therefore the normalized one:

```bash
python3 - <<'EOF'
import re, pathlib
pat = re.compile(r"(not|never|no longer|cannot|does not|doesn't)\\s+"
                 r"(document|documented|documents|cover|covered|covers|reach|list|listed)", re.I)
for p in sorted(pathlib.Path("plugins").rglob("*.md")):
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        flat = line.replace("*", "").replace("`", "")
        if pat.search(flat):
            print(f"{p}:{i}  {flat.strip()[:118]}")
EOF
```

**Of the 18, one other was re-verified and its stamp refreshed:**
`module-05-data-quality-mapping/phase1-quality-assessment.md:133` — "the prerequisite is not
documented on the method". Re-asked `get_sdk_reference(topic='parameters', filter='getRecordPreview')`
on 1.32.8, 2026-08-11: **still true**, so the claim stands and the stamp advanced from 1.32.2 to
1.32.8 — permitted under INV-191 because the claim was actually re-checked.

**Five negative-coverage claims were found and NOT re-checked this run.** They are listed rather
than silently passed, per the criterion:

- `module-02-sdk-setup/SKILL.md:259` — "version-exact install is not documented by the server"
- `module-02-sdk-setup/SKILL.md:288` — "undocumented, not known to be unnecessary"
- `module-03b-truthset-visualization/visualization-api-reference.md:112` and
  `module-06-data-processing/phaseD-validation.md:225` — relationship flags "do not list the export
  methods" in `applies_to` (ledger `relationship-flags-omit-export-methods`, keep-by-design)
- `module-07-query-visualize-discover/phase1-query-visualize.md:134` — "it does not list `RECORDS[]`
  at all", stamped 2026-07-29

Each is a negative claim about server coverage with no test able to pin it, and each is stamped
against 1.32.2 or earlier while the server is now 1.32.8. They are the natural next sweep.

**Stamps deliberately not advanced (INV-191).** The `find_path_*` and `find_network_*` rows in the
same table, and the `WHY_KEY_DETAILS` vs `MATCH_KEY_DETAILS` asymmetry, were not re-asked here —
`filter='how_entity'` was never called — so their dates stand as written.
