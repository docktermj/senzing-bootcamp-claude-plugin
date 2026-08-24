# Make the recap PDF generator fail loudly instead of emitting a plausible, empty PDF

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scripts/generate_recap_pdf.py` accepts `--input` / `--output`, which suggests it can render any Markdown
file. It cannot: it parses `## {Module name}` sections and emits only the recap sub-sections.

Pointed at `docs/bootcamp_data_discoveries.md`, it printed per-section warnings, then
**`PDF generated: … (renderer: stdlib)` and exited 0**. The resulting 6-page, 14 KB PDF looked entirely
plausible and contained **none** of the findings — verified by extracting the text (3,947 characters, and
probes for "APM MEDICAL", "ABSOLUTE DENTAL", "AMH", "SECRETARY OF STATE" and "EFX_YREST" all absent).

Had the exit code and success message been trusted, an empty deliverable would have shipped.

Why it matters, in the reporter's words: "A success message plus a valid, plausibly-sized PDF is exactly the
shape of a failure nobody checks. Both the graduation recap and the discoveries document are terminal
deliverables — the artifacts the bootcamper keeps. Silent content loss there is the most expensive possible
place for it. The warnings *were* printed, but they were per-section noise ahead of a success line, which
reads as cosmetic rather than fatal."

## Root cause

**Confirmed: the render path validates structure *after* rendering and treats every problem as non-fatal.**

`generate_recap_pdf.py:1238-1248`:

```python
if ok:
    # Non-fatal content warning (never blocks; graduation is non-blocking).
    problems = verify_recap(recap)
    if problems:
        sys.stderr.write(
            "WARNING: recap PDF generated but some sections are incomplete:\n"
        )
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
    print(f"PDF generated: {out} (renderer: {used})")
    return 0
```

`verify_recap` (`:232-254`) already detects the fatal case — its first check is literally `if not
recap.modules: problems.append("recap contains no module ('## …') sections")`. The signal exists; it is
downgraded to a warning and then contradicted by a success line and `return 0`. The script's `--check` mode
(`:1221-1229`) *does* return 1 on the same problems — but `--check` does not render, so the render path never
benefits from it.

**One correction to the report.** The feedback states the stdlib fallback happened "because the
recap-structure validation failed." That is not supported by the code: `verify_recap` runs *after* rendering
and cannot influence renderer selection. `render_with_fpdf2` returns False in only two places —
`:387-388`, a **silent** `except Exception: return False` around `from fpdf import FPDF`, and `:439-441`,
which does write `fpdf2 render failed: {exc}` to stderr. Since no such message was reported, the actual cause
was almost certainly the import: `fpdf2` was installed into `data/temp/pdf-venv`, so a plain `python3`
invocation could not import it. **That is still a real defect** — the silent import failure is
indistinguishable from "fpdf2 not installed" and from "fpdf2 present but broken" — just not the one the
report named. The fix below addresses the real cause.

## Proposed change

1. **Fail loudly on structural mismatch.** If the input has no recognizable recap sections, exit non-zero
   with a clear message ("input does not look like a bootcamp recap; N of M sections had no recognized
   sub-sections"). **Never print `PDF generated:` after dropping most of the content.**
2. **Report a content-retention figure** — e.g. "rendered 3,947 of 41,000 source characters" — so truncation
   is visible without manually extracting text. Fail when retention falls below a stated threshold. This is
   the check that catches the *next* variant of this bug, not just this one.
3. **Say why `fpdf2` was unavailable.** Replace the silent `except Exception: return False` at `:387-388`
   with a message distinguishing "not installed" from "installed but failed to import" (including the
   interpreter path, so a venv mismatch is obvious). A renderer downgrade should never be inferred from
   silence.
4. **Either support generic Markdown or rename the flags.** `--input`/`--output` on a structure-specific tool
   invites exactly this misuse. If generic rendering is out of scope, document the required structure in the
   usage string and validate it **up front**, before rendering. Note that
   `specs/always-produce-data-discoveries-document.md` needs a generic Markdown renderer — so the two specs
   should decide this together: generalize this script, or ship a sibling renderer and make this one reject
   non-recap input.

**Preserve the non-blocking guarantee — this is the constraint that makes the fix subtle.** The
`# Non-fatal content warning (never blocks; graduation is non-blocking)` comment reflects a real design
requirement: a missing subsection in an otherwise-good recap must not block graduation, and INV-066 requires
a PDF to be produced with or without `fpdf2`. So separate the two failure classes:

- **Incomplete but recognizable** (a module missing a subsection) → warn, render, exit 0. Unchanged.
- **Unrecognizable, or catastrophic content loss** (no module sections, or retention below threshold) →
  fail, exit non-zero, and do **not** claim success. This case is not "an imperfect recap"; it is the wrong
  input, and rendering it produces a deliverable that is worse than no deliverable.

Callers must also change: `graduation/SKILL.md` treats PDF generation as non-blocking. It should keep
proceeding on the *warning* class, but on the *fail* class it must report the failure to the bootcamper
rather than announcing a PDF that is effectively empty. A silent success is what made this expensive.

Add to `tests/` a case asserting that non-recap Markdown input exits non-zero and does not print
`PDF generated:`, and one asserting that a valid-but-incomplete recap still exits 0 — the two classes must be
distinguishable by exit code, and a regression here is invisible by construction.

## Acceptance criteria

- [ ] Input with no recognizable `## {Module name}` recap sections exits non-zero with a message naming the
      mismatch, and does **not** print `PDF generated:`.
- [ ] The tool reports a content-retention figure and fails when retention falls below a stated threshold.
- [ ] A valid-but-incomplete recap still warns, renders, and exits 0 — the non-blocking guarantee is intact.
- [ ] An unavailable `fpdf2` produces a message distinguishing "not installed" from "import failed",
      including the interpreter path; a renderer downgrade is never silent.
- [ ] `--input`/`--output` either accept generic Markdown or the usage string documents the required
      structure and the tool validates it before rendering.
- [ ] `graduation/SKILL.md` reports the hard-failure class to the bootcamper instead of announcing a PDF.
- [ ] `tests/` covers both classes, asserting the differing exit codes and the absence of a false success
      message.
- [ ] INV-066 still holds: a valid recap renders a PDF with or without `fpdf2`, and INV-100's Certificate of
      Completion is still produced on both renderers.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): a Python
      maintenance script with no new dependency; the interpreter-path message must be meaningful on all three
      platforms.

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `main()` (lines ~1231-1251): split the failure
  classes, add retention reporting; `render_with_fpdf2` (lines ~384-388): report why the import failed;
  `verify_recap` (lines ~232-254): distinguish fatal from non-fatal problems; the module docstring/usage
  (lines ~8-28)
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the PDF-render step: handle the hard-failure class
- `tests/` — a new test module covering both classes

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "The bundled recap PDF generator silently emits an
  empty PDF for non-recap input" (2026-07-25, Graduation; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- Related specs: **`specs/always-produce-data-discoveries-document.md` (blocked on this — decide the generic
  vs. sibling-renderer question together)**, `specs/recap-pdf-professional-design.md`,
  `specs/robust-fpdf2-install.md`, `specs/certificate-name-fallback-at-graduation.md` (the other silent
  placeholder in this script), `specs/write-gate-tests.md` (the `tests/` harness pattern to follow)

## Invariants introduced

- `INV-110` — A bundled generator that produces a terminal bootcamper deliverable MUST NOT report success
  after dropping a material share of its input's content: it MUST audit the input before rendering, report a
  content-retention figure, and — on structural mismatch or retention below its stated minimum — write no
  output file, emit no success line, and exit non-zero. A recognizable-but-incomplete input stays
  non-blocking. (Recorded in `specs/INVARIANTS.md`.)
- `INV-111` — When a bundled generator falls back from its preferred renderer or an optional dependency to a
  lesser path, it MUST state on stderr which case occurred and why — distinguishing "not installed for this
  interpreter" (naming the interpreter) from "installed but unusable" — so a degraded render is never
  inferred from silence. (Recorded in `specs/INVARIANTS.md`.)

## Implementation notes

Two findings from implementing this, recorded because they affect other specs:

1. **This spec's root-cause paragraph overstates one branch.** `verify_recap`'s `if not recap.modules` check
   never fired on the reported input — the discoveries document *did* parse 3 `##` sections. The actual
   content-loss mechanism is `parse_recap` (`generate_recap_pdf.py:198-200`), which appends body lines only
   `if current_sub is not None`, so any line under a `##` but not under a recognized `###` is discarded. The
   proposed fix ("0 of N sections carry any recognized sub-section") targeted this correctly, so the
   implementation is unaffected.
2. **The generic-vs-sibling-renderer question was decided: sibling.** This generator now *rejects* non-recap
   input and documents its required structure, rather than becoming a general-purpose Markdown renderer.
   `specs/always-produce-data-discoveries-document.md` therefore needs its **own** renderer; its current
   "reuse the graduation generator" instruction will not work as written and should be updated when that
   spec is implemented.
