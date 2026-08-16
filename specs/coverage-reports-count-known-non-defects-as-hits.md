# Two coverage reports count known non-defects as hits

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`coverage_reports.py invariants` and `affected` both carry a standing hit count that has never
reached zero and never can, because a measurable share of each is **known non-defects the report
could filter itself**. Triaged 2026-08-13:

**`invariants` — 70 uncited:**

| bucket | count | why it is not a gap |
|---|---|---|
| self-declared superseded | **14** | a retired invariant does not need a test; its replacement does |
| bootcamp outcome invariants (INV-001–050) | **24** | banners, questions, "the SDK is installed" — offline tests cannot assert a live conversation (`dry-run` phase 3) |
| development rules | 32 | the genuine residue |

The 14 are the sharp point: **`coverage_reports.py shipped` already filters superseded entries,
and `invariants` does not** — same corpus, same author, same file, opposite treatment.

**`affected` — 53 gap rows across 38 specs:**

| bucket | count |
|---|---|
| names a real current file | 38 |
| bare filename — an artifact, not a repo path (`brand_tokens.py`, `bootcamp_data_discoveries.md`, `stakeholder_summary.md`) | 10 |
| path no longer exists — `module-03-system-verification/phase2-visualization.md`, moved when Module 03b was split out | 3 |
| glob the scan cannot match (`scripts/*.sh`, `scripts/*.py`) | 2 |

15 of 53 rows are structurally unmatchable. Three name a file the repo deliberately moved; three
more name `.sh` hooks from before the Python migration (**INV-052**).

## Root cause

Both reports were built to be **lead generators**, and both say so in their own preamble — which
is correct and is not the problem. The problem is that each carries noise it has enough
information to remove: `INVARIANTS.md` declares supersession in the invariant's own text and in
the index, and a predicted path is testably a glob, a bare filename, or a file that does not
exist. A report whose floor is "≈49 hits, most of them fine" is one nobody re-reads, which is the
condition that let INV-060 and INV-097 sit for a month each.

## Proposed change

1. **`invariants`: filter fully-superseded invariants**, and report the count filtered so the
   removal is visible rather than silent.

   ⛔ **The filter MUST be "fully superseded", not a grep for `superseded by INV`.**
   `INVARIANTS.md`'s index draws a two-way distinction *specifically because the naive test is
   wrong*: "**Fully superseded:** the whole invariant is retired… Skip it" versus "**Partly
   superseded, or superseded then restored:** one clause was replaced while the rest still binds.
   **Read it**". **INV-040** is the counter-example — its CORD parenthetical is partly superseded
   by INV-198 while its main clause is what INV-198 strengthens. A naive grep drops it and hides a
   live rule. The index lists the fully-superseded IDs per group explicitly; that list is the
   authority, and INV-001–050 are unindexed so they need the outcome bucket below instead.

2. **`invariants`: separate the bootcamp-outcome invariants (INV-001–050) into their own
   section**, labeled as `dry-run` phase 3 territory rather than test debt. They are the flow's
   own outcomes; no offline test can assert that a banner was presented in a live turn.

3. **`affected`: classify each gap row** — `glob`, `bare filename`, `path no longer exists`, or
   `real current file` — and lead with the last. Do not drop the others: a moved path is worth
   seeing once. Report the counts per class.

4. **`affected`: flag the rows whose spec's `## Acceptance criteria` name the unrecorded file.**
   That is the discriminator the INV-097 defect actually had, and it is mechanical: of 53 rows,
   **11** have it. A criterion promising a file is a different claim from an `## Affected files`
   prediction, which is explicitly only a prediction.

## Acceptance criteria

- [ ] `invariants` filters **fully**-superseded invariants only, sourced from the index's own
      fully-superseded lists, and prints how many it filtered.
- [ ] A test asserts INV-040 (partly superseded, still binding) is **not** filtered, and that a
      fully-superseded ID is — negative-controlled, since this is the exact distinction the naive
      implementation gets wrong.
- [ ] `invariants` reports INV-001–050 in a separate, labeled section that names `dry-run`
      phase 3 as their route.
- [ ] `affected` classifies every row into the four buckets, prints per-class counts, and orders
      real-current-file rows first.
- [ ] `affected` marks the rows whose spec's acceptance criteria name the unrecorded file.
- [ ] Both reports still exit 0 whatever they find, stay stdlib-only, and the other three reports
      are unchanged — asserted, not assumed.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — both reports.
- `tests/test_coverage_reports.py` — the bucket and filter tests.
- `.claude/skills/dry-run/SKILL.md` and `.claude/skills/production-readiness-audit/SKILL.md` — the
  report descriptions, if the printed shape changes.

## Source

- Feedback: none — self-observed while triaging both reports at the maintainer's request, 2026-08-13 (`Source: self-observed (assistant retrospective)`).
- Priority: **Low.** Neither report is wrong today and neither gates anything; both correctly say a hit is not a defect. This is a signal-to-noise improvement to maintainer tooling, with no bootcamper-facing effect.
- MCP re-check: **n/a (no Senzing fact).** Both reports concern this repo's own records only.
- Upstream: not applicable.
- Related specs: `the-invariant-to-enforcing-test-link-is-asserted-nowhere` (the same reports, the same signal-quality argument), `no-report-for-invariants-the-shipped-plugin-never-cites` (whose `shipped` report already implements the superseded filter this asks `invariants` to adopt).
