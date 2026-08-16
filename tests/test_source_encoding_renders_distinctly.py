"""Two sources must never be DRAWN the same, and the legend must agree with the graph.

INV-127 forbids giving two present categories the same encoding. `color_for_sources`
satisfied that in the dict it returned and violated it on the canvas: the served JS drew a
stroke only when a source's wrap counter was non-zero, so the rendered space was 6 fills ×
4 stroke states = **24**. The 25th source came out identical to the 7th — measured at
`('#8b5cf6', '#18160F', 1.5)` for `SRC_006` and `SRC_024` — while every returned entry
still carried a distinct counter, so nothing looked wrong.

`tests/test_brand_sync.py` now asserts the rendered key at every size up to capacity, but
it computes that key in Python from the assignment. This file asserts it **in a browser**,
off the drawn SVG and the drawn legend, which is the only place the claim is actually about.
That distinction is the whole defect: the previous guard modelled the output and its model
diverged from the output.

Needs headless Chrome and skips without it.

Source spec: `specs/source-encoding-collides-past-twenty-four-sources.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "scripts")
SERVER = os.path.join(SCRIPTS, "senzing_viz_server.py")

#: Enough sources to reach EVERY channel on the canvas, which is the point of rendering at
#: all. With six fills: the second stroke width first appears at source 24 (the wrap where
#: the pre-fix code began repeating appearances), and the first fill-lightness step at
#: source 42. A count that stops short of 42 leaves the shading channel asserted only in
#: Python — the exact gap this file exists to close.
SOURCE_COUNT = 50


def find_chrome():
    for name in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    return None


def load_server():
    sys.path.insert(0, SCRIPTS)
    spec = importlib.util.spec_from_file_location("viz_server_encoding_test", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["viz_server_encoding_test"] = module
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(find_chrome(), "no headless Chrome/Chromium available")
class ThirtySourcesRenderThirtyAppearances(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_server()
        cls.sources = ["SRC_%03d" % i for i in range(SOURCE_COUNT)]
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.chrome = find_chrome()
        cls.dom = cls.render()

    @classmethod
    def render(cls):
        """One entity per source, so every source has a mark and a legend row."""
        entities = [
            {"entity_id": 1000 + i, "entity_name": "Entity %03d" % i,
             "record_count": 1, "data_sources": [code]}
            for i, code in enumerate(cls.sources)
        ]
        payload = {
            "stats": {"records_total": len(entities), "entities_total": len(entities),
                      "multi_record_entities": 0, "cross_source_entities": 0,
                      "relationships_total": 0, "data_sources_total": len(cls.sources),
                      "histogram": {"1": len(entities), "2": 0, "3": 0, "4+": 0},
                      "bucket_entities": {"1": [], "2": [], "3": [], "4+": []},
                      "sample_entities": []},
            "graph": {"nodes": entities, "edges": []},
            "merges": {"entities": []}, "records": {},
            "overlap": {"sources": cls.sources,
                        "matrix": [[1] * len(cls.sources) for _ in cls.sources]},
            "matchkeys": {"keys": []}, "features": {"features": []},
        }
        shim = ("<script>const __DATA__=" + cls.module._script_json(payload) + ";"
                "window.fetch=function(u){var p=u.split('?')[0].replace('/api/','');"
                "if(p==='search'){return Promise.resolve({json:function(){"
                "return Promise.resolve({results:[]});}});}"
                "return Promise.resolve({json:function(){"
                "return Promise.resolve(__DATA__[p]);}});};</script>")
        page = cls.module.render_page("Encoding", data_shim=shim, sources=cls.sources)
        path = Path(cls.tmp.name) / "encoding.html"
        path.write_text(page, encoding="utf-8")
        result = subprocess.run(
            [cls.chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--window-size=1400,900", "--virtual-time-budget=20000",
             "--dump-dom", path.as_uri()],
            capture_output=True, text=True, timeout=180,
        )
        return result.stdout

    # -- the marks ---------------------------------------------------------- #

    def drawn_circles(self):
        """(fill, stroke, stroke-width) for every node circle, as the DOM carries it.

        A stroke attribute the renderer chose to omit is absent from the DOM, which is
        exactly the "no stroke" state — so its absence is meaningful, not missing data.
        """
        out = []
        for tag in re.findall(r"<circle\b[^>]*>", self.dom):
            fill = re.search(r'\bfill="([^"]+)"', tag)
            if not fill:
                continue
            stroke = re.search(r'\bstroke="([^"]+)"', tag)
            width = re.search(r'\bstroke-width="([^"]+)"', tag)
            out.append((fill.group(1),
                        stroke.group(1) if stroke else None,
                        width.group(1) if width else None))
        return out

    def test_the_graph_actually_rendered(self):
        self.assertEqual(SOURCE_COUNT, len(self.drawn_circles()),
                         "expected one node circle per source; the graph did not draw")

    def test_every_drawn_appearance_is_unique(self):
        drawn = self.drawn_circles()
        counts = {}
        for key in drawn:
            counts[key] = counts.get(key, 0) + 1
        repeats = {k: n for k, n in counts.items() if n > 1}
        self.assertEqual(
            {}, repeats,
            "%d of %d sources share a drawn appearance: %s — this is the collision "
            "INV-127 forbids, and it is invisible to any check that reads the assigned "
            "map instead of the canvas"
            % (sum(repeats.values()), len(drawn), sorted(repeats)))

    def test_both_stroke_widths_reach_the_canvas(self):
        """A width channel that never varies on screen is not a channel."""
        widths = {w for _f, _s, w in self.drawn_circles() if w}
        self.assertGreater(len(widths), 1,
                           "only one stroke width was drawn (%s), so the third channel "
                           "does not render" % sorted(widths))

    def test_the_fill_shading_channel_reaches_the_canvas(self):
        """Past the stroke states, distinctness rests on the fill itself changing.

        Six base fills, so more than six drawn fills is the only evidence that the
        lightness perturbation is real rather than a value computed and discarded.
        """
        fills = {f for f, _s, _w in self.drawn_circles()}
        self.assertGreater(
            len(fills), 6,
            "only %d distinct fills were drawn from %d sources, so the shading channel "
            "never renders and distinctness above the stroke states is fictional"
            % (len(fills), SOURCE_COUNT))

    def test_some_source_is_drawn_with_no_stroke(self):
        """The bare state is one of the encodings; losing it narrows the space."""
        self.assertIn(None, {s for _f, s, _w in self.drawn_circles()},
                      "every source drew a stroke, so the first-cycle appearance changed")

    # -- the legend --------------------------------------------------------- #

    def legend_swatches(self):
        """(background, box-shadow) per legend dot, from the rendered style attribute."""
        out = []
        for tag in re.findall(r'<span class="dot"[^>]*>', self.dom):
            style = re.search(r'style="([^"]*)"', tag)
            if not style:
                out.append((None, None))
                continue
            text = style.group(1)
            bg = re.search(r"background(?:-color)?:\s*([^;]+)", text)
            shadow = re.search(r"box-shadow:\s*([^;]+)", text)
            out.append((bg.group(1).strip() if bg else None,
                        shadow.group(1).strip() if shadow else None))
        return out

    def test_the_legend_rendered_one_row_per_source(self):
        self.assertEqual(SOURCE_COUNT, len(self.legend_swatches()),
                         "the legend did not draw a row per source")

    def test_every_legend_swatch_is_unique(self):
        swatches = self.legend_swatches()
        counts = {}
        for key in swatches:
            counts[key] = counts.get(key, 0) + 1
        repeats = {k: n for k, n in counts.items() if n > 1}
        self.assertEqual(
            {}, repeats,
            "%d legend swatches are identical: %s — a bootcamper reading the legend "
            "cannot tell those sources apart" % (sum(repeats.values()), sorted(repeats)))

    def test_the_legend_carries_more_than_one_ring_width(self):
        """The swatch must mirror the node's width, not a hardcoded 1.5px."""
        # The ring width is box-shadow's SPREAD — the LAST length, after offset-x,
        # offset-y and blur. Two traps: matching the first `px` reads one of the zero
        # offsets and reports every ring as 0px, and Chrome serialises the computed value
        # as `rgb(...) 0px 0px 0px 1.5px inset` — colour first, `inset` last — so a pattern
        # anchored on a leading `inset` finds nothing at all. Anchor on the trailing one.
        spread = re.compile(r"([\d.]+)px\s+inset\b")
        widths = set()
        for _bg, shadow in self.legend_swatches():
            if shadow:
                found = spread.search(shadow)
                self.assertIsNotNone(
                    found, "could not read a spread radius from %r" % shadow)
                widths.add(found.group(1))
        self.assertGreater(
            len(widths), 1,
            "every legend ring is the same width (%s) while the nodes draw two, so the "
            "swatch and the mark describe different appearances" % sorted(widths))

    def test_the_legend_swatch_count_matches_the_mark_count(self):
        """Same encoding space on both surfaces, so neither can be the odd one out."""
        self.assertEqual(len(set(self.drawn_circles())),
                         len(set(self.legend_swatches())),
                         "the graph and the legend disagree on how many distinct "
                         "appearances exist")


if __name__ == "__main__":
    unittest.main()
