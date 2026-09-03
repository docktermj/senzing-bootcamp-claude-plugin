"""Module 5 warns that the routing report miscounts payload fields as dropped.

``sz_routing_report.py`` is MCP-delivered (``mapping_workflow`` step 1). It exempts payload
fields from its DROPPED list -- ``exempt_fields = NEVER_FROM_SOURCE | set(payload_fields)`` --
but ``discover_payload_fields()`` fills that set only from a ``--payload-fields`` override or
a ``phase1_manifest.json`` beside the output. Step 4's own command passes no override, and no
``phase1_manifest.json`` is among the seven resources the workflow delivers or writes. The set
is therefore always empty and the exemption never engages.

Re-read from the delivered script on server **1.35.3, 2026-09-01** (6,855 bytes): the
``return []`` at the end of ``discover_payload_fields()`` is still what runs.

Measured 2026-08-31 on the 1,554-record ``las-vegas / US-LABOR-VIOLATIONS`` CORD source
(61 fields; 6 feature, 6 payload, 49 ignore): **14,480** dropped entries as instructed against
**5,620** with the payload fields supplied by hand -- 8,860 spurious, 61% of the report. The
report prints those same fields under "Payload root keys" a few lines above the dropped list.

⚠️ Why the relay matters rather than being a footnote: step 4 says to reconsider every dropped
entry AND not to route dropped values into payload. With payload listed as dropped those
conflict, and the cheap resolution is to promote payload into features -- the dumping-ground
anti-pattern the workflow's own reference warns against, reached by believing a broken
measurement.

⚠️ ``mcp-server`` finding. The upstream report was sent 2026-08-31 with the maintainer's
approval; this repo ships the relay only.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PHASE_2 = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
           "module-05-data-quality-mapping" / "phase2-data-mapping.md")


def flat(s):
    return re.sub(r"\s+", " ", s)


def limitation_4():
    """The fourth known-limitation entry, from its heading to the shared handling line."""
    text = PHASE_2.read_text(encoding="utf-8")
    start = text.find('4. **The routing report counts every PAYLOAD field as "dropped"')
    assert start != -1, "limitation 4 was not found -- renumbered or reworded?"
    end = text.find("**Handling is the same for all", start)
    assert end != -1, "the shared handling line was not found after limitation 4"
    return text[start:end]


class TheLimitationIsRelayed(unittest.TestCase):
    def setUp(self):
        self.entry = flat(limitation_4())

    def test_it_names_the_miscount(self):
        self.assertRegex(
            self.entry, r'(?i)every PAYLOAD field as "dropped"',
            "The entry must say payload fields are counted as dropped. That is the observable "
            "the guide meets, and the one that makes the step's two instructions conflict.",
        )

    def test_it_explains_why_the_exemption_never_engages(self):
        """⚠️ Asserts the MECHANISM. Without it the note reads as folklore about a flaky tool."""
        self.assertRegex(
            self.entry, r"discover_payload_fields",
            "The entry must name the function whose empty return causes this, so a reader can "
            "check the claim against the delivered script rather than taking it on trust.",
        )
        self.assertRegex(
            self.entry, r"(?i)phase1_manifest\.json",
            "The entry must name the manifest the exemption's second route needs and that the "
            "workflow never writes -- otherwise 'the exemption never engages' is an assertion "
            "with nothing behind it.",
        )
        self.assertRegex(
            self.entry, r"--payload-fields",
            "The entry must name the override, which is both the cause (not passed) and the "
            "remedy (pass it by hand).",
        )

    def test_it_gives_the_remedy(self):
        self.assertRegex(
            self.entry, r'(?i)re-run with `--payload-fields|struck out',
            "The entry must tell the guide how to get a true list -- re-run with the override, "
            "or read the report with the payload fields struck out. Naming a broken measurement "
            "without a way past it stalls the step.",
        )

    def test_it_forbids_the_tempting_wrong_fix(self):
        self.assertRegex(
            self.entry, r"(?i)never promote a payload field into a feature",
            "The entry must forbid promoting payload into features to quiet the report. That "
            "is the dumping-ground anti-pattern, and it is the path of least resistance for a "
            "guide trying to satisfy both of step 4's instructions.",
        )

    def test_it_says_the_mapping_is_not_at_fault(self):
        self.assertRegex(
            self.entry, r"(?i)reporting defect, not a mapping one",
            "The entry must say this is a reporting defect. A guide that reads it as evidence "
            "against its own dispositions will change a correct mapping.",
        )


class TheClaimCarriesItsProvenance(unittest.TestCase):
    def setUp(self):
        self.entry = flat(limitation_4())

    def test_the_measured_figures_are_present(self):
        for figure in ("14,480", "5,620", "8,860"):
            with self.subTest(figure=figure):
                self.assertIn(
                    figure, self.entry,
                    "The measured figures must be shown. 'Some entries are spurious' does not "
                    "let a reader recognize the situation; 61% of the report does.",
                )

    def test_it_carries_a_server_version_and_date(self):
        self.assertRegex(self.entry, r"1\.35\.\d",
                         "The claim must name the MCP server version it was verified against.")
        self.assertRegex(self.entry, r"20\d\d-\d\d-\d\d",
                         "The claim must carry its date (INV-080).")

    def test_it_is_framed_as_upstream_not_plugin_behavior(self):
        """The spec's third criterion -- the Bootcamper must know whose defect this is."""
        self.assertRegex(
            self.entry, r"(?i)the script the server delivers|MCP-delivered|server delivers today",
            "The entry must make clear the script is server-delivered, so the defect reads as "
            "upstream rather than as something this bootcamp did.",
        )


class TheLimitationListStaysConsistent(unittest.TestCase):
    """Adding a fourth entry to a list that counts itself in prose."""

    def setUp(self):
        self.text = PHASE_2.read_text(encoding="utf-8")

    def test_the_prose_count_matches_the_entry_count(self):
        """⚠️ The list states its own length three times; a stale count is a wrong claim."""
        self.assertNotRegex(
            flat(self.text), r"(?i)\*\*Three further limitations",
            "The intro still says 'Three further limitations' after a fourth was added. A list "
            "that counts itself has to be recounted when it grows.",
        )
        for phrase in ("Four further limitations", "all four are CURRENT behavior",
                       "Handling is the same for all four"):
            with self.subTest(phrase=phrase):
                self.assertIn(
                    phrase, self.text,
                    "The list's self-references must all say four. A reader who counts four "
                    "entries under a heading that says three does not know which is stale.",
                )

    def test_the_new_entry_has_a_freshness_line_like_its_siblings(self):
        self.assertRegex(
            flat(self.text),
            r"Limitation \*\*4\*\* was re-confirmed on \*\*MCP server 1\.35\.\d, 20\d\d-\d\d-\d\d\*\*",
            "Every limitation carries a per-limitation freshness line saying when its mechanism "
            "was last re-checked. The fourth needs one too, or it is the only entry a reader "
            "cannot date.",
        )


if __name__ == "__main__":
    unittest.main()
