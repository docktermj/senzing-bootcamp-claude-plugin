"""Two ways the retained visualization keepsake told the reader something false.

**Hardcoded port and dataset wording.** The snapshot's Search / Probe text read
"example searches run against this Truth Set. In the live app
(http://localhost:8080)". One code path serves the Truth Set in its own module and the
bootcamper's own data in Query, Visualize and Discover, and the server takes `--port`, so
that text told a Module 7 reader on a non-default port to open a port nothing was
listening on *and* mislabeled their data — permanently, in `docs/visualizations/*.html`.

**Re-activating the already-active tab.** Capture drives the app with an injected
`activate('<tab>')` (snapshot) or `?tab=<id>` (live server). Both call `activate()`, which
redraws the tab — and for the Entity Graph a redraw starts a fresh d3 force simulation.
Mid-capture that produced a valid PNG of every node collapsed in a corner: 47 KB where
227 KB was expected, at exit 0, with a caption describing a graph the image did not show.

The fix for the second is an idempotent `activate()` rather than a caller-side skip: the
default tab is chosen by `buildNav()` at runtime, so it is not knowable from the markup,
and the guard has to hold for both capture routes plus a user clicking the active button.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
VIZ = PLUGIN / "scripts" / "senzing_viz_server.py"
CAPTURE = PLUGIN / "scripts" / "capture_screenshots.py"
CONTRACT = PLUGIN / "skills" / "module-03b-truthset-visualization" / "visualization-api-reference.md"
MODULE_COMPLETION = PLUGIN / "skills" / "bootcamp-onboarding" / "module-completion.md"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VIZ_MOD = load(VIZ, "viz_snapshot_fidelity")
CAP_MOD = load(CAPTURE, "capture_fidelity")


class FakeModel:
    def merges(self):
        return {"entities": []}

    def data_sources(self):
        return ["CUSTOMERS"]


def contract_flat():
    """Contract text with wrapping collapsed, so a phrase split across lines matches."""
    import re as _re
    return _re.sub(r"\s+", " ", CONTRACT.read_text(encoding="utf-8"))


def note_text(port=8080, dataset=""):
    html = VIZ_MOD._snapshot_probe_html(FakeModel(), None, 0, port=port, dataset=dataset)
    return re.search(r'<p class="muted">.*?</p>', html, re.S).group(0)


class TheSnapshotNamesTheRealPort(unittest.TestCase):
    def test_a_non_default_port_reaches_the_snapshot(self):
        note = note_text(port=9001)
        self.assertIn("9001", note)
        self.assertNotIn("8080", note)

    def test_the_default_port_still_renders(self):
        self.assertIn("8080", note_text(port=8080))

    def test_no_hardcoded_port_literal_remains_in_the_note_path(self):
        """The literal may exist as an argparse default; it must not be in the text."""
        source = VIZ.read_text(encoding="utf-8")
        start = source.index("def _snapshot_probe_html")
        body = source[start:source.index("def ", start + 10)]
        self.assertNotIn("localhost:8080", body)


class TheSnapshotDoesNotAssumeTheTruthSet(unittest.TestCase):
    def test_default_wording_is_neutral(self):
        note = note_text()
        self.assertIn("the loaded data", note)
        self.assertNotIn("Truth Set", note)

    def test_a_caller_supplied_dataset_is_used(self):
        self.assertIn("your CUSTOMERS data", note_text(dataset="your CUSTOMERS data"))

    def test_the_truth_set_module_can_still_say_so(self):
        self.assertIn("the Senzing Truth Set", note_text(dataset="the Senzing Truth Set"))

    def test_a_dataset_label_is_html_escaped(self):
        """It reaches a retained HTML artifact (INV-106's class of concern)."""
        note = note_text(dataset='<script>alert(1)</script>')
        self.assertNotIn("<script>alert(1)</script>", note)

    def test_the_cli_exposes_a_dataset_option(self):
        self.assertIn("--dataset", VIZ.read_text(encoding="utf-8"))

    def test_the_contract_forbids_hardcoding_either(self):
        self.assertRegex(
            contract_flat(),
            r"(?i)MUST NOT hardcode a port or name a dataset the caller did not",
        )


class ActivateIsIdempotent(unittest.TestCase):
    """The guard belongs in activate(), because both capture routes call it."""

    def setUp(self):
        self.page = VIZ_MOD.render_page("T", sources=["CUSTOMERS"])
        start = self.page.index("function activate(id)")
        self.body = self.page[start:self.page.index("function buildNav", start)]

    def test_it_returns_early_when_the_tab_is_already_active(self):
        self.assertRegex(self.body, r'classed\("active"\)')
        self.assertRegex(self.body, r"\breturn;")

    def test_the_early_return_precedes_the_redraw(self):
        self.assertLess(self.body.index("return;"), self.body.index("drawFor(id)"))

    def test_it_still_redraws_when_switching_tabs(self):
        self.assertIn("drawFor(id)", self.body)

    def test_the_contract_requires_idempotence(self):
        text = contract_flat()
        self.assertRegex(text, r"(?i)`activate\(\)` MUST be idempotent")
        self.assertRegex(text, r"(?i)MUST return without redrawing")

    def test_the_contract_says_why_both_routes_matter(self):
        self.assertRegex(contract_flat(), r"(?i)deep-linking calls `activate\(\)` too")


class AnimatedTabsGetALongerSettleBudget(unittest.TestCase):
    def test_the_graph_budget_exceeds_the_static_one(self):
        self.assertGreater(
            CAP_MOD._virtual_time_ms("graph"), CAP_MOD._virtual_time_ms("stats")
        )

    def test_a_static_tab_keeps_the_base_budget(self):
        self.assertEqual(CAP_MOD._CHROME_VIRTUAL_TIME_MS, CAP_MOD._virtual_time_ms("stats"))

    def test_an_unknown_or_empty_tab_keeps_the_base_budget(self):
        self.assertEqual(CAP_MOD._CHROME_VIRTUAL_TIME_MS, CAP_MOD._virtual_time_ms(""))
        self.assertEqual(CAP_MOD._CHROME_VIRTUAL_TIME_MS, CAP_MOD._virtual_time_ms("nope"))

    def test_the_chrome_argv_uses_the_per_tab_budget(self):
        from unittest import mock

        seen = {}

        def fake_run(argv, **kwargs):
            seen["argv"] = argv
            return mock.MagicMock(returncode=0)

        CAP_MOD._CURRENT_TAB = "graph"
        try:
            with mock.patch.object(CAP_MOD, "_chrome_exe", return_value="/usr/bin/chromium"), \
                    mock.patch.object(CAP_MOD.subprocess, "run", side_effect=fake_run):
                CAP_MOD._capture_chrome_cli("http://localhost:8080/?tab=graph",
                                           Path("/nonexistent/x.png"))
        finally:
            CAP_MOD._CURRENT_TAB = ""
        budget = [a for a in seen["argv"] if str(a).startswith("--virtual-time-budget=")]
        self.assertEqual(
            [f"--virtual-time-budget={CAP_MOD._virtual_time_ms('graph')}"], budget
        )

    def test_the_capture_guidance_says_to_check_the_graph_image(self):
        self.assertRegex(
            MODULE_COMPLETION.read_text(encoding="utf-8"),
            r"(?i)nodes are spread|bunched in one corner",
        )


if __name__ == "__main__":
    unittest.main()


class EscapingIsSafeInBothContextsTheContractNames(unittest.TestCase):
    """`_esc_html` covers attribute position, which the contract always promised.

    The visualization contract's "Two contexts, two rules" has said "Escape `&`, `<` and `>`
    (and quotes in attribute position)" for as long as INV-106 has existed. The reference
    helper it points implementers at escaped only the three. Every call site was a text
    node, so nothing rendered wrong — but the contract promised the attribute half and the
    reference did not deliver it, which is the INV-164 pattern: a divergence between the
    written rule and the reference reaches generated code, in a language whose author never
    reads the Python.

    Found by the 2026-07-30 sweep. Pinned in both directions: the helper escapes quotes, and
    a value carrying one cannot close an attribute it is placed in.
    """

    HOSTILE = 'Acme" onmouseover="alert(1)'

    def test_esc_html_escapes_both_quote_characters(self):
        out = VIZ_MOD._esc_html("""double " and single ' quote""")
        self.assertNotIn('"', out, "double quote left raw — unsafe in attribute position")
        self.assertNotIn("'", out, "single quote left raw — unsafe in a single-quoted attribute")
        self.assertIn("&quot;", out)
        self.assertIn("&#39;", out)

    def test_a_hostile_value_cannot_break_out_of_an_attribute(self):
        """Parsed, not pattern-matched: the payload SHOULD survive as inert data.

        A first version of this test stripped `&quot;` and then asserted the payload was
        absent — which fails on correct output, because `onmouseover=` is legitimately
        present as *text inside* the attribute value. The property is not "the dangerous
        string is gone", it is "no second attribute was created". Only a parser can tell
        those apart.
        """
        from html.parser import HTMLParser

        seen = []

        class Collect(HTMLParser):
            def handle_starttag(self, tag, attrs):
                seen.append((tag, dict(attrs)))

        markup = '<div title="%s">x</div>' % VIZ_MOD._esc_html(self.HOSTILE)
        Collect().feed(markup)
        self.assertEqual(1, len(seen), "escaping produced more than one tag: %s" % markup)
        tag, attrs = seen[0]
        self.assertEqual(["title"], list(attrs), "a second attribute was injected: %s" % attrs)
        # The payload survives, inert, as the attribute's value — that is the correct outcome.
        self.assertEqual(self.HOSTILE, attrs["title"])

    def test_the_three_original_characters_are_still_escaped(self):
        out = VIZ_MOD._esc_html("<b>a & b</b>")
        for raw in ("<", ">", "&b"):
            self.assertNotIn(raw, out.replace("&amp;", "").replace("&lt;", "").replace("&gt;", ""))

    def test_text_nodes_are_unharmed_by_quote_escaping(self):
        """`&quot;`/`&#39;` render as the quote characters, so no visible change."""
        import html as _html
        for value in ('He said "hi"', "it's fine", "plain"):
            self.assertEqual(value, _html.unescape(VIZ_MOD._esc_html(value)))

    def test_the_contract_states_the_quote_requirement(self):
        text = CONTRACT.read_text(encoding="utf-8") if hasattr(CONTRACT, "read_text") \
            else open(CONTRACT, encoding="utf-8").read()
        flat = re.sub(r"\s+", " ", text)
        self.assertIn("quotes in attribute position", flat)
        self.assertIn("cover the quotes", flat)
