# INV-121 binds every bundled generator; only the discoveries generator's cursor discipline is guarded

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

INV-121 binds a **class**:

> A bundled generator that renders a bootcamper-facing deliverable MUST NOT depend on the ambient
> cursor position for full-width text: every full-width write MUST reset to the left margin first,
> via a shared helper or an explicit `new_x`, so no block kind can be added that renders off the
> page. … `tests/test_discoveries_pdf.py` enforces this and MUST pass.

Two bundled generators render a bootcamper-facing PDF: `generate_discoveries_pdf.py` and
`generate_recap_pdf.py` (plus `generate_document_pdf.py`, which delegates wholly to the first).
**Only the discoveries generator is guarded.** `tests/test_discoveries_pdf.py` is the sole test
mentioning cursor position at all, and it imports `generate_discoveries_pdf` only.

**The behaviour is correct in both** — this is a coverage gap, not a conformance defect, and it
should not be reported as the latter. `generate_recap_pdf.py` resets before every full-width write
using the same idiom the invariant permits (`pdf.set_x(pdf.l_margin)` / `set_xy(pdf.l_margin, …)`
at `:1558`, `:2278`, `:2413`, `:2419`, `:2457`, `:2461`, and `set_xy(pdf.l_margin, …)` throughout
the certificate and cover). Nothing renders off-page today.

**What the gap costs.** The recap generator is the larger of the two — 3,366 lines against 945 —
and it is the one that carries the certificate page, where INV-121's own failure mode is worst:
the certificate disables the auto page-break, so a write from an unreset cursor draws off-sheet
with no error, no effect on the content-retention figure, and a successful-looking render. INV-121
was written from exactly that defect in the *other* generator. A future block added to the recap
renderer that forgets the reset would ship silently — the class of defect INV-121 exists to make
impossible is currently impossible only in the file that already had it.

This is the same shape as INV-107 → INV-184, recorded 2026-07-30: INV-107 named two generators,
the property belonged to the pattern, and the third drifted out of scope unnoticed *while its own
comment claimed a test asserted it*. That one is now fixed and verified — `tests/test_brand_sync.py`
asserts all three inlined palettes. INV-121 is the same structure with the fix not yet applied.

## Root cause

`discoveries-pdf-offpage-blocks-and-list-spacing` (2026-07-26) found the off-page defect in
`generate_discoveries_pdf.py`, fixed it there, and wrote INV-121 as a class rule while naming the
test it had just written as the enforcement. The recap generator was not swept, because the
finding arrived from the discoveries side and the invariant's class wording was written after the
fix rather than before it.

`citations.py verify` cannot see this: INV-121 resolves, and `tests/test_discoveries_pdf.py`
exists and passes. `coverage_reports.py invariants` cannot see it either — INV-121 *is* cited by a
test, so it does not appear as uncited. The gap is that the citing test's scope is narrower than
the invariant's, which is only visible by reading what the test imports.

## Proposed change

1. **Extend the cursor-discipline assertion to `generate_recap_pdf.py`.** The check should be
   behavioural rather than a source scan where possible — render a document whose blocks follow one
   another and assert every drawn text run's x lies inside the page's text column, which is the
   verification standard INV-121 itself names ("Verification MUST be positional … not a
   text-extraction presence check").
2. **Make the guard derive its subject list rather than hardcoding two names**, so a third
   generator cannot drift out of scope the way `generate_discoveries_pdf.py` did out of INV-107's.
   `tests/test_bundled_script_and_production_paths.py:48` already demonstrates the idiom in this
   repo — `BUNDLED_SCRIPTS = sorted(p.name for p in SCRIPTS.glob("*.py"))` — with a not-vacuous
   guard so an empty glob fails loudly.
3. **Update INV-121's enforcement clause** to name the test that covers the class, as a dated
   in-place clarification. Do **not** rewrite the requirement; only the "enforced by" pointer
   changes, exactly as INV-184 did for INV-107.

⚠️ **`generate_document_pdf.py` needs no separate guard** and should be explicitly excluded with
the reason: it is a 49-line wrapper that imports `generate_discoveries_pdf.main` and parses no
arguments of its own, so it has no independent drawing code. A guard that pretended to cover it
would be asserting something it does not test.

⚠️ **Do not treat a passing render as evidence.** Both generators produce valid PDFs today; the
off-page defect INV-121 records produced a valid PDF too, at exit 0 with a 100%-retention figure.
Only a positional check distinguishes them.

## Acceptance criteria

- [ ] A test asserts cursor discipline for `generate_recap_pdf.py`, positionally — every drawn
      text run's x inside the page's text column — not by scanning source for `set_x`.
- [ ] The certificate page is included in what that test renders, since it is the page with the
      auto page-break disabled and therefore the worst case.
- [ ] The guard derives the generators it covers rather than hardcoding them, with a not-vacuous
      assertion so an empty or drifted list fails loudly.
- [ ] `generate_document_pdf.py` is excluded with the reason stated in the test, not silently.
- [ ] Negative-controlled: remove one `set_x(pdf.l_margin)` before a full-width write in
      `generate_recap_pdf.py`, confirm the new test fails, revert. The mutation is confirmed to
      have landed before the result is believed.
- [ ] INV-121's enforcement clause names the test covering both generators, as a dated in-place
      clarification with no meaning change; the requirement itself is unchanged and nothing is
      deleted or renumbered.
- [ ] `tests/test_discoveries_pdf.py` still passes unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md). The
      positional check needs `fpdf2`; where it is absent the test **skips** with a named reason
      rather than passing (INV-163), since the stdlib fallback draws differently.

## Affected files

- `tests/` — the extended positional guard (new file, or an added class in
  `tests/test_recap_pdf_certificate.py`, which already renders the certificate).
- `specs/INVARIANTS.md` — INV-121's enforcement clause only.

## Source

- **Found by `production-readiness-audit`, 2026-07-31** — the first run of that skill, via Step 7
  class 3 (a guard narrower than the invariant it claims to enforce), by listing the 16 invariants
  that name a test file and checking each named test's scope against its invariant's.
- Priority: **Low.** No live defect: both generators honour the rule today, verified by reading
  every full-width write path in each. The value is that the class INV-121 exists to close is
  currently closed in one file of two, in the smaller one, and the unguarded file is the one with
  the fixed-layout certificate page.
- MCP re-check: **n/a (no Senzing fact).** Cursor position in a bundled PDF generator is
  plugin-internal; no MCP tool owns it and none was called.
- Upstream: not applicable.
- Related specs: `specs/discoveries-pdf-offpage-blocks-and-list-spacing.md` (INV-121's source).
  INV-184 — the same class-drift shape, already fixed for the brand palette and re-verified during
  this audit — has no spec file: it was recorded directly by the `deep-dive-audit-2026-07-30`
  ledger entry in `specs/IMPLEMENTED.md`, which is where its reasoning lives.

## Deviations from this spec, and why (2026-07-31)

**Criterion 1 is satisfied on one write path, not on every full-width write — disclosed rather
than ticked broadly.** The spec asked for a positional assertion of cursor discipline in
`generate_recap_pdf.py`. `tests/test_recap_pdf_text_column.py` provides it and is
negative-controlled: forcing the cursor to the right margin immediately before the module-prose
writer (`generate_recap_pdf.py:2605`) fails the assertion with the intended message.

But the fixture reaches **one** of the generator's full-width write paths. Injecting the same defect
before the code-block writer (`:2459`) and the code-block rule (`:2462`) **escaped**, so those paths
are unguarded, as are the cover, the table of contents, image alt text, and the stdlib fallback. The
guard's docstring and INV-121's new note both say so. A guard whose scope is overstated is the exact
defect this spec exists to fix, so claiming "every full-width write" here would have reproduced it.

**Getting to that answer took distinguishing a mis-targeted mutation from an escaped one, four
times.** The first negative control removed all seven `pdf.set_x(pdf.l_margin)` calls in the
generator, one at a time — **all seven escaped**, which looked like a broken guard. They were not on
any path the fixture exercises. Injecting into `add_wrapped` escaped too: that name at `:2834` is a
nested function inside the **stdlib fallback**, not the fpdf2 renderer under test. Only injecting at
the real fpdf2 prose writer produced a catch. Every one of those escapes was my mutation aiming at
the wrong code, and each was indistinguishable in the loop's output from a guard that does not work
— which is why the injection had to be repeated at a known-correct site before the guard could be
believed.

**Criterion 2 is satisfied concretely:** the fixture's render includes the certificate page — three
runs on it (`Certificate of Completion`, the presented-to line, the cover card title) — and the
x-range check spans it. The certificate is landscape (INV-100) at 841 pt wide against the body's
595 pt, so a single page-width bound would have false-failed; the text-column assertion is scoped to
the marked body runs and the certificate is covered by the negative-x check plus the existing
`TheFixedPageCannotBeOverrun` in `tests/test_recap_pdf_certificate.py`.

**Criterion 3 is satisfied by derivation** (`pdf_generators()` globs `generate_*_pdf.py`) with a
not-vacuous floor of two, and **criterion 4** excludes `generate_document_pdf.py` explicitly, with a
test asserting it still delegates — so if it ever grows drawing code of its own, the exclusion stops
being safe and the suite says so.
