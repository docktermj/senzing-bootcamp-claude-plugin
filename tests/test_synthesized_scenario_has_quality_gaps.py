"""Generated data must be able to fail the quality gate it feeds.

Module 4 Step 2's `provenance: synthesized` branch told the guide exactly what complexity to
build in, and every item on that list is about **shape** — names split in one source and joined
in another, addresses as free text, per-campaign duplicates, deliberate cross-source
inconsistency. None is about **quality**. So a faithful generation produces files in which
every field is populated and every value is uniformly formatted.

Module 5 then scores that at 100.0. Observed live 2026-08-14 on a three-source generated
Customer 360 scenario: 100.0 / 100.0 / 100.0, zero empty applicable fields, sanity-checked
against sample values per step 6's own ⛔ — the scores were genuine, not a measurement
artefact. Every source therefore reached the ≥80% branch, and **two of the three gate branches
were unreachable on a first-class path** (the Business Case Offer produces `synthesized` by
design for every customer-facing category). Lost with them: the per-field completeness
breakdown, the format-consistency diagnosis, the `issues` list below 70, and the
per-`RECORD_TYPE` applicability reasoning (INV-174).

This is the generator's defect, not the scorer's. Module 5's scoring is correct, and inventing
gaps at scoring time would falsify a measurement the Bootcamper is told is real.

Enforces **INV-239** — generated data carries the flaws the module it feeds exists to teach,
spans the bands, records its intent, and never puts a gap in a record key.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
COLLECTION = PLUGIN / "skills" / "module-04-data-collection" / "SKILL.md"
DISCOVERY = PLUGIN / "skills" / "module-01-business-problem" / "phase1-discovery.md"
QUALITY = (PLUGIN / "skills" / "module-05-data-quality-mapping"
           / "phase1-quality-assessment.md")


def squash(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def synthesized_branch():
    """Step 2's `provenance: synthesized` bullet, to the next top-level marker.

    Scoped rather than whole-file: the surrounding step also discusses CORD provenance and the
    bring-your-own-data question, and an assertion satisfied by either of those would not be
    about this branch at all.
    """
    body = squash(COLLECTION)
    start = body.index("**`provenance: synthesized`**")
    end = body.index("⚠️ **Both are bootcamp-generated", start)
    return body[start:end]


class TheSynthesizedBranchRequiresQualityGaps(unittest.TestCase):
    """Criterion 1 — both dimensions, and the reason."""

    def test_it_requires_missing_values_in_non_key_fields(self):
        self.assertRegex(
            synthesized_branch(),
            r"(?i)missing values in non-key fields",
            "the branch still asks only for structural complexity, so a faithful "
            "generation scores 100 and the gate is unreachable",
        )

    def test_it_requires_off_pattern_values(self):
        self.assertRegex(synthesized_branch(), r"(?i)off-pattern values in at least one field")

    def test_it_states_the_reason_not_just_the_mechanics(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"(?i)so the quality\s+assessment has something to find")
        self.assertRegex(
            branch, r"(?i)helpfully.{0,30}produces clean data defeats the module",
            "the intent clause is what stops a generator from optimising the gaps away",
        )

    def test_it_says_the_two_kinds_of_complexity_are_additive(self):
        self.assertRegex(
            synthesized_branch(),
            r"(?i)additive, not alternatives",
            "without this a generator may treat quality gaps as a substitute for the "
            "structural complexity the mapping half needs",
        )

    def test_it_names_the_consequence_of_a_clean_generation(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"(?i)scores \*\*100\.0\*\*")
        self.assertRegex(branch, r"(?i)unreachable on\s+this path")


class TheGeneratedSetSpansTheBands(unittest.TestCase):
    """Criterion 2 — a reachable 70-79 source, a ≥80 contrast, and no gaps in keys."""

    def test_it_requires_a_source_in_the_remediation_band(self):
        self.assertRegex(
            synthesized_branch(),
            r"(?i)at least one source in the \*{0,2}70-79%\s*band",
        )

    def test_it_requires_a_contrasting_strong_source(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"(?i)at least one source at ≥80%")
        self.assertRegex(branch, r"(?i)contrast")

    def test_it_forbids_a_gap_in_a_record_key(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"(?i)Never put a gap in a record key")
        self.assertRegex(branch, r"(?i)`DATA_SOURCE` and `RECORD_ID` stay present and unique")

    def test_it_says_why_a_missing_key_is_not_a_quality_gap(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"(?i)load failure")
        self.assertIn("INV-180", branch)

    def test_the_duplicate_pair_still_keeps_distinct_keys(self):
        self.assertRegex(
            synthesized_branch(),
            r"(?i)keeps its \*\*distinct\*\* keys",
            "the existing per-campaign duplicate requirement must not be read as "
            "licence to duplicate a RECORD_ID",
        )


class TheIntentIsRecorded(unittest.TestCase):
    """Criterion 3 — so a later run can tell a generation fault from a scoring fault."""

    def test_it_requires_a_quality_intent_field_in_the_registry(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"quality_intent")
        self.assertRegex(branch, r"config/data_sources\.yaml")

    def test_it_shows_the_shape_to_write(self):
        branch = synthesized_branch()
        self.assertRegex(branch, r"target_band")
        self.assertRegex(branch, r'">=80"')

    def test_it_says_what_the_record_is_for(self):
        self.assertRegex(
            synthesized_branch(),
            r"(?i)tell a \*\*generation\*\* fault from a \*\*scoring\*\* fault",
        )


class ThePromiseAndTheGenerationAgree(unittest.TestCase):
    """The contributing cause: Step 4a promised only mapping complexity."""

    def test_step_4a_now_requires_quality_variation(self):
        self.assertRegex(
            squash(DISCOVERY),
            r"(?i)quality-varied",
            "Module 1 still promises only mapping-complexity-rich data, so the generation "
            "requirement has no authority behind it",
        )

    def test_step_4a_still_requires_mapping_complexity(self):
        self.assertRegex(squash(DISCOVERY), r"(?i)mapping-complexity-rich")

    def test_step_4a_cites_the_invariant(self):
        self.assertIn("INV-239", squash(DISCOVERY))


class ModuleFiveIsUnchanged(unittest.TestCase):
    """Criterion 4 — this changes what data arrives, never how it is measured."""

    def test_the_formula_is_unchanged(self):
        self.assertIn(
            "quality_score = 0.70 × completeness + 0.25 × format_consistency "
            "+ 0.05 × (100 − duplicate_rate)",
            QUALITY.read_text(encoding="utf-8"),
        )

    def test_the_three_bands_are_unchanged(self):
        body = QUALITY.read_text(encoding="utf-8")
        self.assertRegex(body, r"\*\*≥80% quality score\*\* → Proceed to Phase 2")
        self.assertRegex(body, r"\*\*70-79% quality score\*\* → Warn the user")
        self.assertRegex(body, r"\*\*<70% quality score\*\* → Strongly recommend fixing")

    def test_the_presence_test_is_unchanged(self):
        body = squash(QUALITY)
        self.assertRegex(body, r"(?i)Define \"present\" this way — do not re-invent it")
        self.assertRegex(body, r"(?i)`false`, `0` and `0\.0` count as PRESENT")

    def test_the_per_record_type_applicability_rule_is_unchanged(self):
        self.assertRegex(squash(QUALITY), r"(?i)per-`RECORD_TYPE` applicability \(INV-174\)")

    def test_no_illustrative_score_was_added_to_module_five(self):
        """The rejected alternative: Module 5 describing a gappy source it did not measure."""
        body = squash(QUALITY)
        self.assertNotRegex(
            body, r"(?i)here is what a gappy source would look like",
            "Module 5 must present measured numbers, not illustrative ones",
        )


if __name__ == "__main__":
    unittest.main()
