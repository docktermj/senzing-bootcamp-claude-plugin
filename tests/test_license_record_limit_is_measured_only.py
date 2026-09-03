"""`license_record_limit` is written only from a measurement, and presence is not proof.

The field INV-244 makes authoritative is authoritative **because it is measured**. Its
contract was stated descriptively in two places and enforced in neither, so a value that
was never measured could occupy it and be believed downstream.

Observed 2026-08-25: a Bootcamper said their POC license allowed 100,000 records; the guide
wrote `license_record_limit: 100000` on the strength of the statement. SDK setup then ran
the authoritative `GetLicense` snippet against the freshly installed SDK and got
`recordLimit: 500`, `licenseType: "EVAL (Solely for non-productive use)"` — the built-in
evaluation license. The POC key had never been applied to that install.

⛔ **The consequence is a suppressed warning, not a wrong number.** A `license_record_limit`
above the dataset size **suppresses** Module 4's Step 8a License Key gate — the single
volume-gated prompt in the bootcamp, and the one thing that warns before hitting the cap
mid-load. A fabricated 100,000 against a real 500, on a ~94,000-record scenario, removes it.
This is INV-244 from the other side: that invariant forbids reading *absence* as "no
license"; nothing forbade treating a *present but unmeasured* value as a measurement.

⚠️ **The spec named one inference site. There were two.** Module 2's Step 5a guard said the
limit "was detected earlier", and Module 1's Step 5a read said the field is "present only if
a custom license was configured in a prior session". Both inferred detection from presence,
and a guard written from the spec's file list would have fixed one and certified the other
(INV-246).

⚠️ What this does NOT establish: that a live run refuses to write the field from a
statement, or that SDK setup actually reconciles. Both are turn-level behaviors no offline
suite can assert (INV-108); they need a `dry-run` phase-3 walk.

Source spec: `specs/license-record-limit-has-a-detected-only-contract-nothing-enforces.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
FIELD = "license_record_limit"
STATED = "license_stated_limit"
#: Wording that infers detection from the field merely being present.
PRESENCE_AS_PROOF = (
    r"was detected earlier",
    r"present only if a custom license was configured",
    r"a custom license has already been configured",
)


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def field_sites():
    """Every shipped file that reads or writes the measured limit — derived, not listed."""
    return sorted(p for p in PLUGIN.rglob("*.md")
                  if "__pycache__" not in p.parts and FIELD in p.read_text(encoding="utf-8"))


class NoSiteInfersDetectionFromPresence(unittest.TestCase):
    def test_the_sites_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        sites = field_sites()
        self.assertGreaterEqual(
            len(sites), 4,
            f"fewer than the known readers/writers of `{FIELD}` were found; the scan broke "
            f"or the field was renamed. Found: {[str(p.name) for p in sites]}")

    def test_no_shipped_file_treats_presence_as_proof_of_detection(self):
        bad = []
        for p in field_sites():
            flat = flatten(p.read_text(encoding="utf-8"))
            for pat in PRESENCE_AS_PROOF:
                if re.search(pat, flat):
                    bad.append(f"{p.relative_to(REPO_ROOT)}: /{pat}/")
        self.assertEqual(
            [], bad,
            f"a shipped file infers that `{FIELD}` was MEASURED from the fact that it is "
            "PRESENT. It can be written from a Bootcamper statement, so presence proves "
            "nothing — and a value above the dataset size suppresses the Step 8a gate:\n  "
            + "\n  ".join(bad))

    def test_the_write_prohibition_is_stated(self):
        """Stated as a prohibition, not as an explanation of the absent branch."""
        stating = [p for p in field_sites()
                   if re.search(r"written only from a measured license", flatten(
                       p.read_text(encoding="utf-8")))]
        self.assertTrue(
            stating,
            f"no shipped file forbids writing `{FIELD}` from a Bootcamper statement. The "
            "contract being described elsewhere is not the same as it being forbidden here")

    def test_a_stated_entitlement_has_its_own_key_in_a_different_file(self):
        holders = [p for p in field_sites() if STATED in p.read_text(encoding="utf-8")]
        self.assertTrue(
            holders, f"no shipped file names `{STATED}`, so a Bootcamper's claimed limit has "
                     f"nowhere to go but `{FIELD}` — which is how this defect happened")
        flat = flatten(holders[0].read_text(encoding="utf-8"))
        self.assertIn("bootcamp_preferences.yaml", flat,
                      "the stated key must live in preferences, a different file from the "
                      "measured field, so the two cannot be confused by proximity")
        i = flat.index(STATED)
        self.assertIn("no gate reads it", flat[i:i + 400],
                      "the stated key is introduced without saying no gate reads it, which "
                      "is the only thing keeping it from becoming a second source of truth")

    def test_sdk_setup_reconciles_rather_than_asserting(self):
        """Step 5a is the first point where the SDK exists and the license can be measured."""
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        flat = flatten(m2.read_text(encoding="utf-8"))
        self.assertIn("presence is not proof of detection", flat,
                      "SDK setup's already-licensed guard does not say presence is not proof")
        self.assertIn("recorded, not verified", flat,
                      "SDK setup gives no fallback wording for when the check cannot run, so "
                      "an unverified value is still presented as detected")

    def test_inv244_is_cited_where_the_prohibition_is_stated(self):
        """INV-183 — the governing rule must be nameable at the step."""
        stating = [p for p in field_sites()
                   if "written only from a measured license" in flatten(
                       p.read_text(encoding="utf-8"))]
        for p in stating:
            flat = flatten(p.read_text(encoding="utf-8"))
            i = flat.index("written only from a measured license")
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertIn("inv-244", flat[max(0, i - 200):i + 1600],
                              "the prohibition does not cite INV-244, whose rule it extends")


if __name__ == "__main__":
    unittest.main()
