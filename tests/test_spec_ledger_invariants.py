"""An implemented spec's guarantee must end up in INVARIANTS.md, or say it doesn't.

`specs/INVARIANTS.md` opens by describing itself as machine-extended: "as specs are
implemented, the guarantee a spec establishes becomes an invariant that all future work
must maintain." Nothing enforced that, and one spec slipped through.

`bootcamp-prep-name-never-asked` decided that the Bootcamper's name is detected silently
and never asked. It was implemented and ledgered in `specs/IMPLEMENTED.md` — and
registered no invariant. The guarantee therefore had no address, so two places reached for
the closest-looking ID and cited **INV-076**, which governs the Core-vs-Customized path
choice and says nothing about the name: INVARIANTS.md's own INV-113 parenthetical, and
`graduation/SKILL.md`. A wrong citation in the invariants file is worse than a missing
one, because it looks authoritative. Filed as INV-134 during the 2026-07-26 audit.

Two directions are pinned:

1. **Forward** — a spec implemented on or after the cutoff must either be cited as a
   `Source:` in INVARIANTS.md, name the invariant it established, or state plainly that
   it established none. Any of the three is fine; silence is not.
2. **Backward** — every `Source:` in INVARIANTS.md must name a spec that actually
   exists, so an invariant can never cite a phantom.

Entries before the cutoff are grandfathered deliberately: ~145 specs predate this test
and many are fixes that correctly establish nothing, so retrofitting a marker onto all of
them would be churn with no signal. The gate is forward-looking on purpose.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = REPO_ROOT / "specs"
IMPLEMENTED = SPECS / "IMPLEMENTED.md"
INVARIANTS = SPECS / "INVARIANTS.md"

# Entries implemented on or after this date must account for their invariants.
CUTOFF = "2026-07-26"

# Any of these in an entry's body discharges the obligation explicitly.
NO_INVARIANT_PHRASES = (
    "no new invariant",
    "establishes no invariant",
    "established no invariant",
)
ESTABLISHED_MARKERS = (
    "invariant established:",
    "new invariant inv-",
    "**invariant established**",
)

# Placeholder headings inside each file's own format comment, not real entries.
TEMPLATE_NAMES = {"<spec-name>"}

# Entries landed on the cutoff date itself, BEFORE this test existed. They are named
# individually rather than covered by a looser cutoff, so the exemption is auditable and
# cannot quietly widen. Each was reviewed as part of the 2026-07-26 audit; none is
# claimed here to have established an invariant either way. Do not add to this set —
# a new entry states its own answer instead.
GRANDFATHERED = frozenset(
    {
        "feedback-routing-plugin-vs-mcp-server",
        "audit-2-any-language-contract-and-windows-temp",
        "consolidate-truthset-viz-merges-and-network-tabs",
        "match-key-audit-cannot-read-related-entities-from-export",
        "core-path-enumerates-every-module",
    }
)


def flatten(text):
    """Collapse whitespace so a marker phrase still matches when prose wraps.

    Ledger bodies are hand-wrapped Markdown, so "establishes no new\\n  invariant" is the
    normal shape rather than the exception — matching raw substrings against it produced a
    false failure on the very first entry that used the phrase.
    """
    return re.sub(r"\s+", " ", text).lower()


def entries():
    """Yield (name, iso_date_or_None, body_text) for each ## entry in IMPLEMENTED.md."""
    text = IMPLEMENTED.read_text(encoding="utf-8")
    chunks = re.split(r"^## (?=\S)", text, flags=re.MULTILINE)[1:]
    for chunk in chunks:
        name, _, body = chunk.partition("\n")
        name = name.strip()
        if name in TEMPLATE_NAMES:
            continue
        m = re.search(r"\*\*Implemented:\*\*\s*(\d{4}-\d{2}-\d{2})", body)
        yield name, (m.group(1) if m else None), body


def invariant_sources():
    """Every spec name cited as a `Source:` by an invariant."""
    text = INVARIANTS.read_text(encoding="utf-8")
    return set(re.findall(r"Source:\s*`([^`]+)`", text)) - TEMPLATE_NAMES


class TestForwardCoverage(unittest.TestCase):
    """A newly implemented spec accounts for the invariant it established."""

    def test_recent_entries_account_for_their_invariants(self):
        sources = invariant_sources()
        unaccounted = []
        for name, date, body in entries():
            if date is None or date < CUTOFF:
                continue
            if name in GRANDFATHERED or name in sources:
                continue
            flat = flatten(body)
            if any(flatten(p) in flat for p in NO_INVARIANT_PHRASES):
                continue
            if any(flatten(p) in flat for p in ESTABLISHED_MARKERS):
                continue
            unaccounted.append(
                f"{name} (implemented {date}) is neither cited as a `Source:` in "
                "INVARIANTS.md, nor names the invariant it established, nor states "
                "that it established none"
            )
        self.assertEqual(
            [],
            unaccounted,
            "IMPLEMENTED.md entries whose guarantee has no recorded address — the "
            "defect that left the name-detection design citing INV-076:\n  "
            + "\n  ".join(unaccounted),
        )

    def test_the_cutoff_actually_covers_something(self):
        """A cutoff past the newest entry would make this test vacuous."""
        dated = [d for _, d, _ in entries() if d]
        self.assertTrue(dated, "no dated entries parsed — the parser has drifted")
        self.assertGreaterEqual(
            max(dated), CUTOFF, "CUTOFF is in the future; the forward gate checks nothing"
        )
        covered = [
            n for n, d, _ in entries() if d and d >= CUTOFF and n not in GRANDFATHERED
        ]
        self.assertTrue(
            covered,
            "every post-cutoff entry is grandfathered, so the gate checks nothing — "
            "grandfathering is for entries that predate this test, not new ones",
        )

    def test_grandfather_list_matches_real_entries(self):
        """A stale exemption silently widens the gate; a typo'd one does nothing."""
        names = {n for n, _, _ in entries()}
        self.assertEqual(
            set(),
            GRANDFATHERED - names,
            "GRANDFATHERED names an entry that no longer exists in IMPLEMENTED.md",
        )


class TestBackwardCoverage(unittest.TestCase):
    """An invariant may not cite a spec that does not exist."""

    def test_every_invariant_source_names_a_real_spec(self):
        ledgered = {name for name, _, _ in entries()}
        phantoms = []
        for source in sorted(invariant_sources()):
            if (SPECS / f"{source}.md").exists() or source in ledgered:
                continue
            phantoms.append(source)
        self.assertEqual(
            [],
            phantoms,
            "INVARIANTS.md cites spec(s) with no file under specs/ and no entry in "
            f"IMPLEMENTED.md: {phantoms}",
        )

    def test_inv_134_is_traceable_to_its_spec(self):
        """The specific hole this test was written for stays closed."""
        text = INVARIANTS.read_text(encoding="utf-8")
        self.assertRegex(text, r"\*\*INV-134\*\*", "INV-134 is missing")
        self.assertIn("bootcamp-prep-name-never-asked", invariant_sources())
        self.assertNotIn(
            "never asked (INV-076)",
            text,
            "the name-detection design is citing INV-076 again",
        )


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------------------
# Ledger-claim hygiene (deep-dive-audit-2026-07-29-minor-fixes, items 3 and 4).
#
# Two failures of the ledger AS EVIDENCE, both found by the 2026-07-29 audit:
#
#   Item 3 — 66 of 199 entries said `Commit: uncommitted` against a clean tree, so the
#   field could not answer the one question it exists for. They were backfilled from a
#   derived rule (the commit that added the entry's heading); this pins the field's shape
#   so free text cannot creep back in and staleness has a fixed vocabulary.
#
#   Item 4 — two specs were recorded as implemented with an acceptance criterion unmet
#   (`relocate-integration-deployment-questions-to-module1`, whose criterion named
#   graduation as a reader, and `defer-commonmark-to-graduation`, whose criterion named
#   the generated `production/*.md`). Both left an invariant standing unimplemented for
#   weeks. The commonest visible symptom is a spec predicting a file its ledger entry
#   never records changing, so that is what is gated here — forward-only.
#
# The affected-files gate is FORWARD-ONLY on purpose, exactly as TestForwardCoverage above
# is. A spec's `## Affected files` is a prediction and the entry's `Files changed:` is the
# outcome, so a gap is frequently legitimate (the change turned out not to need the file).
# 38 pre-cutoff entries carry one. Gating them retroactively would be a gate that cannot
# represent a legitimate input — the shape INV-144/INV-173 forbid — so the whole corpus is
# reported instead, by `.claude/skills/dry-run/coverage_reports.py affected`.
# ---------------------------------------------------------------------------------------

# Entries implemented on or after this date must account for their predicted files.
AFFECTED_CUTOFF = "2026-07-29"

# Entries landed on the cutoff date itself, BEFORE this gate existed — named individually
# so the exemption is auditable and cannot quietly widen, exactly as GRANDFATHERED above.
# Both were reviewed and both gaps are legitimate prediction-vs-outcome differences:
#
#   generators-warn-on-dropped-unencodable-characters — predicted `tests/test_discoveries_pdf.py`
#     but the entry explains the tests went to `test_recap_pdf_font_safety.py` instead ("one
#     shared collector"), and `bootcamp_data_discoveries.md` is a generated *project* file the
#     generator reads, never a repo file to change.
#   recap-new-line-labels-regression-tests — a tests-only spec whose whole point was that the
#     two generators already carried the behavior, so not touching them is the outcome.
#
# Do not add to this set: a new entry names its own files or says why it did not.
AFFECTED_GRANDFATHERED = frozenset(
    {
        "generators-warn-on-dropped-unencodable-characters",
        "recap-new-line-labels-regression-tests",
    }
)

COMMIT_FIELD = re.compile(r"^- \*\*Commit:\*\*(.*)$", re.M)
HASH = re.compile(r"`?\b[0-9a-f]{7,40}\b`?")
PATH_IN_TICKS = re.compile(
    r"`([A-Za-z0-9_./{}*-]+\.(?:md|py|sh|json|yaml|yml|js|png|pdf))`"
)


def predicted_paths(name):
    """Paths named in a spec's `## Affected files`, or None when there is no spec file."""
    spec = SPECS / f"{name}.md"
    if not spec.is_file():
        return None
    m = re.search(
        r"^## Affected files\s*$(.*?)(^## |\Z)",
        spec.read_text(encoding="utf-8"),
        re.M | re.S,
    )
    if not m:
        return []
    return sorted(set(PATH_IN_TICKS.findall(m.group(1))))


class TestCommitFieldHygiene(unittest.TestCase):
    """`Commit:` carries a hash, `uncommitted`, or `committed (hash not recorded)`."""

    def test_every_entry_has_a_commit_field(self):
        missing = [n for n, _, body in entries() if not COMMIT_FIELD.search(body)]
        self.assertEqual(
            [], missing, "IMPLEMENTED.md entries with no `Commit:` field:\n  "
            + "\n  ".join(missing)
        )

    def test_commit_fields_use_the_fixed_vocabulary(self):
        bad = []
        for name, _, body in entries():
            m = COMMIT_FIELD.search(body)
            if not m:
                continue
            value = m.group(1).strip()
            if HASH.search(value):
                continue
            if value in ("uncommitted", "`uncommitted`", "committed (hash not recorded)"):
                continue
            bad.append(f"{name}: {value!r}")
        self.assertEqual(
            [],
            bad,
            "`Commit:` must be a hash, `uncommitted`, or `committed (hash not "
            "recorded)` — free text makes the field unreadable:\n  " + "\n  ".join(bad),
        )


class TestAffectedFilesAccounting(unittest.TestCase):
    """A post-cutoff entry records what its spec predicted, or explains the difference."""

    def test_recent_entries_account_for_their_predicted_files(self):
        unaccounted = []
        for name, date, body in entries():
            if date is None or date < AFFECTED_CUTOFF:
                continue
            if name in AFFECTED_GRANDFATHERED:
                continue
            paths = predicted_paths(name)
            if not paths:
                continue
            for path in paths:
                # "Accounted for" is deliberately loose: the basename appearing anywhere
                # in the entry counts, so `Files changed:` naming it OR the Summary
                # explaining why it went untouched both pass. The gate is against
                # silence, not against a considered decision.
                if Path(path).name not in body:
                    unaccounted.append(f"{name} (implemented {date}) never mentions {path}")
        self.assertEqual(
            [],
            unaccounted,
            "A spec predicted a file and its ledger entry neither records changing it "
            "nor says why not — the shape that hid the graduation half of INV-097:\n  "
            + "\n  ".join(unaccounted),
        )

    def test_the_affected_cutoff_actually_covers_something(self):
        covered = [
            n for n, d, _ in entries()
            if d and d >= AFFECTED_CUTOFF
            and n not in AFFECTED_GRANDFATHERED and predicted_paths(n)
        ]
        self.assertTrue(
            covered,
            "no entry is on or after AFFECTED_CUTOFF with a spec that predicts files, "
            "so this gate checks nothing — grandfathering is for entries that predate "
            "this gate, not new ones",
        )

    def test_affected_grandfather_list_matches_real_entries(self):
        """A stale exemption silently widens the gate; a typo'd one does nothing."""
        names = {n for n, _, _ in entries()}
        self.assertEqual(
            set(),
            AFFECTED_GRANDFATHERED - names,
            "AFFECTED_GRANDFATHERED names an entry absent from IMPLEMENTED.md",
        )
