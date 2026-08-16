"""The server's DEFAULT_FLAGS production caution is relayed, in both places it belongs.

`get_sdk_reference(topic='flags', …)` returns a **top-level** `caution` field — sibling to
`data[]`, not attached to any flag entry — which the plugin had never carried. Verbatim, from
`get_sdk_reference(topic='flags', filter='find_network_by_entity_id', language='python')` on
**server 1.32.9, 2026-08-12** (re-confirmed at implementation time):

    PRODUCTION GUIDANCE: *_DEFAULT_FLAGS composites are intended for getting started and
    exploration, not for production code. Their membership may change between Senzing versions,
    so code pinned to a DEFAULT flag can silently change what it returns after an upgrade — no
    error is raised. …

Why it went unnoticed for so long is structural rather than careless: every prior DEFAULT-flags
spec in this repo was *diagnostic* — a field read blank, which flag populates it — so the plugin
consumed `composite_members`, `applies_to` and `response_paths` and had no reason to read a
top-level field about a lifecycle stage (a post-graduation Senzing upgrade) that no bootcamp step
reaches.

Two properties are guarded, and the second is the one with teeth:

1. Module 7 relays the caution where composites are taught, with provenance.
2. `graduation/SKILL.md` puts the corresponding action item in `MIGRATION_CHECKLIST.md`.

The second matters because graduation copies `src/query/**` into `production/src/` verbatim, so
the exploration-shaped flag choice becomes the Bootcamper's shipped code — and the failure the
caution describes is **silent**, so nothing in that code will ever tell them.

What this must NOT do is make the bootcamp enumerate flags in its own examples. The server that
issues the caution also blesses the composites for exploration, and rewriting a learning example
into a production one is the INV-169 error of letting a correct approach look broken. So a test
below asserts the runnable example still starts from `SZ_EXPORT_DEFAULT_FLAGS`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
MODULE_07 = SKILLS / "module-07-query-visualize-discover" / "phase1-query-visualize.md"
GRADUATION = SKILLS / "graduation" / "SKILL.md"
PHASE_D = SKILLS / "module-06-data-processing" / "phaseD-validation.md"


def flat(path):
    """Blockquote markers stripped first — the caution is quoted, so `> ` sits mid-sentence."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class ModuleSevenRelaysTheCaution(unittest.TestCase):
    def test_the_production_guidance_is_quoted(self):
        text = flat(MODULE_07)
        self.assertRegex(text, r"(?i)PRODUCTION GUIDANCE")
        self.assertRegex(
            text,
            r"(?i)intended for getting started and exploration, not for production code",
        )

    def test_the_silent_upgrade_failure_is_named(self):
        """The whole reason a Bootcamper cannot discover this later from their code."""
        text = flat(MODULE_07)
        self.assertRegex(text, r"(?i)membership may change between Senzing versions")
        self.assertRegex(text, r"(?i)no error is raised")

    def test_it_carries_full_provenance(self):
        text = flat(MODULE_07)
        self.assertIn("get_sdk_reference(topic='flags'", text)
        self.assertIn("1.32.9", text)
        self.assertIn("2026-08-12", text)
        self.assertRegex(text, r"(?i)`caution`")

    def test_it_states_the_bootcamp_versus_shipped_code_split(self):
        """Relaying the caution without the split reads as 'the module is wrong'."""
        text = flat(MODULE_07)
        self.assertRegex(text, r"(?i)right\*\* thing for the bootcamp")
        self.assertRegex(text, r"(?i)leaves with the Bootcamper")

    def test_it_forbids_rewriting_the_teaching_examples(self):
        self.assertRegex(
            flat(MODULE_07),
            r"(?i)Do not rewrite this module's examples to enumerate flags",
        )


class GraduationCarriesTheChecklistItem(unittest.TestCase):
    def test_the_migration_checklist_names_the_replacement(self):
        text = flat(GRADUATION)
        self.assertRegex(text, r"(?i)Replace `\*_DEFAULT_FLAGS` composites in `production/src/`")

    def test_the_item_gives_the_reason_not_just_the_instruction(self):
        """A checklist item without its reason is the first one skipped."""
        text = flat(GRADUATION)
        self.assertRegex(text, r"(?i)membership may change between Senzing versions")
        self.assertRegex(text, r"(?i)silently change what it returns after an upgrade")

    def test_the_item_is_warning_marked(self):
        """Every not-covered-in-depth production item is ⚠️-marked in this checklist."""
        text = flat(GRADUATION)
        idx = text.index("Replace `*_DEFAULT_FLAGS`")
        self.assertIn("⚠️", text[max(0, idx - 200):idx + 40])

    def test_it_cites_the_server_and_the_module_that_teaches_the_composites(self):
        text = flat(GRADUATION)
        self.assertIn("get_sdk_reference(topic='flags'", text)
        self.assertIn("1.32.9", text)
        self.assertRegex(text, r"(?i)phase1-query-visualize\.md")

    def test_it_explains_why_this_project_is_exposed(self):
        """src/query/** is copied verbatim — that is what makes the item apply."""
        self.assertRegex(flat(GRADUATION), r"(?i)`src/query/\*\*` is copied into `production/src/`")


class TheBootcampExamplesAreUnchanged(unittest.TestCase):
    """Criterion 3: relay the caution, do not act on it inside the bootcamp."""

    def test_the_export_example_still_starts_from_the_composite(self):
        text = flat(PHASE_D)
        self.assertIn("SZ_EXPORT_DEFAULT_FLAGS", text)
        self.assertRegex(text, r"(?i)start from `SZ_EXPORT_DEFAULT_FLAGS`")

    def test_module_07_still_teaches_composite_membership(self):
        text = flat(MODULE_07)
        self.assertIn("composite_members", text)
        self.assertIn("SZ_FIND_NETWORK_DEFAULT_FLAGS", text)


if __name__ == "__main__":
    unittest.main()
