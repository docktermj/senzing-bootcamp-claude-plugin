"""A sourced env script must locate itself in the shell the bootcamper actually has.

Module 2 mandates a project-local ``src/scripts/senzing-env.sh`` and documents *sourcing*
it into the interactive shell that launches the JVM. The idiom anyone reaches for to make
a script find itself — ``${BASH_SOURCE[0]}`` — is a bash array that expands to **empty**
under zsh, which is macOS's default shell. The script keeps running, resolves the project
root to the wrong directory, exports nothing useful, and the failure surfaces much later.

The reported symptom was ``Unable to get settings``, described in the spec as an SDK error.
Re-verification against MCP server 1.32.1 (2026-07-28) says otherwise: that string carries
no SENZ code because it is not an engine error at all — it is the null-check in Senzing's
own official snippets (``senzing/code-snippets-v4``, e.g.
``java/snippets/information/GetVersion.java`` and the C# equivalents), which print
``Unable to get settings.`` and throw when ``SENZING_ENGINE_CONFIGURATION_JSON`` is unset.
That guard tests for **unset**, not empty, which is why the guidance forbids exporting an
empty value: an empty export sails past the SDK's own check and fails deeper.

So these tests do two different jobs. Most assert the guidance is stated where a reader
meets it. The ones in ``TheDocumentedIdiomActuallyWorks`` **extract the fenced block from
the skill and run it**, because a path-resolution idiom that is merely present but wrong
is exactly the defect being fixed. The zsh half of that is skipped where zsh is not
installed and says so rather than passing quietly.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
MODULE_02 = SKILLS / "module-02-sdk-setup" / "SKILL.md"
PHASE_1 = SKILLS / "module-03-system-verification" / "phase1-verification.md"
GROUND_RULES = SKILLS / "bootcamp-onboarding" / "ground-rules.md"

ANCHOR = '<a id="env-script-path-resolution"></a>'
SETTINGS_VAR = "SENZING_ENGINE_CONFIGURATION_JSON"


def flat(path):
    """Collapse whitespace and strip blockquote markers so prose assertions survive wrapping."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


def documented_idiom():
    """The first ```bash block after the anchor — the snippet a bootcamper would copy."""
    text = MODULE_02.read_text(encoding="utf-8")
    start = text.index(ANCHOR)
    match = re.search(r"```bash\n(.*?)\n```", text[start:], re.S)
    assert match, "no fenced bash block follows the path-resolution anchor"
    return match.group(1)


class ProjectFixture:
    """A throwaway project tree with the documented idiom installed as senzing-env.sh."""

    def __init__(self, settings='{"PIPELINE": {}}'):
        self.dir = Path(tempfile.mkdtemp(prefix="szenv-"))
        # realpath: macOS /var is a symlink to /private/var, and `cd && pwd` resolves it.
        self.root = Path(os.path.realpath(self.dir)) / "proj"
        (self.root / "src" / "scripts").mkdir(parents=True)
        (self.root / "config").mkdir()
        if settings is not None:
            (self.root / "config" / "engine_config.json").write_text(settings, encoding="utf-8")
        self.script = self.root / "src" / "scripts" / "senzing-env.sh"
        self.script.write_text(documented_idiom() + "\n", encoding="utf-8")

    def source(self, shell, cwd=None):
        """Source the script from `shell` and report what it exported."""
        program = (
            '. "$1" || exit $?; '
            'printf "ROOT=%%s\\n" "$SENZING_PROJECT_ROOT"; '
            'printf "SETTINGS=%%s\\n" "$%s"' % SETTINGS_VAR
        )
        return subprocess.run(
            [shell, "-c", program, "probe", str(self.script)],
            capture_output=True,
            text=True,
            cwd=str(cwd or self.dir),
        )

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class TheDocumentedIdiomActuallyWorks(unittest.TestCase):
    """Running the snippet, not just finding it — the defect was a snippet-shaped mistake."""

    def setUp(self):
        self.fx = ProjectFixture()
        self.addCleanup(self.fx.cleanup)

    def test_bash_resolves_the_project_root(self):
        got = self.fx.source("bash")
        self.assertEqual(got.returncode, 0, got.stderr)
        self.assertIn("ROOT=%s" % self.fx.root, got.stdout)

    def test_bash_exports_the_engine_configuration(self):
        got = self.fx.source("bash")
        self.assertIn('SETTINGS={"PIPELINE": {}}', got.stdout)

    def test_the_root_does_not_depend_on_the_working_directory(self):
        """The original bug resolved against the caller's cwd instead of the script."""
        elsewhere = self.fx.root / "config"
        got = self.fx.source("bash", cwd=elsewhere)
        self.assertEqual(got.returncode, 0, got.stderr)
        self.assertIn("ROOT=%s" % self.fx.root, got.stdout)

    def test_zsh_resolves_the_same_root_as_bash(self):
        zsh = shutil.which("zsh")
        if not zsh:
            self.skipTest("zsh is not installed here — the zsh branch is NOT runtime-verified")
        from_bash = self.fx.source("bash")
        from_zsh = self.fx.source(zsh)
        self.assertEqual(from_zsh.returncode, 0, from_zsh.stderr)
        self.assertIn("ROOT=%s" % self.fx.root, from_zsh.stdout)
        self.assertEqual(
            re.search(r"ROOT=(.*)", from_zsh.stdout).group(1),
            re.search(r"ROOT=(.*)", from_bash.stdout).group(1),
        )

    def test_bash_tolerates_the_zsh_only_expansion_in_the_untaken_branch(self):
        """If bash choked parsing ${(%):-%x}, the branch would break the shell it fixes."""
        self.assertIn("${(%):-%x}", documented_idiom())
        got = self.fx.source("bash")
        self.assertNotIn("bad substitution", got.stderr.lower())
        self.assertNotIn("syntax error", got.stderr.lower())


class AMisresolvedRootFailsLoudly(unittest.TestCase):
    """INV-111: name the path you computed rather than exporting a wrong one."""

    def test_a_missing_marker_file_fails_and_prints_the_resolved_root(self):
        fx = ProjectFixture(settings=None)
        self.addCleanup(fx.cleanup)
        got = fx.source("bash")
        self.assertNotEqual(got.returncode, 0, "a wrong root must not succeed silently")
        self.assertIn("resolved root:", got.stderr)
        self.assertIn(str(fx.root), got.stderr, "the message must name the path it computed")

    def test_it_points_at_the_script_not_at_the_senzing_install(self):
        fx = ProjectFixture(settings=None)
        self.addCleanup(fx.cleanup)
        self.assertRegex(
            fx.source("bash").stderr, r"(?i)path-resolution fault, not your Senzing install"
        )

    def test_an_empty_configuration_is_refused_rather_than_exported(self):
        """The SDK snippets' own guard tests for unset, so an empty export defeats it."""
        fx = ProjectFixture(settings="")
        self.addCleanup(fx.cleanup)
        got = fx.source("bash")
        self.assertNotEqual(got.returncode, 0)
        self.assertRegex(got.stderr, r"(?i)refusing to export an empty configuration")
        self.assertNotIn('SETTINGS=""', got.stdout)

    def test_it_returns_instead_of_exiting_so_sourcing_cannot_kill_the_shell(self):
        fx = ProjectFixture(settings=None)
        self.addCleanup(fx.cleanup)
        got = subprocess.run(
            ["bash", "-c", '. "$1" ; printf "SHELL_SURVIVED\\n"', "sh", str(fx.script)],
            capture_output=True,
            text=True,
        )
        self.assertIn("SHELL_SURVIVED", got.stdout, "a sourced script must return, never exit")

    def test_the_guidance_says_return_not_exit(self):
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)`return 1`, never `exit 1`")
        self.assertRegex(text, r"(?i)`set -e` leaks into their session|`set -e` leaks")


class TheRequirementIsStatedWhereTheScriptIsSpecified(unittest.TestCase):
    def test_the_canonical_rule_is_anchored(self):
        self.assertIn(ANCHOR, MODULE_02.read_text(encoding="utf-8"))

    def test_it_declares_itself_canonical(self):
        self.assertRegex(flat(MODULE_02), r"(?i)canonical statement of the rule")

    def test_it_names_the_default_shell_requirement(self):
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)MUST resolve its own path in the platform's \*default\* shell, not only in bash",
        )

    def test_it_names_zsh_as_the_macos_default(self):
        self.assertRegex(flat(MODULE_02), r"(?i)on macOS that is \*\*zsh\*\*")

    def test_bash_source_is_never_recommended_unqualified(self):
        """BASH_SOURCE may appear only where it is being warned about or branched on."""
        text = MODULE_02.read_text(encoding="utf-8")
        for match in re.finditer(r"BASH_SOURCE", text):
            window = text[max(0, match.start() - 400) : match.end() + 400]
            with self.subTest(pos=match.start()):
                self.assertRegex(
                    window,
                    r"(?i)bash-only|empty under zsh|ZSH_VERSION|wrong project root|wrong root",
                    "BASH_SOURCE must never appear as an unqualified recommendation",
                )


class GroundRulesCarriesTheRuleBesideTheWindowsOne(unittest.TestCase):
    """Both supported platforms' shell semantics belong in one place."""

    def test_the_section_exists(self):
        self.assertIn("## Sourced scripts and the default shell", GROUND_RULES.read_text(encoding="utf-8"))

    def test_it_sits_with_the_windows_shell_guidance(self):
        text = GROUND_RULES.read_text(encoding="utf-8")
        self.assertLess(
            text.index("## Windows and PowerShell"),
            text.index("## Sourced scripts and the default shell"),
        )

    def test_it_links_the_canonical_idiom_rather_than_restating_it(self):
        text = flat(GROUND_RULES)
        self.assertIn("SKILL.md#env-script-path-resolution", text)
        self.assertRegex(text, r"(?i)Do not restate it; link to it")

    def test_it_states_the_no_exit_rule(self):
        self.assertRegex(
            flat(GROUND_RULES), r"(?i)sourced script must never `exit` or `set -e`"
        )


class TheSymptomIsNamedWhereItLands(unittest.TestCase):
    def test_module_2_troubleshooting_connects_the_symptom_to_the_script(self):
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)`Unable to get settings`, or an empty `%s`" % SETTINGS_VAR)
        self.assertRegex(text, r"(?i)env script's path resolution, not Senzing")

    def test_it_says_the_symptom_carries_no_senz_code(self):
        """Routing a non-engine error through explain_error_code wastes the lookup."""
        for path in (MODULE_02, PHASE_1):
            with self.subTest(file=path.name):
                self.assertRegex(flat(path), r"(?i)no SENZ code")

    def test_it_attributes_the_string_to_the_snippet_guard_not_the_engine(self):
        """The re-check's finding: this is the sample program's own null-check."""
        for path in (MODULE_02, PHASE_1):
            with self.subTest(file=path.name):
                text = flat(path)
                self.assertRegex(text, r"(?i)null-check in Senzing's own official snippets")
                self.assertRegex(text, r"(?i)is \*\*unset\*\*|when `%s` is unset" % SETTINGS_VAR)

    def test_the_snippet_finding_carries_its_provenance(self):
        """INV-080: server version and date, and the tool that established it."""
        for path in (MODULE_02, PHASE_1):
            with self.subTest(file=path.name):
                self.assertRegex(
                    flat(path), r"(?i)`search_docs`.{0,60}1\.32\.1, 2026-07-28|1\.32\.1, 2026-07-28"
                )

    def test_verification_checks_it_before_reaching_for_explain_error_code(self):
        text = PHASE_1.read_text(encoding="utf-8")
        self.assertLess(
            text.index("If the failure names no SENZ code at all"),
            text.index('Call `explain_error_code(error_code="<code>"'),
        )

    def test_step_1a_list_numbering_stays_contiguous(self):
        """A stale '3.' after inserting an item renders as a restarted list."""
        text = PHASE_1.read_text(encoding="utf-8")
        block = text[text.index("### Step 1a"): text.index("### Step 2:")]
        markers = re.findall(r"(?m)^(\d+)\. ", block)
        self.assertEqual(markers, ["1", "2", "3", "4"], "Step 1a's ordered list must be 1-4")


class TheSourcingRuleIsNotRelaxed(unittest.TestCase):
    """This spec adds portability; it does not loosen the same-shell requirement."""

    def test_the_same_shell_sentence_is_unchanged(self):
        self.assertRegex(
            flat(MODULE_02),
            r"\*\*That is why `senzing-env\.sh` must be sourced in the same shell that launches "
            r"the JVM\*\* — not merely created\.",
        )

    def test_windows_keeps_its_own_script_and_idiom(self):
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)Windows keeps its own script")
        self.assertIn("%~dp0", text)

    def test_no_zsh_material_is_imposed_on_windows(self):
        self.assertRegex(flat(MODULE_02), r"(?i)none of the zsh material applies there")


class TheSnippetStaysLanguageAgnostic(unittest.TestCase):
    """INV-001/INV-052: the fix concerns the shell, not the bootcamper's language."""

    def test_the_idiom_mentions_no_programming_language(self):
        idiom = documented_idiom().lower()
        for lang in ("python", "java", "csharp", "c#", "rust", "typescript", "node"):
            with self.subTest(language=lang):
                self.assertNotIn(lang, idiom)

    def test_platform_specific_paths_are_deferred_to_mcp(self):
        """No hardcoded DYLD/LD values — sdk_guide owns those (INV-080)."""
        idiom = documented_idiom()
        self.assertRegex(idiom, r"sdk_guide\(topic='install'")
        self.assertNotRegex(idiom, r"(?m)^\s*export (DYLD|LD)_LIBRARY_PATH=")


class TheEnvVarNameIsTheDocumentedOne(unittest.TestCase):
    """Re-confirmed via search_docs(category='configuration') on 1.32.1, 2026-07-28."""

    def test_the_idiom_exports_the_documented_variable(self):
        self.assertIn("export %s=" % SETTINGS_VAR, documented_idiom())

    def test_the_config_path_matches_what_module_2_creates(self):
        """Step 8 writes config/engine_config.json; the guard must check that same file."""
        self.assertIn("config/engine_config.json", documented_idiom())
        self.assertIn("config/engine_config.json", flat(MODULE_02))


if __name__ == "__main__":
    unittest.main()
