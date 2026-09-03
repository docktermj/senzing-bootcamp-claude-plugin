"""A screenshot comes from a capture-oriented render, not the interactive one (INV-299).

Three requirements, and **each masked the next** — which is why they ship together and why
dropping any one re-breaks the artifact. Measured 2026-09-03 through ``capture_screenshots.py``
on the full Truth Set (159 records -> 85 entities, SDK 4.4.0 build 4.4.0.26242, 1440x900):

1. **Presettle.** The animation path advanced **5 of the ~300 ticks** the layout needs, at every
   virtual-time budget from 5s to 300s, because d3's timer is driven by ``requestAnimationFrame``
   and headless virtual time does not advance it. The nodes sat near their initial phyllotaxis
   positions — which look plausibly spread out, which is why this went unnoticed for so long.
2. **Fit.** Settling alone put **most of the 85 nodes off-canvas**: ``forceCenter`` centers the
   centroid and bounds nothing. The unsettled clump had been accidentally masking that.
3. **Label ceiling.** Fitting alone rendered a 10px label at the fit scale — **2-3px**, a smudge
   rather than a name.

⚠️ **The interactive view is deliberately untouched.** A real browser advances animation frames
normally, so a reader opening the app or the standalone snapshot already gets a settled layout,
its animation, its labels and its zoom. Applying the capture's ceiling there would degrade a view
they can pan and toggle, for a defect they do not have.

⚠️ **Both label sets go, through the app's OWN auto-off mechanism** rather than a bespoke hide on
the name layer: the interactive ceiling governs entity names *and* match keys together, and
reusing it keeps the on-screen toggles honest about what was actually drawn. The first
implementation hid only the name layer and left the match-key labels as unreadable smudges in the
captured image.

Stdlib only; the scripts are read as text or run as a subprocess, never imported from
``plugins/`` as a package (INV-108).

Run:  python3 -m unittest discover -s tests
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIZ = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "senzing_viz_server.py"
)
CAPTURE = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "capture_screenshots.py"
)
API_REF = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "skills",
    "module-03b-truthset-visualization", "visualization-api-reference.md",
)
COMPLETION = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "skills", "bootcamp-onboarding",
    "module-completion.md",
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class TheRendererHonorsTheCaptureRequest(unittest.TestCase):
    def setUp(self):
        self.text = read(VIZ)

    def test_the_capture_request_is_read_from_the_query(self):
        self.assertRegex(
            self.text, r"capture=/\[\?&\]capture=1/\.test\(location\.search\)",
            "the capture render is requested explicitly with `?capture=1`, so any language's "
            "implementation can honor the same contract (INV-299)",
        )

    def test_the_layout_is_driven_synchronously(self):
        """`simulation.tick()` in a loop — not a longer wait on animation frames."""
        self.assertRegex(
            self.text, r"for\(let i=0;i<need;i\+\+\)\{sim\.tick\(\);\}",
            "the layout must be advanced in a loop. Waiting longer cannot work: headless "
            "virtual time does not advance requestAnimationFrame, which is why the animation "
            "path got 5 of ~300 ticks at every budget from 5s to 300s.",
        )
        self.assertIn(
            "sim.stop()", self.text,
            "stop the timer before driving it by hand, or the two compete",
        )

    def test_the_tick_count_comes_from_the_simulations_own_parameters(self):
        """A hardcoded 300 would drift the day alphaDecay or alphaMin changes."""
        self.assertRegex(
            self.text,
            r"Math\.ceil\(Math\.log\(sim\.alphaMin\(\)\)/Math\.log\(1-sim\.alphaDecay\(\)\)\)",
            "derive the tick count from the simulation's own alphaMin/alphaDecay rather than "
            "writing 300 — the number is a consequence of those two values",
        )

    def test_the_finished_layout_is_fitted(self):
        # ⚠️ Asserts the fit is CALLED in the capture path, not merely defined. The first
        # version checked only that `function fitToExtent()` existed, and removing the call
        # left all fourteen tests green — a guard certifying a definition rather than a use.
        self.assertIn("function fitToExtent()", self.text)
        start = self.text.index("  if(capture){")
        block = self.text[start:self.text.index("\n  }", start)]
        self.assertIn(
            "fitToExtent();", block,
            "the capture path must CALL the fit. Presettling without fitting is strictly "
            "worse than not settling at all: the finished 85-entity layout spreads outside "
            "1440x900 and most nodes end up off-canvas, losing more of the graph than the "
            "unsettled clump did.",
        )
        self.assertIn(
            "place();", block,
            "`simulation.tick()` does not dispatch events, so positions must be applied "
            "explicitly after the loop or nothing moves",
        )
        self.assertRegex(
            self.text, r"zoomB\.transform",
            "the fit drives the app's existing zoom behavior, so the transform and the zoom "
            "state cannot disagree",
        )

    def test_the_fit_floor_allows_a_dense_graph_to_fit(self):
        self.assertRegex(
            self.text, r"scaleExtent\(\[0\.05,4\]\)",
            "a settled 85-entity layout needs well under the old 0.2 floor; clamping there "
            "leaves nodes off-canvas, which is the defect the fit exists to remove",
        )

    def test_the_fit_does_not_reserve_space_for_labels_it_will_not_draw(self):
        self.assertRegex(
            self.text, r"captureLabels\?18:0",
            "the label sits below the node, so the vertical extent is asymmetric — but only "
            "when labels are actually drawn",
        )

    def test_the_capture_ceiling_is_lower_than_the_interactive_one(self):
        both = re.search(r"const LABEL_AUTO_OFF=(\d+);", self.text)
        cap = re.search(r"const CAPTURE_LABEL_MAX=(\d+);", self.text)
        self.assertTrue(both and cap, "both ceilings must exist")
        self.assertLess(
            int(cap.group(1)), int(both.group(1)),
            "the capture ceiling must be LOWER than the interactive one (INV-299). A still "
            "image can neither zoom nor toggle, so it tolerates far fewer labels than a view "
            "the reader can explore.",
        )

    def test_both_label_sets_are_suppressed_via_the_apps_own_mechanism(self):
        """⛔ The first implementation hid only the names and left match-key smudges."""
        self.assertRegex(
            self.text, r"addGraphControls\(\"graph-container\",nodes\.length,!captureLabels\)",
            "the capture ceiling must flow through addGraphControls, which owns the auto-off "
            "for BOTH label sets and keeps the on-screen toggles consistent with what was "
            "drawn. A bespoke hide on the label layer suppresses entity names only.",
        )
        self.assertRegex(
            self.text, r"const auto=!!forceLabelsOff\|\|nodeCount>LABEL_AUTO_OFF",
            "an explicit override parameter, rather than passing a faked node count — so the "
            "function keeps telling the truth about the graph it was given",
        )

    def test_the_interactive_view_is_not_affected(self):
        """INV-299's carve-out: the defect is capture-only."""
        start = self.text.index("const capture=/[?&]capture=1/")
        window = self.text[max(0, start - 900):start + 200]
        self.assertRegex(
            window, r"(?i)interactive artifact is NOT affected|capture-only",
            "the reason the interactive view is excluded must be stated where the flag is "
            "read: a real browser advances animation frames normally, so a reader opening the "
            "app or the snapshot already gets a settled layout.",
        )


class TheCaptureRequestsThatRender(unittest.TestCase):
    def setUp(self):
        self.text = read(CAPTURE)

    def test_a_file_snapshot_url_carries_the_request(self):
        self.assertRegex(
            self.text, r'_to_url\(str\(temp\)\) \+ "\?capture=1"',
            "the standalone snapshot is the artifact the recap embeds, and it is loaded over "
            "file: — Chrome exposes the query there, and without it the capture gets ~5 of "
            "~300 layout ticks",
        )

    def test_a_live_server_url_carries_the_request(self):
        start = self.text.index("def _tab_url")
        block = self.text[start:start + 900]
        self.assertRegex(
            block, r'"capture": "1"',
            "Module 7 and Module 3b capture against a live server too; the same render is "
            "owed there (INV-299)",
        )


class TheRuleIsMirroredForOtherLanguages(unittest.TestCase):
    """INV-002/INV-090: the visualization contract binds every implementation."""

    def test_the_contract_states_all_three_parts(self):
        text = read(API_REF)
        for needle, why in (
            (r"(?i)capture-oriented render", "the rule's subject"),
            (r"(?i)synchronously", "part (a) — drive the layout, do not wait"),
            (r"(?i)\*\*fitting\*\*|fitting the finished layout", "part (b) — fit it"),
            (r"(?i)capture ceiling", "part (c) — a lower label ceiling"),
            (r"(?i)leave the interactive view alone", "the carve-out"),
        ):
            with self.subTest(needle=needle):
                self.assertRegex(text, needle, why)

    def test_the_contract_says_all_three_or_none(self):
        self.assertRegex(
            read(API_REF), r"(?i)all three, or none",
            "each requirement masked the next, so an implementation that adopts one and not "
            "the others produces a worse artifact than it started with — settling without "
            "fitting loses most nodes off-canvas",
        )

    def test_module_completion_no_longer_credits_a_settle_budget(self):
        """The reassurance this spec was written against."""
        text = read(COMPLETION)
        self.assertNotIn(
            "the helper gives animated tabs a", text,
            "that wording credited a longer settle budget with handling this. The budget "
            "never handled it — the layout advanced ~5 ticks at every budget.",
        )
        self.assertRegex(
            text, r"(?i)capture-oriented\s+render",
            "the step must describe what actually happens now, and cite the rules",
        )


if __name__ == "__main__":
    unittest.main()
