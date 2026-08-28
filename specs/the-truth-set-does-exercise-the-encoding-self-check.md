# The API reference says the Truth Set cannot exercise the encoding self-check — it can, and does

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`visualization-api-reference.md:1095-1100` tells the implementer that the INV-270 encoding
self-check is unexercisable in the very module that builds the visualization app:

> ⚠️ **Fewer than two distinct keys means the check was NOT exercised — report that, never "passed"
> (INV-265).** With one registered data source every key is that source, the comparison cannot fail,
> and reporting a pass would be reporting agreement from a match that could not disagree. **This is
> not a corner case: it is the normal Truth Set situation, and it is exactly why the module that
> builds this app cannot catch the defect with its own data.** Say "not exercised — one data source"
> and move on.

**The premise is false.** The Truth Set has **three** registered data sources, not one, and it
produces cross-source entities in quantity. Measured this session against a real load of the
complete 159-record Truth Set (Senzing SDK 4.3.4, MCP server 1.33.0, 2026-08-27):

```text
distinct DATA_SOURCE values in truthset_data.jsonl:
  {'CUSTOMERS': 120, 'REFERENCE': 22, 'WATCHLIST': 17}

/api/stats  -> data_sources_total: 3,  cross_source_entities: 17

/api/graph encoding_check:
  status : ok
  detail : 7 distinct source-set keys, 4 of them combinations
  keys   : ['CUSTOMERS', 'CUSTOMERS|REFERENCE', 'CUSTOMERS|REFERENCE|WATCHLIST',
            'CUSTOMERS|WATCHLIST', 'REFERENCE', 'REFERENCE|WATCHLIST', 'WATCHLIST']
  combos : ['CUSTOMERS|REFERENCE', 'CUSTOMERS|REFERENCE|WATCHLIST',
            'CUSTOMERS|WATCHLIST', 'REFERENCE|WATCHLIST']
```

Seven distinct source-set keys, four of them genuine multi-source combinations, over 84 entities.
The comparison the check performs — *does the legend name as many keys as the graph emitted?* — is
therefore fully live on Truth Set data: first-source coloring would collapse those four
combination keys onto their first member and drop the legend count from 7 to 3, which is exactly
the mismatch INV-270 exists to catch.

**Why this is worth correcting rather than shrugging at.** The paragraph does not merely misstate a
fact; it tells the implementer to *stop looking*. Its closing instruction is literally *"Say 'not
exercised — one data source' and move on."* An implementer who trusts it will:

1. Report `not_exercised` on a run where the check **was** exercised — the false-negative twin of
   the "reporting agreement from a match that could not disagree" error the same paragraph is
   written to prevent. INV-265's rule is right; the situation it is attached to is wrong.
2. Conclude that the INV-259 first-source coloring defect cannot be caught here and must wait for
   Module 7's larger dataset — when this module's own data catches it cleanly. The defect INV-270
   was created for (recorded at `:1069` — "re-implemented wrong in a generated Java app on
   2026-08-25 — colored from `data_sources[0]`, with 294 of 5,619 cross-source entities rendered as
   single-source") would have been caught by the Truth Set, one module earlier than the run that
   actually found it.

That second point is the substantive cost: the guidance sends the one check that would have caught
a shipped defect to sleep in the module best placed to run it.

## Root cause

The paragraph appears to conflate two different things: the number of **data sources** in the Truth
Set (three) and the number of distinct **source-set keys** an implementation emits (seven, here).
The sentence "With one registered data source every key is that source" describes a real and
correct edge case — it is simply not the Truth Set's case. The "normal Truth Set situation" clause
looks like an assumption carried over from a scenario with a single loaded source (System
verification's synthetic `VERIFY` data is exactly that: one data source, four records) and then
attached to the Truth Set module by proximity.

Nothing else in the surrounding contract depends on the false premise — the check's definition,
its `status`/`detail` vocabulary, and the `not_exercised` rule at `:1095` are all correct as
written and need no change.

## Proposed change

1. **Correct the false premise at `visualization-api-reference.md:1097-1100`.** Keep the
   `not_exercised` rule exactly as it is — it is right, and INV-265 depends on it — but stop
   attributing that state to the Truth Set. Replace the "normal Truth Set situation" claim with
   what is actually true: the Truth Set carries three data sources and produces cross-source
   entities, so the check **is** exercised in this module and a real `ok`/mismatch verdict is
   expected here. Name the single-source case for what it is — System verification's synthetic
   `VERIFY` data, and any bootcamper who loads exactly one source — rather than as the norm.
2. **Say plainly that this module is a genuine test site for INV-259.** One sentence, because it
   reverses the reader's expectation: the coloring defect that INV-270 was written for is
   detectable on Truth Set data, so a `not_exercised` result *in this module* is itself a signal
   worth checking (it means fewer sources loaded than expected), not a routine outcome to move
   past.
3. **Do not weaken INV-265.** The rule "fewer than two distinct keys → report not exercised, never
   passed" stays exactly as written. Only the claim about which datasets land in that state changes.

## Acceptance criteria

- [ ] `visualization-api-reference.md` no longer states or implies that the Truth Set yields fewer
      than two distinct source-set keys, or that this module cannot catch the INV-259 defect with
      its own data.
- [ ] The `not_exercised` rule and its INV-265 citation are unchanged in substance; the
      single-source example names a dataset that actually is single-source (e.g. System
      verification's synthetic `VERIFY` records).
- [ ] A test asserts the corrected claim cannot silently regress — e.g. that the file does not
      contain the phrase "normal Truth Set situation" alongside the one-data-source assertion.
      Stdlib only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      correction is prose about data, not about any binding.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the paragraph at `:1095-1100`
- `tests/` — a guard for the corrected claim

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-27 (`Source: self-observed (assistant
  retrospective)`), while building the Java visualization server for the Truth Set visualization
  module and running the INV-270 self-check the contract requires. Found by **executing** the check
  the paragraph says cannot be executed; no amount of reading would have surfaced it, since the
  claim is self-consistent and plausible on its face.
- Priority: **Medium.** Nothing is broken and no bootcamper is blocked — but the guidance disables
  the one automated check standing between the INV-259 coloring defect and a shipped keepsake, in
  the module best positioned to run it, and that defect has already shipped once (`:1069`). Filed
  Medium rather than Low because the instruction is *actively* directing implementers away from a
  working check, not merely omitting a fact.
- MCP re-check: **server 1.33.0, 2026-08-27.** `get_sample_data(dataset='truthset', source='list')`
  called live this session and returned three sources — CUSTOMERS (120), REFERENCE (22), WATCHLIST
  (17), 159 total — which is the server-side half of the claim. The remaining evidence is a
  measurement on this machine (SDK 4.3.4): the loaded file's distinct `DATA_SOURCE` values, and the
  running server's own `/api/stats` and `/api/graph.encoding_check` output quoted above. Marked as
  observation where it is observation (INV-080/INV-149): the *seven keys* figure is a property of
  this load, while the *three data sources* fact is MCP-sourced. No absence claim is made, so
  `owner-checked:` does not apply.
- Upstream: not applicable — the incorrect claim is in this repo's own contract file, not in
  anything the Senzing MCP server returns.
- Related specs: `specs/a-check-that-matches-nothing-must-not-report-agreement.md` (INV-265, the
  rule this spec deliberately leaves intact — only the dataset it is attributed to is wrong);
  `specs/relationship-network-edge-color-and-legend-filter.md` and the INV-259 coloring lineage
  (the defect the self-check exists to catch, and which the Truth Set can in fact catch)

## Deviations from this spec, and why (2026-08-28)

**None on the diagnosis — re-verified live before anything was changed.**
`get_sample_data(dataset='truthset', source='list')` was re-called on server **1.33.0**, 2026-08-28
and still returns **three** sources: CUSTOMERS 120, REFERENCE 22, WATCHLIST 17, 159 records. The
spec's central claim holds.

⚠️ **The spec named ONE site. There were five.** This is the INV-246 hazard exactly — a spec
enumerates where its author *noticed* the defect, and an incomplete application of a rule is
precisely the case where that list is short. Found by sweeping rather than by reading the spec:

| # | Site | Named by the spec? |
|---|---|---|
| 1 | `visualization-api-reference.md:1095` — "the normal Truth Set situation" | yes |
| 2 | `phase1-visualization.md:296` — "the expected outcome whenever one data source is registered ... why this module cannot catch the defect with its own data" | **no** |
| 3 | `module-07/phase1-query-visualize.md:623` — "The Truth Set build almost always reports `not_exercised` — one data source" | **no** |
| 4 | `tests/test_encoding_self_check_is_stated_as_behavior.py` — docstring and two assertion messages calling it "the *normal* Truth Set situation" and "the Truth Set case" | **no** |
| 5 | `specs/INVARIANTS.md` — **INV-270's own text**: "The Truth Set structurally cannot provoke it" | **no** |

Site 3 is the most consequential of the unnamed ones: it told the reader that Module 7 is where the
check first has teeth, which is the belief the spec argues costs a module of early detection.

⛔ **Site 5 required correcting a registered invariant in place**, per the standing rule that an
invariant encoding a false premise is worse than a missing one. INV-270's **rule** is untouched —
expose the count, compare before capture, stop on mismatch, report not-exercised below two keys
(INV-265). Only its closing factual aside about which datasets can provoke the defect is withdrawn,
with a dated `(Corrected 2026-08-28 …)` note quoting what it previously said. ⚠️ **This is worth the
maintainer's eye on return**: correcting an invariant's text is a heavier action than the spec
anticipated, and it was taken unattended.

⛔ **Site 4 is the "test pinned the wrong premise" shape.** No assertion in that guard was wrong —
each requires a build site to *name* the not-exercised outcome, which is correct either way — but
the prose around them stated the false premise, and a guard's own docstring reads as reviewed. No
assertion was weakened; only the stated premise was corrected.

**The guard scans rather than lists.** `tests/test_truthset_is_not_called_single_source.py` matches
the claim across all shipped markdown plus `INVARIANTS.md`, because a guard naming the sites already
known would have certified site 1 and stayed blind to the four that mattered. It also asserts the
**true** claim is present, so deleting the false sentence without replacing it fails; and it asserts
a genuine single-source passage (System verification's `VERIFY`) is *not* flagged, so the matcher
cannot push an editor into deleting a true sentence.
