"""A live server that ignores `?tab=` must fail the capture, not name six PNGs after it.

On 2026-08-28 a Java visualization server built to the contract — six tabs, correct
section ids, correct nav ids, correct endpoints — omitted `?tab=` deep-linking. The
capture wrote **six correctly-named PNGs that were all the Entity Graph**, reported
success for every one, exited 0, and passed the module's completion gate. Two of the six
were byte-identical; the rest differed only by the force simulation's animation frame.
The images then reach the recap captioned as tabs they do not show.

⛔ **Every check that existed passed, and each was right about its own question.**
`_tabs_present` asks whether the ids are in the markup — they were. `_tabs_applicable`
asks whether the data supports the tab — it did. The completion gate compares
`id="tab-<name>"` counts between snapshot and server — equal. Nothing asked whether the
image shows the tab it is named for, and on the `--url` path `?tab=` is the ONLY
activation mechanism: `_ACTIVATE_JS`, with its `#navbtn-` click fallback, is injected into
a temp copy of a snapshot and never runs against a live server.

Two guards, at different depths:

1. `_supports_deep_linking` — a source-level pre-flight, before any capture, so a
   non-conforming server writes nothing instead of six mislabeled files.
2. `_identical_groups` — byte-identical captures in one run, which is never a legitimate
   outcome, caught after the fact for a page that reads the query string and ignores it.

⚠️ **What this does NOT establish:** that a rendered PNG shows the requested tab. That
needs a backend able to evaluate script against a live URL (Playwright, Selenium); neither
is a bootcamp requirement, and the headless-Chrome CLI that does the capturing cannot
evaluate an expression for us. Recorded as a limit rather than implied away.

Source spec: `specs/capture-screenshots-cannot-tell-whether-the-tab-actually-changed.md`.

Run:  python3 -m unittest discover -s tests
"""
import contextlib
import http.server
import importlib.util
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts"
          / "capture_screenshots.py")

TABS = ("graph", "stats", "matchkeys", "features", "overlap", "probe")

#: A page carrying everything the older pre-flights look for: the nav buttons, the
#: sections, and an `activate()`. The ONLY thing missing is any reading of the query
#: string — which is exactly the server that shipped the defect.
NON_CONFORMING = """<!doctype html><html><body>
<nav>%s</nav>
%s
<script>
function activate(id){ document.querySelectorAll('.tab').forEach(function(s){
  s.style.display = (s.id === 'tab-' + id) ? 'block' : 'none'; }); }
function init(){ activate('graph'); }
init();
</script>
</body></html>
""" % (
    "".join('<button id="navbtn-%s">%s</button>' % (t, t) for t in TABS),
    "".join('<section class="tab" id="tab-%s">%s</section>' % (t, t) for t in TABS),
)

#: A page with NO tab bar at all — a single-page deliverable (a quality report, a mapping
#: summary), served live. It reads no query string because it has no reason to.
TABLESS = ("<!doctype html><html><body><h1>A quality report</h1>"
           "<p>No tabs at all.</p></body></html>")

#: The same page with deep-linking applied at the end of init(), per the contract.
CONFORMING = NON_CONFORMING.replace(
    "function init(){ activate('graph'); }",
    "function init(){ activate('graph');"
    " var p = new URLSearchParams(window.location.search);"
    " if (p.get('tab')) { activate(p.get('tab')); } }",
)


def load_module():
    spec = importlib.util.spec_from_file_location("capture_activation_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Server:
    """A localhost-only stub server. Local by construction, so INV-091 holds."""

    def __init__(self, body):
        self.body = body.encode("utf-8")
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith("/api/stats"):
                    payload = json.dumps({"entities": 84, "records": 159}).encode()
                    content_type = "application/json"
                else:
                    payload, content_type = outer.body, "text/html"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d/" % self.httpd.server_address[1]

    def __enter__(self):
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)


def run_capture(module, url, out_dir, backend=None):
    """Drive main() the way the module's capture step does; return (rc, stderr)."""
    original = module._BACKENDS
    if backend is not None:
        module._BACKENDS = (backend,)
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = module.main([
                "--url", url, "--out-dir", str(out_dir), "--name", "truthset",
            ])
    finally:
        module._BACKENDS = original
    return rc, err.getvalue()


def png_files(out_dir):
    return sorted(p.name for p in Path(out_dir).glob("*.png"))


class APageWithoutDeepLinkingIsRefused(unittest.TestCase):
    def test_it_exits_non_zero_and_writes_no_images(self):
        module = load_module()
        with _Server(NON_CONFORMING) as server, tempfile.TemporaryDirectory() as out:
            rc, err = run_capture(module, server.url, out)
            self.assertNotEqual(0, rc,
                                "a server that cannot select a tab still exited 0 — which "
                                "is what let six mislabeled PNGs through the gate")
            self.assertEqual([], png_files(out),
                             "files were written for a page whose tab cannot be selected; "
                             "every one of them would show the default tab")

    def test_the_message_names_activation_as_the_cause(self):
        module = load_module()
        with _Server(NON_CONFORMING) as server, tempfile.TemporaryDirectory() as out:
            _, err = run_capture(module, server.url, out)
            self.assertIn("?tab=", err)
            self.assertIn("deep-linking", err)
            self.assertNotIn("No headless screenshot capability", err)

    def test_the_manifest_records_the_actual_reason(self):
        """⛔ INV-122 — the reported reason must be the real one, not the generic one."""
        module = load_module()
        with _Server(NON_CONFORMING) as server, tempfile.TemporaryDirectory() as out:
            run_capture(module, server.url, out)
            manifest = Path(module.manifest_path(Path(out), "truthset"))
            self.assertTrue(manifest.is_file(), "no manifest was written")
            failed = json.loads(manifest.read_text(encoding="utf-8"))["failed"]
            self.assertTrue(failed, "the manifest records no failure at all")
            for entry in failed:
                self.assertIn("deep-linking", entry["reason"])
                self.assertNotIn("backend", entry["reason"])


class AConformingPageIsNotRefused(unittest.TestCase):
    """⛔ The other half — a guard that fails everything certifies nothing (INV-265)."""

    def test_it_captures_normally(self):
        module = load_module()
        counter = {"n": 0}

        def distinct_backend(url, out):
            counter["n"] += 1
            Path(out).write_bytes(b"PNG-%d" % counter["n"])
            return True

        with _Server(CONFORMING) as server, tempfile.TemporaryDirectory() as out:
            rc, err = run_capture(module, server.url, out, backend=distinct_backend)
            self.assertEqual(0, rc, "a conforming server was refused: " + err)
            self.assertTrue(png_files(out), "a conforming server captured nothing")
            self.assertNotIn("deep-linking", err,
                             "the deep-linking refusal fired on a page that reads the "
                             "query string")
            # ⚠️ Not asserting all six: `_tabs_applicable` legitimately suppresses tabs
            # whose data this stub's /api/stats does not describe, which is
            # `test_capture_suppressed_tabs.py`'s subject, not this file's.

    def test_an_unreadable_page_is_not_refused(self):
        """Best-effort, like every other pre-flight here: never block on a fetch failure."""
        module = load_module()
        self.assertTrue(module._supports_deep_linking(""))


class ATablessPageIsStillCapturedWhole(unittest.TestCase):
    """⛔ The regression this guard did not catch when it was written (2026-08-31).

    The deep-linking pre-flight was first placed ABOVE `main()`'s single-page safety net.
    `_tabs_present` correctly empties `tabs` for a page with no tab bar, the check read
    `[] != [SINGLE_PAGE_ID]` as true, and a tabless page served over http:// was refused —
    exit 1, no image — three lines above the net whose own comment says *"exiting was the
    behavior that silently cost every single-page deliverable its recap image."* Measured
    both ways: rc 0 with an image before, rc 1 with none after.

    ⚠️ **The suite was green across it, and this file is why.** Every case here drove a page
    that HAS tab controls, which is the half the pre-flight was written for; the half it
    could break went untested. A guard narrower than the code it protects certifies the case
    its author was already thinking about.
    """

    def test_it_captures_as_a_single_page_rather_than_being_refused(self):
        module = load_module()

        def backend(url, out):
            Path(out).write_bytes(b"PNG-single")
            return True

        with _Server(TABLESS) as server, tempfile.TemporaryDirectory() as out:
            rc, err = run_capture(module, server.url, out, backend=backend)
            self.assertEqual(
                0, rc,
                "a tabless page served over http:// was refused. The deep-linking "
                "pre-flight is above the single-page safety net again: " + err)
            self.assertEqual(
                ["truthset.png"], png_files(out),
                "the single-page fallback wrote no image, so this deliverable reaches the "
                "recap with no picture")
            self.assertNotIn("deep-linking", err,
                             "the deep-linking refusal fired on a page that has no tabs to "
                             "select in the first place")

    def test_the_tabbed_case_still_refuses(self):
        """Both halves in one class, so moving the check cannot satisfy one by breaking the other."""
        module = load_module()
        with _Server(NON_CONFORMING) as server, tempfile.TemporaryDirectory() as out:
            rc, err = run_capture(module, server.url, out)
            self.assertNotEqual(0, rc)
            self.assertIn("deep-linking", err)


class IdenticalCapturesAreRefused(unittest.TestCase):
    def test_byte_identical_files_are_deleted_and_reported(self):
        module = load_module()

        def same_bytes_backend(url, out):
            Path(out).write_bytes(b"the-default-tab-every-time")
            return True

        with _Server(CONFORMING) as server, tempfile.TemporaryDirectory() as out:
            rc, err = run_capture(module, server.url, out, backend=same_bytes_backend)
            self.assertNotEqual(0, rc, "identical captures exited 0")
            self.assertEqual(
                [], png_files(out),
                "byte-identical captures were kept; at most one can show the tab it is "
                "named for and nothing can say which")
            self.assertIn("byte-identical", err)

    def test_distinct_captures_are_untouched(self):
        """The grouping must not fire on a legitimate run (INV-282)."""
        module = load_module()
        with tempfile.TemporaryDirectory() as out:
            paths = []
            for i, tab in enumerate(TABS):
                path = Path(out) / f"{tab}.png"
                path.write_bytes(b"distinct-%d" % i)
                paths.append(path)
            self.assertEqual([], module._identical_groups(paths))

    def test_the_grouping_finds_a_planted_pair(self):
        """⛔ INV-265 — a scan that matches nothing certifies nothing."""
        module = load_module()
        with tempfile.TemporaryDirectory() as out:
            a, b, c = (Path(out) / n for n in ("a.png", "b.png", "c.png"))
            a.write_bytes(b"same")
            b.write_bytes(b"same")
            c.write_bytes(b"different")
            groups = module._identical_groups([a, b, c])
            self.assertEqual(1, len(groups))
            self.assertEqual({a, b}, set(groups[0]))


class TheStepNamesTheRequirementItDependsOn(unittest.TestCase):
    """⛔ INV-183 — the rule must be reachable at the step that depends on it."""

    def test_phase1_names_deep_linking_at_the_build_step(self):
        phase1 = (REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
                  / "module-03b-truthset-visualization" / "phase1-visualization.md")
        text = phase1.read_text(encoding="utf-8")
        self.assertIn("?tab=", text,
                      "the build step never names the deep-linking parameter the capture "
                      "tool depends on, so an implementer reading only the executable "
                      "file can build a server the capture cannot drive")
        self.assertIn("deep-linking", text)


if __name__ == "__main__":
    unittest.main()
