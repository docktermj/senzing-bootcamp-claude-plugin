"""`/package-bootcamp` produces an archive that is safe to hand to someone else.

A bootcamper who finished the bootcamp had no way to archive the work or hand it on. Graduation
frames the recap PDF as "a keepsake to revisit and share with their team", and INV-094's revisit
bundle was built for the resume story -- but written **in place**, so it only helped on the machine
that produced it. Nothing gathered the artifacts, nothing said what to open first, and nothing
decided what must **not** travel.

That last one is what these tests are mostly about. An archive is a distribution channel: the
things it must never carry are the point, and every one of them is asserted over a fixture project
tree rather than reasoned about.

⛔ **`.git/` is excluded on purpose** -- the archive is a snapshot, not a clone, and git history can
carry secrets that no longer exist in the tree. `OPEN_ME_FIRST.md` has to say so, or a bootcamper
who wants history silently gets a package that cannot give it.

⚠️ **The `share` profile is the one handed to people who should NOT see the inputs**, so it carries
no database, no `data/raw/`, no credentials, and no `docs/mapping/` (which describes the
bootcamper's own source schema).

Offline; stdlib only; no network and no Senzing engine.

Source spec: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
PACKAGER = SCRIPTS / "package_bootcamp.py"
DATE = "20260826"


def load():
    spec = importlib.util.spec_from_file_location("packager_under_test", PACKAGER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PKG = load()


class Project:
    """A fixture project carrying one of everything, including what must not travel."""

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        for d in ("docs/visualizations", "docs/mapping", "production", "config", "data/raw",
                  "data/temp", "logs", "licenses", "src", "backups/revisit/database",
                  "backups/revisit/state", ".git", "__pycache__", "database", ".venv"):
            (root / d).mkdir(parents=True, exist_ok=True)
        write = lambda rel, text: (root / rel).write_text(text, encoding="utf-8")
        write("docs/bootcamp_recap.pdf", "recap")
        write("docs/business_problem.md",
              "# Business Problem Statement\n\n## Problem Description\nDedupe vendors.\n")
        write("docs/bootcamp_notes.md", "notes")
        write("docs/REVISIT_BOOTCAMP.md", "restore steps")
        write("docs/visualizations/results_visualization-entity-graph.png", "png")
        write("docs/mapping/customers.json", '{"map":1}')
        write("production/README.md", "prod")
        write("config/bootcamp_progress.json",
              '{"modules_completed":["system_verification","query_visualize_discover"]}')
        write("config/engine_config.json", '{"connection":"sqlite3://na:na@/tmp/G2C.db"}')
        write("config/license.json", '{"key":"x"}')
        write(".env", "SECRET=abc")
        write("licenses/g2.lic", "AQAAAD" + "A" * 30)
        write("data/raw/customers.csv", "raw,data")
        write("data/temp/scratch.txt", "tmp")
        write("logs/run.log", "log")
        write("database/G2C.db", "live-db")
        write("backups/revisit/database/G2C.db", "db-backup")
        write("backups/revisit/RESUME_STATE.json", '{"resume":true}')
        write("backups/revisit/state/prefs.yaml", "name: x")
        write(".git/config", "gitobj")
        write("__pycache__/x.pyc", "cache")
        write(".venv/pyvenv.cfg", "venv")
        # A source file that legitimately contains a private key -> excluded and named.
        write("src/loader.py", 'KEY = """-----BEGIN RSA PRIVATE KEY-----\nMIIabc\n"""\n')
        write("src/clean.py", "print('ok')\n")
        # A symlink escaping the project root -> skipped and named.
        try:
            (root / "docs" / "escape.md").symlink_to("/etc/hostname")
            self.symlinks = True
        except OSError:  # pragma: no cover - Windows without privilege
            self.symlinks = False
        self.root = root
        return self

    def dry_run(self, profile):
        result = subprocess.run(
            [sys.executable, str(PACKAGER), "--profile", profile,
             "--project-root", str(self.root), "--date", DATE, "--dry-run"],
            capture_output=True, text=True)
        return result, json.loads(result.stdout)

    def write_archive(self, profile):
        result = subprocess.run(
            [sys.executable, str(PACKAGER), "--profile", profile,
             "--project-root", str(self.root), "--date", DATE],
            capture_output=True, text=True)
        path = (self.root / "backups" / "packages"
                / ("senzing-bootcamp-%s-%s.zip" % (profile, DATE)))
        return result, path

    def __exit__(self, *exc):
        self.tmp.cleanup()


def members(path):
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def manifest_of(path):
    with zipfile.ZipFile(path) as archive:
        root = archive.namelist()[0].split("/")[0]
        return json.loads(archive.read("%s/PACKAGE_MANIFEST.json" % root))


class TheDryRunWritesNothing(unittest.TestCase):
    """The consent question quotes its size, so the measurement must precede any write."""

    def test_it_reports_a_size_and_creates_no_archive(self):
        with Project() as p:
            result, manifest = p.dry_run("share")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("DRY RUN: nothing was written.", result.stderr)
            self.assertIn("size:", result.stderr)
            self.assertGreater(manifest["total_uncompressed_bytes"], 0)
            self.assertFalse((p.root / "backups" / "packages").exists(),
                             "the dry run created the output directory")

    def test_the_two_profiles_report_different_sizes(self):
        """INV-265 anti-vacuity: if they matched, the question's numbers would be meaningless."""
        with Project() as p:
            _, share = p.dry_run("share")
            _, transfer = p.dry_run("transfer")
            self.assertLess(share["total_uncompressed_bytes"],
                            transfer["total_uncompressed_bytes"])


class TheShareProfileCarriesNoInputs(unittest.TestCase):
    """The profile handed to someone who should see results but not the data."""

    def setUp(self):
        self.project = Project().__enter__()
        _, self.path = self.project.write_archive("share")
        self.names = members(self.path)

    def tearDown(self):
        self.project.__exit__()

    def test_the_archive_was_written(self):
        self.assertTrue(self.path.exists())
        self.assertGreater(len(self.names), 3)

    def test_it_carries_no_database_file(self):
        for name in self.names:
            with self.subTest(name=name):
                self.assertFalse(name.endswith((".db", ".sqlite", ".sqlite3")))

    def test_it_carries_none_of_the_forbidden_paths(self):
        forbidden = ("data/raw", "data/temp", ".env", "licenses/", "config/license.json",
                     "logs/", ".git/", "__pycache__", ".venv", "backups/")
        for name in self.names:
            for bad in forbidden:
                with self.subTest(name=name, forbidden=bad):
                    self.assertNotIn(bad, name)

    def test_it_carries_no_mapping_layer(self):
        """Transfer-only: it describes the bootcamper's own source schema."""
        self.assertFalse([n for n in self.names if "docs/mapping" in n])

    def test_it_does_carry_the_results(self):
        """Anti-vacuity: the exclusions above are worthless if nothing is included."""
        joined = "\n".join(self.names)
        for expected in ("docs/bootcamp_recap.pdf", "docs/visualizations/", "production/"):
            with self.subTest(expected=expected):
                self.assertIn(expected, joined)


class TheTransferProfileCanResumeElsewhere(unittest.TestCase):
    def setUp(self):
        self.project = Project().__enter__()
        _, self.path = self.project.write_archive("transfer")
        self.names = members(self.path)

    def tearDown(self):
        self.project.__exit__()

    def test_it_carries_the_revisit_state_snapshot_and_database_backup(self):
        joined = "\n".join(self.names)
        self.assertIn("backups/revisit/RESUME_STATE.json", joined)
        self.assertIn("backups/revisit/state/prefs.yaml", joined)
        self.assertIn("backups/revisit/database/G2C.db", joined,
                      "the transfer profile carries no database backup, so it cannot resume")

    def test_it_carries_config_and_mappings(self):
        joined = "\n".join(self.names)
        self.assertIn("config/bootcamp_progress.json", joined)
        self.assertIn("docs/mapping/customers.json", joined)

    def test_it_still_carries_no_credentials_or_source_data(self):
        for name in self.names:
            for bad in ("data/raw", ".env", "licenses/", "config/license.json", ".git/"):
                with self.subTest(name=name, forbidden=bad):
                    self.assertNotIn(bad, name)

    def test_it_does_not_carry_the_live_database(self):
        """The backup travels; the working repository does not."""
        self.assertFalse([n for n in self.names if n.endswith("database/G2C.db")
                          and "backups" not in n])

    def test_open_me_first_points_at_the_restore_guide(self):
        with zipfile.ZipFile(self.path) as archive:
            root = archive.namelist()[0].split("/")[0]
            text = archive.read("%s/OPEN_ME_FIRST.md" % root).decode("utf-8")
        self.assertIn("docs/REVISIT_BOOTCAMP.md", text)


class SecretsAndSymlinksAreExcludedAndNamed(unittest.TestCase):
    def setUp(self):
        self.project = Project().__enter__()
        _, self.path = self.project.write_archive("transfer")
        self.names = members(self.path)
        self.manifest = manifest_of(self.path)

    def tearDown(self):
        self.project.__exit__()

    def test_a_member_matching_a_secret_pattern_is_excluded(self):
        self.assertFalse([n for n in self.names if n.endswith("src/loader.py")],
                         "a file containing a PEM private key was packaged")

    def test_the_excluded_secret_is_named_in_the_manifest(self):
        """⛔ Excluded is not enough -- a recipient must be able to tell what is missing."""
        reasons = {e["path"]: e["reason"] for e in self.manifest["excluded"]}
        self.assertIn("src/loader.py", reasons)
        self.assertIn("secret pattern", reasons["src/loader.py"])
        self.assertIn("PEM private key", reasons["src/loader.py"])

    def test_the_manifest_does_not_echo_the_secret(self):
        self.assertNotIn("MIIabc", json.dumps(self.manifest))

    def test_a_clean_sibling_is_still_packaged(self):
        """Exclusion is per-file, not per-directory: one bad file must not drop src/."""
        self.assertTrue([n for n in self.names if n.endswith("src/clean.py")])

    def test_a_symlink_resolving_outside_the_project_is_skipped_and_named(self):
        if not self.project.symlinks:
            self.skipTest("symlink creation unavailable on this platform")
        self.assertFalse([n for n in self.names if n.endswith("docs/escape.md")])
        reasons = {e["path"]: e["reason"] for e in self.manifest["excluded"]}
        self.assertIn("docs/escape.md", reasons)
        self.assertIn("outside the project root", reasons["docs/escape.md"])


class TheArchiveIsSelfDescribingAndSelfExcluding(unittest.TestCase):
    def test_it_extracts_into_exactly_one_directory(self):
        with Project() as p:
            _, path = p.write_archive("share")
            tops = {name.split("/")[0] for name in members(path)}
            self.assertEqual({"senzing-bootcamp-share-%s" % DATE}, tops)

    def test_the_root_carries_both_orientation_files(self):
        with Project() as p:
            _, path = p.write_archive("share")
            root = "senzing-bootcamp-share-%s" % DATE
            names = members(path)
            self.assertIn("%s/OPEN_ME_FIRST.md" % root, names)
            self.assertIn("%s/PACKAGE_MANIFEST.json" % root, names)

    def test_the_manifest_records_what_the_spec_requires(self):
        with Project() as p:
            _, path = p.write_archive("share")
            manifest = manifest_of(path)
            self.assertEqual("share", manifest["profile"])
            self.assertTrue(manifest["plugin_version"])
            self.assertIn("query_visualize_discover", manifest["modules_completed"])
            self.assertTrue(manifest["included"])
            for entry in manifest["included"]:
                self.assertEqual(64, len(entry["sha256"]))
                self.assertIn("size_bytes", entry)
            self.assertTrue(manifest["exclusion_rules_applied"]["always"])

    def test_open_me_first_explains_the_git_exclusion(self):
        """A snapshot, not a clone -- said out loud, or the recipient cannot know."""
        with Project() as p:
            _, path = p.write_archive("share")
            root = "senzing-bootcamp-share-%s" % DATE
            with zipfile.ZipFile(path) as archive:
                text = archive.read("%s/OPEN_ME_FIRST.md" % root).decode("utf-8")
            self.assertIn("snapshot, not a clone", text)
            self.assertIn("push the repository", text)

    def test_a_second_archive_does_not_contain_the_first(self):
        """`backups/packages/` is excluded from its own output."""
        with Project() as p:
            _, first = p.write_archive("share")
            self.assertTrue(first.exists())
            result = subprocess.run(
                [sys.executable, str(PACKAGER), "--profile", "share",
                 "--project-root", str(p.root), "--date", "20260827"],
                capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            second = p.root / "backups" / "packages" / "senzing-bootcamp-share-20260827.zip"
            names = members(second)
            self.assertFalse([n for n in names if n.endswith(".zip") or "packages" in n],
                             "the second archive contains the first")


class TheArchiveIsVerifiedBeforeItIsAnnounced(unittest.TestCase):
    """INV-067's discipline: never report an artifact you have not re-opened."""

    def test_it_writes_a_sha256_sidecar_and_reports_the_digest(self):
        with Project() as p:
            result, path = p.write_archive("share")
            sidecar = path.with_suffix(path.suffix + ".sha256")
            self.assertTrue(sidecar.exists(), "no .sha256 sidecar was written")
            digest = sidecar.read_text(encoding="utf-8").split()[0]
            self.assertEqual(64, len(digest))
            self.assertIn(digest, result.stdout,
                          "the digest is not reported, so the bootcamper cannot check it")
            self.assertEqual(digest, PKG.sha256_of(path))

    def test_it_says_it_re_opened_the_archive(self):
        with Project() as p:
            result, _ = p.write_archive("share")
            self.assertIn("verified:", result.stdout)

    def test_it_says_the_plugin_transmits_nothing(self):
        """INV-135 — the flow ends by naming a local path, not by sending anything."""
        with Project() as p:
            result, _ = p.write_archive("share")
            self.assertIn("does not transmit it anywhere", result.stdout)


class ItDegradesHonestlyOnAnEmptyProject(unittest.TestCase):
    def test_a_project_with_no_artifacts_reports_rather_than_writing_an_empty_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(PACKAGER), "--profile", "share",
                 "--project-root", tmp, "--date", DATE],
                capture_output=True, text=True)
            self.assertEqual(1, result.returncode)
            self.assertIn("nothing to package", result.stderr)
            self.assertFalse(list(Path(tmp).glob("backups/packages/*.zip")))


class TheExclusionMatcherMatchesSegmentsNotSubstrings(unittest.TestCase):
    """A directory named `logs` is excluded; a file named `changelogs.md` is not."""

    def test_a_similarly_named_file_is_not_excluded(self):
        self.assertIsNone(PKG.is_excluded("docs/changelogs.md", "share"))
        self.assertIsNone(PKG.is_excluded("docs/target_state.md", "share"))
        self.assertIsNone(PKG.is_excluded("docs/environment.md", "share"))

    def test_the_real_paths_are_excluded(self):
        for rel in ("logs/run.log", ".env", "licenses/g2.lic", "config/license.json",
                    "data/raw/x.csv", ".git/config", "backups/packages/a.zip"):
            with self.subTest(rel=rel):
                self.assertIsNotNone(PKG.is_excluded(rel, "share"))

    def test_share_only_rules_do_not_apply_to_transfer(self):
        self.assertIsNotNone(PKG.is_excluded("backups/revisit/db.db", "share"))
        self.assertIsNone(PKG.is_excluded("backups/revisit/state/x.yaml", "transfer"))


if __name__ == "__main__":
    unittest.main()
