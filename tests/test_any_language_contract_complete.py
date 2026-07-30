"""The any-language build guidance must carry every requirement, not just the easy ones.

INV-090 says the visualization server is built in the Bootcamper's chosen language, from
`visualization-api-reference.md` plus `phase1-visualization.md`. The bundled Python server
is the *reference*, run directly only when the chosen language is Python. So any
requirement that exists only in `senzing_viz_server.py` — or that is stated only as the
name of a Python function — is a requirement a Java, C#, Go or TypeScript bootcamp never
receives.

That happened, and it happened to a security control. INV-106 mandated the stored-XSS guard
for inline `<script>` payloads by naming `senzing_viz_server.py`'s `_script_json` helper.
The Python reference escapes correctly at every site; the contract mentioned escaping **zero
times**. A non-Python server built strictly to the contract therefore shipped the exact
breakout vector the invariant was written to close — in the standalone snapshot, which is
the artifact designed to be saved and shared.

What made it a gap rather than an accepted limit: the sibling requirement *did* get through.
Offline rendering (INV-091) is stated in the build guidance in plain terms. Escaping was not.
Same class, one communicated, one missed by inference.

So this test asserts, for each requirement an any-language builder must satisfy, that the
build guidance states it **as behaviour** — and that no such requirement is expressed only
as a Python identifier.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
M3B = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills" / "module-03b-truthset-visualization"
CONTRACT = M3B / "visualization-api-reference.md"
PHASE1 = M3B / "phase1-visualization.md"
SERVER = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts" / "senzing_viz_server.py"


def build_guidance():
    """Everything an any-language implementer is told to build from."""
    return CONTRACT.read_text() + "\n" + PHASE1.read_text()


def squash(text):
    return re.sub(r"\s+", " ", text)


def plain(text):
    """Whitespace-collapsed AND emphasis-stripped, for assertions about wording rather
    than formatting."""
    return re.sub(r"\s+", " ", text.replace("**", ""))


class ContractCarriesEveryBuildRequirement(unittest.TestCase):
    """Each entry: (requirement, phrases that would evidence it). A builder reading only
    the guidance must be able to satisfy every one."""

    REQUIREMENTS = {
        "inline-<script> escaping (stored-XSS guard, INV-106)": [
            "u003c", "JSON escapes", "closes the script element",
        ],
        "HTML escaping of data-sourced strings (INV-106)": [
            "written into rendered HTML", "treats the value as text rather than markup",
        ],
        "offline rendering / no CDN (INV-091)": [
            "no network access", "rather than fetching from a CDN",
        ],
        "tab identifiers and deep-linking (INV-124)": [
            "Tab identifiers and deep-linking", "activate(<id>)", "?tab=",
        ],
        "data-source colours assigned from the data (INV-127)": [
            "ASSIGNED FROM the sources present", "never from a name-keyed palette",
        ],
        "legends generated from the data": [
            "Legends are generated FROM the data",
        ],
        "de-duplication (one tab per dataset)": [
            "De-duplication (required)",
        ],
        "per-entity actions everywhere": [
            "Per-entity actions (required everywhere)",
        ],
        "server lifetime / teardown gate": [
            "Server lifetime (required in every module that starts one)",
        ],
        "scale-aware defaults reviewed against real data": [
            "Scale principle",
        ],
    }

    def setUp(self):
        self.guidance = squash(build_guidance())

    def test_every_requirement_is_stated_in_the_build_guidance(self):
        missing = {}
        for requirement, phrases in self.REQUIREMENTS.items():
            absent = [p for p in phrases if squash(p) not in self.guidance]
            if absent:
                missing[requirement] = absent
        self.assertEqual(
            {},
            missing,
            "these requirements are not stated in the any-language build guidance, so a "
            "non-Python server built strictly from it would not satisfy them:\n  "
            + "\n  ".join(f"{k}: missing {v}" for k, v in missing.items()),
        )

    def test_escaping_is_marked_as_a_hard_requirement(self):
        """It is a security control, so it must be a gate, not advice."""
        text = CONTRACT.read_text()
        start = text.index("### Escaping data-sourced strings")
        section = text[start : start + 3000]
        self.assertIn("⛔", section, "the escaping requirement must be a ⛔ directive")
        self.assertIn("MUST", section)

    def test_escaping_section_explains_why_json_alone_is_insufficient(self):
        """Without the reason, an implementer reasonably concludes their JSON writer suffices."""
        squashed = plain(CONTRACT.read_text())
        self.assertIn("is not sufficient", squashed)
        self.assertIn("JSON does not escape", squashed)

    def test_exempt_surface_is_named(self):
        """application/json responses are not an HTML-embed surface; say so, or an
        implementer over-escapes the API and breaks the client."""
        self.assertIn("application/json", squash(CONTRACT.read_text()))
        self.assertIn("exempt", squash(CONTRACT.read_text()))


class NoRequirementIsStatedOnlyAsAPythonIdentifier(unittest.TestCase):
    """A Python function name is not a requirement a Java bootcamp can act on."""

    # Python-only identifiers that must never be the SOLE expression of a requirement.
    PY_ONLY = ("_script_json", "_esc_html", "json.dumps")

    def test_python_helpers_appear_only_as_a_labelled_reference(self):
        text = CONTRACT.read_text()
        for name in self.PY_ONLY:
            if name not in text:
                continue
            with self.subTest(name=name):
                # Every mention must sit in a passage that flags it as the Python reference.
                for m in re.finditer(re.escape(name), text):
                    window = squash(text[max(0, m.start() - 400) : m.start() + 200])
                    self.assertTrue(
                        "Reference implementation (Python)" in window
                        or "Python reference" in window
                        or "not** the requirement" in window
                        or "not the requirement" in window,
                        f"{name} is cited without marking it as the Python reference: …{window[-160:]}",
                    )

    def test_invariant_states_behaviour_not_a_function_name(self):
        inv = (REPO_ROOT / "specs" / "INVARIANTS.md").read_text()
        body = re.search(r"^- \*\*INV-106\*\* — (.*?)(?=\n- \*\*INV-)", inv, re.M | re.S).group(1)
        squashed = plain(body)
        self.assertIn("MUST have `<`, `>` and `&` escaped", squashed)
        self.assertIn("stated as behaviour in `visualization-api-reference.md`", squashed)
        self.assertRegex(
            squashed,
            r"Python reference implementation of it, not the requirement itself",
            "INV-106 must mark the Python helpers as the reference, not the requirement",
        )

    def test_invariant_records_the_in_place_clarification(self):
        """INVARIANTS.md rule: an in-place edit may only clarify, and must say so."""
        inv = (REPO_ROOT / "specs" / "INVARIANTS.md").read_text()
        body = re.search(r"^- \*\*INV-106\*\* — (.*?)(?=\n- \*\*INV-)", inv, re.M | re.S).group(1)
        self.assertIn("Wording clarified in place 2026-07-26", plain(body))
        self.assertIn("no meaning change", plain(body))


class PythonReferenceStillImplementsWhatItDocuments(unittest.TestCase):
    """The reference must not drift from the contract it is the reference for."""

    def test_script_json_escapes_all_three_characters(self):
        src = SERVER.read_text()
        fn_start = src.index("def _script_json")
        fn = src[fn_start : fn_start + 800]
        for esc in ("u003c", "u003e", "u0026"):
            with self.subTest(esc=esc):
                self.assertIn(esc, fn)

    def test_inline_script_payloads_go_through_it(self):
        src = SERVER.read_text()
        for m in re.finditer(r"<script>const __DATA__=\" \+ (\w+)", src):
            self.assertEqual("_script_json", m.group(1))
        self.assertIn('_script_json(payload)', src.replace('" + _script_json(payload)', '_script_json(payload)'))

    def test_esc_html_exists_and_is_used(self):
        src = SERVER.read_text()
        self.assertIn("def _esc_html", src)
        self.assertGreater(src.count("_esc_html("), 2, "escaping helper must actually be used")


class ShippedFilesDoNotCiteNeverPropagatedPaths(unittest.TestCase):
    """propagate-to-public excludes specs/**, .claude/**, MIGRATION.md, resources/ — a
    shipped file citing one leaves a dangling pointer in the public repo (INV-003)."""

    EXCLUDED = ("specs/", ".claude/", ".sync-state.json")

    def test_no_shipped_markdown_cites_an_excluded_path(self):
        offenders = []
        for path in sorted((REPO_ROOT / "plugins").rglob("*.md")):
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                for ex in self.EXCLUDED:
                    # `src/resources/` is the bootcamper project's own dir, not maintainer resources.
                    if ex in line and "src/resources/" not in line:
                        offenders.append(
                            f"{path.relative_to(REPO_ROOT)}:{lineno} cites {ex}"
                        )
        self.assertEqual([], offenders, "\n  ".join(offenders))


class TheExcludedPathSweepIsNotVacuous(unittest.TestCase):
    """`test_no_shipped_markdown_cites_an_excluded_path` walks `plugins/**/*.md` and
    asserts nothing cites a never-propagated path. An empty walk asserts nothing."""

    def test_plugin_markdown_is_actually_being_scanned(self):
        found = list((REPO_ROOT / "plugins").rglob("*.md"))
        self.assertGreater(
            len(found), 20,
            "only %d plugin .md files found; the excluded-path sweep is vacuous" % len(found),
        )


if __name__ == "__main__":
    unittest.main()
