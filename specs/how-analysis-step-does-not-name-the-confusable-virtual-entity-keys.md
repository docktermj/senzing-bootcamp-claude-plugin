# The how-analysis step teaches dump-before-parse but never names the one key pair that half-exists

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Writing the how-analysis renderer, a guide reached for
`RESOLUTION_STEPS[].INBOUND_VIRTUAL_ENTITY` and `CANDIDATE_VIRTUAL_ENTITY` as the two sides of a
resolution step. The real keys are `VIRTUAL_ENTITY_1` and `VIRTUAL_ENTITY_2`. The parser raised
nothing — it rendered every step as `? joined ?` while the rule and match key beside them populated
correctly.

**The wrong name is plausible rather than careless**, and that is the whole finding:

- the response genuinely contains `INBOUND_VIRTUAL_ENTITY_ID` — a **string ID** on the step, not the
  object holding `MEMBER_RECORDS[]` — alongside `RESULT_VIRTUAL_ENTITY_ID`;
- a reader arriving from why-analysis, where `INBOUND_FEAT_DESC` / `CANDIDATE_FEAT_DESC` **are** the
  two sides of a comparison, carries that pairing across and lands on a key that half-exists.

A wholly invented name is caught by the first lookup. A name that appears in the schema at a
different depth and type survives it.

## Root cause

**The module names this hazard concretely for the graph calls and not for how-analysis.**

- `module-07-query-visualize-discover/phase2-discover.md:202-208` (step 4c, How Analysis) instructs
  looking up `get_sdk_reference(topic='response_schemas', filter='how_entity_by_entity_id')` before
  parsing (INV-115) — correct, and generic. It names no key.
- `phase2b-discover.md:59-69` (step 4d) does the opposite for the graph calls, and is the model to
  follow: *"Do **not** assume a link's two endpoints use the `ENTITY_ID` / `RELATED_ENTITY_ID`
  pairing that related-entity records use … a live dump on SDK 4.3.3 found them under
  `MIN_ENTITY_ID` / `MAX_ENTITY_ID`."*
- The plugin's own visualization server already parses the correct keys —
  `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1161`,
  `const v1=st.VIRTUAL_ENTITY_1||{};const v2=st.VIRTUAL_ENTITY_2||{};` — so the right answer is in
  the repo and simply never reaches the step where a Bootcamper writes the parser.

**Confirmed on the live server** — `get_sdk_reference(topic='response_schemas', filter='how_entity')`,
**MCP server 1.32.9, 2026-08-16**. `HOW_RESULTS.RESOLUTION_STEPS[]` carries exactly:

| Path | Type |
|---|---|
| `RESOLUTION_STEPS[].STEP` | integer |
| `RESOLUTION_STEPS[].INBOUND_VIRTUAL_ENTITY_ID` | **string** |
| `RESOLUTION_STEPS[].RESULT_VIRTUAL_ENTITY_ID` | **string** |
| `RESOLUTION_STEPS[].VIRTUAL_ENTITY_1` | **object** (`.VIRTUAL_ENTITY_ID`, `.MEMBER_RECORDS[]`) |
| `RESOLUTION_STEPS[].VIRTUAL_ENTITY_2` | **object** (`.VIRTUAL_ENTITY_ID`, `.MEMBER_RECORDS[]`) |
| `RESOLUTION_STEPS[].MATCH_INFO` | object |

So the confusable pair is real and current: `INBOUND_VIRTUAL_ENTITY_ID` exists as a string, the
objects carrying `MEMBER_RECORDS[]` are `VIRTUAL_ENTITY_1`/`_2`, and **no** `CANDIDATE_VIRTUAL_ENTITY`
key exists at any depth.

## Proposed change

1. **Add one concrete sentence to step 4c**, in the shape step 4d already uses:

   > The two sides of a resolution step are `VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2` — objects
   > carrying `MEMBER_RECORDS[]`. The similarly-named `INBOUND_VIRTUAL_ENTITY_ID` is a **string ID**
   > on the step, not the object, and there is no `CANDIDATE_VIRTUAL_ENTITY`.

2. **Say why the wrong name is reachable** — the why-analysis `INBOUND_FEAT_DESC` /
   `CANDIDATE_FEAT_DESC` pairing is one step earlier in the same phase, which is what makes the
   carry-across natural. Naming the *source* of the error is what stops it recurring; naming only
   the correct key does not.
3. **Keep the existing lookup-then-dump instruction**, and note that this pair is exactly the case
   where the lookup alone is insufficient — the wrong name is *in* the schema, at a different depth
   and type, so only reading the returned paths' types (or dumping one raw step) separates them.
4. **Record the keys where the plugin records confirmed response paths**:
   `module-03b-truthset-visualization/visualization-api-reference.md` → "MCP-confirmed response
   paths", alongside the `MIN_ENTITY_ID`/`MAX_ENTITY_ID` entry, so both hazards live together.

## Acceptance criteria

- [ ] Step 4c names `VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2` as the two sides of a resolution step
      and identifies `INBOUND_VIRTUAL_ENTITY_ID` as a string ID rather than the object.
- [ ] It states why the wrong pairing is reachable (the why-analysis `INBOUND_`/`CANDIDATE_`
      pairing), not merely which key is right.
- [ ] The existing `response_schemas` lookup and dump-before-parse instruction survives, with a note
      that the lookup alone does not separate this pair.
- [ ] The keys are recorded in `visualization-api-reference.md`'s MCP-confirmed response paths with
      route, server version and date.
- [ ] A test asserts step 4c names both keys, and fails if either is dropped.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      keys are response JSON, identical in every binding.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — step 4c,
  sub-step 2 (`:202-208`).
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the MCP-confirmed response-paths table (`:324`, `:446-450`).
- `tests/` — guard for the named keys.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Query/Discover: the how-analysis step names two confusable keys and a parser silently renders blank" (2026-08-16, Module Query, Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **server 1.32.9, 2026-08-16 — still reproduces (the confusable pair is current).** `get_sdk_reference(topic='response_schemas', filter='how_entity')` returns `RESOLUTION_STEPS[].INBOUND_VIRTUAL_ENTITY_ID` (string) and `RESOLUTION_STEPS[].RESULT_VIRTUAL_ENTITY_ID` (string) alongside `RESOLUTION_STEPS[].VIRTUAL_ENTITY_1` / `VIRTUAL_ENTITY_2` (objects, each with `.VIRTUAL_ENTITY_ID` and `.MEMBER_RECORDS[].RECORDS[].{DATA_SOURCE,RECORD_ID}`). The server documents the correct shape; the gap is that the plugin does not name it at the step where the parser is written.
- Upstream: not applicable — routed `plugin`. The server's schema is correct and complete here.
- Related specs: `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115, the discipline this step already carries), `specs/find-path-and-find-network-links-diverge.md` and `specs/network-link-fields-and-uncovered-response-schemas.md` (the sibling hazard step 4d names concretely — the model for this fix), `specs/graduation-assistant-retrospective-feedback.md`

## One correction to the feedback entry

The entry locates this at "Phase 2b, step 4d". The how-analysis step is **4c**, in
`phase2-discover.md`; step 4d in `phase2b-discover.md` is relationship networks — the step whose
`MIN_ENTITY_ID`/`MAX_ENTITY_ID` warning the entry correctly cites as the model. The fix belongs in
`phase2-discover.md`. Recorded so implementation does not edit the wrong file on the entry's
authority.
