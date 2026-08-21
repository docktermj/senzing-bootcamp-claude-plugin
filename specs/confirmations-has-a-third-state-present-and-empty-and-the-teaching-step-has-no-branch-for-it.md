# `WHY_KEY_DETAILS.CONFIRMATIONS` has a third state — present and empty — and the step that teaches the match-key breakdown has no branch for it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Every `why_records` call on one run returned `WHY_KEY_DETAILS` **present** with an **empty**
`CONFIRMATIONS` array — on rules `SNAME_SSTAB` and `SF1_PNAME_CFF`, with `SZ_INCLUDE_FEATURE_SCORES`
in force. `FEATURE_SCORES` populated normally, so the evidence the step wanted was available by
another path. On the same entity, `how_entity`'s equivalent —
`RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[]` — **did** populate.

**Step 5 makes this path the basis of a teaching step.** A Bootcamper following it sees nothing, and
has no way to tell whether they mis-parsed. In the entry's words: *a documented, empty array is
indistinguishable from a parsing bug.*

## Root cause

The plugin's guidance covers **two** states and this is a **third**.

`plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md:122-152` is
careful and current. It names `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS` as "the path to parse for
step 5", records that the server documents no flag as populating it, records the engine-side
observation that it is **absent** with `SZ_INCLUDE_FEATURE_SCORES` alone and **present** once
`SZ_INCLUDE_MATCH_KEY_DETAILS | SZ_ENTITY_INCLUDE_ALL_RELATIONS` is added, and concludes correctly:

> **So: pass `SZ_INCLUDE_MATCH_KEY_DETAILS` together with a relations flag** — its documented
> `depends_on` still holds — and treat the breakdown as conditional rather than guaranteed.

"Conditional rather than guaranteed" covers *absent*. It does not cover *present and empty*, and the
two need different responses:

| State | What it means | What to do |
|---|---|---|
| `WHY_KEY_DETAILS` absent | wrong flags | add `SZ_INCLUDE_MATCH_KEY_DETAILS` + a relations flag |
| present, `CONFIRMATIONS` empty | **no branch exists** | ← this spec |
| present, populated | working | render it |

The distinction matters because the two look identical downstream — a renderer reading
`CONFIRMATIONS[]` produces nothing either way — while the fixes are opposite: one is a flag change,
the other must not be "chase the flags again". The module's own defensive-parsing rule
(`phase1-query-visualize.md:188-201`) names three causes for a blank field — wrong name, correct name
the flags do not populate, genuinely absent data — and its discriminator ("if `response_schemas`
confirms the path *and* a sibling field from the same response object reads fine, suspect the
**flags**") points at the flags here, which is the wrong answer for this state: the path is confirmed,
`FEATURE_SCORES` reads fine, and adding flags does not fill an array the engine had nothing to put in.

**Two facts, neither governing the other (INV-169).**

- **Documented, server-side.** `get_sdk_reference(topic='response_schemas', filter='why_entities',
  language='python')` on **server 1.33.0, verified 2026-08-21**, documents
  `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[]` in full — `FTYPE_CODE`, `TOKEN`,
  `SOURCE`, `SCORE`, `SCORE_BUCKET`, `SCORE_BEHAVIOR`, `CANDIDATE_FEAT_*`, `INBOUND_FEAT_*`,
  `ADDITIONAL_SCORES.*` — for the `why_entities` / `why_records` / `why_record_in_entity` family. It
  documents the **shape**, and says nothing about when the array has members. The asymmetry the entry
  noticed is real in the schema too: `how_entity_by_entity_id` carries
  `HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO.MATCH_KEY_DETAILS.CONFIRMATIONS[]` as a separate
  documented path (same call, same date), so the two families genuinely have different
  confirmation structures rather than one being a copy of the other.
- **Observed, engine-side — observation-only** (INV-080/INV-149). Empty on every `why_records` call
  on this data, rules `SNAME_SSTAB` and `SF1_PNAME_CFF`, `SZ_INCLUDE_FEATURE_SCORES` in force, SDK as
  installed on 2026-08-18, while `how_entity`'s equivalent populated on the same entity. No MCP route
  can report whether a particular rule produces confirmations — that is a live-engine fact.

⚠️ **Note for the implementer: this observation and the plugin's recorded one differ, and both
stand.** `phase2-discover.md:139-141` records `WHY_KEY_DETAILS` **absent** with
`SZ_INCLUDE_FEATURE_SCORES` alone; this run found it **present but empty** with that flag in force.
Different data, different rules, possibly different SDK builds. Do **not** reconcile them into one
absolute — record both with their conditions, which is what INV-169 requires and what the existing
block already does well for its own pair of observations.

## Proposed change

1. **Add the third branch to step 5's guidance.** When `WHY_KEY_DETAILS` is present and
   `CONFIRMATIONS` is empty, that is a **data/rule outcome, not a flag problem and not a parse
   error** — do not add flags, and do not re-verify a path the schema confirms. Say it in those
   terms, because the module's own discriminator points at the flags for a blank field and would
   mislead here.

2. **Name `FEATURE_SCORES` as the fallback for the teaching step.** It populated on this run and
   carries the same evidence — which feature contributed, with its score and bucket — so step 5's
   demonstration can be completed rather than abandoned. This is the part that turns a dead end into
   a working teaching moment, and it is the highest-value half of this spec.

3. **Record the `how_entity` asymmetry as a documented difference, not a workaround.**
   `MATCH_KEY_DETAILS.CONFIRMATIONS` on a how response and `WHY_KEY_DETAILS.CONFIRMATIONS` on a why
   response are separate documented paths for separate calls; one populating while the other does not
   is a real property of the two structures, not evidence that the why parse is wrong. The file
   already warns against reusing one parser for both
   (`module-03b-truthset-visualization/visualization-api-reference.md:358`) — this extends that from
   *the names differ* to *their population differs too*.

4. **Say what the Bootcamper is told.** Never render an empty breakdown as though it were a result
   (`phase1-query-visualize.md:203-204` already requires this). Here the honest line is that this
   pair's match key has no per-feature confirmation detail on this data, and here is the feature-score
   evidence instead — not "no value returned for X", which reads as a failure.

5. **Mark the observation with its conditions and leave the existing pair intact.** Add it beside the
   two observations already recorded; do not merge or overwrite them (INV-169).

## Acceptance criteria

- [ ] Step 5's guidance distinguishes three states of `WHY_KEY_DETAILS` — absent, present-and-empty,
      present-and-populated — with a different action for each.
- [ ] The present-and-empty branch explicitly says not to add flags and not to re-verify the path.
- [ ] `FEATURE_SCORES` is named as the fallback that lets the teaching step complete, with what it
      carries.
- [ ] The `how_entity` / `why_*` confirmation-path asymmetry is recorded as a documented difference in
      both name and population.
- [ ] The empty case is never rendered as a result; the Bootcamper-facing wording distinguishes "no
      confirmation detail on this data" from a failed lookup.
- [ ] The new observation carries its conditions (rules, flags, SDK, date) and is marked
      observation-only; the two existing observations are unchanged (INV-169).
- [ ] The population behavior is stated as requiring a live engine and is not asserted by the offline
      suite.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — the
  `WHY_KEY_DETAILS` block (`:122-152`) gains the third state and the `FEATURE_SCORES` fallback
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the defensive-parsing discriminator (`:196-201`), so it does not send this case to the flags
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  the why-vs-how confirmation-path note (`:358`) gains the population difference

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew.md` → "Improvement: WHY_KEY_DETAILS.CONFIRMATIONS
  came back empty on every why_records call" (2026-08-18, Module Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces** as a documentation gap.
  `get_sdk_reference(topic='response_schemas', filter='why_entities', language='python')` documents
  `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS.CONFIRMATIONS[]` in full and states no population
  condition; the same call documents `how_entity`'s
  `MATCH_KEY_DETAILS.CONFIRMATIONS[]` as a separate path, confirming the two families differ. Whether
  a given rule populates the array is a live-engine fact and is marked observation-only —
  `owner-checked: get_sdk_reference(topic='response_schemas', filter='why_entities') — the route that
  owns the why response's shape; it returns the CONFIRMATIONS sub-fields in full and carries no
  population/emptiness condition for them, which is why the condition must be stated by the plugin
  rather than relayed.`
- Upstream: already offered and **declined by the maintainer** (per the entry's `Upstream:` field).
  The plugin-side branch is what this spec delivers.
- Related specs: `specs/why-key-details-needs-the-flag-the-plugin-forbids.md`,
  `specs/why-response-carries-why-key-details-not-match-key-details.md`,
  `specs/response-schemas-now-documents-match-info-depth.md`,
  `specs/why-match-info-scalars-are-why-key-and-why-errule-code.md`

## Deviations from this spec, and why (2026-08-21)

**Implemented together with its sibling Module 7 spec, in one commit.** Both edit the same two
regions of `phase1-query-visualize.md` and `phase2-discover.md`, and the region is guarded by four
existing test files. Splitting them would have produced commits that individually fail, for the same
reason the Module 5 batch did.

**Three reworkings were forced by existing guards, and each produced better text than the first
attempt.** (1) `phase1`'s warning keeps the full dotted `WHY_RESULTS[].MATCH_INFO.WHY_KEY_DETAILS`
path: a first rewording split it across two sentences and broke `test_module07_why_flags` and
`test_why_key_details_flag_claim_is_withdrawn`, which require the whole path at that site — and a
parser-writer wants it whole. (2) The new co-occurrence guard matches each field however it is
qualified rather than pinning a bare `` `WHY_KEY` ``; pinning the bare form put it in direct conflict
with those two guards over one sentence. (3) `phase1`'s absence claim carries an `MCP-NEGATIVE`
marker with its `owner:` clause, while `phase2` states the positive instead — the negatives scanner
flagged both, and `implement-spec` prefers asserting what is true, the negative being the form that
expires.

**One site outside the Affected files list was changed** (`phase1-query-visualize.md`'s
defensive-parsing discriminator), because the spec's root cause explains why that rule misleads on
this case. Recorded in the ledger entry; INV-246's point exactly — a spec lists where its author
noticed the defect, not where it lives.
