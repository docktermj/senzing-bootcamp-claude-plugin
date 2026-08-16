# A targeted re-capture rewrites the tab manifest from scratch, and graduation's coverage check then passes on a 1-of-1 denominator

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

All six tabs of `results_visualization.html` were captured, and all six PNGs reached the recap. But
the first Search / Probe capture came back showing an empty result set (the query used a surname
alone, which matched nothing), so that one tab was re-captured on its own. The re-run rewrote
`docs/visualizations/results_visualization-tabs.json` from scratch:

```json
{"requested": ["probe"], "requested_count": 1, "captured_count": 1, "not_applicable": [], "failed": []}
```

The five earlier captures are gone from the manifest. The companion manifest for the Truth Set
visualization, never re-captured, still correctly records all six.

Graduation's Step 1a tab-coverage check reads exactly this manifest to answer "did every captured
tab reach the recap?" On a 1-of-1 denominator it reports full coverage — **and it would report full
coverage just as cheerfully if five of the six images had been lost**, because the record of their
ever having been captured was destroyed by the fix for an unrelated problem.

⛔ **The check is structurally incapable of failing after a targeted re-capture, and nothing says
so.** Graduation's own guidance is emphatic that a skipped check is reported as skipped rather than
counted as passed; this one is silently neutered instead. No harm on this run — the recap carried
all six images, verified by counting them directly against
`docs/visualizations/results_visualization-*.png` rather than trusting the manifest.

## Root cause

**`write_manifest` builds its payload solely from the current run and opens the file for
truncation.** `plugins/senzing-bootcamp/scripts/capture_screenshots.py:952-1015`:

- `:972-999` composes `requested` / `captured` / `not_present` / `not_applicable` / `failed`
  entirely from this invocation's arguments — nothing reads the manifest already on disk.
- `:1000-1001` derives `captured_count` and `requested_count` from that payload.
- `:1005` opens the target with `"w"`, so a run capturing one tab replaces a manifest describing
  six.

The consumer has no way to notice. `generate_recap_pdf.py:874-901` (`tab_coverage_problems`) and
`:904-922` (`tab_coverage_note`) both iterate `manifest["captured"]` and compare it against the
recap's image targets. Both are correct given the manifest; neither has any denominator of its own,
which is by design — the file header at `:826-829` states plainly that the manifest "is the only
number in the system that does not come from the recap Markdown". That is exactly why a truncated
manifest is undetectable from the consumer side: it is the external denominator, and there is no
second one to check it against.

The failure is not that either side is wrong. It is that **a partial write and a complete write are
indistinguishable in the file format** — nothing in the manifest records that this run was scoped
to a subset.

## Proposed change

Two changes; the first is the fix and the second is the guard that survives it.

1. **Merge rather than replace** (`write_manifest`, `capture_screenshots.py:952`). Read any
   existing `<name>-tabs.json` first; when it parses and its `schema` matches:
   - union `requested` with the prior `requested`;
   - replace the `captured` / `not_present` / `not_applicable` / `failed` entry for **each tab this
     run touched**, and keep every entry for tabs it did not;
   - recompute `captured_count` / `requested_count` from the merged payload.

   Keep the existing best-effort contract (INV-122): an unreadable or unparseable prior manifest is
   reported on stderr and overwritten, exactly as today — a merge that could fail the run would be
   worse than the defect. Merging into a corrupt file is not attempted.

2. **Give `--check` a denominator it does not get from the manifest.** Have it compare each
   manifest's captured count against the number of `<name>-*.png` files on disk beside it, and
   report a shortfall as a **problem** naming both figures. This is the cheap version of the same
   guard and it is what makes the check able to fail: the PNGs are the one record a truncating
   write cannot destroy, since the earlier images stay on disk. It also catches the general case —
   any manifest that undercounts, however it got that way — rather than only the re-capture path.

⚠️ **Build both.** The merge fixes the mechanism; the on-disk cross-check is what notices when the
merge is bypassed, skipped, or reintroduced by a future edit. This is the failure class where a
single fix leaves the check still incapable of failing.

## Acceptance criteria

- [ ] Re-capturing a subset of tabs into a directory with an existing `<name>-tabs.json` leaves the
      untouched tabs' entries intact, and `requested_count` / `captured_count` reflect the union.
- [ ] The re-captured tab's own entry is **replaced**, not duplicated — including when it moves
      between `captured`, `failed` and `not_applicable` between runs.
- [ ] An unreadable or schema-mismatched prior manifest is reported on stderr and overwritten; the
      capture run still exits as it does today (INV-122 — the PNGs are the deliverable).
- [ ] `generate_recap_pdf.py --check` reports a problem when a manifest's captured count is lower
      than the number of `<name>-*.png` files beside it, naming both figures.
- [ ] A test reproduces the reported sequence — capture six tabs, re-capture one — and asserts the
      manifest still describes six and that `--check` would have failed had it described one.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — `write_manifest` (`:952-1015`), and
  its two call sites (`:1203`, `:1221`).
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `tab_coverage_problems` (`:874`) and
  the manifest loader `find_tab_manifests` (`:834`), for the on-disk denominator.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1a's coverage check (`:509-510`,
  `:669`) if its reported wording changes.
- `tests/` — new guard for the re-capture sequence and the on-disk cross-check.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "A re-captured tab overwrites the capture manifest, and graduation's coverage check then passes on a 1-of-1 denominator" (2026-08-16, Module Query, Visualize and Discover Phase 1 step 3c, surfaced at graduation Step 1a; `Source: self-observed (assistant retrospective)`)
- Priority: High — the check's failure mode is a false pass on a keepsake deliverable, and a Bootcamper cannot see it.
- MCP re-check: n/a (no Senzing fact). Both scripts ship with the plugin; nothing here involves the Senzing MCP server.
- Upstream: not applicable — routed `plugin`.
- Related specs: `specs/embedded-image-count-needs-an-external-denominator.md` (why the manifest exists at all — the same argument, one level up), `specs/capture-screenshots-captures-tabs-the-app-suppressed.md` (`requested_count`'s other consumer), `specs/embedded-of-referenced-count-needs-external-denominator-crossref.md`

## Why this belongs to the external-denominator family

`embedded-image-count-needs-an-external-denominator` established the manifest precisely because a
count derived from the recap Markdown cannot detect a captured tab that was never referenced. That
reasoning holds, and this defect is its next term: an external denominator that any later run can
silently shrink is not external to the thing it measures once a re-capture is in play. The second
proposed change restores the property by anchoring to the PNGs, which no manifest write touches.
