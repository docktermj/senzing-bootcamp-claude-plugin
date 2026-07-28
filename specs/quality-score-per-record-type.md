# Score completeness per record type — organizations have no date of birth

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Scoring completeness by aggregate feature percentages rated a sanctions list with **NAME and ADDRESS
on 100% of records** at 52% completeness and 69% overall — landing it in the "Recommend fixing before
mapping" band.

The cause was averaging DOB (32%), PASSPORT (14%) and GENDER (25%) across a source where **71 of 110
records are ORGANIZATIONS**, which have no date of birth or passport *by definition*. Rescoring each
record against the features applicable to its own record type gave **97%**.

Had the first figure been trusted, the bootcamper would have been sent to remediate data with nothing
wrong with it.

This fails toward false alarm, and it will misreport most real compliance datasets. Mixed
person/organization sources are the norm in KYC, AML, sanctions screening, vendor MDM and
beneficial-ownership work — several of the plugin's own headline use cases.

## Root cause

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
computes the score at `:164` — *"For each data source, compute a quality score based on field
completeness…"* — and defines presence rigorously at `:168`: a value's presence is a property of the
value, not the key, with `false` and `0` counting as present. It even warns at `:187` that *exactly*
full or *exactly* zero coverage across every record is the signature of a broken presence test.

**All of that governs a single value. None of it governs whether the feature applies to the record at
all.** The score averages each feature's coverage across the whole source, so a feature that is
inapplicable to most records drags the average down exactly as if the data were missing. The example
worked at `:229-235` is a single-type source, so the arithmetic looks right there.

The Senzing Entity Specification organizes features by record type, which is what makes the aggregate
the wrong denominator. Verified via `search_docs(category='data_mapping')` on server 1.32.1,
2026-07-28 — the "What features to map" table labels them explicitly:

| Feature | How the specification labels it |
|---|---|
| `NAME` (person) | "Personal names… `NAME_FIRST`, `NAME_MIDDLE`, `NAME_LAST`" |
| `NAME` (organization) | "Organization legal or trade name… (`NAME_ORG`)" |
| `DOB` | "**Person** date of birth" |
| `ADDRESS` (person) | "Postal/physical address" |
| `REGISTRATION_DATE` | "**(organizations)** — Organization registration/incorporation date" |

and `RECORD_TYPE` itself is "Recommended… **Prevents records of different types from resolving.** Use
standardized kinds (`PERSON`, `ORGANIZATION`)". So the specification treats DOB as a person feature and
`REGISTRATION_DATE` as an organization feature; a score that averages the former across organizations
is measuring absence that the specification predicts.

## Proposed change

1. **Measure completeness per record, against the features applicable to that record's
   `RECORD_TYPE`** — then aggregate those per-record scores. Not per-feature-across-the-source.
2. **Derive applicability from the Entity Specification via MCP, not from a hardcoded list.** Confirm
   which features are person-oriented and which are organization-oriented with
   `search_docs(category='data_mapping')` at assessment time (INV-080). Do not ship a static table
   that silently rots.
3. **Handle the unknown-type case explicitly.** `RECORD_TYPE` is *recommended*, not required, and the
   specification says to leave it blank when unknown. Where a record has no type, score it against the
   features that apply to any type rather than penalizing it for both sets — and say in the report how
   many records were scored that way, since a source with no `RECORD_TYPE` at all is a different
   finding worth surfacing.
4. **Add the mixed-source case as a worked example** beside the existing empty-container one at
   `:229-235`, using the shape that produced this: a source that is ~65% organizations scoring 69%
   aggregate versus 97% per-record-type.
5. **Extend the sanity check at `:187`.** It currently flags 0%/100% coverage as a probable presence-test
   bug. Add: a low score on a source with high NAME/ADDRESS coverage is a probable
   applicability error — check the record-type mix before reporting the score or routing to remediation.

## Acceptance criteria

- [ ] Completeness is computed per record against features applicable to that record's `RECORD_TYPE`,
      then aggregated — a source of organizations is not penalized for lacking DOB or PASSPORT.
- [ ] Feature applicability is obtained from the Entity Specification via MCP at assessment time, not
      from a list hardcoded in the plugin (INV-080).
- [ ] Records with no `RECORD_TYPE` are scored against type-independent features, and their count is
      reported rather than hidden.
- [ ] A mixed person/organization source with NAME and ADDRESS on every record does not land in a
      "fix before mapping" band on account of person-only features.
- [ ] The sanity check treats a low score alongside high NAME/ADDRESS coverage as a probable
      applicability error, before the score routes anyone to remediation.
- [ ] The existing presence-test definition (`false` and `0` are present; presence is a property of the
      value) is unchanged — this spec adds a second question, it does not relax the first.
- [ ] The proceed/iterate gate stays non-blocking (INV-048): a scoring correction never becomes a new
      blocker.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the rule is
      arithmetic over record types and MCP-sourced applicability, with no platform or language
      specifics.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — the
  score definition (`:164-187`), the worked example (`:229-235`), and the sanity check (`:187`).
- `tests/test_quality_presence_test.py` — extend: the presence rules still hold, and the score is
  per-record-type rather than per-feature-aggregate.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Quality scoring must be per-record-type, or
  organizations are penalized for having no date of birth" (2026-07-28, Module Data Quality, Mapping,
  and Transformation; `Source: self-observed (assistant retrospective)`; `Routing: plugin`;
  `Upstream: not applicable`)
- Priority: High
- MCP re-check: **confirmed and strengthened** on server 1.32.1, 2026-07-28.
  `search_docs(category='data_mapping')` returns the Entity Specification's "What features to map"
  table labelling `DOB` as "Person date of birth", `REGISTRATION_DATE` as "(organizations)", and `NAME`
  separately for person and organization — so per-type applicability is the specification's own model,
  not an inference. `RECORD_TYPE` is "Recommended", which is why the unknown-type case needed handling
  the entry did not mention.
- Upstream: not applicable
- Related specs: `specs/quality-scoring-presence-test.md` (**this extends it** — that spec fixed what
  "present" means for a value; this fixes which features belong in the denominator),
  `specs/rename-data-quality-mapping-display-name.md`,
  `specs/analyzer-legacy-sublist-format-false-errors.md` (the sibling
  false-alarm-from-a-quality-gate defect),
  `specs/organization-search-requires-name-org.md` (the other place organization data was mishandled)
