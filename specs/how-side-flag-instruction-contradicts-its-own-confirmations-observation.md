# Step 4c instructs `SZ_INCLUDE_FEATURE_SCORES` alone on the how call, then points at a breakdown that flag does not request

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Step 4c tells the guide to generate the `how_entity` call with `SZ_INCLUDE_FEATURE_SCORES`.
Step 4b, ninety lines earlier in the same file, records that `how_entity`'s
`MATCH_KEY_DETAILS.CONFIRMATIONS[]` populated on an entity where `why_records`' equivalent
came back empty — offered as the reason the how side is worth reaching for.

Followed literally, the two do not meet. On this run (Senzing SDK 4.3.4, Python) with
`SZ_INCLUDE_FEATURE_SCORES` alone, `MATCH_INFO` on the how response carried:

```text
['CANDIDATE_KEYS', 'ERRULE_CODE', 'FEATURE_SCORES', 'MATCH_KEY']
```

`MATCH_KEY_DETAILS` was **absent** — not present-and-empty, which is the third state step 4b
is careful to distinguish. On the same entity and the same run, `why_records` returned
`WHY_KEY_DETAILS` populated with three confirmations once
`SZ_INCLUDE_MATCH_KEY_DETAILS | SZ_ENTITY_INCLUDE_ALL_RELATIONS` was passed.

⚠️ **The guide is not left without an output, only without a reconciliation.** Step 4c
already forbids rendering an empty section, so stating the absence and falling back to
`FEATURE_SCORES` is reachable. But the guide has to work out mid-demonstration that the
step's own cross-reference points at a field its own flag instruction does not request,
under exactly the time pressure the module's headline demonstration creates.

⛔ **This is the same defect as the why side, one method over.** The ⛔ that used to forbid
`SZ_INCLUDE_MATCH_KEY_DETAILS` on why calls was withdrawn by
`specs/why-key-details-needs-the-flag-the-plugin-forbids.md`, and step 4b now passes it with
a relations flag. That spec's acceptance criteria are scoped to why calls throughout — *"no
shipped file instructs omitting `SZ_INCLUDE_MATCH_KEY_DETAILS` from a **why** call"* — so
the how call at `:255-259` was never in its blast radius and still carries the pre-correction
flag set.

## Root cause

`plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md:255-259`,
step 4c item 2:

```text
2. **SDK flag and response shape:** generate the `how_entity` call with the
   `SZ_INCLUDE_FEATURE_SCORES` flag (confirm via `get_sdk_reference(topic='flags',
   filter='how_entity_by_entity_id')`), and look up the response structure via
   `get_sdk_reference(topic='response_schemas', filter='how_entity_by_entity_id')` before
   parsing it (INV-115).
```

versus `:139-141`, inside step 4b's `CONFIRMATIONS[]` caution:

```text
while `how_entity`'s `MATCH_KEY_DETAILS.CONFIRMATIONS[]` populated on the same entity
(observation-only, INV-080/INV-149: no MCP route reports whether a given rule produces
confirmations).
```

The instruction requests feature scores; the observation promises a match-key breakdown.
Nothing in the step passes the flag that names that breakdown.

### What the live server returns

All three routes re-verified on MCP server **1.33.0**, **2026-08-24**.

**1. The how response schema documents the field.**
`get_sdk_reference(topic='response_schemas', filter='how_entity', language='python')`
returns, among the `MATCH_INFO` members:

```text
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[]
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[].FTYPE_CODE
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[].TOKEN
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[].SOURCE
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[].SCORE
HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[].SCORE_BUCKET
```

So the path is real on the how response, and — unlike the why side, where the equivalent
field is `WHY_KEY_DETAILS` — the how side genuinely uses the `MATCH_KEY_DETAILS` spelling.
That distinction must survive this change.

**2. The flag that names it applies to `how_entity`, and is not the one being passed.**
`get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')`:

- `applies_to` **includes** `how_entity_by_entity_id`;
- `depends_on`: one of `SZ_ENTITY_INCLUDE_ALL_RELATIONS`,
  `SZ_ENTITY_INCLUDE_POSSIBLY_SAME_RELATIONS`,
  `SZ_ENTITY_INCLUDE_POSSIBLY_RELATED_RELATIONS`, `SZ_ENTITY_INCLUDE_NAME_ONLY_RELATIONS`,
  `SZ_ENTITY_INCLUDE_DISCLOSED_RELATIONS`.

**3. The flag being passed does not reach that subtree.**
`get_sdk_reference(topic='flags', filter='SZ_INCLUDE_FEATURE_SCORES')` returns
`SZ_HOW_ENTITY_DEFAULT_FLAGS` with `composite_members: ["SZ_INCLUDE_FEATURE_SCORES"]` and
`response_paths: ["HOW_RESULTS.RESOLUTION_STEPS[]"]`. The Python signature carries the same
value as its default:

```text
how_entity_by_entity_id(entity_id: int, flags: int = <SzEngineFlags.SZ_INCLUDE_FEATURE_SCORES: 67108864>) -> str
```

So the step's flag set is the method's default, and the breakdown is a separate opt-in.

⚠️ **The server says three things about where this field lands and they do not fully agree
— record all three, reconcile none** (INV-169). `applies_to` names `how_entity_by_entity_id`
and the how schema documents the path, but that same flag entry's own `response_paths` are
`RELATED_ENTITIES[]` and `RESOLVED_ENTITY.*`, and its description reads *"each related entity
includes a MATCH_KEY_DETAILS object"* — a shape `how_entity` does not return at all. Its
`depends_on` relations requirement points the same way. This is a coverage gap on the
server's side, not a fact the plugin can settle, and it is why proposed change 4 asks for
the breakdown to be treated as conditional rather than promised.

### The two engine observations, side by side

Neither governs the other (INV-169), and both are observation-only (INV-080/INV-149) — no
MCP route reports which flag set populated a given engine response.

| Date | Method | Flags in force | `MATCH_KEY_DETAILS` |
|---|---|---|---|
| 2026-08-18 | `how_entity` | **not recorded** | `CONFIRMATIONS[]` populated |
| 2026-08-24 | `how_entity` | `SZ_INCLUDE_FEATURE_SCORES` alone | **absent** from `MATCH_INFO` |
| 2026-08-24 | `why_records` | `SZ_INCLUDE_MATCH_KEY_DETAILS \| SZ_ENTITY_INCLUDE_ALL_RELATIONS` | `WHY_KEY_DETAILS`, 3 confirmations |

⛔ **The 2026-08-18 row's flag set was never written down**, so it is not evidence that the
breakdown appears without the flag — it is not evidence either way. Writing "it used to work
without the flag" from that row would repeat precisely the error
`specs/why-key-details-needs-the-flag-the-plugin-forbids.md` documents in its `## The general
shape`: a conclusion drawn from a matrix that never varied the relevant term. The rows are
consistent with the flag being required on both methods, and that is the strongest statement
the data supports.

## Proposed change

1. **Pass `SZ_INCLUDE_MATCH_KEY_DETAILS` together with a relations flag on the how call**
   (`:255-259`), matching what step 4b already does for `why_records`. The flag's documented
   `depends_on` holds regardless of the tension above, so the relations flag goes with it.
2. **Keep the caution that `SZ_ENTITY_INCLUDE_ALL_RELATIONS` is a composite** that must be
   enumerated where a binding takes a flag set rather than a bitmask — step 4b's existing
   note applies verbatim to this call and should be cross-referenced, not duplicated.
3. **Record the 2026-08-24 absence observation beside the 2026-08-18 one**, in step 4c, with
   each row's conditions and an explicit statement that the earlier row's flag set is
   unrecorded. Do not merge them into a single claim, and do not write a version floor.
4. **State the breakdown as conditional at the step, with the fallback already in force.**
   Where `MATCH_KEY_DETAILS` is absent for the flags in force, say so in one line and render
   `FEATURE_SCORES`, which carries the same per-feature evidence and populated normally on
   both runs — never an empty section, never "no value returned".
5. **Preserve the `MATCH_KEY_DETAILS` / `WHY_KEY_DETAILS` split.** The why side's field is
   `WHY_KEY_DETAILS`; the how side's is `MATCH_KEY_DETAILS`. Both spellings are correct on
   their own method, and a change that harmonizes them would reintroduce the defect
   `specs/why-response-carries-why-key-details-not-match-key-details.md` fixed.
6. **Keep INV-115's dump-before-parse instruction** at the step. It is what turned this
   absence into a visible finding rather than a blank section.

## Acceptance criteria

- [ ] Step 4c's `how_entity` call passes `SZ_INCLUDE_MATCH_KEY_DETAILS` with a relations
      flag, and no shipped file instructs a how call that names `MATCH_KEY_DETAILS` while
      requesting `SZ_INCLUDE_FEATURE_SCORES` alone.
- [ ] Step 4c records both engine observations with their conditions, marks the 2026-08-18
      flag set as unrecorded, and asserts no version or flag floor.
- [ ] The server's three statements (flag `applies_to`, the how `response_schemas` path, and
      the flag's own `response_paths` / related-entity description) are all recorded with
      route, server version and date, with none presented as governing the others.
- [ ] The step states the fallback to `FEATURE_SCORES` and forbids both an empty section and
      a "no value returned" rendering.
- [ ] `WHY_KEY_DETAILS` remains the why-side spelling and `MATCH_KEY_DETAILS` the how-side
      spelling; a test fails if either is used on the other method.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      the flag names are SDK constants and the composite-enumeration caution must be stated
      in binding-neutral terms.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` —
  step 4c item 2's flag instruction (`:255-259`); the cross-reference at `:139-141`.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
  — check its how-side flag guidance carries no inherited feature-scores-only instruction.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the how-response contract, so a bootcamp building its own renderer requests the same flags.
- `tests/` — guard on the how-call flag set and on the two field spellings.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: `how_entity` omits `MATCH_KEY_DETAILS` under `SZ_INCLUDE_FEATURE_SCORES` alone" (2026-08-24, Module Query, Visualize and Discover, step 4c; `Source: self-observed (assistant retrospective)`)
- Priority: Medium — the entry filed it Low on the grounds that the correct outcome is reachable; raised because the same root cause on the why side shipped as a ⛔ that produced silently blank output, and this is that defect's unfixed half. The step's own cross-reference is what misleads.
- MCP re-check: server **1.33.0**, **2026-08-24** — **still reproduces, and the server now supplies the mechanism the entry lacked.** Called `get_sdk_reference(topic='response_schemas', filter='how_entity', language='python')` (documents `HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[]` with its members), `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` (`applies_to` includes `how_entity_by_entity_id`; `depends_on` one of the five relations flags; `response_paths` `RELATED_ENTITIES[]`, `RESOLVED_ENTITY.*`), and `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_FEATURE_SCORES')` (`SZ_HOW_ENTITY_DEFAULT_FLAGS` is that flag alone, `response_paths` `HOW_RESULTS.RESOLUTION_STEPS[]`; the Python signature defaults to it). owner-checked: `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` — the per-flag catalog is the route that would carry "which flag populates `MATCH_KEY_DETAILS` on a how response", and it attributes the object to related entities while listing `how_entity_by_entity_id` in `applies_to`. The engine-side flag/response observations are outside what the server documents and are marked observation-only.
- Upstream: **candidate — drafted, pending the maintainer's decision.** The server's flag entry and its how-response schema disagree about where `MATCH_KEY_DETAILS` lands for `how_entity_by_entity_id`. ⚠️ Adjacent to the report sent 2026-08-17 on the why side, which noted that this flag's documented effect is on `RELATED_ENTITIES[]`; that report was itself a deliberate possible duplicate and its spec says not to send a third on the why finding. This is a distinct path and method, so it is offered as a new report rather than a follow-up — the maintainer's call.
- Related specs: `specs/why-key-details-needs-the-flag-the-plugin-forbids.md` (the same defect on the why side; its criteria are why-scoped, which is how this half survived), `specs/why-response-carries-why-key-details-not-match-key-details.md` (the field-spelling split that must be preserved), `specs/confirmations-has-a-third-state-present-and-empty-and-the-teaching-step-has-no-branch-for-it.md` (the present-and-empty state this absence must not be conflated with), `specs/how-analysis-step-does-not-name-the-confusable-virtual-entity-keys.md`, `specs/lookup-sdk-response-schemas-before-parsing.md`

## The general shape

A correction scoped to the method where the defect was observed leaves its sibling intact,
and the cross-reference between them becomes the trap: step 4b now passes the flag and
step 4c cites step 4b's result while passing the old flag set. When a spec's criteria name
a method, the sweep should be over the *claim* — which flags a breakdown needs — rather
than over the method that happened to surface it.
