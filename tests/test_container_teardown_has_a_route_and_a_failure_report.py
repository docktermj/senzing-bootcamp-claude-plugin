"""Teardown has a container route, and says what the Bootcamper is told when it cannot confirm.

The teardown contract's primary route is "terminate by the recorded pid" and its fallback is
`lsof -ti:<port>` / `Get-NetTCPConnection`. **Both are host-shell routes**, and on the `docker` path
the container the bootcamp builds has neither tool: it follows the `linux_apt` steps inside a Debian
slim image, which ships no `procps` and no `lsof`. A run that reached for a command-line match inside
one got `exec: "…": executable file not found in $PATH` — and **the Bootcamper had already been told
the server would be stopped while it kept serving**, found only when the port was probed and still
answered 200.

Two things were missing and both are guarded here: a route that works with what a slim container
actually has (a POSIX shell whose `kill` is a builtin, and the `python3` the SDK install brings), and
a statement of what the Bootcamper is told when the port still answers afterwards.

⚠️ **`procps` is deliberately not added to the container build**, so this asserts the decision as
well as the route — an implicit decision is what let the gap sit. If a later change adds the package
for its own reasons, this test should be the thing that makes it a deliberate reversal.

⛔ **Establishes no invariant: INV-223 already governs all of it** — capture the pid, terminate by it,
fall back to the port, and *"the port being free is the exit condition"*, which forecloses trusting a
kill's exit status by construction (an exit code is not the port being free). This file asserts the
container application of that rule, not a new guarantee. Deriving the site set by scanning rather
than listing paths (INV-246).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
CONTRACT = SKILLS / "module-03b-truthset-visualization" / "visualization-api-reference.md"


def read(path):
    return path.read_text(encoding="utf-8")


def teardown_sites():
    """Every shipped file that instructs a teardown, found by scanning, never listed.

    A hardcoded list certifies the sites already thought of and is blind to the next one — which
    is the only one that matters (INV-246).
    """
    hits = []
    for path in sorted(SKILLS.rglob("*.md")):
        text = read(path)
        if re.search(r"(?i)lsof -ti|Get-NetTCPConnection", text):
            hits.append(path)
    return hits


class TheContractNamesAContainerRoute(unittest.TestCase):
    def test_it_states_that_both_host_routes_are_unavailable_in_the_container(self):
        text = read(CONTRACT)
        self.assertRegex(
            text, r"(?i)docker.{0,80}host-shell routes",
            "the contract does not say that its pid and port routes are both host-shell routes; a "
            "reader on the docker path has no signal that neither works there")
        for tool in ("procps", "lsof"):
            self.assertIn(tool, text, "the contract does not name the missing %r" % tool)

    def test_it_gives_a_route_that_needs_neither_missing_tool(self):
        text = read(CONTRACT)
        self.assertRegex(
            text, r"sh -c ['\"]kill",
            "no shell-builtin termination route is given. `/bin/kill` is a procps binary and is "
            "absent; `kill` as a shell builtin is not, which is the whole point")
        self.assertRegex(
            text, r"(?i)probe the port with `python3`|python3 -c",
            "no python3 port probe is given, so the port check still depends on lsof")

    def test_the_pid_namespace_is_addressed(self):
        """A host pid identifies the CONTAINER, not the server inside it."""
        text = read(CONTRACT)
        self.assertRegex(
            text, r"(?i)container-namespace pid|namespace",
            "the contract does not say which namespace the recorded pid belongs to. A host pid "
            "from `docker run` identifies the container, so signaling it stops everything")

    def test_the_procps_decision_is_explicit(self):
        text = read(CONTRACT)
        self.assertRegex(
            text, r"(?i)`procps` is deliberately (?:NOT|not) added",
            "the procps question is left implicit. Either the package is added to the container "
            "build or it is deliberately not; an unstated decision is what let this gap sit")


class TheExitStatusIsNotTheEvidence(unittest.TestCase):
    def test_the_contract_forbids_trusting_the_kills_exit_status(self):
        text = read(CONTRACT)
        self.assertRegex(
            text, r"(?i)never treat the kill's own exit status",
            "the contract does not forbid treating the kill's exit status as evidence the server "
            "stopped. INV-223 makes the port being free the exit condition, and an exit code is "
            "not the port being free")
        self.assertIn(
            "INV-223", text,
            "the container route must name the invariant that governs it (INV-183)")


class AFailedTeardownIsReportedNotClaimed(unittest.TestCase):
    def test_the_contract_says_what_the_bootcamper_is_told(self):
        text = read(CONTRACT)
        self.assertRegex(
            text, r"(?i)when teardown cannot confirm",
            "the contract does not say what the Bootcamper is told when the port still answers. "
            "That silence is how a Bootcamper walks away believing their machine is clean")
        self.assertRegex(
            text, r"(?i)continue without\s*\n?\s*the purge|without the purge",
            "the contract does not say to skip the purge on an unverified stop, which is the "
            "irreversible half (INV-131)")


class EveryTeardownSiteReachesTheContainerRule(unittest.TestCase):
    """The class, not the instance: any site teaching the host routes must reach the container one."""

    def test_each_site_names_the_container_case_or_links_the_full_rule(self):
        """⛔ Scoped to a WINDOW around the teardown instruction, not the whole file.

        A first version searched the file for `visualization-api-reference` or "full rule" and
        passed with the pointer deleted, because both strings occur elsewhere in these files for
        unrelated reasons. A file-scoped check on a corpus that mentions the target everywhere
        asserts nothing — the same defect this session hit twice in other guards.
        """
        offenders = []
        for path in teardown_sites():
            if path == CONTRACT:
                continue
            text = read(path)
            for m in re.finditer(r"(?i)lsof -ti|Get-NetTCPConnection", text):
                window = text[max(0, m.start() - 600):m.end() + 900]
                if not re.search(r"(?i)docker", window):
                    offenders.append("%s:%d — teardown route with no container case nearby"
                                     % (path.relative_to(REPO_ROOT),
                                        text[:m.start()].count("\n") + 1))
                else:
                    # ⛔ Assert the pointer RESOLVES, not that a string is present. A
                    # string-presence check passed with the pointer replaced by `nowhere.md`,
                    # because these files reference the contract more than once inside the
                    # window. A dangling pointer is the failure mode worth catching.
                    # Only PATH-shaped refs: a bare `name.md` in prose is a name, not a link,
                    # and resolving it against this file's directory is a false positive.
                    for ref in re.findall(r"`([^`]*/[^`]*\.md)`", window):
                        target = (path.parent / ref).resolve()
                        if not target.exists():
                            offenders.append(
                                "%s:%d — teardown guidance points at %s, which does not exist"
                                % (path.relative_to(REPO_ROOT),
                                   text[:m.start()].count("\n") + 1, ref))
                break
        self.assertEqual(
            [], offenders,
            "a file teaches the host-shell teardown routes without naming the container case or "
            "linking the file that states it. The routes silently do not work there:\n  %s"
            % "\n  ".join(offenders))

    def test_the_scan_found_the_sites(self):
        sites = teardown_sites()
        self.assertGreaterEqual(
            len(sites), 2,
            "only %d teardown site(s) found; the scan is near-vacuous" % len(sites))
        self.assertIn(CONTRACT, sites, "the canonical contract is not among the scanned sites")


if __name__ == "__main__":
    unittest.main()
