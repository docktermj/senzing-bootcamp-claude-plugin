"""No shipped file states the evaluation license's duration, because the server disagrees.

Two tools on the same MCP server, queried in the same session, give different durations for
the free Senzing evaluation license. Verified on **server 1.32.9, 2026-08-12** (and again at
implementation time, same day, same versions):

- `submit_feedback` tool description, via `get_capabilities`:
  "A **10-day**, 250K-record eval license is generated and emailed with a download link."
- `sdk_guide(topic='install', platform='macos_arm', language='java')`, in its
  `engine_config_notes`: "request a free **5-day** evaluation license (250K records) right
  now using submit_feedback with category='license_request'".

The second one points at the first one to make the request while disagreeing with it about
what the request grants.

So neither figure is citable, and — this is the part that makes a guard necessary rather than
a note sufficient — the plugin's existing rule for such figures is "source them from MCP at
runtime, never a remembered figure" (`module-04-data-collection/SKILL.md`). That rule assumes
the server speaks with one voice. Here it does not, so following the rule faithfully still
produces a coin flip, and the resulting error would carry a genuine MCP citation. That is the
most durable kind of mistake this repo can make.

The plugin's silence today is deliberate, and this guard is what keeps it deliberate rather
than accidental: it fails the moment anyone helpfully adds "you'll get 10 days".

**Reported upstream** as `category='bug'` on 2026-08-12 with the maintainer's explicit
approval (no PII; INV-135 forbids routing a defect report through `license_request`). Retire
this guard, and the note in module 4, once the two tools agree — the 500-record no-license cap
is a separate, stable, MCP-confirmed fact and is deliberately NOT covered here.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"

#: A duration a reader would take as the license's term. The plural and the spelled-out forms
#: are not politeness: a mutation test caught the first version of this pattern missing
#: "The evaluation license lasts 10 days" outright, because `\bday\b` will not match "days" —
#: and the plural is the form someone writing prose naturally reaches for.
_NUM = r"(?:\d+|five|ten|fourteen|thirty)"
DURATION = re.compile(
    r"(?i)\b%s\s*[-\s]\s*days?\b|\bdays?\s+(?:evaluation|eval|trial)\b" % _NUM
)

#: Only durations in license context are this guard's business.
LICENSE_VOCAB = re.compile(r"(?i)licen[cs]e|\beval\b|evaluation|trial")

#: The contested-fact note itself must quote BOTH figures to be useful, so it necessarily
#: contains durations. It is exempt only while it does what a contested-fact note must:
#: name the disagreement and forbid quoting a figure. Losing these words un-exempts it.
CONTESTED = re.compile(
    r"(?i)contradicts itself|contested|two answers|not\s+citable|no figure\s+is citable|"
    r"never state the license's duration"
)

WINDOW = 320


def shipped_markdown():
    return sorted(PLUGIN.rglob("*.md"))


def offences():
    found = []
    for path in shipped_markdown():
        flat = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
        for match in DURATION.finditer(flat):
            window = flat[max(0, match.start() - WINDOW):match.end() + WINDOW]
            if not LICENSE_VOCAB.search(window):
                continue
            if CONTESTED.search(window):
                continue
            found.append("%s: %s" % (path.relative_to(REPO_ROOT), window[:200]))
    return found


class NoShippedFileStatesTheDuration(unittest.TestCase):
    def test_the_scan_reaches_the_shipped_prose(self):
        files = shipped_markdown()
        self.assertGreater(len(files), 30, "the shipped markdown corpus was not found")
        corpus = " ".join(p.read_text(encoding="utf-8") for p in files)
        self.assertRegex(corpus, LICENSE_VOCAB, "no licence vocabulary found — scan is vacuous")

    def test_no_duration_is_stated(self):
        found = offences()
        self.assertEqual(
            [],
            found,
            "A shipped file states an evaluation-license duration. Two MCP tools disagree "
            "about it (submit_feedback: 10-day; sdk_guide install notes: 5-day — server "
            "1.32.9, 2026-08-12), so any figure here is unciteable however it is sourced. "
            "Say 'time- and volume-limited' and let Senzing's email state the terms:\n  "
            + "\n  ".join(found),
        )


class TheOmissionIsRecordedAsADecision(unittest.TestCase):
    """An unexplained omission is indistinguishable from an oversight, and gets 'fixed'."""

    NOTE_HOME = PLUGIN / "skills" / "module-04-data-collection" / "SKILL.md"

    def test_the_licence_step_records_the_contradiction(self):
        flat = re.sub(r"\s+", " ", self.NOTE_HOME.read_text(encoding="utf-8"))
        self.assertRegex(flat, CONTESTED, "the contested-fact note is missing")
        self.assertIn("1.32.9", flat)
        self.assertIn("2026-08-12", flat)

    def test_the_note_names_both_figures_and_both_tools(self):
        flat = re.sub(r"\s+", " ", self.NOTE_HOME.read_text(encoding="utf-8"))
        for token in ("10-day", "5-day", "submit_feedback", "sdk_guide"):
            self.assertIn(token, flat, "a contested-fact note must let a reader re-check it")

    def test_the_note_says_what_to_say_instead(self):
        flat = re.sub(r"\s+", " ", self.NOTE_HOME.read_text(encoding="utf-8"))
        self.assertRegex(flat, r"(?i)time- and volume-limited")

    def test_the_500_record_cap_is_untouched_and_still_cited(self):
        """The stable fact must not be collateral damage of suppressing the unstable one."""
        phase_a = PLUGIN / "skills" / "module-06-data-processing" / "phaseA-build-loading.md"
        flat = re.sub(r"\s+", " ", phase_a.read_text(encoding="utf-8"))
        self.assertIn("500", flat)
        self.assertRegex(flat, r"(?i)senzing MCP server|MCP")


if __name__ == "__main__":
    unittest.main()
