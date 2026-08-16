# The globalization retrieval names one query for four topics, and that query returns homonyms

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5 tells the guide to answer a Bootcamper's multi-language data question from a single
`search_docs(query="globalization")` call, and promises **four** things from it — "UTF-8 encoding,
non-Latin character support, cross-script name matching, and multi-language data quality best
practices" — immediately followed by "Never answer from training data."

That query does not return the material. Asked live on server **1.32.9**, docs indexed
**2026-08-11 20:52 UTC**, on **2026-08-13**, `search_docs(query='globalization', max_results=6)`
returned:

| # | Result | Bearing |
|---|---|---|
| 1 | "Senzing Globalization Guide" — excerpt is the bare heading `# Senzing Globalization Guide` | no substantive content |
| 2 | `static GLOBAL_ENVIRONMENT` from the Rust SDK (`sz_rust_sdk/core/environment.rs`) | **homonym trap** on "global" |
| 3 | Globalization Guide → "Advanced personal name comparisons > Supported cultural groups" | on topic (name matching) |
| 4 | Globalization Guide → "Enhanced address comparisons" | on topic (cross-script addresses) |
| 5 | FAQ: "How do I implement a persistent, **globally** unique ID …" (MDM Lite) | **homonym trap** |
| 6 | `senzing/postgresql-performance-v4` → "**Global** — more workers" (autovacuum tuning) | **homonym trap** |

So **three of six hits are homonym traps**, the top hit is a heading with no prose, and **the UTF-8
answer — the first thing the step promises — is not in the result set at all.**

This is the exact failure shape INV-212 was registered for on 2026-08-13, in the same words:
*"A step whose output shape exceeds what one obvious query returns, with no strategy for closing the
difference, forces a choice between fabricating and under-delivering"*, and *"a bare link stub in a
result is NOT substantive content and MUST NOT be presented as coverage."* INV-212 also names the
more dangerous half: hits that return **plausible wrong content** rather than nothing. A guide that
opens `GLOBAL_ENVIRONMENT` or PostgreSQL autovacuum tuning and then must produce four paragraphs on
multi-language data quality has "Never answer from training data" as its only remaining instruction.

The Bootcamper path is real and named by the step itself: any source containing Chinese, Arabic or
Cyrillic characters.

## Root cause

INV-212 was registered on 2026-08-13 from `pattern-gallery-asks-for-more-than-mcp-can-supply` and
applied **only at the site that spec was working on**. The globalization retrieval is a second
instance of the same rule and was never swept — the #1 defect class in this audit's own Step 7 ("a
rule applied to some of the sites it binds").

Three sites, and they do not agree with each other:

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md:47-50` — bare
  `search_docs(query="globalization")`, **no category**, promises the four topics. The worst of the
  three: it is the only one that states an output shape, and the shape is unreachable.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:507` —
  bare `search_docs(query="globalization")`, **no category**, no output shape.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md:287` —
  `search_docs(query="globalization", category="globalization")`. **This site already carries the
  filter**, which is what makes the other two a drift rather than a uniform gap.

**The working route, established live the same session.** `search_docs(query='UTF-8 encoding
non-Latin character support multi-language data quality', category='globalization')` returns the
Globalization Guide's **"What languages does Senzing support?"** section, which answers the UTF-8
claim directly — *"Senzing utilizes UTF-8 encoding which allows for most languages of the world to
be properly captured and processed … native support for cross-script comparisons"* — plus
"Advanced personal name comparisons > **Additional Cultural Support**", whose transliteration table
covers Indian, Indonesian, Japanese, Polish, Portuguese, East Slavic, Turkish, Yoruban and a Generic
catch-all, and states that *"Japanese Kanji is not directly handled by Senzing and is treated as
Chinese Hanzi when provided"* — a Bootcamper-relevant limitation the current step cannot reach.

⚠️ Note for the implementer: even **with** `category='globalization'`, three of six hits came back
as `category: code_example` (libpostal's `encoding.py`, libpostal-data, a Rust FFI guide) carrying
*higher* `relevance_score` than the on-topic rows (63.6 vs 39.8). The filter promotes the matching
category rather than restricting to it, so the retrieval strategy must name the **document and
section** to look for, not just the filter — which is precisely what INV-212 requires.

## Secondary finding, same root cause

**INV-212's own originating step does not cite INV-212.** `grep -rn "INV-212" plugins/` returns
exactly one hit — `module-00-entity-resolution-concepts/concepts.md:30`, added by
`triage-the-twelve-uncited-hard-rules` — while the pattern-gallery step the invariant was written
from (`module-01-business-problem/phase1-discovery.md:32-62`) cites only INV-080.

This is invisible to `conformance.py rules`, which reports **0** uncited hard rules today: the scan
is satisfied by *any* `INV-NNN` in the enclosing section, so a section citing INV-080 is "covered"
even where INV-212 is the rule doing the work. Same blind spot as the INV-129/INV-218 borrowed
citation, approached from the other end, and it is why INV-183 asks for the governing rule **at the
step**.

## Proposed change

1. **`module-05.../SKILL.md:47-50`** — replace the bare query with a retrieval strategy per INV-212:
   the `category='globalization'` filter, the vocabulary that reaches each promised topic, the
   document and section names ("Senzing Globalization Guide" → "What languages does Senzing
   support?" for UTF-8; "Advanced personal name comparisons" for cross-script names), and the
   homonym trap named explicitly so a guide seeing `GLOBAL_ENVIRONMENT` or autovacuum tuning knows
   it mis-queried rather than that the docs are thin. Cite INV-212.
2. **`phase2-data-mapping.md:507`** — add the `category='globalization'` filter and point at the
   Module 5 `SKILL.md` strategy rather than restating it (INV-183's no-fork clause).
3. **`phase3-test-load.md:287`** — already filtered; add the pointer only. Do **not** restate.
4. **`phase1-discovery.md`** — cite INV-212 at the pattern-gallery retrieval step alongside INV-080.
5. Any negative written into shipped prose (e.g. "bare `globalization` does not return the UTF-8
   answer") carries an `MCP-NEGATIVE` marker with its `owner:` clause per INV-209 — a **routing**
   negative, since the material exists and the owner is the filtered query plus the named section.

⛔ Do not weaken the step's promise to match the thin query. The four topics are the right output
shape; the retrieval strategy is what was missing.

## Acceptance criteria

- [ ] All three globalization retrieval sites pass `category='globalization'`, and none states an
      output shape it cannot reach with the vocabulary it names.
- [ ] The Module 5 `SKILL.md` site names the document **and section** for each promised topic, and
      names the homonym trap; the other two sites point at it rather than forking a second copy.
- [ ] `phase1-discovery.md`'s pattern-gallery retrieval step cites INV-212.
- [ ] Every Senzing claim added is re-asked live in the implementing session, with tool, parameters,
      server version and date recorded; any negative carries a parseable `MCP-NEGATIVE` marker with
      an `owner:` clause (INV-209).
- [ ] A test asserts each site carries the filter and the strategy, structurally rather than by
      pinning the documentation's wording (INV-219), and is negative-controlled.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md` — the strategy.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — filter + pointer.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase3-test-load.md` — pointer.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — the INV-212 citation.
- `tests/` — a new guard for the three sites.

## Source

- Feedback: none — self-observed by `production-readiness-audit` on 2026-08-13 (`Source: self-observed (assistant retrospective)`), from the forward sweep of INV-212, which had been registered hours earlier the same day.
- Priority: **High.** It breaks a documented Bootcamper path (a source with non-Latin characters), the failure mode is fabrication rather than an error, and the step's own "Never answer from training data" line is what makes the fabrication route feel sanctioned. Cheap to fix and the correct vocabulary is already established.
- MCP re-check: **server 1.32.9, docs indexed 2026-08-11 20:52 UTC, 2026-08-13 — the plugin's named route does not reach its promised content.** Tools called: `get_capabilities` (version), `search_docs(query='globalization', max_results=6)` (the six results above), `search_docs(query='UTF-8 encoding non-Latin character support multi-language data quality', category='globalization', max_results=6)` (the working route). `owner-checked: search_docs(query='UTF-8 encoding non-Latin character support multi-language data quality', category='globalization')` — **returns it**: the Globalization Guide's "What languages does Senzing support?" section states the UTF-8 and cross-script answer outright. The material is served; only the plugin's query misses it, so this is a routing finding and **not** an absence claim about the server.
- Upstream: not applicable — the corpus carries the material; the defect is in this plugin's query.
- Related specs: `pattern-gallery-asks-for-more-than-mcp-can-supply` (the spec that registered INV-212, and the first instance of this class), `triage-the-twelve-uncited-hard-rules` (added the one INV-212 citation that exists), `step3b-quality-lookup-misroutes-and-omits-the-evidence-requirement` (the same misrouting shape in Module 7).

## Deviations from this spec, and why (2026-08-13)

- **The re-check found a route this spec never established, and a trap it did not know about.**
  This spec named sections for three of the four promised topics and left "multi-language data
  quality practices" without one. Asked at implementation:
  `search_docs(query='data quality practices multi-language non-Latin',
  category='globalization')` returns, as its **top hit**, the Guide's *"Address matching
  examples > CJK+English cross-script matching (new in v4)"*, whose prose carries the actual
  practice — native-to-native beats native-to-Romanized, and for non-CJK cross-script, Romanize
  via an address-hygiene product and supply **both** forms. So no topic is unreached and no
  absence claim was needed. Separately, the phrase **"best practices" is a second trap:**
  unfiltered, `query='multi-language data quality best practices'` returned **five of five**
  hits as repo `docs/best-practices.md` template files (Markdown lint, Dockerfiles), two of them
  title-only stubs, and **no globalization content at all**. The shipped strategy therefore names
  three traps where the spec named one.
- **The promised topic wording lost one word.** "multi-language data quality **best practices**"
  → "…quality practices", because the phrase itself is the trap above. The promise is unchanged
  in content; only the query-poisoning words are gone.
- ⚠️ **A claim in my first draft was imprecise and an existing guard forced the correction.**
  I wrote that the `best-practices.md` files rank *"above the on-topic rows"*.
  `tests/test_dated_negatives_are_marked` rejected the marker's prose `owner:` clause, and
  re-asking to write a concrete one showed the accurate picture: **unfiltered** the query returns
  5/5 wrong; **with `category='globalization'`** the on-topic rows come back **first** while those
  same files remain in the set carrying the **highest `relevance_score`** (~89–92 against ~12–16).
  The ordering claim was wrong and the score claim was right; both now ship stated separately,
  per INV-169's don't-flatten rule.
- **`tests/test_prescribed_search_queries.py` was not in `## Affected files` and had to change.**
  It requires every prescribed `search_docs` query to be executed and recorded with its observed
  top hit. Four queries were added to `VERIFIED_QUERIES` — two prescribed, two as the evidence
  slots of the markers. It also caught that the marker's `owner:` clause named a phrasing I had
  **not** run (`'data quality practices multi-language non-Latin'`); it was executed before the
  clause was allowed to keep it. Placeholder pseudo-queries (`query='<terms below>'`) were
  replaced with the concrete verified call for the same reason: an unexecuted phrasing is
  indistinguishable from an executed one.
- ⚠️ **Two of my own guard drafts were self-defeating, and their own mutations caught both.**
  The first banned `search_docs(query="globalization")` *at the site whose purpose is to forbid
  it* — INV-219's exact shape, failing on the ⛔ warning and on the marker. The second asserted a
  token appeared **anywhere** in the file, so the trap warning's own quotation satisfied an
  assertion about the instruction; deleting the document name from the prescription left the test
  green. Both are now paragraph-scoped and comment-stripped. That is the **sixth and seventh**
  recorded instances in this repo of asserting a token exists rather than where the claim is made.
- ⚠️ **My markers were malformed on the first pass, which is worse than missing.** Written wrapped
  across lines, they did not match `coverage_reports.py`'s `MCP_NEGATIVE` regex — which is not
  `re.DOTALL` — so both **fell off the re-ask worklist** while looking correct, and the guard test's
  own literal regex registered as a *third* malformed marker. All three fixed: markers are one line
  each, and the test assembles the token at runtime. **Candidate rule, not registered:** the marker
  format is single-line-only and nothing in `implement-spec` Step 3.4 or the scanner's docstring
  says so. Left for the maintainer to rule on rather than smuggled in here.
- **One false alarm of mine, recorded because the method depends on it.** I briefly read the
  prescribed call as missing its closing paren; it was a 118-character terminal truncation of a
  119-character line. Nothing was wrong. The regex tightening it prompted was kept — line-scoped
  `[^)\n]` instead of `[^)]`, which would report an unclosed call as well-formed — and an
  eleventh mutation now proves that guard.
