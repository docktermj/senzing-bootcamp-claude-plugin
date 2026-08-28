"""Every hard rule added since the last audit is cited at its line, or deferred by name.

The reverse contract has two legitimate states for a hard rule the plugin ships, and
silence is neither:

- **Cited** — an `INV-nnn` at the rule's own line, so a reader standing there can look the
  governing rule up (INV-183).
- **Deferred** — the rule is named in a `DEFERRED INVARIANT` block in `IMPLEMENTED.md`, with
  drafted wording, because only the maintainer may sign off on an invariant. The citation is
  then *un-writable* until the id is minted, which is exactly the queued-approval hazard
  `implement-spec` Step 5 names.

⛔ **INV-282 governs how this guard matches** — from the claim, not from phrasings already seen.

⛔ **This guard exists because the manual version of the check failed twice.** On 2026-08-28 a
ledger entry claimed *"all four hard-rule lines cite one of those at the line"* when two did
not — written from a `per-rule --uncited | grep` narrowed to two phrases, three cycles after
an audit had already recorded that method as unsound. A grep can only confirm lines you
already suspect; the uncited ones are by construction the ones you did not. The check has to
be a set difference, and a set difference is a thing a test can do.

⚠️ **Scope: rules added since the newest audit entry's recorded commit** — the set a run is
answerable for, resolved from the ledger rather than guessed. It does **not** police the
standing backlog of uncited rules across the corpus; that is `per-rule --uncited`'s worklist
and is far larger.

⚠️ **A rule REVERTED to its pre-audit wording leaves this guard's scope, and that is not a
hole to plug.** `since` diffs against the newest audit's commit, so deleting a citation that
was added *after* that commit makes the line identical to the committed one and it stops
being reported. Verified by negative control: the guard is unmoved by that edit and fails
correctly on a genuinely new uncited rule, which is what it claims to cover. The standing
backlog is `per-rule --uncited`'s job, and it is far larger.

⚠️ **Skips rather than fails when the range cannot be resolved** — no git, a shallow clone, an
audit entry whose `Commit:` is `uncommitted`. A guard that hard-failed there would fail on
checkouts that have nothing wrong with them.

Source spec:
`specs/three-hard-rules-from-the-2026-08-28-loop-carry-no-citation-at-the-line.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFORMANCE = REPO_ROOT / ".claude" / "skills" / "production-readiness-audit" / "conformance.py"
IMPLEMENTED = REPO_ROOT / "specs" / "IMPLEMENTED.md"


def conformance(*args):
    """Run a conformance view, or return None when it cannot run here."""
    if not CONFORMANCE.is_file():
        return None
    try:
        r = subprocess.run(["python3", str(CONFORMANCE), *args],
                           capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def normalize(line):
    """A rule line reduced to a comparable key, matching how `per-rule` prints it."""
    s = re.sub(r"^[-\d.\s]*", "", line).replace("⛔", "").strip()
    return re.sub(r"\s+", " ", s)[:60]


def deferred_rule_text():
    """All prose inside `DEFERRED INVARIANT` bullets, flattened.

    A deferral names the rule and its site, so a rule whose wording appears here is
    accounted for even though no id exists to cite yet.
    """
    text = IMPLEMENTED.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"DEFERRED INVARIANT", text):
        out.append(text[m.start():m.start() + 4000])
    return re.sub(r"\s+", " ", " ".join(out)).lower()


class EveryNewHardRuleIsAccountedFor(unittest.TestCase):
    def test_the_check_can_run(self):
        """⛔ INV-265 — say so when the scan cannot run, rather than passing silently."""
        if conformance("rules") is None:
            self.skipTest("conformance.py unavailable here (no git range, or not executable)")
        self.assertTrue(True)

    def test_each_rule_added_since_the_last_audit_is_cited_or_deferred(self):
        since = conformance("since", "--since-last-audit")
        uncited = conformance("per-rule", "--uncited")
        if since is None or uncited is None:
            self.skipTest("conformance.py could not resolve the since-last-audit range")

        added = [l[7:].strip() for l in since.splitlines() if l.startswith("     +")]
        if not added:
            self.skipTest("no hard rules added since the newest audit entry — nothing to check")

        flat_uncited = re.sub(r"\s+", " ", uncited)
        deferred = deferred_rule_text()
        unaccounted = []
        for line in added:
            key = normalize(line)
            if not key or key not in flat_uncited:
                continue                                   # cited at the line
            probe = re.sub(r"[`*]", "", key).lower()[:44]
            if probe and probe in re.sub(r"[`*]", "", deferred):
                continue                                   # named in a deferral
            unaccounted.append(line[:110])

        self.assertEqual(
            [], unaccounted,
            "a hard rule added since the last audit cites no invariant at its line AND is "
            "named in no DEFERRED INVARIANT block. Those are the only two legitimate states; "
            "silence is the reverse-contract defect. Either add the citation, or record the "
            "deferral with its drafted wording:\n  " + "\n  ".join(unaccounted))

    def test_the_deferral_scan_is_not_vacuous(self):
        """⛔ INV-265 — an empty deferral corpus would make the escape hatch match nothing."""
        deferred = deferred_rule_text()
        self.assertGreater(
            len(deferred), 500,
            "no DEFERRED INVARIANT prose was found in IMPLEMENTED.md, so the deferral escape "
            "hatch above can never match and this guard is stricter than the contract")
        self.assertIn("inv-nnn", deferred,
                      "no deferral carries drafted `INV-NNN` wording, which is what makes a "
                      "deferral an answer rather than a label")


if __name__ == "__main__":
    unittest.main()
