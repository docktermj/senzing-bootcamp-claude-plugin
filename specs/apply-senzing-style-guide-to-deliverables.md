# Apply the Senzing style guide to every visual deliverable via shared brand tokens

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamper made three per-artifact style-guide requests and then asked to
generalize them into one global rule: whenever the bootcamp produces a visual
deliverable — PDF, HTML, or any format — it should, where appropriate, follow the
Senzing brand style guide bundled in the plugin development repository at
`resources/senzing-style-reference.pdf`, so branding is on-brand by default rather
than re-specified per artifact. The three concrete artifacts:

- **Module 3 live visualization web app** (`localhost:8080`).
- **Module 3 standalone HTML snapshot** (`docs/visualizations/truthset_verification.html`).
- **Graduation recap PDF trophy** (`docs/bootcamp_recap.pdf`).

Each currently uses its own ad hoc styling, and none references the style guide.

## Root cause (confirmed)

Each generator hardcodes its own palette/typography, and none draws on the style
guide or any shared brand tokens:

- Live app + snapshot: `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` —
  the `PAGE` HTML template (`:213-378`), CSS `<style>` block (`:219-259`), `:root`
  color vars (`:220`, navy `#0c2340` / blue `#175ca8` / gold `#c8922a`), fonts
  (`:222`), and `SOURCE_COLORS` (`:52-57`). The snapshot reuses the same `PAGE`
  template via `write_snapshot()` (`:458-478`).
- Recap PDF: `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — palette
  constants (`:232-247`, NAVY/BLUE/ACCENT/etc.), cover design `_render_cover()`
  (`:364-458`), Helvetica core fonts throughout.
- **Key constraint:** `resources/senzing-style-reference.pdf` lives at the **repo
  root `resources/`, not inside `plugins/senzing-bootcamp/`** — it is a maintainer
  asset **not shipped with the plugin** and not available at bootcamper runtime.
  Grep confirms no plugin script or skill references it. So the brand values must be
  **extracted into the shipped plugin** (a shared brand-tokens source consumed by the
  generators), not read from the PDF at runtime.

The current palettes are already loosely "Senzing-flavored" guesses; they must be
reconciled against the actual style guide values.

## Proposed change

1. **Extract brand tokens** (color palette, typography, logo usage,
   spacing/conventions) from `resources/senzing-style-reference.pdf` into a single
   **shared brand-tokens source shipped inside the plugin** (e.g. a small module /
   data file under `plugins/senzing-bootcamp/scripts/`), so the PDF itself is not a
   runtime dependency.
2. **Consume the tokens from every generator:** apply them to
   `senzing_viz_server.py` (entity-graph colors/legend, tabs, search UI, header/
   snapshot HTML — keep the four tabs / four APIs / D3 v7 force-directed graph
   behavior unchanged) and to `generate_recap_pdf.py` (cover page, section styling,
   typography — keep the cover/TOC/per-module four-subsection structure and the
   fpdf2+stdlib fallback intact per INV-048/INV-066).
3. **Add a global directive** in `ground-rules.md` (and/or a shared reference the
   skills cite) that any generated visual artifact should apply the Senzing brand
   tokens "where appropriate" — leaving room for plain functional/dev output that
   does not warrant branding. This consolidates the three per-artifact requests.

This is a visual/branding pass: functional behavior is unchanged, and it must not
regress the offline-render invariant (INV-071, D3 vendored/inlined) or the recap
render fallbacks (INV-048/INV-066).

## Acceptance criteria

- [ ] Brand tokens (colors, typography, logo usage) are extracted from `resources/senzing-style-reference.pdf` into one shared source shipped inside the plugin; the PDF is not required at bootcamper runtime.
- [ ] The live viz app, the standalone snapshot, and the recap PDF all render using the shared brand tokens (consistent look and feel), with no per-generator ad hoc palettes diverging from them.
- [ ] Functional behavior is unchanged: the viz app keeps its four tabs / four APIs / D3 v7 graph; the recap PDF keeps its cover/TOC/per-module four-subsection structure; INV-038/INV-048/INV-066/INV-071 still hold.
- [ ] A global "apply the Senzing style guide to visual deliverables where appropriate" directive is documented in `ground-rules.md`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/` — new shared brand-tokens source (shipped).
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — consume tokens in the `PAGE` template / CSS (`:213-378`, `:219-259`, `:220`, `:222`) and `SOURCE_COLORS` (`:52-57`).
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — consume tokens in the palette (`:232-247`) and cover/section rendering (`:364-458`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — global visual-branding directive.
- `resources/senzing-style-reference.pdf` — source of the extracted tokens (maintainer asset, read at implementation time).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Global rule — apply the Senzing style guide to every visualization the bootcamp produces" (2026-07-18, General/all deliverables), consolidating "Style the Module 3 visualization web app per the Senzing style guide" (Module 3), "Style the standalone snapshot per the style guide …" (Module 3, styling part), and "Render the recap PDF trophy using the Senzing style guide" (Graduation).
- Priority: Medium.
- Related specs: `recap-pdf-professional-design.md` (recap PDF design/renderer — this adds the brand-guide source of truth on top), `vendor-d3-offline-visualization.md` (INV-071 offline render), `snapshot-static-search-results.md` (the snapshot's dead-search-UI fix, done in the same snapshot pass — distinct concern).

## Invariants introduced

- `INV-081` — Bootcamper-facing visual deliverables (viz web app + snapshot, recap PDF, future charts/HTML/PDF) MUST take palette/typography from the shared shipped `scripts/brand_tokens.py` (single source, extracted from the reference PDF, not required at runtime), never an ad hoc palette; consumers fall back gracefully and keep rendering offline (INV-071). (recorded in `specs/INVARIANTS.md`)
