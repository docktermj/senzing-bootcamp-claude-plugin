"""A busy port can still accept a bind, so the server asks who is answering.

Enforces **INV-260** — bind loopback explicitly, never the wildcard, and confirm the process
answering `/api/stats` is the one just started by comparing a per-process nonce; a
disagreement stops rather than warns. Registered 2026-08-17, after the production-readiness
audit found the rule shipped and unregistered.

`lsof -ti:8080` reported port 8080 busy — an unrelated `VizServer` from another project,
started three weeks earlier, bound to `127.0.0.1:8080`. The bootcamp's server bound
**successfully anyway**, to `*:8080`, because a loopback bind and a wildcard bind do not
collide. Two processes then listened on one port and either could answer a localhost
request. The first `/api/stats` probe happened to reach the new server, which is the only
reason it looked fine.

⛔ **Had the browser reached the other one**, the Bootcamper would have been shown a
three-week-old dataset under their own project's title, every number on the page someone
else's, and the keepsake screenshots would have captured it. The existing guidance treated
a port conflict as a *bind failure*; this is a success that produces nondeterministic
results, which is strictly worse — a failure stops the step and this does not.

⚠️ **The bundled Python server was already safe and was not the defect.** It has always
bound `127.0.0.1` explicitly. The Bootcamper was running their **own** implementation,
ported from the reference per Module 7 step 3c, and the any-language contract never stated
the bind host — so a Java port using the idiomatic `InetSocketAddress(port)`, a wildcard
bind, was fully conformant and carried the defect. That is the INV-002 boundary exactly: a
rule constraining the Bootcamper's code must be stated as behavior in the contract, never
only in the Python reference.

⛔ **The two remedies cover opposite directions and neither alone is enough.** A loopback
bind makes a colliding *loopback* listener fail cleanly; it does nothing when the
pre-existing listener is *wildcard*-bound, where our loopback bind is the one that succeeds
alongside it. Only asking which server answered covers both — so the identity probe is
tested here against a **constructed two-listener condition**, not against the happy path.

Source spec: `specs/the-viz-contract-never-states-the-bind-host-so-a-port-conflict-can-succeed.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import json
import socket
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SERVER = PLUGIN / "scripts" / "senzing_viz_server.py"
CONTRACT = (PLUGIN / "skills" / "module-03b-truthset-visualization" /
            "visualization-api-reference.md")


def load_server():
    spec = importlib.util.spec_from_file_location("viz_server_under_test", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["viz_server_under_test"] = module
    spec.loader.exec_module(module)
    return module


VIZ = load_server()


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Foreign(BaseHTTPRequestHandler):
    """A stranger's server: valid, answers /api/stats, and is not us."""

    nonce = "a-different-server"

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler's interface
        body = json.dumps({"records_total": 100, "entities_total": 80,
                           "server_nonce": self.nonce}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class Ours(Foreign):
    """Same shape, but carrying this process's real nonce."""

    @property
    def nonce(self):
        return VIZ.SERVER_NONCE


class serve_on:
    """Run `handler` on `port` for the duration of the block."""

    def __init__(self, handler, port):
        self.handler, self.port = handler, port

    def __enter__(self):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", self.port), self.handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()


class TheBindHostIsPinned(unittest.TestCase):
    """⛔ A future edit must not widen this to the wildcard address."""

    def test_the_constant_is_loopback(self):
        self.assertEqual("127.0.0.1", VIZ.BIND_HOST)

    def test_the_server_binds_the_constant_not_a_literal_wildcard(self):
        source = SERVER.read_text(encoding="utf-8")
        self.assertIn("ThreadingHTTPServer((BIND_HOST, args.port), handler)", source)

    def test_no_wildcard_bind_address_appears_in_the_server(self):
        source = SERVER.read_text(encoding="utf-8")
        for wildcard in ('("", args.port)', '("0.0.0.0"', "'0.0.0.0'"):
            with self.subTest(wildcard=wildcard):
                self.assertNotIn(wildcard, source)

    def test_the_reason_is_recorded_beside_the_constant(self):
        """The rule will be edited again; the reasoning will not be rediscovered."""
        source = " ".join(SERVER.read_text(encoding="utf-8").split())
        self.assertIn("wildcard bind does NOT collide with an existing loopback listener",
                      source)


class TheStatsPayloadCarriesAPerProcessNonce(unittest.TestCase):

    def test_the_nonce_is_exposed(self):
        source = SERVER.read_text(encoding="utf-8")
        self.assertIn('"server_nonce": SERVER_NONCE', source)

    def test_it_is_unique_per_process(self):
        """Two loads of the module must not agree, or the probe proves nothing."""
        other = load_server()
        self.assertNotEqual(VIZ.SERVER_NONCE, other.SERVER_NONCE)


class TheIdentityProbeDetectsAForeignServer(unittest.TestCase):
    """⛔ Negative control — the two-listener condition, constructed."""

    def test_a_foreign_server_on_the_port_is_detected(self):
        port = free_port()
        with serve_on(Foreign, port):
            self.assertFalse(
                VIZ.confirm_server_identity(port),
                "the probe accepted a server that is not this process — the Bootcamper "
                "would be shown a stranger's data under their own project's title")

    def test_our_own_server_is_accepted(self):
        """Fixture control: without this, the test above passes for the wrong reason."""
        port = free_port()
        with serve_on(Ours, port):
            self.assertTrue(VIZ.confirm_server_identity(port))

    def test_a_server_with_no_nonce_at_all_is_rejected(self):
        class Nonceless(Foreign):
            nonce = None

        port = free_port()
        with serve_on(Nonceless, port):
            self.assertFalse(VIZ.confirm_server_identity(port))

    def test_an_unanswerable_probe_is_a_failure_not_a_pass(self):
        """⚠️ The failure mode looks like success, so silence is not permission."""
        self.assertFalse(VIZ.confirm_server_identity(free_port(), timeout=0.5))

    def test_the_conflict_report_names_the_port_and_both_figures(self):
        port = free_port()
        import io
        import contextlib
        buffer = io.StringIO()
        with serve_on(Foreign, port), contextlib.redirect_stderr(buffer):
            VIZ.confirm_server_identity(port)
        message = buffer.getvalue()
        self.assertIn(str(port), message)
        self.assertIn(VIZ.SERVER_NONCE, message)
        self.assertIn("a-different-server", message)
        self.assertIn("DIFFERENT server", message)


class TheStartupSequenceIsOrderedCorrectly(unittest.TestCase):
    """⚠️ Source-order assertions, and the reason they are source-order.

    `main()`'s serve path needs a live Senzing engine, so nothing in this offline suite
    (INV-108) can run it end to end. What IS proven at runtime, above, is the mechanism
    it wires together: a `ThreadingHTTPServer` served from a background thread, probed,
    then shut down — the `serve_on` helper does exactly that and every test using it
    passes. These assertions pin the ORDER of the wiring, which is the part that decides
    whether the Bootcamper can ever see a URL that was not checked.
    """

    def setUp(self):
        self.source = SERVER.read_text(encoding="utf-8")
        self.main = self.source[self.source.index("    handler = make_handler("):]

    def test_the_probe_runs_before_the_url_is_printed(self):
        probe = self.main.index("confirm_server_identity(args.port)")
        url = self.main.index('print(f"Visualization running:')
        self.assertLess(probe, url,
                        "the URL is printed before the identity probe — a Bootcamper "
                        "could open a page served by another process")

    def test_a_failed_probe_returns_non_zero_without_serving(self):
        probe = self.main.index("if not confirm_server_identity(args.port):")
        # Slice to the branch's own end, not a fixed window: a wider window runs past
        # `return 1` into the success path and asserts about the wrong code.
        block = self.main[probe:self.main.index("return 1", probe) + len("return 1")]
        self.assertIn("httpd.shutdown()", block)
        self.assertIn("httpd.server_close()", block)
        self.assertNotIn("Visualization running", block)

    def test_the_server_is_shut_down_before_its_socket_is_closed(self):
        tail = self.main[self.main.index("finally:"):]
        self.assertLess(tail.index("httpd.shutdown()"), tail.index("httpd.server_close()"),
                        "server_close runs while serve_forever is still looping")

    def test_a_bind_failure_is_reported_and_does_not_proceed(self):
        self.assertIn("could not bind {BIND_HOST}:{args.port}", self.main)
        self.assertIn("--port", self.main)


class TheContractStatesBothRulesForEveryLanguage(unittest.TestCase):
    """INV-002/INV-090/INV-124 — the defect was a conformant non-Python implementation."""

    def setUp(self):
        self.text = " ".join(CONTRACT.read_text(encoding="utf-8").split())

    def test_the_loopback_bind_is_required_with_its_reason(self):
        self.assertIn("Bind the LOOPBACK interface explicitly", self.text)
        self.assertIn("does **not** collide with an existing loopback listener",
                      self.text)

    def test_it_names_the_idiomatic_wrong_form_in_other_languages(self):
        """The rule a faithful port gets wrong by writing the shorter thing."""
        for idiom in ("new InetSocketAddress(port)", 'server.listen(port, "127.0.0.1")',
                      "IPAddress.Loopback"):
            with self.subTest(idiom=idiom):
                self.assertIn(idiom, self.text)

    def test_a_successful_bind_is_not_treated_as_proof_the_port_was_free(self):
        self.assertIn("A successful bind is NOT proof the port was free", self.text)

    def test_the_identity_probe_is_required_and_specifies_what_it_compares(self):
        self.assertIn("probe `/api/stats` and confirm the responder is the server just "
                      "started", self.text)
        self.assertIn("Compare the nonce, not the record count", self.text)

    def test_a_disagreement_stops_rather_than_warns(self):
        self.assertIn("On disagreement, STOP and report the conflict", self.text)
        self.assertIn("must not degrade to a warning", self.text)

    def test_it_explains_why_both_remedies_are_needed(self):
        self.assertIn("they cover opposite directions", self.text)

    def test_the_rules_are_stated_as_behavior_not_as_python(self):
        """INV-002 — a Java/C#/TypeScript implementation must be able to satisfy them."""
        start = self.text.index("Bind the LOOPBACK interface explicitly")
        end = self.text.index("Identifying the server process", start)
        block = self.text[start:end]
        self.assertNotIn("ThreadingHTTPServer", block)
        self.assertNotIn("senzing_viz_server.py", block)


if __name__ == "__main__":
    unittest.main()
