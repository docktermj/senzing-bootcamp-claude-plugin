# Data collection asks for "mapping complexity" claims a module before the Entity Specification is read, and its own example contradicts the rules

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

In Data collection, a guide recorded in **both** `config/data_sources.yaml` and
`docs/data_source_locations.md` that the CRM's `full_name` field "needs splitting into NAME_FIRST /
NAME_LAST" and that a loyalty file's `member_name` in `"Last, First"` form needs "a different
split". Reading the Entity Specification at Module 5 Step 4 reversed both:

> "Use parsed person names (NAME_FIRST/NAME_LAST/...) only when the source provides separate
> fields; do NOT attempt to parse a single name field—use NAME_FULL for single-field names (even if
> they appear parseable, like "Smith, Robert"). Use NAME_ORG for organizations."

The specification names the `"Smith, Robert"` shape explicitly — the exact form the loyalty source
uses. Both fields map to `NAME_FULL`; neither is split.

This is the cheap kind of reversal — it happened before any mapper was written — but **the wrong
plan had already been committed to two documents a module earlier, where it read as settled fact**.
Splitting the names would have produced a mapping that loads and validates cleanly while degrading
resolution quality silently, which is precisely the class of fault Module 5 warns a quality score
cannot detect.

## Root cause

Two causes. The second is the more consequential and was not in the report.

### 1. The claim is invited a module before the rules are available

- `module-04-data-collection/SKILL.md:209-213` instructs the synthesized-generation branch to
  *"Generate the mapping complexity the scenario promised … names split into components in one
  source and joined in another"*.
- `module-01-business-problem/phase1-discovery.md:145-146` requires the generated scenario be
  *"mapping-complexity-rich (needs at least one transformation when mapped to the Senzing Entity
  Specification)"*.
- The Entity Specification is not fetched until Module 5 (`phase2-data-mapping.md`).

So both Module 1 and Module 4 require a claim **about how the data maps** while the document that
governs mapping has not been read. Describing transformations before reading the rules that govern
them invites exactly this reversal.

### 2. ⚠️ The module's own example of "mapping complexity" is not a transformation

Verified against the live Entity Specification (`download_resource` →
`https://mcp.senzing.com/resources/senzing_entity_specification.md`, 73,051 bytes, fetched
2026-08-16; server 1.32.9). The specification provides **single-field targets** for exactly the
shapes Module 4 cites:

| Source shape | Maps to | Transformation? |
|---|---|---|
| separate first/last fields | `NAME_FIRST` / `NAME_LAST` | none — direct |
| one `full_name` field | `NAME_FULL` | none — direct, parsing forbidden |
| free-text address | `ADDR_FULL` (`"PO Box 19675, Las Vegas, NV 89111"` is the spec's own example) | none — direct |

So *"names split into components in one source and joined in another"* is a **per-source mapping
difference**, not a transformation: each side is a direct field→attribute mapping, and the
specification forbids the parsing that would make it one. The same holds for the free-text-address
example. A scenario generated to satisfy Module 4's stated notion of complexity can therefore
satisfy **none** of Module 1's "at least one transformation" invariant through these two examples.

⚠️ **This does not make the generated scenario vacuous.** The branch's other requirements —
per-campaign duplicates, dates in two formats, missing values, off-pattern values (`:215-243`) — are
real work and unaffected. What is wrong is the two examples the module leads with, and the
inference a guide draws from them.

## Proposed change

1. **Scope Step 2's generation branch to shape, not mapping.** Have it describe *shape differences
   across sources* — one source carries a single name field, another carries components; one
   carries a free-text address, another carries parts — and explicitly **not** state what any field
   maps to. Route the "what it maps to" claim to Module 5, where the specification is in hand.
2. **Fix the two examples at `:209-213`.** Keep them as shape differences (they are good ones — they
   force the Bootcamper to see two sources describe the same feature differently) and stop
   describing them as transformations. Add, from the specification, that a single-field name maps to
   `NAME_FULL` and is never parsed, so a generated scenario is not built on the assumption that it
   will be split.
3. **Reconcile Module 1's invariant.** `phase1-discovery.md:145-146` requires "at least one
   transformation"; it must be satisfiable by something the specification actually calls for. Either
   name the qualifying kinds (date normalization, code/value standardization, splitting a field the
   spec *does* take as components, composing a `RECORD_ID`) or restate the invariant as
   *cross-source mapping divergence*, which is what the teaching actually needs. ⛔ Do not leave it
   as an unqualified "transformation" — that is the wording that produced the reversal.
4. **Say the rule where the mistake is made.** One line in Step 2 naming `NAME_FULL` for
   single-field names, with the `"Smith, Robert"` example, attributed to the Entity Specification.
   The full rules stay in Module 5; what belongs here is the one that changes what gets generated.

## Acceptance criteria

- [ ] `module-04-data-collection/SKILL.md`'s synthesized branch describes shape differences and does
      not state or invite claims about Senzing attribute mappings.
- [ ] Its name and address examples are no longer presented as transformations, and it states that a
      single-field name maps to `NAME_FULL` and is never parsed, attributed to the Entity
      Specification.
- [ ] `module-01-business-problem/phase1-discovery.md`'s Step 4a invariant names what qualifies, or
      is restated as cross-source mapping divergence; it is satisfiable without contradicting the
      specification.
- [ ] Nothing weakens the branch's other generation requirements (quality bands, duplicates,
      off-pattern values, key integrity — INV-180/INV-239).
- [ ] A test asserts the branch carries no "needs splitting"-style mapping claim for a single-field
      name, and that the `NAME_FULL` rule is stated.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      Entity Specification is binding-independent.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the synthesized branch's
  complexity directive (`:209-213`), and the `docs/data_source_locations.md` template at `:557-612`
  if it invites a mapping column.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 4a's
  invariant list (`:145-146`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — confirm
  the `NAME_FULL` rule is stated there as the authority this spec routes to.
- `tests/` — guard for the two criteria above.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Data Quality/Mapping: planned to parse single-field names; the Entity Specification forbids it" (2026-08-15, Module Data Quality, Mapping, and Transformation Phase 1 Step 4; `Source: self-observed (assistant retrospective)`)
- Priority: Medium — no code was written, but the wrong plan was committed to two documents and the failure it would have produced is silent.
- MCP re-check: **server 1.32.9, 2026-08-16 — still reproduces, and the re-check widened the finding.** `search_docs(query='NAME_FULL single name field do not parse NAME_FIRST NAME_LAST', category='data_mapping')` returns the Senzing Entity Specification; the full document fetched from `https://mcp.senzing.com/resources/senzing_entity_specification.md` (the URL `download_resource(filename='senzing_entity_specification.md')` returns) carries the quoted rule verbatim, plus the parallel `ADDR_FULL` single-field form. The entry quoted the rule accurately. What the entry did not report, and this re-check established, is that Module 4's own two examples are direct mappings under that specification rather than transformations — cause 2 above.
- Upstream: not applicable — routed `plugin`. The specification is correct and unambiguous; the plugin contradicts it.
- Related specs: `specs/step3-makes-the-73kb-spec-authoritative-while-the-workflow-forbids-reading-it.md` (when and how the specification is reachable), `specs/download-resource-returns-a-url-not-the-specification.md` (confirmed again here — `download_resource` returned a `mode: "url"` manifest, not content), `specs/synthesized-scenarios-make-the-quality-gate-unreachable.md` and `specs/generated-dataset-is-sized-before-anything-measures-the-license.md` (siblings in the same branch), `specs/completeness-denominator-has-two-readings-on-a-raw-source.md`

## Ordering, stated generally

The report frames this as a sequencing problem — a claim invited before the governing document is
read — and that framing is right and is what change 1 fixes. Cause 2 is what that sequencing
produced downstream: the examples the module hands the generator were themselves authored without
the specification, so they encode the same assumption the Bootcamper is then led into. Fixing the
sequencing without fixing the examples would leave the module still teaching that a joined name is a
transformation waiting to happen.
