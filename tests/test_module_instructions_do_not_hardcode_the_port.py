"""Module instructions must not hardcode the visualization port where it is acted on.

INV-172: a retained artifact must not hardcode a fact about the environment that produced
it, and "a port MUST be derived from the parsed value actually in use". The invariant was
established by `snapshot-port-and-dataset-wording` (2026-07-28), which fixed the Python
reference server and Module 7's instructions.

`tests/test_snapshot_and_capture_fidelity.py` guards the first of those — it reads
`senzing_viz_server.py`'s `_snapshot_probe_html` and asserts no `localhost:8080` literal
survives in that code path. It scans **no module instruction files at all**, which is how
`module-03b-truthset-visualization/phase1-visualization.md` kept the literal at three sites
while the same file said twice that the port may differ:

    :266  `http://localhost:8080`. If port 8080 is in use, use a different port ...
    :408  - Port in use → pass a different `--port` and share the new URL.

On that branch the capture URL pointed at a dead port — losing every screenshot the module
produces, permanently, since capture must happen before teardown (INV-122/INV-146) — and the
pinned bootcamper-facing line sent the reader to a port nothing was listening on, which is
verbatim the failure INV-172 was written from.

⛔ **The default-port START command is correct and must keep passing.** `--port 8080`, "on
port 8080", "If port 8080 is in use" and "should report a URL like `http://localhost:8080`"
are all legitimate: 8080 *is* the default, and the sentence naming it is what makes the rest
a contradiction rather than a mistake. This guard bans the literal only where the port is
**acted on** — the capture URL, the line spoken to the Bootcamper, and the recorded
checkpoint — never where it is offered as the default.

Out of scope by design, and asserted so below:
  * `docs/examples/bootcamp_recap.example.md` — a sanitized record of a run that really did
    use 8080 (INV-065). Rewriting it would falsify the fixture.
  * `scripts/capture_screenshots.py` — the literal is in `--help` usage text (INV-188).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"

#: Each: (name, compiled pattern, why it is forbidden). Patterns are deliberately narrow —
#: they describe the three places the port is USED, not every mention of 8080.
FORBIDDEN = (
    ("capture-url",
     re.compile(r"--url\s+https?://localhost:8080"),
     "capture must use the port the server was actually started on; a dead port exits 2 "
     "and loses every screenshot for the module (INV-122/INV-146)"),
    ("bootcamper-facing-url",
     re.compile(r'"[^"\n]*running at[^"\n]*localhost:8080'),
     "the line spoken to the Bootcamper must name the port in use, or it sends them to a "
     "port nothing is listening on (INV-172)"),
    ("recorded-checkpoint",
     re.compile(r'"url"\s*:\s*"https?://localhost:8080|"port"\s*:\s*8080'),
     "a recorded checkpoint states what actually happened, so its example must not teach "
     "a literal port"),
)

#: Phrasings that name 8080 as the DEFAULT. These must never be reported.
ALLOWED_SAMPLES = (
    "  --port 8080",
    "records on port 8080. For Python:",
    "`http://localhost:8080`. If port 8080 is in use, use a different port and tell",
    "- Port in use → pass a different `--port` and share the new URL.",
)


def instruction_files():
    return sorted(SKILLS.rglob("*.md"))


class TheScanIsNotVacuous(unittest.TestCase):
    def test_it_reads_a_real_corpus(self):
        files = instruction_files()
        self.assertGreater(len(files), 20,
                           "module instruction sweep found almost nothing — SKILLS moved?")

    def test_it_reads_the_file_this_guard_exists_for(self):
        """A count alone passes on the wrong files; name the one that regressed."""
        names = {p.name for p in instruction_files()}
        self.assertIn("phase1-visualization.md", names)
        self.assertIn("phase1-query-visualize.md", names)


class NoInstructionHardcodesThePortWhereItIsUsed(unittest.TestCase):
    def test_no_shipped_instruction_hardcodes_it(self):
        for path in instruction_files():
            text = path.read_text(encoding="utf-8")
            for name, pattern, why in FORBIDDEN:
                with self.subTest(check=name, file=path.name):
                    hits = [text[:m.start()].count("\n") + 1
                            for m in pattern.finditer(text)]
                    self.assertEqual(
                        [], hits,
                        "%s:%s hardcodes port 8080 (%s) — %s"
                        % (path.relative_to(REPO_ROOT),
                           ",".join(str(n) for n in hits), name, why))


class TheDefaultPortPhrasingsStillPass(unittest.TestCase):
    """Without this, the obvious "ban 8080" simplification looks correct and is wrong."""

    def test_the_allowed_phrasings_trip_nothing(self):
        for sample in ALLOWED_SAMPLES:
            for name, pattern, _why in FORBIDDEN:
                with self.subTest(check=name, sample=sample[:40]):
                    self.assertIsNone(
                        pattern.search(sample),
                        "the %s check flags a legitimate default-port phrasing" % name)

    def test_module_03b_still_documents_the_default_and_the_collision(self):
        text = (SKILLS / "module-03b-truthset-visualization"
                / "phase1-visualization.md").read_text(encoding="utf-8")
        self.assertIn("--port 8080", text,
                      "the default start command was removed; 8080 is still the default")
        self.assertRegex(text, r"(?i)port 8080 is in use",
                         "the port-collision instruction was removed")


class TheExcludedSurfacesAreExcludedOnPurpose(unittest.TestCase):
    """Pins the scope decision, so a later widening is a deliberate act."""

    def test_the_example_recap_is_not_scanned(self):
        example = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "docs" / "examples"
                   / "bootcamp_recap.example.md")
        self.assertTrue(example.is_file(), "the sanitized example recap moved")
        self.assertNotIn(example, instruction_files(),
                         "the example recap records a real run on 8080 (INV-065) and must "
                         "not be rewritten to satisfy this guard")


if __name__ == "__main__":
    unittest.main()
