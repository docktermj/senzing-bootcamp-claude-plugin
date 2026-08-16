"""The reference server's payloads must carry exactly the keys the contract documents.

`visualization-api-reference.md` is "the **authoritative** API/response contract to implement",
and every non-Python bootcamper builds their server from it. The shipped Python reference
returned a different shape at two endpoints, **in both directions** — fields the contract
required were absent, and fields it returned were undocumented:

* `/api/merges` entities carried `record_count` and `data_sources` (undocumented) and no
  `match_key` (documented); its records carried `match_key` (undocumented) and none of the
  documented `name`, `address`, `phone`, `identifiers`.
* `/api/records` was documented as matching `/api/merges` records and did not.

⛔ **The divergence is invisible to a reading audit, because each file is internally
consistent.** That is what makes a test the only real fix — and it is also the silent-blank
failure INV-115 exists to prevent: reading `entity.name` per the record-level contract returns
`None`, which renders as empty text, so the app looks like "Senzing found nothing" rather than
broken.

**Which side was wrong was decided by measurement, not preference.** The model is built with
`SZ_ENTITY_DEFAULT_FLAGS`, and that composite **excludes**
`SZ_ENTITY_INCLUDE_RECORD_FEATURES` and `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA` (read off the SDK's
own flag constants, Senzing 4.3.4, 2026-08-14), so per-record names and addresses are simply not
in the response at those flags. The server was right; the contract was describing data it never
had. See the spec's Deviations section.

The payload constructors are exercised directly on a hand-built `Model`, with no engine: they are
pure functions of the model, and an engine is not available in this environment (nor is the loaded
Truth Set). What is asserted is exactly what a bootcamper's client would see.

Source spec: `specs/visualization-contract-and-reference-server-disagree-on-record-fields.md`.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "senzing-bootcamp"
SERVER = PLUGIN / "scripts" / "senzing_viz_server.py"
CONTRACT = (PLUGIN / "skills" / "module-03b-truthset-visualization"
            / "visualization-api-reference.md")

#: The documented record shape. One list, used for BOTH endpoints, because the contract says
#: they are the same objects — so a test that hardcoded them separately could pass while they
#: diverged.
RECORD_KEYS = {"data_source", "record_id", "match_key"}
MERGE_ENTITY_KEYS = {"entity_id", "entity_name", "record_count", "data_sources", "records"}
RECORDS_TOP_KEYS = {"entity_id", "entity_name", "records"}


def load_server():
    spec = importlib.util.spec_from_file_location("viz_contract_test", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SERVER.parent))
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_model(module):
    """A two-entity model in the shape `Model.build` produces: one merged, one singleton."""
    model = module.Model()
    model.records_total = 3
    model.entities = {
        1: {
            "entity_id": 1, "entity_name": "Robert Smith", "record_count": 2,
            "data_sources": ["CUSTOMERS", "REFERENCE"],
            "records": [
                {"data_source": "CUSTOMERS", "record_id": "1001", "match_key": ""},
                {"data_source": "REFERENCE", "record_id": "2001",
                 "match_key": "+NAME+ADDRESS"},
            ],
        },
        2: {
            "entity_id": 2, "entity_name": "Jane Doe", "record_count": 1,
            "data_sources": ["CUSTOMERS"],
            "records": [
                {"data_source": "CUSTOMERS", "record_id": "1002", "match_key": ""},
            ],
        },
    }
    return model


def contract_text():
    return re.sub(r"\s+", " ", CONTRACT.read_text(encoding="utf-8"))


def build_blocks():
    """(entity-dict source, record-dict source) as `Model.build` writes them.

    ⛔ The payload tests below run against a hand-built model, so `Model.build` itself is
    never executed by them — which means a key ADDED there is invisible to an
    exact-key-set assertion on the payload. A mutation adding `internal_id` to the record
    dict escaped exactly that way. These two blocks are therefore checked as source text:
    it is the only route to `build`'s literal key set without a live engine.
    """
    source = SERVER.read_text(encoding="utf-8")
    start = source.index("self.entities[eid] = {")
    record_start = source.index('"records": [', start)
    record_end = source.index("for r in records", record_start)
    marker = '"records": ['
    entity_block = source[start:record_start]
    # Slice past the `"records": [` marker itself, or `records` counts as a record key.
    return entity_block, source[record_start + len(marker):record_end]


def literal_keys(block):
    """The `"key":` literals in a dict-construction block, ignoring lookups like
    `r.get("MATCH_KEY", "")` — a key being *written* is followed by a colon."""
    return set(re.findall(r'"([a-z_]+)"\s*:', block))


class TheFixtureMatchesTheServersOwnModelShape(unittest.TestCase):
    """If the fixture drifts from what `Model.build` writes, every assertion below is about
    the fixture rather than the server."""

    def test_build_writes_exactly_the_documented_record_keys(self):
        _entity, record = build_blocks()
        self.assertEqual(
            RECORD_KEYS, literal_keys(record),
            "Model.build's record dict does not carry exactly the documented keys. An "
            "EXTRA key is the worse direction: a non-Python implementer omits it, and the "
            "payload tests here run on a fixture so they cannot see it.")

    def test_build_writes_exactly_the_documented_entity_keys(self):
        entity, _record = build_blocks()
        # `records` is opened after this block, so add it back.
        self.assertEqual(
            MERGE_ENTITY_KEYS, literal_keys(entity) | {"records"},
            "Model.build's entity dict does not carry exactly the documented keys")

    def test_the_fixture_uses_the_same_keys(self):
        module = load_server()
        model = build_model(module)
        entity = model.entities[1]
        self.assertEqual(MERGE_ENTITY_KEYS, set(entity),
                         "the fixture entity no longer matches the documented shape")
        self.assertEqual(RECORD_KEYS, set(entity["records"][0]),
                         "the fixture record no longer matches the documented shape")


class MergesMatchesTheContract(unittest.TestCase):
    def setUp(self):
        self.module = load_server()
        self.payload = build_model(self.module).merges()

    def test_the_top_level_key(self):
        self.assertEqual({"entities"}, set(self.payload),
                         "/api/merges top-level shape changed")

    def test_only_multi_record_entities_are_returned(self):
        ids = [e["entity_id"] for e in self.payload["entities"]]
        self.assertEqual([1], ids,
                         "the contract says only entities with 2+ records are returned")

    def test_entity_keys_are_exactly_documented(self):
        for entity in self.payload["entities"]:
            with self.subTest(entity=entity["entity_id"]):
                self.assertEqual(
                    MERGE_ENTITY_KEYS, set(entity),
                    "entity keys diverge from the contract. Undocumented keys are the "
                    "worse half: a non-Python implementer omits them.")

    def test_record_keys_are_exactly_documented(self):
        for entity in self.payload["entities"]:
            for record in entity["records"]:
                with self.subTest(record=record.get("record_id")):
                    self.assertEqual(
                        RECORD_KEYS, set(record),
                        "record keys diverge from the contract; reading an absent key "
                        "yields None and renders as blank text (INV-115)")

    def test_match_key_is_on_the_record_not_the_entity(self):
        entity = self.payload["entities"][0]
        self.assertNotIn("match_key", entity,
                         "match_key has two homes again; the contract gives it one")
        self.assertIn("match_key", entity["records"][0])

    def test_an_empty_match_key_is_representable(self):
        """The seed record joined nothing, so "" is normal and must not be dropped."""
        keys = [r["match_key"] for r in self.payload["entities"][0]["records"]]
        self.assertIn("", keys, "the fixture no longer covers the empty-match_key case")


class RecordsMatchesMerges(unittest.TestCase):
    def setUp(self):
        self.module = load_server()
        self.model = build_model(self.module)

    def test_the_top_level_keys(self):
        self.assertEqual(RECORDS_TOP_KEYS, set(self.model.records(1)))

    def test_its_records_are_the_same_objects_as_merges(self):
        """The contract says "the same fields" — they read one model, so assert equality."""
        from_merges = self.model.merges()["entities"][0]["records"]
        from_records = self.model.records(1)["records"]
        self.assertEqual(from_merges, from_records,
                         "/api/records and /api/merges disagree about one entity's records")

    def test_it_covers_single_record_entities(self):
        payload = self.model.records(2)
        self.assertEqual(1, len(payload["records"]),
                         "/api/records must cover single-record entities, unlike /api/merges")
        self.assertEqual(RECORD_KEYS, set(payload["records"][0]))

    def test_a_bad_entity_id_returns_an_error_object_not_a_raise(self):
        for bad in ("not-an-int", 9999):
            with self.subTest(entity_id=bad):
                payload = self.model.records(bad)
                self.assertIn("error", payload,
                              "one entity's failure must not break the tab")
                self.assertIn("entity_id", payload)


class TheContractDocumentsWhatIsReturned(unittest.TestCase):
    def setUp(self):
        self.flat = contract_text()

    def test_the_undocumented_entity_fields_are_now_documented(self):
        self.assertRegex(
            self.flat,
            r"Each entity: `entity_id`, `entity_name`, `record_count`, `data_sources`, "
            r"`records`",
            "record_count and data_sources are returned but still undocumented")

    def test_the_record_fields_no_longer_claim_name_address_phone(self):
        self.assertRegex(
            self.flat,
            r"Each record:\s*`data_source`, `record_id`, `match_key`",
            "the record-level field list is not the shape the server returns")
        self.assertNotRegex(
            self.flat,
            r"Each record carries the same fields `/api/merges` uses: `data_source`, "
            r"`record_id`, `name`",
            "/api/records still claims per-record name/address/phone/identifiers")

    def test_match_key_has_one_documented_home_with_its_empty_value_explained(self):
        self.assertRegex(
            self.flat, r"(?i)`match_key` lives on the RECORD, not on the entity",
            "match_key's home is not stated")
        self.assertRegex(
            self.flat, r"(?i)An empty string is normal, not missing data",
            "an empty match_key is undocumented, so it reads as a defect")

    def test_the_flag_reason_is_recorded_with_its_measurement(self):
        """Why the contract moved rather than the server: the data is not in the response."""
        self.assertRegex(
            self.flat,
            r"(?i)excludes\*?\*?\s*`SZ_ENTITY_INCLUDE_RECORD_FEATURES` and\s*"
            r"`SZ_ENTITY_INCLUDE_RECORD_JSON_DATA`",
            "the contract asserts a field list without saying why it is that list, so a "
            "future reader re-adds the missing fields")
        self.assertRegex(
            self.flat, r"(?i)Senzing 4\.3\.4, 2026-08-14",
            "the flag measurement carries no version or date")

    def test_the_enrichment_route_is_documented_as_optional(self):
        self.assertRegex(
            self.flat, r"(?i)To enrich the Records panel \(optional",
            "removing the fields without documenting how to get them loses the capability")
        self.assertRegex(
            self.flat, r"(?i)multiply the keepsake's size by the record count",
            "the scale cost of the enrichment is not stated, and Module 7 points this app "
            "at the Bootcamper's full dataset")

    def test_the_two_endpoints_are_required_to_agree(self):
        self.assertRegex(
            self.flat, r"(?i)MUST return \*\*the same record objects\*\*",
            "the contract states the field names match but not that the objects do")


if __name__ == "__main__":
    unittest.main()
