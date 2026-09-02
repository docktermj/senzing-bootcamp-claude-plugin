"""Graph node labels are truncated, so INV-153's distinctness rule binds them too.

INV-153 opens with a general requirement — "A truncated chart label MUST remain
distinguishable: **no two rendered labels may be identical unless their underlying
values are identical**" — and only afterwards adds that *for match keys* middle-ellipsis
is required. The 2026-07-28 deep-dive audit found the general clause implemented for
match keys alone: ``drawMatchKeys`` compared its fitted labels and disambiguated
collisions, while the entity graph cut names at a fixed 20 characters with no check. Two
organizations sharing a long prefix — ``ACME HOLDINGS INTERNATIONAL LLC`` and
``…INC`` share 27 characters — rendered as the same string, on a surface whose whole
purpose is telling entities apart.

The maintainer settled the scope question on 2026-07-29: the general clause binds.

Two halves are tested, because either alone leaves the defect reachable:

1. **The property**, against the transcribed labeling logic. The naive head-only cut is
   asserted to *fail* it, so the regression cannot return looking reasonable.
2. **The contract**, because a server generated in another language (INV-090/INV-124) is
   built from ``visualization-api-reference.md`` and never reads the Python. A rule living
   only in the reference implementation reaches no generated server — which is precisely
   how the ``NAME_FULL`` search defect shipped (INV-164).

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
SERVER = os.path.join(PLUGIN, "scripts", "senzing_viz_server.py")
CONTRACT = os.path.join(
    PLUGIN, "skills", "module-03b-truthset-visualization", "visualization-api-reference.md"
)

# Organization names of the kind Module 7 points the app at. The first three share their
# first 27 characters, so any head-only cut at 20 renders all three identically.
ORG_NAMES = [
    "ACME HOLDINGS INTERNATIONAL LLC",
    "ACME HOLDINGS INTERNATIONAL INC",
    "ACME HOLDINGS INTERNATIONAL GMBH",
    "ACME LOGISTICS LTD",
    "BRIGHTWATER MARINE",
]


def source():
    with open(SERVER, encoding="utf-8") as handle:
        return handle.read()


def contract():
    with open(CONTRACT, encoding="utf-8") as handle:
        return handle.read()


def shipped_max():
    """The constant the page actually uses, so this transcription cannot drift from it."""
    match = re.search(r"NODE_LABEL_MAX\s*=\s*(\d+)", source())
    assert match, "NODE_LABEL_MAX is gone from the reference server"
    return int(match.group(1))


def fit_node_labels(names, limit=None):
    """Transcription of the graph's node-label fitting and collision pass."""
    limit = shipped_max() if limit is None else limit
    taken, out = {}, []
    for full in names:
        label = full[: limit - 1] + "…" if len(full) > limit else full
        if label in taken and taken[label] != full:
            k = 2
            while "%s (%d)" % (label, k) in taken:
                k += 1
            label = "%s (%d)" % (label, k)
        taken[label] = full
        out.append(label)
    return out


def head_only(names, limit=None):
    """What the code did before the fix — the shape a well-meaning rewrite reaches for."""
    limit = shipped_max() if limit is None else limit
    return [(full[: limit - 1] + "…" if len(full) > limit else full) for full in names]


def collisions(names, labels):
    groups = {}
    for name, label in zip(names, labels):
        groups.setdefault(label, set()).add(name)
    return {lbl: vals for lbl, vals in groups.items() if len(vals) > 1}


class TheDistinctnessPropertyHolds(unittest.TestCase):
    """INV-153's general clause, stated as the testable property."""

    def test_no_two_labels_collide_unless_the_names_are_identical(self):
        labels = fit_node_labels(ORG_NAMES)
        found = collisions(ORG_NAMES, labels)
        self.assertEqual(
            {}, found, f"different entities render as the same node label: {found}"
        )

    def test_head_only_truncation_would_not_pass(self):
        """Guards the regression: the old code, re-derived, must fail this test."""
        labels = head_only(ORG_NAMES)
        self.assertNotEqual(
            {},
            collisions(ORG_NAMES, labels),
            "the fixture no longer exercises the defect — pick names that collide",
        )

    def test_identical_names_may_share_a_label(self):
        """"Unless their underlying values are identical" — a real duplicate is not a collision."""
        labels = fit_node_labels(["GLOBEX CORPORATION LIMITED"] * 2)
        self.assertEqual(labels[0], labels[1])

    def test_three_way_collisions_each_get_a_distinct_label(self):
        labels = fit_node_labels(ORG_NAMES[:3])
        self.assertEqual(len(set(labels)), 3, labels)

    def test_the_leading_characters_survive(self):
        """INV-153: truncation MUST NOT remove the leading characters."""
        for name, label in zip(ORG_NAMES, fit_node_labels(ORG_NAMES)):
            with self.subTest(name=name):
                self.assertTrue(
                    label.startswith(name[:8]),
                    f"{label!r} lost the head of {name!r}",
                )

    def test_short_names_are_untouched(self):
        self.assertEqual(fit_node_labels(["BRIGHTWATER MARINE"]), ["BRIGHTWATER MARINE"])

    def test_a_suffixed_label_is_not_itself_reused(self):
        """The counter must skip a suffix already taken, or two labels re-collide."""
        names = ["A" * 30 + "X", "A" * 30 + "Y", "A" * 30 + "Z"]
        labels = fit_node_labels(names)
        self.assertEqual(len(set(labels)), 3, labels)


class TheReferenceImplementsIt(unittest.TestCase):
    def test_the_fitted_labels_are_compared_not_the_names(self):
        text = source()
        self.assertRegex(text, r"NODE_LABEL_MAX\s*=\s*\d+")
        self.assertRegex(
            text,
            r"taken\[lab\]!==undefined&&taken\[lab\]!==full",
            "a genuine collision is 'same fitted label, different name'",
        )

    def test_the_node_label_is_read_from_the_computed_map(self):
        self.assertRegex(source(), r'\.text\(function\(d\)\{return nodeLabel\[d\.entity_id\];\}\)')

    def test_the_full_name_is_reachable_on_hover(self):
        """INV-153: the untruncated value must be reachable — <title> on the label itself.

        ⚠️ Rescoped 2026-09-02. The regex required `.append("title")` to be *chained directly*
        onto the `.text(...)` that sets the fitted label. When node labels moved into their own
        layer so no circle could paint over a neighbor's text
        (`entity-graph-node-occludes-a-neighbors-label-at-small-n`), the label selection had to be
        held in a variable for the tick handler to position, which puts the `<title>` on the next
        statement -- and this failed on a change that preserved the contract exactly. It pinned
        the SYNTAX; the property is that the label element itself carries a `<title>` holding the
        untruncated `entity_name`. That is what it asserts now, in either shape.
        """
        src = source()
        self.assertRegex(
            src,
            r"(?:nodeLabel\[d\.entity_id\];\}\)\s*\n?\s*\.append\(\"title\"\)"
            r"|label\.append\(\"title\"\)\.text\(function\(d\)\{return d\.entity_name)",
            "the node label needs its own <title> carrying the untruncated entity_name, not "
            "only the group tooltip. Chained onto the label's `.text(...)` or applied to the "
            "held label selection are both fine — what matters is that it is on the label "
            "element, since that is what a reader hovers to recover a truncated name.",
        )

    def test_the_old_inline_truncation_is_gone(self):
        self.assertNotRegex(
            source(),
            r"var n=d\.entity_name\|\|\"\";return n\.length>20",
            "the unchecked inline cut is the defect INV-153 forbids",
        )


class TheContractStatesItGenerally(unittest.TestCase):
    """INV-090/INV-124: a generated server is built from the contract, not the Python."""

    def test_the_general_rule_is_its_own_numbered_item(self):
        self.assertRegex(
            contract(), r"\*\*1\. Every truncated label must stay distinguishable"
        )

    def test_the_match_key_rule_is_now_the_second_item(self):
        self.assertRegex(contract(), r"\*\*2\. Match-key labels must stay distinguishable")

    def test_the_graph_default_kept_its_place_in_the_list(self):
        self.assertRegex(contract(), r"\*\*3\. The entity graph must open on something readable")

    def test_the_general_rule_names_the_surfaces_it_binds(self):
        text = re.sub(r"\s+", " ", contract())
        self.assertRegex(text, r"(?i)entity names on graph nodes")
        self.assertRegex(text, r"(?i)binds every truncated label equally")

    def test_the_general_rule_requires_comparing_fitted_values(self):
        text = re.sub(r"\s+", " ", contract())
        self.assertRegex(text, r"(?i)Compare the \*\*fitted\*\* strings, not the source values")

    def test_it_tells_a_non_python_implementer_the_rule_is_theirs(self):
        """⚠️ Rescoped 2026-09-02: this pinned `INV-090/INV-124`, and INV-124 is the wrong rule.

        INV-124 governs the recap capture's tab hooks — `tab-<id>`, `navbtn-<id>`, `activate()`,
        deep-linking. It does not say a rendering rule binds other languages; its "in whichever
        language it is generated" clause scopes its own subject. The rules that carry the
        any-language claim are INV-002 (language-agnostic) and INV-090 (the server is built in
        the chosen language, modeled on this contract) — which is the pair this file's own
        sibling guard already names in its failure message
        (`inv-124-is-cited-as-the-any-language-rule-it-is-not`). Asserting the property: the
        rule is attributed to an invariant that actually governs it, and the reader is told why
        it is stated in the contract rather than only in the Python reference.
        """
        text = re.sub(r"\s+", " ", contract())
        self.assertRegex(text, r"INV-002/INV-090|INV-090/INV-002")
        self.assertRegex(text, r"(?i)a rule that lives only in the Python reference")

    def test_the_lead_no_longer_says_there_are_two_defaults(self):
        self.assertNotRegex(
            re.sub(r"\s+", " ", contract()),
            r"Two defaults do \*\*not\*\* survive",
            "the section now carries three items",
        )


if __name__ == "__main__":
    unittest.main()
