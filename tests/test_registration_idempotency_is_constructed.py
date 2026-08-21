"""Data-source registration is re-runnable by construction, not by catching an error.

Enforces **INV-263** — registration MUST be safe to re-run by construction, never by catching
an error for an already-registered code. Registered 2026-08-21 at the maintainer's sign-off;
it narrows INV-089, which requires idempotency as a property and is silent on the mechanism.
Both bind.

Two Senzing facts the plugin implicitly relied on, neither of which holds. Both re-confirmed on
**server 1.33.0, 2026-08-21** before this guard was written.

**1. `data_sources` selects a snippet and substitutes nothing.** Called with three real codes,
`sdk_guide(topic='configure', language='python', data_sources=[...])` returns a snippet still
hardcoding `("CUSTOMERS", "REFERENCE", "WATCHLIST")`, with `notes` reading *"Replace sample data
source names with your own"*. None of the supplied codes appears anywhere in the response. The
parameter is not inert -- it is the discriminator that makes the registration snippet primary rather
than the seeding one -- so it selects correctly and fills in nothing. Shipping the snippet
unsubstituted registers codes the Bootcamper does not have and leaves the first load failing
SENZ2207 on the codes they do.

**2. No route documents a raised error for re-registering a code, in any binding.**
`get_sdk_reference(topic='parameters', filter='register_data_source', language='python')` returns
`register_data_source(data_source_code: str) -> str` with warnings only about argument types across
bindings. The idempotency the plugin required was coded against an error found via
`search_docs(category='sdk')` -- whose top hit is a **community-maintained Rust wrapper's** trait
doc, not an official SDK's, and the result does not say so. Run twice, nothing was raised and the
`except` branch never executed: the sequence was idempotent by construction, one call later, because
registering an identical configuration returns the existing config ID.

⚠️ **What this guard does NOT assert.** It does not claim `register_data_source` never raises. That
would be an absolute nobody measured, and the community Rust doc describes a real wrapper (INV-169).
What is asserted is narrower and sufficient: **no shipped step may make idempotency depend on an
error being raised**, because no route documents one for the Bootcamper's binding.

⚠️ **The mechanism is only fully confirmable against a live engine.** The criterion is that the
*instruction* no longer depends on an undocumented error -- not that a test observes a second
registration succeeding.

Source spec: `specs/registration-code-rests-on-two-configure-behaviors-the-server-does-not-have.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"

PHASE_A = SKILLS / "module-06-data-processing" / "phaseA-build-loading.md"
VERIFICATION = SKILLS / "module-03-system-verification" / "phase1-verification.md"

#: Both sites that STATE the requirement, plus the three that refer to it by word.
STATEMENT_SITES = (PHASE_A, VERIFICATION)
REFERRING_SITES = (
    SKILLS / "module-03b-truthset-visualization" / "phase1-visualization.md",
    SKILLS / "module-05-data-quality-mapping" / "phase3-test-load.md",
    SKILLS / "module-06-data-processing" / "phaseC-multi-source.md",
)

#: The wording that made an undocumented raised error the mechanism.
ERROR_AS_MECHANISM = re.compile(
    r"(?i)treated as success,?\s*not an error|already registered is treated as success")


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class TheScanIsNotVacuous(unittest.TestCase):
    def test_every_site_exists(self):
        for p in STATEMENT_SITES + REFERRING_SITES:
            with self.subTest(file=p.name):
                self.assertTrue(p.is_file(), "%s moved" % p.name)

    def test_the_referring_sites_still_refer(self):
        """If they stopped requiring it, the statement sites govern nothing."""
        for p in REFERRING_SITES:
            with self.subTest(file=p.name):
                self.assertRegex(
                    flat(p), r"(?i)idempotent",
                    "%s no longer requires idempotent registration, so this guard's "
                    "coverage of it is vacuous" % p.name)


class NoSiteMakesARaisedErrorTheMechanism(unittest.TestCase):
    """Negative-controlled 2026-08-21 by restoring the old phrasing at one site."""

    def test_the_error_as_mechanism_wording_is_gone_everywhere(self):
        offenders = [
            str(p.relative_to(REPO_ROOT))
            for p in sorted((REPO_ROOT / "plugins").rglob("*.md"))
            if ERROR_AS_MECHANISM.search(flat(p))
        ]
        self.assertEqual(
            [], offenders,
            "a shipped step still makes idempotency depend on a code-already-registered error "
            "being treated as success. No route documents that error for any binding, so code "
            "written against it is untested by construction and fails in exactly the case it "
            "exists for: %s" % offenders)

    def test_both_statement_sites_require_re_runnability(self):
        for p in STATEMENT_SITES:
            with self.subTest(file=p.name):
                self.assertRegex(
                    flat(p), r"(?i)safe to re-run|must be\s*safe to re-run|re-runnability",
                    "%s does not require the sequence itself to be re-runnable" % p.name)

    def test_both_statement_sites_permit_a_catch_only_as_a_fallback(self):
        for p in STATEMENT_SITES:
            with self.subTest(file=p.name):
                self.assertRegex(
                    flat(p), r"(?i)fallback, never the\s*mechanism|permitted \*\*fallback\*\*",
                    "%s does not distinguish a permitted fallback catch from the mechanism, so "
                    "a guide can still build idempotency on it" % p.name)

    def test_no_binding_exception_type_is_named_as_a_contract(self):
        """INV-002: the requirement is ownership of re-runnability, not a Python idiom."""
        for p in STATEMENT_SITES:
            with self.subTest(file=p.name):
                self.assertNotRegex(
                    flat(p), r"(?i)catch `?SzBadInput|except SzBadInput|BadInput` for this",
                    "%s names a binding's exception type as the contract" % p.name)


class TheSubstitutionIsStated(unittest.TestCase):
    def test_phase_a_says_the_parameter_substitutes_nothing(self):
        text = flat(PHASE_A)
        self.assertRegex(
            text, r"(?i)SELECTS the snippet and SUBSTITUTES nothing",
            "step 4a does not say that data_sources fills in no values, so a guide can ship "
            "the sample tuple")
        self.assertIn(
            '("CUSTOMERS", "REFERENCE", "WATCHLIST")', text,
            "the sample tuple that gets shipped by mistake is not quoted, so a guide cannot "
            "recognize it in the response")

    def test_it_locates_the_snippet_by_source_path(self):
        self.assertRegex(
            flat(PHASE_A), r"(?i)by its \*\*`source_path`\*\*, not by position",
            "the snippet is located by position among the alternatives, which reorders")

    def test_it_carries_the_route_version_and_date(self):
        text = flat(PHASE_A)
        self.assertIn("sdk_guide(topic='configure', language='python', data_sources=", text)
        self.assertRegex(text, r"\*\*1\.33\.0, 2026-08-21\*\*")

    def test_the_fresh_datastore_precondition_is_stated(self):
        self.assertRegex(
            flat(PHASE_A), r"(?i)WITHOUT `data_sources` first",
            "the registration snippet assumes a default config exists; on a fresh datastore it "
            "raises SENZ7221, and nothing tells the guide to seed one first")


class TheCommunityDocHazardIsStatedOnce(unittest.TestCase):
    def test_phase_a_states_it(self):
        text = flat(PHASE_A)
        self.assertRegex(
            text, r"(?i)community-maintained wrapper docs alongside the\s*official ones",
            "the search_docs(category='sdk') hazard is not stated where the lookup happens")
        self.assertIn("get_capabilities", text,
                      "the community-versus-official distinction is not attributed")

    def test_it_is_not_restated_at_the_other_statement_site(self):
        """INV-179: stated once, referred to from the other site."""
        self.assertRegex(
            flat(VERIFICATION), r"(?i)do not restate it here",
            "the verification site should defer to step 4a rather than fork the reasoning")


if __name__ == "__main__":
    unittest.main()
