"""SDK verification must exercise an engine, and SENZ7426 must not be tied to SUPPORTPATH.

Module 2's Step 9 said "engine initializes and connects without errors" but never pinned
which SDK class the check must touch, so a probe that only proves the SDK imports and
reports its version satisfied the wording. That matters because the libraries and their
support data can be present independently — the Senzing FAQ, verified on MCP server
1.32.1 (2026-07-28):

    I get SENZ2027 Plugin initialization error GNR data files failed to load — You are
    missing the senzingsdk-runtime data directory. The libraries are present but the GNR
    data files (in resources/data/) are not deployed.

So a wrong SUPPORTPATH can pass a version query and fail at the first real engine call,
several steps later.

⛔ These tests also pin a RETRACTION. The feedback entry behind this work claimed the
failing code is SENZ7426 rather than the documented SENZ2027, and the first version of
the spec asked for the plugin's symptom code to be broadened accordingly. Re-verified
2026-07-28: explain_error_code('SENZ7426') returns EAS_ERR_XLITERATOR_FAILED
(Transliteration failed) with input-data causes, and nothing in any MCP source connects
it to SUPPORTPATH — while SENZ2027 (EAS_ERR_PLUGIN_INIT) IS the documented
missing-support-data symptom. Implementing the original claim would have written a false
Senzing fact into the plugin (INV-080/INV-169), so `test_senz7426_is_never_tied_to_supportpath`
exists to stop it being reintroduced.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
MODULE_02 = PLUGIN / "skills" / "module-02-sdk-setup" / "SKILL.md"
PHASE1 = PLUGIN / "skills" / "module-03-system-verification" / "phase1-verification.md"
SKILLS = PLUGIN / "skills"


def flat(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class VerificationExercisesAnEngine(unittest.TestCase):
    def test_step_9_requires_an_engine_class_call(self):
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)MUST create and use an `SzEngine` \(or `SzDiagnostic`\) — not only `SzProduct`",
        )

    def test_it_says_why_a_version_query_is_insufficient(self):
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)version query proves the library loaded")
        self.assertRegex(text, r"(?i)present independently")

    def test_both_success_indicators_exclude_a_version_probe(self):
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)a version query alone does not qualify")
        self.assertRegex(
            text, r"(?i)proven by an `SzEngine`/`SzDiagnostic` call rather than a version query"
        )

    def test_the_code_still_comes_from_mcp(self):
        """INV-080: constrain the class touched, not where the code comes from."""
        text = flat(MODULE_02)
        self.assertRegex(text, r"generate_scaffold\(workflow='initialize'\)")
        self.assertRegex(text, r"(?i)[Dd]o not hand-write it")

    def test_module_03_checks_engine_initialization_before_loading(self):
        text = PHASE1.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^### Step 1a: Engine Initialization Check")
        self.assertLess(text.index("Step 1a: Engine Initialization"),
                        text.index("Step 2: Generate Synthetic Verification Records"))

    def test_module_03_stops_rather_than_loading_on_failure(self):
        self.assertRegex(
            flat(PHASE1), r"(?i)stop here rather than proceeding to generation or loading"
        )

    def test_module_03_check_is_not_a_bootcamper_question(self):
        """INV-012: agent-side apparatus, reported only on failure."""
        self.assertRegex(flat(PHASE1), r"(?i)This is a check, not a 👉 question")


class TheSenz2027DiagnosticIsNamed(unittest.TestCase):
    def test_the_data_directory_cause_is_stated(self):
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)missing the senzingsdk-runtime data directory",
        )

    def test_the_quote_carries_its_provenance(self):
        self.assertRegex(flat(MODULE_02), r"(?i)verified 2026-07-28 on MCP server 1\.32\.1")

    def test_explain_error_code_is_still_first(self):
        self.assertRegex(flat(MODULE_02), r"explain_error_code\('SENZ2027'\)")

    def test_it_points_at_the_supportpath_check(self):
        self.assertRegex(flat(MODULE_02), r"(?i)`Test-Path` check")

    def test_module_03_routes_senz2027_to_the_supportpath_check(self):
        text = flat(PHASE1)
        self.assertIn("SENZ2027", text)
        self.assertRegex(text, r"(?i)data directory\*\* is not where the configuration points")


class TheRetractedClaimStaysRetracted(unittest.TestCase):
    """SENZ7426 is a transliteration error; it must never be a SUPPORTPATH symptom."""

    def test_senz7426_is_never_tied_to_supportpath(self):
        offenders = []
        for path in sorted(SKILLS.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            if "SENZ7426" not in text:
                continue
            flat_text = re.sub(r"\s+", " ", text)
            for match in re.finditer(r"SENZ7426", flat_text):
                window = flat_text[max(0, match.start() - 300):match.end() + 300]
                if re.search(r"(?i)SUPPORTPATH", window):
                    offenders.append("%s: %s" % (path.relative_to(REPO_ROOT), window[:160]))
        self.assertEqual(
            [],
            offenders,
            "SENZ7426 is EAS_ERR_XLITERATOR_FAILED (transliteration), not a SUPPORTPATH "
            "symptom — verified on server 1.32.1, 2026-07-28 (INV-080/INV-169):\n  "
            + "\n  ".join(offenders),
        )

    def test_the_plugin_does_not_claim_szproduct_masks_engine_failure(self):
        """No MCP source states the per-class masking behavior; do not assert it."""
        for path in sorted(SKILLS.rglob("*.md")):
            flat_text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
            with self.subTest(file=path.name):
                self.assertNotRegex(
                    flat_text,
                    r"(?i)SzProduct[^.]{0,80}(?:keep|keeps|still) succeed",
                    "the per-class masking claim is unverified; state only that libraries "
                    "and support data can be present independently",
                )


if __name__ == "__main__":
    unittest.main()
