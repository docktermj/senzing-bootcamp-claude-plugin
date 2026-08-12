# The Module 5 quality score routes a gate to the percentage point and is never defined

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 5 Phase 1 Step 6 opens (`phase1-quality-assessment.md:302-303`):

> For each data source, compute a quality score based on **field completeness, format consistency,
> and duplicate rate**.

and repeats the trio at `:387`. **How the three combine into the single number is stated nowhere.**

What *is* stated precisely is what the number does. `:425-428`:

> ⛔ **The status label MUST match the band above** — `✅` only at ≥80%, `⚠ Acceptable — some gaps`
> at 70-79%, `⚠ Recommend fixing before mapping` below 70%. **Derive the label from the computed
> score** rather than copying one from this example

and `:507-527` routes the iterate-vs-proceed gate on the same bands, with different pinned 👉
questions per band — 70–79% offers "improve the weakest fields first", below 70% opens with "your
data quality needs attention".

So a gate that changes what the Bootcamper is asked, to the percentage point, is fed by a figure the
guidance never defines. Two guides following this file faithfully compute different scores.

**Measured on a real source during a dry-run walk, 2026-08-12** — `PPP_LOANS`, 3,488 records, all
`RECORD_TYPE: ORGANIZATION`, completeness computed with the presence test Step 6 mandates:

| Reading of "field completeness" | Score |
|---|---|
| Entity-Specification attributes only (the 8 keys that resolve) | **100.0%** |
| Every root key, including the 11 unmapped source columns | **94.4%** |

Both land in the same band here, so this source routes identically either way — stated plainly
rather than dressed up. But the module's **own worked example** is a case where the same ambiguity
crosses a band: `:339` records a sanctions list scoring "**52% completeness / 69% overall**" that
became **97%** on rescoring — 69% and 97% are on opposite sides of two thresholds, and the difference
there was *which records a field was averaged over*. This spec is the adjacent gap: *which fields*,
and *how the three dimensions weight*.

**The file is unusually careful everywhere else in this step**, which is what makes the hole
conspicuous. It defines "present" exhaustively and forbids re-inventing it (`:305-322`), mandates
per-`RECORD_TYPE` measurement with a worked failure (`:331-343`), requires deriving applicability
from the specification rather than a hardcoded list, and demands a sanity check on any 0%/100%
figure. Every input to the score is specified except the arithmetic that produces it.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

**The dimensions and the bands were written at different times, and nothing joins them.**

The bands and the ⛔ that pins the label to them read as a late hardening — they exist because a
`✅` once appeared beside a 78%, which is a *label-vs-score* defect. Fixing that made the mapping
from score to label exact while leaving the mapping from data to score unstated. The
`52% / 69% overall` figures at `:339` come from a real incident, so a composite genuinely existed in
whoever's head wrote it; it was never written down.

Nothing catches it because no test computes a score — the tests assert the *label rule* and the
*presence test*, both of which are well specified — and a prose reader sees three named dimensions
and precise bands and reads the middle as obvious. It is only when you actually have to produce the
number that the gap appears, which is why a walk found it and three audits did not.

## Proposed change

1. **Define the composite explicitly** — the three dimensions, how each is computed, and how they
   weight. Whatever is chosen, state it as arithmetic a second guide would reproduce.

2. **Say which fields enter completeness.** The choice is real and consequential: Entity
   Specification attributes only, or every root key. Recommend **spec attributes plus any field
   dispositioned in mapping**, since scoring a source down for raw columns it has not yet been asked
   about penalises it for work this module has not done yet — the same "fails toward false alarm"
   shape INV-174 records — but the decision is the maintainer's and the point is that it be written.

3. **Define format consistency and duplicate rate** at least as tightly as presence is defined.
   Duplicate rate in particular MUST be computed on `(DATA_SOURCE, RECORD_ID)` per INV-180, not on
   whole-row equality — re-sending that pair replaces a record rather than adding one, so row-level
   duplicate counting measures something Senzing does not.

4. **Keep the label ⛔ exactly as it is.** It is correct and it is what makes this gap visible.

## Acceptance criteria

- [ ] Step 6 states the composite formula — each dimension's computation and its weight — such that
      two independent implementations produce the same score on the same source. Verified by opening
      the file.
- [ ] Step 6 states which fields enter completeness, and why, in one sentence.
- [ ] Format consistency and duplicate rate each have a stated definition; duplicate rate is defined
      on `(DATA_SOURCE, RECORD_ID)` and cites INV-180.
- [ ] The band thresholds (≥80 / 70–79 / <70), the label ⛔ at `:425-428` and the pinned gate
      questions at `:507-527` are **unchanged** — verified by `git diff`.
- [ ] A test asserts Step 6 defines a computable score: that the three dimension names appear
      **and** that a weighting or formula statement accompanies them. **Not vacuous:** it names the
      file it parsed and fails if the formula section is removed.
- [ ] **Negative-controlled, mutation verified to land:** deleting the formula statement fails the
      test; deleting a band threshold fails the existing label guard. Revert both.
- [ ] A worked example computes one score end-to-end from a small record set, so the arithmetic is
      demonstrated rather than only described.
- [ ] Full suite passes (baseline **1756 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); cross-platform and language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
- `tests/` — one new guard.

## Source

- Dry run, **phase 3 (conversational walk)**, 2026-08-12, maintainer answering as the Bootcamper.
  Found while executing Step 6 against a real 3,488-record source: the presence test, the
  per-`RECORD_TYPE` rule and the 0%/100% sanity check were all followable as written, and producing
  the single number they feed was not.
- Both figures above were computed during the walk with the presence test as Step 6 defines it
  (`false`/`0` present; empty containers absent), on `data/raw/PPP_LOANS.jsonl` fetched and
  count-verified per INV-203.
- Priority: **Medium.** Every Bootcamper reaches this gate on the required path; the score is
  reproducible only by accident, and the failure is silent — a plausible number routes the gate and
  nothing reveals that a different guide would have routed it elsewhere.
- MCP re-check: **n/a — no Senzing fact.** Server **1.32.9** this session;
  `download_resource(filename='senzing_entity_specification.md')` was called to perform Step 4's
  comparison, not to establish anything this spec asserts.
- Related: INV-128 (the presence test, well specified), INV-174 (per-record-kind measurement, well
  specified), INV-180 (record identity for the duplicate dimension), INV-193 (a figure presented as
  evidence must be able to bear it).

## Invariants introduced

**None proposed.** This is a definition gap in one step, not a standing rule the ruleset lacks —
INV-128, INV-174 and INV-180 already constrain the inputs. If the maintainer wants the general form
("a computed figure that routes a gate MUST have its computation stated"), that is worth its own
discussion; it is deliberately not smuggled in here.

## Deviations from this spec, and why (2026-08-12)

⚠️ **The weights are my choice, not the spec's, and the maintainer should review them.** The spec
required that a formula be *stated*, recommended which fields enter completeness, and explicitly
left the decision to the maintainer. It did **not** specify weights. What shipped is:

```text
quality_score = 0.60 × completeness + 0.25 × format_consistency + 0.15 × (100 − duplicate_rate)
```

Completeness dominates because it is the dimension the module actually measures per record, against
a defensible denominator (INV-174), and because it is the one a bootcamper can act on. Duplicate
rate is weighted lowest because at this stage duplicates are *expected* — resolving them is what
Senzing is for, so a high duplicate rate is not a data-quality defect in the way missing fields are.
These are reasonable, they are not derived from anything, and a different split would move sources
across the band boundaries. **If you disagree with the ratio, change the three numbers; nothing else
in the implementation depends on them.**

**The recommended field rule was implemented as recommended:** completeness counts fields resolving
to an Entity Specification attribute or a structural key, plus any source field already dispositioned
in mapping — with the `PPP_LOANS` 100% vs 94.4% measurement quoted inline as the reason.

**A worked example was added** beyond the criteria's wording, because a formula stated but never
exercised is still ambiguous about rounding and about whether `duplicate_rate` is inverted.

**No other deviation.** The bands, the label ⛔ and both pinned gate questions are unchanged,
verified by `git diff`.
