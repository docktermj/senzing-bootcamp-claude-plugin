"""Screenshot capture must find the browser Windows actually has.

`_chrome_exe()` probed two shapes: bare command names via `shutil.which()`, and
hard-coded **macOS** `/Applications/...` paths. Windows puts neither Chrome nor Edge on
`PATH`, so a Windows 11 workstation carrying *both* reported:

    No headless screenshot capability available (tried Playwright, Selenium, headless
    Chrome/Chromium, wkhtmltoimage). Skipping screenshots; keep the HTML link instead.

Nothing was missing. `C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe` and the
Edge equivalent were both on disk; `C:\\Program Files\\...` was simply never examined. Two
recap sections lost their embedded images, and the message named the wrong cause — it
invited the bootcamper to install software they already had, which is worse than "could
not find your browser" because it sends them to fix the wrong thing.

These tests cover the lookup and the reporting:

* a faked Windows layout resolves with an empty `PATH`
* candidates come from environment variables, never a hard-coded drive or `Program Files`
* a registry probe failure degrades to the path probe and never raises
* the Linux/macOS lookup and the backend order are unchanged
* the three failure reasons are distinguishable, and the no-browser one names what it
  searched
* `--virtual-time-budget` is still on the Chrome CLI argv (without it the captured tab
  body is blank, which reads as a broken app)

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SCRIPT = PLUGIN / "scripts" / "capture_screenshots.py"
MODULE_COMPLETION = PLUGIN / "skills" / "bootcamp-onboarding" / "module-completion.md"


def load_module():
    spec = importlib.util.spec_from_file_location("capture_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAP = load_module()


def windows_env(tmp):
    """The three install-root variables a Windows machine defines."""
    return {
        "PROGRAMFILES": os.path.join(tmp, "Program Files"),
        "PROGRAMFILES(X86)": os.path.join(tmp, "Program Files (x86)"),
        "LOCALAPPDATA": os.path.join(tmp, "AppData", "Local"),
    }


def fake_windows_install(tmp, install=()):
    """Create the exact files the lookup will search for; return the env to use.

    The candidate list is asked for rather than restated, so the fixture cannot drift
    from the implementation and quietly stop testing it. `install` takes "chrome" and/or
    "edge"; an empty tuple gives a Windows machine with no browser.

    Note these paths are only *strings* here — this test suite runs on POSIX, so a
    Windows-shaped relative path becomes one filename containing backslashes. That is
    fine: the lookup checks `os.path.exists`, which is exactly what is being tested.
    `pathlib` is deliberately avoided, since `Path()` would try to build a `WindowsPath`
    once `os.name` is patched.
    """
    env = windows_env(tmp)
    with mock.patch.dict(CAP.os.environ, env, clear=True):
        candidates = CAP._windows_browser_candidates()
    wanted = []
    if "chrome" in install:
        wanted.append("chrome.exe")
    if "edge" in install:
        wanted.append("msedge.exe")
    for candidate in candidates:
        if any(candidate.endswith(suffix) for suffix in wanted):
            parent = os.path.dirname(candidate)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(candidate, "w", encoding="utf-8") as handle:
                handle.write("")
    return env


def resolve_on_fake_windows(tmp, install=()):
    """`_chrome_exe()` as a Windows machine would run it: nothing on PATH, no registry."""
    env = fake_windows_install(tmp, install=install)
    with mock.patch.object(CAP.os, "name", "nt"), mock.patch.dict(
        CAP.os.environ, env, clear=True
    ), mock.patch.object(CAP.shutil, "which", return_value=None), mock.patch.object(
        CAP, "_windows_registry_browsers", return_value=[]
    ):
        return CAP._chrome_exe()


class WindowsInstallPathsAreFound(unittest.TestCase):
    """The reported machine's exact situation: installed, and not on PATH."""

    def test_finds_chrome_with_an_empty_path(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            found = resolve_on_fake_windows(tmp, install=("chrome",))
        self.assertIsNotNone(found, "Chrome on disk must be found with no PATH entry")
        self.assertTrue(found.endswith("chrome.exe"), found)

    def test_finds_edge_when_only_edge_is_installed(self):
        """Windows 11 ships Edge, so this is the near-universal case."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            found = resolve_on_fake_windows(tmp, install=("edge",))
        self.assertIsNotNone(found)
        self.assertTrue(found.endswith("msedge.exe"), found)

    def test_prefers_chrome_over_edge_when_both_are_installed(self):
        """The reported machine had both; either works, but the order must be stable."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            found = resolve_on_fake_windows(tmp, install=("chrome", "edge"))
        self.assertTrue(found.endswith("chrome.exe"), found)

    def test_returns_none_when_no_browser_exists(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(resolve_on_fake_windows(tmp, install=()))


class CandidatesComeFromTheEnvironment(unittest.TestCase):
    """A hard-coded drive or an English `Program Files` breaks localized installs."""

    def test_paths_are_built_from_environment_variables(self):
        env = {
            "PROGRAMFILES": r"D:\Programme",
            "PROGRAMFILES(X86)": r"D:\Programme (x86)",
            "LOCALAPPDATA": r"D:\Users\dana\AppData\Local",
        }
        with mock.patch.dict(CAP.os.environ, env, clear=True):
            candidates = CAP._windows_browser_candidates()
        self.assertTrue(candidates)
        for candidate in candidates:
            self.assertTrue(candidate.startswith("D:"), candidate)
        self.assertTrue(any("Programme" in c for c in candidates))

    def test_no_hard_coded_program_files_literal_in_the_source(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn(r"C:\Program Files\Google", text)
        self.assertNotIn(r"C:\Program Files (x86)\Microsoft", text)

    def test_missing_environment_variables_yield_no_candidates_and_no_error(self):
        with mock.patch.dict(CAP.os.environ, {}, clear=True):
            self.assertEqual([], CAP._windows_browser_candidates())

    def test_both_browsers_are_covered_in_every_install_root(self):
        env = {
            "PROGRAMFILES": r"C:\PF",
            "PROGRAMFILES(X86)": r"C:\PF86",
            "LOCALAPPDATA": r"C:\LA",
        }
        with mock.patch.dict(CAP.os.environ, env, clear=True):
            candidates = CAP._windows_browser_candidates()
        self.assertTrue(any("chrome.exe" in c for c in candidates))
        self.assertTrue(any("msedge.exe" in c for c in candidates))


class RegistryProbeIsBestEffort(unittest.TestCase):
    """A registry failure must degrade to the path probe, never raise."""

    def test_absent_winreg_yields_nothing(self):
        """On Linux/macOS `import winreg` fails; that is the normal case here."""
        self.assertEqual([], CAP._windows_registry_browsers())

    def test_a_raising_registry_is_swallowed(self):
        import sys as _sys

        broken = mock.MagicMock()
        broken.HKEY_LOCAL_MACHINE = 0
        broken.HKEY_CURRENT_USER = 1
        broken.OpenKey.side_effect = OSError("access denied")
        with mock.patch.dict(_sys.modules, {"winreg": broken}):
            self.assertEqual([], CAP._windows_registry_browsers())

    def test_a_registered_path_is_returned_unquoted(self):
        import sys as _sys

        registry = mock.MagicMock()
        registry.HKEY_LOCAL_MACHINE = 0
        registry.HKEY_CURRENT_USER = 1
        registry.OpenKey.return_value.__enter__.return_value = object()
        registry.QueryValue.return_value = '"E:\\Apps\\chrome.exe"'
        with mock.patch.dict(_sys.modules, {"winreg": registry}):
            found = CAP._windows_registry_browsers()
        self.assertIn("E:\\Apps\\chrome.exe", found)

    def test_chrome_exe_still_resolves_when_the_registry_raises(self):
        """The path probe is the answer; the registry is only a further fallback."""
        import sys as _sys
        import tempfile

        broken = mock.MagicMock()
        broken.HKEY_LOCAL_MACHINE = 0
        broken.HKEY_CURRENT_USER = 1
        broken.OpenKey.side_effect = OSError("boom")
        with tempfile.TemporaryDirectory() as tmp:
            env = fake_windows_install(tmp, install=("chrome",))
            with mock.patch.dict(_sys.modules, {"winreg": broken}), mock.patch.object(
                CAP.os, "name", "nt"
            ), mock.patch.dict(CAP.os.environ, env, clear=True), mock.patch.object(
                CAP.shutil, "which", return_value=None
            ):
                self.assertIsNotNone(CAP._chrome_exe())


class UnixLookupIsUnchanged(unittest.TestCase):
    """The fix must be additive: nothing about Linux/macOS may shift."""

    def test_posix_search_paths_carry_no_windows_entries(self):
        with mock.patch.object(CAP.os, "name", "posix"):
            paths = CAP._chrome_search_paths()
        self.assertNotIn("chrome.exe", " ".join(paths))
        self.assertIn("google-chrome", paths)
        self.assertIn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", paths)

    def test_bare_names_still_resolve_through_which(self):
        with mock.patch.object(CAP.os, "name", "posix"), mock.patch.object(
            CAP.shutil, "which", side_effect=lambda n: "/usr/bin/" + n if n == "chromium" else None
        ):
            self.assertEqual("chromium", CAP._chrome_exe())

    def test_macos_absolute_path_still_resolves(self):
        macos = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        with mock.patch.object(CAP.os, "name", "posix"), mock.patch.object(
            CAP.shutil, "which", return_value=None
        ), mock.patch.object(CAP.os.path, "exists", side_effect=lambda p: p == macos):
            self.assertEqual(macos, CAP._chrome_exe())

    def test_backend_order_is_unchanged(self):
        names = [getattr(b, "__name__", "") for b in CAP._BACKENDS]
        self.assertEqual(
            ["_capture_playwright", "_capture_selenium", "_capture_chrome_cli",
             "_capture_wkhtmltoimage"],
            names,
        )


class FailureReasonsAreDistinguishable(unittest.TestCase):
    """INV-122: the reason reported must be the reason that occurred."""

    def _capture_nothing(self, browser):
        """Run main() with every backend failing; return stderr."""
        import io
        import tempfile
        from contextlib import redirect_stderr

        fixture = (
            '<html><body><section id="tab-graph"></section>'
            '<section id="tab-stats"></section></body></html>'
        )
        original = CAP._BACKENDS
        CAP._BACKENDS = tuple(lambda url, out: False for _ in original)
        buffer = io.StringIO()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                html = Path(tmp) / "app.html"
                html.write_text(fixture, encoding="utf-8")
                with mock.patch.object(CAP, "_chrome_exe", return_value=browser):
                    with redirect_stderr(buffer):
                        code = CAP.main(
                            ["--html", str(html), "--out-dir", str(Path(tmp) / "out"),
                             "--name", "viz", "--tabs", "graph,stats"]
                        )
        finally:
            CAP._BACKENDS = original
        return code, buffer.getvalue()

    def test_no_browser_names_the_locations_searched(self):
        code, stderr = self._capture_nothing(browser=None)
        self.assertEqual(2, code)
        self.assertIn("No headless screenshot capability available", stderr)
        self.assertIn("searched:", stderr)
        self.assertIn("google-chrome", stderr)

    def test_browser_found_but_capture_failed_is_reported_differently(self):
        code, stderr = self._capture_nothing(browser="/usr/bin/chromium")
        self.assertEqual(2, code)
        self.assertIn("/usr/bin/chromium", stderr)
        self.assertNotIn("No headless screenshot capability available", stderr)

    def test_browser_found_message_does_not_send_the_reader_to_install(self):
        _, stderr = self._capture_nothing(browser="/usr/bin/chromium")
        self.assertIn("not a missing install", stderr)

    def test_neither_message_suggests_installing_a_browser(self):
        """Capture is dependency-optional (INV-122): never an install instruction."""
        for browser in (None, "/usr/bin/chromium"):
            _, stderr = self._capture_nothing(browser=browser)
            lowered = stderr.lower()
            self.assertNotIn("pip install", lowered)
            self.assertNotIn("playwright install", lowered)
            self.assertNotIn("scoop install", lowered)

    def test_module_completion_tells_the_reader_to_read_the_reason(self):
        text = MODULE_COMPLETION.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?i)three reasons|no browser was found")
        self.assertRegex(text, r"(?i)do \*\*not\*\* install|do not install")


class VirtualTimeBudgetIsStillPassed(unittest.TestCase):
    """Without it Chrome captures before the async data load: a blank tab body."""

    def test_chrome_cli_argv_carries_virtual_time_budget(self):
        seen = {}

        def fake_run(argv, **kwargs):
            seen["argv"] = argv
            return mock.MagicMock(returncode=0)

        with mock.patch.object(CAP, "_chrome_exe", return_value="/usr/bin/chromium"), \
                mock.patch.object(CAP.subprocess, "run", side_effect=fake_run):
            CAP._capture_chrome_cli("http://localhost:8080/?tab=stats", Path("/nonexistent/x.png"))

        argv = seen["argv"]
        self.assertTrue(
            any(str(a).startswith("--virtual-time-budget=") for a in argv),
            "the Chrome CLI path must pass --virtual-time-budget: %r" % (argv,),
        )

    def test_the_budget_is_a_positive_number_of_milliseconds(self):
        self.assertGreater(CAP._CHROME_VIRTUAL_TIME_MS, 1000)


if __name__ == "__main__":
    unittest.main()
