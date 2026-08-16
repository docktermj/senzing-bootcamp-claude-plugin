# Step 11's "expect a field-count warning" block no longer describes the server

Maintain the invariant conditions in @INVARIANTS.md and update the following claim:

## Problem

`phase2-data-mapping.md` step 11 carries a ⛔ block telling the guide to expect — and ignore — a
field-count warning on **every** step-3 advance:

> ⛔ **Expect a field-count warning on exit, and do not chase it.** Step 3 emits
> "mapped N fields … but profile reported M fields" on **every** mapping that uses `derived` entries
> or a `type_discriminator` — which is every mapping that follows this workflow's own guidance, since
> `derived` `DATA_SOURCE`/`RECORD_ID` are mandatory for a master schema…

**It did not fire.** Walked live on **MCP server 1.32.9, 2026-08-14**: a step-3 advance for
`meridian_crm` (6 source fields — 4 `feature`, 1 `payload`, 1 `ignore` — plus **three** `derived`
entries for `DATA_SOURCE`, `RECORD_ID` and `RECORD_TYPE`) returned
`{"status":"ok","step":4,...}` with **no field-count warning anywhere in the response**.

That mapping is squarely inside the block's stated scope: it uses `derived` entries, which the block
says makes the warning unavoidable ("every mapping that follows this workflow's own guidance"). So
the claim's own universal quantifier is contradicted by the first case tried.

The block already anticipates this and asks for exactly this check:

> **Reported upstream 2026-07-31 and not re-run since**, so check whether it still fires rather than
> assuming.

This spec is that check landing. The evidence base was *server 1.32.3, verified 2026-07-31*; the
server is now 1.32.9.

### Related, and confirmed in the same walk: the counts the prose says are required are derived

The step-3 instructions state:

> - DISPOSITION COUNT BALANCE [server-validated]: each schema must include `feature_count`,
>   `payload_count`, and `ignored_count`. Their sum must equal the schema's `field_count`.

The plugin's step 11 does **not** mention those three fields — a grep of the whole module finds no
occurrence — so a guide following the plugin omits them. **That is safe**, and now verified: the
advance above was sent without any of the three and was accepted, and the returned `state` shows the
server had **computed them itself**:

```json
"meridian_crm":{"record_count":14,"field_count":6,"disposition":"master",
  "data_source":"MERIDIAN_CRM","record_type":"PERSON","record_id_source":"account_id",
  "feature_count":4,"payload_count":1,"ignored_count":1,"extract_count":0}
```

So the plugin's silence is correct rather than an omission, and no change is needed there. It is
recorded here because it is the same class of stale server prose, found in the same call, and a
future reader comparing the plugin against the tool's instructions would otherwise take the plugin
for incomplete. Note also that the step-3 typed `payload` branch does not declare these three
properties at all, which is consistent with the server deriving them.

## Root cause

Not a plugin defect — a claim about the server that the server has since changed, carrying its own
"re-run this" caveat. The block is doing exactly what INV-169 asks of a version-dependent
observation (record the observation with its server version and route the reader through a
re-check), and the re-check has now come back negative.

## Proposed change

**Do not simply delete the block** — an absent warning today is not proof it never fires, and the
counter's two-directional error was real and specifically measured (12 reported as 13; 16 reported as
14, on SDK 4.3.3.26191). Instead:

1. **Invert the framing from "expect it" to "if you see it".** Lead with the re-check result: the
   warning did **not** fire on server 1.32.9 (2026-08-14) for a mapping with three `derived` entries,
   so it appears fixed upstream. Keep the diagnosis and the "do not chase it" instruction as a
   conditional — a guide that does meet it still needs to know it is a known-bad counter and not a
   mapping fault.
2. **Remove the universal quantifier.** "on **every** mapping that uses `derived` entries" is now
   falsified; the corrected text must not assert it, or the block reads as discredited by its own
   evidence — the failure mode INV-169's sibling note already warns about for snippet counts
   ("exactly how a correct ⛔ comes to look discredited by its own evidence").
3. **Keep the real instruction, which is version-independent:** confirm every source field carries a
   disposition. That was always "the real question the warning gestures at", and it holds whether or
   not the counter is wrong.
4. **Preserve the ⚠️ against generalizing.** "Do not start ignoring this step's warnings generally"
   must survive — a retired warning is not a license to distrust the step.
5. **Record the `type_discriminator` half as still unverified.** The block's claim covers `derived`
   entries **and** `type_discriminator`; this walk exercised only `derived` (our source is
   single-type, so no discriminator). Say so explicitly rather than letting one re-check retire both
   halves — a source with a per-record type field is what would confirm the second.

## Acceptance criteria

1. The block leads with the 2026-08-14 / server 1.32.9 negative re-check and no longer asserts the
   warning fires on every such mapping.
2. The diagnosis (the counter includes `derived` non-source entries and excludes
   `type_discriminator.field_overrides` fields; the errors do not cancel) and the original measured
   evidence with its SDK version are retained as history, clearly marked as the earlier observation.
3. The version-independent instruction — confirm every source field has a disposition — is retained
   as the step's actual requirement.
4. The `type_discriminator` half is marked as **not** re-run, with what would verify it.
5. The ⚠️ against generalizing to the step's other warnings is retained verbatim.
6. A note records that `feature_count`/`payload_count`/`ignored_count` are **server-derived**, so the
   plugin deliberately does not send them — with the returned-state evidence — so a future reader
   does not "fix" the plugin by adding them.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, walking Module 5 Phase 2 steps 8–11
  against the live server with a three-`derived`-entry mapping and observing no field-count warning
  (`Source: self-observed (assistant retrospective)`). The block's own instruction to re-check rather
  than assume is what prompted it.
- Priority: **Low.** Nothing is broken and no bootcamper is misled into an error — the block tells
  the guide to ignore a warning that no longer appears, which is inert. It matters because a ⛔ whose
  stated trigger demonstrably does not occur erodes the credibility of the surrounding ⛔s, several of
  which are load-bearing (the `extract`/verbatim collision, the field-name-derived value class).
- MCP re-check: **confirmed, server 1.32.9, 2026-08-14.** `mapping_workflow(action='advance')` from
  step 3 with `derived` `DATA_SOURCE`, `RECORD_ID` and `RECORD_TYPE` returned `status: ok` to step 4
  with no warning, and the returned `state` carried server-computed disposition counts.

## Deviations from this spec, and why (2026-08-14)

- **The `MCP re-check` line carried no `owner-checked:` clause, which `implement-spec` treats as a
  blocker on an absence claim (INV-194).** Re-diagnosed rather than implemented on trust: the
  owning route was re-asked directly — `mapping_workflow(action='advance')` from step 3 with three
  `derived` entries (`DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`) on a 6-field master schema — and it
  returned `{"status":"ok","step":4,…}` with no field-count warning, on server 1.32.9, 2026-08-14.
  The spec had named the right route; what was missing was the clause saying so, since the step-3
  advance response is the only route that could carry the warning. The shipped block now carries a
  well-formed `MCP-NEGATIVE` marker with that `owner:` clause.
- **One fact the spec's rewrite did not mention keeping had to be kept.** The proposed change said
  to retain the diagnosis and the measured evidence; implementing it literally dropped the sentence
  naming the `derived_as` enum and `type_discriminator.field_overrides` as live schema features, and
  an existing guard (`tests/test_verbatim_check_limitation.py::test_the_prescriptions_carry_current_mcp_provenance`)
  correctly failed on it. Both mechanisms were re-read on server 1.32.9, 2026-08-14 — still declared —
  and the block now states that explicitly, which also strengthens the spec's own argument for not
  deleting it: the shapes that produced the miscount remain, only the warning is gone.
