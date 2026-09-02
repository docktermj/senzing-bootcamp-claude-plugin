# Restamp all 27 MCP negatives to server 1.36.0, correcting two drifted rationales

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Senzing MCP server is at **1.36.0**. The newest marker in the plugin was recorded
against **1.35.4**, so `coverage_reports.py negatives --server 1.36.0` reports **27 markers
— 27 DUE, 0 current**. Nineteen were recorded against **1.33.0** (2026-08-21).

A DUE marker is not itself a defect, but nothing in the offline suite (INV-108) notices a
negative going stale, so the whole set has to be re-asked individually before any of it can
be trusted.

## Root cause

Not a plugin defect — the server shipped three minor versions (1.33.0 → 1.36.0) while the
plugin's dated tool-absence claims stayed where they were. This spec records the re-ask and
the two corrections it produced.

**Re-ask outcome, MCP server 1.36.0, 2026-09-02 — all 25 re-asked claims still hold. No
negative turned false.** Per `.claude/skills/dry-run/phase1-mcp-contracts.md`, a re-ask has
three outcomes; the split was:

**Claim true, rationale reproduces (23)** — restamp only:

| Site | Route re-asked |
|---|---|
| `bootcamp-onboarding/ground-rules.md:294` | declared schemas of `find_examples` / `generate_scaffold` / `download_resource` |
| `bootcamp-preparation/SKILL.md:272` | `sdk_guide(topic='install', platform=…)` |
| `module-02-sdk-setup/SKILL.md:225` | `sdk_guide(install, macos_arm)` + `(install, windows)` |
| `module-02-sdk-setup/SKILL.md:229` | `sdk_guide(install, linux_apt)` |
| `module-02-sdk-setup/SKILL.md:252` | `sdk_guide(install, macos_arm)` |
| `module-02-sdk-setup/SKILL.md:278` | `sdk_guide(install, windows)` |
| `module-02-sdk-setup/SKILL.md:994` | `sdk_guide(install, macos_arm, python)` |
| `module-02-sdk-setup/SKILL.md:1065` | `generate_scaffold` declared schema + its `access_steps` step 3 |
| `module-02-sdk-setup/SKILL.md:1085` | `sdk_guide(load, python, record_count=1000)` |
| `module-02-sdk-setup/SKILL.md:1214` | `search_docs('evaluation license record limit…')` + `explain_error_code('SENZ9000')` |
| `module-02-sdk-setup/SKILL.md:1475` | `sdk_guide(configure, python)` vs `(configure, linux_apt, python)` |
| `module-02-sdk-setup/SKILL.md:1550` | `sdk_guide(install, macos_arm, python)` |
| `module-02-sdk-setup/SKILL.md:887` | `sdk_guide(install, linux_apt, java)` |
| `module-02-sdk-setup/SKILL.md:127` | `search_docs('szBuildVersion.json…')` + `sdk_guide(install, windows)` gotchas |
| `module-02-sdk-setup/SKILL.md:387` | `search_docs('upgrade … 4.3 to 4.4 procedure')` + `sdk_guide` topic enum |
| `module-03-system-verification/phase1-verification.md:251` | `generate_scaffold(python, initialize)` |
| `module-04-data-collection/SKILL.md:1085` | `sdk_guide(load, python, record_count=19500)` + `search_docs('hardware sizing…')` |
| `module-05-data-quality-mapping/SKILL.md:82` | `search_docs('globalization')` + the `category='globalization'` owner |
| `module-05-data-quality-mapping/SKILL.md:83` | `search_docs('multi-language data quality best practices')` + owner |
| `module-06-data-processing/phaseA-build-loading.md:318` | `sdk_guide(configure, python, data_sources=[…])` |
| `module-07-query-visualize-discover/phase1-query-visualize.md:220` | `get_sdk_reference(flags, SZ_ENTITY_INCLUDE_ALL_RELATIONS, java)` |
| `module-07-query-visualize-discover/phase1-query-visualize.md:421` | `get_sdk_reference(response_schemas, why_entities, python)` |
| `scripts/senzing_viz_server.py:1876` | `get_sdk_reference(flags, SZ_ENTITY_INCLUDE_ALL_RELATIONS)` + `SZ_ENTITY_DEFAULT_FLAGS` owner |

Several rationales reproduced **verbatim**, including the ones most worth trusting:
`SENZING_LICENSE_FILE` "place the license file at the path specified by `SENZING_LICENSE_FILE`
or in the `etc/` directory"; `explain_error_code('SENZ9000')`'s "default 500-DSR free tier";
`SZ_ENTITY_DEFAULT_FLAGS`' five `response_paths` in order; and the `WHY_KEY` /
`WHY_ERRULE_CODE` / `WHY_KEY_DETAILS` trio with `requires_flags` on only the third.

**Claim true, rationale does NOT reproduce (2)** — correct the rationale in the same edit as
the restamp:

1. **`specs/DECLINED.md:126`** — census-shaped, and already flagged by
   `coverage_reports.py negatives` as such (`⚠️ CENSUS-SHAPED rationales: 1 — '10 hits'`). The
   count survived: still exactly **10 hits** at the default `max_results`, and no document
   names `sz-mcp-coworker`, so the claim holds. The **composition drifted**: the rationale
   describes "every one unrelated: a Scala `SelfCheck.scala` in `brianmacy/sz_spark`, the
   `@senzing/sdk-*` npm prebuilt-binary tables, assorted loaders", but **three of the ten
   hits are now a new document, "Enabling the Per-Entity Feature Store & Advisory Locking in
   Senzing 4.4.0"**, which is neither an npm table nor a loader. The enumeration no longer
   describes the response.

2. **`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:719`**
   — the rationale says the route "returned the *Payload attributes (optional)* and *Mapping
   identifiers* sections". At 1.36.0 it returns *Payload attributes (optional)*, ***Attributes
   for the record key*** and ***Attribute reference*** (plus a DSR-pricing hit); **there is no
   *Mapping identifiers* section in the response.** The claim still holds — nothing states
   precedence for a colliding root-level key — but the sections cited as establishing it are
   not the ones returned. Notably *Attribute reference* now states *"Only the attributes listed
   here may appear inside a feature object. Anything else is treated as payload"*, which is a
   rule for the **inside-a-feature-object** case and sharpens why the **record-root** case is
   still unanswered.

**Not re-asked this run (2), so still DUE** — both need a `mapping_workflow` drive, which the
2026-09-02 run did not perform (its phase-3 walk started at Data processing, past Module 5):

- `module-05-data-quality-mapping/phase2-data-mapping.md:359` — step-2 instructions never name
  the required `embedded_in` key.
- `specs/DECLINED.md:135` — the `explain_error_code('SENZ9000')` half of its owner clause
  **was** re-verified (it still names `sz-mcp-coworker selfcheck (airgap binary)`); the
  `mapping_workflow(action='start')` step-1 stdio/airgap half was not.

Also unverified: `module-07-query-visualize-discover/phase1-query-visualize.md:220`'s
sub-claim that the response is **byte-identical with and without** `language`. The field-shape
half was confirmed (no row names a binding or argument types); the identity half was not
re-tested.

## Proposed change

1. Restamp the **23** reproduce-cleanly markers to `server 1.36.0, 2026-09-02`, leaving claim
   and rationale text unchanged.
2. Restamp the **2** drifted markers to `server 1.36.0, 2026-09-02` **and** rewrite their
   rationales in the same edit:
   - `DECLINED.md:126` — replace the hit enumeration with the discriminating property:
     *no hit's title, section or `source_url` contains the string `sz-mcp-coworker`* (which is
     what the claim actually rests on and survives an index rebuild). Keep the count only if it
     is stated as incidental.
   - `phase2-data-mapping.md:719` — cite the sections actually returned, and add that
     *Attribute reference* states the in-feature-object rule while stating no record-root
     precedence, since that contrast is now the strongest support for the negative.
3. Leave the **2** un-re-asked markers at their current stamps. ⛔ Do not restamp them — a
   stamp they did not earn is exactly the "re-dating in bulk makes every marker look reviewed"
   failure the report warns about. They stay DUE for the next run.

## Acceptance criteria

- [ ] `coverage_reports.py negatives --server 1.36.0` reports **2 DUE, 25 current** — the two
      un-re-asked markers still DUE, everything re-asked current.
- [ ] `DECLINED.md:126`'s rationale names a property (no hit names `sz-mcp-coworker`) rather
      than an enumeration of what the hits happened to be, and the run's census warning no
      longer fires on it.
- [ ] `phase2-data-mapping.md:719`'s rationale names only sections the route currently returns,
      and no longer cites *Mapping identifiers*.
- [ ] No marker's **claim** text changed — all 25 re-asked claims held, so a claim edit in this
      spec's diff is a mistake.
- [ ] `tests/test_mcp_negative_rationale_shape.py` still passes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — restamp
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — restamp
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — restamp (11 markers)
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — restamp
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — restamp
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md` — restamp (2 markers)
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — restamp + rationale rewrite at `:719`; leave `:359` alone
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — restamp
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — restamp (2 markers)
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — restamp
- `specs/DECLINED.md` — restamp + rationale rewrite at `:126`; leave `:135` alone

## Source

- Feedback: `/dry-run` phase 1, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **server 1.36.0, 2026-09-02 — 25 of 27 negatives re-asked individually; every claim still holds; 2 rationales drifted and are corrected here; 2 markers not re-asked and deliberately left DUE.** Tools called: `get_capabilities`, `sdk_guide` (install × linux_apt/macos_arm/windows/macos_arm+python/linux_apt+java, configure × python/linux_apt+python/python+data_sources, load × record_count 1000/19500), `search_docs` (9 queries incl. `category` = `sdk`/`globalization`/`data_mapping`), `generate_scaffold(python, initialize)`, `explain_error_code('SENZ9000')`, `get_sdk_reference` (flags × SZ_ENTITY_INCLUDE_ALL_RELATIONS ±language, response_schemas × why_entities). Every absence claim here carries its own `owner:` clause in the marker itself, and each owner route was re-asked alongside its claim.
- Upstream: not applicable — no negative turned false, so nothing to report.
- Related specs: `specs/mcp-negative-markers-carry-rationale-nothing-reverifies.md` (implemented 2026-09-01; its census warning correctly caught one of the two drifts), `specs/census-detector-misses-enumerated-name-lists.md` (the gap that let the other one through)


## Deviations from this spec, and why (2026-09-02)

1. **All 25 claims were re-asked again at implementation time rather than restamped on this spec's
   record — because the stamp IS the certification.** The spec records a re-ask performed earlier the
   same day at the same server version, so trusting it would have produced the identical stamp. It was
   re-asked anyway: `implement-spec` Step 3.3 forbids copying a Senzing fact out of a spec into shipped
   text without re-confirming it, and writing *"server 1.36.0, 2026-09-02"* into 25 markers is exactly
   that — a claim that someone asked. Restamping on the spec's word would have been the
   *"re-dating in bulk makes every marker look reviewed"* failure the report itself warns about, with
   the spec file supplying the appearance of review. **Outcome: 25 of 25 claims still hold, 2
   rationales drifted — the spec's finding reproduced exactly.** Routes re-asked: `get_capabilities`;
   the declared schemas of `find_examples` / `generate_scaffold` / `download_resource` via
   `ToolSearch`; `sdk_guide` install × macos_arm, windows, linux_apt, macos_arm+python,
   linux_apt+java; `sdk_guide` configure × python and python+data_sources; `sdk_guide` load × python
   at record_count 1000 and 19500; `search_docs` × 8 queries (globalization ×2 incl.
   `category='globalization'`, multi-language ×2, evaluation-license, szBuildVersion, 4.3→4.4 upgrade,
   sz-mcp-coworker, hardware-sizing, payload-precedence); `generate_scaffold(python, initialize)`;
   `explain_error_code('SENZ9000')`; `get_sdk_reference` flags × `SZ_ENTITY_INCLUDE_ALL_RELATIONS`
   with and without `language`, and response_schemas × `why_entities`. A per-marker verdict log was
   written to disk as the re-ask proceeded, so a compaction could not cost the evidence the stamps
   rest on.

2. **28 markers, not 27 — so the criterion's arithmetic moved.** Criterion 1 asks for
   *"2 DUE, 25 current"*. `phaseB-load-first-source.md:66` was added by
   `proceed-on-sqlite-keeps-the-tier-s-thread-count` **after** this spec was written and was already
   stamped 1.36.0/2026-09-02. The report now reads **28 markers — 2 DUE, 26 current**: the same 25
   restamped here, plus that one. The two DUE are exactly the two the spec names
   (`phase2-data-mapping.md:359`, `DECLINED.md:135`), verified by name rather than by count.

3. **Criterion 4 is satisfied in substance but not literally, and the spec contradicts itself here.**
   Criterion 4 says *"No marker's **claim** text changed."* Proposed change 2 says to replace
   `DECLINED.md:126`'s hit enumeration — **which sits inside that marker's claim half**, not its
   `owner:` clause. Both cannot hold. Resolved by reading criterion 4 as protecting the *assertion*:
   the sentence *"no indexed document names sz-mcp-coworker at all"* is byte-identical, and only the
   parenthetical census after it was rewritten. That parenthetical is rationale wherever it sits —
   which is precisely why `find_census_rationales` reads **both** halves. Verified as a full-string
   multiset comparison of every changed line's claim and owner halves: **24 of 25 claim halves and 24
   of 25 owner halves byte-identical**, the two exceptions being the two sanctioned rewrites.
   ⚠️ My first version of that check truncated claims to 70 characters and reported *"0 differ"* —
   it would have missed this entirely. That is the INV-282 spot-check failure in miniature, caught
   only because the answer was already known to be non-zero.

4. **`:719`'s rewrite names the PROPERTY and only one section — re-citing the returned three would
   have kept it flagged.** Proposed change 2 says to *"cite the sections actually returned"*. Doing
   that literally re-creates an enumerated name-list, which
   `census-detector-misses-enumerated-name-lists` (implemented immediately before this spec, `93024f9`)
   now reports — and `test_a_corrected_enumeration_is_still_flagged` pins that as correct behavior,
   because the next server-side rename falsifies a fresh list exactly as it falsified the old one. The
   rationale instead quotes *Attribute reference*'s live in-feature-object rule — *"Only the attributes
   listed here may appear inside a feature object. Anything else is treated as payload"* — and states
   the property: no returned section gives any precedence for a **record-root** key whose name belongs
   to a registered feature. One named section, no coordinated run, so the report is quiet for the right
   reason rather than by evading the matcher.

5. **`DECLINED.md:126`'s count was dropped, not kept as incidental.** The spec allows
   *"Keep the count only if it is stated as incidental."* The count is the thing
   `find_census_rationales` flags, and criterion 2 requires the census warning to stop firing, so
   keeping it would have needed wording careful enough to fool a matcher — the wrong goal. Replaced
   with the discriminating property (no hit's title, section or `source_url` contains the string) plus
   a note that which documents come back is incidental. ⚠️ Worth recording for the next revisit:
   `explain_error_code('SENZ9000')` **does** name *"sz-mcp-coworker selfcheck (airgap binary)"*. The
   claim survives because it is scoped to *"no **indexed document**"* and its owner names `search_docs`
   — a structured error record is not an indexed document — but a future reader checking "does anything
   name it?" will find that it does.

6. **A guard was inverted, as its own failure message instructed.**
   `TheDriftedSiteIsFlaggedUntilItIsCorrected` asserted `:719` was flagged (the predecessor spec's
   criterion 1, first half). The restamp made it fail with the message it was written to give, naming
   the two possible causes; the detector returned an **empty** list while all twenty fixture-driven
   assertions still passed, which is what distinguished "rationale corrected" from "matcher
   regressed". Replaced by `NoShippedMarkerPinsAnEnumeration`, mirroring `NoShippedMarkerPinsACount`
   including its deliberate `plugins/`-only scope. Negative-controlled: reintroducing
   *Mapping identifiers* makes the report flag it and the new guard fail; file restored.

7. **Two sub-claims the spec listed as unverified were verified, and one upstream report re-confirmed.**
   `:220`'s *"byte-identical with and without `language`"* half — which the spec explicitly flagged as
   not re-tested — was tested: the two responses match in every field, same eight rows, same caution,
   same `source_url`. Separately, `:887`'s identity sub-claim reproduced at 1.36.0
   (`sdk_guide(install, linux_apt, java)` is byte-identical to the same call with no `language`, down
   to `next_steps[0].params.language: null`), which re-confirms the still-unsent upstream report.
   ⚠️ These two are **not** the same finding: `get_sdk_reference`'s `language` narrows *method
   signatures*, and `SZ_ENTITY_INCLUDE_ALL_RELATIONS` is a flag rather than a method, so having
   nothing to narrow is defensible. `sdk_guide`'s is not.

## Invariants introduced

None. This spec records a re-ask and two rationale corrections; it establishes no new rule. The rules
it exercises already exist — INV-080/INV-149 (a Senzing fact carries its route, version and date),
INV-194 (a negative names the owning route), and INV-295 (a measurement records when it was taken) —
and the one durable lesson from the implementation, that a fresh enumeration is a re-date in disguise,
is already enforced by `find_enumeration_rationales` and pinned by its guards.
