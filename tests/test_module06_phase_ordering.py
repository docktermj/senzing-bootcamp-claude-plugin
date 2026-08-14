"""Phase A's pre-load checks must not prescribe an action Phase A cannot perform.

`phaseA-build-loading.md` opens with "Complete these three checks before starting step 1."
One of the three told the guide, when `test_load_status` is `skipped` or missing, to "run a
quick load of 10-100 records ... then set `test_load_status: complete`". Positioned before
step 1 that is unexecutable twice over:

* the loading program does not exist yet — step 3 builds it, from the volume tier captured
  at step 1;
* no `DATA_SOURCE` code is registered yet — step 4a registers them, and a load before that
  fails with SENZ2207, "Data source code [{0}] does not exist"
  (`explain_error_code('SENZ2207')`, server 1.32.9, 2026-08-14), which is the error step 4a
  exists to prevent.

It was also a **duplicate**: `phaseB-load-first-source.md` step 5 is the same test load on
the same condition, positioned after registration where it can actually run. A guide obeying
both ran it twice; a guide obeying Phase A's placement ran it before it could work.

This is the common path, not an edge case — `test_load_status` is missing on every source
whenever Module 5 Phase 3 was skipped, which that module marks Optional and which the
`mapping_workflow` step-5 `skip` branch makes the cheap default.

The write matters as much as the deletion: Phase A's copy was the **only** place that set
`test_load_status: complete`, so removing the action without moving the write would leave the
field never written, and Phase A would ask for the test load again on every resumed session.
That is what `TheWriteSurvivedTheMove` exists for.

Source spec: `specs/phase-a-preload-test-load-precedes-its-prerequisites.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
M6 = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "module-06-data-processing"
PHASE_A = M6 / "phaseA-build-loading.md"
PHASE_B = M6 / "phaseB-load-first-source.md"


def squash(text):
    return re.sub(r"\s+", " ", text)


def before_loading_section():
    """Phase A's pre-load preamble — everything gated 'before starting step 1'."""
    text = PHASE_A.read_text(encoding="utf-8")
    start = text.index("## Before Loading: pre-load checks")
    end = text.index("\n## ", start + 10)
    return text[start:end]


def phase_b_step5():
    text = PHASE_B.read_text(encoding="utf-8")
    start = text.index("## 5. Test with sample data")
    end = text.index("\n## 6.", start)
    return text[start:end]


class ThePreambleInstructsNoLoad(unittest.TestCase):
    """Criterion 1 — nothing under 'Before Loading' tells the guide to execute a load."""

    def test_the_preamble_does_not_prescribe_running_a_load(self):
        section = squash(before_loading_section())
        for phrase in (
            "run a quick load",
            "include a brief test-load step",
        ):
            self.assertNotIn(
                phrase, section,
                "Phase A's pre-load checks still prescribe a load: %r" % phrase,
            )

    def test_the_preamble_does_not_set_the_status_field(self):
        """Setting the field here would claim a load that never ran."""
        self.assertNotIn("set `test_load_status: complete`", squash(before_loading_section()))

    def test_the_preamble_still_reads_the_field(self):
        """Reading it is the check's whole purpose and must survive the edit."""
        self.assertIn("check `test_load_status` per source", squash(before_loading_section()))


class TheDeferralNamesWhereItHappens(unittest.TestCase):
    """Criterion 2 — a deferral with no destination is just a deletion."""

    def test_the_branch_defers_rather_than_prescribes(self):
        section = squash(before_loading_section())
        self.assertIn("a brief test load is **owed**", section)
        self.assertIn("Do not run it here", section)

    def test_the_branch_names_phase_b_step_5(self):
        self.assertIn("Phase B step 5 runs it", squash(before_loading_section()))

    def test_the_branch_gives_the_ordering_reason(self):
        """Without the reason, a later editor moves it back."""
        section = squash(before_loading_section())
        self.assertIn("step 4a", section)
        self.assertIn("SENZ2207", section)

    def test_the_complete_branch_is_unchanged(self):
        """The other branch of the same check must not be disturbed."""
        section = squash(before_loading_section())
        self.assertIn("You already test-loaded this source during Data Quality", section)


class TheWriteSurvivedTheMove(unittest.TestCase):
    """Criterion 3 — Phase A held the only write; Phase B must now carry it."""

    def test_step_5_sets_the_status_on_success(self):
        step5 = squash(phase_b_step5())
        self.assertIn("set `test_load_status: complete`", step5)
        self.assertIn("On success", step5)

    def test_step_5_says_why_the_write_matters(self):
        """An unrecorded run is re-requested on resume; that is the reason to write."""
        self.assertIn("Phase A", squash(phase_b_step5()))

    def test_the_field_is_written_exactly_once_in_the_module(self):
        """Two writers is how the duplicate arose in the first place."""
        writes = 0
        for path in sorted(M6.glob("*.md")):
            writes += squash(path.read_text(encoding="utf-8")).count(
                "set `test_load_status: complete`"
            )
        self.assertEqual(1, writes, "expected exactly one writer of test_load_status")


class TheOrderingReasonIsStatedAtTheStep(unittest.TestCase):
    """Criterion 4's other half — so the two halves cannot drift apart again."""

    def test_step_5_names_both_prerequisites(self):
        step5 = squash(phase_b_step5())
        self.assertIn("step 3", step5)
        self.assertIn("step 4a", step5)

    def test_step_5_names_the_error_with_its_provenance(self):
        """A dated citation is what lets a later reader re-check the claim (INV-080)."""
        step5 = squash(phase_b_step5())
        self.assertIn("SENZ2207", step5)
        self.assertIn("explain_error_code", step5)
        self.assertIn("1.32.9", step5)

    def test_step_5_forbids_reintroducing_an_upstream_copy(self):
        self.assertIn("do not add a second copy upstream", squash(phase_b_step5()))

    def test_phase_a_no_longer_describes_the_test_load_itself(self):
        """The record range is the signature of the action Phase A must not carry.

        Scoped to Phase A rather than asserted module-wide: `phaseC` step 18 tests the
        *orchestrator* across sources with the same 10-100 range, which is a different
        action on a different trigger. A module-wide uniqueness claim conflates the two
        and would fail on correct content — the shape of finding that INV-230 records.
        """
        self.assertNotIn("10–100 records", PHASE_A.read_text(encoding="utf-8"))

    def test_the_phase_3_gated_test_load_is_instructed_only_in_phase_b(self):
        """The duplicate was two files acting on one condition; only B may act on it."""
        acting = []
        for path in sorted(M6.glob("*.md")):
            text = squash(path.read_text(encoding="utf-8"))
            gated = "Phase 3 was skipped" in text or "did not complete Phase 3" in text
            if gated and "run the loading program on a small" in text:
                acting.append(path.name)
        self.assertEqual(["phaseB-load-first-source.md"], acting, acting)


if __name__ == "__main__":
    unittest.main()
