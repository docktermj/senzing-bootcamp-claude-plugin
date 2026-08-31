"""`license_record_limit` is written only from a measurement, and no file counts its writers.

Three shipped files state why an absent `license_record_limit` says nothing about the
installed license. Each used to justify that with a **count of writers**, and the count was
wrong in every version it had:

- *"the only writer … is Module 4's Step 8a"* — false; Module 4 has a second write of its own,
  and Module 6's Phase A and Phase B absent branches each measure and persist too.
- *"exactly two writers, and neither creates a value where none existed"* (`885a992`) — also
  false, and **self-contradicted four lines below itself**: the same bullet then says
  *"Persist it as `license_record_limit`"*.

⛔ **But the conclusion never needed a count.** What makes absence informative is that **no step
writes this field without measuring it** — a property that held before either correction and holds
now that SDK setup's Step 5a has been added as a writer (2026-08-31,
`sdk-setup-step5a-reads-absence-as-the-built-in-license`). A count is a proxy that has to be
re-derived whenever the code moves, goes stale silently, and reads authoritative while wrong —
which is why **this docstring no longer carries one either**: the version that did said "five
write sites across four steps", and Step 5a made it wrong three days later, exactly as predicted
one sentence above.

⛔ **INV-282 governs this file's matchers.** A guard derives its matcher from the CLAIM being
made, not from the phrasings observed at the sites it was written to fix; every phrasing that
has shipped is pinned as a fixture, and every construction the matcher must NOT flag is pinned
beside it.

⚠️ **The same defect occurred twice in one day, by the same mechanism.** The first version
inherited a stale count; the second **minted a fresh one while fixing the first**, in a spec
whose whole subject was that the writer set had changed — and the guard written alongside it
(this file, under its former name `test_license_limit_has_exactly_two_writers.py`) pinned the
new wrong number into the suite. **Replacing one enumeration with another is not a fix**, and
a guard named for the wrong claim keeps the wrong claim alive in every future grep, which is
why the rename is part of the fix rather than tidying.

⚠️ What this does NOT establish: that a live run measures before writing. That is turn-level
behavior no offline suite can assert (INV-108).

Enforces **INV-278** — a state field whose authority rests on being measured is written only from that measurement,
presence is not proof of it, and a reconciling step persists what it measures.

Source spec: `specs/counting-the-writers-of-license-record-limit-is-the-wrong-invariant.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
FIELD = "license_record_limit"

#: A writer-count claim, matched by the CLAIM rather than by phrasings already seen.
#: ⚠️ **No requirement that the field name be adjacent.** Two sites survived the first
#: version of this matcher by using an anaphor — "its only writer", "the field's only
#: writer" — with the subject established a sentence earlier, which is the normal way to
#: write the second sentence about a subject. Scoping is by FILE (it discusses the field),
#: not by proximity within the sentence.
#: ⛔ Deliberately NOT a corpus-wide ban on the word "only": that would fire on unrelated
#: correct prose and be relaxed within a week, which is worse than the gap.
WRITER_COUNT = (
    # ⚠️ The negative lookbehind excludes a compound adjective: "a stdlib-only writer"
    # is a real string in this repo and states no writer count. Matching it would push an
    # editor into deleting correct prose, which is the failure mode opposite to the one
    # this guard exists for.
    r"(?:its|the field's|the|a)\s+(?<![-\w])only\s+writer\b",
    r"(?:its|the field's)\s+only\s+writer\b",
    r"\bsole\s+writer\b",
    r"is\s+written\s+only\s+by",
    r"written only by module 4",
    r"(?:has|have|is written by)\s*(?:exactly\s*)?(?:one|two|three|four|five|\d+)\s*writers?",
    r"(?:exactly\s*)?(?:one|two|three|four|five|\d+)\s*(?:steps?|writers?)\s*writes?\b",
)
#: The property the conclusion actually rests on.
MEASURED_ONLY = re.compile(
    r"writes only a measured value|written only from a measured license|"
    r"writes it from an assumption")
#: Each site's own phrasing of the conclusion the property supports.
#: An `Absent or null` branch bullet — the genuinely structural marker, and the one a new
#: module adding this branch will carry.
ABSENT_BULLET = re.compile(r"-\s*absent or null\b")
#: The conclusion those branches draw, matched at the CONCEPT level rather than as a list of
#: literal sentences: absence tells you nothing about the installed license.
ABSENCE_CONCLUSION = re.compile(
    r"absence (?:here )?still means|absent no matter wh(?:at|ich) license is installed|"
    r"absence says nothing about the installed license")
#: Sites known to reason about the field being absent, as of 2026-08-28. The floor exists so
#: a branch DISAPPEARING fails rather than passing quietly (INV-265).
KNOWN_BRANCHES = 4


def flatten(text):
    """Whitespace-collapsed, emphasis-stripped, lowercased.

    ⛔ **Stripping `*` and backticks is load-bearing, not cosmetic.** A matcher written
    against a phrase is otherwise sensitive to where an author put emphasis: three sites
    wrote the property with the whole phrase bolded, so the substring survived, and one
    bolded a single word inside it, so it did not. The property was present at all four and
    the matcher saw three.

    ⚠️ **`_` is deliberately NOT stripped.** It is an identifier character throughout this
    repo — license_record_limit, bootcamp_progress.json — and removing it yields
    licenserecordlimit and bootcampprogress.json, breaking every needle that names one.
    Underscore-italics are not used in this corpus, so the trade is not close.
    """
    return re.sub(r"[*`]", "", re.sub(r"\s+", " ", text)).lower()


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
        """Every site reasoning about the field being ABSENT states the property it rests on.

        ⚠️ **The branch set is a union of two markers, because the sites are two kinds.**
        Three are `- **Absent or null**` bullets — genuinely structural, and what a new
        module adding this branch will carry. The fourth, Module 1's Step 5a comparison, is
        not a bullet at all: it reasons about the field being absent inside a threshold
        check. Deriving from the bullet alone silently drops it, which is the same
        one-blind-spot-for-another trade this guard was rewritten to stop.

        ⛔ **Module 2 is deliberately NOT a branch.** Its reconciliation mentions absence —
        *"Never write this field when it is ABSENT"* — while being the **writer**, not a
        reader drawing the not-yet-measured conclusion. A file-level "mentions INV-244 and
        absence" derivation collects it and was rejected for that reason.
        """
        branches = [p for p in field_sites()
                    if ABSENT_BULLET.search(flatten(p.read_text(encoding="utf-8")))
                    or ABSENCE_CONCLUSION.search(flatten(p.read_text(encoding="utf-8")))]
        names = sorted(str(p.relative_to(REPO_ROOT)) for p in branches)
        self.assertGreaterEqual(
            len(branches), KNOWN_BRANCHES,
            f"fewer than the {KNOWN_BRANCHES} known absence branches were found. A branch "
            "that lost its conclusion AND its bullet disappears from this scan rather than "
            f"failing, which is what this floor catches. Found: {names}")
        missing = [str(p.relative_to(REPO_ROOT)) for p in branches
                   if not MEASURED_ONLY.search(flatten(p.read_text(encoding="utf-8")))]
        self.assertEqual(
            [], missing,
            "a site reasoning about an absent `license_record_limit` does not state the "
            "measured-only property its conclusion rests on:\n  " + "\n  ".join(missing))

    def test_the_branch_scan_reaches_the_bullet_only_site(self):
        """⛔ The site that motivated this rewrite, pinned by name.

        `module-04-data-collection/SKILL.md` says *"absent no matter **which** license is
        installed"* where the others say *"what"*, and bolds `**measured**` inside the
        property phrase rather than around it. One word and one asterisk pair put it outside
        both of the previous matchers at once, so the two defects hid each other.
        """
        m4 = PLUGIN / "senzing-bootcamp" / "skills" / "module-04-data-collection" / "SKILL.md"
        flat = flatten(m4.read_text(encoding="utf-8"))
        self.assertTrue(ABSENT_BULLET.search(flat) or ABSENCE_CONCLUSION.search(flat),
                        "module-04's absence branch is outside the branch scan again")
        self.assertTrue(MEASURED_ONLY.search(flat),
                        "module-04's absence branch does not state the measured-only "
                        "property — or flatten() stopped stripping emphasis")

    def test_emphasis_does_not_hide_the_property(self):
        """⛔ INV-265 — the exact markup that defeated the previous matcher."""
        for markup in ("writes only a **measured** value",
                       "**writes only a measured value**",
                       "writes only a `measured` value"):
            with self.subTest(markup=markup):
                self.assertTrue(MEASURED_ONLY.search(flatten(markup)),
                                "flatten() no longer strips emphasis, so the matcher is "
                                "sensitive to where an author put asterisks")
        # ⚠️ `_measured_` is deliberately NOT supported: stripping `_` would turn
        # license_record_limit into licenserecordlimit and break every needle naming a
        # field. Underscore-italics are not used in this corpus. Pinned as a known
        # limitation rather than left as an untested assumption.
        self.assertIsNone(
            MEASURED_ONLY.search(flatten("writes only a _measured_ value")),
            "underscore emphasis now matches — if that was intentional, confirm no needle "
            "in this file names an identifier containing an underscore")

    def test_module_1_justifies_its_assumption_by_ORDER_not_by_the_writer_set(self):
        """What makes Module 1's built-in assumption sound, restated when Step 5a became a writer.

        ⚠️ **This assertion used to read the other way round.** Until 2026-08-31 Module 1 said
        *"SDK setup's Step 5a reconciliation only ever replaces an already-recorded value and
        never creates one, so nothing before Module 4's volume-gated gate can put a figure in
        this field at all"* — true then, and false the moment Step 5a began measuring and
        persisting (`sdk-setup-step5a-reads-absence-as-the-built-in-license`). The conclusion
        Module 1 needs is unchanged and still holds, but it now rests on **order**: SDK setup is
        Module 2, so at Module 1 no step that measures has run yet.

        ⛔ The old needle is pinned in the must-NOT-match set below, because a revert to the
        superseded sentence is the specific regression this replaces.
        """
        m1 = PLUGIN / "senzing-bootcamp" / "skills" / "module-01-business-problem" / "phase1-discovery.md"
        flat = flatten(m1.read_text(encoding="utf-8"))
        self.assertIn("the first step that measures the license is sdk setup's step 5a", flat,
                      "Module 1 no longer names the first measuring step, which is what makes "
                      "its absence reasoning hold now that Step 5a writes the field")
        self.assertIn("sdk setup has not run yet at this point", flat,
                      "Module 1 no longer says WHY that first measurement cannot have happened "
                      "yet — order is the whole justification for assuming the built-in figure")
        self.assertNotIn("only ever replaces an already-recorded value", flat,
                         "Module 1 has gone back to the superseded claim that SDK setup never "
                         "creates this field. Step 5a measures and persists it — re-read "
                         "module-02-sdk-setup/SKILL.md Step 5a before restoring that sentence")

    def test_sdk_setup_measures_persists_and_writes_nothing_when_it_cannot(self):
        """SDK setup Step 5a: measure, persist what was measured, write nothing otherwise.

        ⚠️ **The second assertion used to require the opposite rule.** Until 2026-08-31 Step 5a
        was forbidden to write the field at all when it was absent — correct while the step only
        *reconciled* an existing value, and the reason a Bootcamper with an uncapped license was
        told they were limited to 500 records. The maintainer's decision on
        `sdk-setup-step5a-reads-absence-as-the-built-in-license` was to **persist**, so the
        protection moves rather than disappears: what must never reach this field is an
        UNMEASURED value, which is now stated as "when the measurement cannot run, write nothing".
        """
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        flat = flatten(m2.read_text(encoding="utf-8"))
        self.assertIn("write the measured value into config/bootcamp_progress.json", flat,
                      "SDK setup does not persist the measured value, so a corrected figure "
                      "stays on screen and Module 4's gate remains volume-skipped")
        self.assertIn("when the measurement cannot run, write nothing", flat,
                      "SDK setup no longer rules out writing this field on the branch where "
                      "nothing was measured — which is the only thing keeping an absent "
                      "`license_record_limit` meaningful (INV-244)")
        self.assertIn("measure the license here", flat,
                      "SDK setup Step 5a no longer takes the measurement at all; it is the "
                      "first step where the SDK is verified and the reading is possible")

    def test_the_gate_it_protects_is_still_described(self):
        """Anti-vacuity for the reason: the volume-skip must exist to be worth protecting."""
        m4 = PLUGIN / "senzing-bootcamp" / "skills" / "module-04-data-collection" / "SKILL.md"
        self.assertIn("at or below the effective limit",
                      flatten(m4.read_text(encoding="utf-8")),
                      "Module 4's volume-skip is gone; re-derive whether persisting still "
                      "matters before relaxing anything here")

    def test_the_count_matcher_is_not_vacuous(self):
        """⛔ INV-265 — pin every phrasing that has ACTUALLY shipped, not a sample of them.

        Six have. The last two are the anaphoric pair that survived the first version of this
        matcher, and they are fixtures here rather than a memory precisely because that is
        how the blind spot recurred.
        """
        SHIPPED = (
            "the only writer of `license_record_limit` is Module 4",
            "`license_record_limit` is written only by Module 4's Step 8a",
            "written only by Module 4's volume-gated Step 8a",
            "it has exactly two writers, and neither creates a value",
            "Module 4 Step 8a is its only writer, and a second SDK call",
            "The field's only writer is Step 8a below, which is volume-gated",
        )
        for planted in SHIPPED:
            with self.subTest(planted=planted[:46]):
                flat = flatten(planted)
                self.assertTrue(any(re.search(p, flat) for p in WRITER_COUNT),
                                "the count matcher no longer detects a phrasing that has "
                                "actually shipped in this repo")
        for ok in ("every step that writes it writes only a measured value",
                   "the first step that measures the license is SDK setup's Step 5a",
                   "a stdlib-only writer when it is absent",
                   "the value you would be re-deriving was already measured and persisted"):
            with self.subTest(ok=ok[:46]):
                flat = flatten(ok)
                self.assertFalse(any(re.search(p, flat) for p in WRITER_COUNT),
                                 "the count matcher flags prose that states no writer count, "
                                 "which would push an editor into deleting correct text")


if __name__ == "__main__":
    unittest.main()
