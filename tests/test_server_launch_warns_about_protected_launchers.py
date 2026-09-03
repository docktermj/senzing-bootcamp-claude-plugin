"""Starting a server is documented as a direct child, because macOS strips DYLD_* otherwise.

macOS System Integrity Protection sanitizes `DYLD_*` out of the environment whenever a
**protected** binary execs a child, and `/usr/bin/nohup`, `/usr/bin/env` and `/bin/bash` are
all protected. Demonstrated on Darwin 25.5.0 arm64, 2026-08-25:

    $ echo $DYLD_LIBRARY_PATH              -> /opt/homebrew/opt/senzing/er/lib:...
    $ bash -c 'echo $DYLD_LIBRARY_PATH'    -> (empty)
    $ nohup bash -c '...'                  -> (empty)

⛔ **The symptom points away from the cause.** It surfaces as `UnsatisfiedLinkError: no Sz in
java.library.path` from a backgrounded process whose parent shell has the variable set — so
the obvious response is `-Djava.library.path=…`, which the plugin already documents as
insufficient and which does not fix it. Nothing pointed at the launcher.

⚠️ **The plugin was already right about the hard part and this is a narrow gap.**
`module-02-sdk-setup` states correctly that `DYLD_LIBRARY_PATH` must be set at shell level
and that a JVM flag cannot repair a dynamic-linker path after start. What was missing: the
word `DYLD` appeared in exactly **one** shipped file, and the two steps that actually start a
long-running server are several modules away from it.

⚠️ **Foreground programs work throughout**, being direct children of the exporting shell, so
nothing prompts a re-read. The failure appears only when a process is backgrounded or
wrapped — exactly what starting a server is.

⚠️ What this does NOT establish: that SIP behaves this way. This suite runs on Linux, where
`DYLD_*` does not exist and the stripping cannot occur (INV-108). It asserts the guidance is
present and reachable at the step that needs it (INV-183); the behavior rests on the
reporter's demonstration and needs re-confirming on macOS.

Source spec: `specs/macos-protected-launchers-strip-dyld-from-a-backgrounded-server.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins"
#: The launcher tokens as the contract writes them — BACKTICKED, and the absolute paths.
#: ⚠️ Matching the bare word `env` is vacuous: "environment", "env script" and
#: "senzing-env.sh" all contain it, so an earlier version of this list passed its own
#: negative control when `/usr/bin/env` was deleted from the contract.
PROTECTED = ("`nohup`", "`/usr/bin/env`", "`bash -c`")


def flatten(text):
    return re.sub(r"\s+", " ", text).lower()


def contract_file():
    """The file that DEFINES the Server lifetime contract, not one that references it.

    ⚠️ Matched on the `## Server lifetime` heading. An earlier version of this helper
    matched the phrase anywhere and picked up `phase1-visualization.md`, which now cites the
    section by name — so `[0]` was whichever sorted first, and the assertions ran against the
    wrong file.
    """
    hits = [p for p in PLUGIN.rglob("*.md")
            if "__pycache__" not in p.parts
            and re.search(r"^## Server lifetime", p.read_text(encoding="utf-8"), re.M)]
    assert len(hits) == 1, f"expected exactly one Server lifetime contract, found {hits}"
    return hits[0]


def launch_sites():
    """Shipped files that start or govern a long-running server — derived, not hardcoded.

    INV-246: the spec predicted two files. Deriving the set means a third launch site added
    later is held to the same rule instead of quietly escaping it.
    """
    out = []
    for p in sorted(PLUGIN.rglob("*.md")):
        if "__pycache__" in p.parts:
            continue
        flat = flatten(p.read_text(encoding="utf-8"))
        # ⚠️ The INSTRUCTION, not the phrase. `module-03b/SKILL.md` describes the Kiro
        # mapping as "running the web service as a background process" — prose about the
        # design, not a step that launches one — and an earlier version of this matcher
        # demanded the caution there.
        # ⚠️ A site that only TEARS DOWN a server is not a launch site. `phase2-close.md`
        # cites the same contract for teardown and has no launch to warn about; demanding
        # the caution there would be noise. The tell for a launch is the instruction itself
        # or the launch-handle capture.
        launches = ("start the server as a background process", "handle at launch")
        if re.search(r"^## Server lifetime", p.read_text(encoding="utf-8"), re.M) or any(
                k in flat for k in launches):
            out.append(p)
    return out


class EveryLaunchSiteWarnsAboutProtectedLaunchers(unittest.TestCase):
    def test_the_launch_sites_are_found(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        self.assertTrue(
            launch_sites(),
            "no shipped file starts or governs a long-running server any more; the scan "
            "broke or the vocabulary moved. Re-derive it rather than deleting this guard")

    def test_each_launch_site_names_the_hazard(self):
        bad = [str(p.relative_to(REPO_ROOT)) for p in launch_sites()
               if "dyld" not in flatten(p.read_text(encoding="utf-8"))]
        self.assertEqual(
            [], bad,
            "a step that starts a long-running server never mentions DYLD, so a macOS "
            "bootcamper whose launch gets wrapped has nothing pointing at the launcher:\n  "
            + "\n  ".join(bad))

    def test_the_protected_launchers_are_named_explicitly(self):
        """'Do not wrap it' is unactionable; the three names are the actionable part."""
        for p in [contract_file()]:
            flat = flatten(p.read_text(encoding="utf-8"))
            for name in PROTECTED:
                with self.subTest(file=str(p.relative_to(REPO_ROOT)), launcher=name):
                    self.assertIn(name.lower(), flat,
                                  f"the contract does not name {name} as a protected "
                                  "launcher that strips DYLD_*. Match the backticked token, "
                                  "not the bare word — `env` alone is satisfied by "
                                  '"environment" and asserts nothing')

    def test_the_symptom_is_named(self):
        """A bootcamper searches for the error text, not for 'SIP'."""
        flat = flatten(contract_file().read_text(encoding="utf-8"))
        self.assertIn("no sz in java.library.path", flat,
                      "the contract does not name the error text the failure presents as")

    def test_it_says_the_jvm_flag_does_not_fix_it(self):
        """⛔ The obvious response is the wrong one — say so, or the reader tries it."""
        flat = flatten(contract_file().read_text(encoding="utf-8"))
        i = flat.index("no sz in java.library.path")
        window = flat[i:i + 700]
        self.assertIn("does not fix it", window,
                      "the contract names the symptom without saying that adding "
                      "-Djava.library.path does not fix it")
        # ⛔ **Assert the POINTER, never which id it carries.** This asserted `inv-179`
        # until 2026-09-03 — as a proxy for "carries a citation" — and INV-179 governs
        # SDK response flags, nothing about dynamic-linker search paths. So the guard held
        # a mis-citation in place: correcting it to INV-183, the rule that actually requires
        # a rule to be named and linked rather than restated, turned this test red. A guard
        # that pins the id it happened to find certifies the citation it found, which is the
        # one thing it cannot check. What is load-bearing is that the reader is sent to the
        # owner instead of reading a second copy of the reasoning.
        # (Source: `inv-179-is-cited-as-a-state-it-once-rule-it-does-not-contain`.)
        self.assertIn("module-02-sdk-setup", window,
                      "the reasoning is restated rather than pointing at module-02, which "
                      "owns it — a second copy is what drifts")
        self.assertRegex(window, r"inv-\d+",
                         "the pointer carries no invariant citation, so a reader cannot look "
                         "up why the rule binds (INV-183)")

    def test_the_rule_is_not_hidden_behind_a_platform_branch(self):
        """INV-001 — all three platforms are first-class; a macOS-only section hides it."""
        flat = flatten(contract_file().read_text(encoding="utf-8"))
        self.assertIn("silent on linux and windows", flat,
                      "the contract does not say the hazard is macOS-only and silent "
                      "elsewhere, which is what stops a Linux reader skipping it as N/A")
        self.assertIn("inv-002", flat,
                      "the contract does not mark the JVM error as illustration — the rule "
                      "is about the launcher, not the language")

    def test_the_concrete_launch_says_why_it_is_written_that_way(self):
        """Otherwise a later editor 'improves' the plain & into a nohup."""
        sites = [p for p in launch_sites()
                 if "as a background process" in flatten(p.read_text(encoding="utf-8"))]
        self.assertTrue(sites, "no concrete background launch remains")
        for p in sites:
            flat = flatten(p.read_text(encoding="utf-8"))
            with self.subTest(file=str(p.relative_to(REPO_ROOT))):
                self.assertIn("that is deliberate", flat,
                              "the launch line does not say the plain `&` is deliberate, so "
                              "nothing stops it being rewritten as a nohup")


if __name__ == "__main__":
    unittest.main()
