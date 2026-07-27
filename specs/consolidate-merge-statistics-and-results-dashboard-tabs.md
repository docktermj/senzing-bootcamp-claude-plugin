# Collapse the overlapping Merge Statistics and Results Dashboard tabs into one

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In the Truth Set visualization, the **Merge Statistics** and **Results Dashboard** tabs look similar
enough that the bootcamper asked to collapse them into a single tab named "Merge Statistics". Reason
given: "Fewer tabs makes it easier to navigate."

Separately, the line on Merge Statistics — "159 records collapsed into 84 entities, including 55
multi-record entities" — simply repeats the headline counts already shown in the summary strip above
it, so it can be removed.

## Root cause

The two tabs are backed by endpoints that overlap by construction, and the spec's own
de-duplication rule does not cover this pair.

1. **`/api/dashboard` is largely a superset of `/api/stats`.**
   `visualization-api-reference.md:247` states it plainly: "`counts` and `histogram` are drawn from
   **the same aggregates as `/api/stats`**; `sample_entities` is the multi-record entities in
   descending record-count order". So the only content unique to Results Dashboard is
   `sample_entities` — a top-10 list of the largest entities.
2. **Both tabs are then specified to render the histogram.**
   `visualization-api-reference.md:319` — Merge Statistics: "records-per-entity histogram; this **is**
   the entity-size distribution (clickable bars drill down via `bucket_entities`…)".
   `visualization-api-reference.md:231-232, 323` — Results Dashboard: "headline counts, **the
   records-per-entity histogram**, and a sample of the largest resolved entities".
   The same histogram is specified twice, in two tabs, from two endpoints.
3. **The de-duplication rule misses this pair.** `visualization-api-reference.md:326-330` forbids
   redundant tabs, but names only two collisions — entity-size distribution → Merge Statistics, and
   the cross-source relationship view → Entity Graph. It never addresses Merge Statistics vs. Results
   Dashboard, so an implementer following the tab table literally builds both.
4. **The redundant summary sentence is specified.** `phase1-visualization.md:243-245` requires Merge
   Statistics to render the histogram "**with a summary sentence**" — the exact line the bootcamper
   asked to remove, alongside a page-level summary strip that already carries those counts.

## Proposed change

1. **Merge the two tabs into one, named "Merge Statistics".** It carries: the records-per-entity
   histogram with the existing clickable `bucket_entities` drill-down, plus the largest-resolved-
   entities sample that was Results Dashboard's only unique content — rendered with the canonical
   per-entity action set (see `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md`), since
   `sample_entities` already carries `entity_id`.
2. **Remove the Results Dashboard tab** from the tab table (`visualization-api-reference.md:323`) and
   from `phase1-visualization.md`'s tab list. Keep `/api/dashboard` **or** fold `sample_entities` into
   `/api/stats` — the implementer's choice, but the contract must state which, so snapshot embedding
   (`visualization-api-reference.md:337-343`, which currently embeds both `stats` and `dashboard`)
   stays coherent and no endpoint is left specified-but-unused.
3. **Drop the redundant summary sentence.** Headline counts live in the page-level summary strip once.
   Amend `phase1-visualization.md:243-245` to remove the per-tab "summary sentence" requirement.
4. **Extend the de-duplication rule** at `visualization-api-reference.md:326-330` to state the general
   principle rather than only this instance: *a tab MUST NOT be added whose content is derivable from
   another tab's endpoint; when two candidate tabs share their aggregates, they are one tab.* This is
   what stops the next such pair — the rule already exists but enumerates cases instead of stating the
   test.

Note on prior work: this pair was created deliberately. `specs/consolidate-module7-visualizations-as-
truthset-app-tabs.md` folded Module 7's standalone `results_dashboard.html` into the app **as** the
Results Dashboard tab, which was the right move for that page but landed it next to a tab already
showing the same histogram. Collapsing them completes that consolidation rather than reversing it —
the content is retained; only the second tab goes away.

Cross-check when implementing: `specs/consolidate-results-dashboard-offer-in-module7.md` and the
Module 6 → Module 7 deferral at `skills/module-06-data-processing/phaseD-validation.md:128` both refer
to a "results dashboard" as a bootcamper-facing offer. Confirm no bootcamper-facing text promises a
tab by that name; if it does, update the wording rather than keeping the tab.

## Acceptance criteria

- [ ] The tab table lists one tab (**Merge Statistics**) covering the histogram, its
      `bucket_entities` drill-down, and the largest-entities sample; **Results Dashboard** is gone.
- [ ] The contract states explicitly whether `/api/dashboard` is retained or its `sample_entities` is
      folded into `/api/stats`, and the snapshot-embedding list (`visualization-api-reference.md`
      ~337-343) matches that decision with no orphaned endpoint.
- [ ] Entities in the largest-entities sample carry the canonical per-entity action set.
- [ ] The per-tab "summary sentence" requirement is removed from `phase1-visualization.md`; headline
      counts appear once, in the page summary strip.
- [ ] The de-duplication rule states the general "derivable from another tab's endpoint" test, not
      only an enumeration of known collisions.
- [ ] No bootcamper-facing text in Module 6 or Module 7 promises a "Results Dashboard" tab that no
      longer exists.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): a spec/tab
      change with no dependency on the Java or Python reference build; the standalone snapshot still
      renders every retained tab offline (INV-070).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  tab table (lines ~314-324), `/api/dashboard` (lines ~231-249), de-duplication rule (lines ~326-330),
  snapshot-degradation list (lines ~337-343)
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — tab
  list (lines ~229-250), including the "with a summary sentence" clause
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  line ~208 enumerates the tabs the Module 7 build must serve; drop Results Dashboard
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — the reference implementation's tab set
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — line ~128, if it
  names the tab

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_12.md` → "Merge Statistics and Results Dashboard tabs
  overlap; redundant summary line" (2026-07-23, Truth Set visualization)
- Priority: Medium
- Related specs: `specs/consolidate-module7-visualizations-as-truthset-app-tabs.md` (created the
  Results Dashboard tab), `specs/consolidate-results-dashboard-offer-in-module7.md`,
  `specs/truthset-viz-entity-actions-and-aggregate-drilldowns.md` (the action set the merged tab uses)
