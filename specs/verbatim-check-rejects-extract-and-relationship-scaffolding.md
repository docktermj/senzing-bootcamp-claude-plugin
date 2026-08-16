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
value derived from a source *field name*. **INV-173 already generalizes the class**: where a
validation gate cannot represent a legitimate input, its finding is not evidence about the data, must
not block, and must not be resolved by altering the data to satisfy the gate. What is missing is the
three specific limitations at the step, so a mapper meeting them recognizes the class instead of
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

## Deviations from this spec, and why (2026-07-31)

**The three limitations were added as a sibling block, not appended to the existing list.** The
spec said to add them "in the existing shape that file already uses". Opening
`phase2-data-mapping.md` showed why that would have been wrong: the existing block is scoped
precisely to what the checker **cannot harvest** — a boolean, and a value derived from a field name
— and closes "Two things it cannot harvest, and they are the whole of this limitation." All three
new entries are a *different* mechanism. The harvester works fine for each; what fails is the
equality test's shape (`extract` emits a substring), the key waiver's coverage (`is_exempt()` has no
entry for `REL_*_DOMAIN` / `REL_POINTER_ROLE`), or the input format (CSV never reaches the harvester
at all). Appending them would have made an accurate sentence false. The harvesting block keeps its
scope, gains "that is the whole of the **harvesting** limitation", and the three sit below it under
their own ⛔ heading.

**Criterion 4 required the CSV note in two places, and that is deliberate rather than duplication.**
INV-183 puts the rule where the artifact is produced, so the crash is named at the step that runs the
script — the reader is there when it happens, and without it a `JSONDecodeError` reads as environment
trouble. The limitations block carries the fuller explanation.
`test_the_csv_limitation_appears_at_the_gate_presentation` slices the text before the harvesting
block and asserts it there specifically, so moving it back out fails.

**One mutation escaped and it was a real test gap.** `test_the_extract_disposition_limitation_is_named`
first asserted that `` `extract` ``, `allowed_values()` and `a.k.a.` each appeared *somewhere* in the
file. Deleting the sentence "Any correct `extract` output is rejected." left all three true —
`extract` is a documented disposition named elsewhere in the file, and the rest of the paragraph
survived — so the limitation could be removed with the test green. It now asserts the claim itself,
and a second mutation confirms softening it to "may be flagged" also fails. **That is the fifth time
in this session a guard of mine asserted words near a property rather than the property**, and the
second where the word in question legitimately appears elsewhere in the same file for an unrelated
reason.

**The re-verification split held, and is reflected in the text.** What was re-confirmed on server
1.32.3 is that the server still *prescribes* both mechanisms — the live `mapping_workflow` schema
declares `extract` with its required `expected_features`, and `search_docs` returns the Entity
Specification's *Feature: REL_ANCHOR* and *Feature: REL_POINTER* sections. Whether the gate still
*rejects* them was **not** re-run: that needs a live `mapping_workflow` run with a workspace and real
sources. The plugin text therefore presents the rejections as dated field observations from
2026-07-27 on SDK 4.3.3.26191 and says explicitly they were not re-run —
`test_all_three_are_dated_field_observations_not_current_mcp_claims` pins that, so the framing cannot
quietly harden into a current claim.
