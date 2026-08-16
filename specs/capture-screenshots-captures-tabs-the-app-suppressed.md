# Capture consults the pane, not the app's own applicability rule, so it screenshots tabs the bootcamper never saw

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The visualization app deliberately hides a tab when its data does not exist. Capture does not
ask, so it activates the hidden tab's pane anyway, writes a near-empty PNG under a confident
slug, and records it in the manifest as successfully captured.

Reproduced live on 2026-08-14 against a real engine (Senzing 4.3.4), 4 records in a single
data source `VERIFY` resolving to 2 entities, 1 multi-record:

```console
$ python3 capture_screenshots.py --html snap.html --name dryrun --out-dir shots
dryrun-entity-graph.png       Entity Graph
dryrun-merge-statistics.png   Merge Statistics
dryrun-match-keys.png         Match Keys
dryrun-feature-scores.png     Feature Scores
dryrun-cross-source.png       Cross-Source      <-- the app renders no such tab
dryrun-search-probe.png       Search / Probe
```

The rendered page has **five** nav buttons; Cross-Source is not among them. The manifest
nonetheless reports full coverage:

```json
"captured_count": 6, "requested_count": 6, "not_present": [], "failed": []
```

`dryrun-cross-source.png` (37 KB) is the page chrome, the funnel, and two lines of
explanatory text — *"Cross-source overlap needs at least two data sources."* — above roughly
700 px of empty background. It goes into the graduation recap PDF captioned "Cross-Source".

## Root cause

Two different notions of "this tab exists", and capture uses the weaker one.

- **The app's authority** is `tabApplicable(id)`, a global function in the page
  (`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:809-816`), whose own comment says
  *"A tab is shown only when its data exists"*:

  ```js
  function tabApplicable(id){const s=STATS||{};
    if(id==="overlap")return (s.data_sources_total||0)>=2;
    if(id==="features")return (s.multi_record_entities||0)>0;
    if(id==="matchkeys")return (s.multi_record_entities||0)>0;
    return true;}
  ```

  It gates the **nav button**. It gates **three** tabs, not one.

- **The pane is emitted unconditionally** — `senzing_viz_server.py:777`,
  `<section class="tab" id="tab-overlap">…` — so `tab-overlap` is in the DOM whether or not
  the tab is shown.

- **Capture's presence check is the pane** —
  `plugins/senzing-bootcamp/scripts/capture_screenshots.py:189`:

  ```js
  if (typeof activate === "function" && document.getElementById("tab-" + target)) {
      activate(target);
  ```

  `getElementById("tab-overlap")` is always truthy, so `activate()` runs and the empty pane is
  photographed. The `navbtn-<id>` fallback on the next line would have been the right signal —
  it is exactly the element `tabApplicable` suppresses — but it is only reached when `activate`
  is missing, and no `navbtn-*` id exists in a static snapshot at all, so that branch is dead
  here.

**This is the mirror of the error the manifest was built to prevent.** Its own comment
(`capture_screenshots.py:78-86`) explains that the recap's `embedded N of M images` count
*"derives its denominator from the very Markdown it is measuring"*, so four captures of six
tabs read as `4 of 4` — *"a perfect score against an incomplete set"*. The manifest fixes
under-counting and is silently wrong in the other direction: it reports 6 of 6 for a page that
has 5 tabs, a perfect score against an **over**-counted set, and `generate_recap_pdf.py
--check` trusts it as the external denominator.

⚠️ **This is not an INV-122 violation** and should not be filed as one. INV-122 forbids saving
*the default tab* under another tab's name; the pane activated here really is Cross-Source and
renders its own correct message. The failure is that an inapplicable tab is captured at all.
INV-122's own machinery works: asking for the retired slugs `network`/`merges` was verified in
the same session to skip them with a message on stderr and write no file.

**Reachability is every module, not an edge case.** `module-completion.md:217` runs capture at
each module completion, and the suppression conditions are ordinary early-bootcamp states: one
data source until a second is loaded (Cross-Source), and no multi-record entities (Match Keys
*and* Feature Scores). A module completing with zero multi-record entities produces three
near-empty screenshots, all counted as covered.

### ⚠️ The behavior is already acknowledged in the code, and the fix is a judgment call

`_tabs_present`'s docstring (`capture_screenshots.py:278-281`) states it plainly:

> A tab hidden at runtime by `tabApplicable` still has its `tab-<id>` section in the markup and
> still activates, so this only rejects genuinely absent tabs.

So the interaction was known. What is missing is a decision about it: the sentence scopes
`_tabs_present`, and nothing anywhere decides whether a suppressed tab *should* be photographed
or counted. **There is a defensible reading in which capturing it is right** — the pane renders
an explanatory message ("Cross-source overlap needs at least two data sources"), and a recap
that shows why an analysis is absent is arguably more useful than one that silently omits it.

That reading does not survive the manifest, though, and the two halves can be settled
separately:

- **The count is wrong under either reading.** Reporting `6 of 6` with `not_present: []` for a
  page offering five tabs is an over-count, and `generate_recap_pdf.py --check` consumes it as
  the *external* denominator that exists precisely so the number cannot be self-certified.
- **Whether to keep the image is the open question.** Against keeping it: the bootcamper never
  saw the tab, the funnel already prints `0 CROSS-SOURCE` on every other screenshot, and a
  90%-empty page captioned "Cross-Source" reads as a broken render — the "an empty deliverable
  is worse than none" principle `generate_discoveries_pdf.py` enforces for INV-110.

✅ **Decided by the maintainer, 2026-08-14: do not capture suppressed tabs, and fix the
count.** Both halves apply — the `tabApplicable` check in full, plus the manifest change.
The image is dropped, not merely relabeled.

## Proposed change

1. In `_ACTIVATE_JS` (`capture_screenshots.py:182-200`), consult the app's own rule before
   activating, and report inapplicability distinctly from failure:

   ```js
   if (typeof tabApplicable === "function" && !tabApplicable(target)) { /* signal skip */ }
   ```

   Guard on `typeof` so a snapshot saved before `tabApplicable` existed still captures as it
   does today — the same degradation pattern the file already uses for `activate`.

2. Signal the skip back to Python the way the existing not-present path is signaled, and route
   it to the same handling: stderr message, no PNG, and an entry in the manifest. Record it
   under a distinct reason (e.g. `"reason": "not applicable — the app suppresses this tab"`)
   rather than reusing `"not present in this visualization"`, because the two are diagnostically
   different: not-present means a drifting tab inventory, not-applicable means this dataset.

3. Ensure `requested_count`/`captured_count` and `generate_recap_pdf.py --check`'s external
   denominator exclude suppressed tabs, so the recap's `embedded N of M` counts against the
   tabs the app actually offered.

## Acceptance criteria

- [ ] With a single data source, capture writes **no** `<name>-cross-source.png` and emits a
      message on stderr naming the tab and the reason.
- [ ] With zero multi-record entities, the same holds for `match-keys` and `feature-scores`.
- [ ] The manifest records suppressed tabs with a reason distinct from `not_present`, and
      `captured_count`/`requested_count` do not count them as covered.
- [ ] A snapshot with no `tabApplicable` function captures exactly as it does today (no
      regression for previously saved snapshots).
- [ ] Requesting the retired slugs `network`/`merges` still skips with a message and writes no
      file — INV-122's existing behavior is unchanged.
- [ ] A test covers a suppressed tab and a non-suppressed one, negative-controlled in both
      directions.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — consult `tabApplicable`; add the
  skip reason; correct the manifest counts.
- `tests/test_capture_tabs.py` — extend for suppressed tabs.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — if the `--check` denominator wording
  at :637 needs to name the new manifest reason.

## Source

- Feedback: none — found by `/dry-run` phase 2 on 2026-08-14 (`Source: self-observed
  (assistant retrospective)`), by rendering the captured PNGs and comparing them against the
  page's own nav bar rather than against the exit code (INV-129).
- Priority: Medium-High — it degrades the graduation deliverable, and it corrupts the one
  count that exists specifically to be trustworthy. Not a broken path: capture still exits 0
  and the other tabs are correct.
- MCP re-check: n/a (no Senzing fact) — this is a plugin/app contract defect. The engine was
  live (Senzing 4.3.4) only to produce a realistic snapshot.
- Upstream: not applicable.
- Related specs: `specs/default-tab-capture-without-injection.md` (the INV-122 defect this is
  adjacent to but distinct from)
