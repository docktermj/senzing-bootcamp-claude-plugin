"""The /auto-test harness must work, and must keep working offline.

Two jobs, and the second is the interesting one.

**Job 1 — the harness is negative-controlled.** `transcript_lint.py` ships a
selftest that asserts every rule fires on input built to break it and stays silent
on input built to pass. A guard whose docstring claims more than its assertion
checks is worse than no guard, so the suite runs that selftest rather than trusting
it exists.

**Job 2 — the plugin conforms to the last observed MCP contract, offline.**
`.claude/skills/auto-test/baseline/mcp-snapshot.json` is a committed record of what
the live server accepted, including the value sets discovered by sending deliberate
bad values. Checking the plugin against that file needs no network, so it belongs in
this suite (INV-108: stdlib only, offline, fast) while `/auto-test` refreshes the
file online.

That split is what keeps `tests/test_mcp_call_contracts.py` honest. That test pins
the contract as prose constants a human transcribed on a date; this one checks
against a machine-captured snapshot with a diffable provenance. When the two
disagree, `mcp_probe.py`'s `audit_static_contract` says so.

Run:  python3 -m unittest discover -s tests
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS = REPO_ROOT / ".claude" / "skills" / "auto-test"
BASELINE = HARNESS / "baseline" / "mcp-snapshot.json"

sys.path.insert(0, str(HARNESS))


def _load_baseline():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


class TestHarnessIsPresent(unittest.TestCase):
    """The skill is a maintainer tool; it must not leak into the shipped plugin."""

    def test_every_component_exists(self):
        for name in ("SKILL.md", "mcp_probe.py", "transcript_lint.py", "walk.py",
                     "autotest.py"):
            self.assertTrue((HARNESS / name).is_file(), f"missing {name}")

    def test_baseline_is_committed(self):
        self.assertTrue(BASELINE.is_file(),
                        "the MCP baseline must be committed; without it the offline "
                        "conformance check below silently covers nothing")

    def test_harness_is_not_shipped_to_bootcampers(self):
        """propagate.sh mirrors plugins/, .claude-plugin/, docs/ and README.md."""
        self.assertNotIn("plugins", HARNESS.relative_to(REPO_ROOT).parts,
                         "the harness must live under .claude/, which is not "
                         "propagated to the public repo")


class TestTranscriptLinterIsNegativeControlled(unittest.TestCase):
    def test_selftest_passes(self):
        result = subprocess.run(
            [sys.executable, str(HARNESS / "transcript_lint.py"), "--selftest"],
            capture_output=True, text=True)
        self.assertEqual(
            0, result.returncode,
            f"transcript_lint selftest failed:\n{result.stdout}\n{result.stderr}")

    def test_a_clean_transcript_is_clean(self):
        import transcript_lint as lint
        good = ["Nice — a claims database is exactly the case this is built for.\n\n"
                "\U0001f449 **Which source would you like to start with?**\n\n"
                "1. Claims\n2. Policies\n\n(respond with a number)"]
        self.assertEqual([], lint.lint(good))


class TestPluginConformsToTheCapturedContract(unittest.TestCase):
    """The offline half of the MCP check, against the committed snapshot."""

    def setUp(self):
        import mcp_probe
        self.probe = mcp_probe
        self.live = _load_baseline()

    def test_no_breaking_conformance_findings(self):
        # url=None keeps this offline: a suspicion that would need a live call to
        # settle is skipped rather than guessed at.
        findings = self.probe.conformance(self.live, url=None)
        breaking = [f for f in findings if f["severity"] == self.probe.BREAKING]
        self.assertEqual(
            [], breaking,
            "the plugin calls the MCP server in a way the captured contract "
            "rejects:\n  " + "\n  ".join(f["message"] for f in breaking))

    def test_every_probed_parameter_still_has_a_value_set(self):
        """A baseline whose probes all came back empty would pass everything."""
        enumerated = [
            (tool, param)
            for tool, meta in self.live["tools"].items()
            for param, info in (meta.get("probed_values") or {}).items()
            if info.get("mode") == self.probe.ENUMERATED and info.get("values")
        ]
        self.assertGreaterEqual(
            len(enumerated), 8,
            "fewer enumerated parameters than expected — the conformance check "
            f"only covers {len(enumerated)}; re-run `mcp_probe.py update`")

    def test_the_workflow_actions_match_the_other_test(self):
        """Cross-check against test_mcp_call_contracts.py's hand-written constant."""
        import re
        contract = (REPO_ROOT / "tests" / "test_mcp_call_contracts.py").read_text()
        match = re.search(r"VALID_WORKFLOW_ACTIONS\s*=\s*\{([^}]*)\}", contract)
        self.assertIsNotNone(match, "VALID_WORKFLOW_ACTIONS not found")
        pinned = set(re.findall(r'"([a-z_]+)"', match.group(1)))
        captured = set(
            self.live["tools"]["mapping_workflow"]["probed_values"]["action"]["values"])
        self.assertEqual(
            pinned, captured,
            "the hand-written contract and the captured snapshot disagree about "
            "mapping_workflow's actions; one of them is wrong")


class TestTheHarnessRefusesDangerousCalls(unittest.TestCase):
    """Enforced by flag, not by instruction — an unattended run forgets rules."""

    def test_probe_never_calls_the_forbidden_tools(self):
        import mcp_probe
        self.assertEqual({"submit_feedback", "download_resource"},
                         set(mcp_probe.NEVER_CALL))
        for tool, _param, _base in mcp_probe.PROBE_MATRIX:
            self.assertNotIn(tool, mcp_probe.NEVER_CALL,
                             f"{tool} is in PROBE_MATRIX but must never be called")
        for tool, _args in mcp_probe.CONTENT_PROBES:
            self.assertNotIn(tool, mcp_probe.NEVER_CALL)

    def test_the_walk_disallows_them_by_flag(self):
        import walk
        self.assertEqual(
            ("mcp__senzing__submit_feedback", "mcp__senzing__download_resource"),
            walk.FORBIDDEN_TOOLS)


class TestSandboxLocation(unittest.TestCase):
    """write-gate.py blocks system temp, so a sandbox there tests the gate."""

    def test_sandbox_root_is_under_home(self):
        import autotest
        root = str(autotest.SANDBOX_ROOT)
        for bad in ("/tmp/", "/var/tmp/", "/private/tmp/"):
            self.assertFalse(root.startswith(bad),
                             f"sandbox root {root} is inside a blocked temp location")
        self.assertTrue(root.startswith(str(Path.home())))


if __name__ == "__main__":
    unittest.main()
