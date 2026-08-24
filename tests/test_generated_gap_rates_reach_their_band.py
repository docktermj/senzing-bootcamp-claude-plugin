"""Any absence rates Module 4 offers as an example must reach the band that example claims.

Module 4 requires the generated data to put at least one source in the **70-79%** band, and
illustrated it with *"a phone absent on roughly a third of its records, an address missing on a
handful"*. Generating to those rates and scoring with Module 5's formula produced **94.9%** --
squarely inside the `>=80` band the requirement exists to avoid. The illustration was off by roughly
a factor of six.

**The defect was arithmetic, not wording.** The illustration and the requirement are separated by a
0.70 completeness weight and a per-record denominator, and nothing in either module did the
multiplication. With clean formatting and distinct keys (which INV-239 requires of the keys) the
composite reduces to `score = 100 - 10m` on seven applicable fields, where `m` is the summed
per-field absence in whole fields. The illustration totals `m ~= 0.35`; the band needs `m` between
2.1 and 3.0.

**Two consequences the prose now states:** no single field can reach the band at any rate (a field
absent from every record moves the score by at most `0.70 x 100/n`, ten points on seven fields,
against a band that starts twenty-one points down); and the requirement is scale-free while the
illustration was not -- what the generator needs is a slot-emptiness fraction, 30-43%.

⚠️ **This guard COMPUTES; it does not pattern-match the prose.** The acceptance criterion was
"verified by computing it, not by reading it", and a test that merely greps for the figures would
pass on a table that had drifted. It parses the shipped worked table and the shipped
`quality_intent` sample and runs both through the formula.

Source spec: `specs/module4-example-gap-rates-cannot-reach-the-band-they-illustrate.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
MODULE4 = SKILLS / "module-04-data-collection" / "SKILL.md"
QUALITY = SKILLS / "module-05-data-quality-mapping" / "phase1-quality-assessment.md"

#: Module 5's composite, which this file must never re-implement from prose.
#: score = 0.70*completeness + 0.25*format_consistency + 0.05*(100 - duplicate_rate)
WEIGHT_COMPLETENESS, WEIGHT_FORMAT, WEIGHT_DUP = 0.70, 0.25, 0.05


def score(completeness, fmt=100.0, dup=0.0):
    return WEIGHT_COMPLETENESS * completeness + WEIGHT_FORMAT * fmt + WEIGHT_DUP * (100.0 - dup)


def flat(path):
    """Collapse spaces only -- LINE STRUCTURE IS LOAD-BEARING for the table regex below."""
    return re.sub(r"[ \t]+", " ", path.read_text(encoding="utf-8"))


def squash(path):
    """Collapse all whitespace, for prose assertions that wrap across lines."""
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class TheFormulaStillLivesInModule5(unittest.TestCase):
    """If Module 5's weights change, this guard's arithmetic is stale and must fail loudly."""

    def test_module5_states_the_weights_this_guard_assumes(self):
        text = flat(QUALITY)
        self.assertIn("0.70", text, "Module 5 no longer states a 0.70 completeness weight")
        self.assertIn("0.25", text, "Module 5 no longer states a 0.25 format weight")
        self.assertIn("0.05", text, "Module 5 no longer states a 0.05 duplicate weight")

    def test_module4_routes_to_it_rather_than_restating_it(self):
        """A formula stated twice drifts in one of them."""
        self.assertRegex(
            squash(MODULE4),
            r"(?i)stated once in `\.\./module-05-data-quality-mapping/phase1-quality-assessment\.md`",
            "Module 4 does not route to Module 5 for the arithmetic")


class TheWorkedTableIsArithmeticallyTrue(unittest.TestCase):
    """Parses the shipped table and recomputes every row."""

    #: `| label | m | completeness | score |` with bold and % tolerated.
    ROW = re.compile(
        r"^[ \t]*\|\s*(?P<label>[^|]+?)\s*\|\s*\*{0,2}(?P<m>[\d.]+(?:\s*[–-]\s*[\d.]+)?)\*{0,2}\s*\|"
        r"\s*\*{0,2}(?P<c>[\d.]+%?(?:\s*[–-]\s*[\d.]+%?)?)\*{0,2}\s*\|"
        r"\s*\*{0,2}(?P<s>[\d.]+(?:\s*[–-]\s*[\d.]+)?)\*{0,2}\s*\|",
        re.M)

    def rows(self):
        out = []
        for m in self.ROW.finditer(MODULE4.read_text(encoding="utf-8")):
            label = m.group("label")
            if label.startswith("-") or "Gapping" in label:
                continue
            out.append(m)
        return out

    @staticmethod
    def _nums(raw):
        return [float(x) for x in re.findall(r"[\d.]+", raw)]

    def test_the_table_is_found(self):
        self.assertGreaterEqual(
            len(self.rows()), 4,
            "the worked gap-rate table was not located, so this guard asserts nothing")

    def test_every_row_recomputes(self):
        n = 7  # the table's stated field count
        for m in self.rows():
            label = m.group("label").strip()
            with self.subTest(row=label[:44]):
                ms, cs, ss = (self._nums(m.group(g)) for g in ("m", "c", "s"))
                for i, mv in enumerate(ms):
                    expected_c = 100.0 * (1.0 - mv / n)
                    expected_s = score(expected_c)
                    self.assertAlmostEqual(
                        expected_c, cs[i], delta=0.1,
                        msg="row %r: m=%.2f implies completeness %.2f%%, table says %.2f%%"
                            % (label, mv, expected_c, cs[i]))
                    self.assertAlmostEqual(
                        expected_s, ss[i], delta=0.1,
                        msg="row %r: m=%.2f implies score %.1f, table says %.1f"
                            % (label, mv, expected_s, ss[i]))

    def test_the_band_row_actually_spans_the_band(self):
        band = [m for m in self.rows() if "70-79" in m.group("label")]
        self.assertEqual(1, len(band), "the 70-79 band row was not found")
        scores = self._nums(band[0].group("s"))
        self.assertEqual({70.0, 79.0}, set(scores),
                         "the band row's score column does not span 70-79: %s" % scores)


class TheQualityIntentSampleReachesItsBand(unittest.TestCase):
    """The criterion the previous sample failed: gaps consistent with target_band."""

    def sample(self):
        text = MODULE4.read_text(encoding="utf-8")
        i = text.index("quality_intent:")
        return text[i:text.index("```", i)]

    def test_the_sample_is_found(self):
        self.assertIn("target_band", self.sample())

    def test_its_gap_rates_land_inside_its_target_band(self):
        block = self.sample()
        band = re.search(r'target_band:\s*"(?P<lo>\d+)-(?P<hi>\d+)"', block)
        self.assertIsNotNone(band, "target_band not parseable")
        lo, hi = float(band.group("lo")), float(band.group("hi"))
        rates = [float(p) / 100.0 for p in re.findall(r"missing ~(\d+)%", block)]
        self.assertGreaterEqual(
            len(rates), 2,
            "fewer than two absence rates in the sample; a single-field gap cannot reach any "
            "low band, which is the wrong intuition the old sample created")
        n = 7
        computed = score(100.0 * (1.0 - sum(rates) / n))
        self.assertTrue(
            lo <= computed <= hi,
            "the sample's gaps sum to %.2f of %d fields -> completeness %.1f%% -> score %.1f, "
            "which is OUTSIDE its own target_band %g-%g. That is the defect this spec fixed: a "
            "recorded intent its own gaps could not have produced makes a generation fault "
            "indistinguishable from a scoring fault."
            % (sum(rates), n, 100.0 * (1.0 - sum(rates) / n), computed, lo, hi))

    def test_the_measured_score_field_agrees(self):
        block = self.sample()
        m = re.search(r"measured_score:\s*([\d.]+)", block)
        self.assertIsNotNone(m, "the sample carries no measured_score for the self-check to write")
        rates = [float(p) / 100.0 for p in re.findall(r"missing ~(\d+)%", block)]
        self.assertAlmostEqual(
            score(100.0 * (1.0 - sum(rates) / 7)), float(m.group(1)), delta=0.5,
            msg="measured_score disagrees with the sample's own gap rates")


class TheSingleFieldCeilingIsStated(unittest.TestCase):
    def test_it_says_no_single_field_reaches_the_band(self):
        self.assertRegex(
            squash(MODULE4), r"(?i)No single field can get you there, at any rate",
            "the specific wrong intuition the old example created is not closed")

    def test_the_ceiling_arithmetic_is_right(self):
        """A field absent from every record costs 0.70 * 100/n."""
        n = 7
        self.assertAlmostEqual(10.0, WEIGHT_COMPLETENESS * 100.0 / n, delta=0.01)
        self.assertIn("10 points on a seven-field", squash(MODULE4))


class TheSelfCheckIsRequired(unittest.TestCase):
    def test_generation_verifies_against_the_recorded_band(self):
        self.assertRegex(
            squash(MODULE4), r"(?i)Verify the generated data against the band before this module closes",
            "nothing requires the generator to check its output against the band it recorded")

    def test_it_widens_the_gaps_rather_than_adjusting_a_score(self):
        self.assertRegex(
            squash(MODULE4), r"(?i)widen the gaps and regenerate\*\* — never adjust a score",
            "the self-check does not forbid adjusting the score, which would falsify a "
            "measurement the Bootcamper is told is real (INV-239)")


if __name__ == "__main__":
    unittest.main()
