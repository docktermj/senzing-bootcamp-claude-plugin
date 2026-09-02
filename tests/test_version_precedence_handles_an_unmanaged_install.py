"""Step 1b resolves a version disagreement by its CAUSE, not by an unconditional precedence.

"Comparing the two versions" resolved the disagreement between `dpkg-query`/`rpm -q` and
`szBuildVersion.json` with one rule: **prefer the package manager's version string**. Its
worked example is a separator artifact — `4.3.3-26191` vs `4.3.3.26191`, the same version
written two ways — and for that case the rule is right. Stated unconditionally it is wrong
whenever the SDK on disk was not put there by the package manager.

Observed 2026-09-01, Ubuntu 24.04 (environment observation, not an MCP-sourced fact):

    dpkg-query -W senzingsdk-runtime          -> 4.3.4-26210
    /opt/senzing/er/szBuildVersion.json       -> 4.4.0.26242
    SzProduct.get_version() (after Step 3)    -> 4.4.0

Normalized, that is a genuine version difference, and the library that loads from
`/opt/senzing/er/lib/libSz.so` is the 4.4.0 one. Following the rule as written reports
"Senzing SDK is already installed (version 4.3.4-26210)" — a wrong number stated as fact about
the thing the module exists to establish.

⚠️ Not merely a developer-machine artifact: `sdk_guide(topic='install', platform='linux_apt')`
documents `dpkg-deb -x` extraction for containers, CI and no-sudo environments (re-verified
server 1.35.3, 2026-09-01). On that route no package is ever registered, `dpkg-query` reports
nothing, and the old rule sends the guide to the empty source and away from the correct one.

Enforces **INV-290** — two sources reporting the same environment fact are resolved by the
CAUSE of their disagreement, never by a fixed precedence, and an empty result from one
source is not a finding about the fact.

⚠️ What this asserts is that the branch SHIPS. Whether a live turn reports the right version
on a machine where the two genuinely disagree needs a `dry-run` phase 3 walk on such a
machine — which is how the defect was found in the first place.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
         "module-02-sdk-setup" / "SKILL.md")


def comparing_section():
    text = SKILL.read_text(encoding="utf-8")
    start = text.index("### Comparing the two versions")
    end = text.index("\n### ", start + 1)
    return text[start:end]


def flat(s):
    return re.sub(r"\s+", " ", s)


class TheTwoCausesAreResolvedDifferently(unittest.TestCase):
    def setUp(self):
        self.section = flat(comparing_section())

    def test_the_separator_case_and_the_real_difference_are_distinguished(self):
        self.assertRegex(
            self.section,
            r"(?i)disagree for two different reasons",
            "The section must distinguish the two causes. One unconditional precedence cannot "
            "serve both: a separator artifact and a genuinely different build need opposite "
            "resolutions.",
        )

    def test_the_separator_case_still_prefers_the_package_manager(self):
        self.assertRegex(
            self.section,
            r"(?i)same version, different separator",
            "The separator case must survive with its original resolution — the rule was right "
            "for the case it was written for, and this fix narrows it rather than reversing it.",
        )

    def test_a_genuine_difference_prefers_the_file_that_describes_what_loads(self):
        """⚠️ Asserts the INSTRUCTION and its reason, not the words 'szBuildVersion.json'."""
        self.assertRegex(
            self.section,
            r"(?i)genuinely different values",
            "The genuine-difference branch must be named as its own case.",
        )
        self.assertRegex(
            self.section,
            r"(?i)describes what will actually \*\*load\*\*, so it wins",
            "The genuine-difference branch must say the file wins, and why — it describes the "
            "library that loads. Without the reason a later editor reads the two branches as "
            "arbitrary and collapses them back into one rule.",
        )

    def test_an_empty_package_manager_result_is_not_absence(self):
        self.assertRegex(
            self.section,
            r"(?i)reports nothing at all",
            "The section must handle the package manager reporting nothing.",
        )
        self.assertRegex(
            self.section,
            r'(?i)not\*?\*? "not installed"',
            "Empty output must be named as NOT meaning absent. Concluding 'not installed' from "
            "it sends a Bootcamper with a working SDK to reinstall it, which this step opens by "
            "forbidding.",
        )

    def test_the_documented_extraction_route_is_cited_as_the_generalizing_case(self):
        """It is the difference between a maintainer-box oddity and a shipped environment class."""
        self.assertRegex(
            self.section, r"dpkg-deb -x",
            "The extraction route must be named. It is what makes the unmanaged install a case "
            "the server itself documents rather than a local artifact.",
        )
        self.assertRegex(
            self.section, r"(?i)containers, CI and no-sudo",
            "Naming the environment class is what tells the reader this is reachable for a "
            "Bootcamper, not only on the machine it was found on.",
        )
        self.assertRegex(
            self.section, r"sdk_guide\(topic='install', platform='linux_apt'\)",
            "The claim must name the route that serves it, with a version and date (INV-080).",
        )


class TheAuthoritativeTiebreakerIsNamed(unittest.TestCase):
    def setUp(self):
        self.section = flat(comparing_section())

    def test_get_version_is_named_as_the_tiebreaker(self):
        self.assertRegex(
            self.section, r"SzProduct\.get_version\(\)",
            "The primary route must be named as the tiebreaker — it is authoritative for the "
            "library that actually loads, and the package manager is not in that chain at all.",
        )

    def test_it_says_why_the_tiebreaker_is_unavailable_at_step_1(self):
        """The failure is reachable precisely because the authority arrives late."""
        self.assertRegex(
            self.section, r"(?i)until Step 3's environment script exports `?LD_LIBRARY_PATH",
            "The section must say why the authoritative route is not available at Step 1. That "
            "is what makes the filesystem fallback load-bearing rather than an edge case — and "
            "it is the same coupling `step-1-says-skip-step-3-entirely-then-says-not-entirely` "
            "fixed in this file.",
        )

    def test_a_wrong_reported_version_is_corrected_aloud(self):
        self.assertRegex(
            self.section, r"(?i)correct the version aloud",
            "If Step 1 reported the package manager's number and Step 3 disproves it, the "
            "correction must be spoken. A silently superseded version leaves the Bootcamper "
            "holding a number they were told as fact.",
        )


class TheOriginalObservationSurvives(unittest.TestCase):
    """The spec's fourth criterion: preserve the dated observation, do not delete it."""

    def test_the_2026_07_31_observation_is_still_recorded(self):
        section = flat(comparing_section())
        self.assertRegex(
            section, r"4\.3\.3-26191 install, 2026-07-31",
            "The original dated observation must be preserved. It is the evidence for the "
            "separator branch, and deleting it would leave that branch asserted with nothing "
            "behind it.",
        )

    def test_both_observations_are_marked_observation_only(self):
        section = flat(comparing_section())
        self.assertGreaterEqual(
            len(re.findall(r"(?i)environment observation, not an MCP-sourced fact", section)), 2,
            "Both the 2026-07-31 separator observation and the 2026-09-01 version-split "
            "observation are environment observations. Each needs its own marker — a single "
            "one covering both is the shape that let a sibling caveat in this same file go "
            "half-stale (INV-149).",
        )


if __name__ == "__main__":
    unittest.main()
