# Require `get_sdk_reference(topic='response_schemas')` before writing code that parses an SDK response

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The MCP server's `get_sdk_reference` tool exposes a `response_schemas` topic documenting the JSON response
structure for each SDK method. **The plugin never mentions it.** Module 7's guidance directs the assistant
to `get_sdk_reference(topic='flags')` for flag selection but says nothing about response shapes.

Consequence in the reported session: response structures were inferred from example snippets rather than
looked up, and were wrong three times.

| Assumed | Actual | Symptom |
|---|---|---|
| `FEATURE_TYPE` in `MATCH_KEY_DETAILS` | `FTYPE_CODE` | Review queue printed `=97 (CLOSE)` with a blank feature name |
| `MATCH_LEVEL_CODE` at search-result root | nested under `MATCH_INFO` | Search printed `match=` (empty) |
| `INBOUND_VIRTUAL_ENTITY` / `CANDIDATE_VIRTUAL_ENTITY` in how-steps | `VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2`, with `MATCH_KEY` under `MATCH_INFO` | How output showed `step 1: (rule )` with null bodies |

All three were eventually found by dumping raw responses and reading them — but only because the blank
output was noticed. **None raised an error.**

Why it matters, in the reporter's words: "This is the worst failure mode in the whole bootcamp: output
that renders successfully and is silently incomplete. A bootcamper seeing `step 1: (rule )` has no way to
know a field name was wrong rather than the data being empty, and would reasonably conclude Senzing had
nothing to report. The explainability features — the entire point of Module 7 — are the ones most exposed,
because their responses are the most deeply nested."

"The fix costs one sentence of guidance and one MCP call."

## Root cause

**Confirmed by grep: `response_schemas` appears 0 times across the entire plugin** — all skills, all docs.

What the plugin *does* direct is narrower than it appears. Every `get_sdk_reference` call site specifies a
topic, and only two topics are ever used:

- `get_sdk_reference(topic='flags')` — 5 occurrences
- `get_sdk_reference(topic='functions', filter='why_entities', …)` — 1 occurrence

Module 7's own guidance is explicit about flags and silent about shapes:

- `phase1-query-visualize.md:61` — "`get_sdk_reference(topic='flags')` (filter by method name) and select
  the flags matching the …"
- `phase2-discover.md:62, 102, 164` — "confirm … flag names via `get_sdk_reference(topic='flags')`"
- `phase2b-discover.md:31-32` — `topic='flags'` for network and path methods
- `SKILL.md:45` — "`get_sdk_reference` (flags and method signatures) plus `sdk_guide` /
  `reporting_guide`"

That last line is the root cause in miniature: the plugin's MCP-grounding requirement is **thorough about
method names and flags and silent on response structures**, leaving the most error-prone part of the work
— reading deeply nested JSON — to inference. The visualization contract makes it worse by handing the
implementer example JSON: `visualization-api-reference.md:210-213` and `:225-229` show illustrative
`WHY_RESULTS` / `HOW_RESULTS` shapes, which invite exactly the "infer from a snippet" behavior that failed.

## Proposed change

1. **Add the lookup requirement wherever flags are already looked up.** At each of the six
   `get_sdk_reference` call sites, add the companion instruction:

   > …and look up the response structure via
   > `get_sdk_reference(topic='response_schemas', filter='<method>')` **before writing any code that
   > parses the response — never infer field names from an example snippet.**

   Verify the topic name and its parameter shape against the MCP server at implementation time rather than
   trusting this spec.
2. **Add a defensive-parsing rule.** When a parsed field comes back null/blank, treat it as a **probable
   wrong field name**, not as absent data, and verify against `response_schemas` or a dumped raw response
   before rendering. This is the rule that would have caught all three failures at the moment they
   happened rather than after the output was inspected.
3. **Extend the MCP-grounding statement** so response structures are named alongside method names and
   flags. `specs/mcp-grounding-in-every-skill.md` put an MCP-grounding block in every skill; this adds
   response shapes to what that block covers, so the requirement applies to every module that parses an
   SDK response — not only Module 7.
4. **List the highest-risk shapes inline in `visualization-api-reference.md`**, since the why/how/search
   responses are what every language implementation must parse. The reporter's list, to be **MCP-confirmed
   at implementation time rather than copied from this spec**: `MATCH_INFO.MATCH_LEVEL_CODE`,
   `MATCH_INFO.MATCH_KEY`, `MATCH_INFO.FEATURE_SCORES`,
   `MATCH_KEY_DETAILS.CONFIRMATIONS[].FTYPE_CODE`, `RESOLUTION_STEPS[].VIRTUAL_ENTITY_1|2`. Place them
   beside the existing illustrative payloads with a note that the illustrations are shapes, not field-name
   authority.
5. **Make blank explainability output visible rather than plausible.** A why/how rendering that produces
   an empty feature table or a step with no body should say so ("no feature scores returned — verify the
   response shape") instead of rendering an empty section that reads as a real result. This is the
   defense that survives a future field rename, and it pairs directly with
   `specs/truthset-viz-readable-why-how-and-modal-polish.md`: a summary view makes the failure mode
   *worse*, because a mis-named field becomes a blank cell instead of visibly-absent JSON. Implement the
   two together if possible.

## Acceptance criteria

- [ ] Every `get_sdk_reference(topic='flags')` site in the plugin is paired with a `topic='response_schemas'`
      lookup requirement for the same method, before any response-parsing code is written.
- [ ] The topic name and parameter shape are verified against the MCP server during implementation and
      cited in the skill text.
- [ ] The defensive-parsing rule (blank field ⇒ suspect the field name, not the data) appears in the
      plugin's MCP-grounding guidance, so it reaches every module that parses an SDK response.
- [ ] `visualization-api-reference.md` lists the highest-risk response paths, MCP-confirmed, with a note
      that its example payloads illustrate shape and are not field-name authority.
- [ ] Why/How rendering distinguishes "no data returned" from "rendered empty", so a wrong field name
      cannot present as a real empty result.
- [ ] A grep for `response_schemas` across the plugin returns a non-zero number of references.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): response shapes
      are language-independent JSON, and the requirement applies to the bootcamper's chosen language
      whatever it is.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — line ~61
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — lines ~62,
  ~102, ~164
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2b-discover.md` — lines ~31-32
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/SKILL.md` — line ~45 (the
  "flags and method signatures" description)
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  lines ~195-230: the risk list and the "illustrative, not authoritative" note
- The MCP-grounding block in every skill — add response structures to what must come from MCP

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Direct the assistant to
  `get_sdk_reference(topic='response_schemas')` before parsing SDK responses" (2026-07-25, cross-cutting;
  `Source: self-observed (assistant retrospective)`)
- Priority: **High**
- Related specs: `specs/mcp-grounding-in-every-skill.md`, `specs/visible-mcp-source-attribution.md`,
  `specs/truthset-viz-readable-why-how-and-modal-polish.md` (**implement together if possible**),
  `specs/graduation-assistant-retrospective-feedback.md` (the retrospective that surfaced this)

## Invariants introduced

- `INV-115` — Before writing code that parses an SDK response, the guide MUST look up the response
  structure via `get_sdk_reference(topic='response_schemas', filter='<method>')` and MUST NOT infer
  field names from an example snippet; a null/blank parsed field MUST be treated as a probable wrong
  field name before absent data, and MUST NOT render as a real empty result.
  (Recorded in `specs/INVARIANTS.md`.)

## Implementation notes

Verifying the topic against the MCP server — which this spec required rather than trusting itself —
changed the implementation in three ways:

1. **`response_schemas` returns only top-level shape.** It confirms
   `RESOLVED_ENTITY.RECORDS[].MATCH_LEVEL_CODE`, `HOW_RESULTS.RESOLUTION_STEPS[]`, `WHY_RESULTS[]`,
   and `RESOLVED_ENTITIES[]`, but **not** `MATCH_INFO.FEATURE_SCORES`,
   `MATCH_KEY_DETAILS.CONFIRMATIONS[].FTYPE_CODE`, or `RESOLUTION_STEPS[].VIRTUAL_ENTITY_1|2`. Four
   of the five paths in proposed-change item 4 are therefore not MCP-confirmable via this topic.
   Only the confirmed set was written into the contract; deeper nesting is delegated to a
   raw-response dump. Writing the rest unverified would have repeated the defect being fixed.
2. **`search_docs` confirmed a trap this spec missed**, now documented: with
   `SZ_INCLUDE_MATCH_KEY_DETAILS`, `why_*` puts a `WHY_KEY_DETAILS` object under `MATCH_INFO`, while
   `how_entity_by_entity_id` puts a `MATCH_KEY_DETAILS` object under each resolution step's
   `MATCH_INFO`. One parser reused across both silently returns nothing.
3. **The call-site count was 7, not 5**, and the two the spec's grep missed were written
   `get_sdk_reference(method='find_network', topic='flags')` — exposing a latent bug: `method=` is
   not a parameter (the schema accepts only `topic`, `filter`, `version`), so both calls in
   `phase2b-discover.md` would have failed. Corrected to `filter=`.
