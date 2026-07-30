"""Every MCP call the plugin documents must match the tool's real contract.

Three prose audits and 399 tests all passed while **Module 5's mapping workflow could not
execute at all**. It took a dry run against the live Senzing MCP server to see it, because
the defect is invisible to any check that only reads the plugin: the instructions are
coherent, well-written, internally consistent, and wrong about the tool they call.

What the 2026-07-26 dry run found:

* `mapping_workflow(action='start')` requires BOTH `file_paths` and `data.workspace_dir`
  — the tool's own words are "The call WILL FAIL without both", and "do NOT assume /tmp
  exists". `workspace_dir` appeared **nowhere** in the plugin, so Module 5 failed on its
  first call. `analyze_record` requires it too, and also never passed it.
* Five of the eight `mapping_workflow` action names were payload FIELD names written as
  actions — `profile_summary`, `entity_plan`, `schema_mappings`, `paths`, `verdict`. The
  only valid actions are start/advance/back/status/reset. One of the five sat on workflow
  step 3, and the plugin had filed a step-3 rejection upstream as an MCP-server defect.
* `get_sdk_reference`'s `methods` topic — which answers parameter shapes — was missing
  from the tool-routing table, and INV-132 asserted the reference could not answer them
  at all, routing the guide away from MCP toward local introspection.

These assertions are **static**: they encode the contract as observed on 2026-07-26 rather
than calling the server, so the suite stays offline, stdlib-only, and fast (INV-108). That
is a deliberate trade — a static copy can go stale, which is why CONTRACT_VERIFIED_ON is
recorded and why the assertions are about *shape* (required params present, action names in
the enum) rather than about response content. Re-run a dry run to refresh it; a tool that
gains a required parameter will not be caught here until someone does.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"

# When the contract below was last checked against https://mcp.senzing.com/mcp.
CONTRACT_VERIFIED_ON = "2026-07-26"

# mapping_workflow's action enum, verbatim from the tool schema.
VALID_WORKFLOW_ACTIONS = {"start", "advance", "back", "status", "reset"}

# Tools whose schema marks a parameter REQUIRED, and where the plugin must show it.
REQUIRED_PARAMS = {
    "mapping_workflow": ("file_paths", "workspace_dir"),
    "analyze_record": ("workspace_dir",),
}

# workspace_dir must stay inside the project (the file-placement rule as a parameter).
FORBIDDEN_WORKSPACE_DIRS = ("/tmp", "%TEMP%", "~/", "/var/tmp")

SKILLS = PLUGIN / "skills"


def skill_text():
    """Every shipped skill/command file, as (path, text)."""
    for root in (SKILLS, PLUGIN / "commands"):
        for path in sorted(root.rglob("*.md")):
            if "pytest_cache" in path.parts:
                continue
            yield path, path.read_text(encoding="utf-8", errors="replace")


def files_calling(tool):
    """Files that actually invoke the named tool (not just mention it in prose)."""
    pattern = re.compile(rf"`?{re.escape(tool)}\(")
    for path, text in skill_text():
        if pattern.search(text):
            yield path, text


class TestActionNamesAreInTheEnum(unittest.TestCase):
    """A payload field name used as an action is rejected by the server."""

    def test_no_invented_workflow_actions(self):
        offenders = []
        for path, text in skill_text():
            for n, line in enumerate(text.splitlines(), 1):
                for action in re.findall(r"action='([a-z_]+)'", line):
                    if action not in VALID_WORKFLOW_ACTIONS:
                        offenders.append(
                            f"{path.relative_to(REPO_ROOT)}:{n} uses action='{action}', "
                            f"which is not in the enum {sorted(VALID_WORKFLOW_ACTIONS)} — "
                            "it is a payload field name; advance with action='advance' "
                            "and put the field in data/payload"
                        )
        self.assertEqual(
            [],
            offenders,
            "invalid mapping_workflow action(s) — the server rejects these:\n  "
            + "\n  ".join(offenders),
        )

    def test_the_advance_action_is_actually_used(self):
        """If nothing advances, the workflow instructions describe a dead end."""
        joined = "".join(text for _, text in skill_text())
        self.assertIn("action='advance'", joined)


class TestRequiredParamsArePresent(unittest.TestCase):
    """A required parameter the plugin never names is a call that fails outright."""

    def test_every_tool_shows_its_required_params(self):
        missing = []
        for tool, params in REQUIRED_PARAMS.items():
            callers = list(files_calling(tool))
            self.assertTrue(
                callers, f"no file appears to call {tool}; has it been renamed?"
            )
            for param in params:
                if not any(param in text for _, text in callers):
                    where = ", ".join(
                        str(p.relative_to(REPO_ROOT)) for p, _ in callers
                    )
                    missing.append(
                        f"{tool} requires `{param}`, which appears in none of its "
                        f"calling files ({where}) — the call fails without it"
                    )
        self.assertEqual(
            [],
            missing,
            "required MCP parameter(s) absent from the instructions:\n  "
            + "\n  ".join(missing),
        )

    def test_workspace_dir_is_project_local(self):
        """The parameter exists to keep tool output inside the project."""
        offenders = []
        for path, text in skill_text():
            for n, line in enumerate(text.splitlines(), 1):
                if "workspace_dir" not in line:
                    continue
                for bad in FORBIDDEN_WORKSPACE_DIRS:
                    # An explicit "never /tmp" instruction is the opposite of a defect.
                    if bad in line and not re.search(
                        r"never|not|do NOT|forbid|outside", line, re.IGNORECASE
                    ):
                        offenders.append(
                            f"{path.relative_to(REPO_ROOT)}:{n} points workspace_dir at "
                            f"{bad}: {line.strip()[:90]}"
                        )
        self.assertEqual([], offenders, "\n  ".join(offenders))


class TestParameterShapeRoutingGoesToMcp(unittest.TestCase):
    """INV-080 forbids routing away from MCP; INV-132 briefly did exactly that."""

    def test_ground_rules_routes_parameter_shapes_to_the_methods_topic(self):
        text = (SKILLS / "bootcamp-onboarding" / "ground-rules.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "topic='methods'",
            text,
            "the tool-routing table omits get_sdk_reference's `methods` topic — the one "
            "that answers parameter shapes. Without it the guide is sent to local "
            "binding introspection, which needs a working installed SDK and contradicts "
            "the MCP-first invariant (INV-080).",
        )

    def test_invariants_no_longer_claim_mcp_cannot_reach_parameter_shapes(self):
        text = (REPO_ROOT / "specs" / "INVARIANTS.md").read_text(encoding="utf-8")
        self.assertIn(
            "The reference reaches parameter shapes under **any** topic",
            text,
            "INV-132's correction has been reverted; it would again assert that the MCP "
            "reference cannot answer parameter shapes, which the live server disproves.",
        )
        self.assertNotIn(
            "document neither the argument types nor what a flag family selects",
            text.split("(Corrected in place 2026-07-30")[0],
            "INV-132 again asserts that `flags` and `response_schemas` document neither "
            "argument types nor flag-family membership. Both are false: filtered by a "
            "method, every topic returns a `method_signatures` block, and flag entries "
            "carry composite_members/depends_on/response_paths (server 1.32.2, "
            "2026-07-30). The phrase is allowed only inside the correction note that "
            "quotes what the invariant used to say.",
        )


class TestLicenseRequestIsConsentGated(unittest.TestCase):
    """INV-135: the one call that sends personal data needs an explicit yes."""

    LICENSE_STEP = PLUGIN / "skills" / "module-04-data-collection" / "SKILL.md"

    def test_the_license_request_carries_a_pinned_consent_question(self):
        text = self.LICENSE_STEP.read_text(encoding="utf-8")
        self.assertIn("license_request", text, "the license-request path has moved")
        window_start = text.find("license_request")
        window = text[window_start : window_start + 4000]
        self.assertRegex(
            window,
            r"👉 \*\*Send this evaluation-license request",
            "the license_request call has no pinned consent question near it. This call "
            "transmits the Bootcamper's name and work email off their machine (INV-135); "
            "it must never run without an explicit yes.",
        )

    def test_the_defect_report_path_scopes_its_stripping_rule(self):
        """Otherwise INV-065's 'strip the email' and this call contradict each other."""
        text = (SKILLS / "bootcamp-onboarding" / "feedback.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "license_request",
            text,
            "feedback.md's strip-everything-identifying rule does not say it governs "
            "only the defect categories, so it reads as forbidding the license request's "
            "required email — a rule the plugin both requires and forbids.",
        )


class TestContractProvenance(unittest.TestCase):

    def test_the_verification_date_is_recorded(self):
        """A static copy of a live contract is only trustworthy with a date on it."""
        self.assertRegex(CONTRACT_VERIFIED_ON, r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
