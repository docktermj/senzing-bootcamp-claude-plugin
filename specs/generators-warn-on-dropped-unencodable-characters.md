# The PDF generators drop non-Latin-1 body characters silently — `_safe()`'s "drops, warns" contract is implemented only for the certificate name

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`docs/bootcamp_data_discoveries.md` carried literal Cyrillic organization names (e.g.
`Акционерное общество "Газпром-Медиа Холдинг"`) in prose and inside a fenced diagram, plus Unicode
box-drawing connectors (`│`, `▼`). Rendered to PDF, all of it **silently vanished**: valid PDF,
exit 0, a high `content retained` figure, and no warning of any kind. The loss showed up only on
visual inspection of the rasterized page.

Reproduced against the working tree, 2026-07-29, with a minimal six-section probe document:

```text
$ python3 generate_discoveries_pdf.py --input disc_probe.md --output disc_probe.pdf
PDF generated: disc_probe.pdf (renderer: fpdf2, content retained: 96%)
EXIT=0
```

Source line:

```text
The network centres on Акционерное общество "Газпром-Медиа Холдинг" and its affiliates.
```

Extracted from the rendered PDF:

```text
The network centres on "- " and its affiliates.
```

The fenced diagram lost its `│` and `▼` connectors and its Cyrillic line entirely; only
`[GLEIF]` survived. **Nothing was written to stderr.** `content retained: 96%` is not a
safeguard here: retention is computed over *parsed source characters* before `_safe()` runs at
render time, so a drop that happens during rendering cannot move the figure.

This is real content loss in a keepsake the bootcamper is meant to share, and it passes every
automated check the plugin has — exactly the class of defect INV-143 exists to govern. It is also
produced in Module 7, before graduation's retrospective verification step runs.

## Root cause

The drop itself is **correct and deliberate**. `generate_recap_pdf.py:959-988` (`_fold_to_latin1`)
drops non-Latin-script characters rather than substituting `?`, which is precisely what INV-143
requires, and its docstring states the intended contract:

> "Characters from a non-Latin script (CJK, Cyrillic, Arabic, Hebrew, Greek, Devanagari, Thai)
> are **dropped**, which INV-143 permits, never encoded as `?`, which it forbids. … So the
> generator **drops, warns**, and INV-113's pinned question asks the one person who knows."

**The warn half is implemented for exactly one field.** `generate_recap_pdf.py:2958` warns when
the *bootcamper name* is unprintable (`recap_certificate_name_unprintable` →
`WARNING: the bootcamper name "…" contains …`). For body content — prose, table cells, fenced
code blocks — `_safe()` (`generate_recap_pdf.py:991-1010`) drops and returns, and no caller
warns. `generate_discoveries_pdf.py` imports `_safe` from the recap generator
(`generate_discoveries_pdf.py:74`), so **both** generators inherit the silent-drop behavior on
every body string: `_safe` is called at `generate_discoveries_pdf.py:434, 443, 501-502, 601, 611,
618, 644, 649, 663` and at the recap generator's equivalents, none of which reports a loss.

So the guarantee INV-143 was written to provide — never silently wrong on the page — holds for
the identity field and not for the document body.

## Proposed change

Close the warn half of the contract, in the shared sanitisation path so both generators get it:

1. **Make `_safe()` report what it dropped.** Have the fold path record the characters it
   discarded (and, for the caller's benefit, enough context to locate them) rather than
   discarding silently. Keep `_safe`'s signature usable by existing callers — e.g. accumulate
   into a module-level collector the generators drain before exit, or return the drop set through
   a sibling helper that the render loop consults. Do **not** change the drop policy: dropping
   stays correct, and `?` stays forbidden (INV-143).
2. **Warn once per run, on stderr, naming what was lost.** After rendering, if any character was
   dropped from body content, write a single `WARNING:` line reporting the count, the distinct
   characters (or their Unicode names/scripts, since the characters themselves may not survive
   the terminal either), and at least one location — the section heading or the first affected
   line — so the author can find and fix the passage. One aggregated warning, not one per
   character: a Cyrillic-heavy document would otherwise emit thousands.
3. **Keep it non-blocking.** Warn and render, exit 0 — consistent with the generators' existing
   "incomplete but recognizable" tier (`generate_discoveries_pdf.py:31-38`) and with INV-048 /
   INV-052 / INV-066 (a verification step never blocks graduation). Silent loss is the defect;
   refusing to render is not the fix.
4. **Tell the author what to do about it**, in the warning text and in the module guidance that
   produces these documents: prefer each entity's verified Latin-script name or alias — already
   present in loaded multi-source sanctions/registry data — over its non-Latin primary name,
   especially inside fenced/monospace blocks, and use ASCII connectors (`|`, `v`) in ASCII
   diagrams. Route the guidance to wherever the discoveries document is authored so the author
   sees it before rendering, not only after.

## Acceptance criteria

- [ ] Rendering a document containing non-Latin-1 body characters (Cyrillic prose, `│`/`▼`
      connectors) emits a `WARNING:` on stderr naming the count, the distinct dropped
      characters or their scripts, and at least one location — while still writing the PDF and
      exiting 0.
- [ ] The warning fires for **both** `generate_recap_pdf.py` and `generate_discoveries_pdf.py`,
      including for text inside fenced code blocks and table cells, not only for the
      bootcamper name.
- [ ] A document with only Latin-1-encodable content emits **no** such warning (no false
      positives on ordinary runs).
- [ ] No character is ever rendered as `?`, and the drop policy is unchanged (INV-143 still
      holds); the `content retained` figure and exit code semantics are unchanged.
- [ ] A test asserts the warning on a non-Latin-1 body input and its absence on an ASCII input,
      for both generators.
- [ ] Guidance where the discoveries document is authored tells the author to prefer verified
      Latin-script names/aliases and ASCII diagram connectors, so the warning is preventable
      rather than only diagnostic.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      warning is emitted by the bundled Python generators regardless of the bootcamper's chosen
      language, and must not depend on the terminal being able to display the dropped characters
      (report Unicode names/scripts, not only raw glyphs, so a Windows console cannot turn the
      warning itself into mojibake — see `ground-rules.md` → "Windows and PowerShell").

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `_fold_to_latin1` /
  `_safe` (~lines 959-1010) to record drops; the `main`/render path (~line 2946 onward, beside
  the existing name warning) to emit the aggregated warning.
- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py` — drain and emit the same
  warning (it imports `_safe` at line 74; the stderr-warning path is ~lines 807-813).
- `tests/test_recap_pdf_font_safety.py` / `tests/test_discoveries_pdf.py` — assert the warning
  fires and does not false-positive.
- The Module 7 guidance that authors `bootcamp_data_discoveries.md` — prefer Latin-script
  names/aliases and ASCII diagram connectors.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "bootcamp_data_discoveries.md content with Cyrillic org names corrupts silently in the PDF" (2026-07-29, Module Query, Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact — the Latin-1 limitation is the core PDF fonts' and the
  drop is the plugin's own sanitisation). Server **1.32.2** was current at triage time,
  2026-07-29. Reproduced directly against the working-tree generator instead.
- Upstream: not applicable. The entry is routed `both`, but its non-plugin half is the fpdf2
  core-font character range, not Senzing or the MCP server, so there is nothing to report to
  Senzing. The content half (Cyrillic names authored into the deliverable) was fixed in-session
  by rewriting the affected passages to verified English names/aliases and ASCII connectors.
- Related specs: `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (the sibling
  guarantee for *dropped sections*; this spec extends "fail loudly" to *dropped characters*),
  `specs/certificate-name-fallback-at-graduation.md` and
  `specs/certificate-name-must-reach-the-generator.md` (INV-143's existing warn, on the identity
  field only), `specs/artifact-level-verification-for-deliverables.md`
