# Three shipped steps instruct `search_docs(category=…)` with no `query`, which a schema-respecting client cannot call at all

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`search_docs` declares `query` as its **only required parameter**:

```json
{"properties": {"category": …, "max_results": …, "query": {"type": "string"}, "version": …},
 "required": ["query"]}
```

Verified against the live schema, MCP server **1.33.0**, 2026-08-21.

Three shipped steps instruct the guide to call it with a **category and no query**:

| Site | The instruction |
|---|---|
| `module-02-sdk-setup/SKILL.md:626` | *"For the detailed fix steps, use the Senzing MCP server: `sdk_guide(topic='install', …)` and `search_docs(category='anti_patterns')`."* |
| `module-05-data-quality-mapping/phase2-data-mapping.md:817` | *"Confirm the attribute's expected form via `search_docs(category='data_mapping')` at the time you map it"* |
| `module-05-data-quality-mapping/phase2-data-mapping.md:1011` | the same abbreviated form, offered beside `download_resource(filename=…)` |

**A client that validates arguments against the declared schema cannot make this call.** It is not
a call that returns something unhelpful — it is a call that cannot be constructed. The guide then
either invents a query (unsourced, and the outcome depends on what it invented) or reports the tool
as unavailable.

⚠️ **The first site is in a recovery flow** — the TypeScript-port fallback reached *after*
something has already failed. A second failure there is the worst place for one.

## Root cause

**The abbreviation is indistinguishable from the full form in prose, and only the schema knows the
difference.** `search_docs(category='data_mapping')` reads like a complete call. The same file that
carries site 626 also carries the correct combined form at line 1029 —
`search_docs(query='loading', category='anti_patterns')` — so the pattern is known and applied
inconsistently rather than unknown.

⛔ **This is INV-212's subject, not a typo.** That invariant requires a step retrieving
bootcamper-facing content to carry a **retrieval strategy**: what vocabulary to query with, which
documents hold the material, and which obvious phrasing returns confidently wrong content. A bare
category is the strategy-free form INV-212 exists to forbid, and none of the three sites cites it.

⚠️ **Six further sites are citations, not instructions, and are a lesser but real defect.**
`phase1-quality-assessment.md:258` and `:507`, `module-04-data-collection/SKILL.md:230` and `:504`,
and `phase2-data-mapping.md:586` and `:964` attribute a fact to
`search_docs(category='data_mapping')` with a server version and date but no query. They are
honest about *where* the answer was found and silent about *how*, so the next reader cannot re-run
the check. That cost is not hypothetical: on 2026-08-21 a re-verification of a dated negative
reconstructed a route instead of reading one, asked a different query with a filter, and concluded
a correct claim was false — the INV-194 error, caused by exactly this ambiguity.

`module-06-data-processing/phaseA-build-loading.md:327` is prose **about** what the `sdk` category
indexes, names no call, and is out of scope.

## Proposed change

1. **Give each of the three instructions a query.** Not a placeholder — the vocabulary that
   actually reaches the material, since INV-212 requires the strategy rather than the tool name.
   Site 626 wants the anti-patterns for the platform being recovered; the two mapping sites want the
   attribute or feature being confirmed, which the surrounding step already names.
2. **Cite INV-212 at each**, so the next editor can look up why a bare category is not acceptable.
3. **Give the six citations their query too**, or restate them as "the Entity Specification's *Name >
   Feature: NAME* section" — a destination a reader can reach by any route. ⛔ Do not simply delete
   the tool name: the attribution is what makes the claim checkable at all.
4. **Guard the class by scanning, not by listing** (INV-246): no `search_docs(` in shipped prose may
   carry `category=` without `query=`, with a narrow, commented exemption for prose that discusses a
   category rather than calling it (the `phaseA:327` shape).
5. ⛔ **Do not "fix" this by making `query` optional in the plugin's mental model.** The schema is the
   contract and the server rejects the call; the plugin's prose is the thing under test (INV-080,
   INV-136).

## Acceptance criteria

- [ ] All three instruction sites pass a `query` naming real retrieval vocabulary, and each cites
      INV-212.
- [ ] The six citation sites either carry the query used or name a destination section reachable
      without one.
- [ ] A test asserts no shipped `search_docs(` reference pairs `category=` with no `query=`, deriving
      its site set by scanning; the discussion-of-a-category exemption is explicit and commented.
- [ ] The test is negative-controlled by reintroducing a bare-category instruction and confirming
      failure.
- [ ] `module-06-data-processing/phaseA-build-loading.md:327` is unchanged — it names no call.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      change is shipped markdown and a stdlib-only test (INV-108).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — line 626.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — lines
  817 and 1011 (instructions), 586 and 964 (citations).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  lines 258 and 507 (citations).
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — lines 230 and 504
  (citations).
- `tests/` — the scanning guard.

## Source

- Dry run: phase 1 (MCP call contracts), 2026-08-21. Found by diffing every required parameter in
  the live schemas against every call site in shipped prose — the phase's first documented defect
  pattern, *"a required parameter never mentioned"*.
- Priority: **High** for the three instructions: a documented step cannot be executed by a
  schema-respecting client, and one of them is a recovery path. **Medium** for the six citations,
  which are unreproducible rather than unexecutable.
- MCP re-check: server **1.33.0**, 2026-08-21 — **confirmed**. `search_docs`' declared schema lists
  `query` as its sole required parameter. `owner-checked:` not applicable — this spec asserts no
  absence; the claim is a positive fact about a declared schema.
- Upstream: not applicable — the plugin's calls are what is wrong, not the server.
- Related specs: `specs/pattern-gallery-asks-for-more-than-mcp-can-supply.md` (INV-212's origin),
  `specs/the-negatives-backlog-was-never-re-asked-and-one-claim-is-now-false.md` (the wrong-route
  error this ambiguity caused), `specs/mcp-negative-markers-must-name-the-owning-route.md`

## Deviations from this spec, and why (2026-08-23)

**1. The spec's site enumeration was incomplete — nine named, ten found.** Scanning shipped
markdown for `search_docs(` with a `category=` and no `query=` returned **ten** references. Nine
match the spec's list (its line numbers had drifted by ~30 in `phase2-data-mapping.md`, which the
same run had just edited). The tenth is `phase2-data-mapping.md`'s single-name-field authority
block — the ⛔ *"A single name field maps to `NAME_FULL` — it is not split"* citation, which no
list mentioned. This is INV-246 exactly: a guard given the spec's paths would have certified nine
fixes and been structurally blind to the tenth, so the guard derives its site set by scanning.

**2. All six citation sites already named a destination section**, so criterion 2's second branch
was satisfied before this run — `Name > Feature: NAME`, `Feature: REL_ANCHOR`/`REL_POINTER`,
`Usage types and payload (optional attributes)`, the `Identifiers` section, `Feature: ACCOUNT`.
Each still gained a query anyway, because a named destination does not fix the *call*: the text
still spelled out `search_docs(category='data_mapping')`, a call a schema-respecting client cannot
construct. Naming the destination and naming the route are different repairs and the sites needed
both.

**3. Seven existing guards had to be updated, and five were the same defect.** Files changed
beyond the spec's `## Affected files`:

- `tests/test_fastpath_gates_on_full_mapping.py`, `tests/test_free_data_catalog_caveats.py`,
  `tests/test_group_score_is_not_a_join_prediction.py`,
  `tests/test_shape_claims_precede_mapping_claims.py`, `tests/test_verbatim_check_limitation.py`
  each asserted the **literal** `search_docs(category='data_mapping')`. Adding the required
  parameter broke all five — guards failing on the correction they should welcome, the pattern
  `specs/guards-pinning-a-dated-negative-outlive-it.md` describes. Each now matches the **route**
  (`search_docs(…category='data_mapping')`) rather than an exact argument string, which is what
  they existed to assert.
- `tests/test_free_data_catalog_caveats.py` also uses a **fixed 40-line window** after each
  catalog recommendation. Giving the REL_* citation its query added three lines and pushed
  `"upstream condition"` to exactly the boundary, failing a guard with no connection to this
  change. Widened to 55 with headroom and the reason recorded.
- `tests/test_prescribed_search_queries.py` required each newly prescribed query to be
  **executed and its result written down**. Correct, and satisfied: all seven distinct queries
  are registered in `VERIFIED_QUERIES` with their observed top hit and relevance score. Two
  entries record something a paraphrase would have hidden — the `Identifiers` section heading is
  not a separately indexed chunk, so its member features are the evidence; and a first attempt at
  the anti-patterns query phrased around TypeScript ranked the PostgreSQL/container article first,
  because the corpus has no TypeScript-specific anti-pattern article and the vocabulary that
  works names the **packaging** concern, not the language.

**4. The exemption mechanism is a content marker, not a path list.** The spec asked for "a narrow,
commented exemption" for `phaseA-build-loading.md`'s prose about the `sdk` category. Hardcoding
that path would breach INV-246, so the site declares itself with a
`SEARCH-DOCS-CATEGORY-PROSE:` comment the guard finds by scanning. ⚠️ **A negative control showed
why that needs a cap:** a self-declared exemption can silence a real offender, and adding the
marker above one did exactly that and passed. The guard now pins the exemption count to the single
reviewed site, so any new exemption fails and has to be argued for.
