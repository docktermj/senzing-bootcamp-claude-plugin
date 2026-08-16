# `mapping_workflow` step 1's prose contradicts its own advance schema (upstream)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`mapping_workflow(action='start')` returns step 1 instructions that state the advance payload
**twice, in two incompatible shapes**. Observed live on **server 1.32.9, 2026-08-12**.

**Prose — `profile_summary` as an object keyed by schema name** (appears twice, once in the
`ADVANCE FORMAT:` header and again under `ADVANCING TO STEP 2`):

```json
{"profile_summary": {"<schema_name>": {"record_count": N, "field_count": N}},
 "workspace_dir": "<path>"}
```

**Normative JSON Schema — `profile_summary` as an array of objects**, each requiring
`schema_name`, with `minItems: 1`, delivered both inline in `instructions` and as the
`advance_schema` field, introduced by:

> **this JSON Schema is the EXACT contract for the payload you send to advance FROM step 1.
> Match it exactly**

The two cannot both be satisfied. The prose has no `schema_name` key at all; the schema forbids
the object form via `additionalProperties: false`.

**Resolved empirically rather than by preference.** Advancing with the **array** form succeeded and
returned step 2 (`plan_entity_structure`). The array is correct; the prose is wrong.

**The plugin is already right, and that is the good news.** `phase2-data-mapping.md:164` documents
`action='advance'`, `data={'profile_summary': [...]}` — the array — and `:206` describes it as "one
entry per source schema". A guide following the plugin advances successfully. A guide following the
**tool's own prose** sends the object form and is rejected at the first advance, which is the step
this whole module depends on.

**This is an upstream defect, not a plugin defect.** It is recorded here because the plugin's
instructions tell the guide to follow the workflow's own instructions (`phase2-data-mapping.md:13`:
guidance comes "from the `mapping_workflow` MCP tool"), so the contradiction reaches the plugin's
users even though the plugin's own documented shape is correct.

**Step 2's response does not have this defect** — its prose `ADVANCE FORMAT` and its schema agree
(`master_schemas` / `support_schemas`, both arrays). So this is specific to step 1, not a systemic
pattern across the workflow.

## Root cause

**Upstream, and not diagnosable from here beyond the observation.** The most likely account is that
`profile_summary` changed shape from an object map to an array of typed entries when the typed
`payload` branches were introduced (the schema carries `for_step` discriminators throughout, which
reads as a later addition), and the two prose copies were not updated with it. That is inference,
and it is labeled as such — the server is closed to us.

Nothing in this repo could have caught it: `tests/test_mcp_call_contracts.py` verifies tool names,
required parameters and enumerated values, all of which are correct here. The defect is an
inconsistency *inside one response's free text*, which no offline test can see (INV-108) and which
only appears when the workflow is actually driven.

## Proposed change

1. **Report upstream**, with the maintainer's explicit approval of the exact text, per the same
   route `mcp-tools-disagree-on-eval-license-duration` took: `submit_feedback(category='bug')`.
   ⛔ **A dry run must never send it** — the send is a separate, maintainer-authorized action.

2. **Add a one-line caution to `phase2-data-mapping.md`** at the step-1 advance, stating that the
   tool's prose `ADVANCE FORMAT` for `profile_summary` shows an object map, that the **array** form
   in the `advance_schema` is the one that works, and that the array is what this plugin sends —
   dated, with the server version (INV-080).

3. ⛔ **Do not add an `MCP-NEGATIVE` marker.** This is not a "the tool lacks X" claim; it is a
   contradiction between two things the tool *does* say. The dated caution in (2) is the record, and
   it should be re-checked when the upstream report is answered.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` carries a dated caution naming both shapes, saying which one works,
      and citing tool, server **1.32.9** and date. Verified by opening the file.
- [ ] The plugin's documented payload shape at `:164` and `:206` is **unchanged** — it was already
      correct, and this spec must not "fix" it. Verified by `git diff`.
- [ ] A test asserts the caution names the array form as the working one, so a later edit cannot
      quietly invert it. **Not vacuous:** it names the file and fails if the caution is removed.
- [ ] **Negative-controlled, mutation verified to land:** inverting the caution to name the object
      form fails the test. Revert.
- [ ] The upstream report text is drafted in this spec for maintainer approval and **not sent** by
      the implementing session.
- [ ] Full suite passes (baseline **1756 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108).

## Draft upstream report (for maintainer approval — DO NOT SEND without it)

> `mapping_workflow` step 1 (`action='start'` → `profile_source_data`) describes the advance payload
> in two incompatible ways. The `ADVANCE FORMAT:` line and the `ADVANCING TO STEP 2` block both show
> `profile_summary` as an object keyed by schema name — `{"profile_summary": {"<schema_name>":
> {"record_count": N, "field_count": N}}}` — while the inline JSON Schema and the `advance_schema`
> field define it as an array of objects each requiring `schema_name`, with `additionalProperties:
> false` and `minItems: 1`, introduced as "the EXACT contract … Match it exactly". Advancing with
> the array form succeeds; the prose form cannot validate. Step 2's equivalent prose and schema do
> agree, so this appears specific to step 1. Observed on server 1.32.9, 2026-08-12.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/` — one new guard.

## Source

- Dry run, **phase 3**, 2026-08-12, maintainer answering as the Bootcamper. Found by driving
  `mapping_workflow` from `action='start'` through the first `advance` against a real 3,488-record
  source — the workflow three prior runs recorded as unreached.
- **MCP:** server **1.32.9**, 2026-08-12. `mapping_workflow(action='start')` and
  `action='advance'` called; the array form's success is the evidence, not an inference.
- Priority: **Medium.** The plugin already sends the correct shape, so a conforming run is
  unaffected; the exposure is a guide that follows the tool's instructions over the plugin's, which
  `phase2-data-mapping.md:13` explicitly tells it to do.
- Related: INV-125 (record the raw failure and the concluded cause before falling back), INV-136
  (satisfy the contract the live schema states), `mcp-tools-disagree-on-eval-license-duration` (the
  prior server-self-contradiction, same handling).

## Invariants introduced

**None proposed.** INV-136 and INV-125 already govern; this is an upstream defect plus a dated
caution, not a new standing rule.

## Deviations from this spec, and why (2026-08-12)

**None on content — the claim was re-verified live before anything was written.**
`mapping_workflow(action='start')` was re-called on **server 1.32.9** during implementation, and the
contradiction **still holds**: the prose `ADVANCE FORMAT:` and the `ADVANCING TO STEP 2` block both
show `profile_summary` as an object keyed by schema name, while the inline JSON Schema and the
`advance_schema` field define an array of objects requiring `schema_name`, with
`additionalProperties: false` and `minItems: 1`. Step 2's prose and schema still agree, so it remains
specific to step 1.

**The upstream report was NOT sent**, as the spec requires. Its drafted text stands above awaiting
the maintainer's approval; sending is a separate, maintainer-authorized action.

**The caution is longer than the "one line" the Proposed change asked for** — it shows both shapes as
fenced examples, because the difference is structural and a prose description of it is exactly what
the tool already gets wrong. The guard additionally asserts the caution cannot be **inverted** (a
`assertNotRegex` on "send the OBJECT"), which the criteria did not ask for and which is the failure
mode that would do real damage: a reader sent to the shape the schema rejects.

## Upstream report sent (2026-08-12)

The maintainer approved the drafted text **verbatim** and it was sent as
`submit_feedback(category='bug')` on 2026-08-12 — a separate, maintainer-authorized action, taken
after the dry run closed and therefore outside the skill's ⛔ on invoking `submit_feedback` during a
run. No text was changed between approval and sending.

The server's response records that **submissions are anonymous and cannot be followed up**, so no
reply will arrive and none should be waited for. The plugin-side caution in `phase2-data-mapping.md`
therefore remains the operative protection for our users regardless of what upstream does with the
report; re-check the claim on a later server version rather than assuming it was acted on, and if
the prose is corrected, retire the caution rather than inverting it.
