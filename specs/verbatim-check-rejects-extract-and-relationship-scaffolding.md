# The step-4 fidelity gate rejects two mechanisms the same workflow prescribes, and crashes on CSV

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`mapping_workflow` step 1 ships `sz_verbatim_check.py` and `sz_routing_report.py`, and step 4
presents them as gates with "Do NOT proceed until it passes". A bootcamper mapping four raw sources
end to end (`OPENSANCTIONS_PEP`, `OFAC_SDN`, `ICIJ`, `UK_COMPANIES_HOUSE`) hit three defects in that
gate.

**1 — it rejects the `extract` disposition the workflow documents.** Step 3 documents `extract` for
prose fields and names OFAC SDN `REMARKS` as the canonical example. Repro from the entry:
`ent_num=306`, `Remarks = "a.k.a. 'BNC'."` → a correct extraction emits `NAME_ORG="BNC"` → the gate
reports `rec2 NAME_ORG='BNC'` as a violation. `allowed_values()` accepts only a whole value, a
`|`/`;` segment, or a whitespace token; the tokens here are `a.k.a.` and `'BNC'.`, so **any** correct
extraction from prose fails. The instruction not to proceed then leaves only bad options: emit
`'BNC'.` — quotes and a trailing period inside a name field — or drop a real alias.

**2 — it rejects `REL_ANCHOR` / `REL_POINTER` structural constants.** 31 offenders across 21 records,
every one `REL_ANCHOR_DOMAIN`, `REL_POINTER_DOMAIN` or `REL_POINTER_ROLE`. `REL_ANCHOR_KEY` and
`REL_POINTER_KEY` **pass**, because those carry real source values — so the objection is precisely
and only to the structural constants, which cannot originate in source data. Shared cause with (1):
`is_exempt()` covers `DATA_SOURCE`, `RECORD_ID` and any `*_TYPE` attribute, but not `REL_*_DOMAIN`
or `REL_POINTER_ROLE`.

**3 — it cannot run on a CSV source.** Both scripts call `load_jsonl(source_path)`; usage is
`<source.jsonl> <output.jsonl>`. `mapping_workflow` accepts CSV inputs and step 4 presents both as
gates for any source. On CSV both crash with
`json.decoder.JSONDecodeError: Extra data: line 1 column 5 (char 4)`.

**Both rejected constructs are prescribed by this same server** — verified 2026-07-31, server
**1.32.3**, docs index **2026-07-31 20:21 UTC**:

- `mapping_workflow`'s own live tool schema declares `extract` as a `disposition` with required
  `expected_features`, and declares `derived_as` values `REL_ANCHOR` and `REL_POINTER` with `domain`
  ("for REL_ANCHOR/REL_POINTER") and `role` ("for REL_POINTER") fields.
- `search_docs(query='…relationship…')` returns the Entity Specification's **Feature: REL_ANCHOR**
  and **Feature: REL_POINTER** sections defining `REL_ANCHOR_DOMAIN`, `REL_ANCHOR_KEY`,
  `REL_POINTER_DOMAIN`, `REL_POINTER_KEY` and `REL_POINTER_ROLE`, with rules ("Include at most one
  `REL_ANCHOR` per record", "Do not mix `REL_ANCHOR` and `REL_POINTER` attributes in the same feature
  object") and worked examples.

So the gate blocks output produced by following the specification and the workflow it ships with.

**Why it matters.** A mapper doing the right thing is told it has a defect, and "do not proceed"
pushes toward degrading the data to satisfy a heuristic. Defect 3 is quieter and broader: most raw
sources are CSV, so for many bootcampers the fidelity gate probably never runs at all, and a crash
reads as environment trouble rather than a tool limitation.

## Root cause

The gate's model of a faithful value — whole value, delimiter segment, or whitespace token — is
correct for plain field-to-attribute mapping and has **no representation** for an extracted
substring or for structural scaffolding that has no source value at all. `is_exempt()` is a
key-based waiver list that was never extended when relationship features were added.

This is the third recorded instance of one shape, and the plugin already documents the first two at
`module-05-data-quality-mapping/phase2-data-mapping.md:330-361`: the `EXEMPT_KEYS` waiver, a numeric
source value (fixed upstream since — `:342` records "Numbers are NOT in that list any more"), and a
value derived from a source *field name*. **INV-173 already generalises the class**: where a
validation gate cannot represent a legitimate input, its finding is not evidence about the data, must
not block, and must not be resolved by altering the data to satisfy the gate. What is missing is the
three specific limitations at the step, so a mapper meeting them recognises the class instead of
rediscovering it.

## Proposed change

1. **Add the three limitations to the documented set** at `phase2-data-mapping.md`, in the existing
   shape that file already uses for the numeric-value and field-name-derived gaps — name the
   construct, say why the harvester cannot see it, and route to INV-173's exemption path (verify
   faithfulness against the Entity Specification via MCP, record the reason, proceed).
2. **State the CSV constraint at step 4**, where the gate is presented, so a crash on a CSV source is
   expected rather than read as environment trouble. Name the shim route the bootcamper used — adapt
   CSV→JSONL and call the checker's own `verify()`, so the executed logic stays upstream's,
   unmodified — and keep INV-173's ⛔ against shipping a forked copy of an MCP-delivered validator.
3. **Do not weaken the gate's authority where it is right.** `UK_COMPANIES_HOUSE` passed cleanly
   because it needs neither mechanism; that is evidence the gate breaks only on these two features,
   not that it is unreliable generally.

⚠️ **Do not tell the mapper to change the data.** Emitting `'BNC'.` to satisfy the checker writes
quotes and a period into a name field, and dropping the alias loses a real one. INV-173 exists
because this is the tempting move.

⚠️ **Do not fork the checker.** INV-173 forbids shipping a patched copy of an MCP-delivered
validator, because a fork masks the upstream fix — and the numeric-value gap at `:342` shows these do
get fixed.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` documents all three limitations — `extract` output, `REL_*_DOMAIN` /
      `REL_POINTER_ROLE`, and JSONL-only input — each naming why the harvester cannot see it.
- [ ] Each carries its provenance: the `mapping_workflow` schema and the Entity Specification
      sections that prescribe the rejected constructs, with server version and date (INV-080).
- [ ] The exemption path is the one INV-173 already defines; no new mechanism is invented, and the
      ⛔ against forking the checker survives.
- [ ] The CSV constraint appears **at step 4**, where the gate is presented — not only in a
      limitations list elsewhere (INV-183: the rule belongs at the step).
- [ ] A test asserts all three limitations are documented, so a future edit cannot drop one silently.
- [ ] **Not runtime-verified, and disclosed as such:** that the gate *still* rejects these on the
      current server was **not** re-run this session — it needs a live `mapping_workflow` run with a
      workspace and real sources. What was re-verified is that the server still **prescribes** both
      mechanisms. The plugin text must present the rejection as a field observation dated 2026-07-27
      on SDK 4.3.3.26191, not as a current MCP-sourced claim (INV-080/INV-169).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the
  documented-limitations block (`:330-361`) and step 4's gate presentation (`:314`).
- `tests/` — the three-limitations assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sz_verbatim_check.py rejects two documented
  Senzing mechanisms, and cannot run on a CSV source at all" (2026-07-27, Module: Data Quality,
  Mapping, and Transformation; Priority: High; `Source: assistant-observed during four full
  mapping_workflow runs`).
- Priority: **High.** It blocks correct output on two documented mechanisms and pushes toward
  degrading data; the CSV defect means the gate silently never runs for most raw sources.
- MCP re-check: **server 1.32.3, docs index 2026-07-31 20:21 UTC, 2026-07-31 — the prescriptions are
  confirmed; the rejection is not re-run.** `mapping_workflow`'s live schema declares the `extract`
  disposition and the `REL_ANCHOR`/`REL_POINTER` `derived_as` values with `domain`/`role`;
  `search_docs` returns the Entity Specification's REL_ANCHOR and REL_POINTER feature sections. Tools
  called: `get_capabilities`, `mapping_workflow` (schema), `search_docs`.
- Upstream: **already submitted by the bootcamper on 2026-07-27** (`submit_feedback`, `category=bug`,
  anonymous) covering all three defects. **Do not re-file.** A follow-up would be warranted only with
  something the first lacked — e.g. confirmation that it still reproduces on 1.32.3, which this
  triage did not establish.
- Related specs: `specs/verbatim-check-numeric-source-values.md` (INV-173, the governing class),
  `specs/verbatim-check-cannot-see-field-name-derived-values.md` (the second instance).
