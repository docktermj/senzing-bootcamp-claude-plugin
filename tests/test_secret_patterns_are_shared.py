"""`package_bootcamp.py` and `write-gate.py` scan for the SAME secrets (INV-109).

The write gate blocks a *write* whose content matches a secret pattern. The packager excludes a
*member* whose content matches them. Two consumers of one rule -- and if they drift, the packager
quietly protects less than the gate, in the one artifact the Bootcamper hands to someone else.

⚠️ **The gate keeps its own inline copy on purpose, and this test is the reason that is safe.**
`write-gate.py` is a `PreToolUse` control: an ImportError there does not degrade to "no secret
scan", it degrades to a hook that cannot run at all, on every write in the bootcamp. The plugin
already uses exactly this shape for `brand_tokens.py`, whose palette is inlined into two generators
with `tests/test_brand_sync.py` asserting the copies stay equal. This test does that job for the
secret patterns, so the duplication cannot become drift.

⛔ The comparison is on the pattern **string**, not on behavior sampled from a few examples: a
sampled comparison passes while a fourth alternation branch exists on one side only.

Stdlib only.

Source spec: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
WRITE_GATE = SCRIPTS / "write-gate.py"


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PATTERNS = load("secret_patterns_under_test", "secret_patterns.py")


def gate_inline_pattern():
    """The alternation `write-gate.py` compiles, read out of its source.

    Read as text rather than imported: the gate reads stdin at import time, so importing it inside
    a test would consume the runner's stdin and block.
    """
    text = WRITE_GATE.read_text(encoding="utf-8")
    # The trailing comma sits at the END of the last raw-string line, not on its own line.
    match = re.search(r'if re\.search\(\s*(.*?),\s*\n\s*data,', text, re.S)
    assert match, "the write gate's secret re.search() call no longer parses out of its source"
    body = match.group(1)
    parts = re.findall(r'r"([^"]*)"', body)
    assert parts, "no raw-string fragments found in the gate's pattern"
    return "".join(parts)


class TheTwoListsAreTheSameList(unittest.TestCase):
    def test_the_pattern_strings_are_identical(self):
        self.assertEqual(
            PATTERNS.SECRET_PATTERN,
            gate_inline_pattern(),
            "the packager's secret pattern and write-gate.py's inline copy have drifted. They must "
            "stay byte-identical: the packager writes the one artifact that leaves the machine, so "
            "it must never scan for less than the gate does",
        )

    def test_the_extraction_is_not_vacuous(self):
        """INV-265 — an empty string on both sides would satisfy the equality above."""
        extracted = gate_inline_pattern()
        self.assertGreater(len(extracted), 60,
                           "the gate pattern extracted to something implausibly short; the "
                           "equality test above is comparing nothing")
        for fragment in ("PRIVATE KEY", "AKIA", "AQAAAD"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, extracted)

    def test_all_three_classes_are_named(self):
        self.assertEqual(3, len(PATTERNS.SECRET_PATTERN_NAMES))


class TheClassifierNamesTheRightClass(unittest.TestCase):
    """The manifest says WHICH kind of secret was found; a reader cannot act on "a secret"."""

    def test_each_class_is_identified(self):
        cases = (
            ("-----BEGIN RSA PRIVATE KEY-----", "PEM private key"),
            ("-----BEGIN PRIVATE KEY-----", "PEM private key"),
            ("aws_access_key_id=AKIAIOSFODNN7EXAMPLE", "AWS access-key ID"),
            ("AQAAAD" + "A" * 20, "Senzing license payload"),
        )
        for text, expected in cases:
            with self.subTest(text=text[:30]):
                self.assertEqual(expected, PATTERNS.find_secret(text))

    def test_clean_text_matches_nothing(self):
        self.assertIsNone(PATTERNS.find_secret("just some ordinary bootcamp prose"))

    def test_prose_mentioning_the_license_prefix_is_not_a_secret(self):
        """⛔ The long base64 tail is load-bearing, and this is what it buys.

        Without it the pattern fires on documentation *about* licenses and on `.lic` file paths --
        so the gate would block the plugin's own guidance and the packager would exclude it.
        """
        for benign in (
            "the documented AQAAAD prefix marks a license blob",
            "place it at licenses/g2.lic",
            "AQAAAD",
        ):
            with self.subTest(text=benign):
                self.assertIsNone(PATTERNS.find_secret(benign))

    def test_the_matched_secret_is_never_echoed_back(self):
        """The manifest may be handed to someone else; echoing the match defeats the exclusion."""
        secret = "AQAAAD" + "S3CR3T" * 6
        result = PATTERNS.find_secret(secret)
        self.assertIsNotNone(result)
        self.assertNotIn("S3CR3T", result)


if __name__ == "__main__":
    unittest.main()
