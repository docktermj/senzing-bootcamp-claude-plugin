"""A single-page deliverable must produce exactly one image, not zero.

`module-completion.md` told the guide to capture a single-page HTML deliverable — the Data
Quality, Mapping, and Transformation module's quality and mapping pages — "as one image, with
no `--tabs` argument". Following that captured **nothing**: `--tabs` defaults to the six-tab
app set, so an omitted `--tabs` requested all six, none of which exist on a single-page
document, and the helper exited having written no files. The same paragraph named the
consequence two sentences earlier while prescribing the invocation that caused it.

Nothing recovered it, either: graduation's orphaned-screenshot backfill embeds PNGs the recap
does not reference, and here no PNG existed to backfill.

The concept was missing from the helper, not merely mis-invoked — so `--single` exists, and a
page with no tab controls at all is captured whole rather than exiting empty. The INV-122
skip-and-report path is untouched for a **tabbed** app whose tab ids are merely wrong, because
capturing the whole page there would put the default tab in a file named for a tab it does not
show.

The capture assertions need headless Chrome and skip without it; the argument-handling and
path-naming assertions do not.

Source spec: `specs/single-page-capture-instruction-produces-zero-images.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
HELPER = SCRIPTS / "capture_screenshots.py"
MODULE_COMPLETION = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
                     / "bootcamp-onboarding" / "module-completion.md")

SINGLE_PAGE_HTML = (
    "<!doctype html><html><head><title>Data Quality Assessment</title></head>"
    "<body><h1>Data Quality Assessment</h1><p>Completeness 94%.</p></body></html>"
)

#: A tabbed app whose only tab id is one nobody asks for.
MISTABBED_HTML = (
    "<!doctype html><html><body>"
    "<button id='navbtn-alpha'>Alpha</button><section id='tab-alpha'>A</section>"
    "</body></html>"
)


def load_helper():
    spec = importlib.util.spec_from_file_location("capture_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_chrome():
    for name in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    return None


class TheHelperKnowsWhatASinglePageIs(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper()

    def test_the_single_page_id_is_not_a_tab(self):
        """`--tabs page` must stay an unknown id, so --single is the only route in."""
        self.assertNotIn(self.helper.SINGLE_PAGE_ID, self.helper.TABS,
                         "the single-page pseudo-id leaked into the tab inventory")
        with self.assertRaises(ValueError):
            self.helper.resolve_tabs(self.helper.SINGLE_PAGE_ID)

    def test_a_single_page_capture_has_no_slug_suffix(self):
        out = self.helper._out_path(Path("/x"), "data_quality_assessment",
                                    self.helper.SINGLE_PAGE_ID)
        self.assertEqual("data_quality_assessment.png", out.name,
                         "the single-page image must be {name}.png so the embed target "
                         "is predictable")

    def test_a_tabbed_capture_still_carries_its_slug(self):
        out = self.helper._out_path(Path("/x"), "viz", "graph")
        self.assertEqual("viz-entity-graph.png", out.name,
                         "the tabbed naming convention moved")

    def test_omitting_tabs_still_means_all_of_them(self):
        """The default is load-bearing: changing it would alter every existing call."""
        self.assertEqual(list(self.helper.DEFAULT_TABS), self.helper.resolve_tabs(""))

    def test_all_is_an_explicit_spelling_of_the_default(self):
        self.assertEqual(list(self.helper.DEFAULT_TABS), self.helper.resolve_tabs("all"))
        self.assertEqual(list(self.helper.DEFAULT_TABS), self.helper.resolve_tabs("ALL"))

    def test_tab_controls_are_detected(self):
        self.assertFalse(self.helper._has_tab_controls(SINGLE_PAGE_HTML),
                         "a page with no tab bar was reported as tabbed")
        self.assertTrue(self.helper._has_tab_controls(MISTABBED_HTML),
                        "a page with navbtn-/tab- ids was reported as untabbed, which "
                        "would turn a misnamed-tab skip into a whole-page capture")

    def test_an_unreadable_page_is_not_treated_as_untabbed(self):
        """Empty source means "could not read"; guessing single-page there would
        capture the whole page under a tab's name."""
        self.assertFalse(self.helper._has_tab_controls(""))


class TheCliRefusesAmbiguousCombinations(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.page = Path(self.tmp.name) / "single.html"
        self.page.write_text(SINGLE_PAGE_HTML, encoding="utf-8")

    def test_single_with_tabs_is_refused(self):
        code = self.helper.main(["--html", str(self.page), "--out-dir", self.tmp.name,
                                 "--name", "x", "--single", "--tabs", "graph"])
        self.assertEqual(1, code,
                         "--single and --tabs together must be refused rather than one "
                         "silently winning")


@unittest.skipUnless(find_chrome(), "no headless Chrome/Chromium available")
class CapturingRealPages(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"

    def page(self, name, html):
        path = Path(self.tmp.name) / name
        path.write_text(html, encoding="utf-8")
        return path

    def pngs(self):
        return sorted(p.name for p in self.out.glob("*.png"))

    def manifest(self, name):
        with open(self.out / f"{name}-tabs.json", encoding="utf-8") as handle:
            return json.load(handle)

    def test_single_produces_exactly_one_png(self):
        page = self.page("single.html", SINGLE_PAGE_HTML)
        code = self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                                 "--name", "data_quality_assessment", "--single"])
        self.assertEqual(0, code)
        self.assertEqual(["data_quality_assessment.png"], self.pngs())
        written = (self.out / "data_quality_assessment.png").read_bytes()
        self.assertEqual(b"\x89PNG\r\n\x1a\n", written[:8], "not a PNG")
        self.assertGreater(len(written), 1000, "the PNG is suspiciously small")

    def test_the_manifest_records_the_single_capture(self):
        """Graduation's coverage check reads this; an empty manifest reads as skipped."""
        page = self.page("single.html", SINGLE_PAGE_HTML)
        self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                          "--name", "dq", "--single"])
        manifest = self.manifest("dq")
        self.assertEqual(1, manifest["captured_count"])
        entry = manifest["captured"][0]
        self.assertEqual("dq.png", entry["file"])
        self.assertEqual("Full page", entry["label"])
        self.assertEqual([], manifest["failed"])
        self.assertEqual([], manifest["not_present"])

    def test_single_skips_the_tab_pre_flight_entirely(self):
        """`--single` is not merely a shortcut to the safety net.

        With the flag, no tab is ever requested, so the six "tab X is not present"
        reports do not happen. Without this assertion, deleting the `--single` branch
        passes every other test here — the safety net catches the same page and writes the
        same PNG — while every single-page capture goes back to failing six pre-flight
        checks and telling the reader about tabs the page was never going to have.
        """
        import contextlib
        import io

        page = self.page("single.html", SINGLE_PAGE_HTML)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with contextlib.redirect_stdout(io.StringIO()):
                code = self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                                         "--name", "dq", "--single"])
        self.assertEqual(0, code)
        self.assertNotIn("is not present in this visualization", stderr.getvalue(),
                         "--single still runs the tab pre-flight, so it is doing nothing "
                         "the safety net was not already doing")
        self.assertNotIn("Pass --single to say so explicitly", stderr.getvalue(),
                         "--single took the safety-net path, which advises passing the "
                         "flag that was already passed")

    def test_a_single_page_capture_makes_no_activation_copy(self):
        """There is no tab to activate, so injecting the activation script is waste.

        Pinned by making `_snapshot_copy` fail: a single-page capture must not reach it.
        Left unpinned, routing the single page through it passes — the injected script
        finds no tab, exhausts its retries, and the page still renders.
        """
        page = self.page("single.html", SINGLE_PAGE_HTML)
        original = self.helper._snapshot_copy

        def refuse(*args, **kwargs):
            raise AssertionError("a single-page capture must not make an activation copy")

        self.helper._snapshot_copy = refuse
        try:
            code = self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                                     "--name", "dq", "--single"])
        finally:
            self.helper._snapshot_copy = original
        self.assertEqual(0, code)
        self.assertEqual(["dq.png"], self.pngs())

    def test_a_tabless_page_without_the_flag_is_captured_anyway(self):
        """The reported invocation. It must no longer write zero files."""
        page = self.page("single.html", SINGLE_PAGE_HTML)
        code = self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                                 "--name", "dq"])
        self.assertEqual(0, code, "the no-flag invocation still fails")
        self.assertEqual(["dq.png"], self.pngs())

    def test_a_mistabbed_app_still_reports_and_skips(self):
        """INV-122 preserved: not replaced by a whole-page capture."""
        page = self.page("mistabbed.html", MISTABBED_HTML)
        code = self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                                 "--name", "mis", "--tabs", "graph,stats"])
        self.assertEqual(2, code, "a tabbed app with misnamed tabs must exit 2")
        self.assertEqual([], self.pngs(),
                         "a whole-page image was written under a tab-naming request, "
                         "which is the defect tab-naming exists to prevent")
        manifest = self.manifest("mis")
        self.assertEqual(0, manifest["captured_count"])
        self.assertEqual(["graph", "stats"],
                         sorted(e["tab"] for e in manifest["not_present"]))

    def test_the_tabbed_app_capture_is_unchanged(self):
        """Six images, same slugs and labels, by the same invocation as before."""
        page = self.page("tabbed.html", self.tabbed_app())
        code = self.helper.main(["--html", str(page), "--out-dir", str(self.out),
                                 "--name", "results_visualization"])
        self.assertEqual(0, code)
        self.assertEqual(
            sorted("results_visualization-%s.png" % self.helper.TABS[t][0]
                   for t in self.helper.DEFAULT_TABS),
            self.pngs(),
            "the tabbed app's six-image capture changed")

    def tabbed_app(self):
        """The real visualization page, rendered with a fetch shim."""
        spec = importlib.util.spec_from_file_location(
            "viz_for_capture_test", SCRIPTS / "senzing_viz_server.py")
        viz = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(SCRIPTS))
        spec.loader.exec_module(viz)
        srcs = ["CUSTOMERS", "REFERENCE", "WATCHLIST"]
        ents = [{"entity_id": 1000 + i, "entity_name": "Entity %d" % i,
                 "record_count": 1 + (i % 3), "data_sources": [srcs[i % 3]]}
                for i in range(9)]
        merges = [e for e in ents if e["record_count"] > 1]
        payload = {
            "stats": {"records_total": 18, "entities_total": len(ents),
                      "multi_record_entities": len(merges), "cross_source_entities": 2,
                      "relationships_total": 0, "data_sources_total": 3,
                      "histogram": {"1": 3, "2": 3, "3": 3, "4+": 0},
                      "bucket_entities": {"1": [], "2": [], "3": [], "4+": []},
                      "sample_entities": merges[:3]},
            "graph": {"nodes": ents, "edges": []},
            "merges": {"entities": [dict(e, records=[]) for e in merges]},
            "records": {},
            "overlap": {"sources": srcs, "matrix": [[3, 1, 0], [1, 3, 0], [0, 0, 3]]},
            "matchkeys": {"keys": []}, "features": {"features": []},
        }
        shim = ("<script>const __DATA__=" + viz._script_json(payload) + ";"
                "window.fetch=function(u){var p=u.split('?')[0].replace('/api/','');"
                "if(p==='search'){return Promise.resolve({json:function(){"
                "return Promise.resolve({results:[]});}});}"
                "return Promise.resolve({json:function(){"
                "return Promise.resolve(__DATA__[p]);}});};</script>")
        return viz.render_page("Fixture", data_shim=shim, sources=srcs)


class TheInstructionMatchesTheHelper(unittest.TestCase):
    def setUp(self):
        self.text = MODULE_COMPLETION.read_text(encoding="utf-8")
        self.flat = re.sub(r"\s+", " ", self.text)

    def test_it_prescribes_single(self):
        self.assertRegex(
            self.flat, r"(?i)capture it as \*?\*?one\s*image\*?\*? with `--single`",
            "module-completion still prescribes an invocation that captures nothing")

    def test_the_old_invocation_is_gone(self):
        self.assertNotIn("with no `--tabs` argument", self.flat,
                         "the instruction that produced zero images survives")

    def test_it_explains_why_omitting_tabs_is_not_none(self):
        self.assertRegex(
            self.flat,
            r"(?i)An omitted `--tabs` does not mean \"no tabs\", it means \*?\*?all\s*six",
            "the reason the old invocation failed is not stated, so a reader may "
            "reinvent it")

    def test_it_shows_a_runnable_command(self):
        self.assertIn("--single", self.text)
        self.assertRegex(self.text, r"python3 <helper> --html [^\n]*\n\s*--name \{name\} --single",
                         "no copyable single-page invocation is given")

    def test_it_names_the_output_file(self):
        self.assertRegex(self.flat, r"(?i)writes `\{name\}\.png`",
                         "the embed target is unstated, so the recap reference is a guess")

    def test_it_does_not_present_auto_detect_as_the_route(self):
        self.assertRegex(
            self.flat, r"(?i)Do not rely on that",
            "the safety net is described without saying it is a net, which invites "
            "dropping the flag")


if __name__ == "__main__":
    unittest.main()
