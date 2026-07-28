"""A freshly schema-created datastore has no config, and the plugin must say so.

`sdk_guide(topic='configure')`'s primary RegisterDataSources snippet reads the default
config id and builds a config **from** it, so on a datastore created with
`szcore-schema-sqlite-create.sql` — which the same tool's notes tell you to create — it
fails with SENZ7221 EAS_ERR_NO_CONFIG_REGISTERED_FOR_DATA_ID. Verified still reproducing
on MCP server 1.32.1, 2026-07-28.

Two things make it expensive rather than merely annoying:

* `explain_error_code('SENZ7221')` returns resolution steps about paths, connection
  strings and initialization — **none of which is the remedy** — so the code leads a
  reader away from the cause.
* `init_default_config`, which does seed a config
  (`create_config_from_template()` -> `set_default_config(...)`), is returned only as an
  unannotated entry in the response's `alternatives`, reading as a variation rather than
  a precondition.

None of `SENZ7221`, `init_default_config`, `set_default_config` or `get_default_config_id`
appeared anywhere in the skills tree before this, so a bootcamper met the error with no
guidance at all.

These tests pin the guidance, including the one thing implementation disproved: the
seeding code does NOT come from `generate_scaffold(workflow='initialize')`, whose
snippets cover factory/environment lifecycle only.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
MODULE_02 = PLUGIN / "skills" / "module-02-sdk-setup" / "SKILL.md"
PHASE3 = PLUGIN / "skills" / "module-05-data-quality-mapping" / "phase3-test-load.md"


def flat(path):
    """Whitespace-collapsed text with blockquote markers stripped."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class ThePreconditionIsStated(unittest.TestCase):
    def test_module_02_has_a_seeding_step(self):
        self.assertRegex(MODULE_02.read_text(encoding="utf-8"), r"(?m)^## Step 8a:")

    def test_it_says_a_fresh_datastore_has_no_configuration(self):
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)(?:freshly|just).{0,40}(?:schema-)?created datastore (?:has|whose)",
        )

    def test_it_is_placed_before_the_connection_test(self):
        """Seeding after Step 9 would be too late to help."""
        text = MODULE_02.read_text(encoding="utf-8")
        self.assertLess(text.index("## Step 8a:"), text.index("## Step 9:"))

    def test_the_sandbox_phase_carries_it_too(self):
        """Phase 3 creates its own datastore, so it has the same precondition."""
        text = flat(PHASE3)
        self.assertIn("SENZ7221", text)
        self.assertIn("init_default_config", text)


class TheErrorCodeIsRouted(unittest.TestCase):
    def test_senz7221_is_named_with_its_cause(self):
        text = flat(MODULE_02)
        self.assertIn("SENZ7221", text)
        self.assertRegex(text, r"(?i)SENZ7221[^.]{0,200}no default configuration|seed one per Step 8a")

    def test_it_appears_in_troubleshooting(self):
        text = MODULE_02.read_text(encoding="utf-8")
        trouble = text[text.index("## Troubleshooting"):]
        self.assertIn("SENZ7221", trouble)

    def test_explain_error_code_is_still_called_first(self):
        """INV-080: the MCP tool stays the first stop even when we know the cause."""
        self.assertRegex(flat(MODULE_02), r"explain_error_code\('SENZ7221'\)")

    def test_the_guidance_warns_the_error_codes_own_steps_mislead(self):
        """Its resolution steps name paths/connection/initialization, not seeding."""
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)do \*\*not\*\* name this cause|does not name the (?:actual )?(?:cause|fix)"
            r"|none of which is the actual fix",
        )


class TheSeedingCodeComesFromMcp(unittest.TestCase):
    """INV-080: the plugin says when and why; the server supplies the code."""

    def test_init_default_config_is_named_as_the_route(self):
        self.assertIn("init_default_config", flat(MODULE_02))

    def test_it_points_at_the_configure_response_alternatives(self):
        self.assertRegex(flat(MODULE_02), r"(?i)`?alternatives`?")

    def test_the_wrong_route_is_explicitly_ruled_out(self):
        """Implementation disproved the spec here: initialize does not seed."""
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)generate_scaffold\(workflow='initialize'\)\W{0,4}does not do this"
            r"|initialize.{0,80}does not seed",
        )

    def test_no_seeding_code_is_hand_written_in_the_plugin(self):
        """Naming a method in prose is fine; shipping a code block is not."""
        text = MODULE_02.read_text(encoding="utf-8")
        step = text[text.index("## Step 8a:"):text.index("## Step 9:")]
        fences = re.findall(r"```(\w*)\n(.*?)```", step, re.S)
        for lang, body in fences:
            with self.subTest(lang=lang):
                self.assertNotIn(
                    "set_default_config(", body,
                    "the seeding call must come from MCP, not a copied code block",
                )
                self.assertNotIn("create_config_from_template(", body)

    def test_the_seeding_sequence_is_described_with_its_provenance(self):
        """A Senzing fact in shipped text carries how and when it was established."""
        text = flat(MODULE_02)
        self.assertIn("create_config_from_template()", text)
        self.assertIn("set_default_config", text)
        self.assertRegex(text, r"(?i)verified on server 1\.32\.1")


class TheSeedIsVerifiedNotAssumed(unittest.TestCase):
    def test_a_verification_step_follows_the_seed(self):
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)confirm a default config id is now present|[Vv]erify the seed",
        )

    def test_failure_is_reported_at_this_step(self):
        self.assertRegex(
            flat(MODULE_02),
            r"(?i)stop here and report|surfaces at this step",
            "an unseeded datastore must fail where it is diagnosable",
        )


if __name__ == "__main__":
    unittest.main()
