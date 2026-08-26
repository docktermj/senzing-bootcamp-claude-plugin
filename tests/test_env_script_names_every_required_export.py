"""The env-script export guidance cannot present its own list as the complete variable set.

`module-02-sdk-setup`'s Step 3 template carries a comment telling the author which variables
belong in the generated environment script. It has now been wrong at BOTH ends, each time
complete for the failure most recently observed and silent about the other:

  * It once set `PYTHONPATH` and omitted `LD_LIBRARY_PATH`
    (`specs/ld-library-path-relayed-as-conditional-on-a-stock-linux-apt-install.md`). The remedy
    correctly foregrounded `LD_LIBRARY_PATH` --
  * -- and the template it left behind then named `LD_LIBRARY_PATH` and never named `PYTHONPATH`
    (`specs/env-script-template-names-every-export-but-pythonpath.md`). The failure swapped ends
    rather than closing.

⛔ **The remedy is NOT to name the missing variable in the snippet, and that matters.** The
snippet must name no programming language (INV-002): it routes the author to *their* language's
`gotchas[]` entry rather than picking one, and `PYTHONPATH` inside it was tried and rejected once
already (see `test_ld_library_path_is_not_relayed_as_conditional`, whose docstring records it). A
guard that demanded the variable here would re-introduce the violation the other guard exists to
prevent. So this one checks the two properties that survive the next variable being added --
**the list marks itself illustrative** and **`gotchas[]` is named as the authority for the full
set** -- plus the language-agnosticism that forces that form.

⛔ **The two omissions are not equally visible, which is the other half.** A missing
`LD_LIBRARY_PATH` announces itself at the first engine call ("libSz.so: cannot open shared object
file"). A missing `PYTHONPATH` announces nothing: with a PyPI `senzing` distribution present,
`import senzing` resolves to it, nothing raises, and every later module runs against a different
SDK version than the one Module 2 just verified. Reproduced on the development machine
2026-08-26. The snippet must distinguish the two, or an author triages the invisible one as if it
were the loud one.

Because the snippet names no language, the concrete instance is checked separately in the
module's prose, with its server provenance (INV-080) -- otherwise the fix is unfalsifiable: a
correctly agnostic snippet reads the same whether or not anyone established which variable was
being lost.

Per **INV-246** the site set is derived by scanning shipped markdown for the guidance comment,
never by naming the known path.

Stdlib only; reads shipped markdown as text and imports nothing from `plugins/` (INV-108).

Source spec: `specs/env-script-template-names-every-export-but-pythonpath.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"

#: The env-script template's export-guidance comment, located by its opening line rather
#: than by a path so a second template inherits this guard (INV-246).
BLOCK_START = re.compile(r"(?m)^# Platform-specific exports\b")
BLOCK_END = "unset _sz_self"

#: Languages the snippet must not name: it routes to the author's own gotchas[] entry
#: instead of picking one (INV-002). Naming PYTHONPATH here was tried and rejected once
#: already -- see test_ld_library_path_is_not_relayed_as_conditional.
LANGUAGES = ("python", "java", "csharp", "c#", "rust", "typescript", "node")

#: How far past the agnostic block the concrete-case note must appear. Bounded on
#: purpose: an unbounded search is satisfied by any later mention in the module.
NOTE_WINDOW_CHARS = 3000


def shipped_markdown():
    return sorted(SKILLS.glob("**/*.md"))


def flat(text):
    return " ".join(text.split())


def export_guidance_blocks():
    """(path, block) for each env-script export-guidance comment in shipped markdown."""
    out = []
    for path in shipped_markdown():
        text = path.read_text(encoding="utf-8")
        for match in BLOCK_START.finditer(text):
            try:
                end = text.index(BLOCK_END, match.start())
            except ValueError:
                end = match.start() + 3000
            out.append((path, text[match.start():end]))
    return out


def uncommented(block):
    return flat(re.sub(r"(?m)^\s*#\s?", "", block))


class TheScanFindsTheTemplate(unittest.TestCase):
    def test_at_least_one_export_guidance_block_is_found(self):
        found = export_guidance_blocks()
        self.assertTrue(
            found,
            "no env-script export-guidance comment was found in shipped markdown — the scan "
            "pattern has drifted from the template it guards, so every assertion below is "
            "silently vacuous",
        )


class TheEnumerationDoesNotPresentItselfAsComplete(unittest.TestCase):
    """The property that survives the NEXT variable being added, rather than a longer list."""

    def test_it_marks_its_own_list_illustrative(self):
        for path, block in export_guidance_blocks():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertRegex(
                    uncommented(block),
                    r"(?i)ILLUSTRATIVE, NOT A CHECKLIST"
                    r"|illustrative(?:,| and) not (?:a )?(?:complete|exhaustive|checklist)",
                    "the enumeration does not mark itself as illustrative, so it reads as the "
                    "complete set of variables to export — which is how this template lost "
                    "LD_LIBRARY_PATH once and PYTHONPATH once",
                )

    def test_it_names_gotchas_as_the_authority_for_the_full_set(self):
        for path, block in export_guidance_blocks():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn(
                    "gotchas[]", uncommented(block),
                    "the enumeration does not route to gotchas[] as the authority for the full "
                    "variable set, so the next variable it omits is the same defect again",
                )

    def test_it_stays_language_agnostic(self):
        """INV-002 — the snippet routes to the author's language; it must not pick one.

        This is the constraint that makes the illustrative-list form necessary rather than
        merely tidy: the fix for a missing language variable cannot be to name that
        variable here.
        """
        for path, block in export_guidance_blocks():
            lowered = block.lower()
            for language in LANGUAGES:
                with self.subTest(path=path.relative_to(REPO_ROOT), language=language):
                    self.assertNotIn(language, lowered)


class BothFailureModesAreNamedAndDistinguished(unittest.TestCase):
    """An omitted variable fails loudly or silently, and only one is self-announcing."""

    def test_the_loud_failure_is_named(self):
        for path, block in export_guidance_blocks():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn("libSz.so: cannot open shared object file", uncommented(block))

    def test_the_silent_failure_is_named_as_silent(self):
        for path, block in export_guidance_blocks():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                prose = uncommented(block)
                self.assertRegex(
                    prose, r"(?i)\bsilent\b",
                    "the guidance does not name the silent failure mode, so an author "
                    "triages both omissions as loud ones and skips the invisible case",
                )
                self.assertRegex(
                    prose, r"(?i)raises nothing|nothing raises|different SDK version",
                    "the silent mode is labeled but not described, so there is nothing to "
                    "recognize it by",
                )


class TheConcreteCaseSurvivesOutsideTheAgnosticSnippet(unittest.TestCase):
    """The general rule names no language, so the concrete instance must live in the prose.

    Without this the fix is unfalsifiable: a snippet that correctly names no language reads
    identically whether or not anyone ever established which variable was being lost.
    """

    def setUp(self):
        self.texts = {
            path: path.read_text(encoding="utf-8")
            for path, _ in export_guidance_blocks()
        }

    def test_the_module_names_the_language_variable_that_was_lost(self):
        for path, text in self.texts.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn(
                    "PYTHONPATH", text,
                    "the module carrying the env-script template never names PYTHONPATH, so "
                    "the variable this template omitted is recorded nowhere the author reads",
                )

    def test_the_concrete_case_carries_its_server_provenance(self):
        """INV-080 — the Senzing fact is cited, not remembered.

        Anchored to the note that FOLLOWS the agnostic block, not to the first mention of
        the variable anywhere in the file. An earlier version of this assertion read the
        first occurrence and was satisfied by a different step's citation, so stripping the
        provenance from the note this guard exists for went undetected.
        """
        for path, block in export_guidance_blocks():
            text = self.texts[path]
            after = text.index(BLOCK_END, text.index(block[:60]))
            # Bounded, so a note further down the module cannot stand in for the one that
            # belongs beside the template. Without the bound, deleting this note entirely
            # left the assertion satisfied by Step 4's own PYTHONPATH note.
            idx = text.find("PYTHONPATH", after, after + NOTE_WINDOW_CHARS)
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertNotEqual(
                    -1, idx,
                    "no PYTHONPATH note appears within "
                    f"{NOTE_WINDOW_CHARS} characters after the agnostic export block, so the "
                    "variable this template omitted is recorded nowhere near where an author "
                    "writing the script would read it",
                )
                window = flat(text[idx - 800:idx + 1200])
                self.assertRegex(
                    window, r"sdk_guide\(topic='install'",
                    "the PYTHONPATH note after the export block does not name the sdk_guide "
                    "call that establishes it (INV-080)",
                )
                self.assertRegex(
                    window, r"server 1\.\d+\.\d+",
                    "the PYTHONPATH note after the export block carries no server version",
                )


if __name__ == "__main__":
    unittest.main()
