"""`license_record_limit` is written only from a measurement, and no file counts its writers.

Three shipped files state why an absent `license_record_limit` says nothing about the
installed license. Each used to justify that with a **count of writers**, and the count was
wrong in every version it had:

- *"the only writer … is Module 4's Step 8a"* — false; Module 4 has a second write of its own,
  and Module 6's Phase A and Phase B absent branches each measure and persist too.
- *"exactly two writers, and neither creates a value where none existed"* (`885a992`) — also
  false, and **self-contradicted four lines below itself**: the same bullet then says
  *"Persist it as `license_record_limit`"*.

The real set is five write sites across four steps. ⛔ **But the conclusion never needed a
count.** What makes absence informative is that **no step writes this field without measuring
it** — a property that held before either correction and will hold when a sixth writer
appears. A count is a proxy that has to be re-derived whenever the code moves, goes stale
silently, and reads authoritative while wrong.

⚠️ **The same defect occurred twice in one day, by the same mechanism.** The first version
inherited a stale count; the second **minted a fresh one while fixing the first**, in a spec
whose whole subject was that the writer set had changed — and the guard written alongside it
(this file, under its former name `test_license_limit_has_exactly_two_writers.py`) pinned the
new wrong number into the suite. **Replacing one enumeration with another is not a fix**, and
a guard named for the wrong claim keeps the wrong claim alive in every future grep, which is
why the rename is part of the fix rather than tidying.

⚠️ What this does NOT establish: that a live run measures before writing. That is turn-level
behavior no offline suite can assert (INV-108).

Source spec: `specs/counting-the-writers-of-license-record-limit-is-the-wrong-invariant.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
FIELD = "license_record_limit"

#: Any sentence that states HOW MANY steps write the field. All of these have shipped.
WRITER_COUNT = (
    r"the only writer of\s*`?license_record_limit",
    r"license_record_limit`? is\s*written only by",
    r"written only by module 4",
    r"(?:has|is written by)\s*(?:exactly\s*)?(?:one|two|three|four|five|\d+)\s*writers?",
    r"(?:exactly\s*)?(?:one|two|three|four|five|\d+)\s*(?:steps?|writers?)\s*writes?\b",
)
#: The property the conclusion actually rests on.
MEASURED_ONLY = re.compile(
    r"writes only a measured value|written only from a measured license|"
    r"writes it from an assumption")
#: Each site's own phrasing of the conclusion the property supports.
ABSENCE = re.compile(r"absence still means|absent no matter what license is installed|"
                     r"absence says nothing about the installed license")


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def field_sites():
    """Every shipped file that reads or writes the field — derived, not listed (INV-246)."""
    return sorted(p for p in PLUGIN.rglob("*.md")
                  if "__pycache__" not in p.parts and FIELD in p.read_text(encoding="utf-8"))


class TheFieldIsWrittenOnlyFromAMeasurement(unittest.TestCase):
    def test_the_sites_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertGreaterEqual(
            len(field_sites()), 4,
            f"fewer than the known readers/writers of `{FIELD}` were found; the scan broke "
            "or the field was renamed")

    def test_no_shipped_file_counts_the_writers(self):
        """⛔ The point of this spec: a count is the wrong shape, at any value."""
        bad = []
        for p in field_sites():
            flat = flatten(p.read_text(encoding="utf-8"))
            for pat in WRITER_COUNT:
                m = re.search(pat, flat)
                if m:
                    bad.append(f"{p.relative_to(REPO_ROOT)}: /{pat}/ -> "
                               f"...{flat[max(0, m.start() - 50):m.end() + 50]}...")
        self.assertEqual(
            [], bad,
            f"a shipped file states how many steps write `{FIELD}`. That number has been "
            "wrong in every version it has had, and the conclusion does not rest on it — "
            "state the measured-only property instead:\n  " + "\n  ".join(bad))

    def test_every_absence_branch_states_the_measured_only_property(self):
        """Derived from the CONCLUSION — the sites that OWE the property, not those that have it.

        ⚠️ An earlier version enumerated the files already carrying the fix and required a
        floor, so deleting one of three left the floor satisfied and it passed its own
        negative control.
        """
        branches = [p for p in field_sites()
                    if ABSENCE.search(flatten(p.read_text(encoding="utf-8")))]
        self.assertGreaterEqual(
            len(branches), 3,
            "fewer absence branches were found than the three known sites; one whose "
            "conclusion was deleted rather than corrected disappears from this scan. Found: "
            f"{[str(p.relative_to(REPO_ROOT)) for p in branches]}")
        missing = [str(p.relative_to(REPO_ROOT)) for p in branches
                   if not MEASURED_ONLY.search(flatten(p.read_text(encoding="utf-8")))]
        self.assertEqual(
            [], missing,
            "an INV-244 absence branch draws its conclusion without stating the measured-only "
            "property it rests on:\n  " + "\n  ".join(missing))

    def test_the_replace_only_distinction_survives(self):
        """Not a count — the one writer that never creates a value, which Module 1 relies on."""
        m1 = PLUGIN / "senzing-bootcamp" / "skills" / "module-01-business-problem" / "phase1-discovery.md"
        flat = flatten(m1.read_text(encoding="utf-8"))
        self.assertIn("only ever **replaces** an already-recorded value".lower().replace("**", ""),
                      flat.replace("**", ""),
                      "Module 1 no longer says the reconciliation only replaces and never "
                      "creates — which is what makes its absence reasoning hold")

    def test_sdk_setup_persists_and_never_creates(self):
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        flat = flatten(m2.read_text(encoding="utf-8"))
        self.assertIn("write the measured value into `config/bootcamp_progress.json`", flat,
                      "SDK setup does not persist the measured value, so a corrected figure "
                      "stays on screen and Module 4's gate remains volume-skipped")
        self.assertIn("never write this field when it is absent", flat,
                      "SDK setup does not rule out creating the field when absent")

    def test_the_gate_it_protects_is_still_described(self):
        """Anti-vacuity for the reason: the volume-skip must exist to be worth protecting."""
        m4 = PLUGIN / "senzing-bootcamp" / "skills" / "module-04-data-collection" / "SKILL.md"
        self.assertIn("at or below the effective limit",
                      flatten(m4.read_text(encoding="utf-8")),
                      "Module 4's volume-skip is gone; re-derive whether persisting still "
                      "matters before relaxing anything here")

    def test_the_count_matcher_is_not_vacuous(self):
        """⛔ INV-265 — prove it still detects every count that has actually shipped."""
        for planted in ("the only writer of `license_record_limit` is Module 4",
                        "`license_record_limit` is written only by Module 4's Step 8a",
                        "it has exactly two writers, and neither creates a value",
                        "the field has five writers"):
            with self.subTest(planted=planted):
                flat = flatten(planted)
                self.assertTrue(any(re.search(p, flat) for p in WRITER_COUNT),
                                "the count matcher no longer detects a shipped phrasing")
        for ok in ("every step that writes it writes only a measured value",
                   "SDK setup's Step 5a reconciliation only ever replaces an already-recorded "
                   "value and never creates one"):
            with self.subTest(ok=ok):
                flat = flatten(ok)
                self.assertFalse(any(re.search(p, flat) for p in WRITER_COUNT),
                                 "the count matcher flags the property wording it exists to "
                                 "make room for")


if __name__ == "__main__":
    unittest.main()
