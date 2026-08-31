"""No step turns an absent `license_record_limit` into a finding about the license.

**INV-244 had one enforcer and it was scoped to one module.** `tests/test_module06_license_
reconciliation.py` pins the Module 6 Phase A and Phase B branches that raised the invariant —
and on 2026-08-28 a live walk found the identical defect in **SDK setup Step 5a**, which no
guard reached:

    Otherwise (only the built-in evaluation license is active), present this briefly:
    "Your Senzing SDK uses a built-in evaluation license … (limited to {record limit} records)"

Absence there is the *normal* state, so a Bootcamper whose installed license reported
`recordLimit: 0` — no cap at all — was told their limit was 500. The rule was registered,
documented with this exact scenario, and enforced at one site while the pattern survived at
another (`sdk-setup-step5a-reads-absence-as-the-built-in-license`).

⛔ **This guard derives its site set by scanning, never by listing (INV-246).** A listed guard
certifies the sites its author already thought of and is blind to the one that matters — which
is precisely how a Module-6-scoped guard let Module 2 ship the same branch.

⛔ **It asserts what must be TRUE, not what must not be said (INV-282, and the negatives rule).**
Every absence branch must either **measure** the value or mark its figure as an **assumption**.
A ban on the forbidden sentence cannot work here: every correct site quotes that sentence in
order to forbid it (*this means "never measured", not "no custom license"*), so a matcher hunting
the phrase flags the sites that get it right. The positive form has no such ambiguity, and it
fails on the real defect — the shipped Step 5a text stated a licensing conclusion with neither a
measurement nor an assumption marker, which is pinned as a fixture below.

Enforces **INV-244** plugin-wide.

Source spec: `specs/sdk-setup-step5a-reads-absence-as-the-built-in-license.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
FIELD = "license_record_limit"

#: ⛔ **The trigger is what the block TELLS THE BOOTCAMPER, not whether it says "absent".**
#: A first version keyed on an absence word in the same block and was wrong in both directions:
#: it flagged three correct passages that merely mention absence, and — measured against the
#: text that actually shipped — the defective paragraph does not contain the word at all. The
#: `Otherwise (only the built-in evaluation license is active)` condition sat in one block and
#: the note asserting 500 records in the next. Keying on the CAPACITY CLAIM catches the block
#: that does the damage, wherever its condition was written.
STATES_A_CAPACITY = re.compile(
    r"built-in evaluation license|evaluation license is active|no record cap|"
    r"\{record limit\}|limited to [^.]{0,24}records|record limit of", re.I)
#: Discharge 1 — the block takes the reading itself, or routes to the step that does.
MEASURES = re.compile(
    r"\bmeasure\b|\bmeasured\b|\bmeasurement\b|get_license|getlicense", re.I)
#: Discharge 2 — the block names its figure as unverified rather than detected.
#: ⛔ **"unavailable from the MCP server" was in this set and had to come out — it is why the
#: first version of this guard PASSED the mutation.** That sentence is about failing to fetch the
#: published figure, not about marking the Bootcamper-facing claim as unverified, and it sits in
#: the same branch as the defect. A discharge phrase that can be satisfied by neighboring
#: boilerplate certifies nothing; every phrase below has to be a statement ABOUT THE CLAIM.
ASSUMPTION = re.compile(
    r"\bassum\w+\b|recorded, not verified|could not be determined|cannot be determined|"
    r"not yet measured|never measured", re.I)
#: Discharge 3 — the block explicitly REFUSES the inference. Correct prose that names the
#: forbidden conclusion in order to ban it must not be flagged for containing it (INV-282);
#: this is the shape three sites use, and flagging them is how a guard gets relaxed.
DENIES = re.compile(
    r"never that no custom license|not \"?no custom license|says nothing about the installed "
    r"license|means it has not run|absent no matter wh(?:at|ich) license", re.I)


#: ⛔ **A branch is bounded by its OWN condition marker, not by its section.** Bounding by
#: section was tried and is worse than useless here: the shipped Step 5a section held a correct
#: reconciliation branch saying *"recorded, not verified"* directly above the defective
#: `Otherwise` branch, so a section-scoped check reads the sibling's discharge and certifies the
#: defect. Every marker below has actually shipped in this corpus (INV-282).
CONDITION = re.compile(
    r"^\s*[-*]?\s*\*\*Absent or null\*\*"
    r"|^\s*[-*]?\s*\*\*Present and\b"
    r"|^Otherwise\b|^\s*[-*]?\s*\*\*Otherwise\b"
    r"|^\*\*Only if\b|^\s*[-*]\s*\*\*Only if\b"
    r"|^\s*[-*]?\s*\*\*If a value\b",
    re.M)
#: ⛔ The subset that must discharge: a branch taken because nothing was measured. A **Present**
#: branch bounds a region but owes nothing — a present value IS the measurement (INV-278), and
#: requiring it to hedge would push correct prose toward the assumption language this forbids.
ABSENT_CONDITION = re.compile(
    r"^\s*[-*]?\s*\*\*Absent or null\*\*"
    r"|^Otherwise\b|^\s*[-*]?\s*\*\*Otherwise\b"
    r"|^\*\*Only if\b|^\s*[-*]\s*\*\*Only if\b"
    r"|^\s*[-*]?\s*\*\*If a value\b",
    re.M)
#: A heading ends a branch as surely as the next condition does.
HEADING = re.compile(r"^#{2,4} ", re.M)


def branch_regions(text):
    """Each branch, from its condition marker to the next condition or heading."""
    bounds = sorted({m.start() for m in CONDITION.finditer(text)}
                    | {m.start() for m in HEADING.finditer(text)})
    regions = []
    for i, s in enumerate(bounds):
        if not ABSENT_CONDITION.match(text, s):
            continue          # a heading, or a **Present** branch, bounds without opening one
        e = bounds[i + 1] if i + 1 < len(bounds) else len(text)
        regions.append(text[s:e])
    return regions


def field_files():
    """Every shipped file discussing the field — derived, not listed (INV-246)."""
    return sorted(p for p in PLUGIN.rglob("*.md")
                  if "__pycache__" not in p.parts and FIELD in p.read_text(encoding="utf-8"))


def absent_branches():
    """(file, region) for every branch taken because the value was not measured."""
    return [(p, r) for p in field_files()
            for r in branch_regions(p.read_text(encoding="utf-8"))]


def capacity_claims():
    """The subset that also tells the Bootcamper what their capacity is."""
    return [(p, r) for p, r in absent_branches() if STATES_A_CAPACITY.search(r)]


def is_discharged(region):
    return bool(MEASURES.search(region) or ASSUMPTION.search(region) or DENIES.search(region))


class NoAbsenceBranchAssertsALicensingFinding(unittest.TestCase):
    def test_branches_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        found = absent_branches()
        self.assertGreaterEqual(
            len(found), 6,
            "fewer than the known absence branches were found; the scan broke, the field was "
            f"renamed, or the branches moved. Found {len(found)}. ⚠️ This is a FLOOR, not a "
            "pinned count — branches may legitimately be added, and a count pinned exactly "
            "would have to be re-derived on every edit (which is the failure this field's "
            "sibling guard exists for)")
        modules = {p.parent.name for p, _ in found}
        self.assertGreaterEqual(
            len(modules), 3,
            f"the scan reaches only {sorted(modules)} — a guard that sees one module is how "
            "this defect shipped in the first place")

    def test_every_absence_branch_measures_or_marks_its_figure_as_an_assumption(self):
        bad = []
        for p, b in capacity_claims():
            if not is_discharged(b):
                bad.append(f"{p.relative_to(REPO_ROOT)}: {' '.join(b.split())[:220]}")
        self.assertEqual(
            [], bad,
            "a branch reasoning about an absent `license_record_limit` states a licensing "
            "conclusion without measuring it and without marking it as an assumption. Absence "
            "means NOT MEASURED (INV-244) — measure it, or say plainly that the figure is "
            "assumed and what could not be determined:\n  " + "\n  ".join(bad))

    def test_sdk_setup_reaches_the_scan(self):
        """⛔ The site the Module-6-scoped guard could not see, pinned by name."""
        files = {p for p, _ in capacity_claims()}
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        self.assertIn(m2, files,
                      "SDK setup is outside the absence-branch scan again — which is the exact "
                      "blind spot that let Step 5a tell an uncapped Bootcamper they had 500 "
                      "records")

    def test_the_check_fails_on_the_text_that_actually_shipped(self):
        """⛔ INV-265 — negative control, using the real defect rather than an invented one."""
        SHIPPED_DEFECT = (
            'Otherwise (only the built-in evaluation license is active), present this briefly '
            '— as a statement, **not a question:** "Your Senzing SDK uses a **built-in '
            'evaluation license** automatically when no custom license is present (limited to '
            '{record limit} records) — no license file needed."'
        )
        self.assertTrue(ABSENT_CONDITION.match(SHIPPED_DEFECT),
                        "the shipped defect's own `Otherwise` condition no longer opens a branch "
                        "region, so the scan would never reach it")
        self.assertTrue(STATES_A_CAPACITY.search(SHIPPED_DEFECT),
                        "the shipped defect no longer reads as a capacity claim to the scan, so "
                        "the scan would skip it")
        self.assertFalse(
            is_discharged(SHIPPED_DEFECT),
            "the discharge test now passes the exact text that shipped the defect — it has been "
            "widened until it certifies the thing it exists to catch")

    def test_the_check_passes_correct_branches(self):
        """The other half: prose that gets it right must not be flagged (INV-282)."""
        for ok in (
            'Absent or null — this means "never measured", not "no custom license": measure it '
            "before deciding anything about capacity.",
            "If the check cannot run, present the value as recorded, not verified, rather than "
            "as detected.",
            "This branch assumes the built-in capacity because nothing has measured the "
            "installed license yet, and says so.",
        ):
            with self.subTest(ok=ok[:48]):
                self.assertTrue(is_discharged(ok),
                                "correct prose is flagged, which is how a guard gets relaxed")


if __name__ == "__main__":
    unittest.main()
