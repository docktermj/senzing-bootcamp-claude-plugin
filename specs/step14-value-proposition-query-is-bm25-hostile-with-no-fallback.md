# Module 1 Step 14's prescribed value-proposition query misses, and the step has no re-query rule or fallback

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 1 Phase 2 Step 14 tells the guide to reinforce Senzing's value for the bootcamper's specific
problem using a **templated** `search_docs` query:

`phase2-document-confirm.md:207-211`:

> Before confirming, reinforce why Senzing ER is valuable for THIS problem. Use
> `search_docs(query='value proposition <use_case_category>', version='current')` and tie the
> value to the bootcamper's specific data, sources, and outcomes (not generic marketing).

Substituting a category from the plugin's own recognized set produces off-topic results. Run live,
**MCP server 1.32.9, 2026-08-12**, with `<use_case_category>` = `Supply Chain`:

| Query | Top results |
|---|---|
| `value proposition Supply Chain` (the template) | `senzing/libpostal: scripts/geodata/chains/chains_tsv.py`, `senzing/libpostal: scripts/geodata/chains/query.py`, `brianmacy/sz_spark: CHANGELOG.md` (a Scala CI section) |
| `supply chain supplier vendor third party risk entity resolution` (re-query) | *Data Source Records (DSRs) Explained* ×3 — subscription **pricing** docs |

Neither returns value-proposition material. The template's failure mode is instructive: BM25 latched
onto **"chains"** in `libpostal`'s geodata *store-chains* scripts and onto a **"CI / supply chain"**
changelog heading — the phrase "supply chain" matching a software-supply-chain section rather than a
business one. The words "value proposition" contributed nothing.

**Two defects, and the second is the one that bites.**

1. **The prescribed query is composed rather than documentation-phrased.** It is exactly the class
   `module-00-entity-resolution-concepts/concepts.md:29-43` documents at length: *"`search_docs` is
   BM25, so phrasing decides what comes back"*, and it records a real prior incident where an
   invented query *"latched onto 'data sources' and 'ingest' and returned record-loading snippets
   and `add_record` flags."* Step 14 hands the guide a query template of the same shape — a generic
   abstract phrase plus a variable — and does so for **every** category in the recognized set.
2. **Step 14 carries no re-query instruction and no fallback.** `concepts.md` pairs its query list
   with a ⛔ rule — *"when a query returns nothing relevant, RE-QUERY with the documentation's own
   phrasing before concluding the material is not covered"* — and names the hazard precisely: *"a
   query that misses looks exactly like documentation that does not cover the topic … leaves nothing
   to say under the MCP-only rule, or worse, makes a training-data fallback feel justified on the
   grounds that MCP 'had no answer'."* Step 14 has neither the rule nor a documented path for an
   empty result. So a guide reaching it with a missing lookup is left choosing between saying nothing
   and inventing marketing — and Step 14's own wording ("not generic marketing") forbids the second
   while the MCP-first invariant (INV-080) forbids sourcing it from memory.

**Why this reaches bootcampers rather than being theoretical.** Step 14 runs on the path to **every**
Module 1 completion — it sits immediately before Step 15's confirmation gate, which is part of the
module's success indicator. And the categories most exposed are the ones Senzing's public pages do
not merchandise: `Senzing Use Cases` (retrieved 2026-08-12) surfaces Customer 360 prominently, while
Supply Chain, Data Migration, Vendor MDM and Insurance are in the plugin's recognized set at
`phase1-discovery.md:66-68` with no equivalent page found by either query above. The template works
least well exactly where the guide most needs help.

**Severity is bounded and worth stating.** Nothing crashes, no artifact is wrong, and a resourceful
guide re-queries anyway (this one did, twice). The cost is that the step's *only* instruction is a
query that can return Scala CI notes, with no stated recovery — and the documented consequence of
that shape, in the plugin's own words, is a training-data fallback that "feels justified".

## Root cause

The re-query discipline was learned in Module 0 and written down **there**. `concepts.md` carries a
curated list of five documentation-phrased queries plus a ⛔ re-query rule, both added because a
composed query had already failed in a real run. Step 14 was written with the same instinct — name a
query so the guide does not improvise — but it was authored as a *template with a substitution slot*
rather than as a list of phrasings that were actually tried, and the accompanying safeguard was not
carried across skill boundaries. Nothing links the two: they live in different modules, and no test
asserts that a prescribed `search_docs` query has either been validated or paired with a re-query
rule.

The `version='current'` argument in the template is a further tell that the line was composed from
the tool's signature rather than from a call that was run and inspected.

## Proposed change

1. **Add the re-query rule to Step 14**, referencing `concepts.md`'s wording rather than restating
   it: if the lookup returns nothing relevant, re-query using the documentation's own vocabulary
   (the use case's business language — "supplier due diligence", "beneficial ownership", "watchlist
   screening" — rather than the abstract phrase "value proposition") before concluding the material
   is uncovered.
2. **Replace the template with per-category phrasings that were actually run**, or drop the
   substitution and prescribe a query that works generally (e.g. `entity resolution business value`
   / `why entity resolution matters`) with the category as an *optional* refinement. A template that
   was never executed for the categories it will be substituted with is the defect.
3. **Give the step an honest fallback.** When no value material is retrievable for a category, say
   so plainly and tie the value to what MCP *did* return elsewhere in the module — for a generated
   scenario, the source counts, record types and mapping findings already in hand — rather than
   reaching for marketing. State explicitly that inventing value claims is forbidden (INV-080) and
   that saying less is the correct outcome.
4. **Guard it.** A test asserting that every prescribed `search_docs(query=…)` literal in shipped
   skill text is either (a) accompanied by a re-query/fallback instruction within the same step, or
   (b) listed in an allowlist of phrasings verified against the server with a date. That is the
   durable form and it generalises past this one step.

## Acceptance criteria

- [ ] Step 14 carries a re-query instruction for an empty or off-topic result, and an explicit
      fallback that forbids inventing value claims and permits saying less.
- [ ] Step 14's prescribed query is either validated against the live server for the recognized
      categories, or generalised so it does not depend on substituting a category that returns
      code examples. Record the server version and date for whatever is asserted.
- [ ] No shipped step prescribes a `search_docs` query as its **only** instruction without either a
      re-query rule or a dated validation.
- [ ] A test asserts the property above across shipped skill files. Negative-controlled: removing
      the re-query instruction from Step 14 fails the suite, with the mutation verified to land.
- [ ] `concepts.md:29-43` is unchanged — it is the correct model and this spec propagates it, rather
      than editing it (`git diff` shows no change there).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      documentation and a text assertion only.

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 14
  (`:207-211`).
- `tests/` — the guard.

## Source

- Dry run: `dry-run` phase 3 (conversational walk), 2026-08-12, at Module 1 Phase 2 Step 14 with a
  generated Supply Chain scenario (`Source: self-observed (assistant retrospective)`). Found by
  *running* the prescribed query rather than reading it — the template looks entirely reasonable on
  the page, and only the result set shows it returning libpostal geodata scripts.
- Both queries and their full result sets are recorded in the Problem section above, against server
  **1.32.9**, docs index **2026-08-11 20:52 UTC**.
- Priority: **Medium.** On the path to every Module 1 completion, and the failure mode the plugin
  itself documents as leading to a training-data fallback. Bounded because a guide that re-queries
  recovers, and because the step's content is reinforcement rather than instruction the bootcamper
  acts on.
- MCP re-check: **still reproduces** — this is a live result from 1.32.9 today, not a carried-over
  observation.
- Upstream: **not applicable.** The server behaved correctly; BM25 returned the best lexical matches
  for the words it was given. The plugin chose the words. Nothing to file.
- Related specs: `specs/find-examples-elision-is-by-design-not-a-failed-retrieval.md` and
  `specs/search-attribute-fallback-survives-a-failed-attempt.md` are the same
  "a retrieval that returns the wrong thing is read as absence" family.
