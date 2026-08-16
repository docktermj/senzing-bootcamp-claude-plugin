# Verify generated deliverables at the artifact level, not by exit code

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Across five deliverable refinements in one session, the same failure pattern recurred **four
times**: a step reported success while producing wrong, missing, or unreadable output.

| What reported success | What was actually produced |
|---|---|
| `capture_screenshots.py` exit 0, 3 files written | 3 images of the same tab; 2 captions invented |
| Certificate footer text extracted correctly by `pdftotext` | glyphs sliced in half by the page border |
| `PDF generated: … content retained: 98%`, exit 0 | the entire match-key table drawn off the page |
| Valid, paginated bullet lists | item boundaries invisible; long-label bodies in a 1/3-width ribbon |

None raised an error. **Two reached a signed keepsake** — the recap PDF, explicitly framed as
something to revisit and share with a team — before the bootcamper caught them by eye.

The plugin already has strong guards against a *recognizably* broken artifact: INV-110 audits input
before rendering and refuses to ship on structural mismatch or low content retention; INV-111
forbids a silent fallback. Both are necessary and both were satisfied here. Neither can catch these
four, because in every case the generator's own model of its work was correct — the content *was*
parsed, the text *was* in the content stream, the files *were* written. What was wrong was the
rendered artifact.

The retention percentage specifically **cannot** catch an off-page table: the text is present in the
PDF content stream, merely positioned outside the page box.

The generalizable conclusion, which the two consolidated feedback entries both state as the part
most worth institutionalizing: **artifact-producing steps need artifact-level verification.**
Rasterize the page, open the image, count the objects, grep the extracted text for content you know
must be there. Exit codes and retention percentages are necessary but demonstrably insufficient.

A fifth, related gap: graduation's CommonMark normalization pass runs over `docs/*.md` including the
recap source, immediately before the PDF renders. A cosmetic pass has no business losing prose, but
nothing verifies that it did not.

## Root cause

Not a single code defect — a missing verification discipline, plus one specific unguarded pass.

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md:129-157` treats a
  zero exit from the capture helper as success and asks the agent to "review the shots" without
  requiring the images be opened.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:340-360` treats the generator's success line
  and the optional `--check` as the verification of the recap PDF. `--check` validates the
  **Markdown source's** section structure, not the rendered pages.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:284-288` — the normalization pass is
  described as "one best-effort CommonMark pass over `docs/*.md`", correctly scoped to top-level
  `docs/*.md` so `docs/feedback/` is never touched (INV-015). But there is **no content-preservation
  check**: a normalization that dropped prose would produce a valid, prettier, shorter recap and
  nothing would notice — and it runs immediately before the render, so the loss would ship.
- No invariant states the general rule. INV-110 and INV-111 govern what a *generator* must report;
  nothing governs what the *caller* must confirm about the artifact it just produced.

## Proposed change

**1. Establish the rule as an invariant.**

A step that produces a bootcamper-facing deliverable (PDF, PNG, HTML artifact) MUST verify the
**artifact**, not only the exit status and any self-reported metric. Verification must inspect the
rendered output for content the step knows must be present. This complements INV-110/INV-111 rather
than replacing them: the generator still fails loudly, and the caller still checks the result.

**2. Give graduation a concrete, dependency-optional verification checklist.**

Add to `graduation/SKILL.md`'s render step, each best-effort and non-blocking (INV-048 — graduation
never blocks on verification, it warns):

- **Rasterize before trusting text extraction.** `pdftoppm -r 100 -png` the certificate page and any
  page whose layout changed, and look at it. Text extraction reported the certificate's version
  string present and correct while the glyphs were visually cut in half by the border — only
  rasterizing showed it.
- **Positive presence probes.** `pdftotext` the output and grep for content known to be in the
  source (e.g. a match-key table's header). A count of **0** is the finding; a retention percentage
  cannot produce it.
- **Count unique image XObjects**, not `/Subtype /Image` occurrences. The naive regex reported 12 for
  10 images, because references are counted more than once.
- **Open every captured PNG before writing its caption.** This is what exposed the invented captions
  (see `specs/per-tab-screenshot-capture-and-grounded-captions.md`, which makes the caption rule
  binding).
- **Re-run `--check --expect-modules "…"` after every render**, semicolon-separated (two module
  display names contain commas).
- **When replacing text, confirm both that the new string is present and the old one is gone** —
  decompress the content streams rather than assuming the replacement worked.

Note the toolchain these assume, so a capture path is not designed around absent tools: fpdf2,
headless Chrome, and poppler (`pdftoppm`/`pdftotext`/`pdfinfo`) were present; Playwright, Selenium,
and PyMuPDF were not. Everything above was done with plain headless Chrome and poppler. Each check
degrades silently when its tool is missing (INV-052/INV-066).

**3. Guard the CommonMark normalization pass against content loss.**

Before/after, fingerprint each file's **non-whitespace** content; if the normalized file would
shrink, restore the original and warn on stderr. A cosmetic pass must not be able to lose prose.
Keep the existing scope guarantee explicit: glob top-level `docs/*.md` only, never recurse, so
`docs/feedback/` cannot be touched (INV-015).

The verified reference implementation is a 141-line script
(`src/scripts/normalize_docs_markdown.py`) covering MD022/MD031/MD032 blank lines, MD040 fence
languages, and `**Label:**` colon spacing, with exactly those two safety properties. Bundling it as
`plugins/senzing-bootcamp/scripts/normalize_docs_markdown.py` is preferable to leaving the pass as
prose instructions — a deterministic script with a content guard is testable, and the guard is the
point.

**4. Point the module-completion instruction at the same discipline** so the rule is not
graduation-only: whenever a module produces an artifact, the check is on the artifact.

## Acceptance criteria

- [ ] `specs/INVARIANTS.md` carries a new invariant requiring artifact-level verification of
      bootcamper-facing deliverables, with provenance, appended per the file's own rules.
- [ ] `graduation/SKILL.md`'s render step lists the concrete checks (rasterize, positive presence
      probe, unique-XObject count, open every PNG, re-run `--check`, confirm replacements both ways),
      each explicitly best-effort and non-blocking.
- [ ] Every check degrades silently and warns rather than blocking when its tool (poppler, headless
      Chrome) is unavailable — graduation still completes and still writes the PDF (INV-048,
      INV-052/INV-066).
- [ ] The CommonMark normalization pass restores the original file and warns on stderr when
      normalization would reduce non-whitespace content.
- [ ] The normalization pass globs top-level `docs/*.md` only and never recurses;
      `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` is provably untouched (INV-015).
- [ ] A test drives the normalizer with a case where a naive transform would drop a line, and
      asserts the original content survives.
- [ ] The instruction to verify the artifact appears in `module-completion.md` as well as
      `graduation/SKILL.md`, so it is not graduation-specific.
- [ ] No verification step becomes a 👉 question or a blocking gate (INV-012 — this is agent-facing
      apparatus, not bootcamper-facing output).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      checks must not assume a POSIX-only tool invocation or a Python-only deliverable.

## Affected files

- `specs/INVARIANTS.md` — append the artifact-level-verification invariant.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — add the verification checklist to the
  render step (`:340-360`); add the content-preservation requirement to the normalization pass
  (`:284-288`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — apply the rule at
  every artifact-producing module step (`:97`, `:129-157`).
- `plugins/senzing-bootcamp/scripts/normalize_docs_markdown.py` — new: guarded CommonMark pass with
  the non-whitespace content fingerprint and the non-recursive glob.
- `tests/` — a new test for the normalizer's content-preservation guard and glob scope.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Positive feedback — the improved recap PDF,
  with the full implementation record for porting upstream" (2026-07-26, Module Graduation;
  `Source: bootcamper-reported`) — its "Why it matters", item 7, and "Verification practices that
  actually caught things".
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Positive feedback — the improved discoveries
  PDF, with the full implementation record for porting upstream" (2026-07-26, Module Query,
  Visualize and Discover (deliverable); `Source: bootcamper-reported`) — its "Why it matters" table
  and "Verification practices that found the defects".
- Priority: High
- Related specs: `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111 — the
  generator-side half of this), `specs/defer-commonmark-to-graduation.md` (the normalization pass
  being guarded), `specs/per-tab-screenshot-capture-and-grounded-captions.md` (the caption-from-image
  rule), `specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` and
  `specs/recap-pdf-certificate-version-and-list-spacing.md` (the four defects that motivated it),
  `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — the same
  don't-render-the-unverified principle applied to SDK responses).

## Invariants introduced

- `INV-129` — A step producing a bootcamper-facing deliverable MUST verify the rendered artifact,
  not only the exit status and any self-reported metric; and a cosmetic pass over a deliverable's
  source MUST prove it preserved content, restoring the original on any reduction (recorded in
  `specs/INVARIANTS.md`).
