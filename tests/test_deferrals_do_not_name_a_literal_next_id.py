"""A pending deferred invariant never states a literal "next free id".

`specs/IMPLEMENTED.md` accumulates `DEFERRED INVARIANT — awaiting the maintainer's sign-off`
blocks, each holding drafted wording for an invariant only the maintainer may mint. Each block
carried a parenthetical naming the next free id as a number. On 2026-09-01 there were **eight**
pending blocks and **seven** of them said *"next free id: 285"*.

285 was correct — for the first one minted, and no other. The operative instruction ("mint at
the next free id") is self-correcting; the **number** cannot survive the queue being worked,
and six of seven become wrong the moment sign-off starts while reading exactly as
authoritative as when written.

⚠️ The stale-enumeration class applied to a figure rather than a list: each copy was accurate
on the day it was written, and only the *set* is wrong — which is what makes it invisible to
review of any single block.

⛔ Scoped to **pending** blocks. `DEFERRED INVARIANT (resolved INV-NNN, …)` entries are
historical records of what a draft said before it was minted, and a number inside one is a
fact about the past. Prose *about* this defect — an audit entry quoting it — is likewise not a
deferral hint.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "specs" / "IMPLEMENTED.md"

PENDING = "DEFERRED INVARIANT — awaiting the maintainer's sign-off"
#: "next free id: 285", "next unused id 300", "the next id is 291" — a number offered as THE id.
LITERAL_NEXT_ID = re.compile(r"(?i)next\s+(?:free|unused|available)\s+id\D{0,4}\d{2,}")


def pending_blocks():
    """Each pending deferral's text, from its marker to the entry's Commit: line."""
    text = LEDGER.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(re.escape(PENDING), text):
        end = text.find("\n- **Commit:**", m.start())
        out.append(text[m.start(): end if end != -1 else m.start() + 4000])
    return out


class NoPendingDeferralNamesALiteralId(unittest.TestCase):
    def test_the_scan_finds_the_pending_blocks(self):
        """A scan matching nothing would make the assertion below vacuous.

        ⚠️ Zero is legitimate ONLY when the queue is genuinely empty, which happened on
        2026-09-02 when the maintainer decided the last nine. So zero must be corroborated
        by a second, independent reading of the ledger rather than accepted on the strength
        of this scan finding nothing — a marker whose wording drifted would also find
        nothing, and would look exactly like a finished queue.
        """
        found = pending_blocks()
        if found:
            return
        resolved = LEDGER.read_text(encoding="utf-8").count("DEFERRED INVARIANT (resolved ")
        self.assertNotIn(
            PENDING, LEDGER.read_text(encoding="utf-8"),
            "the scan found no pending blocks while the marker it looks for is still in the "
            "ledger — the scan is broken, not the queue empty.",
        )
        self.assertGreater(
            resolved, 0,
            "no pending blocks AND no resolved ones either: the ledger carries no deferrals "
            "in any state, which means the marker wording changed and this guard has stopped "
            "reading the maintainer's worklist.",
        )

    def test_no_pending_block_states_a_literal_next_free_id(self):
        offenders = []
        for block in pending_blocks():
            m = LITERAL_NEXT_ID.search(block)
            if m:
                offenders.append(m.group(0))
        self.assertEqual(
            [], offenders,
            "A pending deferral names a literal next-free id. At most one pending block can be "
            "right about that number, and the rest go wrong silently the moment sign-off "
            "starts. Say 'mint at the next free id, read it off INVARIANTS.md' instead. "
            "Found: %r" % offenders,
        )

    def test_the_blocks_still_explain_why_the_id_is_written_as_NNN(self):
        """⛔ The reason is real and must not be lost with the number.

        A literal id in a deferral turns `citations.py verify` red, because it reads as a
        citation of an invariant that does not exist. Dropping that explanation would invite
        the next author to write the id in.
        """
        for block in pending_blocks():
            with self.subTest(block=block[:60]):
                self.assertRegex(
                    block, r"(?i)written as NNN deliberately",
                    "Every pending deferral must still say why the id is written as NNN. "
                    "Removing the number without the reason is how it comes back.",
                )

    def test_the_instruction_to_read_the_id_off_the_ruleset_is_present(self):
        for block in pending_blocks():
            with self.subTest(block=block[:60]):
                self.assertRegex(
                    block, r"(?i)read it off `INVARIANTS\.md`",
                    "Each block must tell the maintainer where the real next id lives, since "
                    "the number is no longer written here.",
                )


class ResolvedDeferralsAreLeftAlone(unittest.TestCase):
    """A number inside a resolved block is a fact about the past, not a stale hint."""

    def test_resolved_blocks_are_not_scanned(self):
        text = LEDGER.read_text(encoding="utf-8")
        resolved = re.findall(r"DEFERRED INVARIANT \(resolved INV-\d+", text)
        if not resolved:
            self.skipTest("no resolved deferrals recorded yet")
        for block in pending_blocks():
            self.assertNotIn(
                "(resolved INV-", block[:80],
                "the pending-block scan picked up a resolved deferral; those record what a "
                "draft said before it was minted and must not be rewritten",
            )


if __name__ == "__main__":
    unittest.main()
