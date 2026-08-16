# The stdlib PDF writer substitutes `?` for 24 characters the fpdf2 path renders correctly, silently

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**INV-143 forbids exactly this**, in its own words: "A generator's character sanitization MUST
NOT substitute `?` for a character it cannot encode: every character a bootcamper-authored
deliverable can carry MUST map to an ASCII equivalent or be dropped deliberately." The stdlib
PDF writer does it for 24 characters, and says nothing.

Confirmed end to end 2026-07-31, recap generator with `fpdf2` shadowed so the fallback runs:

```text
source:   Precision came out ≥ 95% and recall ≈ 90%, with cost ≤ €500 per run. The
          vendor's Senzing™ license covers it, and throughput was effectively ∞ …
rendered: Precision came out ? 95% and recall ? 90%, with cost ? ?500 per run. The
          vendor's Senzing? license covers it, and throughput was effectively ? …

PDF generated: out.pdf (renderer: stdlib, rendered 619 of 655 source characters (95%))
```

Exit 0. A `PDF generated:` line. 95% retention. **Nothing on stderr.** Eight characters
replaced by `?` and every signal green — because `?` is one character replacing one character,
so the retention figure is structurally incapable of seeing it (the same blindness INV-193
names for a self-derived denominator).

**The divergence is exactly 24 of the 33 mapped characters.** `_UNICODE_MAP` (`:1133`) is the
authoritative table used by `_safe()`; `_pdf_escape()` (`:3046`) carries its own inline table of
**9** entries and falls back to `"?"`. The 9 that agree are precisely `_pdf_escape`'s 9. Measured
2026-07-31:

| Character | `_UNICODE_MAP` says | fpdf2 path | stdlib path |
|---|---|---|---|
| `≥` `≤` `≈` `≠` | `>=` `<=` `~` `!=` | correct | `?` |
| `€` `™` `∞` | `EUR` `(TM)` `infinity` | correct | `?` |
| `←` `↔` `⇒` `↑` `↓` | `<-` `<->` `=>` `^` `v` | correct | `?` |
| `✅` `✓` `⚠` | `[done]` `[x]` `!` | correct | `?` |
| `⛔` `🛑` `🎓` `🚀` `📄` `🏆` `​` `️` `‑` | dropped, deliberately | correct | `?` |

`dropped_character_warning()` returns `None` after the stdlib path, because `_pdf_escape` never
records into `_DROPPED_CHARACTERS` — so INV-111's fail-loudly requirement is unmet too. The
substitution is not merely wrong, it is unreportable.

**This is not an edge case.** INV-066 makes the stdlib writer the sanctioned fallback, and
`generate_discoveries_pdf.py`'s own docstring says the reporting Bootcamper "had none of
`pandoc`, `wkhtmltopdf`, `weasyprint`, `reportlab` or `fpdf2` installed, so the fallback is the
common case, not an edge case". `_pdf_escape` serves **both** generators
(`generate_recap_pdf.py:2702`, `:2748`, `:2889`; `generate_discoveries_pdf.py:817`), and commit
`b438994` has just widened the exposure: graduation Step 5b now renders
`docs/business_problem.md` and `docs/data_source_evaluation.md` — two more Bootcamper-authored
documents — through the same path.

The characters are not hypothetical. `_UNICODE_MAP`'s own comment records where they came from:
"Comparison, currency and spacing characters a bootcamper's own discoveries document carries but
the plugin's templates never emit — so scanning the templates could not find them. **Each
rendered as `?` until mapped.**" They were mapped for `_safe`. The stdlib writer never got the
fix.

**What is *not* affected, checked rather than assumed.** The Certificate of Completion's
recipient name is safe for a name the fonts cannot render at all: `:1722` tests
`_safe(name).strip()` and substitutes the placeholder when it folds to nothing, so 李明 and
Владимир reach the placeholder on both paths. That guard is intact. It does not help a name
mixing Latin-1 with a `_UNICODE_MAP`-only character, and it does nothing for body text, which is
where the 24 land.

## Root cause

**Two substitution tables, one authoritative and one not.** `_safe()` applies `_UNICODE_MAP`
(33 entries) and then `_fold_to_latin1()`, whose contract is explicit: characters that cannot be
folded are **dropped**, "which INV-143 permits, never encoded as `?`, which it forbids".
`_pdf_escape()` is the low-level PDF string escaper and carries a *duplicate* 9-entry map with a
`"?"` default — and only the fpdf2 call sites pre-normalize through `_safe`. The stdlib writer
calls `_pdf_escape` on raw text.

**Why it survived.** The character-safety work was aimed at a different failure. Both
`test_recap_pdf_font_safety.py` and `test_recap_measure_font_safety.py` exist to stop **fpdf2**
raising on an unencodable character — the first opens "No text path may hand *fpdf2's* Latin-1
core font a character it cannot encode", and the second treats `renderer: stdlib` as evidence
"something crashed". So the stdlib writer was modeled as the *symptom* of a defect, never as a
renderer whose own character handling could be wrong. No test calls `_pdf_escape`. One test
(`test_example_recap_sync.py:105`) has a helper that *folds `_pdf_escape`'s substitutions* "so
comparisons are fair" — accommodating the behavior rather than checking it.

That is also why INV-143's own words go unmet: it requires "the character inventory under test
MUST cover what generated **deliverables** carry" — and the inventory covers one of the two
renderers that produce them.

## Proposed change

1. **One table, not two.** Route `_pdf_escape` through the same authoritative sanitization as
   the fpdf2 path — either by calling `_safe()` at the top of `_pdf_escape`, or by having the
   stdlib writers sanitize before escaping. Then delete the inline 9-entry map; a second copy of
   a subset is the defect, and re-syncing two tables by hand is how it recurs.
2. **Keep `_pdf_escape`'s actual job intact.** It must still escape `\`, `(`, `)` and emit
   `\ooo` octal for 160-255. Only the substitution/fallback half changes. `_safe` guarantees
   Latin-1-encodable output, so the `"?"` branch becomes unreachable rather than merely unused.
3. **Make the residual fallback drop and record, never substitute.** If any character still
   reaches the default, drop it and register it in `_DROPPED_CHARACTERS` so
   `dropped_character_warning()` reports it (INV-111/INV-143). An unreachable branch that would
   silently print `?` is the thing to remove.
4. **Test the inventory across both renderers.** INV-143 asks for an inventory over generated
   deliverables: iterate **every** `_UNICODE_MAP` key through both the fpdf2 and stdlib paths and
   assert neither produces `?` — a loop, not a sample, so a character added to the map later
   cannot be added to only one path. Include an end-to-end stdlib render (shadow `fpdf2` on
   `PYTHONPATH`, as `test_recap_pdf_guard.py` already does) asserting the rendered text.
5. **Assert the warning fires on the stdlib path** for something genuinely unfoldable, so
   "silent" cannot come back.

⚠️ **Do not "fix" this by adding the missing 24 entries to `_pdf_escape`'s inline map.** That
restores parity today and re-creates the drift tomorrow, which is the root cause rather than the
symptom.

## Acceptance criteria

- [ ] No character in `_UNICODE_MAP` renders as `?` on **either** renderer — asserted by
      iterating the whole map, not a sample.
- [ ] `_pdf_escape` has no private substitution table; sanitization comes from the one
      authoritative source.
- [ ] `_pdf_escape` still escapes `\`, `(`, `)` and emits octal for 160-255 — a round-trip test
      on a Latin-1 string with all three metacharacters.
- [ ] A character that cannot be folded is **dropped and recorded**, and
      `dropped_character_warning()` reports it after a stdlib render (INV-111).
- [ ] An end-to-end stdlib render (fpdf2 shadowed) of a document containing `≥ ≈ ≤ € ™ ∞ ✅`
      shows their mapped forms and **zero** `?`.
- [ ] The certificate's existing placeholder guard for an unfoldable name still fires on both
      paths (`recap_certificate_name_unprintable` behavior unchanged).
- [ ] Both generators benefit — `generate_discoveries_pdf.py` imports `_pdf_escape`, so its
      stdlib path is asserted too, not assumed.
- [ ] The fpdf2 path is unchanged: `test_recap_pdf_font_safety.py`,
      `test_recap_measure_font_safety.py` and `test_example_recap_sync.py` all still pass. If
      that last one's `_pdf_escape`-folding helper becomes unnecessary, say so rather than
      leaving a helper that accommodates a fixed defect.
- [ ] MCP re-check: n/a — both generators are plugin-bundled and no Senzing tool is involved.
      Code claims verified 2026-07-31 at the lines quoted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `_pdf_escape` (3046), and the three stdlib call sites (2702, 2748, 2889).
- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py` — imports `_pdf_escape`; its stdlib writer (817) inherits the fix.
- `tests/test_recap_pdf_font_safety.py` or a new `tests/test_stdlib_writer_character_safety.py` — the both-renderers inventory.

## Source

- **Found during implementation, not reported by a Bootcamper.** Surfaced 2026-07-31 while
  implementing `render-any-bootcamp-document-as-a-styled-pdf`: extracting text from a
  stdlib-rendered PDF showed `≥` as `?`. Recorded in that spec's
  `## Deviations from this spec, and why (2026-07-31)` as observed, pre-existing and out of
  scope, deferred to this spec.
- Priority: **High.** It is a live INV-143 violation on a sanctioned output path, it is silent,
  and commit `b438994` has just added two more Bootcamper-authored documents to that path.
- MCP re-check: n/a (no Senzing fact).
- Upstream: not applicable — entirely plugin-side.
- Related specs: `specs/discoveries-pdf-real-tables-and-paragraph-spacing.md`, which
  established **INV-143** — this is the same defect on the renderer that fix did not reach;
  `specs/robust-fpdf2-install.md` (INV-066, which makes the stdlib writer a first-class path),
  `specs/render-any-bootcamp-document-as-a-styled-pdf.md` (where it was found, and which widened
  the exposure).

## Deviations from this spec, and why (2026-07-31)

Implemented as specified — one table, `_pdf_escape` reduced to PDF syntax, residual drops
recorded. Four differences worth recording:

1. **`_safe` is called at the writers' boundaries, not inside `_pdf_escape`.** The spec
   offered either. Putting it inside `_pdf_escape` would have been wrong: `generate_recap_pdf.py`
   measures width on raw text and escapes afterwards *on purpose* — its own comment explains
   that `_pdf_escape` turning `·` into `\267` would mis-center a line measured before escaping.
   Transliteration has the same hazard one step earlier and worse (`∞` → `infinity`, one
   character to eight), so sanitizing inside the escaper would desync every measured width and
   every wrap decision from what is actually drawn. Sanitization therefore happens **before**
   measurement and **before** wrapping: the certificate's `line()` and `wrap()` helpers, and
   both generators' `add()` / `add_wrapped()` token constructors.

2. **Two sanitization points per generator, deliberately, because they cover different
   routes.** `add()` covers direct calls (the H1 title, module labels); `add_wrapped()`
   sanitizes before `_wrap` because `_wrap` counts characters and transliteration changes the
   count. `_safe` is idempotent, so text passing through both is unaffected.

3. **`test_example_recap_sync.py`'s folding helper was NOT redundant — its attribution was
   wrong.** The spec asked me to say so if it became unnecessary. It did not: the
   substitutions still happen, in `_safe` rather than `_pdf_escape`. But it hardcoded 9 of the
   33 — the same duplicated-subset pattern just removed from the source — so it now derives
   from `_UNICODE_MAP`, and its docstring records the correction. Were the example recap ever
   to gain a `≥`, a 9-entry list there would have silently mis-compared.

4. **A weak test of my own, replaced.** `test_its_token_boundary_sanitizes` asserted the string
   `"_safe(text)"` appeared in `render_with_stdlib`'s source. That passed even with the `add()`
   boundary removed, because the string still occurred in `add_wrapped` — a guard that cannot
   fail. It is now behavioral: render a document whose *title* and *subtitle* carry symbols
   (the direct-`add` route) and assert the mapped forms appear with no `?`.

**On the mutation testing, since it is the evidence for everything above.** Three mutations
initially appeared to escape and did not: `_fold_to_latin1` and `_pdf_escape` both call
`_record_dropped_character(ch, s)` at the same indent, so a first-occurrence replace hit the
wrong function — which also explains why the `?`-fallback mutation failed a *certificate* test
rather than a `?` test. Re-run against unique anchors, all are caught. Two further mutations
(removing `add()`'s sanitization in each generator) genuinely escaped the first version of the
tests, for the reason in item 4; the direct-title-route tests were added and both now fail as
they should.

**One thing left unpinned, and named rather than glossed.** `add_wrapped`'s
sanitize-before-wrap ordering is a *layout* correctness measure — its effect is line width, not
which characters appear — and I did not find an assertion for it that would be robust against
ordinary font-metric variation. Reverting it changes no character, so no test here fails. The
character-safety guarantee is fully covered by `add()`; the wrap ordering rests on the reasoning
in item 1 and the comment at the call site.

## Invariants introduced

- None. This *restores* INV-143 on a renderer that never satisfied it, and adds nothing new:
  INV-143 (no `?` substitution), INV-111 (report what was dropped) and INV-066 (both renderers
  produce a valid deliverable) all already applied and are now asserted for both paths rather
  than one.
