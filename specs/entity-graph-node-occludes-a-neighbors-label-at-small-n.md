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

