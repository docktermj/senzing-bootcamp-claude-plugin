# Produce a professionally designed recap PDF (reach the fpdf2 renderer; port the proven redesign)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At graduation, `docs/bootcamp_recap.pdf` — the crown-jewel trophy — rendered via the
**plain stdlib fallback** because `fpdf2` was not installed. The content was correct
and complete (all 7 modules, four subsections each) but the visual styling was plain
and unappealing. `INV-048` requires the trophy to be "very professional looking
(iterate to make it look professional)"; the plain fallback does not meet that bar. A
follow-up create/visualize/critique/improve loop (run in a project-local
`generate_recap_pdf_v2.py`) produced a polished result the bootcamper called
"excellent" and documented concrete fixes worth porting back into the bundled
generator.

## Root cause

`scripts/generate_recap_pdf.py` has two renderers: a designed `render_with_fpdf2`
(`:279` — cover page, per-module color header bands, a `_safe()` Latin-1 sanitizer)
and a plainer stdlib fallback `render_with_stdlib` (`:467`). `main()` (`:729-733`)
uses fpdf2 when importable, else the stdlib fallback. When `fpdf2` is absent — as
here — the plain fallback runs, and the graduation skill treats a missing fpdf2 as
acceptable ("a plainer stdlib-rendered one otherwise … never a reason to skip",
`graduation/SKILL.md:67-69`). So the plain PDF is the *documented* behavior when
fpdf2 is not installed, not a crash. The existing fpdf2 renderer is already
reasonably designed but is never reached without fpdf2; it also lacks a couple of
polish elements the redesign added (a table of contents, per-page page numbers) and
carries a latent bottom-anchored-content blank-page risk (`:357`, the cover footer at
`set_y(-24)` under the `auto_page_break` margin of 18).

## Proposed change

1. **Reach the professional renderer (primary fix).** At graduation Step 1b, when
   `fpdf2` is not importable, **offer to install it** (`pip install fpdf2`, a small
   pure-Python package) before rendering so the designed renderer is used. On decline
   or install failure, fall back to stdlib as today — `INV-048` guarantees a valid PDF
   is always produced. Keep the whole step non-blocking / warns-and-continues.
2. **Port the proven fpdf2 polish/bug-fixes** (from the "redesign — successful
   outcome" feedback) into `render_with_fpdf2`, adding only what it lacks:
   - a **table of contents** built with a **manual dry-run page-numbering pass**
     (render the module pages once into a throwaway PDF to record real page numbers,
     then render the final PDF with those static numbers) rather than
     `insert_toc_placeholder`/`start_section`, whose internal 2-pass render produced
     ghost/duplicate text;
   - a **per-page footer with page numbers** via the `footer()` callback, and moving
     any **bottom-anchored content into `footer()`** so it never triggers an
     auto-page-break blank page (this also hardens the existing cover footer at
     `:357`).
   - Reuse the existing `_safe()` sanitizer and keep bullets Latin-1-safe (both
     already present). The Journal already renders as inline bold-prefix lines, so the
     redesign's fixed-width-column gap fix is **not** needed here.
3. **Verify visually during implementation (`INV-048` "iterate").** Use a
   render-to-PNG inspection (e.g. `pymupdf`) to confirm no heading overlaps, no
   ghost/duplicate text, correct TOC page numbers, and no spurious blank pages — the
   loop that took the redesign from 22 buggy pages to 16 clean ones. This is a
   maintainer/dev verification of the ported design; it MUST NOT add a bootcamper
   runtime dependency (pymupdf stays out of the shipped render path).

## Acceptance criteria

- [ ] At graduation, when `fpdf2` is missing, the bootcamper is offered an install so the designed renderer runs; declining or a failed install still yields a valid PDF via the stdlib fallback (`INV-048`).
- [ ] The fpdf2 renderer produces a table of contents with correct page numbers (built via the dry-run pass, not `insert_toc_placeholder`), per-page page numbers, and no ghost text or spurious blank pages.
- [ ] All four required subsections still render for every completed module (`INV-048`), and `generate_recap_pdf.py --check` still passes.
- [ ] During implementation a render-to-PNG inspection confirms no overlaps/ghosting/blank pages and correct TOC numbering; `pymupdf` is not required at bootcamper runtime.
- [ ] `generate_recap_pdf.py` stays python3-run with `fpdf2` optional and the stdlib fallback intact; no non-python runtime is required, and it holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — port the TOC (dry-run page numbering), the `footer()` page numbers, and the bottom-anchored/blank-page hardening into `render_with_fpdf2`.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1b: offer to install `fpdf2` when missing before rendering; keep the stdlib fallback and the non-blocking posture; note the render-to-PNG visual check.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Recap PDF styling is plain/unappealing" (Medium) and "Recap PDF redesign — successful outcome" (Low) (2026-07-16, Graduation).
- Priority: Medium.
- Related specs: `recap-durability.md` (recap content/checkpoint), `defer-commonmark-to-graduation.md` (recap Markdown normalization before render). Upholds `INV-048` (professional trophy PDF); introduces no new invariant.
