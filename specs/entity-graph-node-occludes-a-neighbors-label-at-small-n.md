# A node occludes its neighbor's label in the smallest entity graph

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

In the Entity Graph tab, a node's circle is drawn over an adjacent node's text label, cutting
off the start of the entity name. Observed on the **smallest possible graph — 2 entities** — so
this is the base case, not a crowding effect.

Rendered headless from a real snapshot (Senzing **4.4.0**, 4 records → 2 entities, 1
multi-record) on 2026-09-02, the larger node's label renders as:

```
relia B Quorndon
```

The entity's name is **`Aurelia B Quorndon`**. The leading `Au` sits behind the smaller
neighboring node's circle. The smaller node's own label (`Tobias Fennimore`) is legible.

⚠️ **Not a layout-settling artifact.** Re-rendered at a `--virtual-time-budget` of 30s against
the 8s render: the two PNGs are **byte-identical** (`md5` match), so the force simulation has
converged and this is the settled state.

The reader sees a plausible, complete-looking graph with a silently wrong entity name — the
"corrupted artifact is the keepsake" failure mode, since Module 3b's graph is the bootcamp's
showpiece and these PNGs are embedded into the recap (INV-146).

## Root cause

Unverified — needs investigation. What is established:

- The occluding shape is a **node circle**, not another label, so this is z-order/placement
  between the node layer and the label layer, not label-vs-label collision.
- It reproduces at N=2, so it is not the density problem
  `specs/visualization-legibility-at-production-scale.md` addresses (that spec's evidence is
  **2,799 entities / 4,464 relationships**, and it is already implemented). Distinct root cause,
  distinct fix.
- Labels are drawn near the node center with a small offset, so a neighbor whose radius exceeds
  the offset overlaps the text. Node radius scales with record count, which is why the
  3-record node's label is the one damaged — the bigger the entity, the wider the occluding disc.

What to check in `plugins/senzing-bootcamp/scripts/senzing_viz_server.py`:

1. The label `<text>` offset relative to node radius — whether the offset is a constant while
   the radius is data-scaled.
2. Whether labels are appended in the same SVG group as the circles (so paint order is
   node-then-label per datum, letting a later node paint over an earlier label) rather than in a
   separate group layered above all circles.
3. The force simulation's collision radius — whether it accounts for the label's rendered width
   at all, or only the circle.

⛔ Per INV-090/INV-104/INV-124 the visualization contract binds **every** language
implementation, so the fix belongs in `visualization-api-reference.md` as well as in the Python
reference, or a bootcamper building the server in Java reproduces it.

## Proposed change

1. Draw all labels in a **separate SVG group appended after** the node group, so no circle can
   ever paint over any text.
2. Offset each label by the **node's own radius** plus a constant, rather than by a constant
   alone, so a data-scaled radius cannot swallow its own label.
3. Include an estimate of label width in the collision force so two labeled nodes are pushed
   apart enough to be readable at small N.
4. Mirror whichever rules are normative into `visualization-api-reference.md`, since they bind
   the chosen-language implementations.

## Acceptance criteria

- [ ] On a 2-entity graph with one multi-record entity, both entity names render fully legible
      with no glyph overlapped by any node circle.
- [ ] Labels are in a group painted after every circle, verified by asserting document order in
      the emitted SVG/JS rather than by eye.
- [ ] A guard rasterizes a small-N snapshot headless and asserts the label text is present in
      the pixels where it is expected — ⛔ **per INV-241, assert the pixels, not that the SVG
      contains the string**: the string was present in this defect's own DOM the whole time.
- [ ] Re-render at two different virtual-time budgets and confirm the result is stable, so a
      pass is not a settling coincidence.
- [ ] The rules that bind other languages appear in `visualization-api-reference.md`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — label group, radius-relative offset, collision radius
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — mirror the normative rules for other languages
- `tests/` — new pixel-level guard for small-N label legibility

## Source

- Feedback: `/dry-run` phase 2, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Low — cosmetic in the 2-entity case, but it damages an embedded keepsake artifact and the mechanism worsens as node radius grows with entity size
- MCP re-check: n/a (no Senzing fact) — this is a rendering defect in the plugin's own bundled server. The underlying resolution was correct: 4 records → 2 entities, 1 multi-record, which is the expected outcome for the fixture's shared DOB and address.
- Upstream: not applicable
- Related specs: `specs/visualization-legibility-at-production-scale.md` (implemented; the same tab at ~2,800 entities — this is the opposite end of the range and a different cause)


## Deviations from this spec, and why (2026-09-02)

⚠️ **Read this section before trusting the acceptance criteria as ticked.** Two of the six are
not runtime-verified in the form they are written, and the reported glyph clipping did not
reproduce here. The structural defect is nonetheless confirmed, and the margin was 3 px.

1. **The spec's first root-cause hypothesis is WRONG, and it is listed first.** "The label
   `<text>` offset relative to node radius — whether the offset is a constant while the radius is
   data-scaled" does not hold: the offset was already `radius(d)+11`, i.e. already radius-scaled.
   A node never occluded its own label. Hypothesis 2 is the cause — labels were a `<text>` child
   of each per-datum node group, so the emitted order is circle,text,circle,text and a later
   node's disc paints over an earlier node's label. Hypothesis 3 (collision ignores label extent)
   is a real contributing factor. Proposed change 2 was therefore a **no-op** and shipped as a
   comment recording that the offset was never the defect.

2. ⛔ **The visible clipping did not reproduce at this fixture and viewport — reported rather than
   papered over.** Rendered from a real Senzing repository (SDK 4.4.0, build 4.4.0.26242; the
   scaffold's 4 verification records resolving to 2 entities, one 3-record; 1440×900) the
   **committed** code produced both labels fully legible and symmetric about their anchors (1.2%
   and 1.3% asymmetry). So a pixel guard asserting "the label is fully visible" would have passed
   on the defective code, which is the guard-that-certifies-what-it-never-tested failure the
   dry-run rules forbid. What the same render *does* show is the mechanism, exactly: the smaller
   node's circle occupies **x 682–702 inside the larger node's label band** (y 537–551), and that
   label's glyphs begin at **x 705**. **3 pixels.** The spec's observation is this geometry with a
   layout that crossed the line rather than grazing it.

3. **So the pixel criterion is measured, not suite-guarded, and the harness is the durable half.**
   A pixel assertion needs Pillow, numpy, a headless browser, a live engine and a loaded
   repository; the suite is offline and stdlib-only (INV-108) and must not require any of them.
   `.claude/skills/dry-run/measure_label_occlusion.py` reports the minimum distance from any node
   marker to a *neighbor's* label glyphs, with `--fail-under`; it exits 1 on the pre-fix render and
   0 on the post-fix one. Measured: **3.0 px** before, **35.9 px** at an 8 s budget, **55.7 px**
   settled. The structural half — labels in their own layer, appended after the node group — is
   suite-guarded by document-order assertions and negative-controlled three ways.

4. **Criterion 4 is met in substance and NOT as literally worded.** "Re-render at two different
   virtual-time budgets and confirm the result is stable" — the 8 s and 30 s renders are **not**
   byte-identical once labels influence the layout, because the label-aware collision takes longer
   to settle than the previous force balance. 30 s and 60 s **are** byte-identical, so the layout
   is converged at the budget `capture_screenshots.py` actually uses for animated tabs (30 s), and
   the property being asserted holds at every budget (35.9 px at 8 s, 55.7 px at 30 s and 60 s).
   Stated rather than smoothed over, and the api-reference rule now warns that settling time
   changes once labels influence the layout.

5. ⛔ **A coupling the spec does not mention nearly made this a production-scale regression.**
   Labels default OFF above `LABEL_AUTO_OFF` (150 nodes), and that works by adding
   `hide-node-labels` to the container and letting CSS descend to `.node text`. Moving labels out
   of `.node` without moving the selector would have left **every label rendered** at exactly the
   scale the threshold exists for — silently undoing
   `visualization-legibility-at-production-scale`, which is implemented and whose evidence was
   2,799 entities / 4,464 relationships. Both CSS rules now name both groups, with a comment
   saying to keep them in step, and a guard fails if either drifts. Found by grepping for what
   else named the old selector.

6. **Four of my own changes broke other guards, and each was a real signal.**
   - A **code comment** containing the literal node-group class attribute was counted by
     `test_viz_tab_consolidation`, which counts rendered nodes in the dumped DOM — the JS is
     inlined into the served page, so the comment is part of the page's text. It reported 10 nodes
     for a 9-entity fixture. The comment was reworded and now warns the next author.
   - `test_graph_label_distinctness::test_the_full_name_is_reachable_on_hover` pinned the
     **syntax** — `.append("title")` chained directly onto the label's `.text(...)`. Holding the
     label selection for the tick handler puts the `<title>` on the next statement, so a change
     preserving the contract exactly failed it. Rescoped to the property, accepting either shape.
   - `specs/…` was cited in `visualization-api-reference.md`; `specs/` is never propagated to the
     public repo, so a shipped file may not point there. Removed.
   - **Four British spellings** (INV-253) in the new files — `neighbour`, `NEIGHBOUR`,
     `rasterisation`, `initialised`, `labelled`. The same lapse as earlier in this session.
   ⚠️ Also: the `⛔ **The natural structure is the defective one:**` rule needed its citation on
   **its own line**. The invariant-citation check the skill prescribes reported **0 uncited**
   while `tests/test_new_hard_rules_are_cited_or_deferred` correctly flagged it — the helper
   normalizes and truncates, the test does not. **Trust the test.**

## Invariants introduced

None. The rules established are mirrored into `visualization-api-reference.md` under the existing
visualization contract and cite **INV-090/INV-104/INV-124**, which already bind every language
implementation — that is precisely what the spec's own ⛔ asks for. Three normative bullets were
added there: labels painted after every node (with the natural-but-defective structure named),
collision sized from the label's extent and applied only while labels show, and whatever hides
labels must follow them into their new layer.
