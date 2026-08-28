"""`license_record_limit` has two writers, neither creates a value, and the fix persists.

`license-record-limit-has-a-detected-only-contract-nothing-enforces` told SDK setup to
*"take the measurement and say the recorded figure was withdrawn"* — which never said whether
to **write it down**. Both readings were wrong.

⛔ **Do not persist → the original defect survives the fix.** `config/bootcamp_progress.json`
keeps the false figure, and Module 4's Step 8a volume-skips its gate — *"If the collected
total is at or below the effective limit … Do not ask for a License Key"*. On the reported
numbers, a stated 100,000 against a measured 500 with a ~94,000-record collection, the single
volume-gated prompt in the bootcamp stays suppressed by the very number SDK setup had just
disproved.

⚠️ **Persist → two shipped files became false.** Both `phase1-discovery.md` and
`phaseA-build-loading.md` called Module 4 Step 8a the **only** writer, each using it as the
premise for an INV-244 absence branch. Those conclusions survive — the reconciliation fires
only on a value already present, so absence still means *not yet measured* — which is exactly
why the sentences needed correcting rather than dropping: the conclusion was right and the
stated reason was not, and a rule whose reason is wrong is one a later edit simplifies
incorrectly.

⚠️ **Root cause worth remembering:** the earlier fix added a second measurement point without
touching the single-writer contract three files shared. The two statements lived in the
*other* two modules, so a sweep for the field name finds them while a reader checking "did I
break the file I edited?" does not.

⚠️ What this does NOT establish: that Module 4's gate actually fires on those numbers. That is
end-to-end conversational behavior across three modules, unreachable offline (INV-108), and it
is the single most valuable thing a `dry-run` phase 3 could check here.

Source spec: `specs/sdk-setups-license-reconciliation-does-not-say-whether-to-persist.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
FIELD = "license_record_limit"
#: Wording that names a single writer of the field.
SOLE_WRITER = (
    r"the only writer of\s*`?license_record_limit",
    r"license_record_limit`? is\s*written only by",
    r"written only by module 4",
)


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def field_sites():
    """Every shipped file that reads or writes the field — derived, not listed (INV-246)."""
    return sorted(p for p in PLUGIN.rglob("*.md")
                  if "__pycache__" not in p.parts and FIELD in p.read_text(encoding="utf-8"))


class TheFieldHasTwoWritersAndNeitherCreatesOne(unittest.TestCase):
    def test_the_sites_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertGreaterEqual(
            len(field_sites()), 4,
            f"fewer than the known readers/writers of `{FIELD}` were found; the scan broke "
            "or the field was renamed")

    def test_no_shipped_file_claims_a_single_writer(self):
        bad = []
        for p in field_sites():
            flat = flatten(p.read_text(encoding="utf-8"))
            for pat in SOLE_WRITER:
                if re.search(pat, flat):
                    bad.append(f"{p.relative_to(REPO_ROOT)}: /{pat}/")
        self.assertEqual(
            [], bad,
            f"a shipped file calls one step the only writer of `{FIELD}`. SDK setup's Step 5a "
            "reconciliation writes it too, and each of these sentences is the premise for an "
            "INV-244 absence branch — so a false premise here is load-bearing:\n  "
            + "\n  ".join(bad))

    def test_every_absence_branch_names_both_writers(self):
        """⛔ Correcting the reason must not cost the conclusion INV-244 rests on.

        ⚠️ **Derived from the CONCLUSION, not from the correction.** An earlier version
        collected files that already carried the corrected sentence and required at least two
        — which meant deleting one of the three left the floor satisfied and passed its own
        negative control. The absence-branch conclusion is what identifies a site that owes
        the correction, so it is the thing to enumerate.

        ⚠️ Three sites phrase that conclusion three different ways. All three are listed: a
        regex fitted to one would pass the other two vacuously.
        """
        ABSENCE = re.compile(r"absence (?:here )?still means|"
                             r"absent no matter what license is installed|"
                             r"absence says nothing about the installed license")
        CORRECTED = re.compile(r"neither creates a value|never creates one")

        branches = [p for p in field_sites() if ABSENCE.search(flatten(p.read_text(
            encoding="utf-8")))]
        self.assertGreaterEqual(
            len(branches), 3,
            "fewer absence branches were found than the three known sites "
            "(phase1-discovery, phaseA-build-loading, phaseB-load-first-source). A branch "
            "whose conclusion was deleted rather than corrected disappears from this scan, "
            f"which is what the floor catches. Found: "
            f"{[str(p.relative_to(REPO_ROOT)) for p in branches]}")

        missing = [str(p.relative_to(REPO_ROOT)) for p in branches
                   if not CORRECTED.search(flatten(p.read_text(encoding="utf-8")))]
        self.assertEqual(
            [], missing,
            "an INV-244 absence branch states its conclusion without saying that neither "
            "writer creates a value — so the conclusion no longer follows from anything "
            "written down:\n  " + "\n  ".join(missing))

    def test_sdk_setup_persists_the_measurement(self):
        """⛔ The whole point: a correction that stays on screen leaves the gate suppressed."""
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        flat = flatten(m2.read_text(encoding="utf-8"))
        self.assertIn("write the measured value into `config/bootcamp_progress.json`", flat,
                      "SDK setup does not say to persist the measured value, so the false "
                      "figure survives and Module 4's gate stays volume-skipped")
        self.assertIn("persisting it is the point", flat,
                      "SDK setup does not say why persisting matters, so it reads as a detail "
                      "an editor can drop")

    def test_sdk_setup_never_writes_an_absent_field(self):
        """⛔ Creating a value here would break the branch INV-244 depends on."""
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        flat = flatten(m2.read_text(encoding="utf-8"))
        self.assertIn("never write this field when it is absent", flat,
                      "SDK setup does not rule out writing the field when absent, which would "
                      "turn a volume-gated measurement into an unconditional one")

    def test_the_gate_it_protects_is_still_described(self):
        """Anti-vacuity for the reason: the volume-skip must still exist to be worth protecting."""
        m4 = PLUGIN / "senzing-bootcamp" / "skills" / "module-04-data-collection" / "SKILL.md"
        flat = flatten(m4.read_text(encoding="utf-8"))
        self.assertIn("at or below the effective limit", flat,
                      "Module 4's volume-skip is gone; if the gate no longer reads this field, "
                      "re-derive whether persisting still matters before relaxing anything")


if __name__ == "__main__":
    unittest.main()
