# The match-key audit pools per-record and relationship suppressors, which mean opposite things

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The match-key audit reads match keys from **two** places and prescribes **one** axis of separation.

Step 1 is explicit that there are two reads:

| What | Where |
|---|---|
| Per-record match keys | `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` |
| Relationship match keys | `RELATED_ENTITIES[].MATCH_KEY` |

Step 2 then says:

> Count the features appearing with a leading `-`, ranked by frequency, and **separate
> single-source from cross-source** comparisons — the cross-source ones are where a mapping
> disagreement between two sources shows up.

Single-versus-cross-source is the only split named. Nothing tells the guide to keep the two *reads*
apart when tabulating — and a suppressor means the **opposite thing** in each:

- **`-FEATURE` on a per-record key** — the records merged into one entity **despite** that feature
  disagreeing. That is the over-merge signal, and the mapping concern the audit exists to surface.
- **`-FEATURE` on a relationship key** — Senzing **declined to merge** those entities *because* the
  feature disagreed, and recorded a relationship instead. That is the engine exercising restraint,
  and on ambiguous data it is the correct outcome, not a defect.

Pooled into one "cross-source suppressor share", a large number cannot be read either way.

**Observed live, 2026-09-02, Senzing SDK 4.4.0, 10,000 records across three sources.** Pooled, the
audit reported:

```
suppressors, CROSS-source:  -DOB  1,758   19.5% of cross-source+relationship comparisons
```

Split, the same data reports:

```
suppressors on PER-RECORD keys, cross-source
  (records that merged DESPITE the feature disagreeing):   (none)
suppressors on RELATIONSHIP keys
  (entities Senzing DECLINED to merge because it disagreed):
  -DOB  1,758   57.4% of 3,061 relationship comparisons
```

**Zero** per-record suppressors and **57.4%** of relationships declined on a DOB conflict. Those are
two different findings, and the pooled 19.5% is neither of them.

⛔ **The consequence reached the Bootcamper.** On the pooled number this run reported match accuracy
as poor, took the gate's `UAT <80%` branch, and recommended *"going back to Data Quality, Mapping,
and Transformation to refine the mapping"*. On the split numbers the correct branch is
`UAT ≥90% and match accuracy ≥90%` — *"Results look strong."* — with the audit finding named
alongside it. **The gate routed to the wrong branch, and the recommendation was the opposite of
correct.** A spot-check of ten merged entities, read from `RECORDS[]` only, came back **10 of 10
clean** (`+EXACTLY_SAME`, `+NAME+DOB+ADDRESS+PHONE+EMAIL`).

## Root cause

`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md`, the match-key
audit, step 2. The step's framing leans toward the suppression case — *"Senzing is then told a
conflict exists where none does, and it **suppresses legitimate merges**"* — so relationship keys
clearly belong in the signal. What is missing is the recognition that per-record suppressors are a
**second, opposite** signal that the same tabulation swallows.

Step 4's remedy inherits the ambiguity: *"If one feature is detracting on a large share of
cross-source comparisons, ask the bootcamper to check whether the two sources' fields for that
feature genuinely measure the same thing."* That is the right question for a **per-record**
suppressor. For a **relationship** suppressor the useful question is different: *why were these
pairs raised as candidates at all* — i.e. which feature is doing the matching (here `EMAIL` and
`SURNAME`) and whether it is as distinguishing as the mapping assumes.

⚠️ **This is not a defect in the audit's existence — the audit worked.** It surfaced a real property
of the data that no aggregate percentage showed. The defect is that its output cannot be acted on
without the split, and the gate it feeds routes on the pooled figure.

## Proposed change

1. **Tabulate three buckets, not two:** single-source per-record, cross-source per-record, and
   relationship. Report each with its own denominator — a relationship share against relationship
   comparisons, a per-record share against per-record comparisons. Mixed denominators are how
   57.4% became 19.5%.
2. **Label what each bucket means at the point of output**, in one clause each: per-record =
   merged despite disagreement; relationship = declined to merge because of disagreement.
3. **Give step 4 two questions, matched to the bucket.** Per-record → do the two sources' fields for
   that feature measure the same thing? Relationship → which feature raised these pairs as
   candidates, and is it distinguishing enough to be doing that work?
4. **Make the gate route on the per-record bucket**, not the pooled figure. A high relationship
   suppressor share is worth reporting and is **not** evidence of poor match accuracy; a non-zero
   cross-source per-record suppressor share is.
5. Keep step 3's plumbing-failure rule as it is — it worked, and it applies to the relationship
   bucket unchanged.

## Acceptance criteria

- [ ] The audit reports single-source per-record, cross-source per-record, and relationship
      suppressors as three separate tabulations, each with its own denominator.
- [ ] Each bucket's output states whether the feature disagreed on records that **merged** or on
      entities that were **not merged**.
- [ ] Step 4 carries a bucket-appropriate question for each, and the per-record question keeps the
      current "do the fields measure the same thing" wording.
- [ ] The iterate-vs-proceed gate routes match accuracy on the per-record bucket; a relationship
      suppressor share cannot by itself push the gate below the ≥90% branch.
- [ ] A test fixture with zero per-record suppressors and a high relationship suppressor share
      routes to "Results look strong" **and** still reports the relationship finding.
- [ ] Negative control: pool the buckets again and confirm that fixture routes to the `<80%` branch,
      reproducing this defect.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — three buckets, per-bucket labels and questions, gate routing
- `tests/` — fixture for the zero-per-record / high-relationship case

## Source

- Feedback: `/dry-run` phase 3, 2026-09-02, Data processing Phase D match-key audit and the iterate-vs-proceed gate (`Source: self-observed (assistant retrospective)`)
- Priority: **High** — the pooled figure routed the gate to the wrong branch and produced a recommendation opposite to the evidence, on data where the engine was behaving correctly. It fails in the direction that costs the Bootcamper work: it sends them back to re-map a mapping that was not the problem.
- MCP re-check: **server 1.36.0, 2026-09-02.** `get_sdk_reference(topic='flags', filter='why_records', language='java')` and `filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS'` confirm the two reads live at different response paths — `RESOLVED_ENTITY.RECORDS[]` versus `RELATED_ENTITIES[]` — and that `SZ_ENTITY_DEFAULT_FLAGS`' `response_paths` cover both. The semantic asymmetry (merged-despite versus declined-because) is a property of what a relationship *is* and is not a Senzing fact requiring a route; the counts are environment observations on SDK 4.4.0 (build 4.4.0.26242).
- Upstream: not applicable — no server defect; the plugin's tabulation is what conflates the two.
- Related specs: `specs/proceed-on-sqlite-keeps-the-tier-s-thread-count.md` (same module, unrelated cause)


## Deviations from this spec, and why (2026-09-02)

1. **The asymmetry IS a documented Senzing fact — the spec said it was not, and the
   implementation cites the server instead.** This spec's `MCP re-check` line claimed the
   merged-versus-not distinction "is a property of what a relationship *is* and is not a Senzing
   fact requiring a route". Re-verification found the server states it directly:
   `get_sdk_reference(topic='response_schemas', filter='get_entity_by_entity_id',
   language='java')` on server **1.36.0, 2026-09-02** documents `RELATED_ENTITIES[]` as
   *"Entities related to but **not resolved into** this one"*, and gives the two `MATCH_KEY`
   paths **different** descriptions — `RESOLVED_ENTITY.RECORDS[].MATCH_KEY` is *"Features that
   matched: + means contributed, - means detracted"* while `RELATED_ENTITIES[].MATCH_KEY` is only
   *"Features that matched/did not match"*. The shipped text now cites those rather than
   asserting the distinction, which is strictly stronger than what the spec asked for.

2. **A second shipped site was changed, which this spec did not name (INV-246).** The sweep
   required before recording found `module-07-query-visualize-discover/phase1-query-visualize.md`
   quoting step 4's heading **verbatim** — *"Report a high-share cross-source suppressor as a
   FINDING, never a pass/fail"* — which the bucket split changed, leaving a dangling citation.
   That file's data-discoveries instruction (`:903`) was also amended to carry the **bucket**
   forward into the keepsake, since a share recorded without its bucket cannot be acted on later.
   The guard derives its site set by scanning shipped markdown rather than listing paths, so the
   next such cross-reference is caught rather than re-derived.

3. **No new invariant: this closes an INV-264 violation rather than establishing a rule.** The
   spec did not predict either way. INV-264 already requires that a band or share MUST NOT by
   itself route the Bootcamper into remediation, and already names
   `module-06-data-processing/phaseD-validation.md` as one of its three sites — satisfied there by
   "a high-share cross-source suppressor is reported as a **FINDING**, never a pass/fail". The
   defect was that the site honored it at the **report** and the gate one step later still routed
   on the pooled number, remediating anyway. All four hard-rule lines now cite INV-264 at their
   own line (INV-183).

4. **An existing test was narrowed, not merely added to.**
   `tests/test_related_entities_guidance.py::test_phase_d_stays_correctly_scoped` asserted
   `assertNotIn("SZ_INCLUDE_MATCH_KEY_DETAILS")` on Phase D. That is broader than its own class's
   stated rule — which is that the flag must not be **grouped with the relations flags as omitting
   the export methods** — and the blunt form held only while Phase D happened not to mention the
   flag at all. It is named freely in five other shipped files. Phase D now cites it correctly
   (`MATCH_KEY_DETAILS` `requires_flags` it; it `depends_on` a relations flag), so the assertion
   was narrowed to the grouped form, mirroring the precise regex its sibling test already uses for
   the viz reference.

## Invariants introduced

None. The implementation closes a gap in **INV-264**'s coverage rather than establishing a new
rule; all four hard-rule lines it ships cite that invariant at their line.
