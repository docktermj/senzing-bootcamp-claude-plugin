# Flag-gated response fields are unannotated in BOTH reference topics, defeating the defensive-parsing rule

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

⚠️ **`mcp-server` finding.** The defect is in `get_sdk_reference`'s reference data. The plugin's job
is to relay it so a Bootcamper is not led to a wrong conclusion by following the plugin's own rule.
A drafted upstream message is at the end.

## Problem

`ground-rules.md` prescribes a defensive-parsing procedure with a specific discriminator:

> **Defensive parsing.** When a parsed field comes back null, empty, or blank, treat it as a
> **probable wrong field name first and absent data second** — verify against `response_schemas`,
> or dump one raw response and read it, before rendering.

For a field that is **flag-gated**, `response_schemas` gives the wrong answer, because its
`requires_flags` annotation is **selectively populated** — and nothing distinguishes an unannotated
field that is always present from one that is gated.

Measured live on 2026-08-31, MCP server **1.35.1**, SDK **4.4.0**, against a loaded 9,033-record
repository. Empirically flag-gated, proven by calling `get_entity_by_record_id` twice with and
without the flag:

| Path | Actually requires | `response_schemas` `requires_flags` | `flags` topic `response_paths` |
|---|---|---|---|
| `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` | `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO` | **absent** | **absent** |
| `RESOLVED_ENTITY.RECORDS[].ERRULE_CODE` | `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO` | **absent** | **absent** |
| `RELATED_ENTITIES[].MATCH_KEY` | `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO` | **absent** | **absent** |
| `RELATED_ENTITIES[].IS_DISCLOSED` | `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO` | **absent** | **absent** |
| `RELATED_ENTITIES[].RECORDS[]` | `SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA` | present ✓ | present ✓ |
| `RELATED_ENTITIES[].MATCH_KEY_DETAILS` | `SZ_INCLUDE_MATCH_KEY_DETAILS` | present ✓ | present ✓ |

Direct proof, same entity, same call, flags the only difference:

```text
flags WITHOUT related-matching-info -> RELATED_ENTITIES[0] keys: ENTITY_ID, ENTITY_NAME
flags WITH    related-matching-info -> RELATED_ENTITIES[0] keys: ENTITY_ID, ENTITY_NAME,
                                       ERRULE_CODE, IS_AMBIGUOUS, IS_DISCLOSED, MATCH_KEY,
                                       MATCH_LEVEL_CODE
```

**Neither reference topic closes the gap**, so there is no route to the answer:

- `topic='response_schemas'` lists `MATCH_KEY` and `IS_DISCLOSED` with **no** `requires_flags`,
  while annotating neighboring paths in the same array. A reader concludes they are unconditional.
- `topic='flags'` gives `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO` and
  `SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO` **no `response_paths` at all**, while populating that
  field for `SZ_ENTITY_INCLUDE_RECORD_FEATURES`, `SZ_ENTITY_INCLUDE_RECORD_DATES`,
  `SZ_INCLUDE_MATCH_KEY_DETAILS` and others.

**The consequence is exactly the failure `ground-rules.md` warns about, reached by following the
rule.** The guide checks `response_schemas`, sees the field listed unconditionally, re-reads its
parse, finds nothing wrong, and concludes the data is genuinely absent — reporting "no match keys
found" for a repository whose match keys are all present. The invariant's own words:

> a wrong field name yields `None`, which renders as blank text. The output then looks like
> "Senzing found nothing" instead of a defect, so nobody reports it.

Observed twice in one module on this walk — once on `RECORDS[].MATCH_KEY` (the match-key audit came
back with **0 distinct match keys** against a true 16) and once on `RELATED_ENTITIES[].IS_DISCLOSED`
(disclosed ownership links came back **0**). Both were caught only by dumping a raw response, which
is the rule's *second* remedy; its first remedy would have confirmed the wrong conclusion.

⚠️ **The plugin's own advice makes this more likely, not less.** `get_sdk_reference` carries a
production caution — *"`*_DEFAULT_FLAGS` composites are intended for getting started and exploration,
not for production code … request exactly the flags whose output you consume"* — and
`SZ_ENTITY_DEFAULT_FLAGS` **includes** both matching-info flags. So a guide that follows the caution
and names flags explicitly is *more* exposed than one that uses the default composite.

## Root cause

Upstream, in `get_sdk_reference`'s derived reference data (both topics derive from
`docs-flags-4-flags_get_entity.md`): the flag→path mapping is populated for some flags and not
others, and the same gap appears from the schema side as a missing `requires_flags`. Because both
annotations are *partially* populated, their absence reads as "not gated" rather than "not recorded".

In the plugin: `ground-rules.md`'s defensive-parsing rule names `response_schemas` as the
verification route without noting that its flag annotation is incomplete, and the "Flags" bullet
above it treats flag lookup and response-shape lookup as two independent steps rather than as a
join that neither tool completes.

## Proposed change

**In the plugin (what this repo can ship):** amend the defensive-parsing rule in `ground-rules.md`
to name the flag hypothesis first for an absent field, and to say plainly that the schema's
annotation cannot rule it out:

> ⚠️ **For an ABSENT field — as opposed to a wrong value — suspect the FLAGS before the field name.**
> `response_schemas`' `requires_flags` annotation is **incomplete**: `RECORDS[].MATCH_KEY`,
> `RECORDS[].ERRULE_CODE`, `RELATED_ENTITIES[].MATCH_KEY` and `RELATED_ENTITIES[].IS_DISCLOSED` are
> all flag-gated and none carries the annotation, while neighboring paths do (server 1.35.1,
> 2026-08-31). So a path listed with no `requires_flags` is **not** evidence that it is
> unconditional. Re-issue the call with the matching `*_MATCHING_INFO` flag, or with a DEFAULT
> composite, and compare — a field that appears is a flag problem, not absent data. Only after that
> comparison is "the data is genuinely absent" a supportable conclusion.

Keep the existing rule intact; this narrows its first step for the absent-field case.

## Acceptance criteria

- [ ] `ground-rules.md`'s defensive-parsing rule distinguishes an **absent** field from a **wrong**
      value, and names re-issuing with broader flags as the first check for the former.
- [ ] It states that `requires_flags` is incomplete, with the measured examples, server version and
      date, so a reader does not treat its absence as proof.
- [ ] The existing `response_schemas` guidance and the raw-dump remedy are unchanged.
- [ ] No guidance recommends `*_DEFAULT_FLAGS` for production code — the broadened call is a
      diagnostic step, not the shipped call.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the "Defensive parsing"
  bullet under the MCP-first invariant.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Data processing Phase D and Query,
  Visualize and Discover step 2 (`Source: self-observed (assistant retrospective)`) — found by
  hitting the same empty-parse twice on real resolved data and following the plugin's defensive-parsing
  rule to a wrong answer both times.
- Priority: Medium
- MCP re-check: server **1.35.1**, 2026-08-31 — both reference topics read live and quoted above;
  the flag dependency was proven by paired `get_entity_by_record_id` calls differing only in flags.
  owner-checked: `get_sdk_reference(topic='response_schemas', filter='get_entity_by_record_id')` and
  `get_sdk_reference(topic='flags', filter='get_entity_by_record_id')` are the two routes that would
  carry the flag→path mapping, and both were asked; each annotates *some* paths/flags and omits these
  (absence negative, with the positive controls tabled above proving the fields exist and are used).
- Upstream: **submitted 2026-08-31** via `submit_feedback` (`category='bug'`, anonymous), with the
  maintainer's explicit approval of the text after the dry run closed. The message below is what was sent (reproduced
  in this repository's US-English house style, per INV-253), batched with the walk's other upstream findings into one report. Submissions are
  anonymous, so there is no follow-up channel; `support@senzing.com` is the route with a return path.
- Related specs: `specs/routing-report-flags-every-payload-field-as-dropped.md` — the walk's other
  `mcp-server` finding; both are owed upstream and could be sent together.

## Drafted upstream message (`category='bug'`, identifying details stripped — INV-065)

> `get_sdk_reference` under-annotates flag-gated response fields, in both topics, for
> `get_entity_by_entity_id` / `get_entity_by_record_id`.
>
> These four paths are flag-gated in practice on SDK 4.4.0 — proven by paired calls differing only in
> flags — but carry no annotation in either reference topic:
>
>   RESOLVED_ENTITY.RECORDS[].MATCH_KEY        requires SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
>   RESOLVED_ENTITY.RECORDS[].ERRULE_CODE      requires SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
>   RELATED_ENTITIES[].MATCH_KEY               requires SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
>   RELATED_ENTITIES[].IS_DISCLOSED            requires SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
>
> topic='response_schemas' lists all four with no `requires_flags`, while annotating neighbors in
> the same arrays (RELATED_ENTITIES[].RECORDS[] -> SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA;
> RELATED_ENTITIES[].MATCH_KEY_DETAILS -> SZ_INCLUDE_MATCH_KEY_DETAILS). topic='flags' gives
> SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO and SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO no
> `response_paths` at all, while populating that field for SZ_ENTITY_INCLUDE_RECORD_FEATURES,
> SZ_ENTITY_INCLUDE_RECORD_DATES and SZ_INCLUDE_MATCH_KEY_DETAILS.
>
> Observed: with SZ_ENTITY_INCLUDE_ALL_RELATIONS | SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME, a related
> entity returns only {ENTITY_ID, ENTITY_NAME}. Adding SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
> returns {ENTITY_ID, ENTITY_NAME, ERRULE_CODE, IS_AMBIGUOUS, IS_DISCLOSED, MATCH_KEY,
> MATCH_LEVEL_CODE}.
>
> Why it matters: because the annotations are partially populated, their absence reads as "this field
> is unconditional" rather than "this was not recorded". A client that consults response_schemas to
> diagnose a missing field is led to conclude the data is absent — silently reporting no match keys
> for a repository that has them. This is worse than no annotation, because the partial coverage
> makes the omission look like information.
>
> Suggested fix: populate `requires_flags` for every flag-gated path, or `response_paths` for every
> flag that gates one — ideally both, since they are the same mapping read from two directions.
>
> Senzing SDK 4.4.0; MCP server 1.35.1.

## Deviations from this spec, and why (2026-09-01)

**Re-verified against server 1.35.3 — the defect is unchanged, so the relay ships.** All six rows of
the spec's table reproduce today: `RESOLVED_ENTITY.RECORDS[].MATCH_KEY`,
`RESOLVED_ENTITY.RECORDS[].ERRULE_CODE`, `RELATED_ENTITIES[].MATCH_KEY` and
`RELATED_ENTITIES[].IS_DISCLOSED` still carry **no** `requires_flags`, while
`RELATED_ENTITIES[].RECORDS[]` (`SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA`) and
`RELATED_ENTITIES[].MATCH_KEY_DETAILS` (`SZ_INCLUDE_MATCH_KEY_DETAILS`) still do. From the other
side, `topic='flags'` filtered on `SZ_ENTITY_INCLUDE_ALL_RELATIONS` returns
`SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO` with **no** `response_paths`, while
`SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA` and `SZ_ENTITY_INCLUDE_RELATED_RECORD_TYPES` both have
them. Had it been fixed upstream, the workaround would have been dropped rather than shipped
(`implement-spec` Step 3.3, "already fixed upstream").

**No invariant was minted: the rule is INV-179 and now cites it at the line.** The drafted amendment
reads as a new guarantee, but INV-179 already says a blank field has **three** causes — wrong field
name, correct name the flags in force do not populate, or genuinely absent data — and that *"the
flags MUST be suspected before the data, and the fix is to OR in the missing sub-flag"*. What this
change adds is the case INV-179 did not anticipate: that `response_schemas` **cannot** confirm the
gating, because its annotation is partial. That is an application of INV-179, not a rule beside it,
so both hard rules cite it rather than opening a fourth deferral in this run.

**The upstream half was already sent** (2026-08-31, `category='bug'`, with the maintainer's explicit
approval after the dry run closed). Nothing was re-sent: the unattended loop never calls
`submit_feedback`, and re-sending an approved report would have duplicated it upstream with no way
to withdraw either copy.

**Two dates, deliberately, because they have different authorities.** The **annotation gaps** are
MCP-sourced and stamped **1.35.3, 2026-09-01** — re-asked today. The **empirical flag-gating** is
stamped **2026-08-31, SDK 4.4.0** and marked observation-only (INV-149): it needs a live engine with
loaded data, this environment no longer has that repository, and no MCP route reports it. Restamping
it today would have claimed a measurement that was not taken.
