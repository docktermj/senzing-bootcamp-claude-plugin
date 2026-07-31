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
        self.assertRegex(flat(MODULE_02), r"(?i)verified 2026-07-30 on MCP server 1\.32\.2")

    def test_explain_error_code_is_still_first(self):
        self.assertRegex(flat(MODULE_02), r"explain_error_code\('SENZ2027'\)")

    def test_it_points_at_the_supportpath_check(self):
        self.assertRegex(flat(MODULE_02), r"(?i)`Test-Path` check")

    def test_module_03_routes_senz2027_to_the_supportpath_check(self):
        text = flat(PHASE1)
        self.assertIn("SENZ2027", text)
        self.assertRegex(text, r"(?i)data directory\*\* is not where the configuration points")


class TheRetractedClaimStaysRetracted(unittest.TestCase):
    """SENZ7426 must never be an *unconditioned* SUPPORTPATH symptom.

    History, because it decides what this class may and may not permit. On 2026-07-28 the
    absolute claim "SENZ7426 is the symptom of a wrong SUPPORTPATH" was retracted:
    `explain_error_code('SENZ7426')` returns generic transliteration causes and makes no
    SUPPORTPATH connection — **re-verified 2026-07-31, still true**. A blanket ban on the
    two appearing together was the right guard at the time.

    It is now too broad. `sdk_guide(topic='install', platform='windows')` (server 1.32.2)
    states the **conditioned** form: on Scoop, `%SENZING_DIR%\\data` resolves to a directory
    that does not exist, and then every SzEngine/SzDiagnostic call fails with SENZ7426 while
    SzProduct keeps working. That is not a contradiction of `explain_error_code` — a missing
    data directory means no transliteration modules, so a transliteration failure is exactly
    what you would expect. It is the same INV-169 distinction that forced the original
    retraction, applied the other way: the conditioned claim is supported, the absolute is
    not.

    So the guard now polices the absolute. A SENZ7426/SUPPORTPATH pairing is permitted only
    where the surrounding text carries **both** the platform condition and the tool that
    actually states it.
    """

    def test_senz7426_is_never_tied_to_supportpath_unconditionally(self):
        offenders = []
        for path in sorted(SKILLS.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            if "SENZ7426" not in text:
                continue
            flat_text = re.sub(r"\s+", " ", text)
            for match in re.finditer(r"SENZ7426", flat_text):
                window = flat_text[max(0, match.start() - 400):match.end() + 400]
                if not re.search(r"(?i)SUPPORTPATH", window):
                    continue
                # A mention that *denies* the link is the safety text, not the claim —
                # requiring it to carry the platform condition too would ban the very
                # sentence that stops the retracted absolute being rebuilt.
                denial = re.search(
                    r"(?i)explain_error_code[^.]{0,220}?(?:generic|makes no|no connection)",
                    window,
                )
                if denial:
                    continue
                conditioned = re.search(r"(?i)scoop|windows", window)
                attributed = re.search(r"(?i)sdk_guide", window)
                if not (conditioned and attributed):
                    offenders.append(
                        "%s: %s" % (path.relative_to(REPO_ROOT), window[:170])
                    )
        self.assertEqual(
            [],
            offenders,
            "SENZ7426 tied to SUPPORTPATH without the condition that makes it true. "
            "explain_error_code('SENZ7426') returns only generic transliteration causes "
            "(re-verified 2026-07-31); only sdk_guide(topic='install', platform='windows') "
            "states the Scoop-specific chain. Name the platform AND the tool, or do not "
            "make the link (INV-080/INV-169):\n  " + "\n  ".join(offenders),
        )

    def test_the_supported_form_names_the_tool_that_states_it(self):
        """Attributing it to explain_error_code would be the original error rebuilt."""
        text = re.sub(r"\s+", " ", MODULE_02.read_text(encoding="utf-8"))
        if "SENZ7426" not in text:
            self.skipTest("module 2 no longer mentions SENZ7426")
        self.assertRegex(
            text,
            r"(?i)explain_error_code\('SENZ7426'\)[^.]{0,200}(?:generic|no connection|makes no)",
            "where module 2 makes the SUPPORTPATH link it must also say that "
            "explain_error_code does NOT make it — otherwise the next reader re-derives "
            "the retracted absolute from the wrong tool",
        )

    def test_the_szproduct_masking_claim_carries_its_source(self):
        """The masking claim is no longer unverified — but it still needs attributing.

        This asserted, until 2026-07-31, that the plugin must NOT state the per-class
        masking behaviour, because no MCP source did. One now does:
        `sdk_guide(topic='install', platform='windows')` says a wrong SUPPORTPATH makes
        every SzEngine/SzDiagnostic call fail "while SzProduct keeps working — so the
        install looks healthy". Banning the claim would now suppress a sourced fact, so
        the guard checks provenance instead of forbidding the statement.
        """
        pattern = re.compile(
            r"(?i)SzProduct[^.]{0,90}(?:keep|keeps|still)\s+(?:succeed|work)", re.DOTALL
        )
        for path in sorted(SKILLS.rglob("*.md")):
            flat_text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
            for match in pattern.finditer(flat_text):
                window = flat_text[max(0, match.start() - 400):match.end() + 400]
                with self.subTest(file=path.name):
                    self.assertRegex(
                        window, r"(?i)sdk_guide",
                        "the SzProduct-masking claim appears without naming the tool that "
                        "states it. It was retracted as unverified on 2026-07-28 and is "
                        "supported only by sdk_guide(topic='install', platform='windows') "
                        "— an unattributed version is the retracted claim again (INV-080).",
                    )


class TheSweepIsNotVacuous(unittest.TestCase):
    """Both checks above assert an empty offender list over `SKILLS.rglob("*.md")`.

    If that glob stops matching — a directory rename, a move — they pass forever while
    checking nothing, and an empty result is indistinguishable from a clean one.
    """

    def test_skill_markdown_is_actually_being_scanned(self):
        found = list(SKILLS.rglob("*.md"))
        self.assertGreater(
            len(found), 20,
            "only %d skill .md files found; the glob has drifted and the SENZ7426 / "
            "SzProduct-masking sweeps are now vacuous" % len(found),
        )


if __name__ == "__main__":
    unittest.main()
