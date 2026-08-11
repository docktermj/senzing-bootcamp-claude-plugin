"""INV-199: the bootcamp never writes outside the generated project to configure the environment.

This is the plugin's only rule about files *outside* the project directory. Every other
file-placement rule — INV-050's tree, INV-108, the `docs/` rules — governs where things go
inside it, so nothing else in the suite would notice a step that appended to `~/.zshrc`.

It shipped unregistered and unasserted until 2026-08-11: stated at two sites in the plugin's
own prose (`ground-rules.md` "File placement", `module-02-sdk-setup/SKILL.md` Step 8) and
present in no invariant and no test. Found by `production-readiness-audit`'s reverse sweep —
a hard rule whose section cited no invariant.

**Why a guard rather than trust.** The most likely breach is not carelessness, it is
compliance with the MCP server: `sdk_guide(topic='install', platform='macos_arm')` returns
"DYLD_LIBRARY_PATH must be set at the shell level before any JVM or Python launch. Add to
~/.zshrc to persist" (re-verified server 1.32.8, 2026-08-11). That is correct advice for a
human operator, and a step that follows it on the Bootcamper's behalf breaks self-containment
while looking like it did the right thing. So the test does not merely check the prohibition
is stated — it checks that every *mention* of a global profile path is a prohibition or a
relay caveat, never an instruction.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GROUND_RULES = PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md"
MODULE_02 = PLUGIN / "skills" / "module-02-sdk-setup" / "SKILL.md"

#: Global shell profiles, POSIX and Windows. INV-001 makes Windows supported, so a rule
#: naming only the POSIX three is incomplete rather than merely terse.
PROFILE_PATHS = re.compile(r"~/\.zshrc|~/\.bashrc|~/\.profile|\$PROFILE", re.I)

#: Wording that makes a mention safe: a prohibition, or a relay that disclaims acting on it.
SAFE = re.compile(
    r"never|not\s+modify|off-limits|do not act|does not (?:do so|edit)|forbidden|instead",
    re.I,
)

#: Files that quote the rule for illustration rather than instructing.
ILLUSTRATIVE = {"bootcamp_recap.example.md"}


def shipped_text_files():
    for path in sorted(PLUGIN.rglob("*")):
        if path.suffix in {".md", ".py"} and path.is_file():
            yield path


class TheProhibitionIsStatedAtBothAuthoritativeSites(unittest.TestCase):
    """A rule stated in one place is a rule half the guide never reads.

    The audit's own spec named only `module-02-sdk-setup/SKILL.md` and missed
    `ground-rules.md`, which is the always-loaded file — the same incomplete-application
    class the rule itself is guarding against.
    """

    def test_ground_rules_states_it(self):
        text = GROUND_RULES.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?i)never modify global shell config")
        self.assertIn("INV-199", text)

    def test_module_02_states_it(self):
        text = MODULE_02.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?i)NEVER modify the user's global shell configuration")
        self.assertIn("INV-199", text)

    def test_both_sites_name_windows_not_only_posix(self):
        """INV-001 makes Windows supported; a POSIX-only prohibition does not bind there."""
        for path in (GROUND_RULES, MODULE_02):
            with self.subTest(file=path.name):
                self.assertIn("$PROFILE", path.read_text(encoding="utf-8"))

    def test_the_project_local_alternative_is_named(self):
        """A prohibition with no alternative gets worked around, not obeyed."""
        for path in (GROUND_RULES, MODULE_02):
            with self.subTest(file=path.name):
                self.assertRegex(
                    path.read_text(encoding="utf-8"),
                    r"(?i)project-local environment script",
                )


class NoShippedFileInstructsWritingToAGlobalProfile(unittest.TestCase):
    def test_every_mention_is_a_prohibition_or_a_relay_caveat(self):
        offenders = []
        scanned = 0
        for path in shipped_text_files():
            if path.name in ILLUSTRATIVE:
                continue
            text = path.read_text(encoding="utf-8")
            # Match against the whole PARAGRAPH, not the line. Prose here wraps at ~100
            # columns, so a prohibition's own continuation lines carry the path without
            # carrying the word "never" — scanning line-by-line flags the rule as a
            # violation of itself. (This test did exactly that on its first run.)
            offset = 0
            for para in text.split("\n\n"):
                start_line = text[:offset].count("\n") + 1
                offset += len(para) + 2
                if not PROFILE_PATHS.search(para):
                    continue
                scanned += 1
                if not SAFE.search(para):
                    flat = " ".join(para.split())[:90]
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{start_line}  {flat}")
        self.assertGreaterEqual(
            scanned, 2,
            "the profile-path scan matched almost nothing — the pattern has drifted and this "
            "check would pass vacuously",
        )
        self.assertEqual(
            [], offenders,
            "a shipped file mentions a global shell profile without forbidding or disclaiming "
            "it — INV-199 allows relaying MCP guidance, never acting on it:\n  "
            + "\n  ".join(offenders),
        )


class TheRelayCaseIsCalledOutWhereItHappens(unittest.TestCase):
    """INV-183: the step that relays install guidance names the rule governing it."""

    def test_module_02_warns_that_sdk_guide_will_suggest_persisting(self):
        text = MODULE_02.read_text(encoding="utf-8")
        flat = text.replace("`", "").replace("*", "")   # emphasis must not decide the match
        self.assertRegex(flat, r"(?i)sdk_guide will tell you to persist to a shell profile")
        self.assertRegex(flat, r"(?i)do not act on it")

    def test_the_relayed_quotation_carries_its_provenance(self):
        """INV-080: a Senzing fact in shipped text says which call and version produced it."""
        text = MODULE_02.read_text(encoding="utf-8")
        i = text.index("sdk_guide` will tell you to persist")
        para = text[i:text.index("\n\n", i)]
        self.assertIn("sdk_guide(topic='install', platform='macos_arm'", para)
        self.assertRegex(para, r"MCP server 1\.\d+\.\d+, \d{4}-\d{2}-\d{2}")


if __name__ == "__main__":
    unittest.main()
