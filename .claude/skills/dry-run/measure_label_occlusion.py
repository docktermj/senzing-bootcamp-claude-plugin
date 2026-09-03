#!/usr/bin/env python3
"""Measure, in pixels, how close a graph node's marker comes to a NEIGHBOR's label glyphs.

Phase 2 helper for the Entity Graph tab. Lives here rather than in ``tests/`` because it needs
Pillow, a headless browser, a live Senzing engine and a loaded repository — and the repo suite is
offline and stdlib-only (INV-108), so it must not require any of them. The structural half of the
same contract *is* suite-guarded, in ``tests/test_graph_labels_paint_after_circles.py``.

⛔ **Why a pixel measurement at all (INV-241).** The occluded label's string was present in the
DOM the whole time — only glyphs were missing from the image. Asserting the SVG contains the text
would have passed on the defect. What matters is whether the text SURVIVES rasterization.

What it reports: for every node, the label band is the strip at ``cy + r + 11`` (the offset the
renderer uses); for every *other* node, the minimum distance from that node's marker pixels to
this label's ink. A small number means a marker is grazing or covering a neighbor's name.

Reference measurements — Senzing 4.4.0 (build 4.4.0.26242).

**2 entities** (the scaffold's 4 verification records), 1440x900, minimum marker-to-neighbor-glyph
clearance:

    committed code before the 2026-09-02 fix, converged      3.0 px
    labels in their own layer + label-aware collide, 8s     35.9 px
    same, 30s budget (settled; 30s == 60s byte-identical)   55.7 px

**85 entities** (the full Truth Set: 159 records over CUSTOMERS/REFERENCE/WATCHLIST, 54 merged,
17 cross-source, 65 relationships), 1440x900, **2026-09-03**. Here the clearance metric is the
wrong tool and the paint-order diff is the right one — see the ⛔ below:

    glyph pixels a node circle covers when labels paint first   1,713
    labels losing glyph pixels                                31 of 85
    worst single label ("Margaret Charney")                     324 px

⛔ **Clearance is only meaningful where paint order is the hazard.** Once labels are in their own
layer a circle overlapping a label's box is expected and harmless — the text draws on top — so a
clearance of 0 is not a defect, and on the 85-entity graph this reported 0.0 px against correct
code. Worse, at that density a +-170px band around one node contains several neighbors' labels
(a measured span of 244px for a <=20-character label), so the "label" being measured is not one
label. **At more than a handful of nodes, measure paint order directly instead:** render twice
from identical code and data, with the label layer created BEFORE the node group in one of them,
and diff the text masks. That is what produced the 85-entity figures above.

⛔ **Three traps, each of which produced a confident wrong answer on 2026-09-03 before being
caught. Check all three before trusting any number.**

1. **The render must be DETERMINISTIC at the budget you use.** At 85 nodes the shipped 30s
   animated-tab budget has not converged: two captures of *identical* code differed by 5,326
   pixels in the same "lost text" sense — larger than any effect being measured. 120s was
   byte-identical. Always run the same file twice first and require 0 differing pixels; a diff
   below the noise floor is not a finding. (The 30s shortfall is a plugin defect in its own
   right, not just a measurement nuisance — `specs/graph-capture-budget-does-not-converge-at-truth-set-density.md`.)
2. **A hand-built "before" variant must be shown to RENDER.** Editing the tick handler to remove
   the label positioning left `<g class="node">` elements with no `transform` at all — nodes
   created, never positioned — and diffing a working render against a broken one shows a large,
   entirely spurious difference. Dump the DOM and require the expected number of
   `class="node" transform="translate(` matches. The safe edit is to MOVE the label-layer block
   above the node group and change nothing else.
3. **Injecting JS into the snapshot does NOT survive the capture path.** A `setInterval` appended
   before `</body>` applied under `--dump-dom` and had no effect under
   `capture_screenshots.py` — a control that tripled every circle radius changed the text mask by
   0 pixels, which is how the injection was caught. Verify any injected manipulation with a
   control that MUST change pixels, or make the change in the server code instead.

⚠️ **Confirm the layout is identical before attributing a diff to paint order.** Compare all
`class="node" transform="translate(...)"` strings between the two DOMs and require an exact
match, and require the "gained" pixel count (text in the flipped render that is not text in the
original) to be **0**. Both were 0/identical for the 85-entity figures; a nonzero "gained" count
means positions moved and the "lost" count is measuring layout drift, not occlusion.

Usage:Usage:

    python3 measure_label_occlusion.py <graph-tab.png> [--fill '#8b5cf6'] [--fail-under 12]

Get the PNG with ``capture_screenshots.py --html <snapshot> --tabs graph``. The fill color is the
node marker's, from ``brand_tokens.color_for_sources()`` for the data source in the snapshot —
pass it explicitly, because guessing the dominant saturated color picks up UI accents instead
(it did, on the first attempt here).

Exit codes: 0 measured (and above ``--fail-under`` if given), 1 measured but below the floor,
2 could not measure (no markers or no labels found).
"""

import argparse
import sys


def _load(png):
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:                      # pragma: no cover - dev-only helper
        sys.stderr.write(
            "needs Pillow and numpy: %s\nThis is a phase-2 helper, not part of the offline "
            "suite — install them in the dry-run environment only.\n" % exc
        )
        raise SystemExit(2)
    return np, np.array(Image.open(png).convert("RGB")).astype(int)


def _label_components(np, mask):
    """Two-pass connected-component labeling over a boolean mask, 8-connected.

    ⚠️ **Replaced a 1-D x-gap clustering that only worked on a toy fixture.** The first version
    sorted marker pixels by x and split on a gap of >10px, which is adequate for two or three
    well-separated nodes and silently merges neighbors in a real graph — on the 85-entity Truth
    Set it would have reported a handful of enormous "markers" and measured nothing. The
    single-source, 2-entity fixture hid the need for this completely.

    scipy is not available here (and the dry-run environment should not need it), so this is a
    compact union-find: label each row's runs, union them with overlapping runs on the previous
    row, then resolve. Linear in the number of runs rather than in pixels.
    """
    h, w = mask.shape
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    runs_by_row, next_id = [], 0
    for y in range(h):
        row = mask[y]
        if not row.any():
            runs_by_row.append([])
            continue
        idx = np.flatnonzero(row)
        breaks = np.flatnonzero(np.diff(idx) > 1)
        starts = np.concatenate(([idx[0]], idx[breaks + 1]))
        ends = np.concatenate((idx[breaks], [idx[-1]]))
        runs = []
        for s, e in zip(starts, ends):
            parent[next_id] = next_id
            runs.append((int(s), int(e), next_id))
            next_id += 1
        # 8-connected: a run touches a previous-row run whose span overlaps by >= -1
        for s, e, rid in runs:
            for ps, pe, pid in runs_by_row[-1] if runs_by_row else []:
                if ps <= e + 1 and s <= pe + 1:
                    union(rid, pid)
        runs_by_row.append(runs)

    groups = {}
    for y, runs in enumerate(runs_by_row):
        for s, e, rid in runs:
            groups.setdefault(find(rid), []).append((y, s, e))
    return groups


def _markers(np, arr, fills, min_px):
    """[(cx, cy, r, xs, ys)] for each connected blob of any marker fill color.

    ⚠️ **`fills` is a LIST.** A real graph colors nodes by their whole source set, so the Truth
    Set renders seven distinct fills (`CUSTOMERS`, `CUSTOMERS|REFERENCE`, … ) — one color is only
    ever enough for a single-source fixture. Blobs are found per color and then measured against
    every other blob regardless of color, because occlusion does not care which source a
    neighboring node came from.
    """
    out = []
    for fill_rgb in fills:
        mask = (abs(arr - np.array(fill_rgb)).sum(axis=2) < 40)
        if not mask.any():
            continue
        for pixels in _label_components(np, mask).values():
            xs, ys = [], []
            for y, s, e in pixels:
                xs.extend(range(s, e + 1))
                ys.extend([y] * (e - s + 1))
            if len(xs) < min_px:
                continue                # legend swatches and antialiasing specks
            xs, ys = np.array(xs), np.array(ys)
            r = max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1) // 2
            out.append((int(xs.mean()), int(ys.mean()), int(r), xs, ys))
    return out


def measure(png, fills, min_px=150, ink_below=250):
    np, arr = _load(png)
    ink = (arr.sum(axis=2) < ink_below)
    markers = _markers(np, arr, fills, min_px)
    worst, detail, pairs = None, "", 0
    for i, (cx, cy, r, _gx, _gy) in enumerate(markers):
        base = cy + r + 11                          # the renderer's own label offset
        top = max(0, base - 10)
        cols = np.nonzero(ink[top:base + 4, :].any(axis=0))[0]
        label = cols[(cols > cx - 170) & (cols < cx + 170)]
        if not len(label):
            continue                                # labels hidden, or this node has none
        lx0, lx1 = int(label.min()), int(label.max())
        for j, (ox, oy, orr, ogx, ogy) in enumerate(markers):
            if i == j:
                continue
            pairs += 1
            dx = np.maximum(0, np.maximum(lx0 - ogx, ogx - lx1))
            dy = np.maximum(0, np.maximum(top - ogy, ogy - (base + 4)))
            d = float(np.sqrt(dx * dx + dy * dy).min())
            if worst is None or d < worst:
                worst = d
                detail = ("marker@(%d,%d) r%d vs the label of node@(%d,%d) [x %d..%d]"
                          % (ox, oy, orr, cx, cy, lx0, lx1))
    return worst, detail, len(markers), pairs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("png")
    ap.add_argument("--fill", default="#8b5cf6",
                    help="node marker fill(s), comma-separated, from color_for_sources(). A "
                         "multi-source graph uses one color per SOURCE SET, so pass them all "
                         "(default: %(default)s)")
    ap.add_argument("--fail-under", type=float, default=None,
                    help="exit 1 if the clearance is below this many pixels")
    ap.add_argument("--min-marker-px", type=int, default=150,
                    help="ignore fill blobs smaller than this — legend swatches (default: "
                         "%(default)s)")
    args = ap.parse_args(argv)

    fills = []
    for one in args.fill.split(","):
        hexs = one.strip().lstrip("#")
        fills.append(tuple(int(hexs[k:k + 2], 16) for k in (0, 2, 4)))
    worst, detail, n_markers, pairs = measure(args.png, fills, args.min_marker_px)

    print("markers found: %d   marker/label pairs compared: %d   %d fill(s)"
          % (n_markers, pairs, len(fills)))
    if worst is None:
        print("⛔ could not measure — no marker/label pair found.")
        print("   Check the fill color (pass --fill) and that node labels are not hidden: they")
        print("   default OFF above LABEL_AUTO_OFF nodes, and a graph with them off has nothing")
        print("   to measure. This is NOT a pass.")
        return 2
    print("minimum clearance: %.1f px" % worst)
    print("   %s" % detail)
    print("   reference: 3.0 px before the 2026-09-02 fix, 55.7 px after (settled).")
    if args.fail_under is not None and worst < args.fail_under:
        print("⛔ below the %.1f px floor — a marker is grazing or covering a neighbor's name."
              % args.fail_under)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
