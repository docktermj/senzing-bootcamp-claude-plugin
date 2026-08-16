# Random sampling destroys the cross-source overlap entity resolution exists to find

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 4 offers sampling when a dataset exceeds the license limit and says nothing about *how* to
sample. The natural instinct — a random sample is representative — is correct for profiling and
**wrong for entity resolution**.

A random 300-record slice was drawn from each of five sources. The load was flawless: 1,147 records,
zero errors, redo drained, quality scores 94–100%. It produced **zero cross-source matches** outside
one pair that happened to be fully included. The KYC business problem returned no findings from a
technically perfect pipeline.

Measuring the full files showed the overlap was real but sparse — 507 shared names across
21,284 × 63,193 candidates for the largest pair. Random slices of large, mostly-disjoint sets share
essentially nothing.

**Every operational signal a bootcamper is taught to check was green.** Records loaded, no errors,
redo queue drained, quality scored well. The failure surfaces only in the cross-source matrix, and
only if someone thinks to compare it against what the business problem needed. A bootcamper who
trusted the load would conclude Senzing found nothing in their data.

## Root cause

**The right guidance exists in the plugin — in the wrong branch.**

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:546` (step 8b, the SQLite
load-time warning branch) already offers *"an entity-resolution-demonstrating strategy that preserves
cross-source overlaps and known match clusters"*. That is exactly the correct instruction.

But the **license-driven** path never mentions it:

- `:82` — "**Work with a smaller slice (optional):** sampling, a CORD subset, or a smaller substitute
  dataset" — strategy-free.
- `:358` — "Create smaller sample files (sampling, a CORD subset, or a smaller substitute dataset)."
- `:360` — "Document the sampling method (first N records, random sample, etc.)" — which names random
  sampling as an ordinary choice, with no warning attached.

So the two paths that reduce a dataset give opposite quality of advice, and the one a bootcamper
reaches first — the license gate at step 6 — silently takes the harmful default. Step 8b fires only
on load-time concerns, which a within-license-but-large dataset never triggers.

## Proposed change

1. **Move the overlap-preserving guidance to where sampling is first offered**, or cross-reference it
   from step 6 so a single edit cannot leave the two paths disagreeing again. Prefer stating it once
   and referencing it, since this defect *is* the two-copies-of-one-rule failure.
2. **State the rule plainly whenever a dataset is reduced for any reason and 2+ sources are present:**
   random selection removes the signal entity resolution exists to find. Make overlap-aware selection
   the default, not an alternative.
3. **Say what overlap-aware selection means concretely**, since "preserve overlaps" is not actionable
   on its own: identify candidate join keys (name, identifier) shared across sources, select records
   participating in those shared values first, then fill the remaining budget to reach the target
   size. Keep it language-agnostic — this is a selection strategy, not code.
4. **Require the sampling method to be recorded with its rationale** in the data-source registry, so
   Module 6's validation can interpret a low cross-source count against how the data was chosen
   rather than treating it as a finding about the data.
5. **Give Module 6 a way to recognize this.** Where post-load validation finds near-zero cross-source
   entities, the first question must be whether the load was sampled and how — a sampled-random load
   explains the result and is not evidence about the sources.

## Acceptance criteria

- [ ] Step 6's sampling offer states that random selection destroys cross-source overlap when 2+
      sources are present, and names overlap-aware selection as the default.
- [ ] The overlap-preserving guidance exists in exactly one place and is referenced from both the
      license-driven path and step 8b's load-time branch — editing one cannot leave them disagreeing.
- [ ] The guidance is concrete enough to act on (identify shared keys → select participating records →
      fill to budget), not just "preserve overlaps".
- [ ] The chosen sampling method and its rationale are recorded where later modules can read them.
- [ ] Module 6's validation treats near-zero cross-source entities as a question about the sampling
      method before treating it as a finding about the data.
- [ ] `:360`'s "random sample" example no longer appears as an unqualified option.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): this is
      selection guidance expressed in terms of shared keys, with no platform or language specifics.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — step 6's offer (`:82`), the
  smaller-slice guidance (`:358-360`), and step 8b (`:546`) as the single source of the strategy.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — read the recorded
  sampling method before interpreting a low cross-source count.
- `tests/` — assert the strategy text exists once, is referenced from both paths, and that the
  license-driven path names the random-sampling hazard.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Random sampling silently destroys cross-source
  overlap, producing a zero-finding load" (2026-07-28, Module Data collection;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`; `Upstream: not applicable`)
- Priority: High
- MCP re-check: n/a (no Senzing fact — the defect is guidance placement within the plugin; the
  measured overlap figures are the reporter's own observations of their data). Server 1.32.1,
  2026-07-28.
- Upstream: not applicable
- Related specs: `specs/module3-synthetic-verification-data.md` (the precedent for constructing data
  that demonstrates resolution rather than sampling it),
  `specs/post-load-match-key-semantic-audit.md` (INV-117 — the audit that surfaces the consequence),
  `specs/single-license-gate-at-data-processing.md` (INV-093 — the license gate that offers sampling)

## Deviations from this spec, and why (2026-07-28)

**A third harmful site the spec did not identify.** Alongside the strategy-free offers at `:82` and
`:358-360`, the smaller-slice guidance instructed *"Ensure the sample is representative of the full
dataset."* That is the harmful instinct stated as an instruction — a sample representative of each
source individually is exactly what contains no cross-source matches. It has been replaced with a
statement of what the *business problem* needs, and a test asserts the old sentence is gone. Fixing
only the two sites the spec named would have left the module still telling readers to do the wrong
thing.

**The rule got an anchor, and the other paths link to it.** The spec offered "move it into step 6, or
cross-reference it" and preferred stating it once. It is now a single anchored block
(`<a id="overlap-preserving-sampling"></a>`) in step 6 that declares itself canonical; the
smaller-slice path and Step 8b link to it, and Step 8b is told explicitly not to restate it. A test
counts the references, because this defect *was* two copies of one rule disagreeing — the failure mode
worth guarding structurally rather than by prose.

**Added: the single-source exemption.** The spec's rule is unconditional, which would over-apply it —
a one-source dataset has no cross-source overlap to preserve, and first-N or random is perfectly fine
there. The guidance says so and tells the reader to state which case applies rather than assume, so
the rule cannot become a ritual on datasets it does not concern.

**Module 6's check went into step 23, not the generic validation.** The spec said only that Module 6
should recognize a sampled load. It landed first in step 22 (single-source UAT) and was moved: a
single-source load has no cross-source count to misread, so the check belongs in step 23
("Validate cross-source results"), which is where a zero count is actually observed and which is
already conditional on 2+ sources. A test pins it between the step 23 and step 24 headings.

**Acceptance criteria status.** All met. Nothing required a live engine — the measured overlap figures
are the reporter's observations of their own data, cited as such rather than re-derived.
