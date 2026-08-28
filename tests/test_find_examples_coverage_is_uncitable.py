"""`find_examples`' coverage figures are not citeable, because the server states two of them.

One tool on one server describes its own coverage two different ways, read in the same
session (server 1.33.0, re-confirmed 2026-08-28):

- **Declared tool description** (the manifest a client loads): *"37 indexed Senzing GitHub
  repositories ... Indexes source code (.py, .java, .cs, .rs) ... Covers Python, Java, C#,
  Rust SDK patterns"*.
- **`get_capabilities`**, on the same tool: *"42 indexed Senzing GitHub repositories ...
  (.py, .java, .cs, .rs, .ts, .js) ... Python, Java, C# official; Rust and TypeScript/Node.js
  community"*.

Two counts and two extension sets. A call settles it:
`find_examples(query='add record engine initialization', language='typescript')` returns
`brianmacy/sz-napi` → `code-snippets/initialization/engine-priming/index.ts`. `.ts` is
indexed; the declared description is the stale half.

⛔ **So no repository count is citeable, and this guard exists to keep one out.** The plugin
was not wrong when this was found — it quotes `get_capabilities` and states no count. The
exposure is structural: `ground-rules.md` makes the **declared schema** authoritative for what
a tool accepts (INV-234), which is correct, and an editor applying that in reverse would trust
manifest *prose* — landing on the stale half with a citation that looks impeccable. A future
edit writing "37 repositories", or "indexes .py, .java, .cs and .rs", would be wrong while
carrying a real MCP citation.

⚠️ TypeScript is a shipped bootcamp language, not hypothetical — `bootcamp-preparation/SKILL.md`
offers it — so the stale half would send a TypeScript bootcamper past the one route that does
have examples for their binding.

⚠️ What this does NOT establish: which figure is current today. That is a live-server property
the offline suite cannot see (INV-108). It asserts the plugin cites **no** figure, which is the
only stance that cannot go stale.

Upstream: reported 2026-08-27 via `submit_feedback(category='bug')` on the maintainer's verbatim
approval. Anonymous, so no reply will arrive; re-check rather than assuming it was acted on.

Source spec: `specs/find-examples-self-describes-two-different-coverages.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"

#: A repo count asserted about the example index. Matched only near a repo/index word so the
#: many unrelated 37s and 42s in the corpus (record counts, line numbers) do not trip it.
COUNT_NEAR_REPO = re.compile(
    r"\b(37|42)\b[^.\n]{0,60}\b(repo|repositor|indexed)|"
    r"\b(repo|repositor|indexed)[^.\n]{0,60}\b(37|42)\b", re.I)
#: The declared description's extension list, which omits .ts/.js.
STALE_EXTENSIONS = re.compile(r"\.cs\s*,\s*\.rs(?!\s*,\s*\.ts)", re.I)


MARKER = "COVERAGE-FIGURE-SCAN: quoted-history"


def scannable_lines(path):
    """(lineno, line) pairs, skipping any block a quoted-history marker exempts.

    ⚠️ Prose that **quotes** the stale figures in order to correct them is not asserting
    them, and a guard that cannot tell the difference forbids the correction from naming
    what it corrects. This mirrors the repo's existing `MCP-NEGATIVE-SCAN: quoted-history`
    convention: the marker sits directly above the block and covers it to the next blank
    line, so the exemption is narrow and visible rather than a file-wide opt-out.
    """
    out, skipping = [], False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if MARKER in line:
            skipping = True
            continue
        if skipping:
            if not line.strip():
                skipping = False
            continue
        out.append((n, line))
    return out


def shipped_files():
    """Shipped markdown plus scripts — a count could be written into either."""
    return sorted(p for p in PLUGIN.rglob("*")
                  if p.is_file() and p.suffix in {".md", ".py"}
                  and "__pycache__" not in p.parts)


class NoShippedFileCitesACoverageFigure(unittest.TestCase):
    def test_no_shipped_file_states_a_repository_count(self):
        bad = []
        for p in shipped_files():
            for n, line in scannable_lines(p):
                if COUNT_NEAR_REPO.search(line):
                    bad.append(f"{p.relative_to(REPO_ROOT)}:{n}  {line.strip()[:100]}")
        self.assertEqual(
            [], bad,
            "a shipped file states a find_examples repository count. The server gives two "
            "different numbers, so NO count is citeable — quoting either recreates the "
            "defect this guard exists for:\n  " + "\n  ".join(bad))

    def test_no_shipped_file_enumerates_the_stale_extension_list(self):
        bad = []
        for p in shipped_files():
            for n, line in scannable_lines(p):
                if STALE_EXTENSIONS.search(line):
                    bad.append(f"{p.relative_to(REPO_ROOT)}:{n}  {line.strip()[:100]}")
        self.assertEqual(
            [], bad,
            "a shipped file enumerates find_examples' indexed extensions ending at `.rs`, "
            "which is the declared description's stale list and omits the indexed .ts/.js:\n  "
            + "\n  ".join(bad))

    def test_the_scan_is_not_vacuous(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertGreater(len(shipped_files()), 40, "the shipped corpus went empty or tiny")
        self.assertTrue(COUNT_NEAR_REPO.search("indexes 37 Senzing GitHub repositories"),
                        "the count matcher no longer detects the claim it exists for")
        self.assertTrue(STALE_EXTENSIONS.search("Indexes source code (.py, .java, .cs, .rs)"),
                        "the extension matcher no longer detects the stale list")

    def test_the_exemption_is_narrow(self):
        """⛔ The marker must not become a file-wide opt-out."""
        gr = PLUGIN / "senzing-bootcamp" / "skills" / "bootcamp-onboarding" / "ground-rules.md"
        total = len(gr.read_text(encoding="utf-8").splitlines())
        scanned = len(scannable_lines(gr))
        self.assertGreater(
            scanned, total - 15,
            f"the quoted-history exemption is skipping {total - scanned} lines of "
            "ground-rules.md; it is meant to cover one quoting paragraph, not a region")
        self.assertLess(scanned, total, "the marker is present but exempting nothing")

    def test_the_current_list_is_not_flagged(self):
        """The complete list is fine to write — only the truncated one is stale."""
        self.assertFalse(STALE_EXTENSIONS.search(".py, .java, .cs, .rs, .ts, .js"),
                         "the matcher flags the CURRENT extension list, which would push an "
                         "editor into deleting a correct sentence")


class ThePluginRecordsWhichSourceGoverns(unittest.TestCase):
    def test_ground_rules_separates_parameters_from_coverage(self):
        """INV-234 is right about parameters and must not be read as endorsing stale prose."""
        gr = PLUGIN / "senzing-bootcamp" / "skills" / "bootcamp-onboarding" / "ground-rules.md"
        flat = re.sub(r"\s+", " ", gr.read_text(encoding="utf-8")).lower()
        self.assertIn("inv-234", flat)
        self.assertRegex(
            flat,
            r"authoritative for the parameters a tool accepts — not for prose",
            "ground-rules.md does not distinguish declared-schema authority over accepted "
            "parameters from get_capabilities' authority over coverage prose, so the INV-234 "
            "passage still reads as endorsing whatever the manifest says")
        self.assertIn("get_capabilities` governs", flat.replace("**", ""),
                      "ground-rules.md does not name which source governs for coverage")

    def test_the_contested_fact_is_recorded_where_the_index_is_quoted(self):
        """INV-183 — reachable at the step that quotes it, not only in ground-rules."""
        pa = (PLUGIN / "senzing-bootcamp" / "skills" / "module-06-data-processing"
              / "phaseA-build-loading.md")
        flat = re.sub(r"\s+", " ", pa.read_text(encoding="utf-8"))
        self.assertIn("get_capabilities", flat)
        self.assertIn("index.ts", flat,
                      "the note does not name the live .ts result that settled the "
                      "disagreement, so a reader cannot tell it was measured rather than argued")
        self.assertIn("2026-08-28", flat,
                      "the contested-fact note carries no date, so nobody can tell when it "
                      "was last checked (INV-080)")


if __name__ == "__main__":
    unittest.main()
