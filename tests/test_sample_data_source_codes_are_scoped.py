"""A sample data-source tuple in shipped prose must be attributed to the language it came from.

Phase A Step 4a told the guide the registration snippet "still hardcodes the sample tuple
``("CUSTOMERS", "REFERENCE", "WATCHLIST")``". That is the **Python** snippet's tuple. Measured on
MCP server **1.36.0, 2026-09-02**, ``sdk_guide(topic='configure', language='java',
data_sources=[…])`` returns ``String[] dataSources = {"CUSTOMERS", "EMPLOYEES", "WATCHLIST"};`` --
``EMPLOYEES``, not ``REFERENCE``. A guide following the step literally on Java sent the Bootcamper
hunting for a line that is not in the response they received.

⛔ **The defect arrived through an ILLUSTRATION, not an instruction**, which is why INV-002 and
INV-090 did not catch it: the surrounding step carefully reads ``programming_language`` from
preferences and never hardcodes a language, and then hands the guide a language-specific literal
to match against. The rule the step teaches reproduced exactly on Java -- ``data_sources`` selects
the registration snippet, substitutes nothing, and ``notes`` still say *"Replace sample data source
names with your own"*. Only the illustration was wrong.

⚠️ **The tuple was not the only unscoped literal in that block.** The same paragraph named
``source_path: python/configuration/register_data_sources.py`` as though it were the path in every
language; Java's is ``java/snippets/configuration/RegisterDataSources.java`` -- a different shape,
not just a different name. Found by sweeping the block rather than fixing the line the spec
named (INV-246).

This guard scans **every** shipped Markdown file for the *claim* -- prose asserting that a
snippet hardcodes a sample tuple -- and requires a language to be named beside it. Searching
for the claim rather than for the codes is what keeps it free of false positives; see the
comment on ``CLAIM_PHRASES`` for the three narrowings that design replaced.

Stdlib only; nothing under ``plugins/`` is imported (INV-108).

Run:  python3 -m unittest discover -s tests
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
STEP_4A_FILE = os.path.join(
    PLUGIN, "skills", "module-06-data-processing", "phaseA-build-loading.md"
)

#: ⛔ **The search is INVERTED, and that is the whole design.** The obvious scan -- look for
#: `REFERENCE`/`EMPLOYEES` and demand a nearby language -- was tried and abandoned after three
#: narrowings. `REFERENCE` is also one of the Senzing demo Truth Set's own data sources
#: (`CUSTOMERS`, `REFERENCE`, `WATCHLIST`, per `get_sample_data`), so the bootcamp names it
#: legitimately throughout: recap examples, purge steps, entity-graph JSON samples. The first
#: version flagged **21** such sites; tightening the context filter twice still left two, both
#: about Truth Set *data* rather than snippet contents. A guard that needs a fourth tuning pass
#: is measuring the wrong thing.
#:
#: So: find the CLAIM, then check its attribution. The defect is never the code -- it is prose
#: asserting that an `sdk_guide` snippet *hardcodes* a particular tuple, because that assertion
#: is per-language and the page presented it as universal. Prose making no such assertion cannot
#: carry the defect however many demo codes it names, which is why this has no false positives
#: by construction rather than by exclusion list (INV-246).
#: ⚠️ Fourth iteration, and the last three are the interesting part. `hardcodes?\s+sample tuple`
#: alone flagged the *corrected* prose -- "hardcodes a sample tuple of Senzing's own demo data
#: source codes" -- which names no tuple at all and is precisely the property the fix installs.
#: The signature is a claim that names a SPECIFIC tuple: a `hardcode`/`sample tuple` phrase with
#: an actual demo-code literal close behind it. Prose stating the property has nothing behind it
#: and is correctly silent here; prose quoting one language's literal is caught.
_DEMO_CODE = r"(?:REFERENCE|EMPLOYEES|WATCHLIST)"
CLAIM_PHRASES = re.compile(
    r"(?:hardcodes?|sample tuple)[^\n]{0,40}(?:\n\s*)?[^\n]{0,120}?" + _DEMO_CODE,
    re.IGNORECASE,
)
#: A language attribution near the claim. Deliberately broad: the point is that SOME language is
#: named, not that a particular phrasing was used.
LANGUAGE_NEAR = re.compile(
    r"python|java|c#|csharp|rust|typescript|javascript|per-language|programming_language",
    re.IGNORECASE,
)
#: Window either side of the claim, in characters, within which the attribution must appear.
WINDOW = 500


def shipped_markdown():
    out = []
    for root, _dirs, files in os.walk(PLUGIN):
        if "__pycache__" in root:
            continue
        for name in files:
            if name.endswith(".md"):
                out.append(os.path.join(root, name))
    return sorted(out)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class NoShippedProseClaimsASampleTupleWithoutItsLanguage(unittest.TestCase):
    """⚠️ The site set is SCANNED for the claim shape, not for a path list (INV-246)."""

    def test_every_sample_tuple_claim_names_its_language(self):
        unscoped = []
        claims = 0
        for path in shipped_markdown():
            text = read(path)
            for m in CLAIM_PHRASES.finditer(text):
                claims += 1
                window = text[max(0, m.start() - WINDOW):m.end() + WINDOW]
                if LANGUAGE_NEAR.search(window):
                    continue
                line = text.count("\n", 0, m.start()) + 1
                unscoped.append(
                    "%s:%d — %r with no language named within %d chars"
                    % (os.path.relpath(path, REPO_ROOT), line, m.group(0).strip(), WINDOW)
                )
        self.assertEqual(
            [], unscoped,
            "Shipped prose claims a snippet hardcodes a sample tuple without saying which "
            "language's snippet. The tuples differ: Python's is "
            "(\"CUSTOMERS\", \"REFERENCE\", \"WATCHLIST\") and Java's is "
            "{\"CUSTOMERS\", \"EMPLOYEES\", \"WATCHLIST\"} on server 1.36.0, so an "
            "unattributed claim sends some Bootcampers looking for a line that is not in the "
            "response they received. Name the language, or state the property instead — a "
            "hardcoded sample tuple, and none of the passed codes anywhere:\n  "
            + "\n  ".join(unscoped),
        )
        self.assertGreater(
            claims, 0,
            "No sample-tuple claim found anywhere under plugins/. Either the phrasing changed "
            "and this scan now matches nothing — in which case fix the pattern, do NOT delete "
            "the test — or the claim was removed entirely, which is also a valid end state and "
            "makes this assertion the thing that tells you so.",
        )


class Step4aTeachesThePropertyRatherThanTheLiteral(unittest.TestCase):
    def setUp(self):
        self.text = read(STEP_4A_FILE)
        start = self.text.index("## 4a. Register the data source codes")
        # ⚠️ Bounded at the next heading, not at a character count. The first version used
        # `start + 4200` and truncated the step three lines short of the retry-loop note, so a
        # correctly-written page failed. A magic width is a guard that fails when the prose grows.
        end = self.text.index("\n## ", start + 5)
        self.step = self.text[start:end]

    def test_the_property_is_stated(self):
        """What the guide actually acts on, and the half that cannot go stale."""
        self.assertRegex(
            self.step,
            r"none of the codes you passed appears anywhere in the\s+response",
            "the discriminating property must be stated outright: the response contains a "
            "hardcoded sample tuple and none of the passed codes. That holds in every language "
            "and survives the snippet being re-authored, which no literal does.",
        )

    def test_both_languages_tuples_are_named_as_theirs(self):
        for lang, code in (("python", "REFERENCE"), ("Java", "EMPLOYEES")):
            with self.subTest(lang=lang):
                self.assertRegex(
                    self.step, r"(?s)%s.{0,400}%s" % (lang, code),
                    "if the step names a tuple it must attribute it — %r is %s's" % (code, lang),
                )

    def test_the_step_warns_against_matching_a_literal_from_the_page(self):
        self.assertRegex(
            self.step,
            r"never against a literal tuple\s+or filename from this page",
            "the instruction that closes the defect is not 'here are both tuples' but 'do not "
            "match against a literal from this page at all' — otherwise a third language "
            "reintroduces it.",
        )

    def test_the_source_path_is_not_stated_as_universal(self):
        """The literal the spec did not name: the paths differ in SHAPE, not just in name."""
        self.assertRegex(
            self.step,
            r"(?s)python/configuration/register_data_sources\.py.{0,500}"
            r"java/snippets/configuration/RegisterDataSources\.java",
            "the step told the guide to locate the snippet by `source_path` and then gave "
            "Python's path unqualified. Java's is java/snippets/configuration/… — a different "
            "shape, so a reader matching the Python path finds nothing.",
        )

    def test_the_per_language_replace_mechanics_are_noted_without_ranking(self):
        self.assertIn("SzReplaceConflictException", self.step)
        self.assertRegex(
            self.step, r"neither shape is canonical",
            "Java's snippet is the more defensive of the two, and saying so as a ranking would "
            "invite a guide to 'improve' Python's. The note records the difference and leaves "
            "the substitution rule unchanged.",
        )

    def test_the_measurement_carries_its_version_and_date(self):
        """INV-080/INV-149/INV-295: re-measured at implementation time, not copied forward."""
        self.assertRegex(
            self.step, r"server \*\*1\.36\.0, 2026-09-02\*\*",
            "the previous parenthetical said server 1.33.0, 2026-08-21 and was Python-only; "
            "both tuples were re-read at 1.36.0 before this text was written.",
        )


if __name__ == "__main__":
    unittest.main()
