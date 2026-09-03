"""`${SENZING_ROOT}` is never presented as *the* classpath root without naming macOS.

A **Linux + Java** bootcamper following SDK setup was handed
`java -cp "${SENZING_ROOT}/sdk/java/sz-sdk.jar:<your classes>" MyApp` as "the MCP install
guidance's example". It is an accurate quotation **of the `macos_arm` response**, and on Linux
`SENZING_ROOT` is unset: the example expands to `-cp "/sdk/java/sz-sdk.jar"`, every
`com.senzing.sdk` import fails to compile, and the failure lands in System verification a module
later, reading as a broken SDK install.

⛔ **The variable is macOS/Windows-only by the server's own anti-pattern list** — *"SENZING_DIR on
macOS → correct: SENZING_ROOT (macOS uses different env var than Windows)"* — and
`sdk_guide(topic='install', platform='linux_apt', language='java')` returns no `SENZING_ROOT`, no
jar path and no Java `gotchas[]` entry at all. The passage that quotes the macOS example must say
so, and must give the Linux reader something that works.

⚠️ **What this can and cannot check.** It is a placement check: the qualification must be *in the
passage*, because a platform caveat two sections away is not reachable from the line being copied
(INV-183). It cannot check that the Linux path is *correct* — that is an environment reading, and
it is marked observation-only in the text for exactly that reason (INV-080/INV-149).

Enforces **INV-283** — a platform- or language-scoped value an MCP route returns is attributed
to the platform or language whose response returned it, at the site it is presented, and where the
Bootcamper's own pair has no such value the step supplies that pair's form as an observation.

Source spec: `specs/java-classpath-guidance-is-macos-sourced-and-unusable-on-linux.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"

#: The variable used AS A PATH ROOT — `${SENZING_ROOT}/...`. A bare mention of the variable
#: name (naming it, warning about it, quoting a server anti-pattern) is not a classpath claim
#: and is deliberately not matched: banning the token outright would flag the very sentences
#: that warn against it, which is how a guard gets relaxed (INV-282).
ROOT_AS_PATH = re.compile(r"\$\{SENZING_ROOT\}/")
#: The qualification that has to be present with it.
NAMES_MACOS = re.compile(r"macos|macOS|mac os|darwin", re.I)
#: What a Linux + JVM reader needs instead, in the same passage.
LINUX_FORM = re.compile(r"/opt/senzing/er/sdk/java|linux_apt", re.I)


def passages(text):
    """Blank-line-delimited passages — the unit a bootcamper reads and copies from."""
    return [b for b in re.split(r"\n\s*\n", text) if b.strip()]


def shipped_files():
    return sorted(p for p in PLUGIN.rglob("*.md") if "__pycache__" not in p.parts)


def bullets(text):
    """Top-level bullets, plus any prose between them.

    ⛔ **The unit is the BULLET, not the blank-line block, and the mutation is why.** The
    classpath example lives in a bullet list whose *other* bullets mention macOS in passing —
    zsh word-splitting is described as "macOS's default shell" two bullets earlier. A
    block-scoped check therefore passed the exact defective sentence, reading a neighbor's
    incidental mention as this bullet's qualification. What a bootcamper copies is the bullet.
    """
    out, cur = [], []
    for line in text.split("\n"):
        if re.match(r"^\s{0,2}[-*] ", line):
            if cur:
                out.append("\n".join(cur))
            cur = [line]
        elif cur and (line.startswith("  ") or line.startswith("\t") or not line.strip()):
            cur.append(line)          # continuation or sub-bullet of the current bullet
        else:
            if cur:
                out.append("\n".join(cur))
            cur = []
    if cur:
        out.append("\n".join(cur))
    return [b for b in out if b.strip()]


def offenders(text):
    """Bullets using the variable as a path root without naming the platform it belongs to."""
    return [b for b in bullets(text) if ROOT_AS_PATH.search(b) and not NAMES_MACOS.search(b)]


class TheClasspathRootIsPlatformQualified(unittest.TestCase):
    def test_the_scan_finds_the_classpath_example(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        hits = [p for p in shipped_files()
                if ROOT_AS_PATH.search(p.read_text(encoding="utf-8"))]
        self.assertTrue(
            hits,
            "no shipped file uses ${SENZING_ROOT} as a path root any more. If the classpath "
            "example was removed that is fine — delete this guard deliberately rather than "
            "leaving it passing on an empty set")

    def test_no_passage_presents_it_as_the_classpath_root_without_naming_macos(self):
        bad = []
        for p in shipped_files():
            for b in offenders(p.read_text(encoding="utf-8")):
                bad.append(f"{p.relative_to(REPO_ROOT)}: {' '.join(b.split())[:200]}")
        self.assertEqual(
            [], bad,
            "a passage builds a path from ${SENZING_ROOT} without naming macOS. That variable "
            "is set by the macOS install and by nothing on linux_apt, so the example silently "
            "expands to a broken path for every Linux bootcamper:\n  " + "\n  ".join(bad))

    def test_the_classpath_passage_gives_the_linux_reader_a_path(self):
        """Naming macOS is only half — the Linux reader still needs something that works."""
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        text = m2.read_text(encoding="utf-8")
        classpath = [b for b in passages(text) if ROOT_AS_PATH.search(b) and "-cp" in b]
        self.assertTrue(classpath,
                        "the classpath example is no longer in a passage this guard can find")
        for b in classpath:
            self.assertTrue(
                LINUX_FORM.search(b),
                "the classpath passage names macOS but gives the Linux reader no path — which "
                "leaves them exactly where the defect left them, with a correct-looking example "
                "that expands to /sdk/java/sz-sdk.jar")

    def test_the_linux_path_is_marked_observation_only(self):
        """⛔ INV-080/INV-149 — no MCP route serves it, so it must not read as a server fact."""
        m2 = PLUGIN / "senzing-bootcamp" / "skills" / "module-02-sdk-setup" / "SKILL.md"
        text = m2.read_text(encoding="utf-8")
        stating = [b for b in passages(text) if "/opt/senzing/er/sdk/java" in b]
        self.assertTrue(stating, "the Linux jar path is gone from the classpath guidance")
        for b in stating:
            with self.subTest(passage=" ".join(b.split())[:60]):
                self.assertRegex(
                    " ".join(b.split()), r"observation-only|observation only",
                    "the Linux jar path is stated without marking it observation-only, so it "
                    "reads as something the server returned — and the server returns no Java "
                    "path for linux_apt at all")

    def test_the_check_fails_on_the_text_that_actually_shipped(self):
        """⛔ INV-265 — negative control, using the real sentence rather than an invented one."""
        SHIPPED_DEFECT = (
            "- **Classpath:** the MCP install guidance's example is\n"
            '  `java -cp "${SENZING_ROOT}/sdk/java/sz-sdk.jar:<your classes>" MyApp`. Note the '
            "SDK **jar** lives\n  under `sdk/java/`, while the **native** library lives under "
            "`lib/`. Confirm both paths via `sdk_guide`."
        )
        self.assertEqual(
            1, len(offenders(SHIPPED_DEFECT)),
            "the guard no longer flags the exact passage that shipped the defect — it has been "
            "narrowed until it certifies the thing it exists to catch")

    def test_the_check_passes_a_correctly_qualified_passage(self):
        """The other half: correct prose must not be flagged (INV-282)."""
        for ok in (
            'The example is the `macos_arm` response\'s: `java -cp '
            '"${SENZING_ROOT}/sdk/java/sz-sdk.jar:myapp.jar" MyApp`. On Linux the jar is at '
            "/opt/senzing/er/sdk/java/sz-sdk.jar (observation-only).",
            "Never carry ${SENZING_ROOT} to Linux — the macOS install sets it and nothing on "
            "linux_apt does.",
        ):
            with self.subTest(ok=ok[:48]):
                self.assertEqual([], offenders(ok),
                                 "correctly qualified prose is flagged, which is how a guard "
                                 "gets relaxed")


if __name__ == "__main__":
    unittest.main()
