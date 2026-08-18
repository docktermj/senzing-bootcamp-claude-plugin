# The why-side sibling scalars are `WHY_KEY` and `WHY_ERRULE_CODE`, and both warnings name only `WHY_KEY_DETAILS`

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 7 warns twice, correctly and at length, that a why response's match-key breakdown lives at
`WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` and **not** at `MATCH_KEY_DETAILS`. Neither warning
mentions that the two **sibling scalar fields in the same object** are differently named as well:
they are `WHY_KEY` and `WHY_ERRULE_CODE`, where the `get_entity` and export paths use `MATCH_KEY` and
`ERRULE_CODE`.

A `why_explain` program was written with `MATCH_KEY` / `ERRULE_CODE`, out of habit from the entity-side
shape, and the error was caught only because Module 7 separately requires reading
`get_sdk_reference(topic='response_schemas', filter='<method>')` before writing any parser (INV-115).
Uncaught, both fields render blank with no error — the exact silent failure the surrounding guidance
exists to prevent, one field over from where it points.

## Root cause

**The existing warnings are correct and their scope is the problem.** By telling the reader that the
*details object* is differently named, they implicitly reassure them that the neighboring fields are
not.

`module-07-query-visualize-discover/phase1-query-visualize.md:293-295`:

> ⛔ **For a why response the match-key breakdown is read from
> `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS`, never from a `MATCH_KEY_DETAILS` field** — that field
> name is the one this module already corrected, and it is still wrong here.

`module-07-query-visualize-discover/phase2-discover.md:122-127` states the same thing for step 4b.3,
naming `WHY_KEY_DETAILS`, its `CONFIRMATIONS[]` entries and their `FTYPE_CODE` / `TOKEN` / `SOURCE` /
`SCORE` / `SCORE_BUCKET` members. Neither names `WHY_KEY` or `WHY_ERRULE_CODE`.

**Confirmed on the live server, and the contrast is confirmed from the same route.**
`get_sdk_reference(topic='response_schemas', filter='why_records', language='python')`, **server
1.32.9, verified 2026-08-17** — the response document shared by `why_entities`, `why_records` and
`why_record_in_entity` — carries under `WHY_RESULTS[].MATCH_INFO` exactly four scalar-or-object
siblings:

```text
WHY_RESULTS[].MATCH_INFO.MATCH_LEVEL_CODE   (string)
WHY_RESULTS[].MATCH_INFO.WHY_ERRULE_CODE    (string)
WHY_RESULTS[].MATCH_INFO.WHY_KEY            (string)
WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS    (object)
```

alongside `CANDIDATE_KEYS`, `DISCLOSED_RELATIONS` and `FEATURE_SCORES`. **No `MATCH_KEY` and no
`ERRULE_CODE` appear anywhere under `WHY_RESULTS[]`.**

The entity side, from the route that owns it —
`get_sdk_reference(topic='response_schemas', filter='get_entity', language='python')`, same server,
same date — is where those two names do live:

```text
RELATED_ENTITIES[].ERRULE_CODE             (string)
RELATED_ENTITIES[].MATCH_KEY               (string)  "Features that matched/did not match"
RELATED_ENTITIES[].MATCH_KEY_DETAILS       (object)
RESOLVED_ENTITY.RECORDS[].ERRULE_CODE      (string)  "Entity resolution rule that triggered the match"
RESOLVED_ENTITY.RECORDS[].MATCH_KEY        (string)
```

So the divergence is systematic — the whole `MATCH_*` family is `WHY_*` on the why surface — and the
plugin documents exactly one member of it. `reporting_guide(topic='evaluation', language='python')`
(same server and date) reinforces the entity-side habit from the other direction: its export-iteration
pattern reads `RELATED_ENTITIES[]` with `MATCH_LEVEL_CODE`, `MATCH_KEY`, `ERRULE_CODE`, and the
`export_with_stats` snippet it returns uses `rec.get("MATCH_KEY")` and `rec.get("ERRULE_CODE")`. A
guide that builds Module 6's audit from that snippet and then writes Module 7's why parser carries the
names straight across.

**Why this is worth a change rather than a shrug.** Anyone building the "explain this match"
deliverable Module 7 asks for touches these two fields first, and a blank match key in an
explainability feature reads to a bootcamper as "Senzing gave no reason" rather than as a wrong field
name. INV-115 caught it once; INV-115 is a rule about reading the schema before parsing, and it works
only when it is followed, whereas naming the trap costs one clause.

## Proposed change

1. **Extend the existing warning at `phase1-query-visualize.md:293-295` by one clause** naming
   `WHY_KEY` and `WHY_ERRULE_CODE` alongside `WHY_KEY_DETAILS`, and naming the entity-side
   counterparts they are confused with (`MATCH_KEY` / `ERRULE_CODE`) so the reader can see which habit
   produces the error. The trap and the fix are identical, so this needs no new block.
2. **Do the same at `phase2-discover.md:122-127`**, where the step already enumerates the fields to
   parse — the two scalars belong in that enumeration, not in a separate caution.
3. **Attribute it to the route that establishes it** — `get_sdk_reference(topic='response_schemas',
   filter='why_records')` — with the server version and date, exactly as the surrounding lines already
   do. Do not assert the field set on the plugin's own authority (INV-080).
4. **Do not add a third site.** Both places that warn are places a parser gets written; anywhere else
   the module mentions why output should keep deferring to these two (INV-179's state-it-once
   discipline, which `phase1-query-visualize.md:296-300` already applies to the flag caveat).

## Acceptance criteria

- [ ] Both existing warnings name `WHY_KEY` and `WHY_ERRULE_CODE` beside `WHY_KEY_DETAILS`, and name
      `MATCH_KEY` / `ERRULE_CODE` as the entity-side names that are **not** present on a why response.
- [ ] Each carries the tool, parameters, server version and date that establish the field set.
- [ ] No new warning block is added, and no third site repeats the rule.
- [ ] A test asserts that every shipped mention of `WHY_KEY_DETAILS` as the why-side name also names
      the two sibling scalars — negative-controlled by removing one name and confirming the mutation
      lands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the field
      names are in the JSON response document, which is identical across bindings; only the accessor
      syntax differs, and the change names no accessor.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the ⛔ at `:293-295`.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — the
  field enumeration at `:122-127`.
- `tests/` — the new guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "why_* MATCH_INFO scalars are WHY_KEY /
  WHY_ERRULE_CODE, and the docs warn only about WHY_KEY_DETAILS" (2026-08-17, Module Query, Visualize
  and Discover, Priority Low; `Source: self-observed (assistant retrospective)`)
- Priority: **Low.** One clause in each of two places. The severity is bounded because INV-115 already
  requires the schema read that catches it; the value is that the trap is named where the parser is
  written rather than depending on a rule being followed.
- MCP re-check: **server 1.32.9, 2026-08-17 — confirmed, and the entity-side contrast confirmed from
  its own route.** Tools called: `get_capabilities` (server version);
  `get_sdk_reference(topic='response_schemas', filter='why_records', language='python')` →
  `WHY_RESULTS[].MATCH_INFO.{MATCH_LEVEL_CODE, WHY_ERRULE_CODE, WHY_KEY, WHY_KEY_DETAILS}`;
  `get_sdk_reference(topic='response_schemas', filter='get_entity', language='python')` →
  `RELATED_ENTITIES[].{MATCH_KEY, ERRULE_CODE, MATCH_KEY_DETAILS}` and
  `RESOLVED_ENTITY.RECORDS[].{MATCH_KEY, ERRULE_CODE}`. The claim that `MATCH_KEY` and `ERRULE_CODE`
  are absent from the why response is **owner-checked:
  `get_sdk_reference(topic='response_schemas', filter='why_records', language='python')` — the route
  that documents this response object; it enumerates every `WHY_RESULTS[].MATCH_INFO` member and
  neither name is among them**.
- Upstream: **not applicable.** The server documents the field set correctly and completely; the
  plugin's warning is the incomplete party.
- Related specs: `specs/why-response-carries-why-key-details-not-match-key-details.md` (established
  the existing warnings this spec extends),
  `specs/response-schemas-now-documents-match-info-depth.md` (established that `response_schemas`
  reaches this depth, which is why the check is cheap),
  `specs/why-key-details-needs-the-flag-the-plugin-forbids.md` (the flag caveat that shares these
  two sites), `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115),
  `specs/match-key-details-does-list-the-export-methods.md`.
