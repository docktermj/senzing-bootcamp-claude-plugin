"""A 403 on a CORD fetch has a documented way forward, and it is not a retry.

Module 4's "CORD fetch integrity" section was written from a **429** incident and gave a
remedy only for that status: retry with a short backoff. A **403** is reachable on the
bootcamp's most likely path and had no remedy at all, so collection simply stopped.

Measured 2026-09-01, Ubuntu 24.04 / Python 3.12.3 — reproducing 2026-08-31 exactly:

    source_download_url (senzing.com), default UA Python-urllib/3.12 -> HTTP 403
    source_download_url, User-Agent curl/8.5.0                       -> HTTP 200
    source_download_url, User-Agent Mozilla/5.0                      -> HTTP 403
    download_url (mcp.senzing.com), default UA                       -> HTTP 200

Python is the bootcamp's most likely language, the module tells the guide to fetch "in
whatever language the Bootcamper chose", and ``urllib.request`` is the zero-dependency
choice a guide reaches for first. A working route was in the same response the whole time.

⛔ The fix must never be a spoofed User-Agent: it is the wrong thing to teach, and
``Mozilla/5.0`` measured **403** on the same host in the same run, so it does not even work.

⚠️ This is an observation of a web host from one machine, not an MCP-reported fact
(INV-080/INV-149), so the guard asserts it is dated and scoped -- never that it is timeless.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "plugins" / "senzing-bootcamp" / "skills"
MODULE_4 = SKILLS / "module-04-data-collection" / "SKILL.md"


def flat(s):
    return re.sub(r"\s+", " ", s)


def fetch_integrity_section():
    """The CORD fetch integrity block -- from its anchor to the end of check 3."""
    text = MODULE_4.read_text(encoding="utf-8")
    start = text.find("**⛔ CORD fetch integrity")
    assert start != -1, "the CORD fetch integrity section was not found -- renamed?"
    nxt = text.find("\n## ", start)
    return text[start: nxt if nxt != -1 else len(text)]


class ThePreferredRouteIsStatedWithItsReason(unittest.TestCase):
    def setUp(self):
        self.section = flat(fetch_integrity_section())

    def test_download_url_is_preferred(self):
        self.assertRegex(
            self.section,
            r"(?i)prefer `?download_url`?[^.]{0,80}over[^.]{0,60}source_download_url",
            "Module 4 must state a preference for the MCP-hosted `download_url`. Both URLs "
            "arrive in the same citation and look equally available; one of them is refused "
            "to programmatic clients.",
        )

    def test_the_reason_is_given_not_just_the_rule(self):
        """A bare preference is followed until it is inconvenient; a reason survives."""
        self.assertRegex(
            self.section, r"(?i)restricted[- ]egress|only `?mcp\.senzing\.com`? (?:reachable|allowed)",
            "The preference must carry its reason -- the MCP endpoint is served to "
            "programmatic clients and is what keeps working when egress is restricted. "
            "Without it the next editor reads the preference as arbitrary and drops it.",
        )


class ForbiddenStatusHasItsOwnBranch(unittest.TestCase):
    def setUp(self):
        self.section = flat(fetch_integrity_section())

    def test_403_is_named(self):
        self.assertIn(
            "403", self.section,
            "403 must appear in the fetch-integrity guidance. It was reachable on the most "
            "likely path with no documented next step, so collection terminated.",
        )

    def test_403_routes_to_the_other_url_rather_than_retrying(self):
        """⚠️ Asserts the INSTRUCTION -- switch URLs -- not merely that '403' appears."""
        self.assertRegex(
            self.section,
            r"(?i)403[^.]{0,60}(?:do not retry|not a throttle)|"
            r"(?:do not retry|not a throttle)[^.]{0,60}403",
            "The 403 branch must say retrying does not help. A 403 is a refusal; a backoff "
            "burns the Bootcamper's time and fails anyway.",
        )
        self.assertRegex(
            self.section,
            r"(?i)(?:re-?fetch|switch)[^.]{0,120}(?:other URL|`?download_url`?)",
            "The 403 branch must route to the alternate URL from the same response. Naming "
            "the failure without the remedy is the gap this fix exists to close.",
        )

    def test_the_429_backoff_survives(self):
        for phrase in ("429", "backoff"):
            self.assertIn(
                phrase, self.section,
                "Adding the 403 branch must not disturb the 429 guidance, which was itself "
                "verified live against a four-source fetch that lost two sources.",
            )

    def test_all_three_checks_survive(self):
        for check in ("Check the HTTP status", "Compare the record count",
                      "Never write an unverified fetch"):
            self.assertIn(
                check, self.section,
                "All three integrity checks must remain -- they behaved correctly and are "
                "not what this fix changes.",
            )


class TheObservationIsDatedAndScoped(unittest.TestCase):
    """INV-080/INV-149: a web-host behavior is not an MCP fact and may not read as one."""

    def setUp(self):
        self.section = flat(fetch_integrity_section())

    def test_it_is_marked_observation_only(self):
        self.assertRegex(
            self.section, r"(?i)observation, not an MCP-sourced fact|observation-only",
            "The 403 finding must be marked as an observation rather than a Senzing-reported "
            "fact. No MCP route reports this, and a reader must be able to tell the "
            "difference between what the server said and what one machine saw.",
        )

    def test_it_carries_a_date_and_the_client_it_was_measured_with(self):
        self.assertRegex(self.section, r"20\d\d-\d\d-\d\d",
                         "The observation must carry the date it was measured.")
        self.assertRegex(
            self.section, r"(?i)Python-urllib|urllib\.request",
            "The observation must name the client it was measured with -- the split is by "
            "User-Agent, so 'senzing.com returns 403' without the client is not reproducible.",
        )


class NothingInstructsASpoofedUserAgent(unittest.TestCase):
    """Derived by scanning all shipped markdown, not by checking the file just edited."""

    def test_no_shipped_file_instructs_setting_a_user_agent(self):
        instructs = re.compile(
            r"(?i)(?:set|send|pass|use|supply|spoof)\s+(?:an?\s+|the\s+)?"
            r"(?:custom\s+|different\s+|browser\s+)?user[- ]agent")
        offenders = []
        for md in sorted(SKILLS.rglob("*.md")):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").split("\n"), 1):
                if not instructs.search(line):
                    continue
                # ⚠️ Self-pinning: the line that FORBIDS it must quote it to be followable.
                if re.search(r"(?i)never set|do not set|never send|not a working", line):
                    continue
                offenders.append("%s:%d" % (md.relative_to(REPO), lineno))
        self.assertEqual(
            [], offenders,
            "No shipped guidance may instruct disguising the client. It teaches the wrong "
            "habit, and `Mozilla/5.0` measured 403 on the same host anyway. Offenders: %s"
            % offenders,
        )

    def test_the_prohibition_is_stated_where_the_temptation_is(self):
        self.assertRegex(
            flat(fetch_integrity_section()), r"(?i)never set a misleading user-agent",
            "The prohibition belongs in the fetch section itself. A reader hitting the 403 "
            "reaches for the User-Agent workaround precisely here, and a rule stated "
            "elsewhere is one they will not be reading at that moment.",
        )


if __name__ == "__main__":
    unittest.main()
