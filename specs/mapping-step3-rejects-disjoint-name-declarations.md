# `mapping_workflow` step 3 applies a per-object name rule to field declarations, and its message describes a data defect the mapping did not have

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two of five sources were rejected at `mapping_workflow` step 3 with:

> NAME_ORG cannot co-exist with person name attributes NAME_FIRST, NAME_FULL, NAME_LAST — a
> record is either a person or an organization.

**The rule is right about records. It was applied to field *declarations*,** and in both sources the
fields were already disjoint:

- **OPEN-OWNERSHIP** — `NAMES.NAME_ORG` and `NAMES.NAME_FULL`, exactly one populated per record,
  selected by `RECORD_TYPE`.
- **EQUIFAX** — `PRIMARY_NAME_ORG` / `LEGAL_NAME_ORG` appear only on `Company` and `Parent` rows;
  `FEATURES.NAME_FIRST` / `NAME_LAST` / `NAME_FULL` only on `Contact` and `Executive` rows.
  Verified in the source: **zero rows carry both.**

The required workaround is to move every name field into `type_discriminator.field_overrides` even
where **no mapping changes by type** — the override is identity in both branches, declared purely to
satisfy the validator.

⚠️ **The Entity Specification scopes this rule to the NAME object, not the record.** Re-read on
server **1.33.0, 2026-08-28** via `search_docs(category='data_mapping')`, the specification's
`Feature: NAME` section says: *"Keep each `NAME` feature object internally consistent: do not mix
`NAME_FULL` with parsed name fields **in the same object**; do not mix `NAME_ORG` with parsed person
fields **in the same object**"*, and its ❌ example is *"Incorrect (mixing `NAME_ORG` with parsed
person fields)"* inside one `FEATURES` object. So the authoritative scope is **one NAME object** —
narrower than the validator's message ("a record is either a person or an organization") and far
narrower than the declaration-level scope it is enforced at.

**Two costs, neither obvious.**

1. **The message describes the wrong defect.** It states a record-level invariant the mapping
   already satisfied, so the natural reading is *"your data is wrong"* rather than *"declare it
   differently."* The first attempt at OPEN-OWNERSHIP was spent re-checking data that was correct.
   Nothing in the message names `type_discriminator`, which is the actual fix.
2. **The workaround then distorts the coverage warning.** Fields moved into `field_overrides` stop
   being counted, so the mapping reported `covers 55 of 61 profiled source fields` for a mapping
   that dispositions all 61. A Bootcamper reasonably reads a coverage shortfall as unmapped data.
   ⚠️ **This half is already tracked** by
   `the-field-count-miscounts-type-discriminator-half-is-confirmed-not-un-re-run` (implemented) and
   is **not** re-specced here; it is named because the two compound — the workaround for cost 1
   causes cost 2.

## Root cause

**Upstream, and not fully diagnosable from here.** The validator enforces a constraint the
specification states about a single NAME feature object at the level of the schema's field
declarations, where disjointness cannot be expressed except through `type_discriminator`. That is a
reasonable conservative choice for a static validator — the profiler cannot always know two fields
never co-occur — but the *message* does not say that, and the message is the whole interface.

Nothing in this repo could have caught it: the plugin relays `mapping_workflow` faithfully, and the
constraint lives inside one step's runtime validation, which no offline test can see (INV-108).

## Proposed change

1. **Add a dated caution to `phase2-data-mapping.md` at the step-3 mapping submission**, stating
   that a source whose person and organization name fields are disjoint **by record type** must
   declare them through `type_discriminator.field_overrides` — identity overrides included — and
   that the rejection message describes a record-level rule rather than the declaration-level fix.
   Date it with the server version (INV-080).
2. **Point at the coverage consequence in the same caution**, so a Bootcamper who applies the
   workaround is not then surprised by a coverage shortfall — one sentence and a pointer to the
   existing note, not a restatement (INV-179).
3. **Report upstream** (maintainer's call, see Source): scope the check to fields that can co-occur
   on one record — the profiler already knows which source fields co-occur — or make the message name
   `type_discriminator` as the fix. ⚠️ **The message change is the cheaper and larger win**: it costs
   Senzing one string and removes the "your data is wrong" misreading entirely.
4. ⛔ **Do not propose that the plugin pre-empt the validator** by always emitting a
   `type_discriminator`. That would encode a workaround for a constraint that may be scoped
   correctly later, and it would add an identity override to every mapping that does not need one.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` carries a dated caution naming the disjoint-declaration case, the
      `type_discriminator.field_overrides` fix including identity overrides, and the server version
      it was observed on.
- [ ] The caution names the coverage-count consequence by reference rather than restating it
      (INV-179).
- [ ] The caution does **not** instruct the guide to emit a `type_discriminator` unconditionally.
- [ ] A test asserts the caution names `type_discriminator` as the fix, so a later edit cannot
      reduce it to "the data is wrong". Stdlib only, no `plugins/` import (INV-108).
- [ ] Negative-controlled: removing `type_discriminator` from the caution fails the test.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the
  step-3 caution
- `tests/` — one new guard

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: mapping step-3 validation rejects
  NAME_ORG and NAME_FULL even when the source fields are disjoint" (2026-08-25, Module: Data
  Quality, Mapping, and Transformation, Priority: Medium; `Source: self-observed (assistant
  retrospective)`; `Routing: mcp-server`; `Upstream: not yet forwarded`).
- Priority: **Medium**, as filed. The mapping completes once the workaround is applied, so nothing
  is blocked; the cost is time spent re-checking correct data plus a coverage figure that reads as a
  gap.
- MCP re-check: **server 1.33.0, 2026-08-28 — the specification's scope confirmed; the validator's
  behavior NOT re-driven this session.** `search_docs(category='data_mapping')` confirms the
  Entity Specification scopes the rule to *"the same object"* (quoted above), which is the load-
  bearing new fact and is what makes the message's record-level framing wrong. ⚠️ **The rejection
  itself was not reproduced today**: reaching step 3 requires driving `mapping_workflow` through
  steps 1–2 against a real multi-source project, which was disproportionate for a triage pass. It
  rests on **two independent field observations on this same server version** — 2026-08-25 (this
  entry) and 2026-08-27 (a `/dry-run` phase-3 walk that hit the identical rejection and applied the
  identical `type_discriminator` workaround). Marked observation-only per INV-080/INV-149 rather
  than presented as re-verified. ⛔ **Re-drive step 3 before sending anything upstream.**
- Upstream: **not sent — the re-drive removed the reason to send it.** The step-3 re-drive
  was performed on 2026-09-02 against server 1.35.4 (see the section at the end of this
  file): the rejection still fires, but the message now carries a `FIX:` clause naming
  `type_discriminator` explicitly, which was this spec's primary complaint. What remains is
  the framing sentence being broader than the specification it enforces — wording, with the
  actionable guidance already present — and the maintainer judged that not worth an
  anonymous, unfollowable submission. Revisit only if the framing is found to mislead
  someone in practice. ⚠️ Superseded text follows, kept because it records what was owed
  before the re-drive:
  The entry records `not yet forwarded`, which per `feedback-to-specs` Step 1 means the report is
  **still owed** — nobody declined it.
- Related specs:
  `specs/the-field-count-miscounts-type-discriminator-half-is-confirmed-not-un-re-run.md` (the
  coverage-count half, already implemented — deliberately not re-specced here);
  `specs/mapping-workflow-step1-prose-contradicts-its-own-advance-schema.md` (the prior
  `mapping_workflow` upstream report, same handling and same caution pattern);
  `specs/step-2-prose-prescribes-a-record-type-its-own-schema-rejects.md` (the sibling step-2
  scope defect)

## Deviations from this spec, and why (2026-08-28)

**The plugin half is implemented as specified; the upstream half is deliberately NOT done.**
Proposed change item 3 (report upstream) was put to the maintainer on 2026-08-28 and they chose
**leave pending** — the report is still owed, and the re-drive named below remains its precondition.
This is not a decline: nobody declined it.

**MCP re-check: the specification's scope confirmed; the validator NOT re-driven.** Unchanged from
what the Source block records, and restated here because it is the spec's weakest evidence:
`search_docs` confirms the Entity Specification scopes the rule to *"the same object"*, which is the
load-bearing new fact. The rejection itself rests on two field observations on this server version
(2026-08-25 and 2026-08-27) and was **not** reproduced during implementation. ⛔ Re-drive
`mapping_workflow` steps 1–3 before anything goes upstream.

⛔ **Two guards caught real errors in this implementation before it was committed, and both are
worth recording because both were mine.**

1. **An unexecutable citation.** The caution first cited `search_docs(category='data_mapping')` with
   no `query=`. `query` is that tool's only required parameter, so the call as written cannot be
   constructed — `tests/test_search_docs_calls_pass_a_query.py` failed with exactly that reasoning.
2. **A query that was never run.** Fixing (1) by adding a plausible-looking `query=` was worse:
   `tests/test_prescribed_search_queries.py` failed because the phrasing had never been executed
   against the server, and `search_docs` is BM25 — an unexecuted phrasing can return anything, and a
   miss looks identical to documentation that does not cover the topic. The caution now cites the
   query that was **actually executed** during triage, and that query is registered in
   `VERIFIED_QUERIES` with its observed top hits. ⚠️ **This is the "laundered fact" class the whole
   re-verification discipline exists for**, reached by paraphrasing my own earlier call rather than
   by copying from a spec.

**The caution went beside the type-discriminator typing discussion, not at the step-3 payload
table.** `phase2-data-mapping.md` already tells the guide to *"let step 3's `type_discriminator` do
the typing"*; placing the rejection and its fix immediately after that is where a reader is already
holding the relevant concept, rather than several hundred lines away at the advance table.

**The coverage consequence is referenced, not restated** (INV-179) — the field-count note later in
the same file already owns it, and this caution points at it in one sentence.

## Re-drive against server 1.35.4 (2026-09-02) — the actionable half is FIXED upstream

Driven end to end before sending anything upstream: a 6-row CSV with `ROW_KIND`
(`Company`/`Contact`), `PRIMARY_NAME_ORG` populated only on Company rows and
`NAME_FIRST`/`NAME_LAST` only on Contact rows — **zero rows carry both**, verified in the
fixture. `mapping_workflow` start → step 1 → step 2 (`record_type: MIXED`) → step 3
declaring all three name fields with no `type_discriminator`.

**The rejection still occurs.** Verbatim, server 1.35.4, 2026-09-02:

> `schema 'entities': NAME_ORG cannot co-exist with person name attributes NAME_FIRST,
> NAME_LAST — a record is either a person or an organization. FIX: declare the name ONCE
> and let the mapper emit NAME_ORG for an ORGANIZATION record and NAME_FULL (or parsed
> person parts) for a PERSON record, branched by RECORD_TYPE; or use a type_discriminator
> to make the mapping conditional.`

⛔ **The message now names `type_discriminator`, and that was this spec's primary
complaint.** Compare the 2026-08-25 text quoted above, which ended at *"a record is either
a person or an organization"* and which this spec faulted precisely because *"Nothing in
the message names `type_discriminator`, which is the actual fix."* A `FIX:` clause has
since been added that names both remedies explicitly.

**So the cost this spec was filed for is gone.** A Bootcamper hitting this today is told
what to do in the same breath as the rejection; they no longer spend an attempt re-checking
data that was correct.

**What remains is narrower, and is wording rather than behavior:**

1. The rule is still enforced at the level of **field declarations**, not per NAME object.
2. The message still frames it as *"a record is either a person or an organization"*, a
   record-level invariant the mapping already satisfied — while the Entity Specification
   scopes the rule to **one NAME object** (*"do not mix `NAME_ORG` with parsed person fields
   in the same object"*).

⚠️ **This materially changes the upstream question.** It is no longer *"the message
describes the wrong defect and names no fix"* — it is *"the framing sentence is broader
than the specification it enforces"*, with the actionable guidance already present. That is
a documentation nicety, not a workflow defect, and the maintainer should decide whether it
is worth an anonymous submission at all.

⚠️ **Noted in passing, not specced:** step 2's prose instructs `record_type: "MIXED"` for a
type-discriminated schema, while the typed `payload` branch for step 2 enumerates only
`PERSON|ORGANIZATION|VESSEL|AIRCRAFT`. `MIXED` is accepted through the untyped `data`
channel and returns `warnings: ["record_type 'MIXED' is non-standard"]`. Prose and schema
disagree; a client using constrained decoding cannot follow the instruction.
