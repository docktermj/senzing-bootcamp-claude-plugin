"""A consented-but-forbidden upstream send has its own `Upstream:` value, everywhere.

Two rules, each correct alone, collided on 2026-08-27. **Graduation Step 0** offers to forward
`mcp-server`-routed findings and send on a yes. **`/dry-run`** forbids calling `submit_feedback`
under any category, so a dry run never files into Senzing's real queue. On the first phase-3
walk ever to reach graduation, the maintainer answered "yes" in character and the walk had to
break character to explain the send could not happen.

⛔ **The vocabulary had no value for that outcome.** `feedback.md` Step 3 offered
`not applicable | offered, declined | submitted YYYY-MM-DD | submission failed: reason`, and the
nearest legal value — `offered, declined` — is **false about the one thing the field records**:
the bootcamper agreed. `submission failed:` is wrong too; nothing failed and no retry will
succeed. So `submission blocked: <reason>` was added.

⚠️ **What the harm is, stated accurately.** `feedback-to-specs` Step 1 skips a finding only when
the field says it was already *sent*, so a `declined` entry is not silently dropped from spec
filing — the spec that prompted this fix reasoned it would be, and that part is overstated. The
real cost is narrower and still worth fixing: the field is the record of what happened, and
`offered, declined` records the opposite of what happened, reading as "considered and rejected"
to anyone later deciding whether the report is still owed.

⚠️ What this does NOT establish: that a walk actually records the new value. That is a runtime
property of a phase-3 run (INV-108). It asserts the value exists wherever the vocabulary is
enumerated, so the two enumerations cannot drift.

Source spec: `specs/graduation-upstream-offer-collides-with-the-dry-run-no-send-rule.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
DRY_RUN = REPO_ROOT / ".claude" / "skills" / "dry-run" / "phase3-conversational.md"
VALUE = "submission blocked"
#: The other values, used to find every place the vocabulary is enumerated.
SIBLINGS = ("offered, declined", "submission failed")


def shipped_markdown():
    return sorted(p for p in PLUGIN.rglob("*.md") if "__pycache__" not in p.parts)


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def enumeration_lines():
    """Every LINE in shipped markdown that lists the `Upstream:` outcome vocabulary.

    Derived by looking for the sibling values rather than by naming files (INV-246): the
    spec predicted two sites, and a hardcoded pair cannot notice a third appearing.

    ⛔ **Line-level, not file-level, and that distinction is load-bearing.** A file-level
    version of this passed its own negative control: removing the value from the entry
    template still left it elsewhere in the same file, so the drift the guard exists to
    catch was invisible to it. The vocabulary drifts one enumeration at a time.
    """
    out = []
    for p in shipped_markdown():
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            low = line.lower()
            if all(s in low for s in SIBLINGS):
                out.append((p, i, line))
    return out


class TheVocabularyCarriesABlockedValue(unittest.TestCase):
    def test_the_enumerations_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertTrue(
            enumeration_lines(),
            "no shipped line enumerates the `Upstream:` outcome vocabulary any more; the scan "
            "broke or the vocabulary moved. Re-derive SIBLINGS rather than deleting this guard")

    def test_every_enumeration_includes_the_blocked_value(self):
        missing = [f"{p.relative_to(REPO_ROOT)}:{n}  {line.strip()[:90]}"
                   for p, n, line in enumeration_lines() if VALUE not in line.lower()]
        self.assertEqual(
            [], missing,
            f"an `Upstream:` vocabulary enumeration omits `{VALUE}:`, so the copies have "
            "drifted and a consented-but-forbidden send has no legal value there:\n  "
            + "\n  ".join(missing))

    def test_graduation_points_at_the_blocked_value(self):
        """Step 0 is where the collision fires, so the rule must be reachable there (INV-183)."""
        grad = PLUGIN / "senzing-bootcamp" / "skills" / "graduation" / "SKILL.md"
        flat = flatten(grad.read_text(encoding="utf-8"))
        self.assertIn(VALUE, flat,
                      "graduation Step 0 offers the forward but never names the value to record "
                      "when the session is forbidden to send")
        self.assertIn("never", flat[flat.index(VALUE):flat.index(VALUE) + 400],
                      "graduation names the blocked value without ruling out `offered, declined`, "
                      "which is the wrong value a runner would otherwise reach for")

    def test_the_blocked_value_is_distinguished_from_declined(self):
        """⛔ The whole point: it must not become a synonym for the other three."""
        fb = PLUGIN / "senzing-bootcamp" / "skills" / "bootcamp-onboarding" / "feedback.md"
        flat = flatten(fb.read_text(encoding="utf-8"))
        self.assertIn(VALUE, flat)
        window = flat[flat.index(f"⛔ **`{VALUE}"): flat.index(f"⛔ **`{VALUE}") + 900] \
            if f"⛔ **`{VALUE}" in flat else flat
        self.assertIn("not a synonym", window,
                      "feedback.md lists the blocked value without saying it is not a synonym "
                      "for declined/failed — which is how it becomes one")
        self.assertIn("offered, declined", window,
                      "the guidance does not name the wrong value it exists to displace")

    def test_the_dry_run_skill_names_the_gate_and_the_wording(self):
        """Maintainer-side, so it never ships — but it is where the runner reads."""
        self.assertTrue(DRY_RUN.is_file(), "dry-run phase3 doc is missing")
        flat = flatten(DRY_RUN.read_text(encoding="utf-8"))
        self.assertIn("graduation", flat)
        self.assertIn(VALUE, flat,
                      "the dry-run phase-3 doc does not tell the runner which value to record")
        self.assertIn("present the offer", flat,
                      "the doc must say the offer is PRESENTED — skipping the gate silently "
                      "corrupts the thing phase 3 exists to observe")
        self.assertRegex(
            flat, r"this is a dry run, so i can present this gate but i can't actually send",
            "the disclosure wording is gone, so a runner has to improvise it mid-walk — which "
            "is the situation this instruction exists to remove")


if __name__ == "__main__":
    unittest.main()
