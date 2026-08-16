# Visualization contract and reference server disagree on record fields

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`visualization-api-reference.md` is described as "the **authoritative** API/response
contract to implement" for the Truth Set visualization server, and every non-Python
bootcamper builds their server from it. The shipped Python reference server does not
return the shape it documents. Two endpoints disagree, in both directions — fields
the contract requires are missing, and fields the server returns are undocumented.

A bootcamper on Java, C#, Rust or TypeScript implements one shape; a bootcamper on
Python runs a server with another. The same divergence reaches Query, Visualize and
Discover, which re-points this server at the bootcamper's own data.

## Root cause

Measured live on 2026-08-13 against the shipped
`plugins/senzing-bootcamp/scripts/senzing_viz_server.py`, serving the 159-record
Senzing Truth Set (85 entities, 54 merged, 17 cross-source, 67 relationships) on
Senzing SDK 4.3.4.

**`/api/merges`** — contract at
`plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md:161-171`:

| Level | Contract says | Server returns |
|---|---|---|
| entity | `entity_id`, `entity_name`, `match_key`, `records` | `entity_id`, `entity_name`, `record_count`, `data_sources`, `records` |
| record | `data_source`, `record_id`, `name`, `address`, `phone`, `identifiers` | `data_source`, `record_id`, `match_key` |

So at entity level `match_key` is **absent** (reads as `None`) while `record_count`
and `data_sources` are **undocumented**; at record level four of the six documented
fields are absent and `match_key` appears instead.

**`/api/records`** — contract at `:446-447`: "Each record carries the same fields
`/api/merges` uses: `data_source`, `record_id`, `name`, `address`, `phone`,
`identifiers`." Server returns `{"data_source": "CUSTOMERS", "record_id": "1063",
"match_key": ""}` — three fields, one undocumented.

This is the failure mode the plugin itself names at
`../bootcamp-onboarding/ground-rules.md:155-161`: "a wrong field name yields `None`,
which renders as blank text. The output then looks like 'Senzing found nothing'
instead of a defect, so nobody reports it." It caught me on the first probe —
reading `entity.name` per the record-level contract returned `None`, and the entity
name was actually under `entity_name`.

Everything else in the contract checked out, which is what makes the two exceptions
worth fixing rather than rewriting: all ten endpoints respond, `/api/dashboard` is
correctly **absent** (HTTP 404) as the contract requires, `/api/stats` carries the
documented counts, and `/api/overlap`, `/api/matchkeys`, `/api/features`,
`/api/graph`, `/api/why`, `/api/how` and `/api/search` all return their documented
top-level keys.

n/a — no Senzing fact is involved; this is the plugin's own API contract against its
own reference implementation.

## Proposed change

Decide which side is right, then make the other match — and add a test so they
cannot drift again.

1. **Preferred: bring the server up to the contract.** `name`, `address`, `phone`
   and `identifiers` are what make the Records action useful — a panel showing only
   a data-source code and a record id tells the bootcamper nothing they did not
   already see in the graph. The reference server already holds the record payloads
   it built the entity model from, so populating them is local work.
2. Document `record_count` and `data_sources` on `/api/merges` entities — they are
   returned, they are useful, and an undocumented field is one a non-Python
   implementer will omit.
3. Decide where `match_key` belongs. The contract puts it on the entity; the server
   puts it on each record (and returns `""` for some). Per-record is arguably more
   informative — it is the key that pulled *that* record in — but pick one, state
   it, and say what an empty value means.
4. **Add a contract test.** Start the reference server against a small fixture and
   assert every documented endpoint returns exactly the documented top-level and
   per-item keys. Repo-level `tests/`, stdlib only, no `plugins/` import (INV-108).
   This is the guard that would have caught it: the divergence is invisible to a
   reading audit because each file is internally consistent.

## Acceptance criteria

- [ ] `/api/merges` records carry `name`, `address`, `phone` and `identifiers`, or
      the contract no longer claims they do.
- [ ] `/api/records` records match `/api/merges` records exactly, as `:446-447`
      states.
- [ ] `record_count` and `data_sources` are documented on `/api/merges` entities.
- [ ] `match_key` has one documented home, with its empty value explained.
- [ ] A repo-level test starts the reference server and fails on any key present in
      the response but absent from the contract, or vice versa; negative-controlled
      by removing a documented field and confirming failure.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The contract binds every language's server, so the test guards the reference
      that all of them are modeled on.

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `/api/merges` and
  `/api/records` payload construction.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` —
  the two response shapes.
- `tests/test_visualization_api_contract.py` — new guard.

## Source

- Feedback: dry run phase 3, 2026-08-13 — ran the shipped reference server against
  the loaded Truth Set and probed all ten documented endpoints
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — nothing crashes and the visualization renders, but the
  contract every non-Python bootcamper builds against is wrong, and the failure mode
  is the silent-blank one INV-115 exists to prevent.
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none

## Deviations from this spec, and why (2026-08-14)

⚠️ **The fix went the OTHER way than "Preferred", and the reason is a false premise in the
proposal.** Proposal 1 says: *"The reference server already holds the record payloads it built
the entity model from, so populating them is local work."* It does not. Measured two ways on
2026-08-14:

- The model is built with `SZ_ENTITY_DEFAULT_FLAGS`, and reading the SDK's own flag constants
  (Senzing 4.3.4, `senzing.SzEngineFlags`) shows that composite **excludes**
  `SZ_ENTITY_INCLUDE_RECORD_FEATURES` and `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA`. It includes
  `SZ_ENTITY_INCLUDE_RECORD_DATA` and `SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO` — which is
  precisely `data_source`, `record_id` and the matching info the server does return.
- `get_sdk_reference(topic='response_schemas', filter='get_entity_by_record_id')` (MCP server
  1.32.9, same date) confirms that per-record `name`/`address`/`phone` live under
  `RESOLVED_ENTITY.RECORDS[].FEATURES.*` and `…JSON_DATA.*` — the branches those two excluded
  flags populate.

So the server was returning exactly what its flags yield, and the contract was describing data
that was never in the response. Criterion 1 permits this direction in terms
(*"or the contract no longer claims they do"*), and criteria 2–5 are direction-independent, so
all six are satisfied.

**Two things were done to avoid losing the spec's actual point.** Its argument for enriching the
Records panel is sound as UX — a panel showing only a source code and a record id shows nothing
the graph did not. So the contract now documents the **enrichment route** explicitly (add the two
flags; take the values from `FEATURES[].FEAT_DESC` or `JSON_DATA`, confirmed against the server
rather than from the contract), marked optional, with the reason it is not the default: this
payload is embedded in the standalone snapshot (INV-070) and Query, Visualize and Discover points
the same app at the Bootcamper's whole dataset, so per-record features multiply the keepsake by
the record count. Keeping the composite is also consistent with the repo's existing position that
DEFAULT composites are correct for exploration and that rewriting a learning example into
production shape is the INV-169 error (`tests/test_default_flags_production_caution.py`).

**`match_key` was placed on the record, not the entity** — proposal 3 asked for a decision, and
per-record is both what the server returns and, as the spec notes, the more informative
placement: it is the key that pulled *that* record in. Its empty value is documented as the seed
record.

**The contract test does not start the server.** Criterion 5 asks for a test that "starts the
reference server against a small fixture". Starting it requires a live engine and a loaded Truth
Set, neither of which exists in this environment, so the payload **constructors** are exercised
directly against a hand-built `Model` — they are pure functions of the model, and the assertion is
the same one a client would make. ⚠️ That substitution has a hole, and it was found by a mutation
rather than by reasoning: with a hand-built fixture, a key **added** inside `Model.build` is
invisible. `tests/test_visualization_api_contract.py` therefore also parses `build`'s entity and
record dict literals and asserts their exact key sets, which is the only route to them without an
engine. Recorded here because a future reader with a live engine should replace that source-text
check with a real request.
