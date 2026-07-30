# The shipped example recap claims a per-tab screenshot capture and four API endpoints it does not have

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` is the plugin's only shipped model
of a finished recap (INV-065) and the thing a guide authoring a real recap is most likely to
pattern-match on. Its Truth Set visualization section makes two claims the file itself contradicts.

**Claim 1 — a capture it does not contain.** `:211`, in Actions Taken:

```text
- Captured one screenshot per visualization tab and embedded them all in this recap, in the app's
  tab order.
```

`:196` describes the app as having **six** tabs. The file embeds **one** image (`:216`,
`bootcamp_recap.example.truthset.png`), which the generator confirms:

```text
PDF generated: ex.pdf (renderer: fpdf2, rendered 29079 of 29345 source characters (99%),
embedded 1 of 1 images)
```

That is a false statement in a shipped artifact, and it is the exact shape INV-146 exists to forbid
— *"…dropped Merge Statistics, Match Keys and Feature Scores (the three analytical tabs) from a
six-tab app while the surrounding prose described all six."* The example demonstrates the anti-pattern
in the plugin's own reference.

**Claim 2 — a stale endpoint count.** The same line says *"all four API endpoints verified"*.
`module-03b-truthset-visualization/phase1-visualization.md:249-264` verifies **ten**: `/api/stats`,
`/api/graph`, `/api/merges`, `/api/search`, `/api/why`, `/api/how`, `/api/records`, `/api/overlap`,
`/api/matchkeys`, `/api/features`.

The header also reads `**Plugin version:** 0.4.0` (`:8`) against `0.5.0` in
`.claude-plugin/plugin.json` — defensible on its own as a record of a past run, but it compounds the
impression of a fixture that stopped tracking the product.

## Root cause

The example was last rewritten by `specs/refresh-example-recap.md`, implemented **2026-07-19**
(`specs/IMPLEMENTED.md:2257`, commit `68d10be`) — when the app had four verified endpoints and before
the tab consolidations. Everything that made the claims stale landed afterwards:

| Change | Date |
|---|---|
| `consolidate-merge-statistics-and-results-dashboard-tabs` | 2026-07-25 |
| `consolidate-truthset-viz-merges-and-network-tabs` | 2026-07-26 |
| `embed-every-captured-tab-in-tab-order` (INV-146/INV-147) | 2026-07-26 |
| `per-tab-screenshot-capture-and-grounded-captions` (INV-122/INV-123) | 2026-07-26 |
| ten-endpoint verification table in `phase1-visualization.md` | after the consolidations |

No spec has refreshed the example since, and nothing detects the drift. `tests/test_example_recap_sync.py`
pins the `.md` ↔ `.pdf` relationship thoroughly — image embedding, document-relative paths, a fresh
render from an unrelated cwd, distinctive source lines present in the committed PDF — but it does not
check whether the example's **prose is true of the example**, which is a different property and the
one that broke.

Note that INV-146 governs runs, not fixtures, so this is not literally an INV-146 breach; it is an
INV-003 (consistent, coherent, complete) defect in a shipped artifact, of the class INV-123 forbids
for captions — *"MUST NOT assert content the image does not contain."*

## Proposed change

Pick **one** of two routes for claim 1 — they differ in maintainer cost, and the spec should record
which was chosen and why.

- **Route A (faithful, higher cost).** Ship the remaining five PNGs — sanitized captures of Merge
  Statistics, Match Keys, Feature Scores, Cross-Source and Search / Probe from a Truth Set run — and
  embed all six in tab order (INV-147), each with a caption derived from the image it shows (INV-123).
  This makes the example a true model of INV-146/INV-147, which is what a guide most needs to copy.
- **Route B (honest, low cost — recommended).** Keep one image and make the example say so: change
  `:211` to state that a screenshot was captured per tab **and that this sanitized example includes
  only the Entity Graph image**, with a short note that a real recap embeds every captured tab in tab
  order (INV-146/INV-147). The example then models the rule by stating it rather than by carrying six
  PNGs into the shipped plugin.

Then, regardless of route:

1. **Fix the endpoint count** at `:211`: "all ten API endpoints verified", or drop the count and say
   "every API endpoint in the contract verified" so it cannot go stale again — preferable, since the
   count is exactly what drifted.
2. **Refresh `**Plugin version:**`** to the current `plugin.json` version, and note in the file (an
   HTML comment, as the file already does at `:215` for the image path) that the version is refreshed
   with the example rather than frozen.
3. **Re-render the committed PDF.** INV-065 requires the pair remain regenerable and
   `test_example_recap_sync.py` asserts distinctive source lines appear in the committed PDF — so
   editing the `.md` alone fails the suite. Regenerate from an unrelated working directory (INV-161):

   ```bash
   python3 plugins/senzing-bootcamp/scripts/generate_recap_pdf.py \
       --input plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md \
       --output plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf
   ```

4. **Guard the class**, so the fixture cannot silently drift from the product again: a test that the
   example's claims are consistent with the example — the number of tabs its prose names vs. the
   number of images it embeds (or an explicit "this example includes only …" statement), and no
   hardcoded endpoint count that disagrees with the contract's verification table.

## Acceptance criteria

- [ ] The example no longer claims to embed a screenshot per tab while embedding one; either six
      images are embedded in tab order (Route A) or the text states what the sanitized example
      includes (Route B).
- [ ] The endpoint claim matches `phase1-visualization.md:249-264` — ten, or a count-free phrasing.
- [ ] `**Plugin version:**` matches `.claude-plugin/plugin.json`.
- [ ] `bootcamp_recap.example.pdf` is re-rendered from the edited `.md` and
      `tests/test_example_recap_sync.py` passes, including the fresh-render-from-another-cwd case.
- [ ] A test asserts the example's tab/image claims are internally consistent and that no stale
      endpoint count is present.
- [ ] The example still carries no real personal data (INV-065) and still satisfies `--check` and
      INV-103's four subsections and INV-176's block shapes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      example is a Java-path recap and stays one; nothing here is OS- or language-specific.

## Affected files

- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` — `:8`, `:196`, `:211`, `:216`.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` — re-rendered.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.*.png` — five new sanitized captures
  under Route A only.
- `tests/test_example_recap_sync.py` — add the internal-consistency assertions.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **Medium** — no runtime effect, but it is a false claim in a shipped artifact and the
  pattern a guide copies when authoring the real thing.
- MCP re-check: n/a (no Senzing fact — the plugin's own example fixture). Server **1.32.2** confirmed
  current at triage time via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/refresh-example-recap.md` (the 2026-07-19 refresh this supersedes in effect),
  `specs/example-recap-reference.md` (INV-065), `specs/embed-every-captured-tab-in-tab-order.md`
  (INV-146/INV-147), `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-122/INV-123),
  `specs/recap-summary-blocks-authored-as-bullets.md` (INV-176 — the previous example-fixture drift,
  same file), `specs/python3-compile-and-example-recap-mechanism.md`.

## Note on choosing the route

Route B is recommended. INV-146's purpose is that a *run* never drops a captured tab; the example's
purpose is to show the shape of a finished recap. Five more PNGs in the shipped plugin buy fidelity
at a real size cost, and a sentence naming the omission removes the false claim just as completely.
Record whichever the maintainer picks in the implementation notes, since a future audit will
otherwise re-raise the one-image example.

## Deviations from this spec, and why (2026-07-30)

- **Route B was chosen by the maintainer** (2026-07-30), and the reason is worth recording beyond
  cost: Route A would have meant **inventing** five screenshots of tabs nobody captured. INV-123
  requires a caption derived from the opened image, so five plausible-looking fabrications would have
  replaced one false claim with six. Route B removes the false claim and keeps every shipped image a
  real capture.
- **The stale endpoint count appeared in THREE places, not one.** The spec cited only the Truth Set
  section's *"all four API endpoints verified"*. Also found and fixed: `:198` *"serving the same
  four-endpoint contract"* (Information Shared, same section) and `:397` *"(verified all four API
  endpoints)"* — in the **Query, Visualize and Discover** section, about the Module 7 app rather than
  the Truth Set one. All three are now count-free ("every API endpoint in the contract"), which the
  spec preferred precisely so the claim cannot go stale a third time.
- **A pre-existing test had to be fixed to accept a multi-line HTML comment.**
  `tests/test_example_recap_sync.py`'s line sampler skipped lines *starting with* `<!--` but not the
  continuation lines of a comment block, so the header note added here was reported as PDF staleness
  on a freshly rendered file. The sampler now skips whole comment blocks. The bug was latent: the
  example's only previous comment was a single line. That file is in this spec's Affected files, but
  the *sampler* change is beyond what the spec asked for.
- **The version is documented as tracking the manifest, not as a historical record.** The spec asked
  for a note that the version "is refreshed with the example rather than frozen"; that note now also
  says a test asserts the match, and explains why the endpoint and tab claims are deliberately
  count-free. Written as an HTML comment, which is what forced the sampler fix above.
- **Not runtime-verified:** nothing. The PDF was re-rendered from an unrelated working directory per
  INV-161 (`rendered 29269 of 29981 source characters (98%), embedded 1 of 1 images`), `--check`
  passes, and all five guards were mutation-tested (disclosure removed; disclosure stripped of the
  real rule; each of the two endpoint phrasings restored; version reverted to 0.4.0) and reverted.
