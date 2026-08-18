# Step 3b's Poor band offers the Module 5 remap loop before anything establishes a mapping-actionable cause

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Step 3b bands the possible-match rate into Acceptable (<5%), Marginal (5-15%) and Poor (>15%), and
routes Poor to *"The results suggest mapping improvements would help"* plus the Module 5 feedback
loop.

A run measured **48.9%** of entities carrying a `POSSIBLY_SAME` relation. The sampled evidence the
same step now requires showed the cause was **not** a mapping defect: roughly half the near-misses
came from one source's genuinely empty contact fields (PHONE 45.7% populated, ADDRESS_LINE1 55% —
correctly mapped, the values simply absent from the source file), and the rest from coincidental
full-name collisions in the synthetic generator's limited name pool. Neither is fixable by remapping.

The band was followed anyway. The loop was offered, the bootcamper accepted, and the remap had
nothing to change — same source file, same already-correct field mappings. It took an extra
confirmation to establish that re-running `mapping_workflow` would reproduce the identical mapping,
and to get back to Module 7.

## Root cause

### The gate acts on the rate, and the shipped wording presupposes the diagnosis

`module-07-query-visualize-discover/phase1-query-visualize.md:360-363` sets the bands, and `:379-381`
is the Poor branch:

> - **Poor:** "The results suggest mapping improvements would help." (Show the entities or
>   possible-match pairs that demonstrate it — naming the match key pattern the near-misses share,
>   **since that is what points at the unmapped feature** — then give recommendations and offer the
>   Module 5 feedback loop.)

The branch does not ask whether there **is** an unmapped feature; it says the shared match-key
pattern *is* what points at one. So the evidence is gathered and then narrated toward a conclusion
the band already reached. Nothing in the step lets the evidence cancel the loop offer, and `:385-399`
follows unconditionally with the pinned 👉 question and the Module 5 hand-off.

⚠️ **This is not the defect `step3b-quality-lookup-misroutes-and-omits-the-evidence-requirement`
fixed, and that spec said so.** That spec added the sample-and-show requirement to every branch and
explicitly left the thresholds alone: *"The quality **thresholds** are unchanged (`< 5%`, `5–15%`,
`> 15%`) — this spec changes what the guide must show, not where the bands sit."* The evidence is now
collected. What is still missing is that it **decides**: a band alone remains sufficient to route a
bootcamper into a remap.

### The server states the mapping diagnosis conditionally, and names a second cause the plugin drops

`reporting_guide(topic='evaluation', language='python')`, **server 1.32.9, verified 2026-08-17** —
the same call step 3b already makes at `:311-313`. Its 4-Point framework, verbatim:

> **UNDER-MATCHING:** Check the possible match (POSSIBLY_SAME) queue. Review sample pairs from the
> queue. For each pair, SHOW THE EVIDENCE — what features matched and what was missing that prevented
> full resolution. **If many near-misses are concentrated on one match key pattern, this likely
> indicates a mapping issue** (e.g., phone numbers not mapped).

and its evaluation anti-pattern:

> Under-matching is as important as over-matching. Always check the POSSIBLY_SAME queue — if many
> near-misses share the same match key pattern, a feature is likely **unmapped or has data quality
> issues**. Possible matches are the primary signal for under-matching.

Three differences from what the plugin ships, all in the direction of this finding:

1. **The server conditions the diagnosis on concentration**, not on the rate. "If many near-misses
   are concentrated on one match key pattern" is a test to run; `> 15%` is not.
2. **The server hedges** — "**likely** indicates" — where the plugin asserts.
3. **The server names two causes and the plugin carries one.** "Unmapped **or has data quality
   issues**" is precisely the run's actual finding (a correctly-mapped field whose values are absent
   in the source), and the branch that would have recognized it is the half the plugin dropped.

The server also supplies the discriminator. Its **SANITY CHECK** step says to compare the rates
against "source profiler uniqueness stats from the data profiling step" — *"If profiler showed 30%
duplicate names but compression is only 2%, likely under-matching"* — which is exactly what separates
"this dataset genuinely contains many similar people" from "a feature is not reaching the engine".
Step 3b never makes that comparison.

### The plugin already has the right shape for this, one module earlier

`module-06-data-processing/phaseD-validation.md:351-356` guards the identical hazard on the
match-key audit:

> **Report a high-share cross-source suppressor as a FINDING, never a pass/fail.** … ⛔ This must not
> become an automatic gate: a suppressor is often entirely legitimate (two records really do
> disagree), and a hard failure here would produce false alarms and train bootcampers to dismiss the
> signal — which would cost more than the check gains.

and `:356-358` makes it three outcomes, "not two — finding, no finding, and could-not-measure". Step
3b's Poor branch has no equivalent caveat, even though the possible-match rate is **more** strongly
driven by characteristics the mapping cannot change: per-field populated share in the source, name
commonality, and dataset size. On the generated-scenario path the plugin creates those characteristics
itself — INV-239 requires a source gapped into the 70-79% band, and gapped contact fields are the
first thing that produces near-misses no remap can fix.

**Why the suite could not catch it.** The Poor branch is well-formed prose that follows its own band
correctly; the defect is that the band is treated as sufficient, which no offline check has a reason
to question.

## Proposed change

1. **Relay the server's conditional form in place of the plugin's assertion.** Replace *"since that is
   what points at the unmapped feature"* with the test the server states: are the near-misses
   **concentrated on one match key pattern**? Quote the "likely indicates a mapping issue" hedge and
   the "unmapped **or has data quality issues**" pair, attributed to
   `reporting_guide(topic='evaluation', language=…)` with server version and date, rather than the
   plugin asserting either.
2. **Give the Poor band three outcomes, matching `phaseD-validation.md`'s pattern.** A high rate is a
   **finding**, and only one of its outcomes reaches Module 5:
   - **mapping-actionable** — near-misses concentrated on one match-key pattern that a mapping change
     would affect → report it and offer the loop, as today;
   - **not mapping-actionable** — the cause is a data characteristic → report it as a finding, say
     plainly that remapping would not change it, and continue to 3c;
   - **could not determine** — say so, and continue to 3c rather than guessing in either direction.
3. **Name the two common non-actionable causes so they are recognized rather than rediscovered.**
   Source field sparsity (a correctly-mapped field whose values are absent — check the **populated
   share per field**, which Module 5 already measured as `completeness`, so route to that figure
   instead of inventing a measurement) and name-only collisions in small or synthetic datasets
   (limited name pools; on a generated scenario the plugin built the pool).
4. **Add the server's sanity-check comparison.** Compare the possible-match rate against the
   profiler's uniqueness statistics from the mapping step before diagnosing, because that is the
   baseline the server names and the plugin has the numbers for.
5. **Make the loop offer conditional, and keep the turn well-formed.** A band alone must not be
   sufficient to reach the 👉 question at `:389`. On the non-actionable and
   could-not-determine outcomes, step 3b states the finding and continues into **3c**, whose pinned
   visualization offer at `:426` closes the turn — the same path the Acceptable branch already takes,
   and consistent with the ⛔ at `:304-307` that carries the turn to "the next 👉". ⛔ Do not create
   a branch that must ask a question it has none for: that is the unsatisfiable-instruction class
   `module5-quality-gate-demands-a-question-its-best-branch-lacks` records.
6. **Record the finding where it survives.** A non-actionable Poor outcome is a real result about the
   bootcamper's data and belongs in the module recap, so the evaluation is not silently discarded just
   because it did not route anywhere.
7. **Leave the thresholds alone.** `< 5%` / `5-15%` / `> 15%` still decide *whether to look hard*;
   this spec changes only what may follow from looking.

**Re-verify before implementing (INV-080).** Re-call `reporting_guide(topic='evaluation', language=…)`
and quote what it returns then. If the conditional wording or the second cause has changed, relay the
current text.

## Acceptance criteria

- [ ] Step 3b's Poor branch no longer asserts that a shared match-key pattern points at an unmapped
      feature; it relays the server's conditional wording with tool, parameters, server version and
      date.
- [ ] The Poor band has three named outcomes, and the Module 5 loop's 👉 question is reachable only
      from the mapping-actionable one.
- [ ] Source field sparsity and name-only collisions are named as non-actionable causes, with the
      sparsity check routed to Module 5's per-source completeness rather than restated.
- [ ] The profiler-uniqueness sanity comparison is prescribed before the diagnosis, attributed to the
      server.
- [ ] Every Poor outcome ends its turn on exactly one 👉 question and none has to invent one: the
      non-actionable and could-not-determine outcomes continue into 3c and close on the pinned
      visualization offer.
- [ ] A non-actionable Poor finding reaches the module recap.
- [ ] The three thresholds are byte-identical to today. Confirm by `git diff`.
- [ ] A test asserts that the Poor branch requires a mapping-actionable cause before the loop
      question, that both non-actionable causes are named, and that no Poor outcome lacks a closing
      question — negative-controlled by restoring the unconditional offer and confirming the mutation
      lands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the change
      is prose plus a `reporting_guide` call that carries the bootcamper's chosen language.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the Poor branch (`:379-381`), the Module 5 feedback-loop block (`:383-399`), and the quality-summary
  table's interpretation column (`:353-357`) where the sanity comparison belongs.
- `tests/` — the new guard; check `tests/test_quality_verdict_needs_evidence.py` still passes, since it
  guards the sibling requirement on the same branch.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Module 7's possible-match bands can route a
  bootcamper into a remap with nothing to fix" (2026-08-17, Module Query, Visualize and Discover,
  Priority High; `Source: self-observed (assistant retrospective)`)
- Priority: **High.** It is a documented route into wasted work at the very end of the bootcamp, and
  it tells a bootcamper their mapping needs improvement while the evidence in front of them says
  otherwise — which is the "train bootcampers to dismiss the signal" cost the plugin already refuses
  to pay one module earlier.
- MCP re-check: **server 1.32.9, 2026-08-17 — the server is correct and more careful than the plugin;
  the plugin is the stale party.** Tools called: `get_capabilities` (server version);
  `reporting_guide(topic='evaluation', language='python')` → the 4-Point framework's UNDER-MATCHING
  step ("If many near-misses are concentrated on one match key pattern, this **likely** indicates a
  mapping issue"), its SANITY CHECK profiler comparison, and the anti-pattern naming "unmapped **or
  has data quality issues**".
- Upstream: **not applicable.** The defect is in plugin-authored banding, and the server already says
  the more careful thing.
- Related specs: `specs/step3b-quality-lookup-misroutes-and-omits-the-evidence-requirement.md` (added
  the evidence requirement to these branches and deliberately left the thresholds and the routing
  alone), `specs/post-load-match-key-semantic-audit.md` (established the finding-not-gate pattern this
  spec borrows), `specs/module5-quality-gate-demands-a-question-its-best-branch-lacks.md` (the
  unsatisfiable-question class item 5 must avoid),
  `specs/synthesized-scenarios-make-the-quality-gate-unreachable.md` (INV-239, which manufactures the
  sparsity that produces non-actionable near-misses),
  `specs/verification-grades-the-engine-against-the-guides-own-prediction.md`.
