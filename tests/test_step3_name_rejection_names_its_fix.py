"""The step-3 name rejection is documented as a declaration fix, not as a data defect.

`mapping_workflow` step 3 rejects a source that declares both organization and person name
fields, with:

    NAME_ORG cannot co-exist with person name attributes NAME_FIRST, NAME_FULL, NAME_LAST —
    a record is either a person or an organization.

⛔ **The rule is right about records and was applied to field DECLARATIONS.** Two sources
hit it on 2026-08-25 whose fields were verified disjoint — one populated per record, chosen
by `RECORD_TYPE`, zero rows carrying both — and the same rejection was hit independently on
2026-08-27. The fix is to declare the names through `type_discriminator.field_overrides`,
including where the override is identity in both branches.

⚠️ **The authoritative scope is narrower than the message.** The Entity Specification's
`Feature: NAME` section says *"do not mix `NAME_ORG` with parsed person fields **in the same
object**"* (`search_docs(category='data_mapping')`, server 1.33.0, 2026-08-28) — one NAME
feature object. The message asserts a record-level rule; the validator enforces at
declaration level. Three different scopes, and the two that are written down disagree.

⚠️ **The cost is a misdirected first attempt.** "A record is either a person or an
organization" reads as *your data is wrong*, so the natural response is to re-check the data
— which is correct — rather than to change the declaration. Nothing in the message names
`type_discriminator`, so this guard's core assertion is that the plugin's caution does.

⚠️ What this does NOT establish: that the server still rejects. That is runtime behavior of
one workflow step, unreachable offline (INV-108), and it was deliberately **not** re-driven
during triage — reaching step 3 requires completing steps 1-2 against a real multi-source
project. It rests on two field observations on this server version.

Source spec: `specs/mapping-step3-rejects-disjoint-name-declarations.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def mapping_files():
    """Shipped files that drive `mapping_workflow` step 3 — derived, not hardcoded."""
    return sorted(p for p in PLUGIN.rglob("*.md")
                  if "__pycache__" not in p.parts
                  and "schema_mappings" in p.read_text(encoding="utf-8"))


class TheRejectionIsDocumentedAsADeclarationFix(unittest.TestCase):
    def test_a_step3_site_is_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertTrue(
            mapping_files(),
            "no shipped file drives mapping_workflow step 3 any more; the scan broke or the "
            "payload key was renamed. Re-derive it rather than deleting this guard")

    def test_the_rejection_is_named(self):
        hits = [p for p in mapping_files() if "name_org cannot co-exist" in flatten(
            p.read_text(encoding="utf-8"))]
        self.assertTrue(
            hits,
            "no shipped file quotes the step-3 name rejection, so a guide meeting it has "
            "nothing to match against and will read it as a data defect")

    def test_type_discriminator_is_named_as_the_fix(self):
        """⛔ The load-bearing assertion: the message never says this, so the plugin must."""
        for p in mapping_files():
            flat = flatten(p.read_text(encoding="utf-8"))
            if "name_org cannot co-exist" not in flat:
                continue
            i = flat.index("name_org cannot co-exist")
            window = flat[i:i + 1200]
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertIn("type_discriminator.field_overrides", window,
                              "the caution quotes the rejection without naming "
                              "type_discriminator.field_overrides as the fix")
                self.assertIn("identity", window,
                              "the caution does not say the override may be identity in both "
                              "branches, which is the non-obvious half of the workaround")

    def test_the_message_is_not_repeated_as_though_it_were_true_of_the_data(self):
        """It must be framed as a declaration problem, not as 'your data is wrong'."""
        for p in mapping_files():
            flat = flatten(p.read_text(encoding="utf-8"))
            if "name_org cannot co-exist" not in flat:
                continue
            i = flat.index("name_org cannot co-exist")
            window = flat[i:i + 1400]
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertRegex(
                    window, r"declare it differently|about the \*field\s*declarations\*|"
                            r"field\s*\*?\*?declarations",
                    "the caution does not tell the reader the rejection is about the "
                    "declarations rather than the data, which is the whole misdirection")

    def test_the_coverage_consequence_is_referenced_not_restated(self):
        """INV-179 — the field-count note already owns this; point at it."""
        for p in mapping_files():
            flat = flatten(p.read_text(encoding="utf-8"))
            if "name_org cannot co-exist" not in flat:
                continue
            i = flat.index("name_org cannot co-exist")
            window = flat[i:i + 1600]
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertRegex(
                    window, r"field-count warning|counted by nothing",
                    "the caution does not warn that coverage drops after the workaround, so "
                    "a Bootcamper reads the shortfall as unmapped data")

    def test_it_does_not_prescribe_a_blanket_type_discriminator(self):
        """⛔ The fix for a rejection must not become a default for every source."""
        for p in mapping_files():
            flat = flatten(p.read_text(encoding="utf-8"))
            if "name_org cannot co-exist" not in flat:
                continue
            i = flat.index("name_org cannot co-exist")
            window = flat[i:i + 1600]
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertIn("do not pre-emptively emit a `type_discriminator`",
                              window.replace("**", ""),
                              "the caution does not rule out emitting a type_discriminator "
                              "everywhere, which would buy the coverage surprise for nothing")


if __name__ == "__main__":
    unittest.main()
