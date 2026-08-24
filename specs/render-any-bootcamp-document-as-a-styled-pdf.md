# A generic styled-Markdown renderer is usable for one file, because its required-section list is a constant

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

A Bootcamper asked that graduation also produce PDFs of `docs/business_problem.md` and
`docs/data_source_evaluation.md`, styled to match the two PDFs the bootcamp already renders.

**The renderer is already general-purpose.** `generate_discoveries_pdf.py` takes `--input`
and `--output`, and its layout engine — cover page, section styling, tables, typography —
contains nothing specific to the discoveries document.

**One module-level constant blocks it.** Confirmed 2026-07-31:

```text
generate_discoveries_pdf.py:142  REQUIRED_SECTIONS = [ … six discoveries headings … ]
generate_discoveries_pdf.py:400      for required in REQUIRED_SECTIONS
generate_discoveries_pdf.py:403      present = len(REQUIRED_SECTIONS) - len(missing)
generate_discoveries_pdf.py:412      f"(looked for: {', '.join(REQUIRED_SECTIONS)})"
```

`audit_discoveries` treats "none of these headings present" as fatal, and the CLI exposes only
`--input`, `--output` and `--check`, so it cannot be relaxed from outside. Both documents are
refused:

```text
Refusing to render docs/business_problem.md: none of the required findings sections
is present (looked for: headline numbers, merges and match keys, review queue,
why and how, relationship networks, what was not found)
No PDF was written. Fix the document and re-run - an empty deliverable is worse than none.
```

**The guard is right and must stay.** It is what stops the script being pointed at an
unrelated Markdown file and silently emitting a near-empty PDF (INV-110). The defect is that
it is expressed as *one document's section names* rather than as a parameter, which makes an
otherwise generic renderer usable for exactly one file.

**Why these two documents.** The bootcamp already treats "rendered as a styled PDF" as the
signal that a document is a keepsake rather than a working file, and both qualify:
`business_problem.md` is the document a stakeholder is most likely to be shown; and
`data_source_evaluation.md` carries the engine-verified readiness findings and the
unmapped-field audit with its rejected-field rationale — the reference a team returns to when
someone asks "why wasn't field X mapped?".

## Root cause

The script was written for one document, and its content guard was written from that
document's outline. Generality arrived in the layout engine and never reached the guard, so
the one line that is document-specific is also the one line that decides whether the script
runs at all.

## Proposed change

1. **Make the required-section list a parameter.** Add `--require-sections "a;b;c"`
   (semicolon-separated, since section names contain commas) and/or `--no-section-check`,
   **defaulting to the current `REQUIRED_SECTIONS`** so the existing discoveries call is
   byte-for-byte unchanged.
2. **Keep every other guard.** The 60% content-retention floor is the real protection against
   rendering the wrong file (INV-110); both documents score ~99% against it. Relaxing the
   section check must not relax retention.
3. **Add a graduation step** after Step 5a and before the revisit bundle: render
   `docs/business_problem.pdf` and `docs/data_source_evaluation.pdf`, verify each by
   extracting text as Step 1b requires (INV-129), and announce them in the closing summary.
   **Non-blocking** like every other graduation step — warn and continue if either fails
   (INV-048).
4. **Make it findable.** Either rename the script to say what it is — a general
   styled-Markdown-to-PDF renderer — or add a thin `generate_document_pdf.py` wrapper, so the
   next person looking for "how do I render a doc in the house style" finds it. A renamed or
   wrapped entry point must resolve via `${CLAUDE_PLUGIN_ROOT}` (INV-185).
5. **Keep the em-dash caution** the discoveries deliverable carries. Both documents happen to
   pass the Latin-1 constraint the PDF fonts impose, but a future document may not, and the
   new step must not become a route that bypasses INV-143/INV-159's character handling.

## Acceptance criteria

- [ ] The required-section list is settable from the CLI; omitting it reproduces today's
      behavior exactly for the discoveries document.
- [ ] The content-retention floor still applies and is not weakened by the section flag.
- [ ] Graduation renders both PDFs after Step 5a, verifies each by text extraction, announces
      them, and continues on failure without blocking.
- [ ] Both PDFs are byte-verified as non-trivial — page count and extracted text probed
      positively, not inferred from exit 0 (INV-129).
- [ ] The renderer is discoverable under a name or wrapper that says what it does, resolved
      via `${CLAUDE_PLUGIN_ROOT}` (INV-185).
- [ ] The character-safety path is unchanged: a document with characters outside the font is
      still handled per INV-143/INV-159, not silently degraded.
- [ ] A test renders a document carrying **none** of the discoveries headings but passing
      retention, with `--require-sections` supplied, and asserts a real PDF results — and a
      companion test asserts that omitting the flag still refuses it.
- [ ] MCP re-check: n/a — `generate_discoveries_pdf.py` and the graduation skill are both
      plugin-bundled; no Senzing tool is involved.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py` — `REQUIRED_SECTIONS` (142), `audit_discoveries` (~400-412), the CLI.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the new render step after Step 5a, and the closing summary.
- `tests/test_discoveries_pdf.py` — the two flag tests.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "graduation should render
  business_problem.md and data_source_evaluation.md as styled PDFs - the renderer already can,
  but a hardcoded section list refuses them" (2026-07-31, Module: Graduation;
  `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). Code claims and both refusal messages verified
  2026-07-31 at the lines quoted.
- Upstream: not applicable.
- Related specs: `specs/discoveries-pdf-real-tables-and-paragraph-spacing.md` and
  `specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` (the layout engine this reuses),
  `specs/space-every-recap-bullet-list-by-default.md` (check whether the sibling generator
  carries the same opt-in spacing shape).

## Deviations from this spec, and why (2026-07-31)

All five proposed changes shipped. Five differences, one of which is a correction to the
spec's own premise:

1. **⚠️ "Its layout engine … contains nothing specific to the discoveries document" is
   false.** The cover subtitle read `"What Senzing found in your data"` — hardcoded in
   **both** renderers (`:476` fpdf2, `:732` stdlib) — plus a `"Data Discoveries"` title
   fallback. Rendering `business_problem.md` therefore put a discoveries line at the top of
   the document the spec itself calls "the one a stakeholder is most likely to be shown",
   and it is the first thing that reader sees. Found by extracting text from a rendered
   PDF rather than by reading the layout code, which is the only way it would have
   surfaced. Fixed with a `--subtitle` flag carried on the parsed document (so neither
   renderer needed a new signature and the two cannot drift), defaulting to the existing
   string. **Without this, item 3 of this spec would have shipped a misleading keepsake.**

2. **`--no-section-check` as well as `--require-sections`.** The spec offered "and/or"; both
   shipped. `--require-sections` is what graduation uses, because naming a document's own
   headings keeps a real guard — `--no-section-check` leaves retention as the only
   structural check, and the guidance says so.

3. **`--require-sections ""` is an error, not a silent skip.** Not in the spec. An empty
   value quietly meaning "no check" would be a footgun in exactly the direction INV-110
   cares about, so it exits 1 and points at `--no-section-check`.

4. **The `--check` line counts against the effective list.** It reported `n/6` from
   `len(REQUIRED_SECTIONS)`; with `--require-sections` naming two sections, `n/6` is a lie.
   `DiscoveriesAudit` gained `sections_present` / `sections_expected` so the denominator
   comes from what was actually expected.

5. **A wrapper, not a rename.** The spec offered either. `generate_discoveries_pdf.py` is
   named in the module-07 skill, the specs and the tests, so a rename breaks every one of
   those addresses for a cosmetic gain. `generate_document_pdf.py` delegates and is asserted
   to contain **no** argument parsing, defaults, or `REQUIRED_SECTIONS` reference, so it
   cannot drift from what it wraps.

**Three user-visible strings changed**, each pinned by a test that had to change with it:
`"none of the required findings sections is present"` → `"…required sections…"`,
`"n/6 findings sections present"` → `"…expected sections present"`, and
`"missing findings sections:"` → `"missing sections:"`. All three said *findings*, which is
wrong for every document but one now that the list is a parameter.

**One test of mine was too weak and was rewritten.** The first
`test_the_retention_floor_is_not_weakened_by_either_flag` accepted either outcome and was
nearly tautological. It now asserts against a document that genuinely fails retention (55%
against the 60% floor) and requires refusal, with `content retention` named on stderr, under
**both** flags.

**Observed and deliberately left alone** (out of scope, pre-existing, affects the
discoveries document equally): the two renderers transliterate out-of-font characters
differently. fpdf2 renders `≥` as `>=`; the stdlib fallback renders it as `?`. Both are
silent — `dropped_character_warning()` fires for neither. That is an INV-143/INV-159 question
worth its own spec; this change neither introduces nor worsens it, and
`test_character_handling_is_unchanged_on_the_new_path` pins the fpdf2 behavior so a future
refactor cannot route the new path around `_safe` unnoticed.

**Criterion 4 is verified for a synthetic document, not for a real bootcamp's.** Page count
and text extraction were both probed positively here against a `business_problem`-shaped
fixture (1 page, 977 extracted characters, content present). The criterion's real subject is
a Bootcamper's own two documents, which this environment does not have; graduation's Step 5b
now requires both probes per file, and the test asserts that requirement is stated.

## Invariants introduced

- None. Turning a constant into a parameter and adding a delegating wrapper adds no standing
  constraint beyond what these tests already enforce; INV-110 (the retention floor), INV-129
  (verify the artifact), INV-185 (`${CLAUDE_PLUGIN_ROOT}`) and INV-066 (both renderers) all
  already applied and are asserted here rather than extended.
