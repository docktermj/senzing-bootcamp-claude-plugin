"""A step that frames licensing consults the measured limit, not the preferences key.

`phaseA-build-loading.md` had two decision points over one fact, thirty lines apart,
keyed on **different state**, giving **opposite answers** for the same bootcamper:

- **Step 1's license framing** keyed on `license` in `config/bootcamp_preferences.yaml`
  and, finding it unset, framed the built-in evaluation license as the default and
  offered three ways to expand capacity.
- **The reconciliation block** keyed on `license_record_limit` in
  `config/bootcamp_progress.json` — the field INV-244 makes authoritative because it is
  *measured* from `SzProduct.get_license()` — and on `0` said to **"suppress it
  entirely: say nothing about licenses or sampling ... A warning the bootcamper cannot
  act on is noise (INV-012)."**

⛔ **The two states come apart on the ordinary path, and did.** Observed 2026-08-27
walking the module: `license` unset, `license_record_limit: 0` (measured, no cap). Step 1
therefore delivered exactly the output the block below it calls noise. The states diverge
because `license` is written only by Module 4 Step 8a's *apply* or *obtain* paths, while
`license_record_limit` is written by its *measurement* — so anyone who simply has a good
license already installed gets the measurement and never gets the key. That is the normal
case for a corporate or internal license, not an edge case.

⚠️ **The reconciliation block was right and is deliberately left alone.** It cites INV-244
and INV-012 and walks the absent/null → measure → re-enter path correctly. The defect was
that Step 1 predated the measurement discipline and never picked it up.

⚠️ What this does NOT establish: that a live run suppresses the framing. These are text
assertions over shipped markdown; whether a guide obeys them is a runtime property the
offline suite cannot see (INV-108).

Source spec: `specs/step1-license-framing-ignores-the-measured-record-limit.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"

MEASURED = "license_record_limit"
PREF_KEY = "bootcamp_preferences.yaml"
#: Wording that offers to expand or downsize capacity -- i.e. licensing framing, the thing
#: that must not fire for an unconstrained bootcamper.
FRAMING = (
    r"expansion path",
    r"built-in evaluation license as the default",
    r"before any mention of downsizing",
)


def shipped_markdown():
    return sorted(p for p in PLUGIN.rglob("*.md") if "__pycache__" not in p.parts)


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def framing_files():
    """Every shipped file that frames licensing capacity -- derived, never hardcoded.

    INV-246: the spec named one file. A guard that named it too would certify the site
    already known and stay blind to a second step that grows the same framing later.
    """
    out = []
    for p in shipped_markdown():
        flat = flatten(p.read_text(encoding="utf-8"))
        if any(re.search(f, flat) for f in FRAMING):
            out.append(p)
    return out


class EveryLicenseFramingSiteConsultsTheMeasuredLimit(unittest.TestCase):
    def test_the_framing_sites_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertTrue(
            framing_files(),
            "no shipped file frames licensing capacity any more; either the vocabulary "
            "moved or the scan broke. Re-derive FRAMING rather than deleting this guard")

    def test_each_framing_site_reads_the_measured_limit(self):
        bad = [str(p.relative_to(REPO_ROOT)) for p in framing_files()
               if MEASURED not in p.read_text(encoding="utf-8")]
        self.assertEqual(
            [], bad,
            "a step frames licensing capacity without consulting the measured "
            f"`{MEASURED}`. An uncapped bootcamper is then handed expansion paths for a "
            "constraint they do not have — the INV-012 noise the reconciliation block "
            f"forbids by name:\n  " + "\n  ".join(bad))

    def test_the_preferences_key_is_not_the_gate(self):
        """`license` records HOW a license was obtained; it never decides WHETHER one binds."""
        for p in framing_files():
            flat = flatten(p.read_text(encoding="utf-8"))
            if PREF_KEY not in flat:
                continue
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertTrue(
                    re.search(r"narrows \*\*which\*\*|not this gate|never \*\*whether\*\*", flat)
                    or "records \\*how\\*" in flat,
                    f"{p.relative_to(REPO_ROOT)} reads `license` from {PREF_KEY} beside its "
                    "licensing framing without saying that key is not the gate. That is the "
                    "shape of the original defect: a bootcamper whose license was measured as "
                    "uncapped never gets the key, so keying on it re-frames a constraint they "
                    "do not have")

    def test_step1_defers_to_the_branches_rather_than_restating_them(self):
        """INV-179 — the three branches are stated once, in the reconciliation block."""
        phase_a = [p for p in framing_files() if p.name == "phaseA-build-loading.md"]
        self.assertTrue(phase_a, "phaseA-build-loading.md no longer frames licensing")
        flat = flatten(phase_a[0].read_text(encoding="utf-8"))
        self.assertIn("reconcile it against the license already detected", flat,
                      "the canonical three-branch block is gone; Step 1 defers to it by name")
        self.assertEqual(
            1, flat.count("suppress it entirely"),
            "the three branches are stated more than once — Step 1 must cite them, not "
            "duplicate them (INV-179), or the two copies drift exactly as they did before")

    def test_the_suppression_branch_is_stated_at_step_1(self):
        """The whole point: an unconstrained bootcamper gets no framing at all."""
        phase_a = [p for p in framing_files() if p.name == "phaseA-build-loading.md"][0]
        flat = flatten(phase_a.read_text(encoding="utf-8"))
        self.assertRegex(
            flat,
            r"suppress this entire block when it does not bind",
            "Step 1 does not state its own suppression branch, so the framing still fires "
            "for a bootcamper with an uncapped license")
        self.assertIn("do not measure it again here", flat,
                      "Step 1 must not re-measure the license — Module 4 Step 8a is the only "
                      "writer, and a second call is how two answers start to differ")


if __name__ == "__main__":
    unittest.main()
