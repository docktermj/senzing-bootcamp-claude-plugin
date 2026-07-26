# Put the plugin version on the certificate and space the recap PDF's bullet lists

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two bootcamper requests against `docs/bootcamp_recap.pdf`, plus one adjacent finding from the
same session. All three concern the recap PDF's keepsake pages.

**1. The Certificate of Completion does not name the plugin version.** The certificate page
carries the bootcamper's name, the completion date, the modules completed, and a "Senzing
Bootcamp" footer line — but not the plugin version that produced the run. The certificate is the
one page most likely to be detached from the rest of the recap: shared, printed, or attached to
something on its own. Without the version it is not self-describing — there is no way to tell
which version of the bootcamp produced it, which matters as the module set and content evolve
between releases.

**2. Bullet lists run together.** Under "Information Shared", "Actions Taken", and "What you
accomplished:", consecutive bullets render with no vertical separation. Because those bullets are
often long enough to wrap onto two or three lines, item boundaries become invisible and the
reader cannot tell where one ends and the next begins. These three lists are the substance of the
recap — what was taught, what was done, what was achieved per module — and they are also its
longest bullets, so the most valuable content is the hardest to read.

**3. A bare lowercase handle passed the certificate-name quality gate.** The auto-detected `name`
was `docktermj`. It is not a system account and is **not identical to the OS username**, so it
passes the letter of the INV-113 unusable list — but it is plainly a handle, not a person's
display name, and the certificate is the one place a wrong value is permanently and prominently
visible. It was queried once and persisted as a real name, but only because the assistant noticed.

Both bootcamper requests were implemented and verified in a project-local copy of the generator
(`src/scripts/generate_recap_pdf_custom.py`) and the bootcamper confirmed the result looks great.
That implementation record is the reference for this spec.

## Root cause

**1.** `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:835-866` — `_cert_fields()`
extracts only `(name, date, module labels)` from `recap.meta`. `_render_certificate()` (`:884`,
fpdf2) and `_stdlib_certificate_stream()` (`:1139`, fallback) consume only those three, so the
recap header's `**Plugin version:**` row — which graduation already stamps
(`graduation/SKILL.md:236-241`) and which `_partition_meta()` classifies as an identity row
(`:679-687`) — reaches the **cover page only** and never the certificate face.

Relatedly, `_partition_meta()`'s docstring (`:682-684`) claims identity rows "(bootcamper, dates,
language, path, plugin version) drive the cover card **and the certificate**", which overstates
what the certificate actually renders. The docstring describes the intended behavior; the code
never implemented it.

**2.** `generate_recap_pdf.py:1036-1037` — `_render_subsection()` loops over the subsection's
lines calling `_render_line()` for each, and `_render_line()` ends every bullet with
`pdf.multi_cell(remaining, 5.5, …)` (`:1129`) with **no trailing gap**. Wrapped continuation lines
therefore sit at exactly the same 5.5 mm spacing as the gap between two separate bullets, which is
what makes the items blend. `_stdlib_subsection()` (`:1275-1297`) has the same shape.

**3.** `plugins/senzing-bootcamp/skills/graduation/SKILL.md:136-141` leads with the correct
governing test — "clearly not a person's display name" — but then enumerates the operative cases,
and the handle case is qualified into uselessness:

> … or a bare lowercase token **identical to the OS username**.

A bare lowercase single-token handle is a handle whether or not it happens to match the OS
username. The enumeration reads as the operative list, so `docktermj` passed.

## Proposed change

**1. Render the plugin version on the certificate face.**

- Add `_cert_plugin_version(recap)` reading the `Plugin version` meta row, returning `""` when it
  is absent — **omit, never print a placeholder**. An unknown version must not become
  "v(unknown)" on a certificate.
- Render `Senzing Bootcamp Claude plugin v<version>` beneath the existing "Senzing Bootcamp"
  line, in **both** `_render_certificate` and `_stdlib_certificate_stream`, so the two renderers
  do not drift (the pairing INV-111 exists to protect).
- ⚠️ **Layout constraint, carried over from the verified implementation.** The certificate's inner
  ember border sits at `y = h - 14` (`generate_recap_pdf.py:906` — `pdf.rect(14, 14, w - 28,
  h - 28)`). A footer line placed at `h - 17` is **clipped by it**. The two attribution lines need
  to sit at roughly `h - 28` and `h - 22`; the existing "Senzing Bootcamp" line is currently at
  `h - 22` (`:948`), so it moves up to `h - 28` and the version line takes `h - 22`.

  This was only visible by **rasterizing** the page. `pdftotext` reported the version string
  present and correct while the glyphs were visually cut in half. Verify by rasterizing, not by
  extracting text — see `specs/artifact-level-verification-for-deliverables.md`.
- Fix the `_partition_meta()` docstring so it describes what the code does.

**2. Space consecutive list items.**

- `_SPACED_SUBSECTIONS = ("information shared", "actions taken")`, compared through the existing
  `_normalize_heading()` (`:170`) so the "Action Taken" singular variant is covered too (INV-048
  names it singular; every implementation surface uses the plural —
  `specs/reconcile-action-taken-wording.md`).
- `_SPACED_LABELS = ("what you accomplished",)` with a `_block_label()` helper, so that **within**
  "End-of-Module Summary" only the accomplishments list is spaced while "Files produced" — a short
  reference list of one-line paths — stays tight.
- Emit a 2.4 mm gap after a bullet **only when the next non-blank line is also a bullet**
  (`_next_nonblank_is_bullet()`), so the gap falls strictly *between* items and never trails the
  last one, where the subsection's own `pdf.ln(2)` already applies.
- Mirror the same logic in `_stdlib_subsection()` at 3 pt so the two rendering paths do not drift.

  **Two deliberate exclusions, to preserve:**

  - **"Questions & Responses" is not spaced.** Its content is Q/R pairs with the response rendered
    as an indented sub-bullet under its question. Spacing every bullet there would separate each
    response from the question it answers and read *worse*.
  - **"Files produced" is not spaced**, being a short list of paths.

  Verified cost: the recap grew from 27 to 28 pages, with the certificate, all embedded
  screenshots, and `--check` subsection validation intact.

**3. Broaden the certificate-name test to its governing form.**

In `graduation/SKILL.md:136-141`, drop the "identical to the OS username" qualifier from the
handle case and present the enumerated cases as **examples of** the governing test, not as the
test itself: treat the name as unusable when it is *clearly not a person's display name*, with a
bare single-token lowercase handle (e.g. `docktermj`) called out as an example regardless of
whether it matches the OS username. Keep the existing conservatism intact — "a plausible real name
must **never** trigger the question" (INV-006) — since the cost of asking someone their name after
correctly detecting it is its own defect. INV-113 already states the governing test, so this
aligns the guidance with the invariant rather than changing it.

## Acceptance criteria

- [ ] The Certificate of Completion page shows `Senzing Bootcamp Claude plugin v<version>`, taken
      from the recap header's `Plugin version` meta row.
- [ ] When no `Plugin version` row exists, the line is **omitted** — no placeholder text on the
      certificate.
- [ ] Both the fpdf2 renderer and the stdlib fallback render the version line identically in
      content and position.
- [ ] **Rasterizing** the certificate page confirms both attribution lines are fully visible and
      not clipped by the inner ember border at `y = h - 14`; text extraction alone is not accepted
      as proof.
- [ ] Bullets in "Information Shared", "Actions Taken" / "Action Taken", and the "What you
      accomplished:" block are visually separated, with the gap strictly between items and none
      after the last.
- [ ] "Questions & Responses" and "Files produced" are **not** spaced; a rasterized page confirms
      each response still reads as attached to its question.
- [ ] Both renderers space the same lists; a stdlib-fallback render shows the same item boundaries.
- [ ] `generate_recap_pdf.py --check --expect-modules "<semicolon-separated names>"` still passes,
      and the content-retention guard (INV-110) still reports its figure and exits 0.
- [ ] All previously embedded screenshots and the certificate are still present after the change
      (counted as **unique image XObjects**, not raw `/Subtype /Image` occurrences).
- [ ] `tests/test_recap_pdf_guard.py` passes; new tests cover the version line's presence,
      its absence when the meta row is missing, and the spaced/unspaced subsection split.
- [ ] A bare lowercase single-token handle triggers the INV-113 name question even when it differs
      from the OS username; a plausible real name still never triggers it.
- [ ] `_partition_meta()`'s docstring matches the code.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — add `_cert_plugin_version()`; render
  it in `_render_certificate` (`:884-952`) and `_stdlib_certificate_stream` (`:1139-1175`) with the
  `h - 28` / `h - 22` positions; add `_SPACED_SUBSECTIONS`, `_SPACED_LABELS`, `_block_label()`,
  `_next_nonblank_is_bullet()` and the inter-item gap to `_render_subsection`/`_render_line`
  (`:1015-1129`) and `_stdlib_subsection` (`:1275-1297`); fix the `_partition_meta` docstring
  (`:682-684`).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — broaden the certificate-name test
  (`:136-141`).
- `tests/test_recap_pdf_guard.py` — cover the certificate version line and the list spacing.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` — re-render so the shipped
  example matches the new layout (`specs/example-recap-reference.md`,
  `tests/test_example_recap_sync.py`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Show the Senzing Bootcamp Claude plugin
  version on the Certificate of Completion" (2026-07-26, Module Graduation;
  `Source: bootcamper-reported`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add blank-line spacing between list items in
  the recap PDF's Information Shared, Actions Taken, and What you accomplished lists" (2026-07-26,
  Module Graduation; `Source: bootcamper-reported`)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Positive feedback — the improved recap PDF,
  with the full implementation record for porting upstream" (2026-07-26, Module Graduation;
  `Source: bootcamper-reported`) — items 3, 4 and 5 of its port list.
- Priority: Medium
- Related specs: `specs/landscape-certificate-of-completion.md` (INV-100 — created the
  certificate), `specs/certificate-name-fallback-at-graduation.md` (INV-113 — the name gate this
  broadens), `specs/show-plugin-version-and-record-environment.md` (stamps the version into the
  recap header), `specs/recap-pdf-professional-design.md`,
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111),
  `specs/reconcile-action-taken-wording.md`, `specs/example-recap-reference.md`,
  `specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` (the sibling generator; carries the
  shared long-bold-label fix that also lands in `_render_line`),
  `specs/artifact-level-verification-for-deliverables.md`.
