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


#: ⛔ The citation must be on the RULE'S OWN LINE, not merely near it.
#:
#: This check used to ask `conformance.py per-rule --uncited` whether a rule was cited, and
#: `per-rule` counts an invariant cited in the **sentence beside** a rule as citing it. That is
#: right for `per-rule`'s own question — can a reader at this line name the governing rule — and
#: wrong as an accounting test, because the neighbor's citation can be about something else.
#:
#: Found by the 2026-09-01 audit: `module-04-data-collection/SKILL.md:469` ships
#: ⛔ "Prefer `download_url` (MCP-hosted) over `source_download_url` for every CORD fetch" with no
#: invariant at its line and no deferral naming it, and this test passed — because the paragraph
#: two lines below reads "Observation, not an MCP-sourced fact (INV-080/INV-149)", which govern the
#: provenance of a 403 observation and say nothing about route preference. The reverse-contract
#: defense reported an unregistered guarantee as accounted for.
#:
#: ⚠️ `per-rule`'s own counting is deliberately NOT changed — every past ledger figure was measured
#: against it, and widening it would move a number nobody would re-measure. The guard is stricter
#: than the report instead.
#:
#: ⛔ And the check must run on the SOURCE line, not the reported one: `since` truncates its
#: display at 110 characters, so a citation past the cut is invisible. Checked against the
#: truncated text this flagged four rules that ARE cited — including a 638-character bullet
#: carrying INV-146 and INV-242 — which is the same truncation defect the 2026-09-01 audit
#: found in `test_conformance_sees_a_rule_beside_a_citation.py`, reintroduced here within the
#: hour by the fix for the audit's own finding.
INV_ON_THE_LINE = re.compile(r"INV-\d+")


def _comparable(text):
    """Both sides of the deferral match, reduced the same way.

    ⚠️ `normalize()` strips the ⛔ from a rule line; the deferral quotes the rule WITH it. For a
    rule whose ⛔ leads the line that still matched, because the probe was a substring of
    "⛔ <same text>". For a rule whose ⛔ sits mid-line — `- **6d (desired outcome).** ⛔ **This
    one is MULTI-select…** — the stop sign lands between the two halves of the probe and the
    match fails against a deferral that names the rule correctly. Strip it from both sides.
    """
    return re.sub(r"\s+", " ", re.sub(r"[`*⛔]", "", text)).lower().strip()


def source_lines(since_output):
    """[(relpath, full source line)] for every rule `since` reported.

    `since` prints a file heading followed by `     + <text>` lines truncated at 110
    characters. Resolve each back to the file so the citation check sees the whole line.
    """
    out, current = [], None
    for raw in since_output.splitlines():
        stripped = raw.strip()
        if stripped.startswith("plugins/") and stripped.endswith(".md"):
            current = stripped
        elif stripped.startswith("+ ") and current:
            body = stripped[2:]
            path = REPO_ROOT / current
            full = body
            if path.exists():
                for line in path.read_text(encoding="utf-8").split("\n"):
                    if line.startswith(body):
                        full = line
                        break
            out.append((current, full))
    return out


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

        added = source_lines(since)
        if not added:
            self.skipTest("no hard rules added since the newest audit entry — nothing to check")

        deferred = deferred_rule_text()
        unaccounted = []
        for _path, line in added:
            key = normalize(line)
            if not key:
                continue
            if INV_ON_THE_LINE.search(line):
                continue                                   # cited ON its own line
            probe = _comparable(key)[:44]
            if probe and probe in _comparable(deferred):
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
