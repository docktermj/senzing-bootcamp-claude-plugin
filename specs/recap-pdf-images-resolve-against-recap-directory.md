# Resolve recap image paths against the recap file, and report the embedded-image count

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Graduation Step 1a instructs backfilling screenshots into `docs/bootcamp_recap.md` as `![alt](path)`
lines. Six captures were embedded with paths relative to the recap document — what every Markdown
renderer expects:

```markdown
![Results visualization — Entity Graph tab](visualizations/results_visualization-entity-graph.png)
```

The PDF reported success:

```text
PDF generated: docs\bootcamp_recap.pdf (renderer: fpdf2, rendered 46707 of 46973 source characters (99%))
```

**All six screenshots were missing.** Counting Image XObjects found only 2 — both 4167x1162, the
Senzing logo on the cover and the certificate:

```text
Image XObjects     : 2
declared widths    : [4167, 4167]
source PNGs        : 6 files, 1,035,596 bytes
```

Re-running the identical command with `docs/` as the working directory produced 8 Image XObjects
(2 logos + 6 screenshots at 1600x1200) and grew the PDF from 115,863 to 834,458 bytes.

There is **no path that satisfies both consumers**. `visualizations/...` is correct for the Markdown
and broken for the PDF; `docs/visualizations/...` is correct for the PDF and broken for the Markdown
(it resolves to `docs/docs/visualizations/...`). So a bootcamper following Step 1a exactly gets a
lossy PDF, and "fixing" the path breaks the Markdown recap instead.

The bootcamper's own screenshots are the most visual content in the keepsake. Losing them produced
no error, no warning, and a success line reporting 99% of source characters — because the characters
*did* render. Only counting image objects in the PDF reveals it.

## Root cause

**`plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:1845-1849` resolves a relative image path
against the process working directory, not the document:**

```python
p = Path(path)
if not p.is_absolute():
    p = Path.cwd() / p
if not p.is_file():
    return
```

The generator is invoked from the project root (graduation Step 1b runs
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/generate_recap_pdf.py"` with no `cd`), so
`visualizations/...` resolves to `<project>/visualizations/...`, which does not exist — the real
location is `<project>/docs/visualizations/...`. Every image hit `if not p.is_file(): return`.

**The silence is deliberate but over-applied.** `_render_image`'s docstring (`:1837-1842`) cites the
never-break-the-PDF rule (INV-048) as the reason a missing image is "skipped silently". INV-048
argues for not *raising*; it does not argue for being indistinguishable from having no images at all.
INV-111 already requires a bundled generator to say on stderr when it fell back to a lesser path —
a dropped image is exactly that class of event and is currently the one case that stays silent.

**The success line satisfies INV-110's letter while missing its intent.** INV-110 requires reporting
a content-retention figure so a generator cannot report success after dropping a material share of
its input. The figure is characters-only, and characters structurally cannot see a dropped image, so
losing ~1 MB of the bootcamper's own screenshots reports as 99% retained.

## Proposed change

1. **Resolve relative image paths against the input recap file's parent directory.** In
   `_render_image`, replace `Path.cwd()` with the directory of the file being rendered — the
   generator already knows it from `args.input` (`:2579`, `:2597`). This makes the Markdown-correct
   path also correct for the PDF, so Step 1a's instruction becomes satisfiable as written and no
   `cd` is required. Keep `Path.cwd()` as a secondary attempt so an already-working absolute or
   root-relative invocation does not regress.

2. **Keep the failure non-fatal but make it audible.** Write one line to stderr per skipped image,
   naming the path and the directories tried (`skipped image (not found): <path>`), and one line for
   an embed that raised. The render still proceeds and the PDF is still valid (INV-048); only the
   silence goes (INV-111).

3. **Report an embedded-image count in the success line** alongside the character figure, e.g.
   `rendered 46707 of 46973 source characters (99%), embedded 6 of 6 images`. The current line
   implies a completeness it does not verify (INV-110).

4. **Audit image targets in `--check`.** `--check` already validates section and subsection
   structure without rendering; extend it to report every `![](...)` target in the recap that does
   not resolve. Graduation runs `--check` before and after the render, so this surfaces the problem
   at the step that can still fix it.

## Acceptance criteria

- [ ] With `docs/bootcamp_recap.md` containing `![alt](visualizations/x.png)` and the file present
      at `docs/visualizations/x.png`, running the generator **from the project root** embeds the
      image; a count of unique image XObjects in the output rises by one per screenshot.
- [ ] The same recap renders identically when the generator is invoked from `docs/` or with an
      absolute `--input`, so the fix is not a swap of one working directory assumption for another.
- [ ] An unresolvable image path produces one stderr line naming the path and the directories tried,
      exit stays 0, and the PDF is still written and valid (INV-048, INV-111).
- [ ] The success line reports embedded-vs-referenced image counts, and a run that drops an image
      cannot report a line implying completeness (INV-110).
- [ ] `--check` reports unresolvable `![](...)` targets and still never writes a PDF.
- [ ] A remote URL is still never fetched (`:1843-1844`, INV-081's offline guarantee).
- [ ] `tests/test_recap_pdf_guard.py` still passes (INV-110), extended to cover the image-count
      reporting and the path resolution.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): path
      resolution goes through `pathlib` with no separator assumptions, and the recap is authored the
      same way whatever language the bootcamper chose.

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `_render_image()` (`:1836-1863`):
  resolve against the input file's parent and report skips; the success-line construction: add the
  embedded-image count; `--check` (`:2581-2585` and the `verify_recap` contract at `:470+`): audit
  image targets. `_render_image` needs the input path threaded to it, or the recap directory held on
  the render context.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1b: state that the recap's image paths
  are document-relative and that the generator resolves them that way, so no one "fixes" the
  Markdown to suit the PDF; add the embedded-image count to what the success line reports.
- `tests/test_recap_pdf_guard.py` — cover both outcomes above.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "recap PDF silently drops every screenshot —
  image paths resolve against CWD, not the recap file" (2026-07-28, Module Graduation;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`;
  `Upstream: not applicable`)
- Priority: High
- Related specs: `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111 — this
  extends both from characters to images),
  `specs/embed-every-captured-tab-in-tab-order.md` (INV-146 — every captured screenshot must reach
  the recap; this is where they stop reaching it),
  `specs/enforce-screenshot-embed-and-backfill.md`,
  `specs/artifact-level-verification-for-deliverables.md` (INV-129 — the caller-side check that
  would have caught this),
  `specs/windows-headless-browser-discovery-for-screenshots.md` (the other half of the same
  session's screenshot loss)

## Invariants introduced

- `INV-161` — A relative asset reference inside a generated deliverable's source document MUST be
  resolved against that document's own directory, never the process working directory (recorded in
  `specs/INVARIANTS.md`).
- `INV-162` — A generator that drops a referenced asset MUST report each drop on stderr and MUST
  report an embedded-of-referenced count alongside any content-retention figure; retention alone MUST
  NOT be presented as evidence of a complete artifact (recorded in `specs/INVARIANTS.md`).
