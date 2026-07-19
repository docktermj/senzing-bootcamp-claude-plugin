# Capture and curate visualization screenshots into the recap PDF

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Whenever a module produces a visualization — the Truth Set visualization, the Module 6
results dashboard / cross-source graph, and Module 7's Query/Visualize/Discover output —
the bootcamp only links to the generated HTML. The bootcamper asked that the bootcamp
instead take multiple screenshots of each visualization, analyze them to pick the 2–3 best
representative shots, and embed those images into the corresponding section of
`docs/bootcamp_recap.md` (which feeds the graduation recap PDF). A screenshot helps the
bootcamper remember what they actually built and saw, not just read text about it.

## Root cause

Not a defect — the feature does not exist. `grep -rniE "screenshot|headless|puppeteer|
playwright|selenium|\.png"` across `plugins/senzing-bootcamp/skills` and `scripts` finds
no screenshot/headless-capture mechanism (only an unrelated prose mention in
`module-05 phase1-quality-assessment.md:21`). Today:

- Visualizations are written as HTML under `docs/visualizations/` (INV-070) — e.g. the
  Truth Set snapshot (`phase2-visualization.md`), the Module 6 results dashboard
  (`phaseD-validation.md:118-120`) and cross-source graph (`:58`), and Module 7's
  visualizations (`module-07-query-visualize-discover/phase1-query-visualize.md`).
- The recap (`docs/bootcamp_recap.md`) carries text/links only — the per-module template
  in `bootcamp-onboarding/module-completion.md:56-76` has no image embedding.
- The recap PDF renderer (`scripts/generate_recap_pdf.py`) renders the four labeled text
  subsections per module; it does not embed images.

## Constraints to respect (call out in the spec — do not hand-wave)

- **INV-001 (cross-platform).** Screenshotting HTML requires a headless renderer. There is
  no guaranteed browser on Linux/macOS/Windows, so capture MUST degrade gracefully: when no
  headless capability is available, skip screenshots and keep the existing HTML link — the
  recap and PDF must still render (never block graduation on a missing screenshot).
- **INV-071 / offline.** Visualizations already render offline (vendored D3, no CDN);
  screenshot capture MUST NOT introduce a network fetch or a CDN/browser download step.
- **INV-052 / INV-066.** Any helper is a `python3` script invoked in exec form; any extra
  dependency (a headless browser) is optional with a fallback, installed per INV-066
  (explicit interpreter, project-local, PEP 668-safe), never modifying system Python.
- **INV-070.** Screenshots (like the HTML) live under `docs/visualizations/` (e.g.
  `docs/visualizations/<name>.png`); INV-017/INV-050 file placement holds.
- **INV-048.** The recap PDF must still always render; embedded images are additive.

## Proposed change

- Add an **optional screenshot-capture step** after each visualization is generated (Truth
  Set visualization; Module 6 results dashboard and cross-source graph; Module 7
  visualizations): render the HTML with a headless capability if one is available, capture
  multiple shots, have the agent compare them and select the 2–3 most representative, and
  save the selected PNGs under `docs/visualizations/`.
- **Embed the selected images** into the matching `## Module N:` section of
  `docs/bootcamp_recap.md` (Actions Taken or a dedicated "Visualizations" line), via the
  `module-completion.md` recap template, so they carry through to the PDF.
- **Extend `scripts/generate_recap_pdf.py`** to embed referenced local images in a module
  section (with a graceful skip if an image is missing or unreadable).
- **Graceful degradation:** when no headless capture is available, record no images and
  keep the existing HTML link; log the skip (INV-012-friendly) and continue. Honor
  verbosity.
- Consider a small shared helper (`scripts/capture_screenshots.py`) so the three
  visualization sites share one tested path rather than each reinventing capture.

## Acceptance criteria

- [ ] After each visualization (Truth Set viz, Module 6 dashboard + cross-source graph, Module 7 visualizations), when a headless capability is available, multiple screenshots are captured, compared, and the 2–3 best are saved under `docs/visualizations/`.
- [ ] The selected images are embedded into the correct `## Module N:` recap section and appear in the rendered `docs/bootcamp_recap.pdf`.
- [ ] When no headless capability exists, capture is skipped without error, the HTML link is retained, and the recap/PDF still render (INV-048); graduation is never blocked.
- [ ] Capture adds no network/CDN fetch (INV-071); any extra dependency is optional and installed per INV-066; helpers are `python3` exec-form (INV-052); images live under `docs/visualizations/` (INV-070).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — capture + curate after the Truth Set visualization.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — capture after the results dashboard (`:118-120`) and cross-source graph (`:58`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — capture after Module 7 visualizations.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — recap template: allow embedded images in a module section (`:56-76`).
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — embed local images referenced in a module section (graceful skip when absent).
- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` (new, optional shared helper) — headless capture with graceful fallback.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Capture and curate screenshots of visualizations for the recap PDF" (2026-07-18, Module: data_processing).
- Priority: Medium.
- Related specs: `recap-pdf-professional-design.md` / `apply-senzing-style-guide-to-deliverables.md` (recap PDF rendering), `vendor-d3-offline-visualization.md` (offline visualization, INV-071), `layout-tree-reconciliation.md` (INV-070 `docs/visualizations/`).
