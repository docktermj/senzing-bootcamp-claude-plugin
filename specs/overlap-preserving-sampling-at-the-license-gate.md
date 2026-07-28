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
reaches first — the licence gate at step 6 — silently takes the harmful default. Step 8b fires only
on load-time concerns, which a within-licence-but-large dataset never triggers.

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
  `specs/single-license-gate-at-data-processing.md` (INV-093 — the licence gate that offers sampling)
