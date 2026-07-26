"""Guard against silent drift between brand_tokens.py and the inlined fallback
palettes in senzing_viz_server.py and generate_recap_pdf.py.

Each script keeps a hardcoded copy of the brand palette so it still renders if
brand_tokens.py is unavailable. The runtime prefers the imported values whenever
brand_tokens loads, so a stale fallback is never exercised in practice — and would
drift undetected. Here brand_tokens IS importable, so the live module globals are
the brand_tokens-derived values; asserting they equal the named fallback copies
proves the fallbacks are in sync with the source of truth.

Run:  python3 -m unittest discover -s tests
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "scripts")
sys.path.insert(0, SCRIPTS)


class BrandTokenSync(unittest.TestCase):
    def test_brand_tokens_importable(self):
        import brand_tokens  # noqa: F401  (fixture: the whole suite assumes this)

    def test_viz_server_fallback_in_sync(self):
        import senzing_viz_server as viz
        self.assertEqual(viz._BRAND, viz._FALLBACK_BRAND)
        self.assertEqual(viz.SOURCE_COLORS, viz._FALLBACK_SOURCE_COLORS)
        self.assertEqual(viz.FALLBACK_COLORS, viz._FALLBACK_COLORS)

    def test_recap_pdf_fallback_in_sync(self):
        import generate_recap_pdf as recap
        for name, rgb in recap._FALLBACK_RGB.items():
            self.assertEqual(getattr(recap, name), rgb,
                             f"{name} fallback diverged from brand_tokens.py")

    def test_source_stroke_fallback_in_sync(self):
        import senzing_viz_server as viz
        self.assertEqual(viz.SOURCE_STROKES, viz._FALLBACK_STROKES)


class SourceColorsComeFromTheData(unittest.TestCase):
    """`SOURCE_COLORS` names the Truth Set's sources, and no bootcamper uses those names
    for their own data — so a name-keyed lookup dropped every real source to one identical
    fallback color, in the module where cross-source structure is the point. Colors must be
    assigned from the sources actually present."""

    def setUp(self):
        import brand_tokens
        self.bt = brand_tokens
        self.assign = brand_tokens.color_for_sources

    def fills(self, sources):
        m = self.assign(sources)
        return [m[s]["fill"] for s in sorted(sources)]

    def test_the_reported_case_gets_distinct_colors(self):
        sources = ["PPP_LOANS", "EQUIFAX", "NOMINO-RISK"]
        fills = self.fills(sources)
        self.assertEqual(len(sources), len(set(fills)), f"sources collapsed to {set(fills)}")

    def test_truth_set_keeps_its_preferred_assignment(self):
        """The Truth Set visualization must not regress."""
        m = self.assign(["CUSTOMERS", "REFERENCE", "WATCHLIST"])
        for code, expected in self.bt.SOURCE_COLORS.items():
            with self.subTest(code=code):
                self.assertEqual(expected, m[code]["fill"])

    def test_mixed_model_never_reuses_a_preferred_color(self):
        m = self.assign(["CUSTOMERS", "PPP_LOANS", "EQUIFAX"])
        fills = [v["fill"] for v in m.values()]
        self.assertEqual(3, len(set(fills)))
        self.assertEqual(self.bt.SOURCE_COLORS["CUSTOMERS"], m["CUSTOMERS"]["fill"])

    def test_assignment_is_deterministic(self):
        """A rebuilt snapshot must match the screenshot the recap already describes."""
        self.assertEqual(self.assign(["C", "A", "B"]), self.assign(["B", "C", "A"]))

    def test_more_sources_than_colors_stay_distinguishable(self):
        sources = [f"SRC{i}" for i in range(len(self.bt.FALLBACK_COLORS) + 3)]
        m = self.assign(sources)
        pairs = {(v["fill"], v["stroke"]) for v in m.values()}
        self.assertEqual(len(sources), len(pairs), "a second channel must distinguish the repeat")

    def test_signal_green_is_never_a_source_color(self):
        m = self.assign([f"S{i}" for i in range(30)])
        self.assertNotIn(self.bt.SIGNAL_GREEN, {v["fill"] for v in m.values()})

    def test_empty_and_blank_inputs_are_safe(self):
        self.assertEqual({}, self.assign([]))
        self.assertEqual({}, self.assign(None))
        self.assertEqual({}, self.assign(["", "  "]))

    def test_viz_server_inline_fallback_matches_the_token_helper(self):
        """The import-failure path must behave identically, not merely exist."""
        import senzing_viz_server as viz
        sources = ["CUSTOMERS", "PPP_LOANS", "EQUIFAX", "NOMINO-RISK"]
        self.assertEqual(self.assign(sources), viz.color_for_sources(sources))


class VizServerUsesTheAssignedColors(unittest.TestCase):
    def setUp(self):
        import senzing_viz_server as viz
        self.viz = viz

    def test_rendered_page_carries_a_per_source_map(self):
        import re
        page = self.viz.render_page("T", sources=["PPP_LOANS", "EQUIFAX", "NOMINO-RISK"])
        payload = re.search(r"const SRC_COLORS=(\{.*?\});", page).group(1)
        for code in ("PPP_LOANS", "EQUIFAX", "NOMINO-RISK"):
            with self.subTest(code=code):
                self.assertIn(code, payload)
        self.assertIn('"fill"', payload)
        self.assertIn('"stroke"', payload)

    def test_no_hardcoded_single_fallback_remains(self):
        """`SRC_COLORS[src]||"#8b5cf6"` is what made every source one color."""
        page = self.viz.render_page("T", sources=["A", "B"])
        self.assertNotIn('SRC_COLORS[src]||"#8b5cf6"', page)

    def test_unassigned_source_is_visually_distinct_from_assigned_ones(self):
        """"Unassigned" must not masquerade as a real category."""
        page = self.viz.render_page("T", sources=["A", "B", "C"])
        self.assertIn("UNKNOWN_SRC", page)
        self.assertNotIn(f'UNKNOWN_SRC="{self.viz.FALLBACK_COLORS[0]}"', page)

    def test_fallback_colors_are_actually_consumed(self):
        """The palette existed but was dead code; the defect was that nothing used it."""
        page = self.viz.render_page("T", sources=["ONE", "TWO"])
        self.assertIn(self.viz.FALLBACK_COLORS[0], page)

    def test_model_reports_its_data_sources_sorted(self):
        model = self.viz.Model()
        model.entities = {
            1: {"data_sources": ["WATCHLIST", "CUSTOMERS"]},
            2: {"data_sources": ["CUSTOMERS", ""]},
        }
        self.assertEqual(["CUSTOMERS", "WATCHLIST"], model.data_sources())


if __name__ == "__main__":
    unittest.main()
