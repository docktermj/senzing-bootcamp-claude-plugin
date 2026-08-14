# Synthesized scenarios generate flawless data, so Module 5's quality gate is unreachable

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 4 Step 2's `provenance: synthesized` branch tells the guide exactly what complexity to build
into the generated source files:

> ⛔ **Generate the mapping complexity the scenario promised** — Module 1 Step 4a's invariant
> required it, so the files must actually carry it: names split into components in one source and
> joined in another, addresses as free text where the scenario says so, per-campaign duplicates, and
> the deliberate inconsistencies across sources.

Every item on that list is about **shape** — how a value is structured across sources. None is about
**quality** — missing values, malformed values, off-pattern values. So a guide following the
instruction faithfully produces three files in which every field is populated and every value is
uniformly formatted.

Module 5 Phase 1 step 6 then scores that data with

```text
quality_score = 0.70 × completeness + 0.25 × format_consistency + 0.05 × (100 − duplicate_rate)
```

and a fully-populated, uniformly-formatted source scores **100.0**. Observed live on a phase-3 dry
run, 2026-08-14, on a three-source generated Customer 360 scenario:

| Source | Completeness | Format consistency | Duplicate rate | Overall |
|---|---|---|---|---|
| MERIDIAN_CRM (14 records) | 100.0% | 100.0% | 0.0% | **100.0 ✅** |
| MERIDIAN_STOREFRONT (12) | 100.0% | 100.0% | 0.0% | **100.0 ✅** |
| MERIDIAN_REWARDS (10) | 100.0% | 100.0% | 0.0% | **100.0 ✅** |

Zero empties in any applicable field, confirmed by printing sample values per the step's own
100%-sanity-check ⛔ — the scores are real, not a measurement artefact.

**The consequence: both gating branches of step 7 are dead on this path.** The gate has three
branches — ≥80% (statement, no question), 70–79% (👉, two options), <70% (👉, two options) — and a
generated-scenario Bootcamper reaches the first one every time. They never see:

- a quality warning, or the remediation conversation behind it;
- the "improve the weakest fields first" option;
- any of step 6's diagnostic apparatus — the per-field completeness breakdown that means something,
  the "report the fields that drag format consistency down" instruction, the `issues` list the
  registry gains below 70;
- the per-`RECORD_TYPE` applicability reasoning (INV-174), which only bites on a mixed or gappy
  source.

They see `100% ✅` three times and reasonably conclude the quality step is a formality. That is a
teaching failure in the module whose Phase 1 is **half about quality** — the module is named "Data
Quality, Mapping, and Transformation" and its first phase is "Quality Assessment".

### Why this is Module 4's defect, not Module 5's

Module 5's scoring is correct: the data genuinely is clean, and inventing gaps at scoring time would
be falsifying the measurement. The gap is that Module 4 generates data designed to exercise the
*mapping* half of Module 5 and not the *quality* half, while Module 1 Step 4a's invariant — the
thing Module 4 cites as its authority — speaks only of "mapping-complexity-rich" data:

> **Validate invariants** before recording: at least two distinctly named data sources, each with ≥1
> record; the data is mapping-complexity-rich (needs at least one transformation when mapped to the
> Senzing Entity Specification); …

So the requirement was scoped to mapping from the start, and Module 4 implemented exactly what it
was asked for. Nothing ever asked the generated data to be *imperfect*.

## Root cause

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`, Step 2's
`provenance: synthesized` branch — the complexity list enumerates structural variation only.

Contributing: `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md`
Step 4a's invariant list requires "mapping-complexity-rich" and nothing about quality, so the
generated scenario is never promised to have gaps in the first place.

## Proposed change

**Extend the synthesized-generation instruction to require realistic quality gaps, at a level that
lands the source in a stated band.** In Module 4 Step 2's `synthesized` branch, alongside the
existing mapping-complexity ⛔, require the generated data to carry:

- **missing values** in non-key fields, at a rate that puts at least one source in the **70–79%**
  band so the first gating branch is exercised — e.g. a phone absent on a third of records, an
  address missing on a handful;
- **off-pattern values** in at least one field per source (a date in a second format, an unformatted
  phone among formatted ones, a lowercase state code), so `format_consistency` is not 100%;
- **at least one source that scores ≥80%**, so the Bootcamper sees the contrast rather than a
  uniformly gappy dataset;
- and the existing structural complexity, unchanged.

⛔ **State the intent, not just the mechanics:** the gaps exist so the quality assessment has
something to find and the remediation conversation actually happens. A generator that "helpfully"
produces clean data defeats the module.

Then **record the intended bands in the registry** (a `quality_intent` note per source, or in
`collection_summary`) so Module 5 can state the contrast, and so a future run can tell a generation
bug from a scoring bug.

⚠️ **Do not put the gaps in the record keys.** `DATA_SOURCE`/`RECORD_ID` must stay present and
unique — a missing key is a load failure, not a quality gap, and `duplicate_rate` is computed on
that pair (INV-180). The per-campaign duplicate pair Module 4 already requires must keep its
**distinct** keys, exactly as today.

### Alternative considered and rejected

*Leave Module 4 alone and have Module 5 say "your generated data is clean, so here is what a gappy
source would look like."* Rejected: it teaches the shape of the conversation without the
conversation, leaves the two gate branches untested by any run, and puts illustrative numbers in a
module that must present measured ones.

## Acceptance criteria

1. Module 4 Step 2's `synthesized` branch requires missing values and off-pattern values in addition
   to the existing structural complexity, and states the reason (so the quality assessment has
   something to find).
2. It requires the generated set to span bands — at least one source landing in 70–79% and at least
   one at ≥80% — and forbids gaps in `DATA_SOURCE`/`RECORD_ID`.
3. The intended bands are recorded in `config/data_sources.yaml` so Module 5 can reference them and
   a later run can distinguish a generation fault from a scoring fault.
4. Module 5's scoring, thresholds, bands, presence test (INV-128) and per-`RECORD_TYPE`
   applicability (INV-174) are asserted **unchanged** — this spec changes what data arrives, never
   how it is measured.
5. A test asserts the synthesized branch names both quality dimensions and the key-exemption, and is
   negative-controlled by removing each requirement independently.
6. Cross-platform, language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` (Step 4a's
  invariant list, so the promise and the generation agree)
- `tests/test_synthesized_scenario_has_quality_gaps.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14 by generating a three-source
  synthesized scenario in Module 4 and scoring it in Module 5, reaching 100.0/100.0/100.0 and
  therefore the ≥80% branch for every source (`Source: self-observed (assistant retrospective)`).
  The 100% figures were sanity-checked against sample values per step 6's own ⛔ and are genuine.
- Priority: **Medium.** Nothing breaks and no wrong statement is made to the Bootcamper — the data
  really is clean. What is lost is half of a required module's teaching, on what is now a
  first-class path (the Business Case Offer produces `synthesized` by design for every
  customer-facing category), plus any live exercise of two gate branches.
- MCP re-check: n/a (no Senzing fact — the scoring formula and thresholds are the plugin's own).
  Server version this session is **1.32.9** (`get_capabilities`, 2026-08-14).
