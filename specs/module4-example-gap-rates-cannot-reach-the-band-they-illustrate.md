# Module 4's example gap rates score ~95%, not the 70-79% band they illustrate

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On the generated-scenario path, Module 4 requires the synthesized data to put at least one source in
the **70-79%** band so Module 5's remediation branch is reachable, and illustrates the gaps that do
it with *"a phone absent on roughly a third of its records, an address missing on a handful"*.

Generating to those rates and scoring with Module 5's formula produced **94.9%** — squarely in the
`>=80` band the requirement exists to avoid. Landing in 70-79 required gapping five of seven fields
far more aggressively (phone ~55% missing, address ~45%, city ~35%, zip ~25%, state ~20%).

Because Module 4 records the intended band as `quality_intent` in `config/data_sources.yaml`
**before** anything scores the data, the mismatch is invisible at generation time and surfaces a
module later — where, as Module 4's own text says, a source that scores wrong is indistinguishable
from a source that was scored wrong.

## Root cause

**Arithmetic, not wording.** The illustration and the requirement are separated by the 0.70 weight and
a per-record denominator, and nothing in either module does the multiplication.

The requirement, `module-04-data-collection/SKILL.md:246-248`:

> - **missing values in non-key fields**, at a rate that puts **at least one source in the 70-79%
>   band** — a phone absent on roughly a third of its records, an address missing on a handful.

The formula, `module-05-data-quality-mapping/phase1-quality-assessment.md:392`:

```text
quality_score = 0.70 × completeness + 0.25 × format_consistency + 0.05 × (100 − duplicate_rate)
```

And completeness, `:406-408` — "the mean, across records, of the share of **applicable** fields that
are present in that record … per-`RECORD_TYPE` applicability (INV-174)".

Let `n` be the applicable fields per record and `m` the **sum** of the per-field absence rates,
expressed in whole fields (a field missing on 30% of records contributes 0.30). Then
`completeness = 100 × (1 − m/n)`, and:

```text
quality_score = 70 − 70·(m/n) + 0.25 × format_consistency + 0.05 × (100 − duplicate_rate)
```

For a seven-field source with clean formatting and distinct keys (`format_consistency = 100`,
`duplicate_rate = 0`, as INV-239 requires of the keys), that collapses to
**`quality_score = 100 − 10m`**. Computed 2026-08-17:

| Gapping | `m` | completeness | score |
|---|---|---|---|
| Module 4's illustration — phone 30%, address ~5% | 0.35 | 95.0 | **96.5** (95.2 at `format_consistency` 95) |
| one field missing on **every** record | 1.00 | 85.7 | **90.0** |
| **five** of seven fields, each missing 30% | 1.50 | 78.6 | **85.0** |
| what the 70-79 band actually needs | 2.1 – 3.0 | 58.9 – 71.8 | 70 – 79 |

Three things follow, and each is a separate reason the current text cannot work:

1. **The illustration is off by roughly a factor of six.** It totals `m ≈ 0.35`; the band needs
   `m ≥ 2.1`.
2. **No single-field gap can reach the band at any rate.** A field absent on *every* record moves the
   score by `0.70 × 100/n` — 10 points on seven fields. The band starts 21 points down. So the very
   shape the illustration suggests (one field heavily gapped, another lightly) is arithmetically
   incapable of the outcome it is offered as an example of.
3. **The requirement is scale-free and the illustration is not.** Rearranged, the band needs
   `m/n ∈ (0.30, 0.43]` — **30% to 43% of every applicable field slot in the source empty** —
   independent of `n`. That is the number the generator needs and the one no module states.

**Why nothing caught it.** `quality_intent.target_band` is written by Module 4 at generation time and
read by nobody until Module 5 scores the data, so the two numbers are never compared in the same step.
Module 4's own note (`SKILL.md:280-282`) explains that `quality_intent` exists so "a later run can
tell a **generation** fault from a **scoring** fault" — and in this case that mechanism works exactly
as designed and still resolves the wrong way: a guide that followed the example rates faithfully sees
`target_band: "70-79"` against a measured `≥80`, and has no reason to suspect the example rather than
the scoring. The `quality_intent` example at `SKILL.md:271-278` carries the same rate
(`gaps: ["phone missing ~30% of records", …]`) beside `target_band: "70-79"`, so the inconsistency is
shipped twice, once as an instruction and once as a sample of the recorded result.

⚠️ **This spec fixes the illustration, and it surfaces a question the illustration was hiding.**
Reaching 70-79 honestly means about a third of all field values absent. That may be more degradation
than a plausible CRM or POS export would carry, in which case the mismatch is not only in the example
rates but in the pairing of a 0.70 completeness weight with a band that must be reachable on
realistic synthetic data. The fix below makes the requirement achievable and states the cost
plainly; whether the **band** or the **weights** should move is a design decision for the maintainer
and is deliberately not taken here.

## Proposed change

1. **State the requirement as a completeness target, not as per-field absence rates.** Replace the
   illustrative rates at `SKILL.md:246-248` with the figure the generator can act on: gap enough
   non-key fields that mean per-record completeness lands in roughly **59-72%** — equivalently, leave
   **30-43%** of all applicable field slots empty — because that is what the composite formula turns
   into a 70-79 score.
2. **Route to Module 5's formula; do not restate it.** Module 4 already routes rather than duplicates
   for the license-capacity decision (`SKILL.md:288-291`, "⚠️ **Do not re-derive or restate its
   measurement procedure at this step**"), and for the same reason: a rule stated twice drifts in one
   of them. Point at `phase1-quality-assessment.md` Step 6 for the arithmetic and keep only the
   target in Module 4.
3. **Ship one worked example with the multiplication shown**, for a seven-field source, so the next
   reader can check the claim instead of trusting it. The table above is the material.
4. **Say that no single field can do it.** One line, because it is the specific wrong intuition the
   current example creates, and it is cheap to state: on `n` applicable fields, a field absent on
   every record costs at most `0.70 × 100/n` points.
5. **Fix the `quality_intent` sample at `SKILL.md:271-278`** so its `gaps` list is consistent with its
   own `target_band: "70-79"`. A sample of a recorded result that could not have produced that band is
   the same defect in a second place.
6. **Have the generation step check its own output against the band it just recorded**, and regenerate
   or widen the gaps if it missed. The formula is fully specified, the generator controls the data
   completely, and this is the only point where the intent and the outcome are both available. It
   must **read** Module 5's formula rather than carry a copy, per item 2 — and it must not adjust the
   *score*, only the *data* (INV-239's diagnose-don't-grade line: inventing gaps at scoring time
   would falsify a measurement the bootcamper is told is real; correcting the generated data before
   it is scored is the generator's own job).
7. **Keep the ≥80% contrast source clean.** The gapping needed for the low band is heavy enough that
   it must be concentrated in one source; INV-239 requires at least one source at ≥80% so the
   comparison is visible, and that requirement is unchanged.

## Acceptance criteria

- [ ] Module 4 states the low-band requirement as a completeness/slot-emptiness target, with the
      70-79 score it produces, and no longer offers per-field absence rates as the way to reach it.
- [ ] The shipped worked example's arithmetic is correct: substituting its figures into
      `0.70 × completeness + 0.25 × format_consistency + 0.05 × (100 − duplicate_rate)` lands in
      70-79. Verified by computing it, not by reading it.
- [ ] The `quality_intent` sample's `gaps` list is consistent with its `target_band`.
- [ ] Module 4 does not restate Module 5's formula; it routes to it.
- [ ] The generation step verifies the produced data against the recorded `target_band` before Module
      4 closes, and widens the gaps rather than adjusting any score if it missed.
- [ ] A test asserts that any per-field absence rate Module 4 offers as an example, substituted into
      the formula for the field count that example names, lands in the band that example claims —
      negative-controlled by restoring the current "roughly a third … a handful" rates and confirming
      the guard fails.
- [ ] INV-239 still holds: gaps in non-key fields only, keys present and unique, at least one source
      at ≥80%, `quality_intent` recorded per source.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the change
      is prose and arithmetic in two skill files; the generator is whatever language the bootcamper
      chose, and the target is stated as a number, not as code.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the requirement at
  `:246-248`, the `quality_intent` sample at `:271-278`, and the new self-check.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  no change expected; confirm Step 6 remains the single statement of the formula (`:392`) and of the
  completeness denominator (`:406-431`).
- `specs/INVARIANTS.md` — INV-239 gains the completeness target if the band figure is to be binding
  rather than illustrative.
- `tests/` — the new arithmetic guard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Module 4's example quality gaps do not produce
  the quality band Module 4 asks for" (2026-08-17, Module Data collection, Priority High;
  `Source: self-observed (assistant retrospective)`)
- Priority: **High.** It defeats INV-239's stated purpose on the path where the plugin generates the
  data and therefore controls the outcome completely, and it does so silently: the guide sees a green
  `✅` three times, which is the specific bootcamper experience INV-239 was written to prevent.
- MCP re-check: n/a (no Senzing fact) — both the requirement and the formula are plugin-authored, and
  the arithmetic was recomputed locally rather than taken from the entry (the entry's 94.9% and this
  spec's 95.2% differ only in the `format_consistency` assumed; both are in the `≥80` band, which is
  the finding).
- Upstream: **not applicable.** Nothing here is Senzing behavior.
- Related specs: `specs/synthesized-scenarios-make-the-quality-gate-unreachable.md` (the spec that
  established INV-239 and this requirement), `specs/module5-quality-score-has-bands-but-no-formula.md`
  (established the composite formula this spec does the arithmetic on),
  `specs/completeness-denominator-has-two-readings-on-a-raw-source.md`,
  `specs/inv174-per-record-applicability-is-unverified.md`,
  `specs/quality-scoring-presence-test.md`,
  `specs/data-collection-generated-path-is-non-yielding-and-unmarked.md`.
