"""A prescribed snake_case filename must not force an un-nameable Java class.

Java couples a **public** top-level class to its filename; Python does not couple anything.
Every `.[ext]` filename in this bootcamp is written in the Python idiom, so on the Java path
`public class MeridianCrmMapper` inside the prescribed `meridian_crm_mapper.java` fails:

    class MeridianCrmMapper is public, should be declared in a file named MeridianCrmMapper.java

Reproduced on javac 21.0.11, 2026-08-14. The reconciliation is to drop `public` from the
top-level class: a package-private top-level class may live in any filename, so the prescribed
path and the idiomatic class name both survive, and `java -cp <dir> <ClassName>` still launches
it. Verified the same day — the package-private form compiles clean under `javac -Xlint:all`
and runs.

Renaming is not available as a fix in either direction. The filenames are read by other
machinery (graduation's artifact mapping, Module 5's source-qualified names, Module 3's build
table, which its own tests pin), and renaming the class to `snake_case` satisfies `javac` while
breaking the same instruction's "idiomatic style for the chosen language".

C# is the quiet version and takes the opposite advice: the file/type correspondence is
conventional, not enforced (`public class MeridianCrmMapper` in `meridian_crm_mapper.cs` builds
with 0 warnings, 0 errors on .NET 8, verified 2026-08-14), so nothing is dropped there.

Enforces **INV-237** — the reconciliation is stated centrally, pointed at from every prescribing
site, and never resolved by renaming the file or the type.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"
VERIFICATION = PLUGIN / "skills" / "module-03-system-verification" / "phase1-verification.md"
MAPPING = PLUGIN / "skills" / "module-05-data-quality-mapping" / "phase2-data-mapping.md"

#: The central statement, identified by the reconciliation it prescribes rather than by a
#: heading, so moving the section does not silently un-cover the sites.
PACKAGE_PRIVATE_RULE = re.compile(
    r"(?i)declare the (?:top-level )?class\s+package-private|Drop `public` from the top-level class"
)
#: A site prescribes a Java filename when it names one, or names the `[ext]`/`<ext>` pattern
#: alongside Java. Both forms appear in the plugin.
PRESCRIBES_JAVA_FILE = re.compile(r"\.java\b|\[ext\]|<ext>")
#: How a site discharges its obligation: point at the central statement.
POINTS_AT_CENTRAL = re.compile(
    r"(?i)ground-rules\.md.{0,60}File placement|INV-237"
)
#: Filenames other machinery reads, which this fix must not change.
PRESCRIBED_NAMES = ("verify_pipeline.java", "transform_[name].[ext]")


def read(path):
    return path.read_text(encoding="utf-8")


def squashed(path):
    return re.sub(r"\s+", " ", read(path))


def java_prescribing_sites():
    """Files that prescribe a Java source filename and so need the pointer.

    Deliberately the two the spec names plus anything that grows the same shape: a file that
    both mentions Java and prescribes a filename pattern. Module 2's `.java` mentions are
    *scaffold* filenames returned by the MCP server, not paths the plugin prescribes, so they
    are excluded by requiring a prescribed-path form.
    """
    return [VERIFICATION, MAPPING]


class TheReconciliationIsStatedCentrally(unittest.TestCase):
    """Criteria 1 and 3 — stated once, with its reason and the C# difference."""

    def test_ground_rules_prescribes_the_package_private_class(self):
        self.assertRegex(squashed(GROUND_RULES), PACKAGE_PRIVATE_RULE)

    def test_it_gives_the_reason(self):
        self.assertRegex(
            squashed(GROUND_RULES),
            r"(?i)only a `public` top-level class is filename-bound",
            "without the reason the rule reads as a superstition and will be 'tidied' away",
        )

    def test_it_says_the_launcher_is_unaffected(self):
        self.assertRegex(squashed(GROUND_RULES), r"java -cp <dir> <ClassName>` still launches it")

    def test_it_quotes_the_compiler_error(self):
        # The error names class visibility while the cause is a filename convention, so the
        # searchable string is what connects the two for a reader who hits it.
        self.assertRegex(
            squashed(GROUND_RULES),
            r"(?i)should be declared in a file named MeridianCrmMapper\.java",
        )

    def test_it_carries_its_verification_provenance(self):
        text = squashed(GROUND_RULES)
        self.assertRegex(text, r"(?i)javac/java 21\.0\.11")
        self.assertRegex(text, r"(?i)-Xlint:all")

    def test_the_csharp_case_distinguishes_conventional_from_enforced(self):
        text = squashed(GROUND_RULES)
        self.assertRegex(text, r"(?i)conventional, not enforced")
        self.assertRegex(text, r"(?i)\.NET 8")
        self.assertRegex(
            text, r"(?i)keep the prescribed filename\s+and name the type idiomatically",
            "C# needs the opposite advice stated, not merely the Java rule scoped away",
        )

    def test_the_unaffected_languages_are_named(self):
        self.assertRegex(
            squashed(GROUND_RULES),
            r"(?i)Python, Rust and TypeScript have no such coupling",
        )


class EveryPrescribingSitePointsAtIt(unittest.TestCase):
    """Criteria 2 and 5 — reachable from the site, and not restated there."""

    def test_each_site_points_at_the_central_statement(self):
        for path in java_prescribing_sites():
            with self.subTest(file=str(path.relative_to(PLUGIN))):
                text = squashed(path)
                self.assertRegex(text, PRESCRIBES_JAVA_FILE)
                self.assertRegex(
                    text, POINTS_AT_CENTRAL,
                    "this file prescribes a Java source filename with no route to the "
                    "reconciliation, so the bootcamper meets it at the compiler instead",
                )

    def test_each_site_names_the_reconciliation_without_restating_it(self):
        """INV-183's shape: named where needed, defined once."""
        for path in java_prescribing_sites():
            with self.subTest(file=str(path.relative_to(PLUGIN))):
                text = squashed(path)
                self.assertRegex(text, r"(?i)package-private")
                # The reason and the C# clause belong to the central statement only.
                self.assertNotRegex(
                    text, r"(?i)conventional, not enforced",
                    "the C# clause is restated here; it has one home (INV-183)",
                )
                self.assertNotRegex(
                    text, r"(?i)do not restate them here.{0,4}$",
                )

    def test_the_central_statement_is_what_makes_them_pass(self):
        """Negative control in assertion form: the pointer must name a real target.

        If the central statement were removed, `test_ground_rules_prescribes_the_package_private
        _class` fails; this asserts the *link target* exists as prose rather than as a path that
        happens to resolve, so a section rename cannot leave two live pointers aimed at nothing.
        """
        self.assertRegex(squashed(GROUND_RULES), r"(?i)## File placement")
        self.assertIn("INV-237", read(GROUND_RULES))


class NoPrescribedFilenameChanged(unittest.TestCase):
    """Criterion 4 — the fix must not ripple into machinery that reads these names."""

    def test_the_verification_build_table_still_names_verify_pipeline_java(self):
        self.assertIn(
            "| Java | `javac src/system_verification/verify_pipeline.java` |",
            read(VERIFICATION),
            "the build table's Java row moved; graduation and this module's own tests read it",
        )

    def test_the_transform_filename_pattern_survives(self):
        self.assertIn("src/transform/transform_[name].[ext]", read(MAPPING))

    def test_no_pascal_case_java_path_was_introduced(self):
        # The tempting fix is renaming to PascalCase.java per language. It ripples further
        # than the defect warrants, so its absence is asserted rather than assumed.
        for path in java_prescribing_sites():
            with self.subTest(file=str(path.relative_to(PLUGIN))):
                self.assertNotRegex(
                    read(path), r"src/\S*/[A-Z][A-Za-z0-9]*\.java",
                    "a PascalCase .java path appeared, changing a prescribed filename",
                )

    def test_the_prescribed_names_are_all_still_present(self):
        joined = read(VERIFICATION) + read(MAPPING)
        for name in PRESCRIBED_NAMES:
            with self.subTest(name=name):
                self.assertIn(name, joined)


class TheOtherLanguagesAreUntouched(unittest.TestCase):
    """Criterion 6 — Python, Rust and TypeScript have no coupling, so no new instruction."""

    def test_the_build_table_rows_are_unchanged(self):
        text = read(VERIFICATION)
        for row in (
            "| Python | `python3 -m py_compile src/system_verification/verify_pipeline.py` |",
            "| C# | `dotnet build src/system_verification/` |",
            "| Rust | `cargo build --manifest-path src/system_verification/Cargo.toml` |",
            "| TypeScript | `tsc src/system_verification/verify_pipeline.ts --noEmit` |",
        ):
            with self.subTest(row=row.split("|")[1].strip()):
                self.assertIn(row, text)

    def test_no_package_private_advice_leaked_onto_a_language_without_the_coupling(self):
        """`package-private` is a Java word; finding it beside Rust or Python is a smell."""
        for path in java_prescribing_sites():
            block = squashed(path)
            for match in re.finditer(r"[^.]*package-private[^.]*\.", block):
                sentence = match.group(0)
                with self.subTest(file=str(path.relative_to(PLUGIN)),
                                  sentence=sentence[:80]):
                    for lang in ("Python", "Rust", "TypeScript"):
                        self.assertNotIn(lang, sentence)


if __name__ == "__main__":
    unittest.main()
