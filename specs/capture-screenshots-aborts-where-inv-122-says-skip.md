# capture_screenshots aborts the whole run where INV-122 says skip the one tab

Maintain the invariant conditions in @INVARIANTS.md and resolve the following ambiguity:

## Problem

INV-122 states:

> A tab that is not present in the page **MUST be skipped and reported on stderr**, never
> captured under its name — otherwise the default tab is silently saved as that tab.

`capture_screenshots.py` has two behaviors for "a requested tab I cannot capture", and only one
of them skips:

**Case A — a tab id the script does not recognize.** Verified 2026-09-02:

```
$ capture_screenshots.py --html snap.html --tabs "graph,nosuchtab,matchkeys"
unknown tab id(s): nosuchtab. Tab ids: graph, stats, matchkeys, features, overlap, probe
exit 1 — zero files written
```

`graph` and `matchkeys` are both valid and both present in the page, and **neither was
captured**. One typo in a comma-separated list yields no screenshots at all.

**Case B — a known tab the app suppresses for this data.** Verified same run, and correct:

```
$ capture_screenshots.py --html snap.html --tabs all
… 5 PNGs written, slug-named …
tab 'overlap' is not applicable to this data, so the app does not show it; skipping it
rather than capturing an empty pane the bootcamper never saw.
exit 0
```
with the manifest recording `not_applicable` distinctly from `not_present` (INV-232), and
`captured_count: 5` matching the app's visible tab count.

Case B is exactly what INV-122 and INV-232 require. Case A is stricter than INV-122's wording
and sits awkwardly against the surrounding contract:

- **INV-146** — "Every screenshot a visualization capture produced MUST reach the recap … a
  count cap or 'best of' selection can only delete unique content." Case A produces none.
- **INV-052 / INV-066 / INV-048** — capture is best-effort and the module continues unblocked.
  Case A blocks on a caller-side typo.

## Root cause

The two cases are answering different questions, and only one of them is the question INV-122
asks:

- Case A validates the requested ids against the script's **own** tab vocabulary — a
  caller-input check, performed before any work.
- Case B checks the tab against **this page's** rendered content — which is what "not present in
  the page" means.

So the implementation is not straightforwardly wrong; INV-122's clause was written for Case B
and Case A is an additional, undocumented behavior that the invariant's wording appears to
forbid. ⚠️ Note that Case A **does** satisfy INV-122's actual hazard — the default tab is never
saved under another tab's name — and the message names every valid id, so it is a good error.
The question is whether it should be fatal to the valid tabs alongside it.

## Proposed change

This needs the maintainer's call, because it is a contract decision rather than a bug fix. Two
coherent options:

**Option 1 — make Case A skip, matching INV-122's wording.** Capture every recognized,
present tab; report each unrecognized id on stderr; exit non-zero *only if nothing was
captured*. Consistent with best-effort capture and with INV-146. Risk: a typo silently yields a
short set, and the caller may not read stderr — though the manifest's `requested` vs `captured`
counts already make the shortfall machine-detectable.

**Option 2 — keep the abort and scope INV-122's clause to Case B.** Amend INV-122 to say a
recognized tab absent *from the page* is skipped and reported, while an **unrecognized id is a
caller error that fails the run before any capture**, and state why: a typo caught before work
is cheaper than a silently short set, and re-running is free. Add the distinction to the
invariant so the next audit does not read the implementation as a violation.

**Recommendation: Option 2.** The abort prevents a partial set being mistaken for a complete
one, the manifest already distinguishes the honest cases, and the failure is loud, immediate and
names every valid id. What is actually missing is that INV-122 does not describe it — the
implementation is defensible and the invariant is silent, which is the gap worth closing.

## Acceptance criteria

- [ ] INV-122 distinguishes an **unrecognized tab id** from a **recognized tab absent from the
      page**, and states the required behavior and exit code for each.
- [ ] Whichever option is chosen, a test pins both cases: Case A's chosen behavior, and Case B
      skipping `overlap` while still capturing the other five with slug names.
- [ ] The three exit codes stay distinguishable and documented — 0 (captured, possibly with
      skips), 1 (caller-side tab error), 2 (no headless capability) — per INV-122's own
      reason-distinguishing clause.
- [ ] Negative control: whichever behavior is specified, break it and confirm the new test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-122: distinguish the two cases (both options require this)
- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — only under Option 1
- `tests/test_capture_tabs.py` — pin both cases

## Source

- Feedback: `/dry-run` phase 2, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Low — no data is silently corrupted in either case; this is an invariant-wording gap that makes a defensible implementation read as a violation
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: `specs/default-tab-capture-without-injection.md`, `specs/capture-screenshots-cannot-tell-whether-the-tab-actually-changed.md` (the 2026-08-28 finding on the `--url` path; ⚠️ note that path was **not** re-tested this run — see coverage limits)

