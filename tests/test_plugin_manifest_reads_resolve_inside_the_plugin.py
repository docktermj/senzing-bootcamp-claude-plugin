"""A bundled file must be read from the plugin serving the run, not from whichever copy is found.

`plugin-version-resolves-to-the-running-plugin-root`. On 2026-08-15 a bootcamper's WELCOME
banner read `Senzing Bootcamp v0.5.0` while 0.5.1 was serving the invocation.
`$CLAUDE_PLUGIN_ROOT` was unset, the manifest read had no documented fallback, and the guide
searched the filesystem — finding a second checkout of the plugin repo that reports 0.5.0.
Both were real plugin roots. The wrong version then flows into the feedback entry, the recap
header and the recap PDF's provenance block, all of which read the same manifest.

INV-185 already required this resolution — `${CLAUDE_PLUGIN_ROOT}/…` with the documented
skill-relative fallback — but only for *running a bundled script*, and its guard
(`test_bundled_script_and_production_paths.py`) sweeps only lines invoking a Python
interpreter. Reading the manifest matched neither the rule nor the sweep.

Enforces **INV-252** (a read of a bundled plugin file resolves inside the plugin serving the
run — `${CLAUDE_PLUGIN_ROOT}`, else the skill-relative fallback, else "Unknown" — and never by
searching the filesystem), which names this file. INV-252 is the generalisation of INV-185:
reading a bundled file resolves the same way running one does.

⚠️ **What this test cannot do.** The defect was a filesystem search improvised at runtime; it
exists in no file, so no file-reading guard can watch it happen. What is asserted here is that
the rule ships, that every shipped manifest path resolves, and that the one hook injecting the
version into the guide's context resolves it itself rather than handing over a variable that
may be unset. A clean run is evidence the plugin no longer *invites* the search — not evidence
the search cannot recur.

Written as sweeps over derived site sets, never over hardcoded paths (INV-246): the spec named
the sites its author noticed, which is exactly the wrong set when a rule was applied
incompletely.

Run:  python3 -m unittest discover -s tests
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
HOOK = PLUGIN / "scripts" / "feedback-capture.py"

#: The manifest path as it may appear in shipped prose. Both branches of the documented
#: resolution, and nothing else.
ENV_BRANCH = "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"
SKILL_RELATIVE_BRANCH = "<this-skill-dir>/../../.claude-plugin/plugin.json"

#: Where the rule is defined. Consumers may point here instead of restating it.
RULE_OWNER = "onboarding-flow.md"

#: A statement forbidding the search. Matched loosely on purpose -- the wording is prose and
#: will be reworded; what must survive is that some site says do not go looking.
NO_SEARCH = re.compile(r"never\s+(?:be\s+)?(?:found\s+by\s+)?(?:search\w*|by\s+search\w*)", re.I)


def shipped_prose():
    """Every shipped file that can instruct the guide."""
    return sorted(PLUGIN.rglob("*.md")) + sorted(PLUGIN.rglob("*.py"))


def files_naming_the_manifest():
    """Files that name a path to the plugin manifest -- the sites the rule governs."""
    return [p for p in shipped_prose() if ".claude-plugin/plugin.json" in p.read_text(encoding="utf-8")]


def files_reading_the_version():
    """Files that tell the guide to read the version out of the manifest.

    Derived by scanning for the phrase the shipped text uses for it, so a new consumer is
    swept in without this test being edited.
    """
    return [p for p in shipped_prose() if "plugin manifest" in p.read_text(encoding="utf-8")]


def blocks(text):
    """Blank-line-separated blocks.

    Scoping matters more than it looks. A file-wide check let two of the four pre-fix sites
    pass, because both happened to name `onboarding-flow.md` somewhere else entirely -- so a
    bare manifest path went unflagged on the strength of an unrelated cross-reference three
    hundred lines away. A rule has to be cited where the path is written or it is not cited.
    """
    return [b for b in re.split(r"\n\s*\n", text) if b.strip()]


def context_injecting_scripts():
    """Hook scripts that inject text into the guide's context."""
    return [p for p in sorted((PLUGIN / "scripts").glob("*.py"))
            if "additionalContext" in p.read_text(encoding="utf-8")]


class TheSweepsAreNotVacuous(unittest.TestCase):
    """A sweep matching nothing passes forever. Anchor each one to a known site."""

    def test_the_manifest_path_sweep_finds_the_rule_owner(self):
        names = {p.name for p in files_naming_the_manifest()}
        self.assertIn(RULE_OWNER, names, "the manifest-path sweep no longer reaches the rule's own site")
        self.assertGreaterEqual(len(names), 2, "the manifest-path sweep has drifted to almost nothing")

    def test_the_version_reader_sweep_finds_more_than_one_consumer(self):
        names = {p.name for p in files_reading_the_version()}
        self.assertIn(RULE_OWNER, names)
        self.assertGreaterEqual(
            len(names), 3,
            "the version is read by the banner, the feedback entry, the recap header and the "
            "recap provenance block -- a sweep finding fewer has stopped testing them",
        )

    def test_the_hook_sweep_finds_the_feedback_hook(self):
        self.assertIn(HOOK, context_injecting_scripts())


class EveryManifestPathResolvesInsideTheRunningPlugin(unittest.TestCase):
    def test_no_site_names_the_manifest_without_the_documented_resolution(self):
        problems = []
        for path in files_naming_the_manifest():
            if path.name == RULE_OWNER:
                continue  # where the rule is defined; checked whole-file by TheRuleItselfShips
            for block in blocks(path.read_text(encoding="utf-8")):
                if ".claude-plugin/plugin.json" not in block:
                    continue
                if ENV_BRANCH in block and SKILL_RELATIVE_BRANCH in block:
                    continue
                if RULE_OWNER in block:  # defers to where the rule is defined
                    continue
                problems.append(f"{path.relative_to(REPO_ROOT)}  {block.strip()[:90]}…")
        self.assertEqual(
            [], problems,
            "a site names the plugin manifest without the documented resolution "
            "(${CLAUDE_PLUGIN_ROOT} then the skill-relative fallback) and without citing "
            f"{RULE_OWNER} where the path is written, so an unset CLAUDE_PLUGIN_ROOT leaves "
            "it unspecified:\n  " + "\n  ".join(problems),
        )

    def test_every_version_reader_states_or_cites_the_rule(self):
        problems = []
        for path in files_reading_the_version():
            if path.name == RULE_OWNER:
                continue
            for block in blocks(path.read_text(encoding="utf-8")):
                if "plugin manifest" not in block:
                    continue
                if RULE_OWNER in block or (ENV_BRANCH in block and SKILL_RELATIVE_BRANCH in block):
                    continue
                problems.append(f"{path.relative_to(REPO_ROOT)}  {block.strip()[:90]}…")
        self.assertEqual(
            [], problems,
            "a step reads the plugin version without stating the resolution or citing "
            f"{RULE_OWNER} beside it; every consumer must resolve it the same way or they "
            "report different versions for one run:\n  " + "\n  ".join(problems),
        )


class TheRuleItselfShips(unittest.TestCase):
    """The three branches, in order, and the prohibition that made them necessary."""

    def setUp(self):
        self.text = (PLUGIN / "skills" / "bootcamp-onboarding" / RULE_OWNER).read_text(encoding="utf-8")

    def test_the_three_branches_ship_in_order(self):
        env = self.text.index(ENV_BRANCH)
        fallback = self.text.index(SKILL_RELATIVE_BRANCH)
        self.assertLess(env, fallback, "the env-var branch must be tried before the skill-relative one")
        self.assertIn('"Unknown"', self.text[fallback:], "the final branch must report Unknown, not a guess")

    def test_the_filesystem_search_is_forbidden(self):
        self.assertRegex(
            self.text, NO_SEARCH,
            "the ⛔ against searching the filesystem for a plugin.json is gone -- it is the "
            "whole defect, and the fallback alone does not forbid the search",
        )

    def test_the_prohibition_reaches_every_consumer(self):
        """A rule stated only where it is defined is not reachable at the step it governs."""
        missing = []
        for path in files_reading_the_version():
            if path.name == RULE_OWNER:
                continue  # the rule's own site, checked above
            for block in blocks(path.read_text(encoding="utf-8")):
                if "plugin manifest" not in block:
                    continue
                if NO_SEARCH.search(block) or "searching" in block or "go looking" in block:
                    continue
                missing.append(f"{path.relative_to(REPO_ROOT)}  {block.strip()[:90]}…")
        self.assertEqual(
            [], missing,
            "a step that reads the plugin version carries no warning against searching for "
            "one; INV-183 requires a rule binding a step to be reachable at that step:\n  "
            + "\n  ".join(missing),
        )


class TheHookResolvesTheVersionItself(unittest.TestCase):
    """Claude Code substitutes the hook's args, never the text the hook injects."""

    @staticmethod
    def run_hook(hook_path, cwd):
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps({"prompt": "I have feedback"}),
            capture_output=True, text=True, cwd=str(cwd), timeout=60,
        )
        if not proc.stdout.strip():
            return ""
        return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]

    @staticmethod
    def scratch_project(root):
        config = Path(root) / "config"
        config.mkdir(parents=True, exist_ok=True)
        (config / "bootcamp_progress.json").write_text("{}\n", encoding="utf-8")
        return root

    def test_no_injected_context_carries_an_unexpanded_variable(self):
        """Asserted against what the hooks EMIT, not against their source.

        A source scan would flag the comment explaining why the variable must not be
        injected, which is the one mention worth keeping. Hooks that emit nothing for this
        prompt pass trivially -- the sweep anchor above is what keeps that from being the
        whole test.
        """
        problems = []
        for script in context_injecting_scripts():
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    ctx = self.run_hook(script, self.scratch_project(Path(tmp)))
                except (ValueError, KeyError):
                    continue  # emits a different shape; not a context injection for this prompt
            if "${CLAUDE_PLUGIN_ROOT}" in ctx:
                problems.append(str(script.relative_to(REPO_ROOT)))
        self.assertEqual(
            [], problems,
            "a hook injects ${CLAUDE_PLUGIN_ROOT} into the guide's context, where nothing "
            "substitutes it -- the hook knows its own path and must resolve the value:\n  "
            + "\n  ".join(problems),
        )

    def test_the_hook_injects_the_running_plugins_version(self):
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self.run_hook(HOOK, self.scratch_project(Path(tmp)))
        self.assertIn(
            expected, ctx,
            "the feedback hook must inject the version of the plugin it ships in, so the "
            "entry records the code that actually ran",
        )

    def test_an_unreadable_manifest_yields_unknown_not_a_guess(self):
        """Copied where no manifest sits above it -- the branch that must never invent a number."""
        with tempfile.TemporaryDirectory() as tmp:
            fake_plugin = Path(tmp) / "fake-plugin" / "scripts"
            fake_plugin.mkdir(parents=True)
            copy = fake_plugin / HOOK.name
            shutil.copyfile(HOOK, copy)
            ctx = self.run_hook(copy, self.scratch_project(Path(tmp) / "project"))
        self.assertIn("Unknown", ctx, "an unresolvable version must be reported as Unknown")
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]
        self.assertNotIn(
            expected, ctx,
            "the hook found a version with no manifest above it -- it is searching, which is "
            "the defect this whole file exists for",
        )


if __name__ == "__main__":
    unittest.main()
