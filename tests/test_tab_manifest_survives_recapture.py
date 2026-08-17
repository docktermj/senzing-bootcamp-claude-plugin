"""Re-capturing one tab must not erase the record of the other five.

All six tabs of a results visualization were captured. The Search / Probe image came back
showing an empty result set — the query used a surname alone, which matched nothing — so
that one tab was re-captured on its own, and the manifest was rewritten from scratch:

    {"requested": ["probe"], "requested_count": 1, "captured_count": 1, ...}

⛔ **Graduation's coverage check then reports full coverage on a 1-of-1 denominator, and
would report it just as cheerfully if five of the six images had been lost.** The record of
their ever having been captured was destroyed by the fix for an unrelated problem.

⚠️ **Neither side of the check was wrong**, which is why this needed two changes. The
manifest is the only number in the system that does not come from the recap Markdown, so
the consumer has no second denominator to catch a truncated one: a partial write and a
complete write are indistinguishable in the format. So `write_manifest` now **merges**, and
`--check` grows a denominator the manifest cannot shrink — the PNGs on disk, which a
manifest write never touches. The merge fixes the mechanism; the cross-check is what
notices if the merge is ever bypassed, skipped, or undone.

Source spec: `specs/a-targeted-re-capture-truncates-the-tab-manifest.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
CAPTURE = SCRIPTS / "capture_screenshots.py"
GENERATOR = SCRIPTS / "generate_recap_pdf.py"

TABS_SIX = ["overview", "entity-graph", "cross-source", "quality", "network", "probe"]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CAP = load(CAPTURE, "capture_under_test_manifest")
GEN = load(GENERATOR, "recap_gen_manifest_under_test")


def write_run(out_dir, name, tabs, absent=(), missed=(), suppressed=()):
    """Run `write_manifest` as a capture invocation for `tabs` would."""
    written = []
    for tab in tabs:
        if tab in missed:
            continue
        path = CAP._out_path(Path(out_dir), name, tab)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x89PNG\r\n\x1a\n")
        written.append((path, "stub"))
    return CAP.write_manifest(Path(out_dir), name, list(tabs), list(absent),
                              written, list(missed), list(suppressed))


def read_manifest(out_dir, name):
    return json.loads(CAP.manifest_path(Path(out_dir), name).read_text(encoding="utf-8"))


class TheReportedSequence(unittest.TestCase):
    """Capture six tabs, then re-capture one. The manifest must still describe six."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.name = "results_visualization"
        write_run(self.tmp, self.name, TABS_SIX)

    def test_the_first_run_records_all_six(self):
        """Fixture control: if this fails, the re-capture assertion proves nothing."""
        manifest = read_manifest(self.tmp, self.name)
        self.assertEqual(6, manifest["captured_count"])

    def test_a_targeted_re_capture_keeps_the_other_five(self):
        write_run(self.tmp, self.name, ["probe"])
        manifest = read_manifest(self.tmp, self.name)
        self.assertEqual(
            6, manifest["captured_count"],
            "re-capturing one tab left the manifest describing "
            f"{manifest['captured_count']} — the other tabs' entries were erased")
        self.assertEqual(sorted(TABS_SIX),
                         sorted(e["tab"] for e in manifest["captured"]))

    def test_requested_is_the_union_not_the_last_run(self):
        write_run(self.tmp, self.name, ["probe"])
        manifest = read_manifest(self.tmp, self.name)
        self.assertEqual(sorted(TABS_SIX), sorted(manifest["requested"]))
        self.assertEqual(6, manifest["requested_count"])

    def test_the_re_captured_tab_is_replaced_not_duplicated(self):
        write_run(self.tmp, self.name, ["probe"])
        manifest = read_manifest(self.tmp, self.name)
        probes = [e for e in manifest["captured"] if e["tab"] == "probe"]
        self.assertEqual(1, len(probes), f"'probe' appears {len(probes)} times")


class ATabThatChangesOutcomeBetweenRunsHasOneEntry(unittest.TestCase):
    """⛔ The entry must move between lists, never appear in two of them."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.name = "viz"
        write_run(self.tmp, self.name, TABS_SIX)

    def _entries_for(self, tab):
        manifest = read_manifest(self.tmp, self.name)
        found = []
        for key in ("captured", "not_present", "not_applicable", "failed"):
            for entry in manifest.get(key, []):
                if entry.get("tab") == tab:
                    found.append(key)
        return found

    def test_captured_then_failed(self):
        write_run(self.tmp, self.name, ["probe"], missed=["probe"])
        self.assertEqual(["failed"], self._entries_for("probe"))

    def test_captured_then_suppressed(self):
        write_run(self.tmp, self.name, [], suppressed=["probe"])
        self.assertEqual(["not_applicable"], self._entries_for("probe"))

    def test_captured_then_absent(self):
        write_run(self.tmp, self.name, [], absent=["probe"])
        self.assertEqual(["not_present"], self._entries_for("probe"))

    def test_an_untouched_tab_keeps_its_original_entry(self):
        write_run(self.tmp, self.name, ["probe"], missed=["probe"])
        self.assertEqual(["captured"], self._entries_for("overview"))


class ACorruptPriorManifestIsReportedAndOverwritten(unittest.TestCase):
    """INV-122 — a merge that could fail the run would be worse than the defect."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.name = "viz"

    def test_unparseable_prior_is_overwritten_and_the_run_succeeds(self):
        CAP.manifest_path(Path(self.tmp), self.name).write_text("{not json",
                                                                encoding="utf-8")
        self.assertTrue(write_run(self.tmp, self.name, ["probe"]))
        self.assertEqual(1, read_manifest(self.tmp, self.name)["captured_count"])

    def test_schema_mismatch_is_overwritten_and_the_run_succeeds(self):
        CAP.manifest_path(Path(self.tmp), self.name).write_text(
            json.dumps({"schema": "something-else", "captured": [{"tab": "x"}]}),
            encoding="utf-8")
        self.assertTrue(write_run(self.tmp, self.name, ["probe"]))
        manifest = read_manifest(self.tmp, self.name)
        self.assertEqual(1, manifest["captured_count"])
        self.assertEqual(CAP.MANIFEST_SCHEMA, manifest["schema"])

    def test_a_merge_never_raises_on_a_prior_with_odd_shapes(self):
        CAP.manifest_path(Path(self.tmp), self.name).write_text(
            json.dumps({"schema": CAP.MANIFEST_SCHEMA, "name": self.name,
                        "requested": ["a", 7, None], "captured": ["not-a-dict", {}]}),
            encoding="utf-8")
        self.assertTrue(write_run(self.tmp, self.name, ["probe"]))


class TheCheckHasADenominatorTheManifestCannotShrink(unittest.TestCase):
    """The guard that survives the merge being bypassed."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.name = "results_visualization"
        write_run(self.tmp, self.name, TABS_SIX)
        self.manifest = CAP.manifest_path(Path(self.tmp), self.name)

    def _problems(self):
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["_path"] = str(self.manifest)
        return GEN.manifest_undercount_problems([data])

    def test_a_complete_manifest_reports_nothing(self):
        self.assertEqual([], self._problems())

    def test_a_truncated_manifest_is_reported_with_both_figures(self):
        """⛔ Exactly the state the reported run ended in — six PNGs, a 1-tab manifest."""
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["captured"] = [e for e in data["captured"] if e["tab"] == "probe"]
        data["captured_count"] = 1
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        problems = self._problems()
        self.assertEqual(1, len(problems), problems)
        self.assertIn("records 1 captured tab(s)", problems[0])
        self.assertIn("6 results_visualization-*.png", problems[0])

    def test_it_reaches_the_check_command(self):
        """End-to-end: the real CLI reports it, not just the helper."""
        docs = Path(self.tmp) / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        viz = docs / "visualizations"
        viz.mkdir(parents=True, exist_ok=True)
        for tab in TABS_SIX:
            (viz / f"{self.name}-{tab}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (viz / f"{self.name}-tabs.json").write_text(json.dumps({
            "schema": CAP.MANIFEST_SCHEMA, "name": self.name,
            "requested": ["probe"], "requested_count": 1, "captured_count": 1,
            "captured": [{"tab": "probe", "slug": "probe",
                          "file": f"{self.name}-probe.png", "label": "Probe"}],
            "not_present": [], "not_applicable": [], "failed": [],
        }), encoding="utf-8")
        (docs / "bootcamp_recap.md").write_text(RECAP, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            capture_output=True, text=True, cwd=self.tmp, timeout=120)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(0, proc.returncode,
                            f"--check passed on an undercounting manifest:\n{out}")
        self.assertIn("undercounts", out, out)


RECAP = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-08-16

## Query, Visualize and Discover — 2026-08-16

### Objectives

- Query the resolved entities.

### Information Shared

- The engine explains every decision.

### Questions & Responses

- Asked which entity to inspect; answered "the largest".

### Actions Taken

- Captured the results visualization.

![Probe](visualizations/results_visualization-probe.png)

### Key Learnings

- A match key explains itself if you ask it.

### End-of-Module Summary

**What you accomplished:**

- Queried the data.

**Files produced:**

- `docs/visualizations/results_visualization.html` — the app.

**Why it matters:** it is the payoff.
"""


if __name__ == "__main__":
    unittest.main()
