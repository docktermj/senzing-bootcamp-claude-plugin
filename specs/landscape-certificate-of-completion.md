# Add a landscape "Certificate of Completion" as the final recap page

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamp recap (`docs/bootcamp_recap.md`, rendered to PDF at graduation) ends with
the last content module and has no capstone. The bootcamper wants the final page of
the recap to be a "Certificate of Completion" containing their name, the bootcamp date,
and the modules completed, rendered in **landscape** orientation (the conventional
certificate format) while the rest of the recap stays portrait. Ultimately a
certificate template should live under the plugin's `resources/` to drive the layout —
but that template is not yet available.

## Root cause

`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`:

- Orientation is hard-coded portrait at `:373`
  (`pdf = RecapPDF(orientation="P", …)`, in the `new_pdf()` helper `:372`); all page
  emitters call `pdf.add_page()` with no orientation argument (`_render_cover` `:407`,
  `_render_toc` `:507`, `_render_module_page` `:534`). fpdf2 supports per-page
  `add_page(orientation="L")`, but it is never used.
- Page sequence is cover → TOC → one page per module (`:384-397`); there is no
  certificate/capstone page.
- Name and date come from `recap.meta` (parsed from the recap Markdown preamble:
  `**Bootcamper:**`, `**Started:**`, `**Path:**`), rendered on the cover (`:448`);
  `modules_completed` is the parsed `recap.modules` list.
- No certificate template ships (`resources/` holds only `2026-sz-light.png` and
  `senzing-style-reference.pdf`).
- The stdlib fallback writer (`render_with_stdlib` `:687-916`) uses a fixed A4 portrait
  MediaBox `595×842` per page (`:695`) — no per-page orientation support.

**Invariant note:** touches **INV-048** (recap PDF always created, professional, the
four subsections — the certificate is additive and must not break `--check` or the
four-subsection guarantee), **INV-081** (brand tokens, render offline), **INV-066**
(robust fpdf2 with stdlib fallback — the landscape page needs a graceful stdlib story,
so the fallback writer's fixed portrait MediaBox must gain a per-page MediaBox), and
**INV-065** (the shipped example PDF would need re-rendering). No invariant currently
addresses a certificate or per-page orientation; a new one would be established.

## Proposed change

Add a Certificate of Completion as the recap's final page during graduation:

- Populate name, bootcamp date, and modules completed from `recap.meta` /
  `recap.modules` (with `config/bootcamp_progress.json` as a fallback source).
- Render that single page in **landscape** via fpdf2 `add_page(orientation="L")`, while
  all other pages remain portrait.
- Style the certificate from `brand_tokens` (INV-081) and render offline (no network).
- Extend the stdlib fallback writer to emit a per-page landscape MediaBox for that page
  so INV-066's fallback still produces the certificate.
- When a certificate template later ships under `resources/`, drive the certificate's
  layout/content from it instead of an ad-hoc design.
- Re-render the shipped example recap PDF (INV-065). Keep the four recap subsections
  intact (INV-048).
- Establish a new invariant for the certificate page and per-page orientation.

## Acceptance criteria

- [ ] The recap PDF ends with a Certificate of Completion page containing the bootcamper's name, the bootcamp date, and the modules completed.
- [ ] That single page is landscape; all other pages remain portrait — in both the fpdf2 renderer and the stdlib fallback (INV-066).
- [ ] The certificate uses `brand_tokens` and renders offline (INV-081); no network dependency.
- [ ] The four recap subsections and `--check` still pass (INV-048); the shipped example PDF is re-rendered (INV-065).
- [ ] If/when a `resources/` certificate template exists, the certificate layout is driven from it.
- [ ] `INVARIANTS.md` records the new certificate / per-page-orientation guarantee.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — add the certificate page; per-page landscape orientation (fpdf2 and stdlib fallback MediaBox `:687-916`).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — pass name/date/modules to the renderer if needed.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` — re-render (INV-065).
- `resources/` — future certificate template (out of scope until it ships).
- `specs/INVARIANTS.md` — new invariant for the certificate/orientation guarantee.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add a landscape 'Certificate of Completion' as the final recap page" (2026-07-22, Module Graduation — recap PDF generation)
- Priority: Medium
- Related specs: `specs/recap-pdf-professional-design.md`, `specs/recap-sections-name-based-and-complete.md`, `specs/refresh-example-recap.md`; INV-048, INV-081, INV-066, INV-065
