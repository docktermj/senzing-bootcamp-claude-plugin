"""Module 7 says what a project-local server must do about the D3 asset.

The reference server inlines its offline D3, resolved **relative to its own file**::

    os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "d3.v7.min.js")

That is correct for the reference, which sits beside ``scripts/vendor/``. But Module 7 does
not run the reference — it instructs the guide to *"Build it modeled on the shipped Truth Set
visualization server"*, writing a **new** server into the Bootcamper's project. A file under
``src/server/`` has no ``vendor/`` beside it, so ``__file__``-relative resolution finds
nothing, and the module never said what the project-local copy should do instead.

⚠️ Module 7 frames the visualization as something to keep and return to, so the asset has to
outlive a plugin update that moves or replaces the cached plugin directory.

⛔ A CDN fallback is not the fix: the offline guarantee (INV-091) is the reason D3 is vendored
at all, and the reference correctly refuses to render rather than reaching the network.

⚠️ The 2026-08-26 report described a ``CLAUDE_PLUGIN_ROOT`` / ``SENZING_VENDOR_D3`` lookup.
Neither string exists in the plugin today — the mechanism was rewritten to inline the asset —
so these assertions are written against what ships, not against what was reported.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "senzing-bootcamp"
MODULE_7 = (PLUGIN / "skills" / "module-07-query-visualize-discover" /
            "phase1-query-visualize.md")
SERVER = PLUGIN / "scripts" / "senzing_viz_server.py"


def flat(s):
    return re.sub(r"\s+", " ", s)


class TheAssetQuestionIsNamedWhereTheServerIsBuilt(unittest.TestCase):
    def setUp(self):
        self.text = flat(MODULE_7.read_text(encoding="utf-8"))

    def test_it_says_to_copy_the_asset_into_the_project(self):
        self.assertRegex(
            self.text, r"(?i)Copy the D3 asset into the project",
            "Module 7 must tell the guide to copy the vendored asset into the Bootcamper's "
            "project. Without it a project-local server has no asset to resolve, and the "
            "documented restart path stops working for reasons unrelated to the project.",
        )

    def test_it_names_the_reference_lookup_as_position_dependent(self):
        """⚠️ The reason, not just the rule — 'modeled on' otherwise copies the bug."""
        self.assertRegex(
            self.text, r"(?i)position-dependent and does not travel|beside \*\*its own file\*\*",
            "the instruction must say WHY: the reference finds `vendor/` beside its own "
            "file, which is correct in the plugin's layout and finds nothing anywhere else. "
            "A rule without that reason reads as boilerplate and gets dropped.",
        )

    def test_it_says_the_snapshot_is_unaffected(self):
        """Scoping the risk stops an unnecessary rebuild of the part that works."""
        self.assertRegex(
            self.text, r"(?i)standalone snapshot is unaffected",
            "the instruction must scope the exposure to the LIVE server — D3 is inlined "
            "into the standalone snapshot at build time, so only the live app is at risk.",
        )

    def test_it_keeps_the_refusal_to_render(self):
        self.assertRegex(
            self.text, r"(?i)Keep the\s+refusal-to-render|refusal-to-render when no asset is found",
            "failing visibly must survive: a CDN fallback would break the offline guarantee "
            "that is the whole reason D3 is vendored (INV-091).",
        )

    def test_it_does_not_reach_for_a_cdn(self):
        self.assertNotRegex(
            self.text, r"(?i)fall back to (?:a )?CDN|load D3 from (?:a )?CDN",
            "no guidance may offer a CDN fallback for the vendored asset.",
        )


class TheReferenceStillInlinesItsOwnAsset(unittest.TestCase):
    """The reference is correct as it stands; this change is about what is copied FROM it."""

    def setUp(self):
        self.source = SERVER.read_text(encoding="utf-8")

    def test_the_reference_resolves_its_asset_beside_itself(self):
        self.assertRegex(
            flat(self.source), r'os\.path\.dirname\(os\.path\.abspath\(__file__\)\), "vendor"',
            "the reference must keep resolving its own vendored asset beside its own file — "
            "that is correct for the plugin's layout, and it is the behavior Module 7 now "
            "tells the guide NOT to copy verbatim.",
        )

    def test_the_reference_still_inlines_rather_than_linking(self):
        self.assertRegex(
            flat(self.source), r"(?i)inline <script> carrying the vendored D3",
            "the asset must stay inlined — the offline guarantee depends on it.",
        )

    def test_the_retired_env_var_mechanism_is_still_absent(self):
        """The 2026-08-26 report's mechanism; pinned so it cannot return unnoticed."""
        for retired in ("SENZING_VENDOR_D3", "CLAUDE_PLUGIN_ROOT/scripts/vendor"):
            with self.subTest(mechanism=retired):
                self.assertNotIn(
                    retired, self.source,
                    "the env-var / plugin-root lookup was replaced by an inlined, "
                    "__file__-relative asset. If it came back, this spec's analysis — "
                    "written against the current mechanism — no longer describes what ships.",
                )


if __name__ == "__main__":
    unittest.main()
