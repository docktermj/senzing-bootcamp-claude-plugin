# The Merge Statistics histogram labels its entity-count axis in fifths, so a small Truth Set run shows "0.4 entities"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Merge Statistics tab's histogram counts **entities per bucket** — a whole number by
construction. Its y-axis is labeled by `d3.axisLeft(y).ticks(5)`, which subdivides the domain
into fifths whenever the tallest bar is small. On a 4-record Truth Set run the axis reads:

```
1.0  0.8  0.6  0.4  0.2  0.0
```

against bars whose own printed values are `1`, `0`, `1`, `0`. The chart simultaneously asserts
that a bucket holds exactly 1 entity and that the axis it is measured against runs in 0.2-entity
increments. There is no such thing as 0.4 of a resolved entity.

Reproduced on a real engine (Senzing 4.4.0.26242, sqlite, 2026-08-31): four `VERIFY` records
resolving to 2 entities (1 multi-record) — see the captured
`truthset-merge-statistics.png`. Re-running with 18 records (tallest bucket 9) produces a
correct integer axis `0 2 4 6 8`, which is why this has not been seen before.

**The threshold is exact.** `d3.ticks(0, n, 5)` returns non-integers for n = 1, 2, 3 and
integers from n = 4 up:

| tallest bucket | ticks d3 emits | |
|---|---|---|
| 1 | `0, 0.2, 0.4, 0.6, 0.8, 1` | fractional |
| 2 | `0, 0.5, 1, 1.5, 2` | fractional |
| 3 | `0, 0.5, 1, 1.5, 2, 2.5, 3` | fractional |
| 4+ | `0, 1, 2, 3, 4` … | integer |

**Why this matters more than it looks.** The affected range is not an edge case here, it is the
*designed* case. Module 3b (Truth Set visualization) is the "wow moment" and runs on the small
demo truth set; the built-in evaluation license caps ingestion at 500 DSRs
(`explain_error_code('SENZ9000')`, server 1.35.1), so small entity counts are the normal
bootcamp shape rather than the exception. The histogram is also a deliverable: it is captured to
PNG by `capture_screenshots.py` and embedded in the recap PDF, so the wrong axis outlives the
session. And it lands at the exact moment the module is trying to convince a bootcamper the
numbers are trustworthy.

## Root cause

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1394-1396`:

```js
const y=d3.scaleLinear().domain([0,d3.max(data,function(d){return d.n;})||1]).nice().range([H-m.b,m.t]);
…
svg.append("g").attr("transform","translate("+m.l+",0)").call(d3.axisLeft(y).ticks(5));
```

`.ticks(5)` is a *request for about five ticks*, not a request for integers. `d3` honors the
count by choosing whatever step divides the domain into roughly five parts — which for a domain
of `[0,1]` is `0.2`. `.nice()` does not help: `[0,1]` is already nice at 0.2 granularity, so it
extends nothing. The scale is continuous and the data is discrete, and nothing in the chain says
so.

This is the only affected site. The viz server makes exactly two axis calls, both on this
histogram (`:1395` `axisBottom` is the categorical bucket band and is unaffected). The two other
linear scales draw bars with no axis at all — `:1556` (match-key counts) renders rects and text
directly, and `:1588` has domain `[0,1]` because it genuinely is a proportion.

## Proposed change

In `senzing_viz_server.py`, replace the tick request at `:1396` with explicit integer tick
values derived from the domain maximum:

```js
const maxN = d3.max(data, function(d){ return d.n; }) || 1;
const step = Math.max(1, Math.ceil(maxN / 5));
const yTicks = d3.range(0, maxN + 1, step);
…
.call(d3.axisLeft(y).tickValues(yTicks).tickFormat(d3.format("d")));
```

⛔ **`.ticks(5).tickFormat(d3.format("d"))` is not the fix and must not be used.** It keeps the
fractional tick *positions* and merely rounds their labels, so a max of 1 renders `0 0 0 1 1 1`
— six ticks, four duplicated labels, at unequal visual spacing. That is worse than the current
state because it looks deliberate. The tick *values* have to be integers, not their formatting.

`step` keeps the tick count near five for large maxima (max 40 → step 8) while guaranteeing
integers, and `d3.range(0, maxN+1, step)` is order-independent and empty-safe.

## Acceptance criteria

- [ ] With a tallest bucket of 1, 2 or 3 the y-axis shows only integer tick labels, with no
      duplicates and no fractional positions.
- [ ] With a tallest bucket of 4+ the axis is unchanged from today's correct behavior
      (a 9-high bucket still reads `0 2 4 6 8` or another integer sequence).
- [ ] The axis never renders more ticks than `maxN + 1`.
- [ ] Guarded by a repo-level test that evaluates the tick-value expression for
      `maxN` in 1..12 and asserts every emitted value is an integer — stdlib only, no browser
      and no `plugins/` import (INV-108/INV-091). Negative-controlled: restore `.ticks(5)`
      and confirm the test fails for `maxN` in 1, 2, 3 and passes for 4+.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — integer tick values at `:1394-1396`
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the contract other languages are built against (INV-090) must state that count axes carry
  integer ticks, or a Java/C# rebuild reproduces the same defect
- `tests/test_viz_histogram_integer_ticks.py` — new guard

## Source

- Feedback: none — found by `/dry-run` phase 2 on 2026-08-31, by rendering the artifact and
  looking at it rather than checking the exit code (INV-129), on the first dry run with a
  working Senzing engine available to build a real snapshot
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — cosmetic in mechanism, but it is on a graded deliverable, in the module
  whose entire purpose is the credibility of the numbers, in the size range the license cap
  makes typical
- MCP re-check: n/a (no Senzing fact) — the defect is in the plugin's own D3 rendering. The
  supporting license figure is server-sourced: `explain_error_code('SENZ9000')` returns "default
  500-DSR free tier" and `sdk_guide(topic='load', record_count=1000)` returns "exceeds the
  default Senzing license limit of 500" (server 1.35.1, 2026-08-31).
- Upstream: not applicable — plugin-side rendering, no Senzing-side bug
- Related specs: `visualization-legibility-at-production-scale.md`
