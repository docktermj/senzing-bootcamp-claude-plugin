# The count-mismatch rule files a clean load as `failed` whenever the mapping multiplies records

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`phaseB-load-first-source.md:92-101` states, as a ⛔ rule:

> **If the two disagree, write the discrepancy rather than the count** (INV-245): leave the existing
> `record_count` in place, set `load_status` to `failed`, record **both** figures in the `issues`
> entry, and do not present the loaded count as a result.

`PPP_LOANS` loaded **3,727** records against a source `record_count` of **3,488**. The two disagree.
The disagreement is fully explained and documented: the mapper emits 239 distinct lenders as
embedded masters, exactly as the source's own mapping specification prescribes. Every input record
loaded and there were **zero errors**.

The only compliant action was to file a completely successful load as `failed`.

## Root cause

**The rule tests for equality and the mapping the bootcamp teaches breaks equality by design.**

`embedded_master` is not an edge case the rule failed to anticipate — it is a disposition Module 5
teaches explicitly, under its own ⛔ heading at
`module-05-data-quality-mapping/phase2-data-mapping.md:236`, *"A second entity hiding in a column:
`embedded_master`, and when to go `back`"*, and defined at `:240` as: *"the value becomes its own
Senzing record, and the parent points at it."* A disposition whose definition is "emit an additional
record" **necessarily** makes the loaded count exceed the input count. The bootcamp teaches the
pattern in Module 5 and then, in Module 6, treats its arithmetic signature as a load failure.

**The remedy over-fires in the mirror direction of the fault it was written for.** The rule's stated
rationale is sound — overwriting on a mismatch *"destroys the input baseline and files a partial load
as a complete one"*. But `failed` is not the only alternative to overwriting. As written it also
files a **complete** load as a **failed** one, and the damage propagates identically: `phaseC` step
12 reads `load_status` straight back out and presents it, and Phase D writes it into
`docs/loading_strategy.md` — which the step's own paragraph says is why the figure matters.

**INV-245 does not require this.** Its condition is that *"a value that failed its own verification
check MUST NOT be presented to the Bootcamper as a result; the discrepancy is reported in its
place."* A delta the mapping specification predicts has **not failed** its verification — it is
verified and reconciled, which is a different outcome from unverified. The step collapses three
states (equal / explained delta / unexplained delta) into two, and INV-245 governs only the third.
So this is fixable **within** INV-245 and INV-243 rather than against them; no invariant needs
amending, which is what makes it worth doing carefully.

## Proposed change

1. **Split the mismatch branch three ways** at `phaseB-load-first-source.md:92`:
   - **equal** → `load_status: loaded`, as now;
   - **delta explained by the source's own mapping specification** — a record-multiplying
     disposition (`embedded_master`) or a documented denormalizing fold — → `load_status: loaded`,
     with **both** figures retained, a `load_reconciliation` note naming the disposition and the
     document that predicts it, and the `validation_checks` entry recorded as `expected_delta`
     rather than pass/fail;
   - **unexplained delta** → `failed`, exactly as the rule stands today.
2. ⛔ **Require the explanation to be sourced, never asserted.** The branch is only reachable when a
   named mapping artifact predicts the delta — the source's mapping specification, the mapping
   disposition recorded in the registry — and the note must cite it. Otherwise this becomes a
   universal escape hatch and the rule protects nothing: "the mapping probably explains it" is the
   failure INV-245 exists to prevent, wearing the new branch as a disguise.
3. **Keep the baseline immutable in all three branches.** The existing `record_count` is never
   overwritten (INV-243); the loaded figure is recorded beside it. That half of the rule is correct
   and is not what is being changed.
4. **Carry the third state downstream.** `phaseC` step 12 and Phase D's
   `docs/loading_strategy.md` must render an `expected_delta` as a reconciled result with its
   explanation, not as a bare pass — a load that legitimately changed the record count is worth
   showing the Bootcamper, since it is the visible consequence of a mapping decision they made.

## Acceptance criteria

- [ ] A load whose delta is predicted by the source's mapping specification records
      `load_status: loaded`, both figures, a `load_reconciliation` note citing the predicting
      document, and `expected_delta` in `validation_checks`.
- [ ] A load with an **undocumented** delta still records `failed` with both figures — the original
      rule intact, negative-controlled so the new branch cannot be reached without a cited source.
- [ ] The input `record_count` baseline is unchanged in every branch (INV-243).
- [ ] `phaseC` step 12 and Phase D present the reconciled third state distinguishably from a plain
      pass, and never as a failure.
- [ ] A test covers the `embedded_master` case end to end, using a source whose mapping document
      declares the disposition — the case that produced this report.
- [ ] The change is stated as behavior, not as a Python helper, so any implementation language
      satisfies it (INV-002).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — the ⛔
  rule at `:92-101` and the registry-write instruction at `:79-90`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — step 12's
  read-back and presentation of `load_status`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — the
  `docs/loading_strategy.md` write.
- `tests/` — the three-way branch, with the unexplained case negative-controlled.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Count-mismatch rule would file a successful load as failed" (2026-08-16, Module Data processing; `Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** It cannot corrupt data, but it puts a false `failed` into durable state on any source whose mapping multiplies records, and the bootcamp actively teaches the mapping that does so — it is reachable by design rather than by accident. A Bootcamper reading their own loading strategy is told a clean load failed.
- MCP re-check: **n/a (no Senzing fact).** The rule is entirely the plugin's own — a comparison between two figures the plugin itself records. No SDK method, flag, response shape or server behavior is asserted, and no absence about the server is relied on. Server **1.32.9** (`get_capabilities`, 2026-08-16) recorded for this run.
- Upstream: not applicable — routed `plugin`.
- Related specs: `specs/inv243-reconciliation-binds-more-sites-than-it-reaches.md` (the reconciliation discipline this extends), `specs/per-source-figures-are-reconciled` guard territory, `specs/orchestrator-per-source-stats-vs-static-scaffold-counters.md` (the same registry figures downstream), and INV-243, INV-245, INV-002.

## One correction to the feedback entry

The entry argues the concept already exists — *"a legitimate denormalizing fold reduces the count and
is fine" appears in Phase A's coverage note, so the concept exists; it just is not carried into this
rule.* **It does not appear.** Searched across `module-06-data-processing/` for `fold`, `denormaliz`,
`legitimate`, `expected delta`, `explained by` and `may differ`: the only `fold` hits in the shipped
plugin are Module 7's record-key fold for counting (`phase1-query-visualize.md:223-238`) and the
unrelated recap-checkpoint fold in `module-completion.md`/`graduation`. Module 6 contains no
statement anywhere that a count may legitimately differ.

This makes the fix **larger** than the entry assumes: the third state has to be introduced, not
carried across from a neighboring paragraph. Recorded so implementation does not go looking for a
precedent to copy and quietly conclude the rule is already half-written.
