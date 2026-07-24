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


if __name__ == "__main__":
    unittest.main()
