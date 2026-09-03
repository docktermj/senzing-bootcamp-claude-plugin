"""Node labels must be painted after every circle, in a layer of their own.

A node's circle was drawn over an adjacent node's text label, cutting off the start of the
entity name -- observed on the **smallest possible graph, 2 entities**, so a base case rather
than a crowding effect. ``Aurelia B Quorndon`` rendered as ``relia B Quorndon``.

⛔ **The cause is paint order, and it is visible in the code rather than inferred.** Labels were
a ``<text>`` child of each per-datum ``<g class="node">``, so the emitted order is
node1-circle, node1-text, node2-circle, node2-text -- and node 2's disc paints over node 1's
label. The per-node ``dy`` was already ``radius(d)+11``, i.e. already radius-scaled, so a node
never occluded *its own* label and the offset was never the defect. (The spec listed the
constant-offset theory first; it is wrong.)

⚠️ **What this guard does NOT assert, stated so the gap is loud.** It checks the structure, not
the pixels. A pixel assertion needs Pillow, a headless browser, a live Senzing engine and a
loaded repository -- and the suite is offline and stdlib-only (INV-108), so it cannot require
any of them. The pixel measurement was taken by hand at implementation time and lives in
``.claude/skills/dry-run/measure_label_occlusion.py`` so a phase-2 run can repeat it. Measured
on Senzing 4.4.0 (build 4.4.0.26242), 4 records -> 2 entities, 1440x900, minimum distance from
any node circle to a *neighbor's* label glyphs:

===================================  ==========
render                               clearance
===================================  ==========
committed code, converged               3.0 px
this fix, 8s budget (mid-settle)       35.9 px
this fix, 30s budget (settled)         55.7 px
===================================  ==========

⚠️ **The visible clipping did not reproduce at that fixture and viewport** -- the layout cleared
the label band by 3 px rather than crossing it. So the pixel numbers are evidence about the
*margin*, which was essentially zero, not a reproduction of the reported glyph loss. The
structural defect below is confirmed independently by reading the emitted order.

Stdlib only; the script is read as text and never imported (INV-108).

Run:  python3 -m unittest discover -s tests
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIZ = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp", "scripts", "senzing_viz_server.py")
API_REF = os.path.join(
    REPO_ROOT, "plugins", "senzing-bootcamp", "skills",
    "module-03b-truthset-visualization", "visualization-api-reference.md",
)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class LabelsAreAppendedAfterTheNodeGroup(unittest.TestCase):
    def setUp(self):
        self.text = read(VIZ)

    def test_labels_live_in_their_own_group(self):
        self.assertRegex(
            self.text,
            r'root\.append\("g"\)\.attr\("class","node-labels"\)',
            "node labels must be appended to a group of their own. As a `<text>` child of each "
            "per-datum `<g class=\"node\">` the emitted order is circle,text,circle,text — so a "
            "later node's disc paints over an earlier node's label.",
        )

    def test_the_label_group_comes_after_the_node_group(self):
        """Document order IS the guarantee — asserted by position, not by eye."""
        node_group = self.text.index('const node=root.append("g")')
        label_group = self.text.index('root.append("g").attr("class","node-labels")')
        self.assertLess(
            node_group, label_group,
            "the label group must be appended AFTER the node group. SVG paints in document "
            "order, so a label layer emitted first is painted under every circle and the "
            "defect is unchanged — while every string is still present in the DOM.",
        )

    def test_no_text_is_appended_to_the_per_datum_node_group(self):
        """The exact regression: putting labels back inside `node`."""
        self.assertNotRegex(
            self.text,
            r'node\.append\("text"\)',
            "`node.append(\"text\")` puts the label back inside the per-datum group and "
            "restores the occlusion. The label group is the fix; this is what it replaced.",
        )

    def test_labels_are_positioned_by_their_own_nodes_radius(self):
        """Out of the group they no longer inherit its transform, so tick must place them."""
        self.assertRegex(
            self.text,
            r'label\.attr\("x",function\(d\)\{return d\.x;\}\)\s*\n\s*'
            r'\.attr\("y",function\(d\)\{return d\.y\+radius\(d\)\+11;\}\)',
            "a label outside the node group inherits no transform, so the tick handler must "
            "set x/y — and the y offset stays the node's OWN radius plus a constant, which is "
            "what the `dy` did before and was never the defect.",
        )


class TheHideLabelsSelectorFollowedTheLabelsOut(unittest.TestCase):
    """⛔ The coupling that nearly turned this fix into a production-scale regression.

    Above ``LABEL_AUTO_OFF`` (150 nodes) both label sets default OFF, and that works by adding
    ``hide-node-labels`` to the container and letting CSS descend to ``.node text``. Moving the
    labels out of ``.node`` without moving the selector would have left every label visible at
    production scale -- silently undoing ``visualization-legibility-at-production-scale``, which
    is already implemented and whose evidence was 2,799 entities / 4,464 relationships. Found by
    grepping for what else named the old selector, not by the spec, which does not mention it.
    """

    def setUp(self):
        self.text = read(VIZ)

    def test_the_base_style_covers_both_groups(self):
        self.assertRegex(
            self.text,
            r"\.node text,\.node-labels text\{font-size:10px",
            "the font/fill/pointer-events rule must cover the new group, or labels change "
            "appearance and start intercepting pointer events over the nodes beneath them.",
        )

    def test_the_hide_rule_covers_both_groups(self):
        self.assertRegex(
            self.text,
            r"\.hide-node-labels \.node text,\.hide-node-labels \.node-labels text\{display:none\}",
            "the auto-off at LABEL_AUTO_OFF works by descending from the container class. A "
            "rule matching only `.node text` leaves every label rendered at production scale.",
        )

    def test_the_toggle_still_targets_the_container_class(self):
        self.assertIn('classList.toggle("hide-node-labels"', self.text)


class CollideAccountsForTheLabelButOnlyWhenLabelsShow(unittest.TestCase):
    def setUp(self):
        self.text = read(VIZ)
        start = self.text.index('.force("collide"')
        self.block = self.text[start:start + 700]

    def test_collide_reads_the_label(self):
        self.assertIn(
            "nodeLabel[d.entity_id]", self.block,
            "the collision radius accounted for the circle only (`radius(d)+6`), so nothing "
            "pushed two labeled nodes apart by the width of their text. On the measured "
            "2-entity fixture that left 3 px between a circle and its neighbor's glyphs.",
        )

    def test_collide_is_gated_on_labels_being_visible(self):
        self.assertRegex(
            self.block, r"nodes\.length>LABEL_AUTO_OFF\)return r",
            "above LABEL_AUTO_OFF the labels are hidden, and inflating the collision radius "
            "for text nobody renders would over-separate the production-scale layout that "
            "`visualization-legibility-at-production-scale` tuned.",
        )

    def test_the_label_map_is_built_before_the_simulation(self):
        """The ordering the gate depends on — a JS `const` is not hoisted."""
        self.assertLess(
            self.text.index("const nodeLabel={}"),
            self.text.index("const sim=graphSim=d3.forceSimulation"),
            "`nodeLabel` is read inside the collide accessor, so it must be initialized before "
            "the simulation is constructed or the first tick throws on a `const` in TDZ.",
        )


class TheRuleIsMirroredForOtherLanguages(unittest.TestCase):
    """INV-090/INV-104/INV-124: the visualization contract binds every implementation."""

    def test_the_api_reference_states_the_paint_order_rule(self):
        text = read(API_REF)
        self.assertRegex(
            text, r"(?i)node labels are painted after every node",
            "a bootcamper building the viz server in Java reproduces the occlusion unless the "
            "rule is normative in the language-agnostic reference, not just in the Python one.",
        )

    def test_the_api_reference_warns_that_the_natural_structure_is_the_defective_one(self):
        """The rule alone is easy to satisfy accidentally-wrongly; the trap needs naming."""
        text = read(API_REF)
        self.assertRegex(
            text, r"(?i)the natural structure is the defective one",
            "one group per datum with marker-then-text inside is what a reader reaches for "
            "first, and it is exactly the bug. Stating the rule without naming the trap "
            "leaves every language implementation to rediscover it.",
        )

    def test_the_api_reference_carries_the_collision_and_hide_rules(self):
        text = read(API_REF)
        for needle, why in (
            (r"(?i)collision must account for the label's extent",
             "sizing collision from the marker alone is what left 3 px of margin"),
            (r"(?i)must follow them into the new layer",
             "the hide mechanism silently stops working when labels move layers"),
        ):
            with self.subTest(needle=needle):
                self.assertRegex(text, needle, why)


if __name__ == "__main__":
    unittest.main()
