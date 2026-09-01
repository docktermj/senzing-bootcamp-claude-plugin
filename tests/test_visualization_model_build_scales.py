"""The visualization model can be built from the export stream, not one call per record.

The reference server built its model by reading a records file and calling
``get_entity_by_record_id`` once per record — correct and fast at the Truth Set's 84
entities. Module 7 then points the same design at the Bootcamper's own data, which on the
reporting run meant **19,584 round trips to build one page** (2026-08-26). Rebuilt on the
export stream, the same model took ~15 seconds.

⚠️ **The correctness gain outlives the speed one.** A records-file build can only see
entities that have a record in the file it was handed; the export stream yields **every
resolved entity**, including embedded-master records a mapper emitted that appear in no
input file. So the per-record build can silently under-represent the multi-source
resolution Module 7 exists to show.

Method names and argument types verified against the live server per binding
(``get_sdk_reference(topic='parameters', …, language='python')``, server 1.35.3,
2026-09-01)::

    export_json_entity_report(flags: int = SZ_EXPORT_DEFAULT_FLAGS) -> int
    fetch_next(export_handle: int) -> str
    close_export_report(export_handle: int) -> None

⛔ These are **offline** tests against a fake engine. They assert that the export path
exists, absorbs identically, and closes its handle — never that it is fast, which needs a
live engine with a loaded datastore and stays the reporter's observation.

Stdlib only; the server is loaded by path (INV-108).
"""

import ast
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SERVER = REPO / "plugins" / "senzing-bootcamp" / "scripts" / "senzing_viz_server.py"


def load_server():
    spec = importlib.util.spec_from_file_location("_viz_server", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_viz_server"] = module
    spec.loader.exec_module(module)
    return module


def entity_doc(eid, records, related=()):
    return {
        "RESOLVED_ENTITY": {
            "ENTITY_ID": eid,
            "ENTITY_NAME": "Entity %d" % eid,
            "RECORDS": [{"DATA_SOURCE": ds, "RECORD_ID": rid, "MATCH_KEY": mk}
                        for ds, rid, mk in records],
        },
        "RELATED_ENTITIES": [{"ENTITY_ID": t, "MATCH_KEY": "+NAME",
                              "MATCH_LEVEL_CODE": "POSSIBLY_SAME"} for t in related],
    }


DOCS = [
    entity_doc(1, [("CUSTOMERS", "A1", ""), ("REFERENCE", "R1", "+NAME+ADDR")], related=[2]),
    entity_doc(2, [("WATCHLIST", "W1", "")]),
    # An entity with no record in any input file — an embedded master. The records-file
    # build cannot reach it; the export stream yields it.
    entity_doc(3, [("CUSTOMERS", "EMBEDDED-1", "")]),
]


class FakeRecordEngine:
    """Serves get_entity_by_record_id, like a records-file build sees it."""

    def __init__(self, docs):
        self.by_key = {}
        for doc in docs:
            for rec in doc["RESOLVED_ENTITY"]["RECORDS"]:
                self.by_key[(rec["DATA_SOURCE"], rec["RECORD_ID"])] = doc
        self.calls = 0

    def get_entity_by_record_id(self, ds, rid, flags):
        self.calls += 1
        return json.dumps(self.by_key[(ds, rid)])


class FakeExportEngine:
    """Serves the export triple, and records that the handle was closed."""

    def __init__(self, docs):
        self.docs = list(docs)
        self.closed = []
        self.opened = 0
        self._streams = {}

    def export_json_entity_report(self, flags):
        self.opened += 1
        handle = 900 + self.opened
        self._streams[handle] = iter([json.dumps(d) for d in self.docs])
        return handle

    def fetch_next(self, handle):
        return next(self._streams[handle], "")

    def close_export_report(self, handle):
        self.closed.append(handle)


class TheExportPathExists(unittest.TestCase):
    def setUp(self):
        self.viz = load_server()

    def test_the_model_has_an_export_build(self):
        self.assertTrue(
            hasattr(self.viz.Model, "build_from_export"),
            "Model must offer an export-stream build; the per-record build is the Truth "
            "Set path and does not scale to a Bootcamper's datastore.",
        )

    def test_the_records_file_build_still_exists(self):
        """The Truth Set path is unchanged — this adds a strategy, it does not replace one."""
        self.assertTrue(hasattr(self.viz.Model, "build"))


class BothPathsAbsorbIdentically(unittest.TestCase):
    """The claim that made the change small: an export row is shaped like a get_entity."""

    def setUp(self):
        self.viz = load_server()

    def test_the_two_builds_agree_on_entities_and_edges(self):
        keys = [(r["DATA_SOURCE"], r["RECORD_ID"])
                for d in DOCS for r in d["RESOLVED_ENTITY"]["RECORDS"]]
        per_record = self.viz.Model().build(FakeRecordEngine(DOCS), 0, keys)
        exported = self.viz.Model().build_from_export(FakeExportEngine(DOCS), 0)

        self.assertEqual(
            sorted(per_record.entities), sorted(exported.entities),
            "both build paths must produce the same entity set from the same documents — "
            "that equivalence is why the absorb step is shared rather than duplicated",
        )
        self.assertEqual(
            sorted(per_record.edges), sorted(exported.edges),
            "both build paths must produce the same relationship edges",
        )

    def test_records_total_counts_records_not_export_rows(self):
        """An export row is one ENTITY; `records_total` is a record count."""
        exported = self.viz.Model().build_from_export(FakeExportEngine(DOCS), 0)
        expected = sum(len(d["RESOLVED_ENTITY"]["RECORDS"]) for d in DOCS)
        self.assertEqual(
            expected, exported.records_total,
            "records_total must count RECORDS. Incrementing once per export row would "
            "report 3 where the model holds 4 records, and the stats tab reads this.",
        )


class TheExportHandleIsAlwaysClosed(unittest.TestCase):
    """⛔ An unclosed export handle holds engine resources for the life of the process."""

    def setUp(self):
        self.viz = load_server()

    def test_the_handle_is_closed_on_a_clean_run(self):
        engine = FakeExportEngine(DOCS)
        self.viz.Model().build_from_export(engine, 0)
        self.assertEqual(1, len(engine.closed), "the export handle must be closed")

    def test_the_handle_is_closed_when_the_stream_raises(self):
        engine = FakeExportEngine(DOCS)

        def exploding(handle):
            raise RuntimeError("engine went away mid-stream")

        engine.fetch_next = exploding
        with self.assertRaises(RuntimeError):
            self.viz.Model().build_from_export(engine, 0)
        self.assertEqual(
            1, len(engine.closed),
            "the handle must be closed even when the stream raises — that is what the "
            "try/finally is for, and a leaked handle outlives the failed build",
        )


class TheExportPathIsReachableFromTheShippedServer(unittest.TestCase):
    """The MEDIUM finding of `production-readiness-audit-2026-09-01d`.

    `build_from_export` was added and **nothing in the shipped script called it**:
    `build_model` built per-record unconditionally and `--records` was `required=True`, so
    no invocation could reach it. Its only callers were these tests, which is dead code in
    a shipped artifact — and Module 7 tells the guide to model their own server on this
    file while mandating the export path, so the reference contradicted the instruction
    pointing at it.

    ⚠️ Asserted against the **call graph**, not the presence of the method. The ledger
    ticked a criterion reading *"can build … and does so when pointed at a Bootcamper
    datastore"* on the evidence that the method existed — which established the first half
    only. A test for `hasattr` would have passed on the defect.
    """

    def setUp(self):
        self.source = SERVER.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def _build_model_fn(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == "build_model":
                return node
        self.fail("build_model() not found in the shipped server")

    def _calls_within(self, fn):
        out = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                out.add(node.func.attr)
        return out

    def test_build_model_can_reach_the_export_path(self):
        calls = self._calls_within(self._build_model_fn())
        self.assertIn(
            "build_from_export", calls,
            "build_model() must be able to reach the export build. Adding the method "
            "without a call site leaves dead code in a shipped script that Module 7 tells "
            "the guide to model on, while instructing the very path it cannot take.",
        )

    def test_build_model_still_reaches_the_per_record_path(self):
        calls = self._calls_within(self._build_model_fn())
        self.assertIn(
            "build", calls,
            "the per-record path must remain reachable — it is correct for the Truth Set, "
            "which is what this reference serves.",
        )

    def test_the_records_argument_is_optional(self):
        """The route that selects the export path: omitting --records."""
        self.assertNotRegex(
            re.sub(r"\s+", " ", self.source),
            r'add_argument\("--records"[^)]*required=True',
            "--records must be optional; while it was required no invocation could select "
            "the export build.",
        )

    def test_the_export_call_does_not_pin_a_default_composite(self):
        """⛔ Module 7 forbids it, so the reference it points at must not do it either.

        `SZ_EXPORT_DEFAULT_FLAGS` is `SZ_EXPORT_INCLUDE_ALL_ENTITIES | SZ_ENTITY_DEFAULT_FLAGS`
        (server 1.35.3, 2026-09-01), and the server's own caution says a DEFAULT composite's
        membership may change between versions with no error raised.
        """
        fn = self._build_model_fn()
        names = {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
        self.assertNotIn(
            "SZ_EXPORT_DEFAULT_FLAGS", names,
            "the export call must request the flags the model consumes, not a DEFAULT "
            "composite — the instruction in Module 7 says so, and a reference that "
            "contradicts it recreates the defect this fix exists for.",
        )
        for required in ("SZ_EXPORT_INCLUDE_ALL_ENTITIES",
                         "SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO",
                         "SZ_ENTITY_INCLUDE_ALL_RELATIONS"):
            with self.subTest(flag=required):
                self.assertIn(
                    required, names,
                    "the export flags must name what `_absorb` actually reads; %s "
                    "populates a field the model consumes" % required,
                )


class TheHeaderDescribesBothBuildPaths(unittest.TestCase):
    """The MEDIUM finding of `production-readiness-audit-2026-09-01e`.

    After the export path was wired, the module header still said the data source was
    ``get_entity_by_record_id`` … "one call per loaded record" — the path Module 7
    **forbids** for a Bootcamper's datastore, presented as the file's only behavior. The
    header is the first thing a reader sees, and Module 7 tells the guide to *"build it
    modeled on the shipped Truth Set visualization server"*, so a guide modeling on this
    file was told the wrong thing by its opening paragraph.

    ⚠️ That was the same instruction/reference disagreement the previous audit had just
    fixed in the call graph, relocated into the prose: one rule, several sites, fixed at
    one of them.
    """

    def setUp(self):
        source = SERVER.read_text(encoding="utf-8")
        # The module docstring only — a match anywhere else in a 2,000-line file would
        # not tell a reader at the top of it anything.
        self.header = ast.get_docstring(ast.parse(source)) or ""
        # ⚠️ And the DATA SOURCE section only, for the claims about it. Checked against
        # the whole docstring, `test_the_header_names_both_paths` passed with the entire
        # two-path block deleted — because the Usage block below it also says "export
        # stream". An assertion a neighboring section can satisfy is not an assertion
        # about the section it names.
        self.data_source = self.header.split("Usage:")[0]

    def test_the_header_names_both_paths(self):
        for path in ("get_entity_by_record_id", "export stream"):
            with self.subTest(path=path):
                self.assertIn(
                    path, self.data_source,
                    "the module header must name both build paths. Describing only the "
                    "per-record one tells a guide modeling on this file to implement "
                    "exactly what Module 7's stop-sign forbids.",
                )

    def test_the_header_says_what_selects_each(self):
        self.assertRegex(
            re.sub(r"\s+", " ", self.data_source),
            r"(?i)--records given.*--records omitted",
            "naming both paths is not enough — the header must say which condition "
            "selects each, or a reader cannot tell which one they are getting.",
        )

    def test_the_header_no_longer_claims_one_call_per_record_is_the_data_source(self):
        """The retired sentence, pinned so it cannot come back as a 'simplification'."""
        self.assertNotRegex(
            re.sub(r"\s+", " ", self.data_source),
            r"so nodes and edges come from one call per loaded record",
            "the header must not present the per-record build as the file's only data "
            "source.",
        )

    def test_the_no_direct_sql_guarantee_survives_and_covers_both(self):
        self.assertRegex(
            re.sub(r"\s+", " ", self.data_source),
            r"(?i)no direct SQL is ever run against the database on either",
            "the no-direct-SQL guarantee must survive the rewrite and must be stated as "
            "covering both paths — it is true of both, and dropping it to make room for "
            "the second path would trade a real guarantee for a description.",
        )

    def test_the_usage_block_shows_the_export_invocation(self):
        """A form shown nowhere is a form a reader does not know exists."""
        usage = self.header[self.header.index("Usage:"):]
        without_records = [
            line for line in usage.splitlines()
            if "senzing_viz_server.py" in line and "--records" not in line
        ]
        self.assertTrue(
            without_records,
            "the Usage block must show an invocation WITHOUT --records. Every example "
            "passing it means the export form is undiscoverable to a reader working "
            "top-to-bottom, which is how the path stayed unreachable in the first place.",
        )


class TheModuleSaysWhichStrategyApplies(unittest.TestCase):
    """Module 7 delegates by resemblance, so the scale assumption travels unless it is named."""

    def setUp(self):
        self.text = (REPO / "plugins" / "senzing-bootcamp" / "skills" /
                     "module-07-query-visualize-discover" /
                     "phase1-query-visualize.md").read_text(encoding="utf-8")

    def test_it_instructs_the_export_stream_build(self):
        self.assertRegex(
            self.text, r"(?i)Build the model from the EXPORT STREAM",
            "Module 7 must say which build strategy applies to the Bootcamper's own data — "
            "'model it on the Truth Set server' otherwise carries the Truth Set's scale "
            "assumption into a 19,584-record datastore.",
        )

    def test_it_names_the_correctness_reason_not_only_speed(self):
        self.assertRegex(
            self.text, r"(?i)every \*\*resolved entity\*\*|appear in no input file",
            "the instruction must give the correctness reason too. Stated as a speed tip it "
            "reads as optional; the records-file build also MISSES entities.",
        )

    def test_it_sends_the_reader_to_the_server_for_the_signature(self):
        self.assertRegex(
            self.text, r"filter='export_json_entity_report'",
            "the export signature differs by binding in both name and argument type, so the "
            "instruction must name the route rather than showing one binding's form "
            "(INV-002/INV-080).",
        )

    def test_it_warns_against_pinning_a_default_composite(self):
        self.assertRegex(
            self.text, r"(?i)\*_DEFAULT_FLAGS`? composite into the export call|"
            r"Do not pin a `?\*_DEFAULT_FLAGS",
            "the guidance must not send a Bootcamper to pin a DEFAULT composite — the "
            "server's own caution says their membership may change with no error raised.",
        )


if __name__ == "__main__":
    unittest.main()
