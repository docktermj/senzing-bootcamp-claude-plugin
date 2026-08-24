# `ground-rules` names a `reporting_guide` response field the server no longer returns

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`ground-rules.md` tells the guide how to recognize a `reporting_guide` language gate, and names the
response fields that come back empty when it fires:

> ⛔ **Always pass `language` to `reporting_guide` — every call, whatever the topic** (INV-192).
> Most topics withhold their content until it is supplied, answering instead with a `needs_input`
> decision tree and **empty** `sdk_patterns` / `sql_patterns` / `design_concepts` (verified on MCP
> server 1.32.2, 2026-07-30).
> (`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:108-111`)

**`design_concepts` is not a field the server returns.** Asked twice on server **1.32.9**, docs
indexed **2026-08-11 20:52 UTC**, on 2026-08-13:

- `reporting_guide(topic='evaluation')`, no `language` — gates as the rule says:
  `"needs_input":{"parameter":"language","decision_tree":{…}}` with `"sdk_patterns":[]`,
  `"sql_patterns":[]`, `"visualization":[]`, `"next_steps":[]`. The third empty content array is
  named **`visualization`**. There is no `design_concepts` key.
- `reporting_guide(topic='dashboard')`, no `language` — does **not** gate: full `sql_patterns`
  (22 queries) and `visualization` (8 entries), no `needs_input`. Again a `visualization` key and
  no `design_concepts`.

**This is `contradicted`, and it is the narrow kind.** The *rule* is correct and re-confirmed —
`evaluation` still gates, `dashboard` still does not, so passing `language` unconditionally is
right and the surrounding paragraph's refusal to keep a per-topic gating list is vindicated by
those two calls disagreeing. What is wrong is one field name in the evidence clause: a reader who
follows the instruction to check for an empty `design_concepts` will not find that key at all, and
may read its absence as the gate not having fired.

INV-169 applied first, and it narrows the claim rather than dissolving it: two of `reporting_guide`'s
eight topics were asked, so the supportable statement is "`evaluation` and `dashboard` return
`visualization`, not `design_concepts`", **not** "no topic returns `design_concepts`". The fix must
not replace one unverified enumeration with another.

## Root cause

The field name was accurate when written. `specs/reporting-guide-topics-gate-on-language.md:15`
records the same three names from server **1.32.2** on 2026-07-30 — `sdk_patterns`, `sql_patterns`,
`design_concepts` — so the response either renamed that array between 1.32.2 and 1.32.9 or never
carried it for these topics. Nothing has re-read the clause since: the enumeration is prose inside a
dated citation, and **no test pins the string** (`grep -rn design_concepts tests/` is empty), which
is precisely why it survived two server minor versions unnoticed.

This is the maintenance-surface problem in miniature. The clause holds three server-owned field
names to make one point that does not depend on any of them.

## Proposed change

**Stop naming the content fields; name the behavior, which is what the rule actually rests on.**
In `ground-rules.md:108-115`, replace the parenthetical enumeration with the gate's own signal:

- The gate is recognized by **`needs_input`** naming the parameter it wants — that is the field the
  rule turns on, it is stable, and INV-192 already defines it as "a gate, not a result".
- State that the response's **content arrays come back empty** when it fires, without listing them.
  If a concrete example is wanted, cite exactly what was observed and scope it: on 1.32.9,
  `topic='evaluation'` returned empty `sdk_patterns`, `sql_patterns` and `visualization`.
- Keep the dated provenance, re-stamped to the call that established it.

**What stays, verbatim in substance:** the ⛔ instruction to pass `language` on every call whatever
the topic; the observation that the parameter is optional in the schema so a gateless call still
returns 200 (the trap); the reasoning that passing it where a topic does not gate costs nothing and
only adds content; and the explicit decision **not** to maintain a per-topic list of which topics
gate. That last sentence is the load-bearing one and this change strengthens it — a field-name list
is the same liability as a topic list, one level down.

No fallback clause is needed (INV-125): this removes a claim, it does not add a call. The step
already depends on `reporting_guide`.

## Acceptance criteria

- [ ] `ground-rules.md` no longer names `design_concepts`, and no longer enumerates
      `reporting_guide`'s content fields as the way to recognize a gate; it names `needs_input`.
- [ ] Any field names that remain are scoped to the topic and server version they were observed on,
      not stated as the response's general shape.
- [ ] The ⛔ "always pass `language`, every call, whatever the topic" instruction, the
      optional-in-schema trap, and the explicit refusal to keep a per-topic gating list all survive
      unchanged in substance.
- [ ] **Re-verification clause:** implementing this requires `reporting_guide(topic='evaluation')`
      with no `language` to still return `needs_input.parameter == 'language'` with empty content
      arrays, and `reporting_guide(topic='dashboard')` with no `language` to still return content
      without gating. If `evaluation` has stopped gating, the whole paragraph is a different problem
      and this spec must be re-triaged rather than implemented.
- [ ] No test asserts `design_concepts` (verified empty at authoring time) — so **no assertion needs
      updating**, and the change must not need one. `tests/test_mcp_call_contracts.py` cites INV-192
      and asserts `reporting_guide` calls pass `topic`; confirm it still passes untouched.
- [ ] INV-192's own dated 1.32.2 clause is **not** edited by this spec: it scopes its claim to a
      server version correctly, and `INVARIANTS.md` is append-only.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the field enumeration at
  :108-115.

## Source

- Skill: `delegate-to-mcp-server` sweep, 2026-08-13. Server **1.32.9**, docs indexed
  **2026-08-11 20:52 UTC** (both axes unchanged since the 2026-08-12 sweep).
- Ledger key: `reporting-guide-design-concepts-field-renamed` (verdict `contradicted`); found while
  re-checking `reporting-guide-gates-on-language`, which itself **holds**.
- Priority: Low-Medium. Nothing a Bootcamper does breaks — the instruction is right and the gate is
  still recognizable by `needs_input`. It is a stale server-owned field name inside a dated citation,
  which is the exact shape this skill exists to find, and it went two minor versions unnoticed.
- Upstream: not applicable — this is our stale citation, not a server defect.
- Related: `specs/reporting-guide-topics-gate-on-language.md` (established the clause on 1.32.2),
  INV-192 (the gate rule), INV-169 (why the claim here is scoped to the two topics asked).

## Deviations from this spec, and why (2026-08-13)

Implemented as written. Two things about the evidence differ from the plan and are recorded rather
than absorbed.

1. **A third topic was asked, and it is named in the shipped text.** The proposed change offered
   `topic='evaluation'` as the one concrete example. At implementation time
   `reporting_guide(topic='graph')` was also asked (server 1.32.9, 2026-08-13) and behaves the same
   way — `needs_input.parameter` of `language`, empty `sdk_patterns` / `sql_patterns` /
   `visualization`, no `design_concepts` — so the clause now names **`evaluation` and `graph` as
   gating and `dashboard` as ungated**. Three topics of eight is still not a general claim about the
   response shape, which is why the recognition rule turns on `needs_input.parameter` and the field
   names stay inside the dated observation. It also independently corroborates INV-192's own
   1.32.2 statement that `graph` gates.
2. **Only `graph` was called in the implementing turn.** `evaluation` and `dashboard` were
   established earlier in the **same session** against the same server version and docs index,
   during the `delegate-to-mcp-server` sweep that produced this spec — not copied from this file,
   which is what INV-080 forbids. Disclosed because "re-verified at implementation time" and
   "re-verified this session" are not the same sentence, and the difference is the kind this repo
   has been bitten by.
