# `--single` crops to the viewport and labels the result "Full page"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scripts/capture_screenshots.py --single` captures only the browser viewport — a fixed
1440×900 — while printing the label **`Full page`** for the image it wrote. For any single-page
deliverable taller than 900 px, the recap keepsake therefore carries an image showing the top of the
page under a label asserting it shows all of it.

**Observed live, phase-3 dry run, 2026-08-14.** Module 5 Phase 1 step 6's quality-assessment page
was rendered for a three-source scenario and captured with the invocation
`module-completion.md` prescribes:

```bash
python3 <helper> --html docs/visualizations/data_quality_assessment.html \
    --out-dir docs/visualizations --name data_quality_assessment --single
```

The helper exited 0 and printed:

```text
docs/visualizations/data_quality_assessment.png	Full page
```

The PNG is **1440×900**. The rendered page is **~2100 px** tall (measured by re-rendering the same
file at `--window-size=1440,4000`). The captured image contains **MERIDIAN_CRM in full and the top
three lines of MERIDIAN_STOREFRONT**; `MERIDIAN_REWARDS` — an entire source, its scores, its
per-field completeness and its format patterns — is **absent**, as is the footer recording that the
page rendered offline from the brand tokens.

So two of three sources are missing from the artifact the Bootcamper keeps, and nothing anywhere
says so: exit 0, a real 84 KB PNG, a manifest entry, and the label `Full page`.

### Why the label is the harmful half

INV-123 requires every caption to be **derived from the capture**: *"Build it from the tab label the
helper printed (which matches the filename slug), and — before writing it — open the image and
confirm it shows that tab."* The helper's printed label is the designated input to that caption. Here
that input is itself the false claim, so a caller who follows INV-123 exactly — take the label,
open the image — is handed "Full page" for an image that is not the full page. Only measuring the
page's height against the PNG's reveals it, which nothing asks for.

This is the same failure shape the script's own docstring was written to close, one mode over:

> ⛔ **One capture per tab, never per viewport.** This script used to vary the browser window size
> across a single page load — `(1280,800)`, `(1280,1600)`, `(1024,768)` — and had no interaction
> step at all, so every image showed whichever tab was active by default. Three files were written,
> the script exited 0, and nothing looked wrong…

The tabbed path was fixed by capturing per tab at a fixed viewport, which is correct **for a tabbed
app** — each tab's content is designed to fit a screen. `--single` then inherited that fixed
viewport, where the premise does not hold: a single-page deliverable is a *document*, and documents
are as tall as their content.

## Root cause

`plugins/senzing-bootcamp/scripts/capture_screenshots.py`:

- `_WINDOW = (1440, 900)` (line ~178) is a single fixed viewport used by every backend.
- None of the three backends requests a full-page capture in `--single` mode:
  - Playwright: `page.screenshot(path=str(out))` — **no `full_page=True`**;
  - Selenium: `driver.set_window_size(*_WINDOW)` then `driver.save_screenshot(...)`;
  - Chrome CLI: `--window-size=1440,900 --screenshot=<out>`.
- `SINGLE_PAGE_LABEL = "Full page"` (line ~130) is emitted unconditionally for the mode, so the
  label describes the *intent* of `--single` rather than what the capture did.

`--single` was added by `single-page-capture-instruction-produces-zero-images` (implemented
2026-08-14). That spec's criteria were about **producing one image instead of zero** — which it does
— and its verification measured the PNG's existence, magic bytes, size and manifest entry, never its
height against the page's. So the gap was not a regression; it was never in scope.

## Proposed change

1. **Capture the whole page in `--single` mode, per backend:**
   - **Playwright:** `page.screenshot(path=str(out), full_page=True)` — the supported route, one
     argument.
   - **Selenium:** measure `document.documentElement.scrollHeight` via
     `driver.execute_script`, resize the window to that height (clamped, see 3), re-screenshot.
   - **Chrome CLI:** it has no full-page flag, so do it in two passes — render once with
     `--dump-dom`/`--virtual-time-budget` to read `scrollHeight`, then re-render with
     `--window-size=<width>,<measured height>`. If the measurement cannot be obtained, fall back to
     today's fixed viewport and say so (see 2).
   ⛔ **The tabbed path keeps the fixed viewport unchanged** — its per-tab premise is correct and
   its docstring records why. This change is scoped to `--single` (and to the auto-detect safety net
   that routes a tab-less page into it).

2. **Make the label describe what happened, not what was intended.** Emit `Full page` only when a
   full-page capture actually succeeded; otherwise emit something that cannot be mistaken for it —
   e.g. `Top of page (viewport only)` — and warn on stderr naming the captured height against the
   page height. A caller obeying INV-123 then produces an honest caption without having to measure
   anything.

3. **Clamp the height, and report the clamp.** A pathological page must not produce a 30,000-px PNG.
   Pick a documented maximum, and when it bites, say so in the label and on stderr rather than
   silently truncating — the same skip-and-report discipline INV-122 already requires of this script.

4. **Verify by height, not by existence.** The test for this mode must render a page known to be
   taller than the viewport and assert the PNG's pixel height covers it, so the defect cannot return
   under a passing "the file exists and has magic bytes" assertion — which is exactly what let it
   through.

## Acceptance criteria

1. `--single` on a page taller than the viewport produces a PNG whose pixel height covers the full
   rendered page, on whichever backend is available.
2. The printed label is `Full page` **only** when a full-page capture succeeded; a viewport-only
   fallback prints a distinct label and warns on stderr with both heights.
3. The tabbed path is unchanged: same fixed viewport, same per-tab slugs, same labels, same
   skip-and-report behaviour (asserted, not assumed).
4. A height clamp exists, is documented, and is reported in the label and on stderr when it applies.
5. The new test renders a deliberately tall page and asserts the captured height — negative-controlled
   by restoring the viewport-only capture, which must fail the new assertion while still passing the
   existing existence/magic-byte checks.
6. Cross-platform: the measurement path works on each backend or degrades per criterion 2; no new
   dependency is introduced.

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py`
- `tests/test_capture_single_page.py` (extend — it currently asserts existence, not height)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, by obeying Module 5 step 6's fourth
  rule (INV-129: *"Verify the rendered page, not the exit status — open it and confirm the bars and
  the per-field numbers actually drew"*) and noticing the opened image stopped mid-page
  (`Source: self-observed (assistant retrospective)`). Confirmed by re-rendering the same HTML at
  `--window-size=1440,4000` and comparing: 2 of 3 sources present in the `--single` capture, all 3
  present in the taller render.
- Priority: **Medium-High.** It degrades a graduation deliverable silently, and it does so through
  the exact input INV-123 tells the caller to trust. It is not a broken path — a capture still
  happens and never blocks the module (INV-048/INV-122) — but the artifact misrepresents itself, and
  the two deliverables `--single` exists for (Module 5's quality and mapping pages) are both
  one-card-per-source documents that grow past the viewport with three or more sources, which is the
  normal case.
- MCP re-check: n/a (no Senzing fact — this is the plugin's own capture helper). Server version this
  session is **1.32.9** (`get_capabilities`, 2026-08-14).

## Invariants introduced

- `INV-235` — A capture helper's printed label MUST describe what the capture **achieved**,
  never what its mode intended; a shortfall MUST be reported on stderr with both heights, and
  the "full page" wording MUST be unreachable except on an actual full-page capture, including
  by silence (recorded in `specs/INVARIANTS.md`).

## Deviations from this spec, and why (2026-08-14)

- **The root cause was deeper than the spec's diagnosis, and the spec's own verification
  recipe would have missed it.** Criterion 4 says to "verify by height, not by existence".
  Implementing exactly that — measure `scrollHeight`, screenshot at that height — produced a
  **2671px PNG of a 2671px page with the footer still missing**, and a height assertion passes
  that build. Cause: under `--headless=new`, `--window-size` includes window chrome, so the
  rendered viewport was 813px for a requested 900 and the last ~87px of the page never
  rendered into the image. Found by decoding the PNG's bottom rows and finding zero footer
  pixels, then probing the live layout (`footerTop: 2613, footerBottom: 2671, innerHeight:
  813`). The offset is now measured at runtime and added to the requested window height, and
  the guard asserts the footer's **pixels**, not the image's dimensions. Both facts are
  recorded in INV-235, because "verify by height" is the intuitive check and it is insufficient.
- **Two of the four backends are implemented but not runtime-verified**, and this environment
  cannot verify them: Playwright and Selenium are not installed (`wkhtmltoimage` is absent
  too). Verified live on the **Chrome CLI** backend, which is the one needing the two-pass
  measurement and therefore the riskiest: a 2671px page captured whole with its footer present
  (58 footer rows at y=2613-2670), a 14428px page clamped to 12000 with the stderr warning and
  the `Full page (clamped at 12000px)` label, and a short page still labelled `Full page`.
  Playwright uses its native `full_page=True` (no offset applies, since its `viewport` sets the
  viewport directly); Selenium grows the window to the measured height. Both record their
  outcome, and any backend that records nothing defaults to the viewport-only label rather than
  inheriting the full-page claim — which is the safe direction for an unverified path.
- **`wkhtmltoimage` is exempt from the clamp, and says so inline.** `--width` with no
  `--height` renders the full content height by design, so it needs no measurement pass; the
  clamp is not enforced there. Stated rather than implied, since a reader would otherwise
  expect all four backends to clamp.

## Invariants introduced — updated 2026-08-14 on maintainer review

Split into two, so a code rule and a test rule do not share one ID:

- `INV-235` — the **label-honesty rule**: a capture helper's printed label describes what the capture
  achieved, never what its mode intended.
- `INV-241` — the **verification rule** extracted from it: a guard for a rule about an artifact's
  content asserts that content, never a proxy for it (a dimension, a byte count, an exit status, a
  file's existence). Filed under *The development record itself*, which is where this repo files rules
  governing its own tests — and which is also the group exempt from shipped-citation scoring, correctly,
  since no file under `plugins/` should cite it.

⚠️ **The ⛔ stays in INV-235 as the concrete case**, where it is unmissable at the point of use, with a
dated forward pointer to INV-241 for any other artifact. Rules 1 and 2 forbid removing it, and it earns
its place: this is the clause that stops the next person writing a height-only assertion that passes a
broken build.
