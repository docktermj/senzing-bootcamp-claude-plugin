"""Tests that the visualization endpoint lists stay in sync.

Three places name the visualization server's HTTP routes:

* ``scripts/senzing_viz_server.py`` — the reference implementation's routes.
* ``skills/module-03b-truthset-visualization/phase1-visualization.md`` — the
  verification table the module probes at run time.
* ``skills/module-03b-truthset-visualization/visualization-api-reference.md`` —
  the contract a language-native server is built from (INV-090).

They drifted: consolidating the tabs removed ``/api/dashboard`` and added
``/api/records``, but the verification table kept probing the removed route and
never checked the new one. That is worse than cosmetic — the module would issue
a request that 404s and report a verification failure for an endpoint that is
gone on purpose, while the endpoint backing the Records action went unverified.

The contract is allowed to mention a removed route, because it documents the
removal so a reader does not reintroduce it. The verification table is not: it
is executed.

Run:  python3 -m unittest discover -s tests
"""
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "senzing-bootcamp")
SERVER = os.path.join(PLUGIN, "scripts", "senzing_viz_server.py")
MODULE_03B = os.path.join(PLUGIN, "skills", "module-03b-truthset-visualization")
VERIFY_TABLE = os.path.join(MODULE_03B, "phase1-visualization.md")
CONTRACT = os.path.join(MODULE_03B, "visualization-api-reference.md")

# Routes the contract documents *as removed*, so a reader does not reintroduce
# them. Allowed to appear in the contract; never in the verification table.
REMOVED = {"/api/dashboard"}


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def server_routes():
    """Routes the reference server actually serves."""
    return set(re.findall(r'"(/api/[a-z]+)"', read(SERVER)))


def table_routes():
    """Routes the module's verification table probes."""
    return set(re.findall(r"GET (/api/[a-z]+)", read(VERIFY_TABLE)))


def contract_routes():
    return set(re.findall(r"`GET (/api/[a-z]+)", read(CONTRACT)))


class TestVerificationTableMatchesServer(unittest.TestCase):
    def test_no_removed_route_is_probed(self):
        offenders = sorted(table_routes() & REMOVED)
        self.assertEqual(
            [],
            offenders,
            f"The verification table probes removed route(s) {offenders}. They "
            "404 by design, so the module would report a false failure.",
        )

    def test_table_probes_every_served_route(self):
        missing = sorted(server_routes() - table_routes())
        self.assertEqual(
            [],
            missing,
            f"Served but never verified: {missing}. A route nobody probes is a "
            "route that can break silently.",
        )

    def test_table_probes_nothing_the_server_lacks(self):
        extra = sorted(table_routes() - server_routes())
        self.assertEqual(
            [],
            extra,
            f"Verified but not served: {extra}. Either the route was removed "
            "and the table is stale, or the reference server is missing it.",
        )


class TestContractCoversTheServer(unittest.TestCase):
    def test_contract_documents_every_served_route(self):
        missing = sorted(server_routes() - contract_routes())
        self.assertEqual(
            [],
            missing,
            f"Served but undocumented in the contract: {missing}. A "
            "language-native server (INV-090) is built from that contract, so "
            "an undocumented route simply will not exist there.",
        )

    def test_removed_routes_are_documented_as_removed(self):
        """A removed route may stay in the contract only as a removal note."""
        text = read(CONTRACT)
        for route in sorted(REMOVED & contract_routes()):
            with self.subTest(route=route):
                idx = text.index(f"`GET {route}")
                window = text[idx : idx + 200]
                self.assertIn(
                    "REMOVED",
                    window,
                    f"{route} appears in the contract without being marked "
                    "REMOVED — a reader would implement it.",
                )


if __name__ == "__main__":
    unittest.main()
