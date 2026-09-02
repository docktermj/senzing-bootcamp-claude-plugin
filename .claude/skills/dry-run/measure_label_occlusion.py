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

Reference measurements — Senzing 4.4.0 (build 4.4.0.26242), the scaffold's 4 verification records
resolving to 2 entities (one 3-record), 1440x900:

    committed code before the fix, converged      3.0 px
    labels in their own layer + label-aware collide, 8s budget    35.9 px
    same, 30s budget (settled; 30s == 60s byte-identical)         55.7 px

⚠️ **The reported glyph clipping did not reproduce at that fixture and viewport** — the layout
cleared the band by 3 px instead of crossing it. Treat a small number as the finding, not only a
visibly clipped name: 3 px is the same defect with a luckier layout, and node positions move with
viewport size, entity count and record counts.

Usage:

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


def _markers(np, arr, fill_rgb, min_px):
    """[(cx, cy, r, xs, ys)] for each blob of the marker fill color."""
    fill = (abs(arr - np.array(fill_rgb)).sum(axis=2) < 40)
    ys, xs = np.nonzero(fill)
    if not len(ys):
        return []
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]
    groups, cur = [], [0]
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] > 10:
            groups.append(cur)
            cur = []
        cur.append(i)
    groups.append(cur)
    out = []
    for g in groups:
        gx, gy = xs[g], ys[g]
        if len(g) < min_px:
            continue                    # legend swatches and antialiasing specks
        r = max(gx.max() - gx.min() + 1, gy.max() - gy.min() + 1) // 2
        out.append((int(gx.mean()), int(gy.mean()), int(r), gx, gy))
    return out


def measure(png, fill_rgb, min_px=150, ink_below=250):
    np, arr = _load(png)
    ink = (arr.sum(axis=2) < ink_below)
    markers = _markers(np, arr, fill_rgb, min_px)
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
                    help="node marker fill, from color_for_sources() (default: %(default)s)")
    ap.add_argument("--fail-under", type=float, default=None,
                    help="exit 1 if the clearance is below this many pixels")
    ap.add_argument("--min-marker-px", type=int, default=150,
                    help="ignore fill blobs smaller than this — legend swatches (default: "
                         "%(default)s)")
    args = ap.parse_args(argv)

    hexs = args.fill.lstrip("#")
    rgb = tuple(int(hexs[k:k + 2], 16) for k in (0, 2, 4))
    worst, detail, n_markers, pairs = measure(args.png, rgb, args.min_marker_px)

    print("markers found: %d   marker/label pairs compared: %d   fill %s" % (n_markers, pairs, rgb))
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
