"""Graduation's PDF verification must not assume a Unix toolchain, and must
report the checks it could not run.

Step 1b makes rasterizing a page and counting image XObjects "part of verifying the
render" (INV-129) and named `pdftoppm` and `pdfimages` as the tools. Both ship with
poppler, which is standard on Linux and macOS and **absent on Windows by default**. On
one Windows 11 workstation only `pdftotext` resolved, so the two checks that catch what
text extraction cannot — border-clipped glyphs and content outside the page box — did
not run at all, and the image count fell back to the `/Subtype /Image` grep the skill
itself warns overcounts. Nothing said so: the recap was reported verified with its
layout never inspected.

The same session shipped a recap PDF missing all six of the bootcamper's screenshots,
detectable only by counting image objects — the check that had been skipped.

These tests pin the guidance, not an implementation:

* a poppler-free route to the image count exists (the generator's own count, and
  Pillow, which `fpdf2` already pulls in) and the overcounting grep is labeled as such
* Windows is named as the platform where poppler is typically absent
* a skipped check must be reported, and the closing announcement must say what was
  not verified
* no verification step installs a tool to satisfy itself (INV-129)

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GRADUATION_SKILL = PLUGIN / "skills" / "graduation" / "SKILL.md"


def skill_text():
    return GRADUATION_SKILL.read_text(encoding="utf-8")


class PopplerFreeImageCount(unittest.TestCase):
    """The honest image count must be reachable without poppler."""

    def test_names_a_dependency_free_count(self):
        """The generator already reports what it embedded — no tool required."""
        self.assertIn("embedded N of M images", skill_text())

    def test_names_pillow_as_the_no_new_dependency_route(self):
        text = skill_text()
        self.assertRegex(text, r"Pillow")
        # And says why it is free: fpdf2 already pulls it into the venv Step 1b made.
        self.assertRegex(
            text,
            r"Pillow[^\n]*(?:\n[^\n]*){0,6}?(?:already|no new dependency)",
            "Step 1b must say Pillow is already available via fpdf2, not a new install",
        )

    def test_labels_the_subtype_grep_as_overcounting(self):
        text = skill_text()
        self.assertIn("/Subtype /Image", text)
        self.assertRegex(
            text, r"(?i)/Subtype /Image[^\n]*(?:\n[^\n]*){0,4}?overcount"
        )

    def test_pdfimages_is_no_longer_the_only_honest_count(self):
        """It may still be named — it must not be the sole route."""
        text = skill_text()
        self.assertIn("pdfimages -list", text)
        head, _, tail = text.partition("pdfimages -list")
        window = head[-1200:] + tail[:600]
        self.assertRegex(
            window, r"(?i)Pillow|embedded N of M",
            "a poppler-free alternative must sit alongside pdfimages",
        )


class WindowsToolchainIsNamed(unittest.TestCase):
    """The platform where the strongest checks vanish must be called out."""

    def test_windows_poppler_absence_is_stated(self):
        self.assertRegex(
            skill_text(),
            r"(?i)Windows[^\n]*poppler[^\n]*(?:absent|missing|not (?:standard|present))"
            r"|poppler is typically absent",
        )

    def test_pdftotext_only_case_is_described(self):
        self.assertRegex(skill_text(), r"(?i)only\s+`?pdftotext`?\s+(?:resolved|was present)")


class SkippedChecksAreReported(unittest.TestCase):
    """INV-111's fail-loudly discipline, applied to the verification apparatus."""

    def test_a_skipped_check_must_be_recorded_as_skipped(self):
        self.assertRegex(
            skill_text(),
            r"(?i)skipped[^\n]*(?:MUST|must) be (?:recorded|reported)"
            r"|(?:MUST|must) be (?:recorded|reported) as skipped",
        )

    def test_closing_announcement_states_what_was_not_verified(self):
        text = skill_text()
        marker = "Mandatory closing step"
        self.assertIn(marker, text)
        closing = text[text.index(marker):]
        self.assertRegex(
            closing,
            r"(?i)(?:skipped|couldn't check|could not (?:be )?(?:check|verif))",
            "the closing announcement must state which verification steps did not run",
        )

    def test_never_claims_verified_when_a_check_did_not_run(self):
        self.assertRegex(
            skill_text(),
            r"(?i)never (?:describe|claim)[^\n]*verified[^\n]*(?:when|unless)"
            r"|\"?verified\"? (?:that )?silently means",
        )


class NoInstallToSatisfyVerification(unittest.TestCase):
    """INV-129 forbids a verification check installing its own tool."""

    def test_no_install_rule_is_explicit(self):
        self.assertRegex(
            skill_text(), r"(?i)never install (?:one|a tool|anything) to satisfy"
        )

    def test_does_not_instruct_installing_poppler(self):
        """The feedback suggested `scoop install poppler`; INV-129 rules it out."""
        text = skill_text()
        for command in ("scoop install poppler", "brew install poppler", "apt install poppler"):
            occurrences = [
                m.start() for m in re.finditer(re.escape(command), text, re.IGNORECASE)
            ]
            for start in occurrences:
                context = text[max(0, start - 400):start]
                self.assertRegex(
                    context, r"(?i)do not|never|MUST NOT",
                    "%r may appear only as something not to do (INV-129)" % command,
                )


if __name__ == "__main__":
    unittest.main()
