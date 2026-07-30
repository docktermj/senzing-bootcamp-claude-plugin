# Module 5's two generated HTML pages sit outside every visualization rule — no brand tokens, no offline guarantee, no escaping

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5 offers the bootcamper two web pages and saves both under `docs/visualizations/`:

- `phase1-quality-assessment.md:335` — 👉 *"Would you like a visual of the quality assessment
  (coverage bars and per-field completeness)?"*
- `phase2-data-mapping.md:604` — 👉 *"Would you like a web page showing the quality analysis
  (coverage charts and the field mapping summary)?"*

Both instructions are one sentence long:

```text
If the bootcamper accepts, generate a self-contained HTML page and save it to
`docs/visualizations/`.
```

That sentence carries none of the requirements that bind every *other* bootcamper-facing visual the
plugin produces. Three concrete consequences:

1. **A CDN fetch breaks the offline guarantee.** Nothing tells the guide to inline the vendored
   `scripts/vendor/d3.v7.min.js`, so "coverage charts" plausibly arrive as
   `<script src="https://cdn.jsdelivr.net/npm/chart.js">` — a page that renders blank on the
   air-gapped workstation Senzing evaluations frequently run on, with no error.
2. **An unbranded page ships beside branded ones.** The recap PDF and the Truth Set app take their
   palette and typography from `brand_tokens.py`; these two pages take whatever the model picks, and
   they sit in the same directory the recap embeds screenshots from.
3. **Unescaped bootcamper data reaches a saved, shareable artifact.** A quality page's whole content
   *is* the bootcamper's field names and sample values. Nothing tells the guide to escape them for
   the HTML or inline-`<script>` context.

## Root cause

The rules exist; they are stated in places these two steps never reach.

- **INV-081** binds them by its own terms — *"Every bootcamper-facing visual deliverable the
  bootcamp generates (… and any future generated charts/dashboards/HTML/PDF) MUST take its palette
  and typography from the shared Senzing brand tokens … and MUST keep rendering offline (no
  web-font/CDN fetch)"*. But `grep -rn brand_tokens skills/` matches modules 3b and 7 and
  `ground-rules.md` only — **never module 5**.
- **The only governing text softens the MUST into a SHOULD.** `ground-rules.md:303-315`:

  ```text
  - **Apply the Senzing brand to generated visual artifacts, where appropriate.** Any visual
    deliverable the bootcamp produces … should follow the Senzing "Obsidian & Ember" style guide …
    "Where appropriate" leaves plain functional/dev output unbranded.
  ```

  A bootcamper-facing keepsake is never "plain functional/dev output", so the carve-out does not
  apply — but a reader deciding in the moment has a *should* and an escape hatch, against an
  invariant that says MUST.
- **INV-106's escaping requirement is stated only inside the Truth Set contract.**
  `module-03b-truthset-visualization/visualization-api-reference.md:706` — *"Every string that
  reaches the page from the loaded data MUST be escaped for the context it is written into"* — and
  neither Module 5 step cites that file. INV-106's own text is general ("Data-sourced strings written
  into rendered HTML MUST likewise be escaped for that context"), so the requirement binds; only its
  statement is out of reach.
- **A fourth mismatch, cosmetic but confusing.**
  `bootcamp-onboarding/module-completion.md:154` triggers screenshot capture on *"an HTML page under
  `docs/visualizations/`"* — which these two pages are — but its entire procedure is tab-based
  (`--tabs graph,stats,matchkeys,…`). Pointed at a quality page the helper correctly skips every
  requested tab and reports on stderr (INV-122), so nothing breaks; the instruction is simply
  inapplicable and reads as though it applies.

This is the failure mode INV-164 named explicitly: *"the defect reached a generated query program
precisely because it lived in the reference implementation and in no written rule."* Here the rule
exists but lives in a file the generating step never opens.

## Proposed change

1. **State the requirements at both offer sites.** Replace the one-liner in
   `phase1-quality-assessment.md:337-339` and `phase2-data-mapping.md:606-608` with the four things
   that actually bind, stated once and cross-referenced rather than restated in full:
   - palette and typography from `${CLAUDE_PLUGIN_ROOT}/scripts/brand_tokens.py`, falling back
     gracefully if the module is absent (INV-081);
   - renders **offline** — inline the vendored `scripts/vendor/d3.v7.min.js` if a chart library is
     needed, never a CDN (INV-081/INV-091's offline clause);
   - every bootcamper-sourced string (field names, sample values, source names) escaped for the
     context it is written into — HTML text, attribute, and inline `<script>` per INV-106, pointing
     at `visualization-api-reference.md`'s "Rendering contract" as the statement of record;
   - written under `docs/visualizations/` (INV-070 — already correct in both).
2. **Harden `ground-rules.md:303-315`** so the global statement matches INV-081: a bootcamper-facing
   visual deliverable **MUST** take palette/typography from the tokens and **MUST** render offline;
   keep "where appropriate" scoped explicitly to plain functional/dev output, which is what it was
   for.
3. **Scope the capture trigger.** At `module-completion.md:154`, say the per-tab procedure applies to
   the **tabbed visualization app**; a single-page HTML deliverable is captured as one image (or not
   at all) and never with `--tabs`.
4. **Assert the reachability**, not the prose: a test that every skill step instructing generation of
   a bootcamper-facing HTML page names the brand tokens, the offline requirement, and the escaping
   requirement. That is the guard that catches the *next* ad-hoc HTML offer.

## Acceptance criteria

- [ ] Both Module 5 offer sites state the brand-token, offline, escaping and location requirements,
      each with its invariant reference.
- [ ] `ground-rules.md`'s "Visual deliverables (Senzing brand)" section states MUST for
      bootcamper-facing deliverables and confines "where appropriate" to plain functional/dev output.
- [ ] Neither Module 5 page instruction can be satisfied by a CDN fetch: the offline requirement and
      the vendored-D3 path are named at the point of generation.
- [ ] `module-completion.md`'s screenshot procedure states it is for the tabbed app, and what to do
      with a single-page HTML deliverable instead.
- [ ] A test enumerates every skill instruction to generate bootcamper-facing HTML and asserts each
      names brand tokens, offline rendering, and escaping — failing for a newly added ad-hoc offer.
- [ ] No change to the Truth Set contract or the Python reference is needed or made; this spec moves
      requirements into reach, it does not restate or fork them (INV-080's no-fork discipline).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the pages
      are generated HTML, and the guidance names no language-specific tooling.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  the visualization checkpoint (~`:332-339`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` —
  the "Offer visualization" block (~`:602-608`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — "Visual deliverables
  (Senzing brand)" (~`:303-315`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — capture-trigger scope
  (~`:152-157`).
- `tests/test_generated_html_deliverables.py` (new) — the reachability guard.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **Medium** — the pages are opt-in, so not every run hits them; but the offline failure is
  silent and total on an air-gapped workstation, and the escaping gap puts bootcamper data unescaped
  into a saved artifact.
- MCP re-check: n/a (no Senzing fact — the plugin's own branding, offline and escaping rules). Server
  **1.32.2** confirmed current at triage time via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/apply-senzing-style-guide-to-deliverables.md` (INV-081, which named "any
  future generated charts/dashboards/HTML" and never reached Module 5),
  `specs/escape-viz-snapshot-script-payload.md` (INV-106),
  `specs/vendor-d3-offline-visualization.md` / `specs/visualization-server-in-chosen-language.md`
  (INV-071/INV-091's offline guarantee), `specs/layout-tree-reconciliation.md` (INV-070),
  `specs/organization-search-requires-name-org.md` (INV-164 — the rule-lives-in-the-wrong-file class).

## Deviations from this spec, and why (2026-07-29)

- **A pre-existing test had to be made rewrap-proof.** `tests/test_capture_tabs.py`'s
  `test_capture_is_per_tab_not_several_of_one` matched the literal `one image per tab.{0,80}never
  several shots of one` against raw file text. Scoping `module-completion.md`'s capture section to the
  tabbed app re-wrapped that paragraph, moving a line break inside the phrase, and the assertion
  failed on prose that still said exactly the right thing. The test now flattens whitespace first —
  it asserts the requirement rather than the current line wrapping. Recorded because
  `tests/test_capture_tabs.py` is in neither spec's `## Affected files`.
- **The escaping probe requires the INV-106 citation, not the word "escape".** Mutation-testing showed
  a bare-word probe passing after the rule itself was deleted, because the surviving phrase
  "`\uXXXX` escapes" still contained it. Requiring the citation is also what makes the rule
  *reachable*: it is how a reader gets from the offer to the statement of record.
- **`ground-rules.md` gained two bullets, not just a MUST.** Beyond hardening the brand rule, the
  carve-out now carries an explicit test for what counts as bootcamper-facing ("saved and handed to
  them"), because "where appropriate" without a test is an exemption in practice; and the escaping
  rule is stated there for **any** generated page, since it was previously reachable only from the
  Truth Set app's contract.
- **Criterion 6 holds for this spec, but the same commit does change the Python reference** — under
  the sibling spec `viz-reference-help-text-names-removed-tabs`, implemented in the same pass. This
  spec restated no rule and forked no validator; it made existing rules reachable from where the
  pages are authored.
- **Not runtime-verified:** no HTML page was generated, because generating one needs a bootcamp run
  with profiled source data. What is verified: both offers name every binding rule, the sweep finds
  the offers rather than being hardcoded to them, and all six guards were mutation-tested (brand
  tokens stripped, offline rule stripped, INV-106 stripped from each offer, INV-129 stripped, the
  softened "should" wording restored, the single-page capture note deleted) and reverted.

## Invariants introduced

- `INV-183` — A step that instructs the guide to generate a bootcamper-facing artifact MUST, at that
  step, name every rule governing how the artifact is produced — or cite the file that states it —
  and MUST NOT rely on a rule stated only elsewhere; the rule is named and linked, never restated or
  forked. Generalizes INV-164 from a reference implementation to any authoring instruction. Recorded
  in `specs/INVARIANTS.md`, maintainer-approved 2026-07-30.
