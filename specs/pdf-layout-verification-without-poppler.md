# Graduation's PDF layout verification assumes poppler — on Windows it silently does not run

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Graduation Step 1b requires verifying the rendered artifact rather than the exit code (INV-129), and
specifies two checks that text extraction cannot substitute for:

- `pdftoppm -r 100 -png` the certificate page and **look at the image** — "only the raster shows the
  glyphs cut in half" (`SKILL.md:475-478`);
- `pdfimages -list` for an honest image count, because counting `/Subtype /Image` overcounts
  (`:483-484`).

On the reporting Windows workstation only **`pdftotext`** was present. `pdftoppm`, `pdfinfo` and
`pdfimages` were all absent. The skill says to probe for a tool and skip the check when it is missing,
which is what happened — so nothing broke. But it means the two checks specifically designed to catch
the failures text extraction *cannot* catch — border-clipped glyphs, content positioned outside the
page box — **did not run at all**, and the image count fell back to the method the skill explicitly
warns is inaccurate.

The recap PDF was therefore verified by content only: 11/11 text probes, cross-checked with
`pdftotext` at 47,357 characters across 27 pages. **Its visual layout is unverified**, and the closing
announcement did not say so.

Two things make it worth filing despite degrading safely. The toolchain note at `:498-501` says the
field machine "had `fpdf2`, headless Chrome, and poppler (`pdftoppm` / `pdftotext` / `pdfinfo` /
`pdfimages`)" — a Linux/macOS assumption presented as the baseline. And on Windows the strongest
verification steps are the ones most likely to be skipped, so the keepsake most likely to carry a
layout defect is the one nobody can check.

This also compounded a real loss in the same session: the recap PDF silently dropped all six of the
bootcamper's screenshots, and the only clue was an implausibly small file size. `pdfimages -list`
would have shown 2 images where 8 were expected — the check that was skipped is the one that would
have caught it.

## Root cause

**`plugins/senzing-bootcamp/skills/graduation/SKILL.md:475-501` names Unix tools as the way to
perform the checks, with no Windows-available alternative and no requirement to report a skip.**

- `:475-478` and `:483-484` name `pdftoppm` and `pdfimages` specifically. Both ship with poppler,
  which is standard on Linux and macOS and **not** present on Windows by default.
- `:430-434` softens this correctly for rasterization ("`pymupdf` also works where it happens to be
  installed. Neither is required: every check degrades silently when its tool is absent") — but
  "degrades silently" is the defect: INV-129 requires the check to be best-effort and non-blocking,
  which it is, and INV-111 requires a *generator* to announce a fallback on stderr, but nothing
  requires the *verification apparatus* to announce which checks it could not run.
- `:498-501` documents the field toolchain as fact rather than as one platform's baseline, so a
  Windows run has no signal that it is operating with a reduced check set.

**The constraint that shapes the fix:** INV-129 states that artifact verification "MUST NOT install a
tool to satisfy itself", and `:501` restates it ("never install one to satisfy a verification step").
So the feedback's first suggestion — `scoop install poppler` as a one-liner — **conflicts with an
invariant** and is not adopted here. The feedback's own alternative is invariant-compatible and is
adopted instead: `fpdf2` already pulls in **Pillow**, so when the project-local venv was created for
the renderer, Pillow is *already importable* and an image inventory needs no new install. (`pypdfium2`
would be a new install and is therefore out.) The feedback's third suggestion — report which checks
were skipped — is compatible with everything and is the most valuable part.

## Proposed change

1. **Report what was not verified.** The strongest and cheapest fix: when a verification check is
   skipped for a missing tool, say so — and have the closing announcement state which checks did not
   run, so "verified" never overstates what was confirmed. A layout defect nobody could check for is
   acceptable; a keepsake described as verified when its layout was never inspected is not. This is
   INV-111's fail-loudly discipline applied to the verification apparatus rather than the generator.

2. **Use the dependency that is already there.** Where the project-local venv exists with `fpdf2`,
   Pillow is importable in that same interpreter. Prefer it for the image inventory — opening the
   embedded images gives an honest count and their dimensions, which is what `pdfimages -list` was
   for — before falling back to the `/Subtype /Image` regex the skill warns is inaccurate. State the
   Pillow route in Step 1b so it is reached on any platform, not discovered per-session. Do **not**
   instruct installing poppler, `pypdfium2`, or anything else to satisfy a check (INV-129).

3. **Reframe the toolchain note (`:498-501`)** as platform-conditional rather than as the baseline:
   poppler is typically present on Linux and macOS and typically **absent on Windows**, so on Windows
   the rasterization and image-count checks will usually be skipped and must be reported as skipped.
   Keep the existing point that nothing here is designed around a heavy dependency.

4. **Rank the checks by what only they can catch,** so a reduced set is spent well: the positive
   `pdftotext` content probe (available on the reporting machine, and the only check that catches
   content outside the page box) and the image inventory run wherever possible; the page raster is the
   one genuinely tool-gated check, and its absence is the thing to announce.

## Acceptance criteria

- [ ] A verification check skipped for a missing tool emits a line naming the check and the missing
      tool, and the graduation closing announcement states which verification checks did not run.
- [ ] "Verified" is never asserted for a check that was skipped; a run with only `pdftotext` available
      reports content verified and layout unverified.
- [ ] The image inventory uses Pillow from the existing `fpdf2` venv when importable, falls back to
      `pdfimages -list` where poppler exists, and only then to the `/Subtype /Image` regex — with the
      regex path labeled as the inaccurate method it is.
- [ ] No verification step installs, or instructs installing, any tool — including poppler (INV-129,
      `SKILL.md:501`).
- [ ] Step 1b's toolchain note states that poppler is typically absent on Windows and what that means
      for the check set.
- [ ] Every check remains best-effort and non-blocking; no missing tool blocks graduation
      (INV-048, INV-052/INV-066), and none of this becomes bootcamper-facing 👉 output (INV-012).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the check
      set adapts to what is present on each platform and reports the difference, and the recap PDF is
      generated the same way whatever language the bootcamper chose.

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the rasterization bullet (`:475-478`), the
  image-count bullet (`:483-484`), the rasterization aside (`:430-434`), and the toolchain note
  (`:498-501`): the Pillow route, the skip-reporting requirement, and the platform framing. Plus the
  closing announcement: state the skipped checks.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — if the image inventory is implemented as
  a reusable check, it belongs alongside the generator's existing `--check` mode rather than as
  per-session ad hoc code.
- `tests/` — assert Step 1b names a poppler-free image-inventory route and requires skipped checks to
  be reported.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "graduation's PDF verification assumes a full
  poppler install; Windows had only pdftotext" (2026-07-28, Module Graduation;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`;
  `Upstream: not applicable`)
- Priority: Low
- Related specs: `specs/artifact-level-verification-for-deliverables.md` (INV-129 — the verification
  contract this operates under, including its no-install rule),
  `specs/recap-pdf-images-resolve-against-recap-directory.md` (**the loss this skipped check would
  have caught** — implement together if possible),
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111),
  `specs/robust-fpdf2-install.md` (INV-066 — the venv whose Pillow this reuses),
  `specs/windows-headless-browser-discovery-for-screenshots.md` (the sibling Unix-toolchain
  assumption)

## Invariants introduced

- `INV-163` — A verification check that cannot run for a missing tool MUST be recorded as skipped and
  named in the closing message; an artifact MUST NOT be described as verified for a check that did not
  execute, and where a check's tool is absent on a supported platform the guidance MUST offer a route
  needing no new dependency (recorded in `specs/INVARIANTS.md`).
