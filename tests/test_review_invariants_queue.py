"""`pending_invariants.py` counts deferral BLOCKS, not lines that mention deferrals.

The helper exists because a hand count of pending invariants on 2026-09-01 returned **29**
against a true **11**: it grepped `specs/IMPLEMENTED.md` for the phrase "DEFERRED
INVARIANT", and ledger prose *about* deferrals -- audit summaries, "INVARIANT REGISTERED"
entries quoting the term, a bullet explaining the deferral convention -- matched too.

The first version of the helper reproduced that same overcount (25 against 9), because it
kept any bullet containing the phrase rather than any block carrying the sign-off MARKER.
Twice in one day, in the fix for itself, is the argument for pinning it here.

This asserts the count by a **different mechanism** than the helper uses: a flat scan for
the marker string, versus the helper's block splitting. Agreement between two mechanisms
is evidence; re-running the helper's own logic would not be.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HELPER = REPO / ".claude" / "skills" / "review-invariants" / "pending_invariants.py"
LEDGER = REPO / "specs" / "IMPLEMENTED.md"
SPECS = REPO / "specs"

AWAITING = "awaiting the maintainer's sign-off; NOT minted"
# ⚠️ A deferral carries ONE of two markers, not always the first. A block whose spec
# required approval before implementation never says "awaiting sign-off" -- it says this.
# Scanning for only the first found 0 held where 1 is held, and the disagreement with the
# helper is what surfaced it: two mechanisms are evidence precisely when they differ.
HELD_IN_BLOCK = "must be approved before implementation"
HELD_IN_SPEC = "Held, not merely unapproved"


def helper(*args):
    r = subprocess.run([sys.executable, str(HELPER), *args],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, f"helper exited {r.returncode}: {r.stderr[:400]}"
    return r.stdout


def counted_by_scanning():
    """(pending, held) derived by a flat marker scan -- not by splitting blocks."""
    text = LEDGER.read_text(encoding="utf-8")
    spec, pending, held = None, 0, 0
    for line in text.splitlines():
        if line.startswith("## "):
            spec = line[3:].strip()
        if AWAITING not in line and HELD_IN_BLOCK not in line:
            continue
        f = SPECS / f"{spec}.md"
        is_held = (HELD_IN_BLOCK in line
                   or (f.is_file() and HELD_IN_SPEC in f.read_text(encoding="utf-8")))
        held += is_held
        pending += not is_held
    return pending, held


class TheQueueCountsBlocksNotMentions(unittest.TestCase):
    def setUp(self):
        self.out = helper("list")
        m = re.search(r"pending: (\d+)\s+held: (\d+)", self.out)
        self.assertIsNotNone(m, f"`list` printed no counts:\n{self.out[:400]}")
        self.reported = (int(m.group(1)), int(m.group(2)))

    def test_the_pending_count_agrees_with_a_flat_marker_scan(self):
        pending, _ = counted_by_scanning()
        self.assertEqual(
            pending, self.reported[0],
            f"the helper reports {self.reported[0]} pending; scanning for the sign-off "
            f"marker finds {pending}. A gap this way round means prose that merely "
            "mentions a deferral is being counted as one.",
        )

    def test_a_held_block_is_never_listed_as_pending(self):
        """The other half: a decision already made must not be re-offered."""
        _, held = counted_by_scanning()
        self.assertEqual(
            held, self.reported[1],
            "the helper's held count disagrees with the spec files' recorded holds. A "
            "block whose spec says 'Held, not merely unapproved' has been decided, and "
            "presenting it as awaiting review asks for a decision that already exists.",
        )
        self.assertIn("HELD: already decided, NOT for review", self.out)

    def test_every_quoted_rule_still_matches_its_source(self):
        """`check` is the guard the skill runs before quoting a block to the maintainer."""
        out = helper("check")
        m = re.search(r"(\d+) rule quotes checked, (\d+) mismatched", out)
        self.assertIsNotNone(m, out[:300])
        self.assertEqual(
            "0", m.group(2),
            f"a deferral quotes a rule its named file does not contain:\n{out}",
        )
        # ⚠️ Zero CHECKED is legitimate once every deferral carrying `— in `path`` bullets has
        # been resolved — which happened on 2026-09-02. It is not legitimate while such a
        # block is still pending, so the floor is conditional on the queue rather than fixed.
        # A fixed floor of 1 fails on a finished queue and reads as a defect; no floor at all
        # would let a broken scan report a clean run forever.
        # Block-aware: a rule bullet counts only while inside an UNRESOLVED block. Counting
        # every such bullet in the file counts the resolved ones too, which are exactly what
        # the helper stops checking — so the floor never falls and a finished queue reads as
        # a broken scan.
        quotable, inside = 0, False
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.startswith("- **") or line.startswith("## "):
                inside = ("DEFERRED INVARIANT" in line and "resolved INV-" not in line)
            elif inside and line.lstrip().startswith("- ") and "⛔ **" in line and "— in `" in line:
                quotable += 1
        if quotable:
            self.assertGreater(
                int(m.group(1)), 0,
                f"the ledger still carries {quotable} quotable rule bullet(s) and the scan "
                "checked none — the scan is broken, not the queue empty.",
            )

    def test_next_id_is_one_past_the_highest(self):
        inv = (REPO / "specs" / "INVARIANTS.md").read_text(encoding="utf-8")
        highest = max(int(x) for x in re.findall(r"\*\*INV-(\d{3})\*\*", inv))
        self.assertEqual(f"INV-{highest + 1:03d}", helper("next-id").strip())


if __name__ == "__main__":
    unittest.main()
