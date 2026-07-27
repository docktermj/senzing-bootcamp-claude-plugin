"""The tab set must be stated once and agree everywhere it is stated.

This test exists because a previous change consolidated the visualization from eight tabs
to six in the reference server and in `visualization-api-reference.md`, and the whole suite
passed — while **nine** locations across four module-instruction files still told the agent
to build the removed tabs. An agent following
`module-07-query-visualize-discover/phase1-query-visualize.md` would have rebuilt them,
contradicting the contract it was told to build to.

The lesson generalised: the earlier tests asserted the two surfaces that had been *edited*
and inferred the rest was consistent. Consistency between files is exactly what cannot be
inferred, so it gets asserted here — across **every** shipped skill file, not a listed few.

What this pins:

* No shipped skill, command, or bundled doc presents a removed tab as a live tab.
* The reference server's `ALL_TABS`, the contract's active inventory, and the screenshot
  helper's tab catalogue all describe the same set.
* A removed tab id may survive only as an explicit removal/reserved note.
* Anything that enumerates the tab set names the same six.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SERVER = PLUGIN / "scripts" / "senzing_viz_server.py"
CAPTURE = PLUGIN / "scripts" / "capture_screenshots.py"
CONTRACT = (
    PLUGIN / "skills" / "module-03b-truthset-visualization" / "visualization-api-reference.md"
)

LIVE_TAB_IDS = ["graph", "stats", "matchkeys", "features", "overlap", "probe"]
LIVE_TAB_LABELS = [
    "Entity Graph",
    "Merge Statistics",
    "Match Keys",
    "Feature Scores",
    "Cross-Source",
    "Search / Probe",
]
REMOVED_TAB_LABELS = ["Relationship Network", "Record Merges"]

# A mention of a removed tab is legitimate only when it is *about* the removal. Each phrase
# below marks such a context; a mention on a line matching none of them is a live reference.
REMOVAL_CONTEXT = (
    "REMOVED",
    'no "Relationship Network" tab',
    'no "Record Merges" tab',
    "reverses an earlier ruling",
    "strict **superset**",
    "former Record Merges",
    "removed Record Merges",
    "standalone \"Relationship Network\"",
    "Relationship Network, or Record Merges tab",
    "relationship-network",   # the screenshot slug, in the identifier table
    "record-merges",          # ditto
    "Relationship Networks (exploring",  # the Discover demo of find_network, not a tab
)


def shipped_markdown():
    """Every Markdown file that ships to a bootcamper."""
    out = []
    for sub in ("skills", "commands", "docs"):
        out += sorted((PLUGIN / sub).rglob("*.md"))
    return out


def load(path):
    spec = importlib.util.spec_from_file_location(f"mod_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    return module


def server_tabs():
    src = SERVER.read_text()
    payload = re.search(r"const ALL_TABS=(\[\[.*?\]\]);", src).group(1)
    return re.findall(r'\["(\w+)","([^"]+)"\]', payload)


def contract_active_rows():
    text = CONTRACT.read_text()
    start = text.index("| Tab | Endpoint(s) | Shown when |")
    section = text[start : text.index("**De-duplication", start)]
    rows = re.findall(r"^\| \*\*(.+?)\*\*", section, re.M)
    return [r.replace(" (default)", "").strip() for r in rows]


class NoShippedFilePresentsARemovedTabAsLive(unittest.TestCase):
    """The check that the earlier suite was missing."""

    def test_no_live_reference_to_a_removed_tab(self):
        offenders = []
        for path in shipped_markdown():
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                if not any(label in line for label in REMOVED_TAB_LABELS):
                    continue
                if any(marker in line for marker in REMOVAL_CONTEXT):
                    continue
                offenders.append(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()[:110]}"
                )
        self.assertEqual(
            [],
            offenders,
            "these lines present a removed tab as a live tab; an agent reading them would "
            "rebuild it, contradicting visualization-api-reference.md:\n  "
            + "\n  ".join(offenders),
        )

    def test_no_shipped_file_claims_eight_tabs(self):
        offenders = []
        for path in shipped_markdown():
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                if re.search(r"\b(eight|8) tabs\b", line, re.I):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")
        self.assertEqual([], offenders, f"stale tab count: {offenders}")


class EveryTabInventoryAgrees(unittest.TestCase):
    def test_server_and_contract_agree(self):
        self.assertEqual(LIVE_TAB_LABELS, [label for _id, label in server_tabs()])
        self.assertEqual(LIVE_TAB_LABELS, contract_active_rows())

    def test_capture_helper_default_matches_the_live_set(self):
        module = load(CAPTURE)
        self.assertEqual(LIVE_TAB_IDS, list(module.DEFAULT_TABS))

    def test_capture_helper_catalogue_matches_the_contract_identifier_table(self):
        """Removed ids stay in the catalogue so an older snapshot is still capturable —
        but they must be marked REMOVED in the contract, never offered as defaults."""
        module = load(CAPTURE)
        text = CONTRACT.read_text()
        start = text.index("### Tab identifiers and deep-linking")
        section = text[start : text.index("Headline counts belong", start)]
        documented = {}
        for line in section.splitlines():
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) == 5 and cells[1].startswith("`") and cells[1] != "`Id`":
                documented[cells[1].strip("`")] = cells[4].strip("`")
        self.assertEqual(
            {tab: slug for tab, (slug, _label) in module.TABS.items()}, documented
        )
        for removed in ("network", "merges"):
            with self.subTest(removed=removed):
                self.assertIn(removed, module.TABS, "kept for older snapshots")
                self.assertNotIn(removed, module.DEFAULT_TABS, "must not be a default")

    def test_module_instructions_that_enumerate_tabs_name_the_live_six(self):
        """A file listing 3+ tab labels is enumerating the set; it must not miss one or add one."""
        problems = []
        for path in shipped_markdown():
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                if any(m in line for m in REMOVAL_CONTEXT):
                    continue
                named = [l for l in LIVE_TAB_LABELS + REMOVED_TAB_LABELS if l in line]
                if len(named) >= 3 and any(r in named for r in REMOVED_TAB_LABELS):
                    problems.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")
        self.assertEqual([], problems, f"tab enumeration includes a removed tab: {problems}")


class SnapshotKeepsTheNoQueryBrowse(unittest.TestCase):
    """Removing Record Merges is only lossless if its unique capability survives — and it
    has to survive in the **snapshot**, which is the artifact the bootcamper keeps. The
    first implementation lost it there: `#probe-btns` existed only in the live probe body,
    so `loadProbes()` had nowhere to render and the browse silently vanished offline."""

    def setUp(self):
        self.module = load(SERVER)

    def snapshot_probe_body(self):
        entities = [
            {
                "entity_id": 1,
                "entity_name": "Robert Smith",
                "record_count": 3,
                "data_sources": ["CUSTOMERS", "REFERENCE"],
                "records": [
                    {
                        "data_source": "CUSTOMERS",
                        "record_id": "1001",
                        "name": "Robert Smith",
                        "match_key": "+NAME+ADDRESS",
                    }
                ],
            }
        ]

        class FakeModel:
            def merges(self_inner):
                return {"entities": entities}

        return self.module._snapshot_probe_html(FakeModel(), None, None)

    def test_snapshot_probe_body_has_the_browse_container(self):
        self.assertIn('id="probe-btns"', self.snapshot_probe_body())

    def test_snapshot_probe_body_has_no_live_search_box(self):
        """It cannot work in a static file; its absence is what makes the chips live-only."""
        self.assertNotIn('id="search-in"', self.snapshot_probe_body())

    def test_live_probe_body_has_both(self):
        self.assertIn('id="probe-btns"', self.module.PROBE_BODY_LIVE)
        self.assertIn('id="search-in"', self.module.PROBE_BODY_LIVE)

    def test_chips_are_suppressed_without_a_search_box(self):
        page = self.module.render_page("T", sources=["CUSTOMERS"])
        self.assertRegex(
            page, r'const live=!!document\.getElementById\("search-in"\);'
        )
        self.assertRegex(page, r"if\(live\)m\.entities\.slice")

    def test_show_all_merges_does_not_require_a_search_box(self):
        """It runs in the snapshot, where #search-in does not exist."""
        page = self.module.render_page("T", sources=["CUSTOMERS"])
        body = page[page.index("function showAllMerges") :][:400]
        self.assertNotRegex(
            body,
            r'document\.getElementById\("search-in"\)\.value',
            "must not dereference the search box unguarded",
        )
        self.assertIn("if(si)si.value", body)

    def test_contract_states_the_offline_browse_requirement(self):
        text = CONTRACT.read_text()
        squashed = re.sub(r"\s+", " ", text)
        self.assertIn("that browse works offline", squashed.replace("**", ""))
        self.assertIn("MUST therefore include the `#probe-btns` container", squashed)


class YesNoHintConventionIsDocumented(unittest.TestCase):
    """INV-051 exempts the `(respond yes or no)` hint, but the exemption lived only in
    INVARIANTS.md — not in the file the agent actually reads each turn."""

    def test_ground_rules_documents_the_exemption(self):
        text = (PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md").read_text()
        self.assertIn("The one sanctioned \"or\"", text)
        self.assertIn("(respond yes or no)", text)
        self.assertIn("INV-051", text)

    def test_it_forbids_editing_a_pinned_question_to_add_or_remove_it(self):
        text = (PLUGIN / "skills" / "bootcamp-onboarding" / "ground-rules.md").read_text()
        squashed = re.sub(r"[*\s]+", " ", text)
        self.assertIn("do not add or remove it from a question whose wording is pinned", squashed)


if __name__ == "__main__":
    unittest.main()
