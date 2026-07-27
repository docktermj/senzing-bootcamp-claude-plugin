"""Every surface describing graduation's ending must describe the same ending.

INV-057 is precise about how the bootcamp stops: the terminal "END OF SENZING BOOTCAMP"
banner is presented exactly once, as the **final output**, after the Bootcamper declines
further exploration — and never while exploration continues. `graduation/SKILL.md`
implements that correctly.

`commands/graduate.md` did not. It said graduation should "end with the guaranteed-recap
announcement and the single closing question" — wording that predates INV-057, omits the
banner entirely, and describes the closing question as the last thing that happens. The
slash command is a first-class entry point, so a Bootcamper who typed `/graduate` was
driven from a description of the wrong ending. Nothing caught it because every test looked
at the skill, which was right.

The lesson is the one `test_tab_set_is_singular.py` already learned for tabs: agreement
between files is exactly what cannot be inferred from the file that was edited. Pinned
here for graduation's two ending surfaces, plus the graduation-offer question, which the
plugin itself asks to be kept "identical to module-completion.md" across two files — an
instruction with no enforcement until now.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"

GRADUATION_SKILL = PLUGIN / "skills" / "graduation" / "SKILL.md"
GRADUATE_COMMAND = PLUGIN / "commands" / "graduate.md"
MODULE_COMPLETION = PLUGIN / "skills" / "bootcamp-onboarding" / "module-completion.md"
MODULE_07_PHASE1 = (
    PLUGIN / "skills" / "module-07-query-visualize-discover" / "phase1-query-visualize.md"
)

TERMINAL_BANNER = "END OF SENZING BOOTCAMP"

# Surfaces that tell the reader how graduation finishes.
ENDING_SURFACES = (GRADUATION_SKILL, GRADUATE_COMMAND)

# The graduation offer, which must be worded identically wherever it is presented.
OFFER = re.compile(r"👉 \*\*Would you like to graduate now[^*]*\*\*")

# Ordering language: the banner follows the Bootcamper declining, it is not the reply to
# the closing question itself.
DECLINE_CUES = ("declin", "done", "nothing else", "keep exploring")

# Prose distance, in characters, between the banner's render site and the condition that
# governs it. Generous because graduation/SKILL.md spells the decline branch out at
# length (the stand-down-the-Stop-hook step sits between the two).
CUE_WINDOW = 1600


def read(path):
    return path.read_text(encoding="utf-8")


class TestEndingSurfacesAgree(unittest.TestCase):

    def test_every_ending_surface_names_the_terminal_banner(self):
        missing = [
            str(p.relative_to(REPO_ROOT))
            for p in ENDING_SURFACES
            if TERMINAL_BANNER not in read(p)
        ]
        self.assertEqual(
            [],
            missing,
            f"surface(s) describing graduation's ending without naming the "
            f"'{TERMINAL_BANNER}' banner (INV-057): {missing}",
        )

    def test_every_ending_surface_conditions_the_banner_on_a_decline(self):
        """Naming the banner is not enough; it must not read as unconditional.

        Checks whether *any* mention carries the condition, not the first: both surfaces
        legitimately foreshadow the banner in their opening prose before specifying it.
        """
        offenders = []
        for path in ENDING_SURFACES:
            text = read(path)
            conditioned = False
            for m in re.finditer(re.escape(TERMINAL_BANNER), text):
                window = text[
                    max(0, m.start() - CUE_WINDOW) : m.start() + CUE_WINDOW
                ].lower()
                if any(cue in window for cue in DECLINE_CUES):
                    conditioned = True
                    break
            if not conditioned:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(
            [],
            offenders,
            "surface(s) naming the terminal banner without tying it to the Bootcamper "
            f"declining further exploration (INV-057): {offenders}",
        )

    def test_the_banner_is_described_after_the_closing_question(self):
        """Structural, not prose-matching: order on the page encodes order in the flow.

        Prose matching cannot tell the correct "end the graduation *turn* on the closing
        question" from the defect's "end *with* the closing question" — both contain the
        same words. Position can: whatever a surface says, the banner has to come after
        the question it follows.

        Anchored on the LAST banner mention — its render site. Both surfaces foreshadow
        the banner in their opening prose, so the first mention says nothing about order.
        """
        for path in ENDING_SURFACES:
            with self.subTest(path=path.name):
                text = read(path)
                question = text.find("anything else you would like to explore")
                banner = text.rfind(TERMINAL_BANNER)
                self.assertNotEqual(-1, question, "closing question not found")
                self.assertNotEqual(-1, banner, "terminal banner not found")
                self.assertGreater(
                    banner,
                    question,
                    "the terminal banner is described before the closing question it "
                    "must follow (INV-057)",
                )


class TestGraduationOfferIsWordedOnce(unittest.TestCase):
    """module-completion.md asks Module 7 to keep this wording identical to its own."""

    def test_the_offer_appears_in_both_surfaces(self):
        for path in (MODULE_COMPLETION, MODULE_07_PHASE1):
            with self.subTest(path=path.name):
                self.assertTrue(
                    OFFER.search(read(path)),
                    f"{path.relative_to(REPO_ROOT)} no longer presents the graduation "
                    "offer in the expected pinned form",
                )

    def test_the_offer_is_identical_in_both_surfaces(self):
        found = {p.name: OFFER.findall(read(p)) for p in (MODULE_COMPLETION, MODULE_07_PHASE1)}
        wordings = {w for hits in found.values() for w in hits}
        self.assertEqual(
            1,
            len(wordings),
            "the graduation offer is worded differently across its two surfaces, which "
            f"module-completion.md explicitly forbids: {sorted(wordings)}",
        )


if __name__ == "__main__":
    unittest.main()
