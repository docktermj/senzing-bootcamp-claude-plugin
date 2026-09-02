"""The license record limit must be measured with an engine configuration in force.

``SzProduct.get_license()`` resolves the license from the settings it is handed.
SDK setup's Step 5a runs three steps before Step 8 writes ``CONFIGPATH``, so a
reading taken there cannot reach a license installed at the system config path --
the third of the four tiers in Step 5's own documented check order. On a machine
carrying such a license the early reading returns the built-in default and says
nothing about having missed anything.

That matters because ``license_record_limit`` is the one field the license
apparatus treats as authoritative *because* it was measured. A measured-but-
incomplete value is worse than an absent one: absence triggers Module 4's
re-measure branch, presence suppresses it, and the Bootcamper is then steered
toward sampling against a ceiling that may not exist.

Measured on Senzing SDK 4.4.0 (build 4.4.0.26242), 2026-09-01, on a machine with a
license at /etc/opt/senzing: ``{"PIPELINE": {}}`` returns ``recordLimit: 500``;
the same call with ``CONFIGPATH`` in force returns ``recordLimit: 0`` (no cap).
Which tier wins for a given settings string is engine behavior no MCP route
reports, so it is recorded as observation-only (INV-080/INV-149).

⛔ The site set here is DERIVED BY SCANNING, never hardcoded (INV-246). A guard
that names the files the author already thought of certifies exactly those and is
blind to the one that matters.

Enforces **INV-295** — a measurement whose result can change once later configuration
exists records WHEN it was taken, and a step branching on it treats a pre-configuration
reading as provisional rather than authoritative.

⚠️ Scoped deliberately: ``platform`` and ``database_type`` are also environment
measurements and need no marker, because neither can move once a later step writes
configuration. Asserting a timestamp on them would teach that the marker means nothing.

⚠️ What this establishes is that the six rules SHIP across four modules. Whether a live
walk actually re-measures at Step 8a is a claim about a turn, and ``dry-run`` phase 3's.

Stdlib only, and nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "plugins" / "senzing-bootcamp" / "skills"

FIELD = "license_record_limit"
MARKER = "license_record_limit_measured_at"

#: A line that *instructs a write* of the field, as opposed to merely discussing it.
#: Both spellings the corpus uses appear: "Write the measured value into ... as
#: `license_record_limit`" and "Persist it as `license_record_limit`".
#:
#: ⚠️ "record" is deliberately NOT in this alternation. It is a noun far more often
#: than a verb in this corpus -- Module 1's "compute the total *record count* across
#: the mentioned sources and read `license_record_limit`" matched it and produced a
#: false positive against a file whose whole point is that it must NEVER write the
#: field. The same noun/verb split `conformance.py` draws for its stop-sign scan.
WRITES = re.compile(
    r"(?:write|writes|writing|written|persist|persists|persisted)\b[^.\n]{0,160}`" + FIELD + "`",
    re.IGNORECASE,
)


def markdown_files():
    return sorted(p for p in SKILLS.rglob("*.md"))


def sections(text):
    """Split a skill file into (heading, body) pairs on ATX headings."""
    parts = re.split(r"^(#{2,4} .+)$", text, flags=re.M)
    out, i = [], 1
    while i < len(parts) - 1:
        out.append((parts[i].strip(), parts[i + 1]))
        i += 2
    return out


class TheReadingIsMarkedProvisionalUntilTheConfigExists(unittest.TestCase):
    def setUp(self):
        self.sdk_setup = SKILLS / "module-02-sdk-setup" / "SKILL.md"
        self.text = self.sdk_setup.read_text(encoding="utf-8")

    def _prose_of_5a(self):
        """Section 5a with inline-code spans removed.

        ⛔ The marker VALUE this step writes is the string
        ``"module-02 step 5a (provisional -- ...)"``, and it sits in a backticked span
        inside this very section. Asserting on the raw text therefore passes on the
        marker alone, even with the caveat deleted -- which is what the first version
        of this test did, and the M1 mutation proved it. Strip code spans so the
        assertion is about the PROSE that makes the claim.
        """
        body = next(b for h, b in sections(self.text) if h.startswith("### 5a."))
        return re.sub(r"`[^`]*`", "", body)

    def test_step_5a_names_its_reading_provisional(self):
        """The early reading must say it is provisional, not merely be corrected later."""
        self.assertRegex(
            self._prose_of_5a(), r"(?i)provisional",
            "SDK setup Step 5a takes the license reading before Step 8 writes CONFIGPATH, so it "
            "cannot see a license at the system config path. The step's PROSE must say the reading "
            "is provisional; otherwise a downstream reader treats it as complete. (The marker value "
            "this step writes also contains the word, so it is excluded from this assertion.)",
        )

    def test_step_5a_says_a_later_step_re_takes_the_reading(self):
        """'Provisional' with no successor names a problem and no remedy."""
        self.assertRegex(
            self._prose_of_5a(), r"(?i)(re-?take|re-?measure)",
            "Step 5a must say that a later step re-takes the reading. Calling it provisional "
            "without naming the successor tells the reader the figure is untrustworthy and gives "
            "them nowhere to go.",
        )

    def test_step_5a_names_configpath_as_the_reason(self):
        """A bare 'provisional' is unactionable -- the reason is what makes it checkable."""
        body = next(b for h, b in sections(self.text) if h.startswith("### 5a."))
        self.assertIn(
            "CONFIGPATH", body,
            "Step 5a must name CONFIGPATH as what the reading cannot yet see. Without the reason, "
            "a later editor cannot tell whether the caveat still applies.",
        )

    def test_a_re_measure_step_exists_AFTER_the_engine_configuration_is_written(self):
        """Position is the whole fix: re-measuring before Step 8 would change nothing."""
        step8 = self.text.find("## Step 8: Create Engine Configuration")
        self.assertNotEqual(step8, -1, "Step 8 heading not found -- has the module been renamed?")
        remeasure = re.search(r"(?im)^#{2,4} .*re-?measure.*$", self.text)
        self.assertIsNotNone(
            remeasure,
            "No re-measure step found in SDK setup. Step 5a's reading is provisional, so something "
            "after Step 8 must take the authoritative one.",
        )
        self.assertGreater(
            remeasure.start(), step8,
            "The re-measure step is positioned BEFORE Step 8 writes the engine configuration, so it "
            "reads the same incomplete settings Step 5a did and corrects nothing.",
        )

    def test_the_re_measure_step_says_a_withdrawn_figure_is_named_aloud(self):
        """Replacing the number silently leaves anything sized against it unexamined.

        Step 5a's sub-step 3 already requires naming both numbers on a disagreement;
        before the re-measure existed nothing in this module wrote the field twice, so
        that rule described a situation that could not arise. The re-measure is what
        makes it reachable, so it must carry the obligation too.
        """
        remeasure = re.search(r"(?im)^#{2,4} .*re-?measure.*$", self.text)
        body = self.text[remeasure.start():]
        body = body[: body.find("\n## ") if "\n## " in body else len(body)]
        self.assertRegex(
            body, r"(?i)withdraw",
            "The re-measure step must say the superseded figure is withdrawn and both numbers "
            "stated. A silent replacement leaves a sampling plan or generated scenario sized "
            "against a ceiling that has just been shown not to exist.",
        )


class EveryWriteSiteRecordsWhenTheReadingWasTaken(unittest.TestCase):
    """Derived by scanning: any file that writes the field must also write the marker."""

    def test_every_file_that_writes_the_field_also_writes_the_marker(self):
        offenders = []
        for path in markdown_files():
            text = path.read_text(encoding="utf-8")
            if WRITES.search(text) and MARKER not in text:
                offenders.append(str(path.relative_to(REPO)))
        self.assertEqual(
            [], offenders,
            "These files instruct writing `%s` without ever naming `%s`. Both readings are genuine "
            "measurements, so the figure alone cannot distinguish a complete one from a "
            "pre-configuration one -- the marker is what lets a later step tell them apart: %s"
            % (FIELD, MARKER, offenders),
        )

    def test_at_least_two_files_write_the_field(self):
        """Guards the guard: if the scan matches nothing, the test above passes vacuously."""
        writers = [p for p in markdown_files() if WRITES.search(p.read_text(encoding="utf-8"))]
        self.assertGreaterEqual(
            len(writers), 2,
            "Expected at least the SDK-setup and Data-collection write sites; the scan found %d. "
            "A pattern that matches nothing makes the sibling assertion vacuous." % len(writers),
        )


class TheDownstreamGateDoesNotTrustAProvisionalReading(unittest.TestCase):
    def test_every_file_that_branches_on_the_field_consults_the_marker(self):
        """A consumer that decides capacity must know whether the reading was complete.

        Scanned, not listed. A file only *mentions* the field (cross-references, prose
        about the invariant) without deciding on it; the discriminator is whether it
        instructs reading the value to drive a decision.
        """
        reads = re.compile(r"(?i)read\b[^.\n]{0,120}`" + FIELD + "`")
        offenders = []
        for path in markdown_files():
            text = path.read_text(encoding="utf-8")
            if not reads.search(text):
                continue
            # Module 1 runs before SDK setup, so no measurement can exist yet there;
            # its own text says the field is "normally absent at this point".
            if "normally absent at this point" in text:
                continue
            if MARKER not in text:
                offenders.append(str(path.relative_to(REPO)))
        self.assertEqual(
            [], offenders,
            "These files read `%s` to drive a decision without consulting `%s`. A present figure is "
            "authoritative only if it was taken with an engine configuration in force: %s"
            % (FIELD, MARKER, offenders),
        )


if __name__ == "__main__":
    unittest.main()
