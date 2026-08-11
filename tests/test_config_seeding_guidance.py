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

    def test_the_guidance_sends_the_reader_to_follow_the_error_codes_own_steps(self):
        """The 2026-07-30 correction, and the sharpest instance of its class.

        This test previously asserted the opposite — that the guidance *warns* the error
        code's own resolution steps mislead ("do **not** name this cause", "none of which
        is the actual fix"). True on server 1.32.1. On 1.32.2 `explain_error_code('SENZ7221')`
        returns the never-seeded datastore as its **first** cause and the seeding sequence
        as its **first** resolution step — the plugin's own diagnosis and remedy. So the
        old text told the guide to discount three accurate, ordered steps, inverting the
        INV-080 routing it was written to serve, and this test made that load-bearing.
        """
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)names its own remedy|follow what it returns")
        for stale in ("none of which is the actual fix", "pulled toward re-checking"):
            with self.subTest(phrase=stale):
                self.assertNotIn(stale, text)

    def test_the_correction_is_scoped_to_senz7221_only(self):
        """SENZ2027 was re-checked the same day and is still a stub returning a
        placeholder cause, so its compensating guidance is correct and must survive.
        Richness varies per code; a blanket 'trust explain_error_code' would be wrong."""
        text = flat(MODULE_02)
        self.assertRegex(
            text, r"(?i)SENZ2027.{0,300}?The actionable detail is in the Senzing FAQ",
            "the SENZ2027 compensating text was lost — that code is still a stub "
            "(verified 2026-07-30: placeholder cause, three generic resolution steps), "
            "so the plugin must keep supplying the FAQ detail the tool omits",
        )


class TheSeedingCodeComesFromMcp(unittest.TestCase):
    """INV-080: the plugin says when and why; the server supplies the code."""

    def test_init_default_config_is_named_as_the_route(self):
        self.assertIn("init_default_config", flat(MODULE_02))

    def test_it_explains_which_call_puts_the_snippet_where(self):
        """Repointed 2026-08-11 (INV-181): `alternatives` alone is not the requirement.

        `sdk_guide(topic='configure')` called WITHOUT `data_sources` returns
        `init_default_config` as the PRIMARY snippet and `register_data_sources` in
        `alternatives`; called WITH `data_sources` the two swap. The module must state that
        discriminator, because a step that just says "take the alternative" is right for one
        call and wrong for the other."""
        text = flat(MODULE_02).replace("*", "")   # emphasis must not decide the match
        self.assertRegex(text, r"(?i)without\s+`?data_sources`?")
        self.assertRegex(text, r"(?i)\bwith\s+`?data_sources`?")
        self.assertRegex(text, r"(?i)`?alternatives`?")

    def test_the_snippet_is_located_by_source_path_not_by_position(self):
        """Repointed 2026-08-11 (`sdk-guide-configure-now-leads-with-seeding`, INV-181).

        This asserted that the module rules `generate_scaffold(workflow='initialize')` out as
        a seeding route — "does not do this". On server 1.32.8 that workflow DOES return the
        `configuration/` snippets, so the assertion pinned a claim the server had falsified.

        What the module actually promises, and what is worth pinning, is the discipline the
        stale claim was a symptom of: `sdk_guide(topic='configure')` returns ONE primary
        snippet and puts the other in `alternatives`, selected by whether `data_sources` was
        passed — so a step must find the snippet by its `source_path`, never by its position
        in the response. Pinning position is what went stale; pinning the rule cannot."""
        text = flat(MODULE_02)
        self.assertRegex(text, r"(?i)source_path.{0,120}never by its position"
                               r"|never by its position in the response")
        self.assertIn("configuration/init_default_config.py", text)

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
        self.assertRegex(
            text, r"(?i)verified on MCP server 1\.\d+\.\d+, \d{4}-\d{2}-\d{2}"
                  r"|verified on server 1\.\d+\.\d+",
            "the sequence must carry a server version and date, whichever version is current "
            "(repointed 2026-08-11: pinning 1.32.2 exactly made a correct re-verification fail)",
        )


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
