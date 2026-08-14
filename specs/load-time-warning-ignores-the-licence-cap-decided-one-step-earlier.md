# Load-time warning ignores the licence cap decided one step earlier

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Data collection's Step 8a settles the Senzing License Key question, and a
Bootcamper who declines a key is capped at the built-in evaluation licence — **500
records**, whatever they collected. Step 8b then runs immediately afterwards and
judges SQLite load time from the **collected** total, not the **loadable** one. So a
Bootcamper who has just chosen to load 500 records is warned about the load time of
19,500, and offered "sample down to a smaller record count" — which is what the
previous step already decided for them.

On this walk the numbers are 19,500 collected against a 500-record effective cap: a
warning about a roughly half-hour load, for a load that will take about two minutes.

## Root cause

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:709-716` scopes
the step deliberately, and the scoping is where it goes wrong:

> "it judges the Module 6 SQLite load time from the **actual collected dataset** and
> fires **even when the effective license imposes no record cap**."

The second clause anticipates the *unlimited* licence case — warn anyway, because
time is a separate concern from capacity. That is right. But the *capped* case is
the mirror image and is not addressed: when the licence caps loading **below** the
collected total, the collected total is no longer what will be loaded, and the
warning describes work that cannot happen.

`:719-722` compounds it by computing the total from `config/data_sources.yaml`
alone. Step 8a's outcome — the effective limit, and whether a key was supplied — is
recorded in `config/bootcamp_preferences.yaml` (`license`) and
`config/bootcamp_progress.json` (`license_record_limit`), and Step 8b reads neither,
though it runs seconds later in the same flow.

The overlap in remedies makes it worse rather than merely redundant: Step 8a's
no-key path is "load only the first 500 records as a sample", and Step 8b's option 2
is "Sample down to a smaller record count". Same action, asked twice, one step
apart.

## Proposed change

1. **Compute from the loadable total, not the collected total.** Loadable =
   `min(collected_total, effective_limit)`, where the effective limit comes from
   Step 8a's outcome — `license_record_limit` when set, the evaluation limit when
   `license: evaluation`, unbounded when the limit is `0`.
2. **State both numbers when they differ**, so the Bootcamper sees why the estimate
   is what it is: "19,500 collected, 500 loadable under the evaluation licence — the
   load will take about N minutes." Suppressing the collected figure would be worse
   than the current behaviour, not better.
3. **Do not offer "sample down" when the licence already caps the load.** Option 2
   is a decision Step 8a just made. Keep options 1 and 3 (load it, or switch
   database) and say plainly that sampling is already in force.
4. Keep the "fires even when the licence imposes no cap" clause — it is correct —
   and add its mirror: **when the licence caps below the collected total, judge the
   time from the cap.**

## Acceptance criteria

- [ ] With 19,500 collected and a 500-record effective limit, Step 8b either stays
      silent or warns using the 500-record figure — never the 19,500-record one.
- [ ] With an unlimited licence and a large collected total, Step 8b warns exactly
      as it does today.
- [ ] When the two totals differ, both are stated, with the loadable one driving
      the estimate.
- [ ] "Sample down to a smaller record count" is not offered when the licence
      already caps the load.
- [ ] Timing figures still come from the Senzing MCP server at request time, with
      any figure the server does not return left unavailable rather than
      substituted (unchanged).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — Step 8b's
  input computation, its option list, and the scoping paragraph.

## Source

- Feedback: dry run phase 3, 2026-08-14 — reached Step 8b with 19,500 collected
  records and no licence key, one step after Step 8a capped the load at 500
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — non-blocking and the Bootcamper can proceed either way, but it
  presents a misleading estimate and re-offers a decision made one step earlier,
  which is the INV-006 shape.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-14. `sdk_guide(topic='load', language='python', record_count=19500)`
  returns the licence-required note and the 500-record default limit but **no timing
  figures**; `search_docs(query='hardware sizing capacity planning')` is the route
  that carries them — the Hardware Sizing FAQ gives ~5-10 records/second per engine
  core steady-state, a three-phase load profile where Phase 1 runs 10-100x faster
  than Phase 3, and worked examples (1,000 records ≈ 2 minutes; 100,000 ≈ 55
  minutes). Worth naming that route in Step 8b, which currently says only "consult
  the Senzing MCP server".
- Upstream: not applicable
- Related specs: none
