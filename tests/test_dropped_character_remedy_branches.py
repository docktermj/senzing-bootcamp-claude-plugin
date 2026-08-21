"""The dropped-character warning offers a remedy for BOTH kinds of non-Latin text.

The warning itself has worked since `generators-warn-on-dropped-unencodable-characters`: content
that cannot be rendered by the Latin-1 core fonts is dropped (INV-143 forbids substituting `?`) and
the loss is reported rather than silent. What was under-specified was the remedy.

It named one case — a non-Latin **entity name**, fixed by using that entity's verified Latin-script
name or alias. On a 2026-08-18 run the dropped text was not a name: the finding was *about* Japanese
text wrongly stored in a `PASSPORT_NUMBER` field, so the CJK string was the **evidence**. There is no
Latin-script alias for an issuance note, and following the advice literally would have **deleted the
finding** — the one outcome the warning exists to prevent.

So the remedy now branches on what the dropped text *was*:

* **(a) it NAMES an entity** -> use the verified Latin-script name or alias; never guess one.
* **(b) it IS the subject** -> keep it verbatim and add an ASCII description alongside, so the page
  still carries the meaning. Explicitly: do not remove it.

⚠️ **The warning must stay pure ASCII** (`test_recap_pdf_font_safety.py` asserts this): a legacy
Windows code page cannot display the very characters that were dropped, so a warning containing them
would corrupt itself and reproduce the defect it reports. These tests therefore check the branch text
without embedding any non-Latin characters in the expectations.

One string serves all three generators: `generate_document_pdf.py` is a thin alias importing
`generate_discoveries_pdf.main`, and `generate_discoveries_pdf.py` imports the folding machinery from
`generate_recap_pdf.py`. Verified 2026-08-21 by rendering a subject-not-label fixture through each of
the three CLIs and confirming the branch text in all three warnings.

Source spec: `specs/the-cjk-drop-remedy-assumes-the-non-latin-text-is-a-label-not-the-finding.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"

#: A field VALUE under discussion, not a label — the case that motivated the branch. Built from
#: code points so this file stays ASCII-only, matching the discipline the warning itself follows.
SUBJECT_NOT_LABEL = (
    "The finding: PASSPORT_NUMBER held "
    + "".join(chr(c) for c in (0xFF08, 0x5E73, 0x6210, 0x5E74, 0x767A, 0x884C, 0xFF09))
    + " instead of a number."
)


def load(name):
    """Load a generator by path.

    It MUST be registered in ``sys.modules`` before ``exec_module``: the generator defines
    dataclasses, and ``dataclasses._is_type`` resolves annotations through
    ``sys.modules[cls.__module__]``, which is ``None`` for an unregistered module — the
    failure surfaces as an unrelated ``AttributeError`` on ``NoneType.__dict__`` in
    unittest's own machinery. Same reason and same fix as
    ``test_recap_pdf_font_safety.load_generator``.
    """
    import sys

    spec = importlib.util.spec_from_file_location("_remedy_" + name, SCRIPTS / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class TheRemedyBranchesOnWhatWasDropped(unittest.TestCase):
    def setUp(self):
        self.gen = load("generate_recap_pdf")
        self.gen.reset_dropped_characters()
        self.gen._safe(SUBJECT_NOT_LABEL)
        self.warning = self.gen.dropped_character_warning()

    def tearDown(self):
        self.gen.reset_dropped_characters()

    def test_a_warning_is_produced_at_all(self):
        self.assertIsNotNone(
            self.warning, "the fixture dropped nothing, so every check below is vacuous")

    def test_the_entity_name_branch_survives(self):
        """The original remedy is still right for the case it was written for."""
        self.assertIn("NAMES an entity", self.warning)
        self.assertIn("verified Latin-script name or alias", self.warning)

    def test_the_subject_branch_exists(self):
        self.assertIn("IS the subject rather than a label", self.warning)
        self.assertIn("keep it verbatim and add an ASCII description", self.warning)

    def test_the_subject_branch_forbids_deletion(self):
        """The failure mode: following the name-branch advice on a subject deletes the finding."""
        self.assertIn(
            "do NOT remove it", self.warning,
            "the subject branch does not say to keep the value, so a reader can still "
            "resolve the warning by deleting the evidence")

    def test_the_guess_caution_is_scoped_to_the_name_branch(self):
        """"Never substitute a guess" must not read as forbidding the ASCII description."""
        name_branch = self.warning.split("IS the subject")[0]
        self.assertIn(
            "never substitute a guess for a name you have not verified", name_branch,
            "the guess caution has drifted out of the entity-name branch, where it belongs; "
            "applied to the subject branch it would forbid the remedy")

    def test_the_warning_is_still_pure_ascii(self):
        """Re-asserted here because this spec ADDED text to the warning."""
        self.assertTrue(
            self.warning.isascii(),
            "the remedy text carries non-ASCII characters, so a legacy Windows code page "
            "corrupts the warning itself: %r" % self.warning)

    def test_no_dropped_character_is_echoed_raw(self):
        for ch in SUBJECT_NOT_LABEL:
            if not ch.isascii():
                with self.subTest(codepoint="U+%04X" % ord(ch)):
                    self.assertNotIn(ch, self.warning)


class AllThreeGeneratorsShareTheOneString(unittest.TestCase):
    """`generate_document_pdf` -> `generate_discoveries_pdf` -> `generate_recap_pdf`.

    Asserted structurally rather than by rendering three PDFs, which the offline suite should
    not depend on; the three-CLI render was performed once at implementation time (2026-08-21)
    and is recorded in the ledger entry.
    """

    def test_document_pdf_delegates_to_discoveries(self):
        text = (SCRIPTS / "generate_document_pdf.py").read_text(encoding="utf-8")
        self.assertIn("from generate_discoveries_pdf import main", text,
                      "generate_document_pdf no longer delegates, so it may carry its own "
                      "copy of the remedy and drift from this one")

    def test_discoveries_pdf_imports_the_recap_machinery(self):
        text = (SCRIPTS / "generate_discoveries_pdf.py").read_text(encoding="utf-8")
        self.assertIn("generate_recap_pdf", text,
                      "generate_discoveries_pdf no longer sources the folding/warning "
                      "machinery from generate_recap_pdf, so the remedy can diverge")

    def test_only_one_generator_defines_the_warning(self):
        definers = [
            p.name for p in sorted(SCRIPTS.glob("generate_*.py"))
            if "def dropped_character_warning" in p.read_text(encoding="utf-8")
        ]
        self.assertEqual(
            ["generate_recap_pdf.py"], definers,
            "the warning is defined in more than one generator, so fixing one leaves the "
            "others stale — which is the defect this spec's own reach depended on not existing")


if __name__ == "__main__":
    unittest.main()
