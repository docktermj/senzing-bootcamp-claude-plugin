"""Every module that compiles an MCP Java scaffold warns about the javax.json gap.

`generate_scaffold`'s Java loading snippets `import javax.json.*` and call
`Json.createReader(...)` to pull `DATA_SOURCE` and `RECORD_ID` out of each line. `javax.json`
(JSON-P) is **not** part of Java SE, the stock `senzingsdk-runtime` install does not supply it,
and the bootcamp compiles with plain `javac` — no Maven, no Gradle. So the scaffold does not
compile as delivered.

`specs/java-scaffold-json-dependency-gap.md` diagnosed this on 2026-07-25 and fixed it in three
modules: SDK setup (the canonical procedure), Data processing, and Data quality/mapping.
**System verification was never included** — even though its Step 4 independently calls
`generate_scaffold(workflow='full_pipeline')` and its own selection rule steers straight at a
loading snippet with the identical dependency.

⛔ **On Java the selection rule routes toward the dependency with no escape hatch.** All six
`loading/` snippets in that response that read an input file import `javax.json` — LoadViaLoop,
LoadViaFutures, LoadWithInfoViaFutures, LoadViaQueue, LoadWithStatsViaLoop,
LoadTruthSetWithInfoViaLoop (each fetched and checked on server 1.33.0, 2026-08-28). The only
one that does not, `LoadRecords.java`, hardcodes its records — which Step 4 explicitly forbids
picking. No jar under `/opt/senzing` carries a `javax/json` class.

⚠️ **The original fix shipped with no test at all** — `grep` found no guard naming it anywhere in
`tests/` before this file. That is why its three sites could not tell anyone a fourth was
missing, and why this guard covers **all** of them rather than only the new one.

⚠️ What this does NOT establish: that a substituted file compiles. That needs `javac` and the
installed SDK, which the offline suite has neither of (INV-108). It asserts the guidance is
present and reachable at the step that needs it (INV-183).

Source spec: `specs/system-verification-java-loading-scaffold-hits-the-json-p-gap-too.md`.
Original:    `specs/java-scaffold-json-dependency-gap.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
CANONICAL = "MCP Java scaffolds may need a JSON library the install does not provide"


def shipped_markdown():
    return sorted(p for p in PLUGIN.rglob("*.md") if "__pycache__" not in p.parts)


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def compiles_a_java_scaffold(path):
    """True when this file tells the guide to build a scaffold it fetched.

    Derived, never hardcoded (INV-246): the original fix listed three files, and a guard
    written from that list would have been satisfied while the fourth site was missing.
    """
    flat = flatten(path.read_text(encoding="utf-8"))
    return ("generate_scaffold" in flat or "sdk_guide" in flat) and (
        "javac" in flat or "compile" in flat) and "java" in flat


class EverySiteThatCompilesAScaffoldCoversTheGap(unittest.TestCase):
    def test_the_canonical_procedure_exists_exactly_once(self):
        """INV-179 — the four-item procedure lives in one file; the rest cite it by name.

        ⚠️ Matched on the procedure BODY, not on the heading. Citing sites quote the heading
        verbatim so a reader can find it, which is the intended shape — an earlier draft of
        this assertion counted those citations as duplicate copies and failed on a correct
        cross-reference.
        """
        procedure = "verify before compiling, not after"
        holders = [p.relative_to(REPO_ROOT) for p in shipped_markdown()
                   if procedure in flatten(p.read_text(encoding="utf-8"))]
        self.assertEqual(
            1, len(holders),
            "the four-item javax.json procedure must live in exactly one file and be cited "
            f"from the rest, not copied. Found in: {holders}")

    def test_the_canonical_heading_is_cited_by_more_than_its_holder(self):
        """A procedure nobody points at is a procedure nobody reaches (INV-183)."""
        citers = [p.relative_to(REPO_ROOT) for p in shipped_markdown()
                  if CANONICAL.lower() in flatten(p.read_text(encoding="utf-8"))]
        self.assertGreaterEqual(
            len(citers), 2,
            "only the canonical file names this section, so no other module routes a "
            f"bootcamper to it. Found: {citers}")

    def test_the_scan_finds_the_java_build_sites(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        sites = [p for p in shipped_markdown() if compiles_a_java_scaffold(p)]
        self.assertGreaterEqual(
            len(sites), 4,
            "fewer than the four known Java-scaffold build sites were found (SDK setup, "
            "System verification, Data processing, Data quality/mapping). The scan broke "
            "or the vocabulary moved — re-derive it, do not lower this floor")

    def test_system_verification_covers_the_gap(self):
        """The fourth site, and the one this spec exists for."""
        path = (PLUGIN / "senzing-bootcamp" / "skills" / "module-03-system-verification"
                / "phase1-verification.md")
        flat = flatten(path.read_text(encoding="utf-8"))
        self.assertIn("javax.json", flat,
                      "System verification never names the dependency its own Step 4 routes at")
        self.assertIn(CANONICAL.lower(), flat,
                      "System verification does not cross-reference the canonical procedure "
                      "in module-02-sdk-setup (INV-179)")

    def test_the_safety_asymmetry_is_restated_where_the_bootcamper_reads_it(self):
        """A cross-reference alone loses the one sentence that prevents the damage.

        Rewriting the Senzing calls to clear an import error is the failure the scaffold
        exists to prevent, so that sentence is repeated at the step rather than linked.
        """
        for name in ("module-02-sdk-setup", "module-03-system-verification"):
            hits = [p for p in shipped_markdown()
                    if name in str(p) and "javax.json" in flatten(p.read_text(encoding="utf-8"))]
            self.assertTrue(hits, f"{name} no longer names javax.json")
            for p in hits:
                flat = flatten(p.read_text(encoding="utf-8"))
                with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                    self.assertRegex(
                        flat,
                        r"replacing the \*\*json library\*\* is safe|"
                        r"replacing the json library is safe. altering the senzing sdk calls is not",
                        "the safety-asymmetry sentence is missing. Without it a bootcamper "
                        "facing an import error may 'fix' it by rewriting the SDK calls")

    def test_the_check_runs_before_the_compile_step(self):
        """Verify-before-compiling: a raw javac error is what this exists to prevent."""
        path = (PLUGIN / "senzing-bootcamp" / "skills" / "module-03-system-verification"
                / "phase1-verification.md")
        text = path.read_text(encoding="utf-8")
        check = text.find("Check the saved file's imports for a package outside the standard")
        compile_step = text.find("### Step 5: Build/Compile")
        self.assertNotEqual(-1, check, "the import check is gone from System verification")
        self.assertNotEqual(-1, compile_step, "Step 5 heading is gone")
        self.assertLess(
            check, compile_step,
            "the import check must come BEFORE the compile step — resolving it after the fact "
            "means surfacing the raw compiler error this fix exists to avoid")

    def test_step5_names_a_non_sdk_dependency_as_its_own_cause(self):
        """Its failure guidance listed only SDK-shaped causes, in the module that just
        verified the install — so an unresolved import read as a broken install."""
        path = (PLUGIN / "senzing-bootcamp" / "skills" / "module-03-system-verification"
                / "phase1-verification.md")
        flat = flatten(path.read_text(encoding="utf-8"))
        self.assertIn("non-sdk* dependency", flat.replace("*non-sdk*", "non-sdk*"),
                      "Step 5's Fix_Instruction does not name a missing non-SDK dependency as a "
                      "cause distinct from the SDK ones")


if __name__ == "__main__":
    unittest.main()
