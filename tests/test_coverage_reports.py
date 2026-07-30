"""The maintainer coverage reports run, and report the two gaps they exist for.

`deep-dive-audit-2026-07-29-minor-fixes` item 4 added
`.claude/skills/dry-run/coverage_reports.py` because two blind spots let an invariant stand
unimplemented for weeks while `IMPLEMENTED.md` recorded its spec as done: an invariant no
test cites, and a spec file a ledger entry never records changing.

Neither gap can be a failing test — a hit in either is usually legitimate — so both are
reports. That makes them exactly the kind of apparatus that rots unnoticed: nothing fails
when a report stops reporting. So it is *executed* here rather than asserted present, the
discipline INV-175 settled for shipped snippets.

Three properties, one per way it could rot:

1. **It runs at all**, from a working directory that is not the repo root (the audit
   workflows run from a scratch project — see `dry-run/SKILL.md`), and exits 0 whatever it
   finds, because a report that gates is a report nobody runs.
2. **The invariants report's own property holds** — everything it calls uncited is defined
   in INVARIANTS.md and appears in no `tests/*.py`. Naming specific IDs here cannot work:
   writing an ID into this file makes this file cite it, so the report correctly stops
   listing it and the assertion destroys itself. The first version of this test did
   exactly that with INV-060 and INV-097.
3. **The affected report finds a known gap** and does not crash on the audit entries that
   have no spec file at all.

Run:  python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / ".claude" / "skills" / "dry-run" / "coverage_reports.py"


def run(report, cwd):
    """Run the report from `cwd`, returning (returncode, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), report, "--repo", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestReportsRun(unittest.TestCase):
    def test_the_script_ships(self):
        self.assertTrue(SCRIPT.is_file(), f"missing: {SCRIPT}")

    def test_both_reports_run_from_an_unrelated_directory_and_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            for report in ("invariants", "affected", "both"):
                code, out, err = run(report, tmp)
                self.assertEqual(
                    0, code, f"{report} exited {code}; stderr:\n{err}"
                )
                self.assertTrue(out.strip(), f"{report} produced no output")

    def test_a_missing_repo_is_reported_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "invariants", "--repo", tmp],
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, proc.returncode)
            self.assertIn("no specs/", proc.stderr)


class TestInvariantsReport(unittest.TestCase):
    def test_it_counts_the_invariants_it_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out, _ = run("invariants", tmp)
        m = re.search(r"defined: (\d+)\s+cited by a test: (\d+)\s+uncited: (\d+)", out)
        self.assertIsNotNone(m, f"the summary line is gone:\n{out[:400]}")
        defined, cited, uncited = (int(g) for g in m.groups())
        self.assertGreater(defined, 150, "far fewer invariants parsed than exist")
        self.assertEqual(defined, cited + uncited, "the counts do not add up")

    def test_every_reported_invariant_is_real_and_genuinely_uncited(self):
        """The report's own property, checked independently of it.

        Naming specific IDs here does not work: writing `INV-060` into this file makes
        this file cite it, so the report correctly stops listing it and the assertion
        destroys itself. (That is exactly what the first version of this test did.) So
        assert the property instead — every ID reported is defined in INVARIANTS.md and
        appears in no `tests/*.py` — which stays true however the corpus moves.
        """
        with tempfile.TemporaryDirectory() as tmp:
            _, out, _ = run("invariants", tmp)
        reported = set(re.findall(r"\bINV-(\d{3})\b", out.split("uncited:")[-1]))
        self.assertTrue(reported, "the report listed no uncited invariant at all")

        invariants = (REPO_ROOT / "specs" / "INVARIANTS.md").read_text(encoding="utf-8")
        defined = set(re.findall(r"\*\*INV-(\d{3})\*\*", invariants))
        self.assertEqual(
            set(),
            reported - defined,
            "the report named an invariant that INVARIANTS.md does not define",
        )

        cited_anywhere = set()
        for test_file in (REPO_ROOT / "tests").glob("*.py"):
            cited_anywhere |= set(
                re.findall(r"INV-(\d{3})", test_file.read_text(encoding="utf-8"))
            )
        leaked = sorted(reported & cited_anywhere)
        self.assertEqual(
            [],
            leaked,
            "the report called these uncited while a test file cites them: "
            + ", ".join("INV-" + n for n in leaked),
        )


class TestAffectedReport(unittest.TestCase):
    def test_it_reports_gaps_without_choking_on_specless_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out, _ = run("affected", tmp)
        m = re.search(r"ledgered specs examined: (\d+)\s+with a gap: (\d+)", out)
        self.assertIsNotNone(m, f"the summary line is gone:\n{out[:400]}")
        examined, gaps = (int(g) for g in m.groups())
        self.assertGreater(examined, 150, "far fewer ledger entries parsed than exist")
        self.assertGreater(
            gaps, 0, "no gaps at all — the corpus had 38 when this report was written"
        )
        self.assertLess(gaps, examined, "every entry flagged; the matcher is broken")
