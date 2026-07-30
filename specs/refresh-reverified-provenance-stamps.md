# Refresh provenance stamps that re-verified unchanged, and correct one that misdescribes its own call

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Sixteen shipped sites carry a dated provenance stamp naming **MCP server 1.32.1**. The
server is now at **1.32.2**, so every one of those stamps is expired: a reader cannot
tell a fact that is still true from one nobody has re-checked since the version bumped.
The stamps are the plugin's own mechanism for making Senzing claims auditable (INV-080),
and an expired stamp quietly stops doing that job — it still *looks* like provenance.

The `delegate-to-mcp-server` sweep of 2026-07-30 re-asked the server for three of them.
All three facts **re-verified unchanged**, so the text is right and only the stamp is
stale:

1. `module-03b-truthset-visualization/phase1-visualization.md:95` — "`dataset='list'`
   returns **four** datasets — the three CORD collections plus `truthset`
   (`available: true`)". Confirmed: `get_sample_data(dataset='list')` returned
   `las-vegas`, `london`, `moscow`, `truthset`, all `available: true`.
2. `module-03b-truthset-visualization/SKILL.md:81` — "`truthset` is listed with
   `available: true` alongside the three CORD collections, so the fallback is
   exceptional, not routine". Confirmed by the same call.
3. `module-05-data-quality-mapping/phase1-quality-assessment.md:124` — the
   data-source-registration prerequisite for `get_record_preview` is "**not** documented
   on the method". Confirmed: `get_sdk_reference(topic='parameters',
   filter='getRecordPreview', language='python')` returned
   `get_record_preview(record_definition: str, flags: int = <SZ_ENTITY_INCLUDE_RECORD_FEATURE_DETAILS>)`
   with no mention of the prerequisite anywhere in the response.

A second pass the same day re-asked two more claims, spanning four further stamps.
These also **re-verified unchanged**:

4. `module-02-sdk-setup/SKILL.md:710` and
   `module-03-system-verification/phase1-verification.md:137` — `SENZ2027`'s own
   resolution steps do not name the missing-runtime-data-directory cause, which is why
   the plugin adds it from the Senzing FAQ. Confirmed, and it is starker than the plugin
   states: `explain_error_code('SENZ2027')` returns the placeholder
   `common_causes: ["Error class: SzError — consult Senzing documentation for details"]`
   and three generic `resolution_steps` ("Check Senzing documentation", "Enable verbose
   logging", "Search Senzing support forums"). Compare `SENZ2207`, which returns four
   specific causes and four actionable steps — so this is a per-code stub, not a
   uniformly thin tool.
5. `module-03b-truthset-visualization/visualization-api-reference.md:341` and
   `module-07-query-visualize-discover/phase2b-discover.md:50` — `response_schemas` now
   documents the `ENTITY_NETWORK_LINKS` element fields itself. Confirmed:
   `get_sdk_reference(topic='response_schemas', filter='find_network')` returned all
   seven — `MIN_ENTITY_ID`, `MAX_ENTITY_ID`, `MATCH_KEY`, `MATCH_LEVEL_CODE`,
   `ERRULE_CODE`, `IS_AMBIGUOUS`, `IS_DISCLOSED` — plus
   `ENTITIES[].RESOLVED_ENTITY.{ENTITY_ID,ENTITY_NAME,RECORD_SUMMARY[]}` and
   `ENTITY_PATHS[].{START_ENTITY_ID,END_ENTITY_ID,ENTITIES[]}`.

A third pass re-asked three more, all **unchanged**:

6. `module-06-data-processing/phaseD-validation.md:13` — a **verbatim quote** of
   `reporting_guide`'s schema notes. Matches word-for-word:
   `reporting_guide(topic='data_mart', language='python', scale='poc')` returns
   `schema.description` beginning *"IMPORTANT: These tables are NOT part of the Senzing
   SDK and do NOT exist out of the box. They must be created and maintained by a separate
   data mart replication pipeline that YOU build and operate."*
7. `module-03b-truthset-visualization/visualization-api-reference.md:289` — the
   `find_network_*` row of the MCP-confirmed response-paths table
   (`ENTITY_PATHS[]`, `ENTITIES[]`, `ENTITY_NETWORK_LINKS[]`). Covered by the same
   `response_schemas` evidence as site 5.
8. `bootcamp-onboarding/ground-rules.md:100` — `find_examples` retrieval returns an empty
   `content`. Still reproduces (`content: ""` against `content_length: 20706`), so the
   claim stands and only the stamp is stale. Ledger keys `inv160-*`.

**One of the first three also misdescribes its own call.** Site 3 says the lookup "returns both
overloads for every binding". It does not. The response carried two entries because the
filter matched two *different methods* — `get_record` (`variant: "record_id"`) and
`get_record_preview` (`variant: null`) — and `get_record_preview` has exactly **one**
signature per binding. The load-bearing claim (the prerequisite is undocumented, so
register the source code first) is correct and unaffected; the sentence describing what
the call returns is not.

## Root cause

A stamp records when a fact was last checked, but nothing re-checks it. Only a sweep
against the live server can move one, and until 2026-07-30 there was no sweep — so
stamps accumulated at whatever version was current the day they were written. The
`get_record_preview` wording is a separate, ordinary slip: the response was read for the
fact it was fetched for, and the incidental second match was described from a glance.

## Proposed change

1. **Update the ten verified stamps to `MCP server 1.32.2, 2026-07-30`.** Change the
   version and date only — the surrounding claims re-verified unchanged and their wording
   stays exactly as it is, including the "re-verify rather than trusting this note"
   instructions, which are what make these sites correct in the first place.
2. **Fix site 3's description of its own call.** Replace "returns both overloads for every
   binding" with what the response actually contains: a single `get_record_preview`
   signature per binding, `record_definition` plus `flags`, and no prerequisite. Keep the
   order it prescribes (register the source codes from `sdk_guide(topic='configure')`,
   then preview) — that is correct and is the point of the passage.
3. **Leave the remaining six 1.32.1 stamps alone.** They were not re-asked in this
   sweep, and changing a stamp without re-verifying its claim is worse than leaving it
   expired: it would assert a check that never happened. They are listed below so the
   next sweep can pick them up.

**Not in scope:** the recurring half of this problem. Stamps will expire again on the
next server bump, and refreshing them is exactly what `delegate-to-mcp-server` does. This
spec clears the ten that are already verified; it does not try to automate the rest.

## Acceptance criteria

- [ ] The ten sites named above carry `MCP server 1.32.2, 2026-07-30`, and their claims
      are otherwise byte-identical to what ships today.
- [ ] `phase1-quality-assessment.md:124` no longer says the lookup returns "both
      overloads"; it describes the single `get_record_preview` signature and its two
      parameters.
- [ ] The register-then-preview ordering and the `sdk_guide(topic='configure')` sourcing
      instruction survive the edit unchanged.
- [ ] No stamp is advanced for a claim this spec did not re-verify — the remaining six
      1.32.1 stamps still read 1.32.1.
- [ ] **Re-verification clause:** implementing this requires, all on the current server:
      `get_sample_data(dataset='list')` to return exactly those four datasets with
      `truthset` available; `get_sdk_reference(topic='parameters', filter='getRecordPreview')`
      to document no registration prerequisite; `explain_error_code('SENZ2027')` to still
      return a placeholder cause and generic steps; and
      `get_sdk_reference(topic='response_schemas', filter='find_network')` to still return
      all seven `ENTITY_NETWORK_LINKS` element fields. Where one has changed, the fact —
      not the stamp — is what needs updating, and that site should be re-triaged instead
      of restamped.
- [ ] `tests/test_truthset_acquisition_call.py` and
      `tests/test_record_preview_requires_registered_source.py`-equivalent assertions pass;
      any that quote the edited wording are updated.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — stamp at line 95.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/SKILL.md` — stamp at line 81.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — stamp and wording at line 124.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — stamp at line 710.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — stamp at line 137.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — stamp at line 341.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — stamp at line 50.
- `tests/` — any assertion quoting the edited sentence.

### Still expired, not re-asked in any of the three passes

- `module-02-sdk-setup/SKILL.md` (385, 789, 871) and
  `module-03-system-verification/phase1-verification.md` (132) — snippet-guard and
  `sdk_guide(topic='configure')` sequence claims. Checkable, just not reached.
- `module-05-data-quality-mapping/phase1-quality-assessment.md` (254) — the
  PERSON/ORGANIZATION feature-applicability table. Checkable via
  `search_docs(category='data_mapping')`.
- `module-05-data-quality-mapping/phase2-data-mapping.md` (344) — **not checkable from
  MCP alone.** The claim is about how the MCP-delivered `sz_verbatim_check.py` behaves on
  numeric source values, which needs the validator run against data, not a tool response.
  Leave the stamp until a run can produce the evidence (INV-163: a check that cannot run
  is recorded as skipped, never as passed).

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 (first run, two passes), ledger keys
  `sample-data-list-returns-four-datasets`, `truthset-listed-available-in-sample-data`,
  `record-preview-registration-prerequisite-undocumented`,
  `senz2027-explain-error-code-is-a-stub`, `find-network-link-element-fields-documented`,
  `data-mart-tables-not-in-sdk-quote`, `inv160-find-examples-empty-content`
- Verdict: `keep-by-design` (sites 1-2, 5), `keep-server-lacks-it` (sites 3-4) — every
  claim survives; this spec updates provenance, not content
- MCP evidence: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30 —
  `get_sample_data(dataset='list')`; `get_sdk_reference(topic='parameters',
  filter='getRecordPreview', language='python')`; `explain_error_code('SENZ2027')`;
  `get_sdk_reference(topic='response_schemas', filter='find_network')`;
  `reporting_guide(topic='data_mart', language='python', scale='poc')`;
  `find_examples(repo=…, file_path=…)`. Quoted above.
- Priority: Low — no claim is wrong; the audit trail is stale and one sentence
  misdescribes its own call.
- Upstream: not applicable for sites 1-2. Site 3 is a genuine documentation gap on
  Senzing's side (a method whose undocumented prerequisite fails with `SENZ2207`) and is a
  reasonable `feature` request; not filed, pending the maintainer's decision.
- Related specs: `specs/record-preview-requires-registered-source.md` (established the
  register-then-preview rule this spec preserves),
  `specs/sdk-reference-carries-signatures-under-every-topic.md` (the same sweep's
  `contradicted` finding).
