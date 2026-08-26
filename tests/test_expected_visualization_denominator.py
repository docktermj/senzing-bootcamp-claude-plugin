"""Tab coverage needs a denominator that does not come from the manifests.

`tab_coverage_problems` answers "did every captured tab reach the recap?" for each manifest it
is given, and `find_tab_manifests` supplies the manifests that exist. So its denominator is the
set of captures that HAPPENED -- and a module that captured nothing contributes no manifest, no
denominator, and no shortfall anything can see.

⛔ **The 2026-08-25 run, plugin 0.5.2.** `docs/visualizations/` held six
`truthset_verification-*.png` and their manifest, plus `entity_resolution.html` with no PNGs and
no manifest. The check reported:

    6 of 6 captured tabs reached the recap

A clean pass, measured against the only manifest that existed. The recap PDF illustrated the
whole bootcamp with pictures of the demo Truth Set while the Bootcamper's own resolved data --
their cross-source entities, their fraud leads -- appeared only as prose. That inverts which
work was theirs, in the artifact most likely to be shown to someone else.

⚠️ **This is INV-193's own failure shape, one level out.** INV-193 moved the completeness
denominator off the artifact being measured and onto the manifest. The manifest is external to
the recap -- but the SET of manifests is still derived from whatever capture produced, which is
the same self-referential shape one layer further out. The pre-existing `SKIPPED` branch fires
only when NO manifest exists, so with one present it never fired.

The denominator that closes it is already on disk and already read at graduation:
`modules_completed` in `config/bootcamp_progress.json`, mapped to the visualization each
producing module is specified to build.

⚠️ **Non-blocking by design (INV-048).** The requirement is that graduation STATES the
shortfall, by name and with the remedy -- not that it refuses to graduate. So these tests assert
exit code 0 with a `SKIPPED:` line and a withheld coverage figure, never a failure.

⛔ **Module 7's capture instruction is NOT re-stated and must not be.** It has existed since
2026-07-23, names the script, names `{name} = results_visualization`, and carries its own ⛔
against skipping. It was ignored anyway. A fourth copy is the state-it-once violation (INV-179)
and would not have changed that run; the defect fixed here is the silence afterward.

Source spec: `specs/tab-coverage-has-no-denominator-for-a-visualization-that-wrote-no-manifest.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
GENERATOR = SCRIPTS / "generate_recap_pdf.py"
GRADUATION = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "graduation" / "SKILL.md"

TABS = [
    ("graph", "entity-graph"),
    ("stats", "merge-statistics"),
    ("matchkeys", "match-keys"),
    ("features", "feature-scores"),
    ("overlap", "cross-source"),
    ("probe", "search-probe"),
]


def load_generator():
    spec = importlib.util.spec_from_file_location("recap_gen_denominator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GEN = load_generator()


def tiny_png(path):
    ihdr = struct.pack(">IIBBBBB", 4, 1, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data)))

    raw = b"\x00" + b"\xff\x00\x00" * 4
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def recap_text(names, slugs):
    """A recap embedding every captured tab of every captured visualization.

    Every name's images must be referenced, or the pre-existing per-manifest check fires
    a genuine captured-but-not-embedded shortfall and the fixture stops testing the
    thing it was built for.
    """
    first = names[0] if names else "truthset_verification"
    lines = [
        "# Bootcamp Recap", "",
        "## Truth Set visualization", "",
        "### Information Shared", "", "Loaded the Senzing Truth Set.", "",
        "### Questions & Responses", "", "- **Q:** Ready? **R:** Yes.", "",
        "### Actions Taken", "",
        "Captured the app's tabs. See docs/visualizations/%s.html" % first, "",
    ]
    for name in names:
        for slug in slugs:
            lines += ["![a tab](visualizations/%s-%s.png)" % (name, slug), ""]
    lines += [
        "### End-of-Module Summary", "",
        "**What you accomplished:** explored the Truth Set.", "",
        "**Why it matters:** it is the shared baseline.", "",
        "**Files produced:**", "",
        "- docs/visualizations/%s.html - the visualization" % first, "",
    ]
    return "\n".join(lines)


class Project:
    """A temp project reproducing the 2026-08-25 shape: one module captured, one not."""

    def __init__(self, completed, captured_names):
        self.completed = completed
        self.captured_names = captured_names

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.viz = root / "docs" / "visualizations"
        self.viz.mkdir(parents=True)
        (root / "config").mkdir()
        (root / "config" / "bootcamp_progress.json").write_text(
            json.dumps({"modules_completed": self.completed}), encoding="utf-8")
        slugs = [slug for _, slug in TABS]
        first = self.captured_names[0] if self.captured_names else "truthset_verification"
        for name in self.captured_names:
            for slug in slugs:
                tiny_png(self.viz / ("%s-%s.png" % (name, slug)))
            payload = {
                "schema": 1, "name": name,
                "requested": [tab for tab, _ in TABS],
                "captured": [{"tab": tab, "slug": slug,
                              "file": "%s-%s.png" % (name, slug), "label": tab}
                             for tab, slug in TABS],
                "not_present": [], "not_applicable": [], "failed": [],
            }
            payload["captured_count"] = len(payload["captured"])
            payload["requested_count"] = len(payload["requested"])
            (self.viz / ("%s-tabs.json" % name)).write_text(
                json.dumps(payload, indent=2), encoding="utf-8")
        self.recap = root / "docs" / "bootcamp_recap.md"
        self.recap.write_text(recap_text(self.captured_names, slugs), encoding="utf-8")
        self.root = root
        return self

    def check(self):
        return subprocess.run(
            [sys.executable, str(GENERATOR), "--input", str(self.recap), "--check",
             "--progress", "config/bootcamp_progress.json"],
            capture_output=True, text=True, cwd=str(self.root))

    def __exit__(self, *exc):
        self.tmp.cleanup()


BOTH = ["system_verification", "truthset_visualization", "data_processing",
        "query_visualize_discover"]


class TheDenominatorComesFromTheModulesThatRan(unittest.TestCase):
    def test_the_mapping_covers_both_visualizing_modules(self):
        self.assertEqual(
            {"truthset_visualization": "truthset_verification",
             "query_visualize_discover": "results_visualization"},
            GEN.MODULE_VISUALIZATIONS,
            "the module-to-visualization mapping changed; the denominator is only as "
            "complete as this table",
        )

    def test_expected_set_is_derived_from_completed_modules(self):
        self.assertEqual(["results_visualization", "truthset_verification"],
                         GEN.expected_visualizations(BOTH))

    def test_a_module_that_builds_no_visualization_expects_nothing(self):
        self.assertEqual([], GEN.expected_visualizations(["system_verification"]))

    def test_an_unreadable_progress_file_expects_nothing_rather_than_raising(self):
        """INV-048 — a missing progress file must never break the render."""
        for value in ("/nonexistent/progress.json",):
            with self.subTest(path=value):
                self.assertEqual([], GEN.read_completed_modules(Path(value)))

    def test_a_malformed_progress_file_expects_nothing_rather_than_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "p.json"
            for text in ("{not json", "[]", '{"modules_completed": "seven"}', "{}"):
                bad.write_text(text, encoding="utf-8")
                with self.subTest(text=text):
                    self.assertEqual([], GEN.read_completed_modules(bad))

    def test_manifest_names_prefer_the_name_field_and_fall_back_to_the_stem(self):
        self.assertEqual(
            {"a", "b"},
            GEN.manifest_names([{"name": "a"},
                                {"_path": "docs/visualizations/b-tabs.json"}]),
        )


class AMissingManifestIsReportedUnrunNotPassed(unittest.TestCase):
    """Criterion 7's two cases, end to end through the real --check."""

    def test_both_captured_passes_and_reports_coverage(self):
        with Project(BOTH, ["truthset_verification", "results_visualization"]) as p:
            result = p.check()
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotIn("SKIPPED: tab-coverage check for", result.stderr)
            self.assertIn("Tab coverage:", result.stdout)
            self.assertNotIn("Tab coverage NOT reported", result.stdout)

    def test_the_reported_shape_names_the_missing_visualization(self):
        """One manifest present, one expected visualization absent — the 2026-08-25 run."""
        with Project(BOTH, ["truthset_verification"]) as p:
            result = p.check()
            self.assertIn("SKIPPED:", result.stderr)
            self.assertIn("results_visualization", result.stderr)
            self.assertIn("query_visualize_discover", result.stderr,
                          "the report does not name the module that owed the capture")

    def test_it_says_the_check_was_not_measured_rather_than_passed(self):
        with Project(BOTH, ["truthset_verification"]) as p:
            stderr = p.check().stderr
            self.assertIn("NOT been measured", stderr)
            self.assertIn("not a pass", stderr)

    def test_the_coverage_figure_is_withheld_while_one_is_unaccounted_for(self):
        """⛔ The exact sentence that made the failing run look clean."""
        with Project(BOTH, ["truthset_verification"]) as p:
            stdout = p.check().stdout
            self.assertNotIn(
                "Tab coverage:", stdout,
                "a coverage figure is printed while an expected visualization has no "
                "manifest — true of the manifests that exist and false of the bootcamp",
            )
            self.assertIn("Tab coverage NOT reported", stdout)

    def test_it_states_the_backfill_remedy(self):
        with Project(BOTH, ["truthset_verification"]) as p:
            stderr = p.check().stderr
            self.assertIn("capture_screenshots.py", stderr)
            self.assertIn("--url", stderr)

    def test_it_is_not_blocking(self):
        """INV-048 — graduation always produces the recap; the shortfall is reported."""
        with Project(BOTH, ["truthset_verification"]) as p:
            self.assertEqual(0, p.check().returncode,
                             "a missing manifest made --check fail; graduation must state "
                             "the shortfall, not refuse")

    def test_the_no_manifest_branch_still_fires_when_nothing_was_captured(self):
        """The pre-existing check is unchanged."""
        with Project(BOTH, []) as p:
            stderr = p.check().stderr
            self.assertIn("no capture manifest", stderr)


class TheAnalysisIsNotVacuous(unittest.TestCase):
    """INV-265 — the fixture must actually distinguish the two outcomes."""

    def test_the_two_fixtures_differ_in_the_thing_under_test(self):
        with Project(BOTH, ["truthset_verification", "results_visualization"]) as both:
            complete = both.check().stdout
        with Project(BOTH, ["truthset_verification"]) as partial:
            incomplete = partial.check().stdout
        self.assertNotEqual(
            complete, incomplete,
            "the complete and incomplete fixtures produce identical output, so none of "
            "the assertions above distinguishes them",
        )

    def test_the_old_behavior_would_have_passed_the_failing_fixture(self):
        """Proof the defect was real: with no expected set, the run reports a clean pass."""
        with Project(BOTH, ["truthset_verification"]) as p:
            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--input", str(p.recap), "--check",
                 "--expect-visualizations", ""],
                capture_output=True, text=True, cwd=str(p.root))
            self.assertEqual(0, result.returncode)
            self.assertIn(
                "Tab coverage:", result.stdout,
                "with no expected set the run should reproduce the old clean pass; if it "
                "does not, this test no longer demonstrates what the fix changed",
            )
            self.assertNotIn("SKIPPED: tab-coverage check for", result.stderr)


class GraduationDocumentsTheDenominator(unittest.TestCase):
    def setUp(self):
        self.text = " ".join(GRADUATION.read_text(encoding="utf-8").split())

    def test_graduation_names_the_expected_visualization_denominator(self):
        self.assertIn("modules_completed", self.text)
        self.assertRegex(
            self.text, r"(?i)expected visualization",
            "graduation does not describe the expected-visualization denominator, so a "
            "reader cannot tell the per-manifest figure is not the whole answer",
        )

    def test_graduation_states_the_remedy(self):
        self.assertRegex(
            self.text, r"(?i)re-?start the app",
            "graduation does not state the backfill remedy for a missing manifest",
        )

    def test_graduation_keeps_the_recap_unconditional(self):
        """INV-048 — reported, not blocking."""
        self.assertRegex(self.text, r"(?i)not blocking|non-blocking|never blocks")


if __name__ == "__main__":
    unittest.main()
