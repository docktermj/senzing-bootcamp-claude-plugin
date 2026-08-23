"""The profile report has two possible filenames, and the relocation contract covers both.

`module-05-data-quality-mapping/phase2-data-mapping.md` warned of a profiler limitation that no
longer exists, and prescribed a workaround that had become the server's own behavior:

  > **For a multi-file source, the emitted commands write to the same output path.** [...]
  > **Profile each input to its own path** (`profile_report_<stem>.md`) and concatenate [...]

Re-verified on server **1.33.0, 2026-08-23** by calling `mapping_workflow(action='start')` twice
and reading the emitted `commands` both times:

  * one `file_paths` entry  -> `-o <workspace_dir>/profile_report.md`
  * two `file_paths` entries -> `-o <workspace_dir>/profile_report_crm.md`
                               `-o <workspace_dir>/profile_report_orders.md`

⛔ **So the collision is fixed AND the prescribed workaround now REINTRODUCES it.** The server
already writes one report per input; a guide following the instruction to "concatenate" them into
a single `profile_report.md` recreates the single-schema file whose silent wrongness the entry
existed to prevent.

**The second cost reached INV-177.** That invariant's rule is stated in the general -- *every*
such artifact, *every* fixed filename the workspace receives -- but its illustrative premise names
three literal filenames, and `profile_report_<stem>.md` is not among them. A reader matching the
literal `profile_report.md` relocates that and leaves `profile_report_crm.md` behind in the
**shared** `data/mapping` workspace, un-relocated and un-source-qualified, where the next source's
run overwrites it: exactly the overwrite INV-177 prevents, arriving through a filename its text
did not cover. INV-177 now carries a dated premise correction; the rule is unchanged.

⛔ **This checks the plugin's guidance, not the server's behavior.** The suite is offline
(INV-108), so the dated stamps are what a later run re-asks. Per
`specs/guards-pinning-a-dated-negative-outlive-it.md` the provenance assertions check that a
well-formed version and date are present, never which.

Per **INV-246** the relocation sites are derived by scanning for the rule's subject rather than
listing paths -- the contract states it in two places, and a spec that named one would have left
the other silent.

Source spec: `specs/profile-report-filename-is-conditional-on-file-count.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE2 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" /
          "module-05-data-quality-mapping" / "phase2-data-mapping.md")
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: The suffixed filename shape a multi-file start produces.
SUFFIXED = "profile_report_<stem>.md"

#: A dated MCP provenance stamp. Deliberately not pinned to a version or date.
DATED = re.compile(r"server\s+\*{0,2}1\.\d+\.\d+\*{0,2},\s*(?:verified\s*)?\d{4}-\d{2}-\d{2}")

#: How far either side of a mention the guard looks for its companion. A CHARACTER window, not a
#: line-based one.
#:
#: ⚠️ **Chosen after a line-based passage regex produced false positives.** A
#: `(?:relocate|relocated).*(?:\n[^\n]*){0,14}` pattern split the contract mid-paragraph and
#: yielded fragments that mentioned relocating a `profile_report` while the suffixed form sat just
#: outside the fragment -- so the guard reported two offenders in text that was already correct.
#: Segmenting prose into "passages" by counting lines does not survive reflowing.
WINDOW_CHARS = 700

#: The rule's subject, located by mention rather than by path or line (INV-246): the contract
#: states relocation in three places -- the transient-artifacts list, "File placement during the
#: workflow", and the pre-next-source confirmation -- and a guard naming one would certify a
#: third of the fix.
RELOCATION_CUE = re.compile(r"(?i)relocate|relocated")


def text():
    return PHASE2.read_text(encoding="utf-8")


def flat(chunk):
    return re.sub(r"\s+", " ", chunk)


def profile_report_mentions():
    """(window, offset) for every `profile_report.md` mention, as a character window."""
    body = text()
    for match in re.finditer(r"`profile_report\.md`", body):
        lo = max(0, match.start() - WINDOW_CHARS)
        yield body[lo:match.end() + WINDOW_CHARS], match.start()


def relocation_passages():
    """Windows around a `profile_report.md` mention whose subject is relocation."""
    return [(w, off) for w, off in profile_report_mentions() if RELOCATION_CUE.search(w)]


class TheScanFindsBothRelocationSites(unittest.TestCase):
    def test_more_than_one_passage_governs_relocation(self):
        found = relocation_passages()
        self.assertGreaterEqual(
            len(found), 2,
            "fewer than two relocation windows mention the profile report (found %d). The "
            "contract states the rule in more than one place; a guard seeing one would certify "
            "part of the fix" % len(found))


class TheStaleLimitationIsRetired(unittest.TestCase):
    def setUp(self):
        self.flat = flat(text())

    def test_it_no_longer_claims_a_shared_output_path(self):
        self.assertNotRegex(
            self.flat, r"(?i)the emitted commands write to the same output path",
            "the retired limitation is back. On 1.33.0 a multi-file start writes one report per "
            "input; claiming otherwise sends the guide to work around a defect that is gone")

    def test_it_no_longer_instructs_concatenating_the_reports(self):
        self.assertNotRegex(
            self.flat, r"(?i)profile_report_<stem>\.md`\) and\s+concatenate",
            "the instruction to concatenate per-file reports is back — it recreates the "
            "single-schema file the entry existed to prevent, which is the worse half of the "
            "stale note")

    def test_the_lead_in_count_matches_the_surviving_entry(self):
        """The renumber half: 'Two limitations' over a list of one is the stale-count class."""
        self.assertNotRegex(
            self.flat, r"(?i)Two profiler limitations",
            "the lead-in still says two profiler limitations while only the headerless-CSV "
            "entry survives")
        self.assertRegex(
            self.flat, r"(?i)One profiler limitation",
            "the lead-in no longer states how many limitations follow, in either direction — "
            "check the renumber landed rather than that the old text is gone")

    def test_the_surviving_limitation_is_numbered_one(self):
        self.assertRegex(
            self.flat,
            r"1\. \*\*A headerless CSV is profiled by consuming its first data row",
            "the headerless-CSV entry is not numbered 1 after the retirement, so the lead-in "
            "count and the list still disagree")


class BothFilenamesAreDocumented(unittest.TestCase):
    def setUp(self):
        self.flat = flat(text())

    def test_the_conditional_naming_is_stated(self):
        self.assertRegex(
            self.flat, r"(?i)filename depends on how many files you pass",
            "the file does not state that the report's name is conditional on the input count")

    def test_both_shapes_are_named(self):
        self.assertIn(
            SUFFIXED, self.flat,
            "the suffixed form `%s` is never named, so a reader has no name for the files a "
            "multi-file start actually produces" % SUFFIXED)
        self.assertRegex(
            self.flat, r"\*{0,2}one\*{0,2} `file_paths` entry",
            "the single-file case is not distinguished from the multi-file one, so the "
            "conditional reads as a blanket rename")

    def test_the_claim_carries_dated_provenance(self):
        """⚠️ Checks EVERY occurrence of the phrase, because the FIRST is a cross-reference.

        A first version used `re.search` and landed on the relocation contract's pointer back to
        this claim -- which carries no stamp, and should not, since the claim it points at does.
        Asserting on the first match tested the wrong sentence.
        """
        occurrences = [m.group(0) for m in re.finditer(
            r"filename depends on how many files you pass.{0,900}", self.flat, re.S)]
        self.assertTrue(occurrences, "the conditional-naming phrase was not found at all")
        stamped = [o for o in occurrences if DATED.search(o)]
        self.assertTrue(
            stamped,
            "no occurrence of the conditional-naming claim carries a `server <version>, <date>` "
            "stamp (%d occurrence(s) checked); the suite is offline (INV-108), so the date IS "
            "the re-check mechanism" % len(occurrences))

    def test_the_server_prose_mismatch_is_marked_observation_only(self):
        self.assertRegex(
            self.flat, r"(?i)Read the `commands` array, not the prose",
            "the file does not tell the reader to read the emitted commands rather than step "
            "1's prose, which still hardcodes the unsuffixed name for a multi-file start")


class EveryRelocationPassageCoversTheSuffixedForm(unittest.TestCase):
    def test_no_passage_names_only_the_unsuffixed_report(self):
        offenders = []
        for passage, offset in relocation_passages():
            squashed = flat(passage)
            if "profile_report_" not in squashed:
                offenders.append("offset %d: %s" % (offset, squashed[:120]))
        self.assertEqual(
            [], offenders,
            "a relocation passage names `profile_report.md` and not the suffixed form: %s. A "
            "reader matching the literal name leaves `profile_report_<stem>.md` in the SHARED "
            "workspace, where the next source's run overwrites it — the exact collision INV-177 "
            "prevents, through a filename its original text did not cover" % offenders)

    def test_the_contract_states_the_rule_as_leaving_none_behind(self):
        """A per-filename list is what went stale; the property is what cannot."""
        self.assertRegex(
            flat(text()),
            r"(?i)NO profile report\s*is left in the shared workspace",
            "the contract does not state the rule as a property — that no profile report is "
            "left in the shared workspace whatever the server named it. Enumerating filenames "
            "is what failed the first time")


class Inv177CarriesTheDatedPremiseCorrection(unittest.TestCase):
    def setUp(self):
        body = INVARIANTS.read_text(encoding="utf-8")
        match = re.search(r"^- \*\*INV-177\*\* — .*$", body, re.M)
        assert match, "INV-177 was not found in INVARIANTS.md"
        self.invariant = match.group(0)

    def test_it_records_that_the_premise_was_narrower_than_the_rule(self):
        self.assertRegex(
            self.invariant, r"(?i)Premise corrected 2026-\d\d-\d\d",
            "INV-177 carries no dated premise correction, so its three-filename list still "
            "reads as the complete set of what the workspace receives")

    def test_it_is_marked_as_a_clarification_not_a_rule_change(self):
        """INVARIANTS.md rule 2 permits an in-place edit only to clarify without changing meaning."""
        self.assertRegex(
            self.invariant, r"Clarified \d{4}-\d{2}-\d{2}, no meaning change",
            "INV-177's note carries no dated no-meaning-change marker, so a later reader cannot "
            "tell a clarification from a rewritten rule")

    def test_it_names_the_suffixed_filename(self):
        self.assertIn(
            "profile_report_<stem>.md", self.invariant,
            "INV-177's correction does not name the filename shape that was missing from its "
            "premise, which is the whole content of the correction")

    def test_it_says_the_rule_still_binds_every_profile_report(self):
        self.assertRegex(
            self.invariant,
            r"(?i)binding \*\*every profile report the workspace\s*receives\*\*"
            r"|binding every profile report the workspace receives",
            "INV-177's correction does not say how to read the rule now, leaving the reader to "
            "infer whether the suffixed files are covered")


if __name__ == "__main__":
    unittest.main()
