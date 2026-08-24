# PR #7 review: batched minor fixes (silent palette fallback, serial chip verification, sequential-capture contract, repo-wide mojibake sweep)

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

The PR #7 code review surfaced a cluster of small items alongside one real correctness bug (split
out into `specs/search-attribute-fallback-survives-a-failed-attempt.md`). Each item below was
re-checked against the code on 2026-07-30 and is genuine; the review's remaining findings were
checked and rejected, recorded under "Evaluated, no change" so the next audit does not re-raise
them.

1. **`generate_recap_pdf.py` falls back to the inlined palette in silence** —
   `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:831-853`. The `brand_tokens` import is
   wrapped in a bare `except Exception:` that assigns the nine fallback colors and writes
   **nothing** to stderr. INV-111 requires a generator that drops to a lesser path to say on
   stderr which case occurred, distinguishing "not importable" from "present but unusable", so a
   degraded render is never inferred from silence. The sibling generator does exactly that:
   `generate_discoveries_pdf.py:116-130` splits `ModuleNotFoundError` (naming the directory it
   looked in, because a project-local copy of the script without `brand_tokens.py` beside it is
   easy to create by accident) from any other exception, and cites INV-111 for the split. The
   recap PDF is the Bootcamper's keepsake and the higher-stakes of the two artifacts, and it is
   the one that reports nothing.

2. **Same file, the palette fallback is nine hand-written assignment lines** — the review's DRY
   finding. `_FALLBACK_RGB` is already a single named constant, so INV-184's literal requirement
   ("a single named constant rather than repeating the literals per code path") is met and this is
   not a drift surface today. It becomes one under item 1: splitting the handler into two `except`
   branches would duplicate the nine assignments unless they are first factored into a
   `_use_fallback_palette()` helper, which is precisely the shape
   `generate_discoveries_pdf.py:100-106` already ships. Do item 2 to make item 1 a one-line change
   per branch, and adding a tenth token stays a one-place edit.

3. **Example-chip verification issues its searches one at a time** —
   `senzing_viz_server.py:1157-1163`. `loadProbes` loops `for(const e of cands)` with an `await
   getJSON("/api/search?…")` inside, so up to ten live engine round-trips run strictly in series
   on **every load of the live app**, before a single chip appears. Verification itself is
   required and must stay (a chip that finds nothing is worse than no chip — that is why the loop
   exists), but nothing about it is order-dependent. Worst-case engine load is unchanged at ten
   searches; the current early exit at six good chips only reduces the typical count, and it trades
   a bounded saving in engine calls for an unbounded-in-practice serial latency on the first paint.

4. **The sequential-capture precondition behind `_CURRENT_TAB` is unwritten** —
   `capture_screenshots.py:466-484` and `:422`. The module-level `_CURRENT_TAB` is set by
   `_capture_one` and read by `_capture_chrome_cli` through `_virtual_time_ms(_CURRENT_TAB)`. The
   existing comment explains *why* the global exists (backends are invoked through a uniform
   two-argument signature) but not the condition that makes it **correct**: captures run strictly
   one at a time from `capture()`'s loop. Parallelizing that loop for speed — an obvious future
   optimization on a step that shells out to a browser per tab — would silently apply one tab's
   virtual-time budget to another tab's capture, and the symptom is a subtly under-settled PNG,
   not an error. INV-122 requires each file to show the tab it is named after; a wrong settle
   budget is the quiet way to violate it.

5. **Only one shipped Markdown file is swept for mojibake** — `mojibake_lines()`
   (`normalize_docs_markdown.py:74-91`) detects the Windows-1252 round-trip corruption that
   `ground-rules.md:225` documents, and `tests/test_windows_powershell_guidance.py` covers the
   detector itself thoroughly. The only **shipped content** it is run over is
   `docs/examples/bootcamp_recap.example.md` (`test_the_shipped_example_recap_is_clean`), and the
   normalizer's own sweep at `normalize_docs_markdown.py:249` covers a project's top-level `docs/`
   at bootcamp time, not the plugin's own Markdown. `tests/test_markdown_hygiene.py` already walks
   `PLUGIN.rglob("*.md")` for trailing whitespace and punctuation, so the corpus is enumerated and
   the detector exists — they are simply not pointed at each other. Any of the plugin's ~200
   shipped `.md` files edited on Windows through the trap the ground rules describe would ship
   corrupted with nothing to catch it.

## Root cause

Items 1 and 2 are one drift: two sibling generators built to the same standard, only one of which
was brought up to INV-111/INV-184 when that standard was set. Item 3 is a correctness-first loop
that was never revisited for cost. Items 4 and 5 are both "the safeguard exists, the thing it
protects was never wired to it" — an invariant held by a call-site convention nobody wrote down,
and a detector never aimed at the corpus.

## Proposed change

1. Factor `generate_recap_pdf.py`'s nine fallback assignments into a `_use_fallback_palette()`
   returning the nine values in a fixed order, mirroring
   `generate_discoveries_pdf.py:100-106` (item 2), then split the handler into
   `except ModuleNotFoundError:` and `except Exception as exc:`, each writing the corresponding
   stderr line before calling it (item 1). Match the sibling's wording so the two read as one
   idiom. The fallback still proceeds and the exit status is unchanged — only silence is
   forbidden (INV-111), and the PDF is always produced (INV-048/INV-066).
2. Replace `loadProbes`' serial verification with a single parallel round: issue all candidate
   searches at once, await them together, then keep the first six that matched **in the original
   merge order**, dropping and `console.warn`-ing the rest exactly as now. A rejected search must
   not reject the batch — each candidate's failure stays that candidate's failure.
3. Extend the `_CURRENT_TAB` comment to state the precondition ("`_capture_one` runs one capture
   at a time; parallelizing `capture()`'s loop requires threading the tab through the backend
   signature instead"), and pin it with a test in `tests/test_capture_tabs.py` so a future
   parallelization fails a test rather than producing a mis-settled PNG.
4. Run `mojibake_lines()` over every shipped `.md` in `tests/test_markdown_hygiene.py`, reusing
   the glob already there, reporting `path:line` for each hit. Keep the existing
   not-vacuous guard covering the new check, so a drifted glob cannot make it pass silently.

## Acceptance criteria

- [ ] `generate_recap_pdf.py` writes a distinct stderr line for "brand_tokens not importable"
      (naming the directory searched) and for "present but unusable" (naming the exception), and
      neither path raises or changes the exit status.
- [ ] `generate_recap_pdf.py` assigns its fallback palette through one helper, called once per
      `except` branch; the nine literals appear exactly once in the file.
- [ ] `tests/test_brand_sync.py` still passes and still asserts the fallback equals `brand_tokens`
      (INV-107/INV-184), through the helper rather than around it.
- [ ] Example-chip verification issues its searches concurrently; the chips offered, their order,
      the six-chip cap, and the drop-with-`console.warn` behavior are unchanged from the serial
      version, and one failing search does not lose the others.
- [ ] `tests/test_organization_search.py::ChipsAreVerifiedBeforeBeingOffered` still passes.
- [ ] The `_CURRENT_TAB` comment names the sequential-only precondition, and a test in
      `tests/test_capture_tabs.py` fails if a capture is started while another is in flight.
- [ ] `tests/test_markdown_hygiene.py` reports mojibake in any shipped `.md`, is covered by the
      existing not-vacuous guard, and passes on the current tree.
- [ ] No bootcamper-facing behavior changes (INV-012): every item is a stderr diagnostic, a
      latency improvement, a comment, or a test.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — items 1, 2 (~831-853).
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — item 3 (`loadProbes`, ~1157-1163).
- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — item 4 (~466-484).
- `tests/test_capture_tabs.py` — item 4's guard.
- `tests/test_markdown_hygiene.py` — item 5.
- `tests/test_brand_sync.py` — follow items 1-2 if the helper changes how the fallback is read.

## Evaluated, no change

Checked against the tree on 2026-07-30 and deliberately not specified, so a later audit does not
re-open them:

- **"No unit tests for `mojibake_lines`, `_esc_html`'s quote escaping, or the node-label
  de-duplication."** All three are covered; the reviewer saw only the diff, not the repo.
  `tests/test_windows_powershell_guidance.py` exercises `mojibake_lines` across eleven cases
  (true positives per corrupted character class, accented text, CJK, emoji, ASCII-only, the
  replacement-character guard, multi-line numbering, and the shipped example recap);
  `tests/test_snapshot_and_capture_fidelity.py::test_esc_html_escapes_both_quote_characters`
  pins the quote escaping against a hostile attribute payload; and
  `tests/test_graph_label_distinctness.py` covers the label collision suffixing. Likewise
  `_windows_registry_browsers` (`tests/test_windows_browser_discovery.py`),
  `dropped_character_warning` (`tests/test_recap_pdf_font_safety.py`) and the certificate
  clipping loops (`tests/test_recap_pdf_certificate.py::TheFixedPageCannotBeOverrun`) are all
  tested. The one real gap the review pointed at — the two-attribute search fallback on the
  **error** path — is in `specs/search-attribute-fallback-survives-a-failed-attempt.md`.
- **"`resolve_recap_image` accepts absolute paths."** Intended. The recap Markdown is authored
  locally by the agent and the Bootcamper in their own project, and embedding a local image the
  recap references is the function's purpose; an absolute path is the form a Bootcamper's own
  screenshot reference legitimately takes. There is no untrusted-input path into the recap
  source, and refusing absolute paths would silently drop the Bootcamper's own images from their
  keepsake — INV-162's failure, traded for no gain. Revisit only if recap content ever becomes
  remotely sourced.
- **"The `reporting_guide` topic warning is duplicated across two skill files."** The reviewer's
  own reading is right: skill files load independently and must each carry the context the model
  needs. Deliberate.
- **"Markdown/CommonMark compliance could not be verified from the diff."** Already enforced in
  the repo by `tests/test_markdown_hygiene.py` and `normalize_docs_markdown.py` with its
  content-preservation guard; item 5 above closes the one part that genuinely was not covered.

## Deviations from this spec, and why (2026-07-30)

- **Item 5 needed an exemption the spec did not anticipate.** Pointing `mojibake_lines` at every
  shipped `.md` immediately found one hit, and it is legitimate:
  `skills/bootcamp-onboarding/ground-rules.md:226` **teaches** the Windows-1252 trap by quoting
  the corruption it produces (``25 em dashes became `â€”` ``) inside a backtick span. The gate
  structurally cannot represent that input, so per INV-173 it was exempted rather than resolved
  by altering the documentation to satisfy the check. The exemption is as narrow as the case —
  that one file, and only where **every** mojibake character sits inside inline code, so
  corrupted prose in the same file still fails — and it is self-invalidating:
  `test_the_exemption_is_not_stale` fails if the file stops carrying the example, so a dead
  exemption cannot later mask a real defect. Two further tests pin that the exemption does not
  extend to prose or to other files.
- **Item 4 got a runtime guard as well as the comment and the test.** The spec asked for the
  precondition to be written down and pinned by a test. Implemented as specified, plus
  `_CAPTURE_IN_FLIGHT`: `_capture_one` now warns on stderr (never raises — INV-052/INV-048) if a
  capture begins while another is in flight, and clears the flag in a `finally` so a backend that
  raises cannot leave it set. Without it the "test" could only assert the comment's text; with it
  the hazard is detected at runtime in a parallelized future, which is what the spec's "announces
  itself" actually requires.
- **Item 3's engine cost, measured.** The spec predicted the worst case is unchanged and the
  typical case costs a few more searches. Confirmed under a Node harness on a ten-candidate
  fixture: the serial version would have issued nine searches (stopping at the sixth hit), the
  parallel version issues ten — in one round-trip rather than ten, with identical chips in
  identical order.

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #7 (comment 5135083534),
  Parts 1-3. Part 3 found no defects.
- Priority: Low — no bootcamper-facing behavior changes.
- Related specs: `specs/search-attribute-fallback-survives-a-failed-attempt.md` (the one
  correctness bug from the same review), `specs/pr4-review-minor-fixes.md` (the same exercise for
  PR #4, which established INV-107), and the `deep-dive-audit-2026-07-30` entry in
  `specs/IMPLEMENTED.md` (not a spec file; established INV-184, the palette-fallback pattern
  item 2 completes).

## Invariants introduced

- None required. Items 1-2 bring `generate_recap_pdf.py` into conformance with existing INV-111
  and INV-184; item 4 documents and tests the precondition behind INV-122's per-tab settle
  budget; items 3 and 5 add no guarantee not already implied.
