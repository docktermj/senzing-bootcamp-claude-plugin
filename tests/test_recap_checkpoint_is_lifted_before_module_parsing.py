"""The RECAP-CHECKPOINT block is lifted before module parsing, like BOOTCAMP-NOTES.

`SessionStart:resume` folds `docs/progress/recap_checkpoint.md` into the recap verbatim,
fenced in ``<!-- RECAP-CHECKPOINT:START/END -->``. The checkpoint's own interior uses
``## `` headings (``## Where we are``, ``## Still to do``, …), and **every** ``## `` in a
recap is parsed as a module — so a resumed session put five phantom "modules" beside the
nine real ones in the keepsake PDF (2026-08-26, plugin 0.5.2).

The generator already lifts the sibling ``BOOTCAMP-NOTES`` fence for exactly this reason,
and its own comment says the fence "is the discriminator, not the heading text". The
checkpoint fence had the same exposure and none of the protection: one rule, two fences,
one implementation.

⚠️ ``audit_recap`` DID warn that a checkpoint block survived — the reporter's "no error, no
warning" was not accurate. But the warning is **non-fatal** and the block was never lifted,
so the PDF rendered with the phantom sections anyway. Detection is not prevention, and this
guard asserts both halves: the lift happens AND the warning survives it.

Stdlib only; the generator is loaded by path, importing nothing from ``plugins/`` as a
package (INV-108).
"""

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GENERATOR = REPO / "plugins" / "senzing-bootcamp" / "scripts" / "generate_recap_pdf.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("_recap_gen", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: the module's @dataclass decorators resolve annotations
    # through sys.modules, and fail with AttributeError without this.
    sys.modules["_recap_gen"] = module
    spec.loader.exec_module(module)
    return module


CHECKPOINT_BODY = """<!-- RECAP-CHECKPOINT:START -->
## Where we are
mid-module
## What is done in this module
- a thing
## Still to do
- another
## To restart the visualization
run it
## Headline results to carry in
- 12 entities
<!-- RECAP-CHECKPOINT:END -->"""

PHANTOM_TITLES = ("Where we are", "What is done in this module", "Still to do",
                  "To restart the visualization", "Headline results to carry in")


def recap_with(block):
    """A two-module recap with `block` folded between them, as the resume hook folds it."""
    return """# Senzing Bootcamp Recap

## Discover the Business Problem

### Information Shared
- something real that is long enough to carry the retention ratio comfortably

%s

## SDK setup

### Information Shared
- also real, and also long enough to count for something in the denominator
""" % block


class TheCheckpointNeverBecomesAModule(unittest.TestCase):
    def setUp(self):
        self.gen = load_generator()

    def test_checkpoint_headings_are_not_parsed_as_modules(self):
        recap = self.gen.parse_recap(recap_with(CHECKPOINT_BODY))
        titles = [m.title for m in recap.modules]
        for phantom in PHANTOM_TITLES:
            with self.subTest(heading=phantom):
                self.assertNotIn(
                    phantom, titles,
                    "a heading inside the RECAP-CHECKPOINT fence reached Recap.modules. "
                    "The fence must be lifted before module parsing, exactly as the "
                    "BOOTCAMP-NOTES fence is — otherwise a resumed session prints phantom "
                    "modules in the Bootcamper's keepsake PDF.",
                )

    def test_the_real_modules_on_both_sides_survive(self):
        """A lift that ate real content would be worse than the defect."""
        recap = self.gen.parse_recap(recap_with(CHECKPOINT_BODY))
        titles = [m.title for m in recap.modules]
        self.assertEqual(
            ["Discover the Business Problem", "SDK setup"], titles,
            "the modules before and after the fence must both survive the lift",
        )


class TheWarningSurvivesTheLift(unittest.TestCase):
    """⛔ Lifting the block must not silence the audit — they answer different questions."""

    def setUp(self):
        self.gen = load_generator()

    def test_a_surviving_checkpoint_block_is_still_reported(self):
        source = recap_with(CHECKPOINT_BODY)
        audit = self.gen.audit_recap(self.gen.parse_recap(source), source)
        self.assertTrue(
            any("RECAP-CHECKPOINT" in w for w in audit.warnings),
            "audit_recap must still warn that a checkpoint block survived into the recap — "
            "that means a module was folded and never finalized (module-completion step "
            "2d), which stays worth reporting even once its headings can no longer leak.",
        )


class TheLiftDoesNotLookLikeContentLoss(unittest.TestCase):
    """⚠️ The second-order effect the fix has to carry, or it blocks the PDF.

    Lifted characters cannot reach the PDF by design, so counting them in the retention
    denominator measures the lift's own effect as loss. On a fixture that dropped
    retention to 42% and produced a **fatal** catastrophic-content-loss verdict — which
    would block the recap PDF that INV-048 requires always to be produced.
    """

    def setUp(self):
        self.gen = load_generator()

    def test_lifting_the_block_does_not_trip_the_fatal_content_loss_gate(self):
        source = recap_with(CHECKPOINT_BODY)
        audit = self.gen.audit_recap(self.gen.parse_recap(source), source)
        self.assertEqual(
            [], audit.fatal,
            "lifting the checkpoint must not register as content loss: its characters are "
            "excluded from the source count because they can never be rendered. Fatal: %r"
            % (audit.fatal,),
        )

    def test_retention_is_measured_against_renderable_source(self):
        source = recap_with(CHECKPOINT_BODY)
        audit = self.gen.audit_recap(self.gen.parse_recap(source), source)
        self.assertGreater(
            audit.retention, 0.60,
            "retention must be computed against the source MINUS the discarded fences; "
            "otherwise a resumed session's recap reads as catastrophically lossy.",
        )


class AnUnterminatedFenceDoesNotEatTheRecap(unittest.TestCase):
    """⛔ The deliberate asymmetry with the notes fence, pinned so it is not "tidied".

    `_extract_notes_block` runs an unterminated notes fence to end-of-text, which is safe
    because graduation appends notes AFTER the last module. The checkpoint is folded
    MID-recap, so the same treatment would delete the Bootcamper's real finalized modules.
    A phantom section the audit already warns about is the lesser loss.
    """

    def setUp(self):
        self.gen = load_generator()

    def test_modules_after_an_unterminated_fence_are_not_truncated(self):
        unterminated = CHECKPOINT_BODY.replace("\n<!-- RECAP-CHECKPOINT:END -->", "")
        recap = self.gen.parse_recap(recap_with(unterminated))
        titles = [m.title for m in recap.modules]
        self.assertIn(
            "SDK setup", titles,
            "an unterminated checkpoint fence must NOT truncate the recap to end-of-text: "
            "the block is folded mid-recap, so everything after it is real module content.",
        )
        self.assertIn("Discover the Business Problem", titles)


class TheLiftNeverEmptiesTheRecap(unittest.TestCase):
    """⛔ Deleting real module content to avoid phantom headings is not a trade this makes.

    A checkpoint fence contains only in-progress narrative — `recap_checkpoint.py`'s
    `_strip_block` states it: *"Completed ``## {module}`` sections carry no markers and are
    never touched."* But a malformed or mis-placed fence CAN enclose finalized sections,
    and `tests/test_recap_pdf_guard.py` builds exactly that shape. Where stripping would
    remove every module heading from a recap that had one, the unstripped text is kept:
    the phantom sections render and `audit_recap` warns, which is the pre-existing
    behavior and the lesser loss.
    """

    def setUp(self):
        self.gen = load_generator()

    def test_a_fence_enclosing_every_module_is_not_stripped(self):
        swallowed = ("<!-- RECAP-CHECKPOINT:START -->\n\n"
                     "## Discover the Business Problem\n\n"
                     "### Information Shared\n"
                     "- real content that must not be deleted\n\n"
                     "<!-- RECAP-CHECKPOINT:END -->\n")
        recap = self.gen.parse_recap("# Senzing Bootcamp Recap\n\n" + swallowed)
        self.assertIn(
            "Discover the Business Problem", [m.title for m in recap.modules],
            "a fence that encloses every module must NOT be stripped — doing so deletes "
            "the Bootcamper's real content to avoid phantom headings, which is the worse "
            "of the two failures.",
        )

    def test_the_normal_case_is_still_stripped(self):
        """The guard must not disable the lift whenever any fence is present."""
        recap = self.gen.parse_recap(recap_with(CHECKPOINT_BODY))
        self.assertNotIn("Where we are", [m.title for m in recap.modules])


#: Both fence types, so the rule below is asserted as a class rather than an instance.
FENCE_PAIRS = (
    ("<!-- RECAP-CHECKPOINT:START -->", "<!-- RECAP-CHECKPOINT:END -->"),
    ("<!-- BOOTCAMP-NOTES:START -->", "<!-- BOOTCAMP-NOTES:END -->"),
)


def recap_with_stray_fence(start_marker, end_marker):
    """A stray START, then a REAL module, then a well-formed fence.

    The shape that deleted `## SDK setup`: the stray's terminator search found the LATER
    fence's END, so the span covered both and the module between them went with it.
    """
    return """# Senzing Bootcamp Recap

## Discover the Business Problem

### Information Shared
- first real module, long enough for the retention denominator to be meaningful

%s
## Where we are
stale, never closed

## SDK setup

### Information Shared
- SECOND REAL MODULE between the two fences, with content that must not vanish

%s
## Still to do
- a later, well-formed block
%s

## Data collection

### Information Shared
- third real module, also long enough to count for something here
""" % (start_marker, start_marker, end_marker)


class AStrayFenceNeverAnnexesAModule(unittest.TestCase):
    """⛔ The HIGH finding of `production-readiness-audit-2026-09-01d`.

    Both handlers located their terminator with ``text.find(END, start)`` — the next END
    *anywhere* — so a stray unterminated START spanned to a later fence's terminator and
    discarded every finalized module in between. Measured on the shipped script: a
    three-module recap parsed to two.

    ⚠️ It was silent three ways, which is why this is asserted rather than left to review:
    ``audit_recap`` fired the *unfinalized-module* warning (true, about something else),
    ``--expect-modules`` checks presence and never absence, and ``_source_content_chars``
    stripped the same region so the loss left the retention **denominator** too — 94%
    retention, no fatal, on a recap that had lost a module.
    """

    def setUp(self):
        self.gen = load_generator()

    def test_the_module_between_two_fences_survives(self):
        for start_marker, end_marker in FENCE_PAIRS:
            with self.subTest(fence=start_marker):
                recap = self.gen.parse_recap(recap_with_stray_fence(start_marker, end_marker))
                titles = [m.title for m in recap.modules]
                self.assertIn(
                    "SDK setup", titles,
                    "a finalized module between a stray fence START and a later fence's "
                    "END must survive. Annexing that region to lift one block deletes the "
                    "Bootcamper's own content from the keepsake PDF, and nothing reports "
                    "it. Parsed: %r" % (titles,),
                )
                self.assertIn("Data collection", titles)
                self.assertIn("Discover the Business Problem", titles)

    def test_the_stray_is_reported_by_name(self):
        """Not deleted and not silent: the operator is told which marker is malformed."""
        for start_marker, end_marker in FENCE_PAIRS:
            with self.subTest(fence=start_marker):
                source = recap_with_stray_fence(start_marker, end_marker)
                audit = self.gen.audit_recap(self.gen.parse_recap(source), source)
                self.assertTrue(
                    any("stray" in w and start_marker in w for w in audit.warnings),
                    "a stray fence START must be reported by name. Leaving its region in "
                    "place is the safe choice, but an unremoved block is content the fence "
                    "was meant to lift — for the notes fence, a private note one heading "
                    "from the recap (INV-100).",
                )

    def test_the_well_formed_fence_after_a_stray_is_still_handled(self):
        """Skipping the stray must not disable the fence that IS well formed."""
        start_marker, end_marker = FENCE_PAIRS[0]
        recap = self.gen.parse_recap(recap_with_stray_fence(start_marker, end_marker))
        self.assertNotIn(
            "Still to do", [m.title for m in recap.modules],
            "the later, well-formed checkpoint block must still be lifted — otherwise "
            "fixing the stray case would reintroduce the phantom-module defect.",
        )

    def test_a_genuinely_unterminated_notes_fence_keeps_its_end_of_text_policy(self):
        """⚠️ Unchanged, and only reachable when NO well-formed block exists.

        Graduation appends the notes block after the last module, so sweeping to
        end-of-text is safe there — and it is what stops a truncated fold putting a
        private note on the certificate (INV-100). Where a later well-formed fence
        exists, the sweep is NOT used, because it would delete every module after the
        stray marker.
        """
        text = ("# Senzing Bootcamp Recap\n\n## Discover the Business Problem\n\n"
                "### Information Shared\n- real\n\n"
                "<!-- BOOTCAMP-NOTES:START -->\n## Notes, Ideas and Questions\n\n"
                "### Idea: one\n**Captured:** 2026-08-26\n\na private thought\n")
        recap = self.gen.parse_recap(text)
        self.assertNotIn(
            "Notes, Ideas and Questions", [m.title for m in recap.modules],
            "an unterminated notes fence with no well-formed block after it must still "
            "sweep to end of text — the note must never become a module section.",
        )
        self.assertIsNotNone(recap.notes)


class TheFenceSetIsARegistryNotAOneOff(unittest.TestCase):
    """INV-246: adding a fence brings it under the lift, rather than needing a new branch."""

    def setUp(self):
        self.gen = load_generator()

    def test_the_checkpoint_fence_is_registered(self):
        self.assertIn(
            (self.gen.RECAP_CHECKPOINT_START, self.gen.RECAP_CHECKPOINT_END),
            tuple(self.gen.DISCARDED_FENCES),
            "the checkpoint fence must be in DISCARDED_FENCES, which the parse path "
            "iterates — a third fenced block must not be able to repeat this defect by "
            "being overlooked in a hand-written branch.",
        )

    def test_the_notes_fence_is_not_discarded(self):
        """Its content is KEPT and parsed; discarding it would delete the Bootcamper's notes."""
        markers = {start for start, _ in self.gen.DISCARDED_FENCES}
        self.assertNotIn(
            self.gen.BOOTCAMP_NOTES_START, markers,
            "the notes fence must never be in DISCARDED_FENCES — its content is rendered "
            "into the recap, not discarded.",
        )

    def test_notes_are_still_parsed_and_kept(self):
        notes_block = ("<!-- BOOTCAMP-NOTES:START -->\n"
                       "## Notes, Ideas and Questions\n\n"
                       "### Idea: check the truth-set counts\n"
                       "**Captured:** 2026-08-26\n\n"
                       "a thought of my own\n"
                       "<!-- BOOTCAMP-NOTES:END -->")
        recap = self.gen.parse_recap(recap_with(notes_block))
        self.assertIsNotNone(
            recap.notes,
            "the notes block must still be lifted AND kept — this fix must not turn the "
            "notes fence into a discarded one.",
        )
        self.assertNotIn("Notes, Ideas and Questions", [m.title for m in recap.modules])


if __name__ == "__main__":
    unittest.main()
