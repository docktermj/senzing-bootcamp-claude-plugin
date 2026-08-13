"""Senzing has no license-path environment variable, so the plugin must not name one.

A custom Senzing license is an engine-config `PIPELINE` key -- `LICENSEFILE` for a `.lic`
path, `LICENSESTRINGBASE64` for an inline Base64 key. It is NOT read from the environment.
Verified against the live MCP server (1.32.9, 2026-08-13): `sdk_guide(topic='configure',
language='python', platform='linux_apt')` returns exactly two env vars, `LD_LIBRARY_PATH`
and `PYTHONPATH`, and names the license options under `PIPELINE`; `sdk_guide(topic='install',
platform='macos_arm')` agrees; `search_docs` returns no variable name at all.

The plugin got this wrong twice, in two different spellings, and neither was ever verified:

1. `SENZING_LICENSE_PATH` shipped in graduation's `.env.example` -- a fabricated variable in
   a deliverable the bootcamper carries into production. Setting it licenses nothing, and the
   failure surfaces much later as a capacity error (`SENZ9000|LIMIT`) with nothing pointing
   back at the unread variable.
2. `SENZING_LICENSE_FILE` was named in module-02's compensating note as the value `sdk_guide`
   "returns". It does not return it either.

That second one is why this test asserts a **class** rather than one token: the note meant to
prevent the confabulation had adopted a second confabulation as its premise, and instructed
the guide to confirm a name from MCP that MCP has never had. An instruction that cannot be
satisfied is worse than none -- it trains the reader to treat the surrounding ⛔ rules as
advisory (the INV-207 failure mode, reached here through a stale premise rather than a
missing one).

So: no `SENZING_LICENSE_` token in any spelling, anywhere under `plugins/`. Any future
spelling is wrong by construction, which is what makes the class cheap to guard and an
allowlist of "the two known-bad names" useless.

Enforces **INV-208**. Complements INV-080 (Senzing facts route through the MCP server) by
pinning the one fact whose correct answer is "this does not exist" -- a shape INV-080's
route-to-server rule cannot express on its own, because there is nothing for the server to
return.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
GRADUATION = PLUGIN / "skills" / "graduation" / "SKILL.md"
MODULE_02 = PLUGIN / "skills" / "module-02-sdk-setup" / "SKILL.md"

# Any SENZING_LICENSE_* environment variable is a confabulation. Matched with a word
# boundary so a prose mention of the *prefix* cannot slip through as e.g.
# "SENZING_LICENSE_PATH-style", and case-sensitively because env vars are uppercase.
LICENSE_ENV_RE = re.compile(r"\bSENZING_LICENSE_[A-Z_]*")

# The PIPELINE keys that are the real mechanism.
PIPELINE_KEYS = ("LICENSEFILE", "LICENSESTRINGBASE64")


def plugin_text_files():
    """Every Markdown and script file that ships in the plugin."""
    for path in sorted(PLUGIN.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".py", ".sh", ".json", ".yaml", ".yml"}:
            yield path


class LicenseEnvVarIsNeverNamed(unittest.TestCase):
    def test_no_senzing_license_env_var_anywhere_in_plugin(self):
        """No file under plugins/ names a SENZING_LICENSE_* variable, in any spelling."""
        offenders = []
        for path in plugin_text_files():
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                for match in LICENSE_ENV_RE.finditer(line):
                    rel = path.relative_to(REPO_ROOT)
                    offenders.append(f"{rel}:{lineno}: {match.group(0)}  |  {line.strip()[:100]}")
        self.assertEqual(
            [],
            offenders,
            "Senzing reads no license-path environment variable (server 1.32.9, 2026-08-13); a "
            "custom license is a PIPELINE key (LICENSEFILE / LICENSESTRINGBASE64) inside the "
            "engine config. Remove the variable rather than renaming it:\n  "
            + "\n  ".join(offenders),
        )

    def test_graduation_env_example_names_no_license_variable(self):
        """graduation's .env.example description must not introduce a license variable."""
        text = GRADUATION.read_text(encoding="utf-8")
        self.assertIn(
            ".env.example",
            text,
            "graduation/SKILL.md no longer describes .env.example -- retarget this test.",
        )
        # Locate the .env.example bullet and read its paragraph.
        start = text.index(".env.example")
        block = text[start : start + 1200]
        self.assertNotRegex(
            block,
            LICENSE_ENV_RE,
            "graduation's .env.example must not name a SENZING_LICENSE_* variable -- it is a "
            "production deliverable, so a fabricated variable there is the most expensive place "
            "for one.",
        )
        self.assertTrue(
            any(key in block for key in PIPELINE_KEYS),
            "graduation's .env.example guidance must show a custom license as a PIPELINE key "
            f"({' or '.join(PIPELINE_KEYS)}) so the bootcamper has the correct mechanism, not "
            "merely the absence of the wrong one.",
        )

    def test_module_02_states_the_absence_positively(self):
        """Module 02's license note must state the absence, not send the guide to confirm a name.

        The prior text instructed the guide to "Confirm the environment variable's exact name
        from MCP" -- unsatisfiable, since MCP has no such name and the note offered no fallback
        for that outcome. Pin the positive statement so the unsatisfiable form cannot return.
        """
        text = MODULE_02.read_text(encoding="utf-8")
        self.assertNotRegex(
            text,
            LICENSE_ENV_RE,
            "module-02 must not name a SENZING_LICENSE_* variable, including as the value it "
            "claims sdk_guide returns.",
        )
        self.assertRegex(
            text,
            r"no license-path environment variable",
            "module-02's Step 5 must state outright that no license-path environment variable "
            "exists, so a guide reading it has an answer rather than a lookup that cannot "
            "succeed.",
        )
        self.assertTrue(
            any(key in text for key in PIPELINE_KEYS),
            "module-02's Step 5 must name the real mechanism (a PIPELINE license key) alongside "
            "the absence.",
        )


if __name__ == "__main__":
    unittest.main()
