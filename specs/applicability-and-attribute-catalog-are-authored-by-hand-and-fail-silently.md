# Two hand-authored inputs to the quality score fail silently: per-RECORD_TYPE applicability, and an attribute catalog built by scanning for backticks

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5 Phase 1's quality score has two inputs that are **authored per run** rather than derived,
and both produced wrong numbers that looked like findings about the data. The rules governing them
are correct and were followed; what is missing is a check that runs **before** the score is
reported. Two root causes, one step, each independently implementable.

### 1. Applicability is authored by hand, so getting it wrong is the default failure

The applicability table was authored for five sources with ADDRESS, PHONE, WEBSITE and TRUSTED_ID
marked as applying to **both** record types on EQUIFAX. Measured per type, all four appear on
**ORGANIZATION records only** — 100% / 91.5% / 42.3% / 100% — and on **0%** of PERSON records, while
EMAIL and GENDER are the mirror image (0% org, 10.6% / 8.3% person). EQUIFAX's person records are
officer and contact records attached to a company, so a business address is data that *structurally
cannot* exist on them.

With the wrong applicability EQUIFAX scored **70.5%** and landed in the "acceptable but has some
gaps" band. Corrected, it scores **85.7%** and passes cleanly.

⛔ **The wrong score would have sent a Bootcamper to remediate a source with nothing wrong with it** —
the false alarm **INV-264** exists to prevent — on the largest source in the project (72,799
records). `phase1-quality-assessment.md:410-411` already computes completeness per `RECORD_TYPE`,
and INV-174 already governs per-record applicability. **The rules held; the input to them did not.**

**The discriminator is cheap and already in hand.** A field marked "applies to both" that measures
100% on one type and 0% on the other is an applicability error *by construction* — no real field
behaves that way — and the profiling pass already holds both numbers.

### 2. The attribute catalog was built by scanning for backticked tokens, and under-collected by 81%

The Entity Specification catalog was built with a backticked-token regex. It found **21** attributes
instead of **110**, and reported `NAME_ORG`, `ADDR_LINE1` and `PHONE_NUMBER` as unrecognized keys.

**Re-measured against the shipped specification on server 1.33.0, 2026-08-28**, and the reported
figures reproduce exactly. Fetching `senzing_entity_specification.md` from the URL
`download_resource` returns (73,051 bytes) and parsing its feature tables:

```text
first-column attribute names, BACKTICKED : 0
first-column attribute names, PLAIN TEXT : 102
backticked ALL-CAPS tokens anywhere      : 21
union (plain first-col + any backticked) : 110
   NAME_ORG       plain-in-first-col=True  backticked-anywhere=False
   ADDR_LINE1     plain-in-first-col=True  backticked-anywhere=False
   PHONE_NUMBER   plain-in-first-col=True  backticked-anywhere=False
```

⚠️ **The same names render *differently* through a different route, which is what makes this a trap
rather than a typo.** `search_docs(category='data_mapping')` excerpts return the very same tables
with the names **backticked** — e.g. `` | `OTHER_ID_TYPE` | ``. So a regex tuned on a `search_docs`
excerpt works there and silently under-collects by 81% against the downloaded document, and the
plugin's mapping flow uses the downloaded document.

The wrong catalog would have reported every source as having **zero** mapped fields, which feeds the
fast-path decision in step 5a and the completeness denominator in step 6. It was caught only by the
step's own *"sanity-check any 0% or 100% figure"* instruction — four of five sources reporting
exactly zero specification attributes is not a plausible finding about CORD data.

## Root cause

Both are **measurement faults that present as data findings**, and neither has a structural guard:

- The applicability set is a judgment authored per source. `phase1-quality-assessment.md` states the
  per-`RECORD_TYPE` rule and warns that a low score with high NAME/ADDRESS coverage is probably an
  applicability error — both of which caught this, but **after** the wrong number existed.
- The catalog's parse depends on a rendering detail of an external document that differs between the
  two routes that serve it, and nothing in the plugin names which rendering to expect.

## Proposed change

1. **Require a per-`RECORD_TYPE` presence breakdown for every field marked "applies to both",
   before the score is reported.** A field at 100%/0% across the two types is an applicability error
   by construction and MUST stop the score rather than feed it. The breakdown is free — the
   profiling pass already holds the per-type presence counts.
2. **State the specification's rendering where the catalog is built** (step 3 or step 5a): in the
   document `download_resource` serves, feature-table attribute names are **plain text in the first
   column**, not backticked, and a catalog built by scanning for backticked tokens under-collects by
   roughly 80%. ⛔ **Say that `search_docs` excerpts render the same names backticked**, or the next
   author tunes on the wrong sample and reproduces this exactly.
3. ⛔ **Do not hardcode the attribute count.** 110 is what the document holds today; pinning it in
   shipped prose recreates the class of defect this repo has already had to retract. State the
   *parse rule*, and let the count be whatever the document yields.
4. ⛔ **Do not weaken the existing sanity-check instruction.** It is what caught the second fault,
   and it stays exactly as written.

## Acceptance criteria

- [ ] Step 6 requires a per-`RECORD_TYPE` presence breakdown for any field marked "applies to both",
      and states that a 100%/0% split is an applicability error that stops the score.
- [ ] The breakdown requirement is stated as a precondition of reporting the score, not as a
      post-hoc sanity check.
- [ ] Shipped text names the specification's plain-text first-column rendering **and** the
      contrasting backticked rendering in `search_docs` excerpts.
- [ ] No shipped file states an attribute count.
- [ ] The existing "sanity-check any 0% or 100% figure" instruction is unchanged in substance.
- [ ] A test asserts both additions and that no attribute count appears. Stdlib only, no `plugins/`
      import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  step 6's scoring precondition near `:410-411`, and the catalog-build guidance at step 3 / step 5a
- `tests/` — a guard for the breakdown requirement and the rendering note

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: EQUIFAX quality score was wrong
  until per-RECORD_TYPE applicability was corrected" (2026-08-25, Module: Data Quality, Mapping, and
  Transformation, Priority: Medium; `Source: self-observed (assistant retrospective)`). Both faults
  were caught and withdrawn by the guide; a Bootcamper would have seen only the scores.
- Priority: **Medium**, as filed. The existing rules did catch both before anything shipped, which
  caps severity — but each catch was after the wrong number was computed, and the first would
  otherwise have routed the largest source in the project into needless remediation.
- MCP re-check: **server 1.33.0, 2026-08-28 — confirmed, and the reported figures reproduce
  exactly.** `download_resource(filename='senzing_entity_specification.md')` returned a URL; the
  document was fetched (HTTP 200, 73,051 bytes) and parsed, giving 21 backticked tokens, 102
  plain-text first-column names and a 110-name union — the report's own numbers.
  `search_docs(query='entity specification attribute names feature tables NAME_ORG ADDR_LINE1
  PHONE_NUMBER', category='data_mapping')` returned the same tables with names **backticked**,
  establishing the two-rendering trap the report did not name. The per-type presence percentages are
  **observation-only** from this run's CORD data (INV-080, INV-149) — no MCP route reports them.
- Upstream: not applicable — the rendering is a property of Senzing's published document and is not
  a defect; the defect is that the plugin does not say which rendering to expect.
- Related specs: `specs/quality-score-per-record-type.md` (established the per-record-type rule this
  spec adds a precondition to, already implemented);
  `specs/inv174-per-record-applicability-is-unverified.md` (INV-174's coverage gap);
  `specs/completeness-denominator-has-two-readings-on-a-raw-source.md` (the denominator this feeds)
