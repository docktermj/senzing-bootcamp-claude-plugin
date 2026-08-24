"""Graduation's PDF verification must not assume a Unix toolchain, and must
report the checks it could not run.

Step 1b makes rasterizing a page and counting image XObjects "part of verifying the
render" (INV-129) and named `pdftoppm` and `pdfimages` as the tools. Both ship with
poppler, which is standard on Linux and **absent by default on both Windows and macOS**.
On one Windows 11 workstation only `pdftotext` resolved, so the two checks that catch what
text extraction cannot — border-clipped glyphs and content outside the page box — did
not run at all, and the image count fell back to the `/Subtype /Image` grep the skill
itself warns overcounts. Nothing said so: the recap was reported verified with its
layout never inspected.

⚠️ **This docstring said "standard on Linux and macOS" until 2026-07-31, and that was
false.** poppler is a Linux distribution package, not a macOS system component: a macOS
26.5.2 machine with Homebrew in active use had all four binaries absent. The claim came
from `specs/pdf-layout-verification-without-poppler.md` and reached the skill, INV-163 and
this file — and no test could catch it, because no suite can check what is installed on a
platform it is not running on, and this repo's CI runs on Linux, where it happens to hold.
The macOS grouping is now asserted below so the habitual "Linux / macOS" pairing cannot be
reintroduced silently. That assertion is the only defense available; it checks what the
guidance *says*, not what any machine *has*.

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


class MacosIsNotGroupedWithLinux(unittest.TestCase):
    """poppler is a Linux distribution package, not a macOS system component.

    The guidance promised the full check set on macOS while removing the two checks it
    itself calls irreplaceable. Observed 2026-07-31: macOS 26.5.2 (Apple Silicon) with
    Homebrew installed and in active use had all four binaries absent.

    ⚠️ These assertions check what the guidance *says*. Nothing here can verify what a
    macOS machine actually has — this suite runs on Linux, where poppler is present, so
    the absence is not reproducible in CI. That is exactly why the claim survived, and
    why the wording is pinned instead.
    """

    def setUp(self):
        self.text = skill_text()
        # Collapse whitespace AND emphasis markers: these phrases carry bold runs
        # whose placement moves whenever the paragraph is re-wrapped, and a test that
        # fails on re-wrapping teaches the next editor to delete it.
        self.flat = re.sub(r"[*\s]+", " ", self.text)

    def test_macos_is_not_paired_with_linux_for_poppler(self):
        """The habitual Unix pairing is the defect; it must not come back."""
        for pairing in ("Linux / macOS", "Linux and macOS", "macOS / Linux"):
            with self.subTest(pairing=pairing):
                for match in re.finditer(re.escape(pairing), self.text, re.IGNORECASE):
                    window = self.text[match.start(): match.start() + 400]
                    self.assertNotRegex(
                        window,
                        r"(?i)poppler is (usually|typically) present|poppler is standard",
                        "poppler ships on neither macOS nor Windows; grouping macOS with "
                        "Linux promises the full check set on a platform that has none "
                        "of the four binaries",
                    )

    def test_macos_is_stated_to_lack_poppler(self):
        self.assertRegex(
            self.flat,
            r"(?i)macOS[^.]{0,80}poppler is NOT part of the base system"
            r"|macOS ships none of the four binaries",
        )

    def test_macos_and_windows_are_the_same_case(self):
        self.assertRegex(
            self.flat,
            r"(?i)missing-poppler (path|case) is the expected case on both macOS and Windows"
            r"|Treat macOS as the missing-poppler case",
        )

    def test_the_pdftotext_fallback_is_not_offered_unconditionally(self):
        """The Windows advice "keep the positive pdftotext probe" is unactionable on
        macOS, where pdftotext is one of the four missing binaries."""
        self.assertRegex(
            self.flat,
            r"(?i)Do not fall back on `pdftotext` without probing",
        )
        self.assertRegex(self.flat, r"(?i)not actionable there|missing along with the other three")

    def test_the_remaining_route_is_named_and_needs_no_new_dependency(self):
        """A reduced check set must be actionable, not merely reduced (INV-163)."""
        # `Pillow\s*,` because stripping the bold run leaves a space before the comma.
        self.assertRegex(self.flat, r"(?i)Pillow\s*, which `fpdf2` already requires")
        self.assertRegex(self.flat, r"(?i)needs no tool at all")

    def test_it_still_forbids_installing_poppler(self):
        """INV-129 is unaffected: naming macOS must not become a reason to install."""
        self.assertRegex(
            self.flat, r"(?i)never install (?:one|a tool|anything) to satisfy"
        )

    def test_the_page_raster_is_reported_unverified(self):
        self.assertRegex(self.flat, r"(?i)[Rr]eport the page raster as not verified")

    def test_the_invariant_example_was_corrected_too(self):
        """The false claim originated in the spec that established INV-163, so the
        invariant carried it as well. A criterion that names a second file is checked
        against that file."""
        invariants = (REPO_ROOT / "specs" / "INVARIANTS.md").read_text(encoding="utf-8")
        body = re.search(r"\*\*INV-163\*\* — .*", invariants).group(0)
        self.assertRegex(
            body,
            r"(?i)absent by default on \*\*both Windows and macOS\*\*",
            "INV-163's platform example named Windows alone",
        )
        self.assertIn("2026-07-31", body, "the in-place correction must carry its date")
        self.assertRegex(
            body,
            r"(?i)MUST be recorded as skipped",
            "the invariant's MUST must be unchanged by the example fix",
        )

    def test_the_originating_spec_carries_a_dated_correction(self):
        spec = (
            REPO_ROOT / "specs" / "pdf-layout-verification-without-poppler.md"
        ).read_text(encoding="utf-8")
        self.assertRegex(spec, r"(?i)## Correction: the platform claim was wrong for macOS")
        self.assertIn("2026-07-31", spec)
        self.assertRegex(
            spec,
            r"(?i)standard on Linux and macOS",
            "the original wording must be left in place — the record of what was "
            "believed is the point of a correction note",
        )


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
