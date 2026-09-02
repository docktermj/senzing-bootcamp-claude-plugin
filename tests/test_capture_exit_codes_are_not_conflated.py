"""A shipped step reading the capture helper's exit status must not gloss non-zero as exit 2.

``capture_screenshots.py`` has three exit codes, made normative by INV-122 on 2026-09-02:

= ======================================================================================
0 captured, possibly with skips
1 **caller error** — an unrecognized tab id, rejected before anything was captured
2 no headless capability, or nothing capturable
= ======================================================================================

``module-completion.md`` handled failure as *"If it exits non-zero (exit 2 = nothing was
captured): skip screenshots … and continue"* and then distinguished **three** reasons — all three
of which are exit-2 reasons. So exit 1 got the exit-2 response.

⛔ **The two need opposite responses.** On exit 2 nothing was capturable, so skipping and keeping
the HTML link is right. On exit 1 **everything** was capturable and the request was wrong: the fix
is to correct the tab list and re-run. Taking the skip path drops every screenshot from the recap
on a run where all of them were available — the loss INV-146 exists to prevent, reached through a
typo instead of a cap.

⚠️ **Reachable from exactly one call site, and the sweep is what establishes that.** Three shipped
files invoke the helper. Module 3b's and Module 7's pass ``--tabs all``, a keyword the helper
resolves itself, so their requests cannot disagree with its vocabulary; both also delegate the
procedure explicitly ("stays stated once in ``module-completion.md``"). Only
``module-completion.md`` names the six tab ids literally, which is why it is both the only
reachable site and the only one that needs the rule — fixing it fixes the class by reference
rather than by repetition (INV-246 satisfied by scanning, not by a path list).

Stdlib only; nothing under ``plugins/`` is imported (INV-108).

Run:  python3 -m unittest discover -s tests
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins")
COMPLETION = os.path.join(
    PLUGIN, "senzing-bootcamp", "skills", "bootcamp-onboarding", "module-completion.md"
)
SCRIPT = os.path.join(PLUGIN, "senzing-bootcamp", "scripts", "capture_screenshots.py")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def shipped_markdown():
    out = []
    for base, _dirs, files in os.walk(PLUGIN):
        if "__pycache__" in base:
            continue
        for name in files:
            if name.endswith(".md"):
                out.append(os.path.join(base, name))
    return sorted(out)


class NonZeroIsNotGlossedAsExitTwo(unittest.TestCase):
    """⚠️ Scanned across shipped markdown, not pinned to the one line that had the defect."""

    #: "non-zero" (or "nonzero") with `exit 2` close behind and no mention of exit 1.
    GLOSS = re.compile(r"non-?zero[^.\n]{0,80}exit\s*2", re.IGNORECASE)

    def test_no_shipped_step_equates_non_zero_with_exit_two(self):
        bad = []
        for path in shipped_markdown():
            text = read(path)
            for m in self.GLOSS.finditer(text):
                window = text[max(0, m.start() - 200):m.end() + 700]
                if re.search(r"exit\s*\*{0,2}1\*{0,2}\b", window):
                    continue          # the two codes are distinguished nearby
                bad.append((os.path.relpath(path, REPO_ROOT),
                            text.count("\n", 0, m.start()) + 1,
                            re.sub(r"\s+", " ", m.group(0))))
        self.assertEqual(
            [], bad,
            "A shipped step equates a non-zero capture exit with exit 2 and never mentions exit "
            "1. Exit 1 is a caller error — an unrecognized tab id, rejected before anything was "
            "captured — and its correct response is to fix the request and re-run, not to skip "
            "screenshots. Skipping drops every screenshot on a run where all were capturable:\n  "
            + "\n  ".join("%s:%d — %r" % b for b in bad),
        )


class ModuleCompletionGivesEachCodeItsOwnResponse(unittest.TestCase):
    def setUp(self):
        self.text = read(COMPLETION)

    def test_exit_one_is_named_as_a_caller_error(self):
        # ⚠️ Matches the CLAIM, not one bolding of it. The first version required the literal
        # `exit **1**` and failed on correct prose that reads `**exit 1 — an unrecognized tab
        # id.**` — the emphasis wraps the whole label rather than the digit. A guard pinned to
        # markup fails on a rewording that says exactly the same thing.
        self.assertRegex(
            self.text,
            r"(?is)exit\s*\*{0,2}1\*{0,2}\s*[—:-].{0,120}unrecognized tab id",
            "exit 1 must be named, and named as what it is: the tab list disagreeing with the "
            "helper's vocabulary, not a missing dependency.",
        )

    def test_exit_one_leads_to_a_rerun_not_a_skip(self):
        self.assertRegex(
            self.text,
            r"(?i)correct the tab list and run it again",
            "the exit-1 branch must send the reader back to the request. Without that it "
            "inherits the skip path, which is the defect.",
        )
        self.assertRegex(
            self.text,
            r"(?s)Do \*\*not\*\* take the skip path.{0,260}INV-146",
            "the cost of taking the skip path on exit 1 — losing every screenshot while all "
            "were available — is what makes this worth a branch rather than a footnote.",
        )

    def test_the_three_exit_two_reasons_survive_verbatim(self):
        """⛔ Hard-won and unrelated to this change: they must not be casualties of it."""
        for needle in (
            "no browser was found",
            "a browser was found but every capture failed",
            "do **not** install a browser or suggest installing",
        ):
            with self.subTest(needle=needle):
                self.assertIn(
                    needle, self.text,
                    "the exit-2 reasons and the do-not-install rule are correct and were kept; "
                    "a Windows machine carrying both Edge and Chrome was once told no "
                    "capability existed, which is why that rule is there.",
                )

    def test_the_split_cites_the_invariant_that_makes_it_normative(self):
        start = self.text.index("Two non-zero exits")
        self.assertIn(
            "INV-122", self.text[max(0, start - 120):start + 60],
            "INV-122 is what makes three distinguishable codes a contract rather than an "
            "implementation detail, so it must be citable at the step that reads them "
            "(INV-183).",
        )


class TheReachabilityClaimMatchesTheOtherCallSites(unittest.TestCase):
    """If another site starts naming tab ids literally, exit 1 becomes reachable there too."""

    def test_only_module_completion_names_tab_ids_literally(self):
        literal = []
        for path in shipped_markdown():
            for m in re.finditer(r"--tabs\s+([A-Za-z0-9_,]+)", read(path)):
                value = m.group(1)
                if value == "all":
                    continue
                literal.append((os.path.relpath(path, REPO_ROOT), value))
        others = sorted({p for p, _v in literal if not p.endswith("module-completion.md")})
        self.assertEqual(
            [], others,
            "another shipped file now passes a literal tab-id list to the capture helper, so "
            "exit 1 is reachable from there too — and the exit-code procedure is stated once, "
            "in module-completion.md. Either pass `--tabs all` there, or state the exit-1 "
            "branch at that site as well: %s" % others,
        )

    def test_the_scan_sees_module_completion_itself(self):
        """A scan that matches no literal list would pass this class vacuously."""
        found = any(
            re.search(r"--tabs\s+graph,", read(p))
            for p in shipped_markdown() if p.endswith("module-completion.md")
        )
        self.assertTrue(
            found,
            "module-completion.md no longer passes a literal tab list. If it moved to "
            "`--tabs all`, exit 1 is no longer reachable from any shipped site and this class "
            "can be retired — but say so deliberately rather than letting it pass empty.",
        )


if __name__ == "__main__":
    unittest.main()
