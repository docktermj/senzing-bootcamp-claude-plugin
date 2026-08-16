# Guards enforce class-scoped rules from hardcoded site sets

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**INV-246** requires that a guard enforcing a rule across multiple shipped sites derive its site set
by scanning the corpus, never by hardcoding a list of paths. Four guards do the opposite, and each
one's own comment states a **class** claim while its constant names two or three files:

| Guard | Class claim in its own text | Hardcoded set |
|---|---|---|
| `tests/test_brand_sync.py` | INV-184: "**Every** shipped generator that inlines a fallback copy of the brand palette" | three per-generator test methods |
| `tests/test_model_effort_nudge_edges.py:34` | "**Every** file that pins a switch question the bootcamper reads" | `PINNING_FILES = (GROUND_RULES, GRADUATION)` |
| `tests/test_graduation_ending_surfaces.py:42` | "worded identically **wherever** it is presented"; "Surfaces that tell the reader how graduation finishes" | `ENDING_SURFACES = (GRADUATION_SKILL, GRADUATE_COMMAND)` |
| `tests/test_screenshot_retention_and_order.py:21` | "these tests assert **both** call sites defer to it" | `CALL_SITES = (MODULE_COMPLETION, GRADUATION)` |

⚠️ **All four are correct today.** Every class claim was re-checked against the corpus on 2026-08-15
and no site is currently uncovered: exactly two files pin a switch question (the third hit,
`docs/examples/bootcamp_recap.example.md`, is recap *transcript* prose under "Questions & Responses",
not a pinned gate); exactly two files carry the graduation offer, and the guard checks the offer
against `(MODULE_COMPLETION, MODULE_07_PHASE1)` — the two that carry it — using `ENDING_SURFACES`
only for the separate terminal-banner rule; exactly two files invoke `capture_screenshots`; and all
four scripts inlining a brand fallback are covered. **The defect is structural, not a live gap.**

## Root cause

The site sets encode where each author noticed the pattern — which INV-246 exists to say is exactly
the belief that is wrong when a rule is applied incompletely. Two things make this worth fixing
rather than noting:

1. **`test_brand_sync.py` guards the rule whose entire existence is this failure.** INV-184's own
   text records it: *"INV-107 named two generators; the property belongs to the pattern, and the
   third (`generate_discoveries_pdf.py`) drifted out of scope unnoticed while its own comment claimed
   a test asserted it."* The remedy at the time was to add the third generator **by hand**. INV-246
   was registered later (2026-08-14) and now forbids that guard shape — so a fourth generator added
   tomorrow reproduces, step for step, the history INV-184 was written to record. A derived sweep is
   the only version of this guard that cannot repeat it.
2. **A hardcoded set is silent, not loud, when it goes stale.** Adding a fifth shipped file that
   pins a switch question, or a third `capture_screenshots` call site, leaves every one of these
   guards green. Nothing in an offline suite (INV-108) notices, and the next audit re-derives the
   same conclusion by hand — which is how INV-244's third site and INV-243's three uncovered sites
   were both found, months apart, by reading rather than by a failing test.

`coverage_reports.py shipped` cannot substitute: it reports invariants cited by **no** shipped file,
so a rule cited once scores as covered. It answers "is this mentioned anywhere?", never "is it
enforced everywhere it binds?"

## Proposed change

For each of the four, replace the hardcoded constant with a derivation, and keep the constant only
as an assertion about what the derivation should currently find:

1. **`test_brand_sync.py`** — scan `plugins/senzing-bootcamp/scripts/*.py` for a module-level
   `_?FALLBACK_(BRAND|COLORS|RGB|SOURCE_COLORS)` constant, and assert **each discovered carrier** is
   in sync with `brand_tokens.py`. A generator added with a fallback is then covered on the day it
   ships, which is what INV-184 asks for and what INV-246 requires.
2. **`test_model_effort_nudge_edges.py`** — derive `PINNING_FILES` by scanning shipped Markdown for
   the pinned switch-question form, excluding recap-transcript prose (`- **Q:**` lines under
   "Questions & Responses"), then apply the existing hint assertions to every file found.
3. **`test_graduation_ending_surfaces.py`** — derive the offer sites by scanning for the `OFFER`
   regex rather than naming `MODULE_COMPLETION` and `MODULE_07_PHASE1`; derive the ending surfaces by
   scanning for `TERMINAL_BANNER`.
4. **`test_screenshot_retention_and_order.py`** — derive `CALL_SITES` by scanning shipped Markdown for
   `capture_screenshots` invocations.

Each derivation carries a **non-vacuity floor** (assert the scan found at least the count known
today), so a broken pattern degrades to a failure rather than to a guard that silently checks
nothing — the failure mode a derived guard introduces and a hardcoded one does not.

⛔ **Do not "fix" this by adding more paths to the lists.** That is the remedy INV-184 already tried.

## Acceptance criteria

- [ ] Each of the four guards derives its site set by scanning the corpus; no shipped-file path list
      remains as the *source* of what gets checked.
- [ ] Each derivation asserts a non-vacuity floor, so a pattern that stops matching fails loudly
      rather than passing over an empty set.
- [ ] A new shipped file matching each pattern is picked up without editing the guard —
      **negative-controlled** for every one of the four: plant a file/passage that should be covered,
      confirm the guard fails, then revert.
- [ ] `tests/test_brand_sync.py` covers every script carrying a brand-palette fallback constant,
      discovered rather than listed, satisfying INV-184's "every shipped generator" as INV-246
      requires it be satisfied.
- [ ] No behaviour changes in `plugins/` — this is entirely test-side.
- [ ] The full suite stays green and `citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_brand_sync.py` — derive the generator set.
- `tests/test_model_effort_nudge_edges.py` — derive `PINNING_FILES`.
- `tests/test_graduation_ending_surfaces.py` — derive the offer sites and the ending surfaces.
- `tests/test_screenshot_retention_and_order.py` — derive `CALL_SITES`.

⚠️ This list is where the pattern was **noticed**, not necessarily the whole set — the detector that
found it (a scan for module-level tuples of shipped-file constants that are then iterated) missed
`test_brand_sync.py`, which uses one method per generator instead of a tuple. Re-derive by scanning
rather than trusting these four.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15 (second run of the day)
  (`Source: self-observed (assistant retrospective)`). Found by forward-sweeping INV-246, registered
  the previous day, against the test suite that is supposed to obey it.
- Priority: **Medium**. No site is uncovered today, so nothing a Bootcamper can hit. It is the exact
  structural condition that has already failed twice in this repo — INV-107→INV-184, and the
  INV-244/INV-243 site gaps found by the 2026-08-14 audit — and the fix is test-side and cheap.
- MCP re-check: **n/a (no Senzing fact).** Entirely about this repo's own test suite and its own
  ruleset; no MCP tool was called and no Senzing claim is asserted. Server **1.32.9** recorded this
  session (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `inv244-absent-license-branch-exists-in-module-4-too` (the spec that established
  INV-246), `deep-dive-audit-2026-07-30` (established INV-184 after the same failure), and INV-246,
  INV-184, INV-107, INV-108.

## Deviations from this spec, and why (2026-08-15)

- **`test_brand_sync.py` got a derived coverage SWEEP, not a derived comparison.** Each carrier
  exposes differently-named constants (`_FALLBACK_BRAND`, `_FALLBACK_RGB`, `_FALLBACK_STROKES` …),
  so a single generic equality check would have been weaker than the per-generator assertions it
  replaced. Instead `TheCarrierSetIsDerived` scans `scripts/*.py` for a module-level
  `_?FALLBACK_[A-Z_]+` constant and fails if a discovered carrier is not exercised anywhere in the
  file — the *site set* is derived, and a new generator forces someone to add its assertions.
  Verified by planting `generate_zzz_pdf.py` carrying a fallback: the sweep fails.
- **`test_screenshot_retention_and_order.py` uses `os.path`, not `pathlib`.** Its `PLUGIN` is a
  string, so the derivation is written with `os.walk` to match the file's conventions rather than
  converting it. A first attempt used `PLUGIN.rglob` and raised `AttributeError` on five tests.
- **Each derivation carries a *membership* floor, not a count floor.** Asserting "the scan still
  finds the files known to match" is stronger than asserting a number: a count floor passes when one
  known site drops out and an unrelated new one appears.
- **All four negative controls plant a NEW site rather than mutating an existing one**, because that
  is the property under test — a hardcoded list passes every one of these, and each derivation
  fails: a new fallback carrier, a new file pinning a switch question with a wrong hint, a new
  graduation-offer surface, a new `capture_screenshots` call site.
- ⚠️ **An insertion error, caught and fixed.** The new class was first inserted between
  `BrandTokenSync`'s first and second methods, silently re-parenting five existing tests into it.
  The suite still passed — 30 tests either way — so nothing failed; it was caught by an AST check of
  class/method counts, not by the run. Worth recording because a test-count-only check would have
  missed it entirely.
- **No Senzing fact required re-verification.** `get_capabilities` was called this session to date
  the run (server **1.32.9**, 2026-08-15), confirming this spec's `MCP re-check: n/a`.
