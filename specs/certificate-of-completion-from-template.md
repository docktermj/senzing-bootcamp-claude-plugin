# Lay the Certificate of Completion out from the shipped Senzing template

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The recap PDF's final page is a Certificate of Completion (INV-100). It was designed
ad hoc, because the certificate template `specs/landscape-certificate-of-completion.md`
anticipated ("Ultimately a certificate template should live under the plugin's
`resources/` to drive the layout — but that template is not yet available") did not exist
when that spec was implemented. Its last unmet acceptance criterion is still open:

> - [ ] If/when a `resources/` certificate template exists, the certificate layout is
>   driven from it.

That template now exists: `resources/certificate-of-completion.pdf`, a maintainer asset
alongside `resources/senzing-style-reference.pdf`. Rendered, it is a landscape certificate
with a warm ember gradient band down the left edge, a white card bordered by an ember rule,
the Senzing wordmark, a `SENZING BOOTCAMP` eyebrow, an ember headline, a tagline over a
short ember rule, a letterspaced `THIS CERTIFICATE IS PROUDLY PRESENTED TO`, the
recipient's name, a three-line citation, and a `DATE COMPLETED` / `ISSUED BY` signature row
flanking an award seal.

The shipped certificate looks nothing like it: a navy-and-ember double border around
centred Helvetica, an italic footer, and a `Modules completed` label — visibly the weakest
page of the recap, and the one page a bootcamper detaches, prints and shows to other
people.

## Root cause

`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`:

- `_render_certificate` hard-codes its own design: two nested `rect` borders, five centred
  `cell` calls at fixed `y` offsets, and two bottom-anchored italic attribution lines.
- `_stdlib_certificate_stream` (INV-066's fallback) hard-codes a *second*, different design
  — a navy border plus a stack of centred lines — with its own magic offsets. The two
  renderers share only the strings, so nothing keeps their layouts in step beyond
  INV-126's version line.
- Neither renderer draws the template's band, card, seal or signature blocks, and the only
  brand asset available (`senzing_logo_light.png`) is the *light* wordmark, invisible on a
  white card except for its ember "z".
- The module list is `multi_cell`'d with the auto page-break off and no cap, so a long
  list prints over whatever is beneath it.

## Proposed change

Lay both renderers out from one set of geometry constants measured off the template:

- Millimetre constants on landscape A4 for the band, card, baselines, signature blocks and
  seal, shared by the fpdf2 renderer and the stdlib fallback, so the fallback becomes a
  plainer *rendering* of one design rather than a second design (INV-066/INV-126).
- Palette strictly from `brand_tokens` (INV-081): the band mirrors the brand's own
  `EMBER_GRAD_START`/`EMBER_GRAD_END` pair rather than hexes sampled off the template, and
  the muted label grey is *derived* from body ink the way `TABLE_HEAD_FILL` is derived —
  no new token, nothing invented.
- Repaint the shipped light wordmark's white letterforms in dark ink at render time, so
  one asset serves both the dark cover band and the white certificate card and they cannot
  drift; keep the ember "z"; fall back to drawn text when Pillow or the asset is absent.
- Take the citation's module count from the recap. The template reads "all 10 modules"; a
  bootcamper who completed four has not completed ten, and the template's description of
  the whole arc must attach to *the bootcamp* rather than to what was completed.
- Keep the modules completed on the page (INV-100), fitted so the block can never reach
  the seal or the signature row: narrow measure first, then the card's full width, then
  type size, and only then truncation.
- Real letterspacing (`Tc` / `set_char_spacing`), never spaces inserted between glyphs — a
  certificate is searched and copied out of.
- Shrink an over-long recipient name to fit the card instead of running it off the page.
- Re-render the shipped example recap PDF (INV-065).

## Acceptance criteria

- [ ] The certificate reproduces the template's layout: gradient band, bordered white card, wordmark, eyebrow, headline, tagline + rule, presented-to line, name, citation, award seal, and the `DATE COMPLETED` / `ISSUED BY` signature blocks.
- [ ] Both renderers lay it out from the same constants; every shared line sits at the same height in each (INV-066/INV-126), verified positionally.
- [ ] The wordmark prints as dark letterforms with the ember "z" on the white card, keeps its transparency, and degrades to drawn text when the asset or Pillow is unavailable (INV-048).
- [ ] The citation states the number of modules actually completed, and the modules completed are named on the page (INV-100).
- [ ] A module list long enough to overflow is fitted, not printed over the seal and signature row; nothing is drawn below the card.
- [ ] Letterspaced lines still extract as words, and the recipient's name extracts as a name.
- [ ] Palette and typography come from `brand_tokens`; the certificate renders offline (INV-081) and `_FALLBACK_RGB` stays in sync (INV-107).
- [ ] `--check`, the four subsections (INV-048) and the shipped example pair (INV-065) all still hold; the example PDF is re-rendered.
- [ ] Verified by **rasterizing** the page, not by text extraction (INV-129).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — certificate geometry constants, `_render_certificate`, `_stdlib_certificate_stream`, wordmark recolor, derived palette entries.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` — re-render (INV-065).
- `tests/test_recap_pdf_certificate.py` — new: template-layout, renderer-agreement, overflow and letterspacing tests.
- `tests/test_recap_pdf_guard.py` — page-aware off-page bound (the portrait bound was never right for a landscape page).
- `specs/INVARIANTS.md` — the certificate-follows-the-template guarantee.

## Source

- Maintainer request (2026-07-28): "the last page of the generated `bootcamp_recap.pdf` contains a 'Certificate of Completion'. Improve that page by using the template seen in `resources/certificate-of-completion.pdf`."
- Priority: Medium
- Related specs: `landscape-certificate-of-completion.md` (discharges its deferred template criterion), `recap-pdf-certificate-version-and-list-spacing.md`, `certificate-name-fallback-at-graduation.md`, `recap-pdf-professional-design.md`; INV-100, INV-126, INV-113, INV-081, INV-066, INV-065, INV-107

## Invariants introduced

- `INV-156` — The Certificate of Completion is laid out from `resources/certificate-of-completion.pdf` via one shared set of geometry constants both renderers read, with the citation counting only the modules actually completed (recorded in `specs/INVARIANTS.md`).
