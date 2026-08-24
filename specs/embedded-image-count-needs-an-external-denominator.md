# `embedded N of M images` counts the Markdown's own links, so it cannot detect a missing tab

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A Bootcamper reported that `docs/bootcamp_recap.pdf` did not appear to contain every tab of
the two visualization sections. Two separate findings came out of it.

**On that PDF the images were all present**, verified four ways rather than by the
generator's success line: 12 image XObjects at 1440×900, 12 distinct SHA-1 hashes (no
repeated tab), 12 `Do` paint operations each exactly once, and all 12 inside the A4 page box.
The impression came from layout — images render two per page at ~368 pt, so they land on
their own pages after each section's Actions Taken bullets rather than inline. That half is
a discoverability issue, not missing content.

**On the guarantee the Bootcamper is right, and the metric is the problem.** Confirmed in
code, 2026-07-31:

```text
generate_recap_pdf.py:712   def image_embed_note(referenced: int) -> str:
generate_recap_pdf.py:720       return f"embedded {embedded} of {referenced} images"
generate_recap_pdf.py:3001      referenced_images = recap_image_targets(source_text)
generate_recap_pdf.py:3107      note = f"{note}, {image_embed_note(len(referenced_images))}"
```

`referenced` is the count of `![](…)` links **in the recap Markdown being rendered**. The
denominator is derived from the same file being measured, so if only four of six tabs were
ever captured and embedded, the line reads `embedded 4 of 4 images` — a perfect score
against an incomplete set.

Nothing else in the chain closes the gap:

1. Screenshot capture is best-effort and non-blocking by contract (INV-122); a tab that
   fails is reported on stderr and everything downstream proceeds.
2. `--check` validates that each image reference resolves to a file on disk. It cannot know
   how many tabs existed.
3. Graduation Step 1a checks for "a visualization-producing module with no image" — it
   triggers only at **zero**. A section with 4 of 6 passes every check in the chain.

**Why this is worse than having no metric.** It is the number an agent naturally reaches for
to confirm completeness, and it is structurally incapable of detecting incompleteness. That
is not hypothetical: in the reporting session the assistant cited `embedded 12 of 12` to the
Bootcamper as evidence the screenshots were complete, when by construction it could not have
detected the failure being described. It was correct by luck of the input, not by
measurement — confident, wrong reassurance, which is the INV-110 failure applied to a count
instead of a retention percentage.

The plugin already has scar tissue here: the skills record a prior run whose recap "showed
the same three tabs in both visualization sections and the app looked narrower than it was."

## Root cause

The count was added to make embedding visible after images had silently gone missing
(INV-162). It was built from what the generator can see — the Markdown it is handed — which
makes it a faithful report of *embedding* and no report at all of *coverage*. The two read
identically in the success line, and the line is the only place either is stated.

## Proposed change

Give the count an **external** denominator: the number of tabs the app actually rendered,
not the number of links the Markdown happens to contain.

1. **`capture_screenshots.py` writes a sidecar manifest** next to the PNGs (e.g.
   `<name>-tabs.json`): tabs requested, tabs captured, and each tab that produced nothing
   with the reason. Capture stays non-blocking (INV-122); the manifest records what it did.
2. **`generate_recap_pdf.py --check` reads the manifest** where one exists and fails when a
   section embeds fewer images than the manifest recorded as captured, naming the missing
   tab slugs. Absent manifest → current behavior, reported as such rather than as a pass
   (INV-163).
3. **The success line reports against the manifest** when one exists, e.g.
   `embedded 12 of 12 images (12 of 12 captured tabs)`, so the denominator is visibly not
   derived from the file being measured.
4. **Graduation Step 1a's zero-image check becomes a count check** — compare each
   visualization section's embedded images against the PNGs on disk carrying that
   visualization's `<name>-` prefix, and warn on any shortfall, not only on zero.
   Non-blocking (INV-048).
5. **Interim, and independently worth doing:** state in Step 1b's verification guidance that
   `embedded N of M` measures Markdown references, not tab coverage, so it must not be cited
   as evidence of completeness. This is the part that would have stopped the wrong
   reassurance in the reporting session even with no code change.

Item 5 should ship even if 1–4 are deferred: the misuse is a documentation gap, and it has
already happened once.

## Acceptance criteria

- [ ] `capture_screenshots.py` writes a manifest recording tabs requested, captured, and
      failed-with-reason; capture remains non-blocking (INV-122).
- [ ] `--check` fails when a section embeds fewer images than its manifest recorded, naming
      the missing tab slugs.
- [ ] With no manifest present, `--check` reports the coverage check as **skipped** rather
      than passed (INV-163).
- [ ] The success line names the manifest-derived count separately from the
      Markdown-derived one, so the two are never conflated again.
- [ ] Graduation Step 1a warns on a *shortfall*, not only on zero, and stays non-blocking.
- [ ] Step 1b's guidance states that `embedded N of M` measures references, not coverage,
      and must not be cited as evidence of completeness.
- [ ] A test proves the failure this closes: a recap referencing 4 images with a manifest
      recording 6 captured tabs must fail `--check` and name the two missing slugs.
- [ ] MCP re-check: n/a — the capture helper, generator and `--check` are all plugin-bundled;
      no Senzing tool is involved.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/capture_screenshots.py` — the manifest.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `image_embed_note` (712-720), the `--check` path, the success line (~3107).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1a count check, Step 1b guidance.
- `tests/test_screenshot_retention_and_order.py` or `tests/test_recap_pdf_images.py` — the shortfall test.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "nothing verifies that every
  visualization tab reached the recap PDF - the \"embedded N of M images\" metric is
  self-referential" (2026-07-31, Module: Graduation; `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). Code claims verified 2026-07-31 at the line numbers
  quoted above.
- Upstream: not applicable.
- Related specs: `specs/enforce-screenshot-embed-and-backfill.md` and
  `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-122/INV-146 — both
  require every captured image to reach the recap; **neither adds a count check**, which is
  the gap this closes), `specs/recap-pdf-images-resolve-against-recap-directory.md` (INV-162).

## Deviations from this spec, and why (2026-07-31)

All five items shipped. Four differences from the text, and one limitation worth naming
rather than leaving for a reader to discover:

1. **`--check`'s coverage check is document-level, not per-section.** The criterion says
   "fails when a *section* embeds fewer images than its manifest recorded". The manifest is
   keyed by visualization `name`, and nothing in the recap records which module section a
   given visualization belongs to — so `--check` compares each manifest's captured files
   against the **whole recap's** image references. Consequence: a captured tab embedded in
   the *wrong* section still passes `--check`. The per-section comparison is done by
   graduation Step 1a, which has the section structure in hand; the spec's criterion is
   therefore met across the two together, not by `--check` alone. Closing it inside
   `--check` would need the recap to record a section↔visualization mapping, which is a
   larger change than this spec proposes.
2. **The manifest distinguishes three outcomes, not two.** The spec asks for "tabs
   requested, tabs captured, and each tab that produced nothing with the reason". Capture
   already separates *not present in this app* from *capture failed*, and collapsing them
   would make a tab the app does not serve look like lost content — so `not_present` and
   `failed` are separate lists. This matters for correctness, not tidiness: the coverage
   check must not demand an image for a tab that never existed, or every partial capture
   would fail graduation and INV-122 would be violated.
3. **The manifest is written before the no-capture early returns.** A run that captured
   *nothing* is the case the coverage check most needs to see, and the spec's placement
   would have skipped writing a manifest exactly then. It is also written on the
   "none of the requested tabs exist in this visualization" path.
4. **A corrupt manifest is reported and then treated as absent.** Not in the spec. An
   unreadable JSON file must not read as "no tabs expected" — that would convert a corrupt
   file into a clean bill of health. It reports `unreadable tab manifest …` and falls
   through to the `SKIPPED` path (INV-163). Mutation-proven.

Two pre-existing tests had to change, both because they enumerated a whole directory that
now also holds the sidecar (`test_absent_tab_produces_no_file_and_is_reported`,
`test_each_tab_produces_a_distinct_image`) — scoped to `*.png` and given manifest
assertions instead.

One test **pinned wording this spec deliberately changes**:
`test_warns_when_a_visualization_module_has_no_image` asserted the heading
"visualization-producing module with no image", which named a check that fired only at
zero — the very shortcoming being fixed. It now asserts the requirement (shortfall, not
only zero) rather than the heading, following the reasoning already recorded on its
neighbor `test_module_completion_requires_one_image_per_tab`; the zero case is asserted
separately so it cannot be lost.

The success line now reads, e.g.: `rendered 686 of 707 source characters (97%), embedded 6
of 6 images, 6 of 6 captured tabs reached the recap` — the two counts deliberately worded
differently, since reading alike is how they were conflated.

## Invariants introduced

- `INV-193` — A count or percentage presented as evidence of **completeness** MUST derive its
  denominator from outside the artifact it measures; a self-derived figure MUST state what it
  cannot detect and MUST NOT be cited as proof of completeness (recorded in
  `specs/INVARIANTS.md`, maintainer-approved 2026-07-31).
