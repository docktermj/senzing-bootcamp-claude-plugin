# Search both `NAME_FULL` and `NAME_ORG` — a `NAME_FULL`-only search silently misses organizations

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Searching `"ABSOLUTE DENTAL"` — an organization present many times in the loaded data — returned
**0 results**. A person name returned a hit immediately, which is the only reason the empty result
looked suspicious rather than believable.

The search built its attribute document as `{"NAME_FULL": "<query>"}`. The loaded dataset was roughly
half organizations (EQUIFAX alone: 39,110 `ORGANIZATION` vs 33,689 `PERSON`), so **search silently
failed for about half the population**. Trying `NAME_FULL` then `NAME_ORG` returned 10 hits for
`"ABSOLUTE DENTAL"` and 10 for `"AUTONATION"`.

Two things make this High priority:

- **It is silent.** An empty result set is indistinguishable from "not in the data", so a bootcamper
  concludes their load failed or their data is thin, rather than that the query is wrong. This is
  exactly the blank-output failure class INV-115 exists to stop, arriving through a query rather than
  a parse.
- **It is in the bundled reference implementation**, which every non-Python build is modeled on
  (INV-090), so the defect propagates into whatever language the bootcamper chose. It was reproduced
  independently in two places in one session — the query program's search subcommand and the
  visualization server — before being traced, because both were modeled on the same reference.

Any bootcamper whose data contains organizations gets a Search / Probe tab that appears to work and
finds nothing.

## Root cause

**`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:436`**, in `Model.search()`
(`:432-461`):

```python
attrs = json.dumps({"NAME_FULL": query})
```

`NAME_FULL` is the wrong attribute for an organization name. Confirmed against the Senzing MCP
server (`search_docs`, category `data_mapping` → Senzing Entity Specification, "Name > Feature:
NAME"):

| Attribute | Guidance |
|---|---|
| `NAME_ORG` | Organization name. |
| `NAME_FULL` | Single-field name when type (person vs org) is unknown or only a full name is provided. |

and the specification's rule: *"use `NAME_ORG` for organizations; use `NAME_FULL` only when the type
is unknown or only a single field exists."* An organization name supplied as `NAME_FULL` does not
match records mapped with `NAME_ORG`.

**Nothing in the guidance names the trap.** `NAME_ORG` appears in the plugin only in
`module-05-data-quality-mapping/phase1-quality-assessment.md` (as a mapping target) and in an example
recap — never in the Module 7 query guidance, where a bootcamper writes the search. So the reference
implementation models the wrong attribute and no text corrects it.

**The chips contract would have caught it and does not check.**
`module-03b-truthset-visualization/visualization-api-reference.md:720` requires the Search / Probe tab
to ship "pre-verified example queries as clickable chips", and `:444` calls them "pre-verified" — but
nothing verifies at build time that a chip returns a match. The contract exists precisely because a
hint that returns nothing is worse than no hint, which is this defect's exact shape.

## Proposed change

1. **Search both attributes in the bundled reference.** In `Model.search()`, issue the
   `NAME_FULL` search, and when it yields no results retry with `{"NAME_ORG": query}` before
   reporting empty. Merge/deduplicate by `ENTITY_ID` if both are sent. Do not guess further
   attributes — confirm any addition against `search_docs`/`get_sdk_reference` at implementation
   time (INV-080).

2. **State the rule in the any-language contract, not only the Python reference.** The search
   behavior belongs in `visualization-api-reference.md`'s `/api/search` description so a server
   generated in any language inherits it (INV-090/INV-124) — the defect propagated precisely because
   the behavior lived only in the Python file.

3. **Add the attribute guidance to Module 7's query step.** One line where the bootcamper writes
   search code: `NAME_FULL` is for names whose type is unknown, `NAME_ORG` is the organization name
   attribute, and a search for organization data must use it — citing the Entity Specification's NAME
   feature via MCP rather than asserting it (INV-080).

4. **Make the example chips actually pre-verified.** At build time, run each candidate chip query and
   keep only those that return at least one hit; if a chip returns nothing, drop it and say so on
   stderr rather than shipping a hint that finds nothing. This closes the contract's existing
   "pre-verified" claim and would have caught this defect on its own.

5. **Report an empty search result as possibly-wrong-attribute, not as absence.** When a search
   returns zero results, the UI must not imply the name is absent from the data — the same discipline
   INV-115 requires for a blank parsed field.

## Acceptance criteria

- [ ] A search for an organization name present in the loaded data returns matching entities in the
      Search / Probe tab, in the bundled Python reference.
- [ ] A search for a person name still returns its previous results — the `NAME_ORG` path is additive,
      not a replacement.
- [ ] `visualization-api-reference.md`'s `/api/search` contract states the two-attribute behavior, so
      a server generated in any language implements it (INV-090/INV-124).
- [ ] Module 7's query guidance names `NAME_ORG` as the organization-name attribute and `NAME_FULL`
      as the unknown-type attribute, sourced from the MCP server rather than asserted (INV-080).
- [ ] Every shipped example chip is verified against the loaded data at build time; a chip that
      returns no match is dropped with a stderr line, and no chip ships unverified
      (`visualization-api-reference.md:720`).
- [ ] A zero-result search states that no match was returned for the attributes tried, and never
      renders as "this name is not in your data" (INV-115).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the fix
      is stated as required server behavior in the contract, with the Python file as its reference
      implementation.

## Affected files

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `Model.search()` (`:432-461`, the
  attribute document at `:436`): try `NAME_FULL` then `NAME_ORG`; empty-result wording.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the `/api/search` contract and the Search / Probe tab row (`:444`), plus the chips requirement
  (`:720`): the two-attribute rule and build-time chip verification.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the query/search step (`:237` mentions the pre-verified chips): add the attribute guidance.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  the chips requirement at `:294`: verify before shipping.
- `tests/` — assert the contract states the two-attribute search and that the reference server
  attempts `NAME_ORG` when `NAME_FULL` yields nothing.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "NAME_FULL-only search silently returns nothing
  for organizations" (2026-07-28, Module Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`;
  `Upstream: not applicable`)
- Priority: High
- Related specs: `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — the blank-output
  rule this applies to a query rather than a parse),
  `specs/visualization-server-in-chosen-language.md` (INV-090 — why a defect in the reference
  propagates), `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-124 — the
  any-language server contract), `specs/snapshot-static-search-results.md`,
  `specs/visualization-why-how-and-clickable-histogram.md`,
  `specs/mcp-grounding-in-every-skill.md` (INV-080)

## Invariants introduced

- `INV-164` — A name search MUST NOT use `NAME_FULL` alone; it MUST also try `NAME_ORG`, MUST report
  the attributes tried, and MUST render a zero-result search as "nothing matched the attributes
  tried" rather than as absence from the data. Binds a server or query program in any language
  (recorded in `specs/INVARIANTS.md`).
- `INV-165` — An example, hint, or suggested query offered to the Bootcamper MUST be verified by
  actually running it and returning at least one result; one that returns nothing MUST be dropped
  with a reported reason, never shipped as a dead control (recorded in `specs/INVARIANTS.md`).
