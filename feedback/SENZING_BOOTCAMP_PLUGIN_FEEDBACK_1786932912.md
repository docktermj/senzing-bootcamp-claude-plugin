# Senzing Bootcamp — plugin feedback

Append-only. Each entry is one observation.

## Improvement: howEntity resolution steps use undocumented key names, and a wrong guess renders blank

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — `reporting_guide(topic='entity_views')` returns the `howEntity` CALL but not its RESPONSE shape, and `get_sdk_reference(topic='response_schemas')` does not cover the step structure either.
**Upstream:** offer pending — batched with the other mcp-server findings at graduation

### What happened

`reporting_guide(topic='entity_views', language='java')` returns a working `howEntity` snippet with
the note "HOW_RESULTS shows the step-by-step merge sequence" — but no field names for a step. A
parser written from plausible names (`INBOUND_VIRTUAL_ENTITY` / `CANDIDATE_VIRTUAL_ENTITY`, which
mirror the `INBOUND_FEAT_DESC` / `CANDIDATE_FEAT_DESC` naming used in the `why_*` responses) printed
**nothing at all** and raised no error. The real keys are `VIRTUAL_ENTITY_1` and `VIRTUAL_ENTITY_2`,
alongside `INBOUND_VIRTUAL_ENTITY_ID` and `RESULT_VIRTUAL_ENTITY_ID`.

The `INBOUND_` prefix genuinely exists in the response — but on the *ID* field, not on the object —
which is what makes the wrong guess so plausible.

### Why it matters

This is the silent-blank failure class the plugin already warns about generally (INV-115), reached
through a documented call whose response shape is not documented. The `how` view is one of Module
7's eight derived requirements, so every bootcamper who builds it hits this. The step printed a
correct-looking merge list with the member records silently missing.

### Suggested fix

Add the `HOW_RESULTS.RESOLUTION_STEPS[]` shape to `get_sdk_reference(topic='response_schemas',
filter='how_entity')` — at minimum `STEP`, `MATCH_INFO`, `VIRTUAL_ENTITY_1`, `VIRTUAL_ENTITY_2`,
`INBOUND_VIRTUAL_ENTITY_ID`, `RESULT_VIRTUAL_ENTITY_ID`, and
`VIRTUAL_ENTITY_n.MEMBER_RECORDS[].RECORDS[]`.

### Context when reported

- **Time:** 2026-08-17, graduation
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** query_visualize_discover / 4c
- **Behind the scenes:** building `src/query/Explain.java` against `reporting_guide(topic='entity_views')`
- **Observed problem:** merge steps listed, member records blank, exit 0
- **Expected behavior:** documented call implies a documented response shape
- **Divergence:** the call is documented; the response is not

## Improvement: findNetwork links and paths use DIFFERENT endpoint key names

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — `reporting_guide(topic='graph')` names both arrays but neither array's fields.
**Upstream:** offer pending — batched with the other mcp-server findings at graduation

### What happened

`reporting_guide(topic='graph', language='java')` comments the `findNetwork` snippet with
"ENTITY_PATHS holds the seed-to-seed paths; ENTITY_NETWORK_LINKS holds the edges" — accurate, and
not enough to parse either. The two arrays use **different** endpoint keys:

- `ENTITY_PATHS[]` → `START_ENTITY_ID` / `END_ENTITY_ID` (directed)
- `ENTITY_NETWORK_LINKS[]` → `MIN_ENTITY_ID` / `MAX_ENTITY_ID` (undirected), plus `IS_DISCLOSED`
  and `IS_AMBIGUOUS` integer flags

Reading the path names on a link printed `null -> null` for all 38 edges of a corporate hierarchy,
with no error. The distinction is sensible once seen — a link is an unordered pair — but nothing
signals it beforehand, and `START_`/`END_` is the natural guess because the sibling array uses it.

### Why it matters

Relationship networks are the capability the fraud-detection pattern leans on most. A silently
empty edge list looks exactly like "this data has no relationships", which is the wrong conclusion
to hand an analyst.

### Suggested fix

Document both arrays' fields under `get_sdk_reference(topic='response_schemas',
filter='find_network')`, and note explicitly that links are undirected `MIN`/`MAX` pairs while paths
are directed `START`/`END`.

### Context when reported

- **Time:** 2026-08-17, graduation
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** query_visualize_discover / 4d
- **Observed problem:** 38 links rendered `null -> null`
- **Expected behavior:** endpoint fields parse the same way across the response
- **Divergence:** two arrays in one response use different endpoint conventions

## Improvement: get_sdk_reference(topic='response_schemas') can exceed the tool-result token limit

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the tool returned 61,689 characters in 3 lines, over the host's per-result limit.
**Upstream:** offer pending — batched with the other mcp-server findings at graduation

### What happened

`get_sdk_reference(topic='response_schemas', filter='getEntityByEntityId whyEntities')` returned a
61,689-character result that the host refused to inline, spilling it to a file. Recovering the two
signatures then took three `grep` passes over that file.

The plugin instructs reading response schemas **before** parsing (INV-115), so this is on the
critical path of a required check — and the friction pushes toward skipping it.

### Why it matters

A check that is expensive to run is a check that gets skipped, and this one guards the
silently-renders-blank failure class that produced the two entries above.

### Suggested fix

Have `filter` narrow the payload rather than only select entries — a single-method filter should
return that method's schema, not a document containing it. Multi-term filters could also return a
summary with per-method follow-ups.

### Context when reported

- **Time:** 2026-08-17
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** query_visualize_discover / 2
- **Observed problem:** result exceeded the token limit and was written to a file
- **Expected behavior:** a filtered schema lookup returns a focused result
- **Divergence:** `filter` selects but does not narrow

## Improvement: the "do not ask" instruction sits directly above the pinned question it forbids

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — a skill-authoring layout issue in `phase1-query-visualize.md` step 25.
**Upstream:** not applicable

### What happened

Step 25 opens "**First, check whether there are real stakeholders** … if it carries the
bootcamp-generated marker … there are no business users to involve — so **do not ask**", and then
prints the pinned question verbatim two lines below, under "Otherwise …". On a bootcamp-generated
scenario I asked it anyway. The bootcamper answered "no", which routes to the same self-directed
spot-check the generated-scenario branch prescribes, so no work was affected — but it was one
question they should never have seen.

The same shape appears in step 13 and step 15 of `phase2b`/`phaseC` and I got those right, which
suggests what differs here: in those the confirm-instead-of-ask branch supplies its **own** pinned
question, so there is something to say. In step 25 the generated branch has no question at all, and
the only pinned text on the page is the one that must not be used.

### Why it matters

Asking a bootcamper to convene stakeholders for a scenario the bootcamp invented is exactly the
re-litigation INV-006 exists to prevent, and it lands at the end of a long session.

### Suggested fix

Move the pinned question inside the "Otherwise" branch rather than leaving it at the section's
outer level, or add the marker check as a one-line precondition immediately above the question.

### Context when reported

- **Time:** 2026-08-17
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** query_visualize_discover / 25
- **Recent questions:** "Would you like to involve business users in testing the cross-source results?"
- **Bootcamper responses:** "no"
- **Observed problem:** a question was asked that the same step forbids on this path
- **Expected behavior:** generated scenarios skip the stakeholder question silently
- **Divergence:** the forbidden question is the most visually prominent text in the step

## Improvement: a busy port can still accept a wildcard bind, giving two servers on one port

**Date:** 2026-08-17
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the visualization server's port handling and the module's port-conflict guidance.
**Upstream:** not applicable

### What happened

`lsof -ti:8080` reported 8080 busy — an unrelated `VizServer` from a previous project, started three
weeks earlier, bound to `127.0.0.1:8080`. The bootcamp's server nevertheless bound successfully to
`*:8080`, because a loopback bind and a wildcard bind do not collide on macOS. Two processes then
listened on the same port and **either could answer a localhost request**. The first `/api/stats`
probe happened to hit the new server, which is what made it look fine.

Had the browser hit the other one, the bootcamper would have been shown a three-week-old dataset
(100 records, 2 sources) under their own project's title, with nothing indicating anything was wrong.

### Why it matters

The existing guidance treats port conflicts as bind failures. This one is not a failure — it is a
success that produces nondeterministic results, which is strictly worse.

### Suggested fix

After binding, probe the port and verify the responding server is the one just started (e.g. compare
`/api/stats` against the known record count) before handing the URL over. Alternatively bind
explicitly to `127.0.0.1` so a conflicting loopback listener causes a clean failure.

### Context when reported

- **Time:** 2026-08-17
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** query_visualize_discover / 3c
- **Observed problem:** two listeners on 8080; response source nondeterministic
- **Expected behavior:** a busy port either fails to bind or is detected as occupied
- **Divergence:** loopback and wildcard binds coexist

## Improvement: group-based completeness invites reading group coverage as per-identifier coverage

**Date:** 2026-08-17
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — a consequence of the module's prescribed group-based completeness metric.
**Upstream:** not applicable

### What happened

The module defines completeness against feature GROUPS, where IDENTIFIER counts as present if any
of NATIONAL_ID / PASSPORT / TAX_ID / LEI / TRUSTED_ID is populated. Both GLEIF and OpenSanctions
scored **IDENTIFIER 100%**. I wrote in `docs/data_source_evaluation.md` that they would therefore be
the highest-confidence cross-source pair, "both carrying LEI".

They do not. GLEIF carries 2,375 LEIs; OpenSanctions carries **one** in 137 records — its
identifiers are national IDs and passports. Exactly one LEI value is shared across the whole
dataset. The prediction was only disproved after loading, when the match-key distribution showed
LEI in a single match key.

### Why it matters

The group metric is right for measuring *completeness* and wrong for predicting *joins*, and nothing
in the module flags the difference. The wrong prediction reached a written evaluation document and
shaped a load-order rationale before measurement corrected it.

### Suggested fix

Where the module discusses cross-source matching outlook, note that a shared **group** does not
imply a shared **attribute**, and suggest a per-attribute overlap count for any pair whose join is
being predicted.

### Context when reported

- **Time:** 2026-08-17
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** data_quality_mapping / phase1 step 7
- **Observed problem:** group coverage read as attribute coverage; prediction wrong by 38x
- **Expected behavior:** the evaluation predicts the strongest pair correctly
- **Divergence:** the metric measures presence-of-any, the prediction needed presence-of-same

## Improvement: two mappings were reversed after loading, and neither was filed when it happened

**Date:** 2026-08-17
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the reversed-decision rule fired but the entries were not written at the time.
**Upstream:** not applicable

### What happened

Two mapping decisions were changed after they had passed every static gate. Ground-rules require
filing a reversal when it happens; neither was filed until this retrospective.

1. **OPEN-SANCTIONS lost 8 legitimate identifiers.** The rules file had no `OTHER_ID` group at all,
   which correctly dropped 123 self-referential rows and silently dropped 6 `swiftBic` and 2
   `imoNumber` values with them. Fixed with `exclude_when`. The two designs are indistinguishable in
   output whenever the excluded rows dominate — which is why the analyzer, the verbatim check and
   the routing report all passed.
2. **ICIJ `COUNTRY_OF_ASSOCIATION` was not actually payload.** The bootcamper chose payload; kept
   under its own name at the record root, it is a *registered feature attribute*, so Senzing extracts
   it as a feature regardless. `payload_from_list` also joins values, so 13,803 of 19,050 records
   carried `"XXX; VGB; GBR"` as one literal value. Renamed to `ICIJ_COUNTRIES`; the analyzer's SCHEMA
   warning cleared.

### Why it matters

Both were found by *writing the per-source documentation*, not by any gate — a review step the
module treats as a deliverable rather than a check. The second one also means a bootcamper's explicit
answer can be silently not honored: routing a registered feature attribute to "payload" does nothing
unless it is also renamed.

### Suggested fix

Add a mapping-time check that a root-level payload key is not a registered feature attribute, and
surface the analyzer's SCHEMA warning at the mapping gate rather than only in the output analysis.

### Context when reported

- **Time:** 2026-08-17
- **Plugin version:** 0.5.1
- **Workstation:** macOS 26.5.2 (arm64)
- **Model / effort:** claude-opus-5 / high
- **Module / step:** data_quality_mapping / phase2
- **Observed problem:** two mappings passed all gates and were still wrong
- **Expected behavior:** gates catch a dropped identifier and a non-honored payload routing
- **Divergence:** static gates check structure and faithfulness, not intent
