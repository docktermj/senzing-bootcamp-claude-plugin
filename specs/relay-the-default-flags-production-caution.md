# The server cautions that DEFAULT_FLAGS composites are not for production code; the plugin never relays it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`get_sdk_reference(topic='flags', …)` returns a top-level `caution` field the plugin has never
carried into its guidance. Verbatim, from **MCP server 1.32.9, 2026-08-12**
(`get_sdk_reference(topic='flags', filter='find_network_by_entity_id', language='python')`):

> **PRODUCTION GUIDANCE:** `*_DEFAULT_FLAGS` composites are intended for getting started and
> exploration, not for production code. Their membership may change between Senzing versions, so
> code pinned to a DEFAULT flag can silently change what it returns after an upgrade — no error is
> raised. They also return more than most callers need, and unrequested data costs engine work and
> response size. In production, request exactly the flags whose output you consume (OR the specific
> `SZ_*` flags together) rather than relying on a DEFAULT composite.

**The plugin teaches the opposite for its production deliverable, and is right to teach it for the
bootcamp.** Two facts that only matter together:

1. The bootcamp deliberately starts from DEFAULT composites, and the server's own wording blesses
   that for *exploration*: `phaseD-validation.md:231` says *"start from `SZ_EXPORT_DEFAULT_FLAGS`,
   dump one row, and read its top-level keys"*, and `:266` ships that flag in runnable code.
   Module 7 teaches composite **membership** at `phase1-query-visualize.md:66-88`.
2. **Graduation copies that code into the production deliverable.**
   `graduation/SKILL.md:711-714` maps `src/transform/**`, `src/load/**`, `src/query/**` and
   `src/utils/**` into `production/src/…`. `src/query/` is where the DEFAULT-composite query code
   from Module 7 lives, so the exploration-shaped flag choice becomes the production artifact
   verbatim.

**Nothing bridges the two.** `DEFAULT_FLAGS` appears **24 times** across four shipped files and
**zero** of those lines mention the caution, upgrade-fragility, or over-fetching
(`grep -rn 'DEFAULT_FLAGS' … | grep -icE 'production|exploration|getting started|may change'` → 0,
2026-08-12). `production/MIGRATION_CHECKLIST.md` — six sections, Database / Security / Licensing /
Performance / Data / Deployment (`graduation/SKILL.md:766`) — has no item for it either, even though
that checklist exists precisely to carry production concerns the bootcamp does not cover in depth
and already marks such items ⚠️.

**Why this is not covered by the existing flag invariants.** INV-179, INV-194 and INV-169 all govern
DEFAULT composite **membership** — which sub-flags a composite carries, and how to diagnose a blank
field. This caution is a different claim: that pinning *production* code to a DEFAULT composite is
unsafe **across versions**, and fails **silently with no error raised**. INV-179's remedy ("OR in
the missing sub-flag") is the same mechanical action this caution wants, but for the opposite
reason and at a different time — INV-179 fixes a field that is blank *today*; this is about a field
whose contents change *after an upgrade*, on a machine the Bootcamper owns and the bootcamp never
sees.

**Severity is bounded and worth stating.** Nothing breaks during the bootcamp, and no artifact the
Bootcamper receives is wrong. The cost is that the plugin hands over a `production/` project whose
flag usage the authoritative source calls not-production, without telling them — and the failure
mode it warns about is silent, so the Bootcamper has no way to discover it later from the code.

## Root cause

The DEFAULT-composite work in this repo has all been *diagnostic*: every prior spec on the subject
(`method-default-flags-omit-record-data`, `why-entities-default-flags-has-no-composite-members`,
`export-related-entities-is-flag-conditional`) started from a field that read blank and asked which
flag populates it. That framing consumes `composite_members`, `applies_to` and `response_paths` from
the `topic='flags'` response and never had reason to read the response's **top-level `caution`**,
which is not attached to any individual flag entry.

So the field was structurally invisible to the way the plugin has always used this tool: sibling to
`data[]` rather than inside it, and only relevant to a lifecycle stage (post-graduation upgrade)
that no bootcamp step reaches.

## Proposed change

Two edits, both small, and deliberately **not** a change to what the bootcamp teaches.

1. **Relay the caution where flags are taught, scoped to production.** In
   `module-07-query-visualize-discover/phase1-query-visualize.md`, beside the existing composite
   table (`:66-88`), add the server's caution with its provenance (tool, parameters, server version,
   date), and state the split plainly: *starting from a DEFAULT composite is correct for the
   bootcamp — the server calls it the getting-started path — and the code that leaves with you
   should name its flags explicitly.* Do **not** rewrite the bootcamp's own examples to enumerate
   flags: that would trade a learning path the server endorses for noise, and INV-169's lesson is
   that an over-generalized absolute teaches that a correct approach is broken.

2. **Add the migration-checklist item.** In `graduation/SKILL.md`, add a ⚠️ item under
   `production/MIGRATION_CHECKLIST.md`'s **Performance** or **Data** section: replace
   `*_DEFAULT_FLAGS` in `production/src/` with the explicit `SZ_*` flags whose output the code
   consumes, because composite membership may change between Senzing versions and the change is
   silent. This is exactly the checklist's stated purpose — a production topic the bootcamp does not
   cover in depth — so it needs no new mechanism.

**Re-verify before implementing.** The `caution` text is a server string and may be reworded or
moved; re-read it via `get_sdk_reference(topic='flags', …)` and quote what the server returns then,
not this spec's copy (INV-080).

## Acceptance criteria

- [ ] `phase1-query-visualize.md` carries the caution with full provenance (tool, parameters, server
      version, date), and states that DEFAULT composites are right for the bootcamp and explicit
      flags are right for code that ships.
- [ ] `graduation/SKILL.md` adds a ⚠️ `MIGRATION_CHECKLIST.md` item for replacing `*_DEFAULT_FLAGS`
      in `production/src/` with explicit flags, naming the silent-change-on-upgrade reason.
- [ ] The bootcamp's own runnable examples are **unchanged** — `phaseD-validation.md:266` still
      starts from `SZ_EXPORT_DEFAULT_FLAGS`, and no example is rewritten to enumerate flags.
- [ ] A test asserts the caution is relayed wherever the composite table is taught, and that the
      migration-checklist item exists — so neither can be silently dropped. Negative-controlled:
      removing either fails the suite, with the mutation verified to land.
- [ ] The relayed text is checked against the live server at implementation time, not copied from
      this spec (INV-080). If the server has reworded or removed the caution, implement what it says
      then and record the deviation.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      caution is binding-independent and must not be written as a Python-only note.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  relay the caution beside the composite table (`:66-88`).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the `MIGRATION_CHECKLIST.md` item
  (`:766`).
- `tests/` — the guard.

## Source

- Dry run: `dry-run` phase 1 (MCP call contracts), 2026-08-12, server **1.32.9**
  (`Source: self-observed (assistant retrospective)`). Found while probing INV-132's correction —
  the probe confirmed the invariant and surfaced this in the same response's `caution` field.
- Verified correct in the same pass, so a later run need not re-check: all **42** distinct `action=`
  / `topic=` / `category=` / `workflow=` / `platform=` / `dataset=` / `language=` literals the
  plugin uses are in their schema enums (the only out-of-enum hits are template placeholders such as
  `<chosen_language>`); the server's five `common_confabulations` are all absent from the plugin
  (`add_data_source`, `G2Engine`, bare `close_export`, `EMPLOYER_NAME`, V3 patterns) and the correct
  `register_data_source` is used instead; and the plugin uses neither
  `SZ_ENTITY_INCLUDE_RECORD_FEATURES` nor `SZ_ENTITY_INCLUDE_NAME_ONLY_RELATIONS`, so the v4.1.0
  `FEATURES` → `FEATURE_IDS` rename and the v4 name-only reclassification do not reach it.
- Priority: **Medium.** No live defect and nothing a Bootcamper sees during the bootcamp; the cost
  is a production deliverable whose flag usage the authoritative source calls not-production, handed
  over silently.
- MCP re-check: **still current** — the caution was read from server 1.32.9 on 2026-08-12 via
  `get_sdk_reference(topic='flags', filter='find_network_by_entity_id', language='python')`. Whether
  it is new in 1.32.9 or long-standing was **not** determined; the plugin has never carried it
  either way.
- Upstream: not applicable — the server is correct here; the plugin is the thing that is stale.
- Related specs: `specs/method-default-flags-omit-record-data.md` (INV-179),
  `specs/why-entities-default-flags-has-no-composite-members.md` (INV-194),
  `specs/export-related-entities-is-flag-conditional.md` (INV-169) — all three govern composite
  *membership*, not production suitability.
