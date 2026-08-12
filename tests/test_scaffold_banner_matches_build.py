"""The dry-run scaffold's fixture banner describes the mode it actually built.

`scaffold_project.py`'s banner exists to tell the operator what the project exercises, and
`dry-run/SKILL.md` introduces it as "The scaffold prints which fixture exercises which
invariant. Each one is there because a naive fixture hid a defect." It was a **static** list
printed in all three modes, while `build()` branches: `--fresh`/`--seeded` write two config
files, the default mid-bootcamp path writes six.

Run with `--fresh` on 2026-08-12 the banner claimed 8 fixtures over a 4-file project, and one
claim was not merely stale but **inverted** — it described `bootcamp_preferences.yaml` as
carrying "saved verbosity + language to test honor-don't-ask (INV-133)" when in `--fresh` that
file is deliberately empty, which is the entire point of the mode. `phase3-conversational.md`
is explicit that a walk where everything was asked exercises the honor path "only in its inert
direction", which is why a separate `--seeded` walk exists at all. A banner claiming otherwise
invites exactly the false conclusion that doc was written to prevent.

That matters more than tooling polish usually would: `dry-run/SKILL.md` requires a report to
"State the coverage limits explicitly" and calls an unstated limit "the difference between a
report and a false clean bill of health". The banner is the operator's primary input for
writing that section, and in two of three modes it inflated it.

The fix is structural rather than a corrected list. Each `FIXTURE_MAP` row carries the modes
it applies to **and** the project-relative path it describes, so the tests below can build a
real project per mode and compare the banner against the filesystem in both directions:
nothing is described that was not written, and nothing is written that is not described. A
future fixture added to `build()` without a banner row fails here, which a corrected static
list would not have prevented.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import io
import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = REPO_ROOT / ".claude" / "skills" / "dry-run" / "scaffold_project.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scaffold = load(SCAFFOLD, "scaffold_project_banner")

#: (mode, fresh, seeded) — the three ways build() can be invoked.
INVOCATIONS = (("mid", False, False), ("fresh", True, False), ("seeded", False, True))


def built_files(root):
    """Project-relative POSIX paths of every file build() wrote."""
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def build_in_mode(fresh, seeded):
    """Build into a temp dir and return (root_paths, banner_text). Caller owns nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "project"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scaffold.build(root, fresh, seeded)
        return built_files(root), buf.getvalue()


class TheBannerMatchesTheFilesystem(unittest.TestCase):
    """Both directions, in every mode — this is what makes the banner drift-proof."""

    def test_every_described_fixture_exists(self):
        for mode, fresh, seeded in INVOCATIONS:
            with self.subTest(mode=mode):
                files, _ = build_in_mode(fresh, seeded)
                described = {row[1] for row in scaffold.fixtures_for(mode) if row[1]}
                missing = sorted(described - files)
                self.assertEqual(
                    [], missing,
                    f"--{mode} banner describes fixtures the mode does not create: {missing}",
                )

    def test_every_written_file_is_described(self):
        for mode, fresh, seeded in INVOCATIONS:
            with self.subTest(mode=mode):
                files, _ = build_in_mode(fresh, seeded)
                described = {row[1] for row in scaffold.fixtures_for(mode) if row[1]}
                undescribed = sorted(files - described)
                self.assertEqual(
                    [], undescribed,
                    f"--{mode} writes files the banner never mentions, so the operator "
                    f"cannot know they are exercised: {undescribed}",
                )

    def test_the_printed_banner_names_the_mode(self):
        for mode, fresh, seeded in INVOCATIONS:
            with self.subTest(mode=mode):
                _, out = build_in_mode(fresh, seeded)
                self.assertIn(mode, out)


class FreshNoLongerOverClaims(unittest.TestCase):
    """The specific false lines from the 2026-08-12 run, pinned as absent."""

    MID_ONLY = (
        "docs/bootcamp_recap.md",
        "docs/progress/recap_checkpoint.md",
        "docs/loading_strategy.md",
        "src/system_verification/records.jsonl",
    )

    def setUp(self):
        _, self.out = build_in_mode(fresh=True, seeded=False)
        self.described = [row[0] for row in scaffold.fixtures_for("fresh")]

    def test_no_mid_only_fixture_is_described(self):
        for path in self.MID_ONLY:
            with self.subTest(path=path):
                self.assertNotIn(path, self.described)

    def test_no_docker_containers_line(self):
        """INV-101's warn-and-continue path needs a progress file that names a container."""
        self.assertNotIn("  └ docker_containers", self.described)
        self.assertNotIn("INV-101", self.out)

    def test_the_preferences_line_is_not_inverted(self):
        """The inversion was the worst of it: empty described as carrying saved values."""
        prefs = [
            row for row in scaffold.fixtures_for("fresh")
            if row[1] == "config/bootcamp_preferences.yaml"
        ]
        self.assertEqual(1, len(prefs), "exactly one preferences row must apply to fresh")
        why = prefs[0][3]
        self.assertIn("EMPTY", why)
        self.assertIn("INERT", why)
        self.assertNotIn("saved verbosity", why)

    def test_the_absent_fixtures_are_named_as_absent(self):
        """Stating the limit is the banner's whole job for a dry-run report."""
        self.assertIn("NOT in this mode", self.out)
        for path in self.MID_ONLY:
            with self.subTest(path=path):
                self.assertIn(path, self.out)


class SeededDescribesItsOwnCoverage(unittest.TestCase):
    def setUp(self):
        _, self.out = build_in_mode(fresh=False, seeded=True)
        self.rows = scaffold.fixtures_for("seeded")

    def test_the_preferences_line_is_the_seeded_one(self):
        prefs = [r for r in self.rows if r[1] == "config/bootcamp_preferences.yaml"]
        self.assertEqual(1, len(prefs))
        self.assertIn("honor-don't-ask (INV-133)", prefs[0][3])

    def test_the_four_mid_only_fixtures_are_omitted(self):
        described = {r[1] for r in self.rows}
        for path in FreshNoLongerOverClaims.MID_ONLY:
            with self.subTest(path=path):
                self.assertNotIn(path, described)


class MidBootcampOutputIsUnchanged(unittest.TestCase):
    """Criterion 4: the mode the original banner already described correctly."""

    def test_all_nine_original_rows_still_apply(self):
        described = [row[0] for row in scaffold.fixtures_for("mid")]
        for display in (
            "config/bootcamp_progress.json",
            "  └ docker_containers",
            "config/bootcamp_preferences.yaml",
            "docs/bootcamp_recap.md",
            "docs/progress/recap_checkpoint.md",
            "docs/feedback/...FEEDBACK.md",
            "docs/loading_strategy.md",
            "src/system_verification/records.jsonl",
            "config/engine_config.json",
        ):
            with self.subTest(display=display):
                self.assertIn(display, described)

    def test_mid_omits_nothing(self):
        """Nothing is absent in mid, so the limits block must not appear."""
        _, out = build_in_mode(fresh=False, seeded=False)
        self.assertNotIn("NOT in this mode", out)


class ExplainNamesItsMode(unittest.TestCase):
    """Criterion 6: --explain writes nothing, so it must say what it is describing."""

    def test_explain_defaults_to_mid_and_says_so(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scaffold.explain(scaffold.mode_name(False, False))
        self.assertIn("mid", buf.getvalue())

    def test_explain_follows_the_mode_flags(self):
        for mode, fresh, seeded in INVOCATIONS:
            with self.subTest(mode=mode):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    scaffold.explain(scaffold.mode_name(fresh, seeded))
                self.assertIn(mode, buf.getvalue())

    def test_mode_name_resolves_seeded_before_fresh(self):
        """build() treats --seeded as winning; the banner must agree or it mislabels."""
        self.assertEqual("seeded", scaffold.mode_name(True, True))
        self.assertEqual("fresh", scaffold.mode_name(True, False))
        self.assertEqual("mid", scaffold.mode_name(False, False))


class TheScaffoldStaysStdlibOnly(unittest.TestCase):
    """INV-108: the suite and this tooling import nothing from plugins/."""

    def test_no_plugin_import(self):
        source = SCAFFOLD.read_text(encoding="utf-8")
        self.assertNotIn("from plugins", source)
        self.assertNotIn("import plugins", source)

    def test_paths_stay_pathlib_based(self):
        """Cross-platform: no os.path string joining crept in with this change."""
        source = SCAFFOLD.read_text(encoding="utf-8")
        self.assertNotIn("os.path.join", source)


if __name__ == "__main__":
    unittest.main()
