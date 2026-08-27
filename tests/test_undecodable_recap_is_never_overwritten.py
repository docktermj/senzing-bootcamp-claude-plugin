"""A recap that is not valid UTF-8 must be refused, never rewritten, and never crash a hook.

⛔ **The assertion that matters here is the byte-identity one, and it is not the obvious
assertion.** The defect this file guards has two layers, and a fix for the first one alone
makes the second one *worse*:

1. `recap_checkpoint._read` caught `OSError` only. `UnicodeDecodeError` derives from
   `ValueError`, so a cp1252-encoded `docs/bootcamp_recap.md` — what a Windows editor
   saving ANSI produces the moment the text contains a smart quote or an en dash —
   propagated and killed `precompact-recap.py`, `session-start.py` and `session-end.py`
   with a raw traceback. The PreCompact hook is the INV-059 durability mechanism, so the
   fold stopped happening exactly when the recap was about to be needed.

2. Widening that `except` to return `None` — the natural one-line patch — converts the
   crash into **silent destruction**. `fold()` reads the recap and then rewrites it in
   `"w"` mode; `None` is treated as empty, so the file is replaced by the current
   checkpoint block alone. Measured on the real scripts with only that patch applied: a
   279-byte recap holding two completed module sections became 98 bytes holding none,
   and the hook printed `folded ... (97 characters)` — a success line — while doing it.

So `_read` returns a distinct `UNREADABLE` sentinel and every caller that goes on to write
must refuse. A test that only asserted "no traceback" would pass against the destructive
patch, which is why the byte-identity and surviving-section checks below are the point.

⚠️ Driven as **subprocesses**, so nothing under `plugins/` is imported (INV-108). That also
makes these true end-to-end checks of the shipped hook entries rather than of a helper.

Enforces **INV-276** — a helper reading a bootcamper-owned artifact distinguishes absent from
present-but-unreadable, and no caller may write on the unreadable branch.

⚠️ What this file does NOT establish: that a *live* run leaves the recap intact under every
condition. It drives the shipped hook entries as subprocesses against one constructed
undecodable fixture; a different unreadable-file mode (permissions, a partial write) is not
covered here.

Source spec: `specs/a-non-utf8-recap-crashes-three-hooks-and-the-obvious-fix-destroys-it.md`.

Run:  python3 -m unittest discover -s tests
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"

#: The hook entries that reach the recap through ``recap_checkpoint._read``.
FOLDING_HOOKS = ("precompact-recap.py", "session-start.py", "session-end.py")

#: A recap with two COMPLETED module sections, and prose carrying characters that a
#: cp1252 editor writes as bytes invalid in UTF-8 (U+2019 -> 0x92, U+2014 -> 0x97).
RECAP_TEXT = """# Bootcamp Recap

## Entity Resolution Concepts — 2026-01-01T09:00:00-07:00

### Information Shared

The customer’s data – all of it – matters.

## Data collection — 2026-01-01T11:00:00-07:00

### Information Shared

Collected 3 sources, 19,500 records.
"""

CHECKPOINT_TEXT = (
    "<!-- RECAP-CHECKPOINT:START -->\n"
    "### Actions Taken\n\n"
    "Built the loader.\n"
    "<!-- RECAP-CHECKPOINT:END -->\n"
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class UndecodableRecapProject(unittest.TestCase):
    """A mid-bootcamp project whose recap exists but is not valid UTF-8."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="sbcp-undecodable-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "config").mkdir()
        (self.root / "docs" / "progress").mkdir(parents=True)
        (self.root / "config" / "bootcamp_progress.json").write_text(
            '{"current_module": "Data processing", "current_step": 3}', encoding="utf-8"
        )
        self.recap = self.root / "docs" / "bootcamp_recap.md"
        # cp1252, so the file EXISTS and is writable but cannot be decoded as UTF-8.
        self.recap.write_bytes(RECAP_TEXT.encode("cp1252"))
        (self.root / "docs" / "progress" / "recap_checkpoint.md").write_text(
            CHECKPOINT_TEXT, encoding="utf-8"
        )
        self.discoveries = self.root / "docs" / "bootcamp_data_discoveries.md"
        self.discoveries.write_bytes(RECAP_TEXT.encode("cp1252"))

    def run_script(self, name, args=(), stdin="{}"):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            cwd=self.root,
            input=stdin,
            capture_output=True,
            text=True,
        )

    # ---- layer 1: the hooks must not crash -------------------------------------

    def test_no_folding_hook_emits_a_traceback(self):
        for name in FOLDING_HOOKS:
            with self.subTest(hook=name):
                result = self.run_script(name)
                self.assertNotIn(
                    "Traceback",
                    result.stderr,
                    f"{name} crashed on a non-UTF-8 recap; a hook must absorb this "
                    f"(INV-048) rather than surface a traceback the bootcamper never asked for",
                )
                self.assertNotIn("UnicodeDecodeError", result.stderr)

    def test_the_folding_hooks_say_what_is_wrong(self):
        """A silent no-op is its own failure mode (INV-111) — name the cause."""
        for name in FOLDING_HOOKS:
            with self.subTest(hook=name):
                stderr = self.run_script(name).stderr
                self.assertIn("UTF-8", stderr, f"{name} did not name the encoding problem")

    # ---- layer 2: the destructive patch must not pass --------------------------

    def test_the_recap_is_byte_identical_after_every_folding_hook(self):
        """⛔ The negative control. Passes under a crash AND under the correct refusal;
        fails under the `except (OSError, UnicodeDecodeError): return None` patch, which
        rewrites the recap with the checkpoint block alone."""
        before = digest(self.recap)
        for name in FOLDING_HOOKS:
            self.run_script(name)
            self.assertEqual(
                before,
                digest(self.recap),
                f"{name} MODIFIED an undecodable recap. Its completed sections cannot be "
                f"read, so any rewrite destroys them — the fold must refuse and write nothing",
            )

    def test_completed_module_sections_survive(self):
        """The bootcamper-visible consequence, asserted on content rather than on a hash."""
        for name in FOLDING_HOOKS:
            self.run_script(name)
        text = self.recap.read_bytes().decode("cp1252")
        self.assertIn("## Entity Resolution Concepts", text)
        self.assertIn("## Data collection", text)
        self.assertEqual(
            2,
            text.count("\n## "),
            "a completed module section was dropped from the recap",
        )

    # ---- the PDF generators ----------------------------------------------------

    def test_recap_pdf_refuses_and_writes_nothing(self):
        result = self.run_script("generate_recap_pdf.py")
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotEqual(0, result.returncode, "a non-UTF-8 recap must not exit 0")
        self.assertIn("UTF-8", result.stderr)
        self.assertFalse(
            (self.root / "docs" / "bootcamp_recap.pdf").exists(),
            "a PDF was written from a source that could not be read (INV-110)",
        )

    def test_discoveries_pdf_refuses_and_writes_nothing(self):
        result = self.run_script("generate_discoveries_pdf.py")
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("UTF-8", result.stderr)
        self.assertFalse(
            (self.root / "docs" / "bootcamp_data_discoveries.pdf").exists(),
            "a PDF was written from a source that could not be read (INV-110)",
        )


class TheGuardDoesNotBreakTheHealthyPath(unittest.TestCase):
    """A valid UTF-8 recap must still fold, and still fold idempotently (INV-059)."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="sbcp-utf8-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "config").mkdir()
        (self.root / "docs" / "progress").mkdir(parents=True)
        (self.root / "config" / "bootcamp_progress.json").write_text(
            '{"current_module": "Data processing", "current_step": 3}', encoding="utf-8"
        )
        self.recap = self.root / "docs" / "bootcamp_recap.md"
        self.recap.write_text(RECAP_TEXT, encoding="utf-8")
        (self.root / "docs" / "progress" / "recap_checkpoint.md").write_text(
            CHECKPOINT_TEXT, encoding="utf-8"
        )

    def fold(self):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "precompact-recap.py")],
            cwd=self.root,
            input="{}",
            capture_output=True,
            text=True,
        )

    def test_a_utf8_recap_still_folds(self):
        result = self.fold()
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("folded", result.stderr, "the healthy fold path stopped working")
        self.assertIn("RECAP-CHECKPOINT", self.recap.read_text(encoding="utf-8"))

    def test_the_fold_is_still_idempotent(self):
        self.fold()
        once = digest(self.recap)
        self.fold()
        self.fold()
        self.assertEqual(once, digest(self.recap), "fold is no longer idempotent (INV-059)")

    def test_completed_sections_are_untouched_by_a_healthy_fold(self):
        self.fold()
        text = self.recap.read_text(encoding="utf-8")
        self.assertIn("## Entity Resolution Concepts", text)
        self.assertIn("## Data collection", text)

    def test_an_absent_recap_is_still_created(self):
        """`None` (absent) must stay the safe case — the sentinel is only for unreadable."""
        self.recap.unlink()
        result = self.fold()
        self.assertNotIn("Traceback", result.stderr)
        self.assertTrue(self.recap.is_file(), "an absent recap must still be created")
        self.assertIn("RECAP-CHECKPOINT", self.recap.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
