# Single-page capture instruction produces zero images

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-completion.md` tells the guide how to screenshot a single-page HTML
deliverable — the Data Quality, Mapping, and Transformation module's quality and
mapping pages:

> A **single-page** HTML deliverable … has no tabs: capture it as **one image**,
> with **no `--tabs` argument**, and embed that one image.

Following it captures **nothing**. `--tabs` defaults to the six-tab app set, so
omitting it requests all six tabs, none of which exist on a single-page document,
and the helper exits having written no files:

```text
tab 'features' is not present in this visualization; skipping it rather than
capturing the default tab under its name.
…
None of the requested tabs exist in this visualization; nothing to capture.
Requested: graph, stats, matchkeys, features, overlap, probe.
```

The same paragraph names the consequence two sentences earlier — "it captures
nothing, so the page **silently misses the recap**" — while prescribing the
invocation that causes it. And unlike a missed tabbed capture, nothing recovers it:
graduation's orphaned-screenshot backfill embeds PNGs the recap does not reference,
and here no PNG exists to backfill.

## Root cause

`plugins/senzing-bootcamp/scripts/capture_screenshots.py`:

- `:675-679` — `ap.add_argument("--tabs", default="")`.
- `:523-526` — `def resolve_tabs(spec): if not spec: return list(DEFAULT_TABS)`.

So an omitted `--tabs` is not "no tabs", it is **all** tabs. The helper has no
single-page / no-tab mode at all.

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:166-171`
assumes the opposite, and is otherwise exactly right about the situation — it
correctly identifies which deliverables are single-page, and correctly describes the
INV-122 skip-and-report behaviour. Only the invocation is wrong.

Reproduced 2026-08-14 against `docs/visualizations/data_quality_assessment.html`, a
valid 10,991-byte page that renders correctly.

## Proposed change

Fix the helper, not just the instruction — the instruction describes the behaviour a
reader would reasonably expect, and the helper is where the concept is missing.

1. **Add a single-page mode to `capture_screenshots.py`.** Either make `--tabs ""`
   mean "capture the page as one image" (renaming the current default to an explicit
   `--tabs all`), or add `--single` / `--no-tabs`. Prefer whichever keeps the tabbed
   app's existing invocations unchanged.
2. **Auto-detect as a safety net.** When none of the requested tabs is present *and*
   the page contains no tab controls at all, capture the page as one image rather
   than exiting empty — the current message is correct for a tabbed app whose tabs
   were misnamed, and wrong for a document that has no tabs by design.
3. **Correct `module-completion.md:166-171`** to the invocation that actually works,
   whichever is chosen.
4. **Name the output** so the embed is predictable: `{name}.png` for a single-page
   capture, alongside the tabbed `{name}-<tab-slug>.png` convention.

## Acceptance criteria

- [ ] Capturing a single-page HTML deliverable produces exactly one PNG.
- [ ] The tabbed app's six-image capture is unchanged, by the same invocation it
      uses today.
- [ ] A tabbed app whose requested tabs are all misnamed still reports and skips —
      the INV-122 behaviour is preserved, and is not replaced by a whole-page
      capture.
- [ ] `module-completion.md` prescribes an invocation that works, and the two agree.
- [ ] A repo-level test covers the single-page path against a fixture page with no
      tab controls, negative-controlled by restoring the `default=""` →
      `DEFAULT_TABS` behaviour.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — single-page mode and
  the no-tab-controls safety net.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — the
  invocation at `:166-171`.
- `tests/test_capture_single_page.py` — new guard.

## Source

- Feedback: dry run phase 3, 2026-08-14 — accepted the Phase 1 quality-visual offer,
  generated the page, and tried to capture it for the recap as
  `module-completion.md` instructs (`Source: self-observed (assistant
  retrospective)`)
- Priority: Medium — the page itself is still produced and linked, so nothing is
  broken for the Bootcamper; what is lost is the embedded image in the permanent
  keepsake, silently, for every single-page deliverable in the bootcamp.
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none
