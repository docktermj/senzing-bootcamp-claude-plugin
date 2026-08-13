"""An unreachable MCP server has two causes, and only one of them is a network problem.

The bootcamp rests entirely on the Senzing MCP server (INV-080), and the plugin ships `.mcp.json`
pointing at the public endpoint. At many companies adding a new external MCP server is restricted
or prohibited. Such a bootcamper hits the same surface symptom as someone behind a misconfigured
proxy -- "unreachable" -- and the step 0b advice they used to get was network troubleshooting for a
problem no proxy configuration fixes. They did everything right and had nowhere to go.

So the failure branch must ASK which blocker it is, and the policy branch must give a real route
plus a named contact.

⚠️ **What the server documents here changed between the spec and its implementation, and the tests
below pin the CURRENT state deliberately.** The spec (2026-07-31, server 1.32.3) cited two routes
from live tool descriptions: a **private deployment**, and a **stdio mode** running a local
`sz-mcp-coworker` binary. Re-verified at **1.32.9, 2026-08-13**:

* **private deployment** -- still named, in `get_capabilities`' tool manifest (the `get_sample_data`
  entry): "For full record access, call the MCP server endpoint directly ... or use the private
  deployment." Citable.
* **stdio mode / `sz-mcp-coworker`** -- **gone.** Neither string appears in `sdk_guide`'s description
  nor anywhere in the `get_capabilities` manifest. Whether the mode was retired or the text trimmed
  cannot be told from here, so the plugin MUST NOT offer it: a fact the server no longer states is
  not a fact the plugin may assert (INV-080).

That is why `test_stdio_mode_is_not_offered_as_a_route` exists and asserts an absence. It is the
unusual case where pinning "do not say X" is right rather than fragile, because the underlying rule
is INV-080 and the claim's own `MCP-NEGATIVE` marker carries the re-check date -- so if a later
server restores the mode, the marker is the thing that surfaces on the worklist and this test is
rescoped rather than silently outliving its premise.

Enforces **INV-215**.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ONBOARDING = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "bootcamp-onboarding"
              / "onboarding-flow.md")
GROUND_RULES = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "bootcamp-onboarding"
                / "ground-rules.md")
POINTER = "\U0001f449"


def onboarding():
    return ONBOARDING.read_text(encoding="utf-8")


def policy_branch():
    """Step 0c's body — the policy branch."""
    text = onboarding()
    start = text.index("## 0c.")
    end = text.index("\n## 1. Project setup", start)
    return text[start:end]


class TheFailureBranchSeparatesTheTwoCauses(unittest.TestCase):
    def test_the_health_check_asks_which_blocker_it_is(self):
        text = onboarding()
        start = text.index("## 0b.")
        end = text.index("## 0c.", start)
        branch = text[start:end]
        self.assertIn(
            POINTER, branch,
            "0b's failure path must end on a question separating connectivity from policy — the "
            "two causes share a symptom and need different answers",
        )
        self.assertRegex(
            branch, r"(?i)allowed to add an external MCP server",
            "the separating question must ask about permission, not about the network",
        )

    def test_both_answers_are_routed(self):
        text = onboarding()
        branch = text[text.index("## 0b."):text.index("## 0c.")]
        self.assertRegex(branch, r"(?i)connectivity", "the yes branch keeps the network advice")
        self.assertRegex(branch, r"(?i)polic", "the no branch is named as a policy failure")
        self.assertRegex(
            branch, r"0c",
            "the policy answer must route somewhere concrete, not just be acknowledged",
        )

    def test_a_policy_answer_is_not_answered_with_proxy_advice(self):
        """The original defect: connectivity troubleshooting offered to a policy-blocked reader.

        Asserts the absence of *imperative* network advice, not of the word "proxy". The no-branch
        legitimately says "which no amount of proxy configuration fixes" — that sentence exists to
        rule the remedy out. An earlier version of this test banned the word and failed on correct
        text, which is the same mistake as measuring a proxy for the property instead of the
        property.
        """
        branch = onboarding()
        branch = branch[branch.index("## 0b."):branch.index("## 0c.")]
        no_branch = branch[branch.index("**No**"):]
        for imperative in ("Verify internet connectivity", "allowlist mcp.senzing.com",
                           "say \"retry\""):
            with self.subTest(advice=imperative):
                self.assertNotIn(
                    imperative, no_branch,
                    "the policy branch must not hand the bootcamper network troubleshooting or a "
                    "retry loop — that advice is for the connectivity branch, and giving it here "
                    "is the defect being fixed",
                )


class ThePolicyBranchGivesARealRouteAndAContact(unittest.TestCase):
    def setUp(self):
        self.body = policy_branch()

    def test_it_names_the_private_deployment_with_attribution(self):
        self.assertRegex(self.body, r"(?i)private deployment")
        self.assertIn(
            "get_capabilities", self.body,
            "the route must be attributed to the surface that actually carries it — the manifest, "
            "not the get_sample_data schema description, which does not",
        )
        self.assertRegex(
            self.body, r"1\.32\.9.{0,40}2026-08-13|2026-08-13",
            "attribution must carry the server version and date (INV-080)",
        )

    def test_it_names_a_human_contact(self):
        self.assertIn("support@senzing.com", self.body)
        self.assertRegex(self.body, r"(?i)Senzing contact")

    def test_it_states_that_setup_is_undocumented_rather_than_inventing_steps(self):
        self.assertRegex(
            self.body, r"(?i)no documentation|does not currently cover",
            "the plugin must say the corpus does not document obtaining a private deployment",
        )
        self.assertRegex(
            self.body, r"(?i)never invented setup steps|not invented setup steps",
            "and must forbid inventing them — anything written would be from outside MCP",
        )
        self.assertRegex(
            self.body, r"index_built 2026-08-11|14,240",
            "the absence must be stamped with the corpus it was verified against, so it can be "
            "re-checked rather than trusted indefinitely",
        )

    def test_the_absence_carries_an_mcp_negative_marker_with_an_owner(self):
        """INV-209: a shipped negative names the route that owns the fact."""
        markers = [ln for ln in self.body.splitlines() if "MCP-NEGATIVE" in ln]
        self.assertGreaterEqual(len(markers), 1, "the absence claim must carry a marker")
        for marker in markers:
            with self.subTest(marker=marker[:70]):
                self.assertIn("owner:", marker, "every marker names the owning route (INV-209)")

    def test_it_does_not_offer_to_continue_without_the_server(self):
        self.assertRegex(
            self.body, r"(?i)never offer to continue without|no offline mode",
            "INV-080 is not negotiable; a bootcamp answering from training data is worse than one "
            "that does not start, and the branch must say so",
        )

    def test_no_wording_actually_offers_a_degraded_bootcamp(self):
        """Presence of the prohibition is not absence of the offer.

        Caught by negative control: inserting "We can continue in a limited mode." passed, because
        the prohibition's other phrasing ("no offline mode") still satisfied the alternation above.
        A branch whose purpose is honesty needs the forbidden-claim assertion as well as the
        required-text one.
        """
        for offer in (r"we can continue", r"limited mode", r"reduced mode", r"proceed without",
                      r"partial bootcamp", r"continue anyway"):
            with self.subTest(offer=offer):
                self.assertNotRegex(
                    self.body, r"(?i)" + offer,
                    "the policy branch must not offer a degraded bootcamp. There is no offline "
                    "mode: every Senzing fact comes from the server (INV-080), so continuing "
                    "means answering from training data.",
                )

    def test_no_wording_claims_the_setup_is_documented_or_easy(self):
        """The honest limit is 'named but undocumented'; overclaiming is the failure mode.

        Also caught by negative control: replacing the corpus finding with "Setup is
        straightforward once approved" passed, because "does not currently cover" survived
        elsewhere in the branch and satisfied the alternation.
        """
        for claim in (r"straightforward", r"easy to set up", r"setup is documented",
                      r"simply follow", r"here is how to obtain"):
            with self.subTest(claim=claim):
                self.assertNotRegex(
                    self.body, r"(?i)" + claim,
                    "the branch must not imply it knows how to obtain or configure a private "
                    "deployment. The corpus does not document it, so anything written would be "
                    "from outside MCP — exactly what INV-080 forbids.",
                )

    def test_it_does_not_claim_the_route_satisfies_any_policy(self):
        self.assertRegex(
            self.body, r"(?i)not present a private deployment as verified|their organisation's decision",
            "whether a configuration is permitted is the bootcamper's organisation's call, not a "
            "fact the plugin can assert",
        )

    def test_it_ends_on_exactly_one_question(self):
        """Counts question LINES, not glyph occurrences.

        A glyph count also counts the authoring sentence "end the turn on this single 👉 question",
        which is a reference to the marker rather than a question — so the naive count read 2 on
        correct text. A question is a line that *begins* with the pointer (optionally quoted).
        """
        questions = [ln for ln in self.body.splitlines()
                     if re.match(r"^\s*>?\s*" + POINTER, ln)]
        self.assertEqual(
            1, len(questions),
            "the branch yields to the bootcamper on exactly one 👉 question (INV-005); found "
            f"{len(questions)}: {[q.strip()[:70] for q in questions]}",
        )

    def test_the_downloads_route_is_not_oversold(self):
        """/downloads/ solves package egress, not MCP access — conflating them misleads."""
        self.assertRegex(
            self.body, r"(?i)does not (?:clear this blocker|solve this blocker)|not MCP access",
            "the /downloads/ note must be qualified: it addresses package download, not MCP "
            "access, so it does not clear a policy blocker on its own",
        )


class StdioModeIsNoLongerCitable(unittest.TestCase):
    def test_stdio_mode_is_not_offered_as_a_route(self):
        body = policy_branch()
        offered = re.search(r"(?i)(?:use|run|try|ask about)[^.\n]{0,60}stdio", body)
        self.assertIsNone(
            offered,
            "stdio mode / sz-mcp-coworker was named at server 1.32.3 and is named nowhere at "
            "1.32.9 — not in sdk_guide's description, not in the get_capabilities manifest. It "
            f"must not be offered as an available route (INV-080). Found: {offered!r}",
        )

    def test_the_withdrawal_is_recorded_rather_than_silently_dropped(self):
        body = policy_branch()
        self.assertRegex(
            body, r"1\.32\.3",
            "the withdrawal must be recorded with the version that did name it, so a later reader "
            "can tell 'checked and gone' from 'never considered'",
        )
        self.assertRegex(
            body, r"(?i)sz-mcp-coworker",
            "name the binary in the withdrawal note so a re-check knows what to look for",
        )


class GroundRulesStopsAssumingTheCauseIsTheConnection(unittest.TestCase):
    def test_the_mcp_failure_clause_names_both_causes(self):
        text = GROUND_RULES.read_text(encoding="utf-8")
        start = text.index("- **MCP failure:**")
        clause = text[start:start + 1400]
        self.assertRegex(
            clause, r"(?i)do not assume the cause is the connection",
            "the MCP-first clause must stop treating 'unreachable' as necessarily a connection "
            "problem",
        )
        self.assertRegex(clause, r"(?i)polic", "and must name the policy cause")
        self.assertIn("0c", clause, "and must route to the branch that handles it")

    def test_it_applies_beyond_onboarding(self):
        text = GROUND_RULES.read_text(encoding="utf-8")
        clause = text[text.index("- **MCP failure:**"):][:1400]
        self.assertRegex(
            clause, r"(?i)any point in the bootcamp|not only at onboarding",
            "a server reachable at session start can stop being reachable mid-module, so the "
            "branch must not be scoped to onboarding",
        )


if __name__ == "__main__":
    unittest.main()
