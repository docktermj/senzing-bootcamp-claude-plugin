# Enforce screenshot embedding and backfill orphaned screenshots at graduation

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The final recap PDF (`docs/bootcamp_recap.pdf`) contained no visualization images even though
screenshots were captured throughout the bootcamp. Nine PNGs existed in `docs/visualizations/`
(`entity_graph-*.png`, `multi_source_results-*.png`, `results_dashboard-*.png`), and the PDF
generator supports embedding `![alt](path)` image lines — but the agent never wrote the
`![caption](docs/visualizations/<name>.png)` lines into the recap sections, so at render time there
were no image references to embed. Embedded images make the recap read as a polished keepsake rather
than a text-only document.

## Root cause

The capture → curate → embed mechanism **exists**, but the embed step is a soft agent instruction
that was skipped this run (an execution gap in Modules 3, 6, and 7), and nothing re-links the
orphaned PNGs:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:117-142` documents
  capture → keep 2–3 best → embed `![caption](docs/visualizations/{name}-1.png)` into the module's
  recap **Actions Taken**; `scripts/capture_screenshots.py` does the capture; `scripts/generate_recap_pdf.py`
  embeds referenced local images. The embed is worded as optional ("may embed").
- The capture sites all defer to that optional guidance:
  `module-03-system-verification/phase2-visualization.md:160-165`,
  `module-06-data-processing/phaseD-validation.md:60-63` and `:127-130`,
  `module-07-query-visualize-discover/phase1-query-visualize.md:190-193`.
- Graduation Step 1a reconcile (`graduation/SKILL.md:81-102`) reconciles missing **sections** but
  does **not** backfill un-referenced screenshots into existing sections — so orphaned PNGs are
  never linked before the PDF renders.

This is a follow-up to `capture-visualization-screenshots-for-recap.md`, which established the
mechanism; this spec hardens the enforcement so captured screenshots actually reach the PDF.

## Proposed change

1. **Make the post-capture embed a required step, not an afterthought.** In `module-completion.md`
   and at each capture site, after `capture_screenshots.py` exits 0, writing the 2–3 curated
   `![caption](docs/visualizations/<name>-N.png)` lines into that module's recap **Actions Taken**
   is a MUST in the same turn, recorded at the step checkpoint. (Graceful degradation is unchanged:
   when capture exits non-zero — no headless capability — skip silently and keep the HTML link.)
2. **Add a graduation safety-net** in Step 1, **before** the PDF render: scan
   `docs/visualizations/*.png`; for any PNG not already referenced by an `![...]` line in
   `docs/bootcamp_recap.md`, embed it (2–3 best per module, grouped by filename prefix —
   `truthset_verification-*`, `multi_source_results-*`, `results_dashboard-*`, `entity_graph-*`) into
   the matching `## {Module name}` section's Actions Taken. Append-only and idempotent (INV-085,
   never rewrite prose), skipping missing/unreadable images (INV-048), never blocking graduation.

## Acceptance criteria

- [ ] After a successful capture at any site (Module 3 / 6 / 7), the curated `![...]` image lines are written into that module's recap section in the same turn (a required step, not optional).
- [ ] At graduation, any un-referenced `docs/visualizations/*.png` is embedded into its matching module's recap section **before** the PDF renders, and the resulting `docs/bootcamp_recap.pdf` shows the images.
- [ ] The backfill is append-only and idempotent (INV-085), skips missing/unreadable images (INV-048), never blocks graduation, and re-running produces no duplicate embeds.
- [ ] Capture still degrades gracefully when no headless capability exists (no images, HTML link retained, PDF still renders); no network/CDN fetch is introduced (INV-071).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — make the post-capture embed a required (MUST) step.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — enforce embed at the Truth Set capture site.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — enforce embed at the cross-source-graph and dashboard capture sites.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — enforce embed at the Module 7 capture sites.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1 orphan-screenshot backfill before render.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — no change expected (already embeds referenced images); confirm during implementation.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Captured visualization screenshots were never embedded into the recap PDF" (2026-07-20, Graduation; root cause spans Modules 3, 6, 7)
- Priority: Medium
- Related specs: `capture-visualization-screenshots-for-recap.md` (the mechanism), `recap-sections-name-based-and-complete.md` (INV-085), `recap-durability.md`, `refresh-example-recap.md`
