"""The scaffold's engine_config fixture must reach the SDK gate, not the pre-flight gate.

``senzing_viz_server.py`` runs a config-completeness pre-flight -- ``PIPELINE`` must carry
``CONFIGPATH``, ``RESOURCEPATH`` and ``SUPPORTPATH`` -- **before** it touches the SDK. The
scaffold shipped ``{"PIPELINE": {}}`` while its banner said the fixture existed "so scripts
reach their **real failure**, not a missing-file one". It did the opposite: every run stopped at
the pre-flight (exit 2) having never loaded the library.

⛔ **Both gates fail loudly and write no snapshot, which is why this survived.** On a machine
with no ``libSz.so`` the two outcomes are indistinguishable without reading the exit code, so
phase 2's "without libSz.so it must fail loudly and write no snapshot" assertion was satisfied
by the wrong gate. The 2026-09-02 run was the first with a working SDK, and the SDK-missing
branch turned out to have been **unverified by every prior dry run that listed it as checked**.

Verified live on 2026-09-02 (Senzing SDK 4.4.0, build 4.4.0.26242), all three distinguished by
exit code and all three writing no snapshot except the success case:

===========================================  ====  =========================================
fixture / environment                        exit  outcome
===========================================  ====  =========================================
``engine_config_incomplete.json``               2  pre-flight rejects; SDK never touched
``engine_config.json``, no ``libSz.so``         1  ``libSz.so: cannot open shared object file``
``engine_config.json``, SDK + initialized DB    0  snapshot written
===========================================  ====  =========================================

⚠️ The required-key set is **read from the viz server**, never restated here (INV-246). A guard
that hardcodes the three names certifies the list its author had in mind and goes quiet the day
a fourth key is required -- which is the same shape as the defect above, one level up.

Stdlib only; nothing under ``plugins/`` is imported as a package (INV-108).

Run:  python3 -m unittest discover -s tests
"""

import ast
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCAFFOLD = REPO / ".claude" / "skills" / "dry-run" / "scaffold_project.py"
PHASE2 = REPO / ".claude" / "skills" / "dry-run" / "phase2-hooks-and-scripts.md"
VIZ = REPO / "plugins" / "senzing-bootcamp" / "scripts" / "senzing_viz_server.py"


def load_scaffold():
    spec = importlib.util.spec_from_file_location("scaffold_project", SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def required_pipeline_keys():
    """The keys the viz server's pre-flight demands, parsed from its own source.

    Read with ``ast`` rather than a regex so a reformatted tuple still resolves, and so a
    changed *shape* fails loudly here instead of silently matching nothing.
    """
    tree = ast.parse(VIZ.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "REQUIRED_PIPELINE_KEYS":
                    return tuple(ast.literal_eval(node.value))
    raise AssertionError(
        "REQUIRED_PIPELINE_KEYS not found in senzing_viz_server.py. The pre-flight this "
        "fixture exists to get past has moved or been renamed -- find it and re-point this "
        "guard rather than hardcoding the key names it used to have."
    )


class TheDefaultFixtureClearsThePreFlight(unittest.TestCase):
    def setUp(self):
        self.scaffold = load_scaffold()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "proj"
        self.scaffold.build(self.root, fresh=False)

    def tearDown(self):
        self.tmp.cleanup()

    def _load(self, name):
        return json.loads((self.root / "config" / name).read_text(encoding="utf-8"))

    def test_the_default_fixture_carries_every_required_pipeline_key(self):
        """The whole defect: an empty PIPELINE never reaches the SDK."""
        pipeline = self._load("engine_config.json")["PIPELINE"]
        missing = [k for k in required_pipeline_keys() if not pipeline.get(k)]
        self.assertEqual(
            [], missing,
            "The default engine_config fixture is missing %s, so senzing_viz_server.py exits 2 "
            "at the config pre-flight and never loads the SDK. The SDK-missing branch (exit 1) "
            "is then reported as checked by a run that never reached it." % missing,
        )

    def test_the_sql_connection_points_inside_the_scratch_project(self):
        """A fixture pointing at a shared path would have runs clobber each other's datastore."""
        conn = self._load("engine_config.json")["SQL"]["CONNECTION"]
        self.assertIn(
            str(self.root), conn,
            "The datastore must live inside the scratch project. A path outside it survives "
            "`rm -rf` of the project and leaks state between phase-2 runs.",
        )
        # ⚠️ Asserted against the SOURCE, not against `conn`. The first version checked
        # `"/tmp/" not in conn` and failed on a correct fixture, because this test builds into
        # a `tempfile` directory that is itself under /tmp -- so it was reading the test's own
        # scratch location as if it were the fixture's hardcoded value.
        self.assertNotIn(
            "/tmp/sqlite", SCAFFOLD.read_text(encoding="utf-8"),
            "`sdk_guide(topic='install', platform='linux_apt')` returns `db_url` "
            "`sqlite3://na:na@/tmp/sqlite/G2C.db`, and copying it verbatim is the tempting "
            "move — but the maintainer's write-location gate blocks system-temp writes, so the "
            "fixture would fail for a reason unrelated to the gate being tested. The datastore "
            "path must be derived from the project root, which the assertion above pins.",
        )

    def test_the_incomplete_fixture_is_kept_under_its_own_name(self):
        """The pre-flight is good behavior; it keeps a fixture rather than losing coverage."""
        pipeline = self._load("engine_config_incomplete.json")["PIPELINE"]
        self.assertEqual(
            {}, pipeline,
            "engine_config_incomplete.json exists to reach the exit-2 pre-flight gate. If it "
            "gains keys, that gate has no fixture and stops being exercised at all.",
        )

    def test_the_two_fixtures_reach_different_gates(self):
        complete = self._load("engine_config.json")["PIPELINE"]
        incomplete = self._load("engine_config_incomplete.json")["PIPELINE"]
        self.assertNotEqual(
            complete, incomplete,
            "Two fixtures that differ in name only cover one gate twice.",
        )


class TheBannerAndPhase2NameBothGates(unittest.TestCase):
    """A run that cannot tell the gates apart reports the wrong one as verified."""

    def test_the_banner_names_a_gate_for_each_fixture(self):
        rows = {r[1]: r[3] for r in load_scaffold().FIXTURE_MAP if r[1]}
        self.assertIn("config/engine_config.json", rows)
        self.assertIn("config/engine_config_incomplete.json", rows)
        self.assertRegex(
            rows["config/engine_config.json"], r"COMPLETE|exit 1|SDK gate",
            "The banner row must say which gate the complete fixture reaches. Its previous "
            "wording -- 'minimal settings so scripts reach their real failure' -- described an "
            "intent the value did not deliver, which is how this went unnoticed.",
        )
        self.assertRegex(
            rows["config/engine_config_incomplete.json"], r"exit 2|pre-flight",
            "The banner row must say the incomplete fixture stops at the pre-flight.",
        )

    def test_phase2_distinguishes_the_two_exit_codes(self):
        text = PHASE2.read_text(encoding="utf-8")
        start = text.index("senzing_viz_server.py --no-serve")
        section = text[start:start + 2000]
        for token in ("exit 2", "exit 1"):
            with self.subTest(token=token):
                self.assertIn(
                    token, section,
                    "phase2-hooks-and-scripts.md must name both exit codes at the viz-server "
                    "bullet. Without them, 'it failed and wrote nothing' reads as a pass for "
                    "whichever gate the reader had in mind.",
                )
        self.assertRegex(
            section, r"read the exit code",
            "The bullet must tell the reader to read the exit code -- the two gates are "
            "otherwise indistinguishable, which is exactly how the SDK branch went unverified.",
        )


class TheFixturePathsAreMcpSourced(unittest.TestCase):
    """INV-080/INV-149: a Senzing fact in the fixture carries its route, version and date."""

    def test_the_pipeline_defaults_cite_their_route_and_version(self):
        text = SCAFFOLD.read_text(encoding="utf-8")
        block = text[text.index("PIPELINE_DEFAULTS") - 1400:text.index("PIPELINE_DEFAULTS")]
        self.assertRegex(block, r"sdk_guide\(topic='install'")
        self.assertRegex(block, r"default_paths")
        self.assertRegex(
            block, r"1\.36\.0.{0,20}2026-09-02",
            "The paths are a Senzing fact and carry the server version and date they were "
            "read at, like every other such fact in the repo.",
        )

    def test_the_linux_only_scope_is_stated(self):
        text = SCAFFOLD.read_text(encoding="utf-8")
        self.assertRegex(
            text, r"linux_apt\*\* defaults",
            "The literal paths are the linux_apt ones. Saying so is what stops a maintainer "
            "running phase 2 on macOS from reading an exit-1 result as a defect.",
        )


if __name__ == "__main__":
    unittest.main()
