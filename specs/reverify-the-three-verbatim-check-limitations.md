# Re-verify the three verbatim-check limitations

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`phase2-data-mapping.md` records three limitations of `sz_verbatim_check.py` and
labels them honestly as stale:

> These are **field observations from 2026-07-27** on SDK 4.3.3.26191 … They were
> **not** re-run against the current server, so treat them as "expect this, and
> check" rather than as current behavior

Two of the three have now been re-run and both reproduce exactly. The block should
carry that, so a reader gets current behavior rather than a caveat inviting them to
re-derive it. The plugin asks for this check by name; this is the check.

## Root cause

Not a defect — a freshness gap the file itself flags. The observations were correct
and remain correct; only their dating is behind.

## What was re-run

Dry run phase 3, **2026-08-14**, MCP server **1.32.9**, Senzing SDK **4.3.4**
(4.3.4-26210), resource hash `1420ec8d7c32d569`, mapping four synthetic sources end
to end through `mapping_workflow`.

**Limitation 1 — "Any correct `extract` output is rejected." CONFIRMED.**
`support_tickets.jsonl` has a shipping address inside a free-text `body`
(`"Refund not received. Please ship the replacement to 9766 Blackthorn Way,
Pellinore ND 58309."`). Mapped `body` with `disposition: extract`,
`expected_features: ["ADDRESS"]` — accepted by step 3 — and emitted the address as
`ADDR_FULL`, copied character-for-character from the source. `sz_verbatim_check.py`
rejected **all 1,525** extractions:

```text
1525 emitted value(s) are NOT verbatim from the source — they were
transformed/normalized, which is forbidden.
Offenders: rec1 ADDR_FULL='9766 Blackthorn Way, Pellinore ND 58309'; …
```

The mechanism is exactly as the file states: whole-value membership
(`if v.strip() not in allowed`), so a contiguous multi-word substring of a longer
field value is unreachable. The `extract` disposition is still declared in the live
schema with a required `expected_features`, so the workflow offers a disposition its
own step-4 gate rejects by construction.

**Limitation 3 — "Neither script runs on a CSV source." CONFIRMED.** Both
`sz_verbatim_check.py` and `sz_routing_report.py` call `load_jsonl(source_path)` and
are documented `<source.jsonl> <output.jsonl>`, while `mapping_workflow` accepts CSV
and its own step-4 PATHS block names the CSV as `<input_file>`. Unhandled
`JSONDecodeError`, exit 1. The plugin's CSV→JSONL adaptation with upstream's
`verify()` unmodified worked on both CSV sources.

⚠️ One detail to correct while there: the file quotes the crash as
`json.decoder.JSONDecodeError: Extra data: line 1 column 5 (char 4)`. Ours was
`Expecting value: line 1 column 1 (char 0)` — same crash, same cause, different text
because the CSV's first line differs. Quoting one message invites "different message,
different problem".

**Limitation 2 — `REL_ANCHOR_DOMAIN` / `REL_POINTER_DOMAIN` / `REL_POINTER_ROLE`
rejected: NOT re-run.** No source in this walk carried disclosed relationships, so
it stays "expect this, and check".

## Proposed change

1. Re-date limitations **1** and **3** to server 1.32.9 / SDK 4.3.4, 2026-08-14,
   and move them out of the "not re-run" caveat — they are current behavior.
2. Keep limitation **2** under the caveat, and say explicitly that it is the only
   one still unverified, so the next run knows what to target.
3. Generalize the `JSONDecodeError` quote to "a `json.decoder.JSONDecodeError` whose
   text depends on the CSV's first line".
4. Consider promoting limitation 1 in the reader's path. `extract` is not exotic —
   any prose field with an embedded address, DOB or identifier reaches it, and the
   gate's own wording ("a code bug: fix the mapper … Do NOT proceed until it
   passes") points the guide at their own correct code. The block that defuses it
   currently sits ~450 lines into the phase file, well below the step where the
   collision happens.

## Acceptance criteria

- [ ] Limitations 1 and 3 carry the 2026-08-14 / 1.32.9 / SDK 4.3.4 verification and
      are no longer flagged as un-re-run.
- [ ] Limitation 2 is named as the only one still unverified.
- [ ] The `JSONDecodeError` text is generalized rather than quoted exactly.
- [ ] A guide reading the `extract` disposition reaches the "do not iterate, record
      the exemption, proceed" guidance before running the step-4 gate.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` —
  the verbatim-check limitations block.

## Source

- Feedback: dry run phase 3, 2026-08-14 — mapped four sources end to end through
  `mapping_workflow`, hitting the `extract` and CSV limitations for real
  (`Source: self-observed (assistant retrospective)`)
- Priority: Low — the guidance is correct and worked; only its dating is behind, and
  the file asks for exactly this re-check.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-14. `mapping_workflow` step-3 accepted `disposition: extract` with
  `expected_features`; step-4's `sz_verbatim_check.py` rejected all 1,525 correct
  extractions. Still reproduces.
- Upstream: not applicable to the plugin — the collision between `extract` and the
  verbatim gate is the server's, and worth reporting there if it has not been.
- Related specs: `specs/single-page-capture-instruction-produces-zero-images.md`
  (the other bundled-script/instruction mismatch found this run)
