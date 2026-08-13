"""Every prescribed `search_docs` query is either verified against the server or paired
with a re-query rule.

`search_docs` is BM25, so phrasing decides what comes back — a fact
`module-00-entity-resolution-concepts/concepts.md` documents at length, together with a ⛔
re-query rule, both added because a *composed* query had already failed in a real run.

Module 1 Step 14 was written with the same instinct (name the query so the guide does not
improvise) but as a **template with a substitution slot** that was never executed for the
categories it would be substituted with, and without the safeguard. Measured on server 1.32.9,
docs index 2026-08-11, checked 2026-08-12:

- `value proposition Supply Chain` — the prescribed template with a category from the plugin's
  own recognized set — returns `senzing/libpostal`'s geodata *store-chains* scripts and a
  `sz_spark` changelog's "CI / supply chain" heading. BM25 matched "chains" and the *software*
  sense of "supply chain"; "value proposition" contributed nothing.
- `entity resolution business value` returns the real material: the *Entity Resolution Buyer's
  Guide* ("Five Primary Business Use Cases") and *Agentic Entity Resolution* ("Why Agentic
  Entity Resolution Matters", whose Business Impact list is broken out by use case).
- `entity resolution business value supply chain` — the working query **plus** the category —
  puts the libpostal script back at the top, outranking the real material (57.9 vs 57.5).

That last measurement is why the shipped fix forbids appending the category rather than
offering it as an optional refinement: the category token is the defect, not a refinement of a
working query. The category selects which part of the results to use; it does not retrieve them.

Why the failure shape matters more than the wasted call, in the plugin's own words: "a query
that misses looks exactly like documentation that does not cover the topic", which "makes a
training-data fallback feel justified on the grounds that MCP 'had no answer'" — and Step 14
sits immediately before the confirmation gate on the path to *every* Module 1 completion.

The allowlist below is not a convenience. Each entry was executed against the live server at
the date recorded, and the observed top hit is written down so a later reader can re-check the
claim rather than trust it. A query added without either verification or a re-query rule fails.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "senzing-bootcamp" / "skills"
STEP14 = SKILLS / "module-01-business-problem" / "phase2-document-confirm.md"

#: When every phrasing below was last executed against the live server.
VERIFIED_ON = "server 1.32.9, docs index 2026-08-11 20:52 UTC, checked 2026-08-12"

#: query -> the top hit observed, so the verification is re-checkable and not just asserted.
#: "Verified" means EXECUTED and its result written down — not "ideal". Where a phrasing lands
#: on adjacent rather than on-target material that is said so explicitly, because an allowlist
#: that quietly upgrades "I ran it" into "it is good" is the same laundering this guard exists
#: to stop.
VERIFIED_QUERIES = {
    "entity resolution business value":
        "ON TARGET: Entity Resolution Buyer's Guide -> 'Five Primary Business Use Cases'; "
        "Agentic Entity Resolution -> 'Why Agentic Entity Resolution Matters'",
    "what features to map":
        "ON TARGET: Senzing Entity Specification -> 'What features to map' (exact section)",
    "SZ_WHY_ENTITIES_DEFAULT_FLAGS default recommended flags":
        "ADJACENT: v4 Engine Flags -> 'get_entity* Flags' / SZ_ENTITY_DEFAULT_FLAGS. Right "
        "document family and the why_* flag pages are siblings there, so a guide reaches the "
        "material, but the top hit is not the why_entities composite itself",
    "Senzing engine configuration PostgreSQL connection":
        "ON TARGET: Senzing Engine Configuration (exact page)",
    "PostgreSQL schema DDL initialization":
        "ON TARGET: Database Setup -> 'PostgreSQL Setup: Create the database, schema, and "
        "permissions'",
    "CORD datasets: names, contents, and availability for entity resolution scenarios":
        "ON TARGET: Collections Of Relatable Data (CORDs) -> 'What Is a CORD?'",
    "temporary evaluation license for a dataset larger than the default limit":
        "ON TARGET: End User License Agreement (EULA) -> 'Senzing Non-Production License' "
        "(relevance 171, the highest in this set)",
    # ⚠️ Not a query a step tells the guide to RUN — it is the evidence slot of an
    # MCP-NEGATIVE marker in module-02 Step 1, recording a query that was run and came back
    # without the fact. The guard cannot tell the two apart (both are `search_docs(query='…')`
    # literals in shipped markdown), and that is the right default: an unexecuted phrasing is
    # indistinguishable from an executed one, so both must be accountable. Executed against
    # server 1.32.9, docs indexed 2026-08-11 20:52 UTC, on 2026-08-13.
    "szBuildVersion.json build version file location":
        "OFF TARGET BY DESIGN — this is the negative's evidence: no indexed document gives the "
        "file's path on any platform. All four hits are SDK version-call examples, top hit "
        "brianmacy/sz-rust-sdk -> code-snippets/information/get_version.rs (relevance 39.5). "
        "The corpus serves SzProduct.get_version(), not a file location, which is why Step 1 "
        "routes the reader to the SDK call and marks the file paths as environment observations",
    # "entity resolution quality evaluation" was listed here as OFF TARGET on 2026-08-12 and is
    # gone: Module 7 Step 3b no longer prescribes it. It returned the Buyer's Guide's
    # vendor-selection steps rather than precision/recall material, and
    # step3b-quality-lookup-misroutes-and-omits-the-evidence-requirement replaced it with
    # reporting_guide(topic='evaluation'), the tool that owns the material. Left as a comment
    # rather than deleted, so the phrasing is not helpfully reintroduced.
}

#: Vocabulary that shows a step handles a miss instead of assuming a hit.
REQUERY_RULE = re.compile(
    r"(?i)re-?quer(?:y|ies|ying)|nothing relevant|off-topic|empty or off-topic"
)

QUERY_LITERAL = re.compile(r"search_docs\(query='([^']*)'")
HEADING = re.compile(r"(?m)^#{2,4} ")


def shipped_markdown():
    return sorted(SKILLS.rglob("*.md"))


def sections(text):
    """(start, end) spans between Markdown headings, so 'the same step' is well-defined."""
    bounds = [m.start() for m in HEADING.finditer(text)] + [len(text)]
    if not bounds or bounds[0] != 0:
        bounds = [0] + bounds
    return [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]


def prescribed_queries():
    """(path, query, enclosing section text) for every prescribed query literal."""
    found = []
    for path in shipped_markdown():
        text = path.read_text(encoding="utf-8")
        spans = sections(text)
        for match in QUERY_LITERAL.finditer(text):
            section = next(
                (text[a:b] for a, b in spans if a <= match.start() < b), text
            )
            # Whitespace-collapsed: a literal wrapped across source lines is still one
            # query. A line-based scan misses these entirely — three of the eight
            # prescribed queries in this corpus are wrapped, and all three were invisible
            # to the first version of this guard.
            query = re.sub(r"\s+", " ", match.group(1)).strip()
            found.append((path.relative_to(REPO_ROOT), query, section))
    return found


class EveryPrescribedQueryIsAccountedFor(unittest.TestCase):
    def test_the_scan_finds_the_queries(self):
        found = prescribed_queries()
        self.assertGreaterEqual(len(found), 5, "the query scan came up empty or too small")

    def test_each_query_is_verified_or_carries_a_requery_rule(self):
        unaccounted = []
        for path, query, section in prescribed_queries():
            if query in VERIFIED_QUERIES:
                continue
            if REQUERY_RULE.search(section):
                continue
            unaccounted.append(f"{path}: search_docs(query='{query}')")
        self.assertEqual(
            [],
            unaccounted,
            "A shipped step prescribes a search_docs query that was never verified against "
            "the server and has no re-query rule in its section. search_docs is BM25, so an "
            "unexecuted phrasing can return anything — and a miss looks exactly like "
            "documentation that does not cover the topic. Verify it and add it to "
            "VERIFIED_QUERIES with its observed top hit, or pair it with a re-query "
            "instruction:\n  " + "\n  ".join(unaccounted),
        )

    def test_the_allowlist_has_no_dead_entries(self):
        """An allowlist that outlives its queries starts exempting things by accident."""
        live = {query for _p, query, _s in prescribed_queries()}
        dead = sorted(set(VERIFIED_QUERIES) - live)
        self.assertEqual(
            [], dead,
            "VERIFIED_QUERIES lists phrasings no shipped file prescribes any more — remove "
            "them so the allowlist keeps meaning what it says: %s" % dead,
        )

    def test_every_allowlist_entry_records_what_it_returned(self):
        for query, top_hit in VERIFIED_QUERIES.items():
            with self.subTest(query=query):
                self.assertTrue(
                    top_hit and len(top_hit) > 15,
                    "a verification with no recorded result cannot be re-checked",
                )


class StepFourteenHandlesAMiss(unittest.TestCase):
    def flat(self):
        text = STEP14.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^\s*>\s?", "", text)
        return re.sub(r"\s+", " ", text)

    def test_the_broken_template_is_gone(self):
        self.assertNotIn("value proposition <use_case_category>", self.flat())

    def test_it_prescribes_the_verified_query(self):
        self.assertIn("search_docs(query='entity resolution business value')", self.flat())

    def test_it_carries_the_verification_stamp(self):
        flat = self.flat()
        self.assertIn("1.32.9", flat)
        self.assertIn("2026-08-12", flat)

    def test_it_forbids_appending_the_category(self):
        """The measured cause: the category token, not the abstract phrasing."""
        flat = self.flat()
        self.assertRegex(flat, r"(?i)Do not append the use-case category to the query")
        self.assertRegex(flat, r"(?i)libpostal")

    def test_it_carries_the_requery_rule_and_defers_for_the_reasoning(self):
        flat = self.flat()
        self.assertRegex(flat, REQUERY_RULE)
        self.assertRegex(flat, r"(?i)concepts\.md")
        self.assertRegex(flat, r"(?i)[Dd]o not restate that reasoning here")

    def test_it_gives_an_honest_fallback(self):
        flat = self.flat()
        self.assertRegex(flat, r"(?i)say less — do not invent value")
        self.assertIn("INV-080", flat)


if __name__ == "__main__":
    unittest.main()
