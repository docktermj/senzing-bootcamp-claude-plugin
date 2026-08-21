"""`conformance.py all` runs every view that needs no argument, and `since` can compute its ref.

`per-rule` and `since` were added on 2026-08-21 because the section-scoped `rules` count cannot
see a hard rule that lands beside an unrelated citation. Three places then told a run to use them
— and **neither was reachable from the path that prescribes the generators**: `all` ran `rules`,
`enumerations`, `size` and `duplication`, while the audit's Step 1.3 called `all` *"every lead
generator"*. A run following Step 1 literally got only the view documented, in the same file, as
unable to see the class.

⚠️ **That is the fixed defect one layer out.** The finding it came from was a run watching a count
that could not answer the question it was used for; the remedy added views that answer it and left
the prescribed command pointing at the old one. The tests written for the new views could not
notice, because they invoke the views directly with explicit arguments — the right way to test a
view's behavior and the wrong way to see that nothing else invokes it.

⛔ **The subcommand set is DERIVED from the script's own parser, never listed here.** A listed test
certifies the views someone remembered and is blind to the next one added — which is the exact
shape of the defect it guards (INV-246). `since` is excluded because it takes a required range;
excluding it is asserted too, so the exclusion stays deliberate rather than accidental.

Run:  python3 -m unittest discover -s tests
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude/skills/production-readiness-audit/conformance.py"

# Views that legitimately need an argument, and why. Anything else must be in `all`.
NEEDS_AN_ARGUMENT = {
    "since": "takes a range; guessing one would report the wrong answer silently",
    "all": "is the aggregate itself",
}


def run(*argv):
    return subprocess.run([sys.executable, str(CONFORMANCE)] + list(argv),
                          capture_output=True, text=True, cwd=str(REPO_ROOT))


def declared_subcommands():
    """Every subcommand the script's parser declares, from `--help`."""
    out = run("--help").stdout
    m = re.search(r"\{([a-z,\-]+)\}", out)
    if m:
        return [c for c in m.group(1).split(",") if c]
    return []


def section_headers(text):
    return [l.strip() for l in text.splitlines() if l.startswith("== ")]


class AllRunsEveryArgumentFreeView(unittest.TestCase):
    def test_the_parser_declares_the_views_this_test_reasons_about(self):
        cmds = declared_subcommands()
        self.assertTrue(cmds, "could not parse the subcommand list from --help; the test is "
                              "vacuous and would pass no matter what `all` runs")
        for expected in ("rules", "per-rule", "since", "all"):
            self.assertIn(expected, cmds, "the parser no longer declares %r" % expected)

    def test_every_argument_free_view_appears_in_all(self):
        cmds = [c for c in declared_subcommands() if c not in NEEDS_AN_ARGUMENT]
        self.assertTrue(cmds, "no argument-free subcommands found")
        all_out = run("all")
        self.assertEqual(0, all_out.returncode, all_out.stderr)
        all_sections = section_headers(all_out.stdout)
        for cmd in cmds:
            with self.subTest(view=cmd):
                own = run(cmd)
                self.assertEqual(0, own.returncode, "%s failed on its own: %s" % (cmd, own.stderr))
                own_sections = section_headers(own.stdout)
                self.assertTrue(own_sections, "%s printed no `== ` section header" % cmd)
                self.assertIn(
                    own_sections[0], all_sections,
                    "`all` does not run %r. Step 1.3 calls `all` \"every lead generator\", so a "
                    "view missing here is a view no run reaches.\n`all` printed: %s"
                    % (cmd, all_sections))

    def test_all_says_what_it_did_not_run(self):
        out = run("all").stdout
        self.assertIn("not run by `all`: since", out,
                      "`all` silently omits `since`. An aggregate that quietly covers some views "
                      "is the same shape as a count that quietly covered one population of two.")
        self.assertIn("--since-last-audit", out,
                      "`all` should name how to run the view it skipped")


class SinceCanComputeItsOwnRef(unittest.TestCase):
    """Both call sites used to pass a placeholder no run could resolve."""

    def test_since_last_audit_resolves_from_the_ledger(self):
        out = run("since", "--since-last-audit")
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertIn("resolved from the newest audit entry", out.stdout,
                      "the flag did not report where it got the ref:\n%s" % out.stdout)
        m = re.search(r"added to shipped markdown since ([0-9a-f]{7,40})", out.stdout)
        self.assertIsNotNone(m, "the resolved ref is not reported:\n%s" % out.stdout)
        # The ref must be a real commit, not a plausible-looking string.
        rev = subprocess.run(["git", "rev-parse", "--verify", "%s^{commit}" % m.group(1)],
                             cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(0, rev.returncode,
                         "the resolved ref %r is not a commit in this repo" % m.group(1))

    def test_a_bare_since_with_no_range_refuses(self):
        out = run("since")
        self.assertEqual(2, out.returncode,
                         "`since` with no range must refuse: an empty result and an unspecified "
                         "range are indistinguishable (INV-110/INV-115)")
        self.assertIn("--since-last-audit", out.stderr,
                      "the refusal should name the flag that works")

    def test_the_call_sites_pass_the_flag_not_a_placeholder(self):
        for rel in (".claude/skills/production-readiness-audit/SKILL.md",
                    ".claude/skills/implement-spec/SKILL.md"):
            with self.subTest(file=rel):
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                if "conformance.py since" not in text:
                    continue
                for m in re.finditer(r"conformance\.py since ([^\n`]*)", text):
                    arg = m.group(1).strip()
                    self.assertNotRegex(
                        arg, r"--ref\s*<",
                        "%s passes a placeholder ref (%r). A run cannot compute it, so the "
                        "instruction gets skipped or guessed; use --since-last-audit." % (rel, arg))


if __name__ == "__main__":
    unittest.main()
