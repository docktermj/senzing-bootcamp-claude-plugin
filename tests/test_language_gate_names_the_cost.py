"""The programming-language gate states what choosing Python on Windows or macOS COSTS.

A Bootcamper on Windows 11 chose Python at the Bootcamp preparation language gate and learned two
modules later, at SDK setup, that the Senzing Python SDK is Linux-only. Continuing cost them a WSL2
install, a reboot, and a new Ubuntu user account. The annotation they saw was exactly what the rules
prescribed:

    1. Python - runs via Docker (the SDK doesn't install natively on Windows)

True, and not the information the choice needs. It names a **mechanism** where the Bootcamper needs
a **price**: a system-level install, administrator rights, a reboot. That is a reversible decision
presented as a costless one, at the one point where reversing it was free.

⚠️ **This guard covers the disclosure, not a machine probe.** The spec also proposed a silent
presence check for Docker/WSL2 at the gate so the annotation could say "already available" versus
"needs installing first". The maintainer held that for review — it adds behavior to a heavily-pinned
step (INV-056, INV-224, INV-251) — so the annotation names the cost accurately while still not
knowing whether the Bootcamper's machine already has the runtime. `TheProbeIsNotClaimed` pins that
boundary, so a later reader cannot mistake the disclosure for a capability check.

Source spec: `specs/language-gate-names-the-container-not-its-cost-and-omits-wsl2.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
PREP = PLUGIN / "skills" / "bootcamp-preparation" / "SKILL.md"
MODULE2 = PLUGIN / "skills" / "module-02-sdk-setup" / "SKILL.md"

#: Words that describe the PRICE rather than the routing.
#:
#: ⚠️ **This is an alternation, so mutation-testing it means removing every branch.** Negative
#: control 2026-08-21: deleting only the "administrator rights and, for WSL2, a reboot" clause left
#: the guard passing — correctly, because "means installing and running a Linux environment" is
#: still a cost statement. Blanking all five tokens inside the annotation-rules block fails it.
#: Recorded because the first attempt looked like a weak guard and was a weak mutation: with an
#: alternation, the mutation has to remove the *property*, not a *phrase*.
COST_VOCAB = re.compile(r"(?i)admin(istrator)? rights|reboot|system-level|installing and running")


def annotation_rules():
    """The per-platform annotation rules block at the language gate."""
    text = PREP.read_text(encoding="utf-8")
    start = text.index("Annotate an option **only where the Module 2 routing rules")
    end = text.index("The resulting shape (Linux", start)
    return re.sub(r"\s+", " ", text[start:end])


def routing_rules():
    text = MODULE2.read_text(encoding="utf-8")
    start = text.index("**Routing rules (apply in order):**")
    end = text.index("When a learner lands on Docker", start)
    return re.sub(r"\s+", " ", text[start:end])


class TheScanIsNotVacuous(unittest.TestCase):
    def test_both_regions_are_locatable(self):
        self.assertIn("macOS Apple Silicon", annotation_rules(),
                      "the annotation-rules block was not located")
        self.assertIn("Linux", routing_rules(), "the routing rules were not located")


class TheAnnotationNamesThePriceNotTheMechanism(unittest.TestCase):
    def setUp(self):
        self.rules = annotation_rules()

    def test_the_cost_is_stated(self):
        self.assertRegex(
            self.rules, COST_VOCAB,
            "the annotation rules describe the routing mechanism with no mention of what it "
            "costs (a system-level install, administrator rights, a reboot) - which is the "
            "defect: the Bootcamper cannot price the choice at the point of making it")

    def test_both_environment_routes_are_named(self):
        """The server returns two; the plugin used to relay one."""
        self.assertRegex(self.rules, r"(?i)Docker Desktop \*\*or\*\* WSL2|Docker or WSL2",
                         "only one environment route is named, but the server returns two")

    def test_the_routes_come_from_the_server_not_this_file(self):
        self.assertIn("sdk_guide(topic='install'", self.rules,
                      "the route list is asserted rather than sourced at gate time (INV-080)")
        self.assertRegex(self.rules, r"1\.33\.0, 2026-08-21",
                         "the server claim carries no version and date")

    def test_the_wsl2_clause_is_suppressed_on_macos(self):
        """WSL2 does not exist on macOS; the server's macos_arm note wrongly offers it."""
        self.assertRegex(
            self.rules, r"(?i)suppress the WSL2 half",
            "nothing tells the guide to drop the WSL2 clause on macOS, so the server's own "
            "macos_arm inaccuracy gets relayed to a Mac user")

    def test_no_worked_example_shows_the_mechanism_only_form(self):
        """The rule and its example must agree; the example is what gets copied."""
        flat = re.sub(r"\s+", " ", PREP.read_text(encoding="utf-8"))
        self.assertNotIn(
            "1. Python — runs via Docker (the SDK is Linux-only)` — and nothing platform-wide", flat,
            "the worked shape still shows the mechanism-only annotation, so a guide copying the "
            "example produces exactly the text this spec removed from the rule")


class RoutingRuleOneResolvesBothEnvironments(unittest.TestCase):
    def setUp(self):
        self.rules = routing_rules()

    def test_it_names_the_wsl2_outcome(self):
        self.assertRegex(
            self.rules, r"(?i)WSL2 \(Windows only\)",
            "routing rule 1 still resolves only to a container, so a Bootcamper who takes the "
            "server's other option lands on an outcome the rules do not describe - which is "
            "what happened on 2026-08-18")

    def test_the_wsl2_branch_resolves_to_linux_apt(self):
        self.assertRegex(
            self.rules, r"platform='linux_apt'",
            "the WSL2 branch does not say which platform it resolves to, leaving the rest of "
            "the module without a path to follow")

    def test_it_says_macos_has_only_the_container_route(self):
        self.assertRegex(
            self.rules, r"(?i)On macOS only the container route exists",
            "the rules do not distinguish macOS, where WSL2 is not available")


class TheProbeIsNotClaimed(unittest.TestCase):
    """Pins the held boundary: disclosure shipped, capability check did not."""

    def test_no_shipped_text_claims_the_runtime_is_already_present(self):
        flat = re.sub(r"\s+", " ", PREP.read_text(encoding="utf-8"))
        for claim in ("already available on this machine", "needs installing first"):
            with self.subTest(claim=claim):
                self.assertNotIn(
                    claim, flat,
                    "the gate claims to know whether the runtime is installed, but the presence "
                    "check was held for maintainer review - so this text would assert a "
                    "capability the plugin does not have")


if __name__ == "__main__":
    unittest.main()
