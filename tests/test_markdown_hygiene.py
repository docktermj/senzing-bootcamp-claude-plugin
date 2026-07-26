"""Shipped Markdown carries no mangled punctuation or trailing whitespace.

The cheapest of the six guards, and it pins a defect that reached the Bootcamper's ears.
A mechanical em-dash replacement left four sites reading ``… the common attributes , ``
with the comma orphaned after a space and trailing whitespace behind it. Three sat inside
quoted dialogue the guide reads aloud:

    "I'll use Entity [ID], which contains records from [Source A] and [Source B] ,
    let's see why Senzing decided these belong to the same real-world entity."

Nothing failed. The Markdown is valid, the meaning survives, and no reviewer scanning for
logic errors looks at spacing — which is exactly why it needs a machine. INV-004 is the
production-ready bar, and a guide that speaks mangled punctuation is not at it.

Scoped to what was actually found, so it stays a hygiene check rather than a style
opinion: space-before-comma, and trailing whitespace. Both are unambiguous defects in this
codebase — the audit sweep found zero legitimate instances of either.

Run:  python3 -m unittest discover -s tests
"""
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"


def shipped_markdown():
    for path in sorted(PLUGIN.rglob("*.md")):
        if "pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        yield path


class TestPunctuationHygiene(unittest.TestCase):

    def test_no_space_before_a_comma(self):
        offenders = []
        for path in shipped_markdown():
            for n, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if " ," in line:
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT)}:{n}: {line.strip()[:100]}"
                    )
        self.assertEqual(
            [],
            offenders,
            "space before a comma — the signature of a mechanical em-dash replacement, "
            "which put mangled punctuation into spoken dialogue:\n  "
            + "\n  ".join(offenders),
        )

    def test_no_trailing_whitespace(self):
        offenders = []
        for path in shipped_markdown():
            for n, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if line != line.rstrip():
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{n}")
        self.assertEqual(
            [],
            offenders,
            "trailing whitespace in shipped Markdown (a two-space Markdown line break is "
            "not used anywhere in this codebase, so these are edit residue):\n  "
            + "\n  ".join(offenders),
        )


class TestTheScanIsNotVacuous(unittest.TestCase):
    """A glob that stops matching would make both checks pass silently."""

    def test_markdown_is_actually_being_scanned(self):
        files = list(shipped_markdown())
        self.assertGreaterEqual(
            len(files),
            30,
            f"only {len(files)} shipped .md files found; the glob has drifted and these "
            "checks are now vacuous",
        )

    def test_the_known_regression_would_be_caught(self):
        """Self-check on the exact string that shipped."""
        regression = "explain the common attributes , "
        self.assertIn(" ,", regression)
        self.assertNotEqual(regression, regression.rstrip())


if __name__ == "__main__":
    unittest.main()
