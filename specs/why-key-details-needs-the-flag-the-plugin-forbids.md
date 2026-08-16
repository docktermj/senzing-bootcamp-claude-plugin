# The ⛔ forbidding `SZ_INCLUDE_MATCH_KEY_DETAILS` on a why call rests on a claim no measurement ever tested

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A guide followed the module's explicit ⛔ directive when writing its why-analysis renderer:

> ⛔ **Do not reach for `SZ_INCLUDE_MATCH_KEY_DETAILS` here.** … The CONFIRMATIONS and DENIALS named
> above are already there without it — they are part of `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS`

The resulting output had **no match-key breakdown at all**. Probing three flag sets against the same
record pair on **Senzing SDK 4.3.4**:

| Flags | `WHY_KEY_DETAILS` |
|---|---|
| `SZ_INCLUDE_FEATURE_SCORES` | **absent** |
| `+ SZ_ENTITY_INCLUDE_ENTITY_NAME` | **absent** |
| `+ SZ_INCLUDE_MATCH_KEY_DETAILS \| SZ_ENTITY_INCLUDE_ALL_RELATIONS` | **present** |

With the flag, `CONFIRMATIONS[]` returned `+NAME score 95 (CLOSE)` and `+ADDRESS score 100 (SAME)`.

⛔ **The failure is silent and the directive makes it look correct.** Every other analytical field
renders; only the breakdown is missing, so a guide following the ⛔ faithfully concludes "this SDK
doesn't provide that detail" rather than "a flag is missing". That is the half-populated-response
failure mode (INV-179) the *same file* warns about two paragraphs earlier, reached by following its
own instruction.

## Root cause

**The claim was inferred from a measurement whose two arms both passed the flag.**

`specs/why-response-carries-why-key-details-not-match-key-details` (2026-08-14) measured
`whyRecords` two ways and recorded the result as a table:

| Flags passed | keys observed |
|---|---|
| `SZ_INCLUDE_FEATURE_SCORES` + `SZ_INCLUDE_MATCH_KEY_DETAILS` | `… WHY_KEY, WHY_KEY_DETAILS` |
| the same **plus** the four relations flags | *identical* |

`SZ_INCLUDE_MATCH_KEY_DETAILS` is present in **both** rows. That measurement establishes what it set
out to — that `MATCH_KEY_DETAILS` is absent and `WHY_KEY_DETAILS` is the real field — and it
**never removed the flag**, so it is no evidence at all for "already there without it". The
conclusion was written as though the flag had been the variable, when the variable was the relations
flags.

The claim then propagated into two shipped sites:

- `module-07-query-visualize-discover/phase2-discover.md:128-138` — the ⛔ quoted above.
- `module-07-query-visualize-discover/phase1-query-visualize.md:120-127` — *"The CONFIRMATIONS and
  DENIALS named above are already there without it"*, and `:290-294`, *"on a why call it has nothing
  to attach to"*.

**What the live server actually says** (all re-verified on **MCP server 1.32.9, 2026-08-16**):

1. `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` — `applies_to`
   **includes** `why_entities`, `why_records` and `why_record_in_entity`. Its `response_paths` are
   `RELATED_ENTITIES[]`, `RESOLVED_ENTITY.*`, and it `depends_on` one of the five relations flags.
2. `get_sdk_reference(topic='response_schemas', filter='why_records')` — documents
   `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` and `…WHY_KEY_DETAILS.CONFIRMATIONS[]` as real paths
   on the why response. **No field description in that schema names any flag.**
3. `get_sdk_reference(topic='flags', filter='why_records')` — returns **29** flags that apply to
   `why_records`. **Not one** of them lists `WHY_KEY_DETAILS` in its `response_paths`.
4. `SZ_WHY_RECORDS_DEFAULT_FLAGS` is `composite_members: ["SZ_INCLUDE_FEATURE_SCORES"]` — so the
   method's default does not include the flag.

**So the server documents the field and attributes it to no flag whatsoever.** The plugin's
positive claim — *"already there without it"* — is not something the server ever said, and the
2026-08-14 table did not test it. The 2026-08-16 observation on SDK 4.3.4 contradicts it directly.

⚠️ **What is NOT established**, and must not be written as though it were: that
`SZ_INCLUDE_MATCH_KEY_DETAILS` is *documented* to populate `WHY_KEY_DETAILS`. It is not — the
server's `response_paths` for that flag name only `RELATED_ENTITIES[]` and `RESOLVED_ENTITY.*`. What
is established is one reproducible engine observation on one SDK version, plus a server that names
no populating flag. Per INV-169 both go in with their conditions; neither is flattened into an
absolute.

## Proposed change

1. **Withdraw the ⛔ at `phase2-discover.md:128-138` and the matching claims at
   `phase1-query-visualize.md:120-127` and `:290-294`.** They instruct omitting a flag on the
   strength of an untested negative, and following them produces the blank output reported.
2. **Replace with the measured, conditioned statement:**
   - the server documents `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` and names **no** flag that
     populates it (route + version + date);
   - on **Senzing SDK 4.3.4**, `WHY_KEY_DETAILS` was **absent** without
     `SZ_INCLUDE_MATCH_KEY_DETAILS` and **present** with it plus a relations flag — marked
     observation-only, with its SDK version and date (INV-080/INV-149);
   - the flag's documented `depends_on` still holds, so it is passed **with** a relations flag, and
     `SZ_ENTITY_INCLUDE_ALL_RELATIONS` is a composite that must be enumerated in a `Set<SzFlag>`
     argument (the existing caution at `:139-146` is correct and stays).
3. **Make the step's own remedy explicit at the step:** dump `MATCH_INFO`'s top-level keys before
   writing the parser, and print an explicit "not returned by this SDK for these flags" line rather
   than omitting the section — which is what surfaced this, and what turns the next silent absence
   into a visible one.
4. **Do not restore the `MATCH_KEY_DETAILS` field name.** The prior spec's central correction —
   the field is `WHY_KEY_DETAILS`, not `MATCH_KEY_DETAILS` — is confirmed again here and must
   survive this change intact.

## Acceptance criteria

- [ ] No shipped file instructs omitting `SZ_INCLUDE_MATCH_KEY_DETAILS` from a why call on the
      grounds that `WHY_KEY_DETAILS` is populated without it.
- [ ] The three sites state the server position (field documented, no populating flag named) and the
      SDK-4.3.4 observation separately, each with its route/version/date, neither presented as
      governing the other (INV-169).
- [ ] The SDK-4.3.4 result is marked observation-only, not laundered into an MCP-sourced claim
      (INV-080/INV-149).
- [ ] The flag's `depends_on` requirement and the Java composite-type caution both survive.
- [ ] Step 4b instructs dumping `MATCH_INFO`'s keys before parsing, and rendering an explicit
      "not returned" line rather than an empty section.
- [ ] A test asserts no file claims the breakdown is present "without" the flag, and fails if the
      withdrawn wording returns.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` —
  the ⛔ at `:128-138`, and step 4b.3's flag/response guidance at `:113-127`.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  `:120-127` and `:285-294`.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — check its `WHY_KEY_DETAILS` entry carries no inherited "without the flag" claim.
- `tests/` — guard against the withdrawn wording.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Module 7: WHY_KEY_DETAILS is absent without SZ_INCLUDE_MATCH_KEY_DETAILS on SDK 4.3.4" (2026-08-16, Module Query, Visualize and Discover Phase 2a step 4b; `Source: self-observed (assistant retrospective)`)
- Priority: High — a ⛔ directive that produces silently incomplete output in the module's headline demonstration.
- MCP re-check: **server 1.32.9, 2026-08-16 — the server now contradicts the plugin.** Called `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` (`applies_to` includes `why_records`/`why_entities`/`why_record_in_entity`; `response_paths` `RELATED_ENTITIES[]`, `RESOLVED_ENTITY.*`; `depends_on` the five relations flags), `get_sdk_reference(topic='response_schemas', filter='why_records')` (documents `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS[.CONFIRMATIONS[]]`, no flag named in any field description), and `get_sdk_reference(topic='flags', filter='why_records')` (29 flags apply; none names `WHY_KEY_DETAILS` in `response_paths`; `SZ_WHY_RECORDS_DEFAULT_FLAGS` = `SZ_INCLUDE_FEATURE_SCORES` alone). owner-checked: `get_sdk_reference(topic='flags', filter='why_records')` — the per-method flag catalog with `response_paths` per flag is the route that would carry "which flag populates `WHY_KEY_DETAILS`"; it returned 29 flags and no such attribution. The SDK-4.3.4 flag-set observation is engine-only and outside what the server documents.
- Upstream: **candidate — not yet sent.** The server documents a response field and attributes it to no flag, while an engine requires a flag to produce it. That is an actionable coverage gap in `flags`/`response_schemas`, and it is distinct from the entry's already-filed `LD_LIBRARY_PATH` report. Draft and get approval before sending (`category='bug'`).
- Related specs: `specs/why-response-carries-why-key-details-not-match-key-details.md` (established the current text; its measurement is the root cause), `specs/lookup-sdk-response-schemas-before-parsing.md`, `specs/why-entities-default-flags-has-no-composite-members.md`, `specs/fifth-response-schemas-stops-short-site-survives.md`

## The general shape

The 2026-08-14 measurement was sound for the question it asked and became evidence for a second,
adjacent claim it had not varied. Both arms held the flag constant, so the flag's contribution was
unobservable — and the conclusion was stated in the strongest available form ("already there without
it") and shipped as a ⛔. A negative about a flag is only supported by an arm in which that flag is
**absent**; where no such arm was run, the honest form is "not measured", not "not needed". That is
INV-194's reasoning applied to a flag matrix rather than to a tool route.
