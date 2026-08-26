"""`docs/business_problem.md` keeps the Bootcamper's own words beside each refinement.

The template recorded only the guide's **refined** rendering of each interview answer and preserved
nothing of what was actually said. Asked about downstream integration on **2026-08-25**, a
Bootcamper said their **possible**-fraud entities should feed the fraud tool. The document rendered
it as *"Internal fraud tool (**confirmed fraud cases**)"*.

⛔ **One adjective, and a different routing rule** -- which entities reach the fraud tool, and how
large that queue is. Four lines earlier the same document still said *"Possible-fraud entities
routed to the internal fraud tool"*, so it **contradicted itself and carried nothing that could
settle which reading was right**.

⛔ **The gate that should have caught it could not see it.** Step 15 shows the refined document and
asks *"Does this accurately capture your problem and approach?"*. With the original wording visible
nowhere the question is *"does this plausible-sounding text sound right?"* rather than *"does this
match what I said?"* -- and a substituted adjective inside an otherwise-accurate sentence survives
it. It did: the document was confirmed as accurate, and the substitution propagated three modules on,
where Module 7 step 1 derived requirement 7 as *"Confirmed-fraud candidate list"*. The Bootcamper
approved those derived requirements too, reviewing only the refined artifact again.

⚠️ **So this is a correctness measure, not an archival nicety** -- which is why the tests below check
the *gate* as well as the template. A verbatim slot nobody is told to compare against changes
nothing.

⚠️ **Scope, deliberately narrow.** Only `docs/business_problem.md` and its confirmation gate. It is
the one artifact that is both built entirely from interview prose and read as an input by later
modules. Retrofitting verbatim capture into every module's write-ups is a separate decision with its
own cost in document length, and this guard must not be read as requiring it.

⛔ **What this cannot check.** Whether a given run actually quotes faithfully is a property of the
conversation, not of the files; `dry-run` phase 3 owns that. What is asserted here is that the slots
exist, that the omit-rather-than-invent rule is stated, that the gate tells the Bootcamper what they
are comparing, and that downstream derivation reads the refined text.

Stdlib only; shipped markdown read as text (INV-108).

Source spec: `specs/business-problem-keeps-only-the-refined-wording-so-the-gate-cannot-catch-drift.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
DOC_CONFIRM = SKILLS / "module-01-business-problem" / "phase2-document-confirm.md"
MODULE_07 = SKILLS / "module-07-query-visualize-discover" / "phase1-query-visualize.md"

QUOTE_SLOT = '> "[Their own words, verbatim]"'

#: The sections built from interview prose, which the guide interprets. Only these carry a slot.
INTERPRETED = ("Problem Description", "Success Criteria", "Desired Output",
               "Integration Requirements", "Notes")

#: Selections from fixed vocabularies -- nothing to preserve, so no slot.
MECHANICAL = ("Use Case Category", "Deployment Target", "Entity Types")


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def template_block():
    """The Step 11 markdown template, isolated from the prose around it."""
    text = DOC_CONFIRM.read_text(encoding="utf-8")
    start = text.index("# Business Problem Statement")
    end = text.index("```", start)
    return text[start:end]


class Base(unittest.TestCase):
    def has(self, text, pattern, msg):
        self.assertTrue(re.search(pattern, text), msg)


class TheTemplateCarriesAVerbatimSlot(Base):
    def setUp(self):
        self.template = template_block()

    def test_the_template_is_found(self):
        """Anti-vacuity (INV-265): every assertion below reads this block."""
        self.assertIn("## Problem Description", self.template)
        self.assertGreater(len(self.template), 800,
                           "the template block did not parse; the assertions below are vacuous")

    def test_every_interpreted_section_has_a_quote_slot(self):
        for section in INTERPRETED:
            with self.subTest(section=section):
                start = self.template.index("## %s" % section)
                nxt = self.template.find("\n## ", start + 1)
                body = self.template[start:nxt if nxt != -1 else len(self.template)]
                self.assertIn(
                    QUOTE_SLOT, body,
                    "'%s' is built from interview prose and carries no verbatim slot, so a "
                    "misrendering of it cannot be caught at the confirmation gate" % section,
                )

    def test_no_mechanical_section_has_a_quote_slot(self):
        """A fixed-vocabulary selection has nothing to preserve; a slot there invites invention."""
        for section in MECHANICAL:
            with self.subTest(section=section):
                start = self.template.index("## %s" % section)
                nxt = self.template.find("\n## ", start + 1)
                body = self.template[start:nxt if nxt != -1 else len(self.template)]
                self.assertNotIn(QUOTE_SLOT, body,
                                 "'%s' is a selection from a fixed vocabulary; a verbatim slot "
                                 "there can only be filled by inventing one" % section)

    def test_the_slot_count_matches_the_interpreted_sections(self):
        self.assertEqual(
            len(INTERPRETED), self.template.count(QUOTE_SLOT),
            "the number of verbatim slots does not match the number of interpreted sections",
        )


class TheRuleGoverningTheSlotsIsStated(Base):
    def setUp(self):
        self.text = flat(DOC_CONFIRM)

    def test_the_slots_are_identified_as_quotes_not_renderings(self):
        self.has(self.text,
                 r"(?i)the Bootcamper's OWN WORDS, quoted — not a second\s+rendering",
                 "nothing tells the guide the slots are quotes rather than a second summary, which "
                 "is the one way to fill them that preserves nothing")

    def test_refinement_is_distinguished_from_transcription(self):
        self.has(self.text, r"(?i)Refinement\s+is not transcription",
                 "the rule does not say refinement is not transcription")

    def test_the_omit_rather_than_invent_rule_is_stated(self):
        self.has(self.text,
                 r"(?i)OMIT the quote — never manufacture one|omit the quote rather than",
                 "the template does not say to omit the quote for a fixed-vocabulary selection, so "
                 "a guide facing a bare option number invents a verbatim line")
        self.has(self.text, r'(?i)invented "verbatim"\s+line is worse than none',
                 "the reason omission beats invention is not given")

    def test_the_refined_prose_stays_the_working_text(self):
        self.has(self.text,
                 r"(?i)refined prose stays the working text",
                 "the template does not say the refined text remains what downstream reads, so a "
                 "guide may treat the quotes as the new source of truth")

    def test_the_incident_keeps_its_evidence(self):
        self.has(self.text, r"2026-08-25", "the incident date is not recorded")
        self.has(self.text, r"(?i)confirmed fraud cases",
                 "the actual misrendering is not quoted, so the rule loses the example that makes "
                 "its stakes concrete")
        self.has(self.text, r"(?i)contradicted\s+itself",
                 "the self-contradiction -- the strongest evidence the document could not settle "
                 "the question -- is not recorded")

    def test_the_persisted_answer_route_is_named_for_integration_requirements(self):
        """INV-097 already persists that answer; quoting from disk beats reconstructing it."""
        self.has(self.text, r"INV-097", "INV-097 is not cited")
        self.has(self.text,
                 r"(?i)quote from there, do not\s+reconstruct it",
                 "the template does not route the Integration Requirements quote to the persisted "
                 "answer, so the one section whose drift is mechanically checkable is not")


class TheGateShowsBothVersions(Base):
    def setUp(self):
        self.text = flat(DOC_CONFIRM)

    def test_step_15_says_to_present_both(self):
        self.has(self.text,
                 r"(?i)Present the document with BOTH versions visible",
                 "Step 15 does not require both versions to be visible, so the verbatim slots "
                 "exist and nobody is asked to compare against them")

    def test_it_says_which_lines_are_whose(self):
        self.has(self.text,
                 r"(?i)their own words as they said them and the prose above each is your",
                 "Step 15 does not tell the Bootcamper which lines are theirs and which are the "
                 "guide's rendering")

    def test_it_names_a_mismatch_as_the_point_of_the_question(self):
        self.has(self.text,
                 r"(?i)a mismatch between the two is exactly what this question is for",
                 "Step 15 shows both versions without saying that a mismatch is what it is asking "
                 "about")

    def test_the_pinned_question_wording_is_unchanged(self):
        """INV-056 — this spec changes what precedes the question, not the question."""
        self.assertIn(
            "👉 **Does this accurately capture your problem and approach?**",
            DOC_CONFIRM.read_text(encoding="utf-8"),
            "the pinned confirmation question wording changed; this spec must not touch it",
        )
        self.has(self.text, r"(?i)pinned verbatim \(INV-056\) and is\s+\*\*unchanged\*\*",
                 "Step 15 does not record that the question wording is unchanged")


class DownstreamReadsTheRefinedText(Base):
    def setUp(self):
        self.text = flat(MODULE_07)

    def test_module_7_derives_from_the_refined_prose(self):
        self.has(self.text,
                 r"(?i)Derive from the REFINED prose, not from the",
                 "Module 7 step 1 does not say which of the two versions its requirement "
                 "derivation consumes, so the added quotes can be mistaken for requirements input")

    def test_it_still_reads_the_quotes_when_the_two_disagree(self):
        """The quotes are provenance -- useless if the one consumer is told to ignore them."""
        self.has(self.text,
                 r"(?i)read them when the two\s+disagree",
                 "Module 7 is told to ignore the quotes unconditionally, so a drift that reached "
                 "this module has no chance of being noticed here either")

    def test_it_raises_a_discrepancy_rather_than_picking_a_side(self):
        self.has(self.text,
                 r"(?i)Raise the discrepancy here rather than deriving a\s+requirement from either "
                 r"side",
                 "Module 7 is not told what to do when the two disagree, which is the case that "
                 "actually occurred")


if __name__ == "__main__":
    unittest.main()
