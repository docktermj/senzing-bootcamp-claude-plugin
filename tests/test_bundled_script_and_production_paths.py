"""A path a step tells the guide to run must resolve where that step actually runs.

`deep-dive-audit-2026-07-30b`. Three path defects of one shape, none of which any existing
test could see, because each is a *string in prose* that is only wrong relative to a working
directory no test had modelled.

1. **A bundled script invoked by a bare project-relative path.** Module 7 said:

       python3 scripts/generate_discoveries_pdf.py

   Every other bundled-script invocation in the plugin resolves as
   `${CLAUDE_PLUGIN_ROOT}/scripts/…` with a skill-relative fallback, because the script ships
   *inside the plugin* while the command runs in the *bootcamp project* — and the project
   layout (INV-050) has no top-level `scripts/`, only `src/scripts/`. Run from a project root
   the command exits 2, `can't open file`. It was the only invocation of that generator, and
   the discoveries deliverable is produced on every path, so the realistic outcome was a
   guaranteed deliverable silently reported missing (the surrounding text is explicitly
   "report exactly what failed and continue").

2. **A production copy that flattened a path its own copied code depends on.** Graduation
   copied `data/senzing-ready/**` to `production/data/` while copying `src/load/**`
   *verbatim* to `production/src/load/`. The loading code reads `data/senzing-ready/`
   (INV-084), so the handover project's loader pointed at a directory that did not exist.

3. **An install doc covering two of three supported platforms.** The Claude Code CLI section
   installed on "macOS or Linux" only, with no Windows route and no line sending a Windows
   reader to the Desktop path — while INV-001 makes Windows supported and INV-158 makes the
   CLI one of the two interfaces the install docs must document.

Written as sweeps, not as three assertions about three lines, so the next one is caught too.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SKILLS = PLUGIN / "skills"
COMMANDS = PLUGIN / "commands"
SCRIPTS = PLUGIN / "scripts"
GRADUATION = SKILLS / "graduation" / "SKILL.md"
CLI_INSTALL_DOC = REPO_ROOT / "docs" / "README.md"

# The scripts that ship inside the plugin. A step that runs one of these is running a file
# that is NOT in the bootcamper's project, so the path has to be resolved, never assumed.
BUNDLED_SCRIPTS = sorted(p.name for p in SCRIPTS.glob("*.py"))

# How a resolved invocation is allowed to look. Either the env var the harness substitutes,
# or the explicit skill-relative fallback the plugin documents beside it, or a placeholder
# the surrounding prose resolves (module 3b's `<viz-server-path>`).
RESOLVED = (
    "${CLAUDE_PLUGIN_ROOT}",
    "<this-skill-dir>",
    "../../scripts/",
    "<helper>",
    "<viz-server-path>",
)


def prose_files():
    """Every file that can instruct the guide to run a command."""
    return sorted(SKILLS.rglob("*.md")) + sorted(COMMANDS.rglob("*.md"))


def invocation_lines():
    """(path, lineno, line) for each line invoking a bundled script with an interpreter."""
    out = []
    runner = re.compile(r"(?:^|\s)(?:python3?|py -3|[\w./\\-]*/(?:python3?|bin/python))\s")
    for path in prose_files():
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not runner.search(line):
                continue
            if any(name in line for name in BUNDLED_SCRIPTS):
                out.append((path, i, line.strip()))
    return out


class BundledScriptsAreInvokedByAResolvedPath(unittest.TestCase):
    def test_the_sweep_finds_the_known_invocations(self):
        """A sweep that matches nothing would pass forever."""
        found = invocation_lines()
        self.assertGreaterEqual(
            len(found),
            5,
            "the invocation sweep matched almost nothing — its regex or the "
            "BUNDLED_SCRIPTS list has drifted, and it is no longer testing anything",
        )
        names = {n for _, _, line in found for n in BUNDLED_SCRIPTS if n in line}
        self.assertIn("generate_recap_pdf.py", names)
        self.assertIn("generate_discoveries_pdf.py", names)

    def test_no_step_runs_a_bundled_script_by_an_unresolved_path(self):
        problems = []
        for path, lineno, line in invocation_lines():
            if not any(marker in line for marker in RESOLVED):
                problems.append(f"{path.relative_to(REPO_ROOT)}:{lineno}  {line}")
        self.assertEqual(
            [],
            problems,
            "a bundled script is invoked by a path that does not resolve from the "
            "bootcamp project (the plugin's scripts/ is not the project's):\n  "
            + "\n  ".join(problems),
        )

    def test_the_discoveries_generator_is_reachable(self):
        """The one that was broken, named explicitly so a regression is unambiguous."""
        text = (
            SKILLS
            / "module-07-query-visualize-discover"
            / "phase1-query-visualize.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '"${CLAUDE_PLUGIN_ROOT}/scripts/generate_discoveries_pdf.py"',
            text,
            "Module 7 must resolve the discoveries generator inside the plugin",
        )
        self.assertNotRegex(
            text,
            r"(?m)^\s*python3 scripts/generate_discoveries_pdf\.py\s*$",
            "the bare project-relative invocation is back; it exits 2 from a project root",
        )


class ProductionCopyPreservesThePathsItsCodeUses(unittest.TestCase):
    """Copied code is not rewritten, so its inputs must land where it looks for them."""

    def _copy_table_rows(self):
        rows = []
        for line in GRADUATION.read_text(encoding="utf-8").splitlines():
            if line.startswith("| `") and "production/" in line:
                cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
                if len(cells) >= 2:
                    rows.append((cells[0], cells[1]))
        return rows

    def test_the_copy_table_is_readable(self):
        rows = self._copy_table_rows()
        self.assertGreaterEqual(
            len(rows), 5, "graduation's Step 2 copy table no longer parses"
        )

    def test_senzing_ready_keeps_its_directory(self):
        rows = dict(self._copy_table_rows())
        dest = rows.get("data/senzing-ready/**")
        self.assertIsNotNone(dest, "the Senzing-ready copy row disappeared from Step 2")
        self.assertEqual(
            "production/data/senzing-ready/",
            dest,
            "the loading code is copied verbatim and reads data/senzing-ready/ "
            "(INV-084); flattening it to production/data/ ships a project whose "
            "loader points at a directory that does not exist",
        )

    def test_every_src_row_preserves_its_subdirectory(self):
        for source, dest in self._copy_table_rows():
            if source.startswith("src/"):
                self.assertEqual(
                    "production/" + source.replace("**", ""),
                    dest,
                    f"{source} must keep its path under production/ — copied code is "
                    "not rewritten, so a moved directory breaks its imports",
                )

    def test_the_excluded_raw_input_is_disclosed(self):
        """data/raw/ is excluded by design; a fast-pathed source's loader then has no input.

        Asserted per *paragraph* rather than by character distance: the disclosure is
        several wrapped sentences, and a proximity window either misses it or would pass
        on an unrelated mention elsewhere in an 850-line file.
        """
        text = GRADUATION.read_text(encoding="utf-8")
        self.assertIn("data/raw/", text, "the exclusion list lost data/raw/")

        paragraphs = [
            re.sub(r"\s+", " ", p)
            for p in re.split(r"\n\s*\n", text)
            if "fast-pathed source" in p
        ]
        self.assertTrue(
            paragraphs,
            "graduation no longer says what happens to a fast-pathed source's input, "
            "which data/raw/'s exclusion leaves out of production/",
        )
        disclosing = [
            p
            for p in paragraphs
            if "data/raw/" in p
            and "files-excluded" in p
            and "README" in p
        ]
        self.assertTrue(
            disclosing,
            "the fast-pathed paragraph must name data/raw/ as the excluded input AND "
            "route the disclosure to both the graduation report's files-excluded table "
            "and production/README.md — otherwise the missing input is silent.\n"
            "Paragraphs found:\n  " + "\n  ".join(paragraphs),
        )


class InstallDocsCoverEverySupportedPlatform(unittest.TestCase):
    """INV-001 makes Windows supported; INV-158 makes the CLI a documented interface."""

    def test_the_cli_section_has_a_windows_route(self):
        text = CLI_INSTALL_DOC.read_text(encoding="utf-8")
        self.assertIn(
            "install.ps1",
            text,
            "the Claude Code CLI install section gives no Windows command "
            "(verified against the official setup docs: `irm https://claude.ai/install.ps1 | iex`)",
        )
        self.assertIn(
            "install.sh",
            text,
            "the macOS/Linux install command disappeared",
        )

    def test_no_install_step_claims_two_platforms_are_the_set(self):
        """'on macOS or Linux' with no Windows line is how the gap read as complete."""
        flat = re.sub(r"\s+", " ", CLI_INSTALL_DOC.read_text(encoding="utf-8"))
        self.assertNotIn(
            "Claude Code CLI on macOS or Linux",
            flat,
            "this phrasing presents two platforms as the whole supported set",
        )

    def test_the_windows_command_is_powershell_shaped(self):
        """INV-167: a PowerShell command must not carry bash chaining operators."""
        for line in CLI_INSTALL_DOC.read_text(encoding="utf-8").splitlines():
            if "install.ps1" in line:
                self.assertNotIn("&&", line, "bash chaining in a PowerShell command")
                self.assertNotIn("||", line, "bash chaining in a PowerShell command")


class TheProseSweepIsNotVacuous(unittest.TestCase):
    """`prose_files()` is skills + commands. If either half stops matching, the path
    checks pass over a smaller corpus and report clean."""

    def test_both_halves_contribute(self):
        found = prose_files()
        self.assertGreater(len(found), 20, "corpus shrank to %d files" % len(found))
        self.assertTrue(any("skills" in p.parts for p in found), "no skill .md found")
        self.assertTrue(any("commands" in p.parts for p in found), "no command .md found")


if __name__ == "__main__":
    unittest.main()
