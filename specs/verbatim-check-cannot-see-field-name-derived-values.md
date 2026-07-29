# sz_verbatim_check.py cannot see values derived from a source FIELD NAME, not just non-string values — the module's own crypto-currency example triggers it

Maintain the invariant conditions in @INVARIANTS.md.

## Problem

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
already documents one gap in `sz_verbatim_check.py`'s harvesting logic: it cannot see a
source value stored as a JSON number, because its allowed-set builder only walks
`isinstance(obj, str)` values. That section's 4-step resolution (don't conclude the
mapping is wrong; confirm faithfulness on the Entity Specification's terms; record the
exemption and proceed; never alter a source value to satisfy the tool) is exactly right
— but it is scoped to **non-string values**, and there is a second, distinct root cause
the same section does not cover: a value that is faithfully derived from a source
**field NAME** rather than a source field **value**.

The module's own inline mapping reference (delivered at `mapping_workflow` step 2)
documents this pattern as the canonical, correct way to map a real, common shape:

> "A crypto/'Digital Currency Address' (Bitcoin/XBT, ETH, USDT, XMR, LTC, TRX, XRP,
> BCH, …) maps as ACCOUNT_NUMBER = the address string, ACCOUNT_DOMAIN = the
> currency/network code (e.g. 'Digital Currency Address - XBT 1A1zP...' ->
> ACCOUNT_NUMBER:'1A1zP...', ACCOUNT_DOMAIN:'XBT')."

Following this exactly on a real OFAC SDN export (`data/raw/ofac_moscow.jsonl`, root
fields `"Digital Currency Address - LTC"`, `"- XBT"`, `"- ETH"`, etc.) produces a mapper
that `sz_verbatim_check.py` **fails outright** (exit 1, 43 offenders, all
`ACCOUNT_DOMAIN`), because `"LTC"`, `"XBT"`, etc. never appear as a **value** anywhere in
the source record — only as substrings of the field **name**. Verified directly: for
every one of the 17 records carrying a "Digital Currency Address - <CODE>" field in this
file, the currency code does not appear as a standalone string value anywhere else in
that same record.

Unlike the non-string-value case, there is **no alternative correct mapping** that would
also satisfy the checker — the ACCOUNT_DOMAIN value is definitionally derived from the
key, not from any value the checker's harvester walks. A bootcamper following the
module's own worked example word-for-word hits this exact wall with no guidance that it
is a checker limitation rather than a mapping defect, and `mapping_workflow`'s own step-4
instructions ("Exit 1 = a code bug... Do NOT proceed until it passes") point the wrong
direction for this specific, unfixable-by-code case.

## Root cause

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`,
the "⛔ The verbatim check cannot express a non-string source value" section
(~lines 307-339): scoped only to the JSON-number/boolean cause it was written for, with
no analogous carve-out for a value sourced from a field name rather than a field value —
even though the module's own crypto-currency example (same file, inline mapping
reference delivered at step 2) produces exactly this case.

## Proposed change

Extend the existing section (or add an adjacent one immediately after it) to name this
second root cause explicitly, using the same 4-step resolution already established:

1. State the general principle: `sz_verbatim_check.py`'s allowed set is built from source
   **values** only — any value legitimately derived from a source **field name**
   (a dynamic-key convention, e.g. `"Digital Currency Address - <CODE>"`,
   `"Listing Date (EO 14024 Directive N):"`) will never be found in it, regardless of the
   value's own type.
2. Name the concrete instance: `ACCOUNT_DOMAIN` parsed from a
   `"Digital Currency Address - <CODE>"` field name is real, faithful routing, not
   fabrication — confirm this the same way as the non-string case (check the currency
   code does not independently appear as a value elsewhere in the record; if it did, that
   would be evidence of a different, wrong mapping).
3. State plainly that `mapping_workflow`'s own step-4 instruction to treat a verbatim
   exit 1 as a blocking code bug does not apply to this class of failure: there is no
   code fix that produces a different, still-faithful `ACCOUNT_DOMAIN` value that would
   satisfy the checker, so submitting `rework_code` would be inaccurate and unproductive.
   Record the exemption and proceed with `approve`, per the same "never alter a source
   value to satisfy the tool" rule already stated for the non-string case.
4. Cross-reference this section from wherever the crypto-currency inline example first
   appears, so a bootcamper reading the worked example forward (not backward from a
   verbatim-check failure) sees the caveat before hitting it.

## Acceptance criteria

- [ ] `phase2-data-mapping.md` names "value derived from a source field name" as a second,
      distinct cause of `sz_verbatim_check.py` false-positive failures, alongside the
      existing non-string-value cause.
- [ ] The `ACCOUNT_DOMAIN`/"Digital Currency Address - <CODE>" case is named as the
      concrete example, with the same do-not-alter-the-mapping resolution.
- [ ] The text states explicitly that `mapping_workflow`'s generic "exit 1 = code bug"
      instruction does not apply to this class, so a bootcamper does not loop trying to
      "fix" an unfixable checker gap.
- [ ] Cross-platform / language-agnostic: this is a prose-only addition to bootcamper-facing
      guidance, unaffected by OS or the bootcamper's chosen mapper language.
- [ ] A live mapping of a source containing a dynamic-key currency/domain-style field
      (this spec's own OFAC reproduction is sufficient evidence) confirms the described
      failure mode and that `approve`-despite-exit-1 is the correct outcome — already
      verified live in the session that produced this spec (2026-07-29); no further
      runtime verification is needed to implement the prose fix.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
  (the verbatim-check-limitation section, ~lines 307-339, and the inline crypto-currency
  reference wherever `mapping_workflow` step 2 delivers it — same file, not separately
  editable since it is server-delivered content, so the cross-reference lives on the
  plugin side only).

## Source

Self-observed during a maintainer-run phase-3 dry-run walk (`.claude/skills/dry-run/`),
mapping a real OFAC SDN source (`data/raw/ofac_moscow.jsonl`) end-to-end through
`mapping_workflow`, following the module's own crypto-currency worked example exactly as
written. Not bootcamper-reported. Date: 2026-07-29.

## Deviations from this spec, and why (2026-07-29)

- **The spec's central quote was confirmed — but it does not live where a reader might look for it.**
  The crypto/`ACCOUNT_DOMAIN` text is delivered in `mapping_workflow` **step 2's inline SENZING
  MAPPING REFERENCE** (verified by running `mapping_workflow(action='start')` then advancing from
  step 1; server **1.32.2**, 2026-07-29). It is **not** in `senzing_mapping_examples.md`: that
  resource was fetched and searched and contains **zero** occurrences of `ACCOUNT`, "crypto", "XBT",
  "bitcoin" or "currency". The spec's phrasing ("the module's own inline mapping reference, delivered
  at `mapping_workflow` step 2") was accurate; this note records the precise location so a future
  reader can re-verify it without hunting.
- **The failure was reproduced independently, not taken from the spec.** Two records with fields
  `"Digital Currency Address - XBT"` / `"- LTC"`, mapped per the reference, gave
  `rec0 ACCOUNT_DOMAIN='XBT'; rec1 ACCOUNT_DOMAIN='LTC'`, exit 1, on server 1.32.2 (2026-07-29).
  `ACCOUNT_DOMAIN` is neither in `EXEMPT_KEYS` nor `_TYPE`-suffixed, so no waiver applies. The
  mapping's correctness was confirmed separately: `ACCOUNT_DOMAIN` is "Domain/system for the account
  number" (`search_docs(category='data_mapping')`, Entity Specification → Feature: ACCOUNT,
  2026-07-29).
- **The forward cross-reference landed at the plugin's step 11 (Map), not at the example itself** —
  the example is server-delivered and not editable from here, exactly as the spec's Affected-files
  note anticipated.
- ⚠️ **A material finding outside this spec's scope: the adjacent section's NUMERIC premise is now
  fixed upstream.** That section (and `tests/test_verbatim_check_limitation.py`) states, verified
  against server 1.32.1 on 2026-07-28, that `collect_strings()` captures `isinstance(obj, str)` only
  and that a JSON **number** therefore fails under both emissions. On **1.32.2** that is no longer
  true: `collect_strings()` now also flattens int/float via `str(obj)`, and re-running the checker
  gives exit **0** for a source `RegKey: 1001` emitted as `"1001"` and for `98.6` → `"98.6"`
  (verified 2026-07-29). Booleans remain excluded, deliberately and with a documented reason, so
  `true` → `"true"` still fails.

  Correcting that text properly means retiring part of the implemented spec
  `verbatim-check-numeric-source-values` and rewriting three of its tests, which is a maintainer
  decision and a `feedback-to-specs` job — not something this implementation should do unasked (the
  skill's "already fixed upstream" rule says propose and report, not rewrite). So the original
  sentences were left **verbatim**, preserving both the historical claim with its original 1.32.1
  date and the tests that pin it, and a dated ⚠️ correction note was **added** beside them telling
  the reader to run the check before recording any non-string exemption, and not to record a
  numeric-value exemption on 1.32.2 or later. This spec's own addition does not depend on the stale
  premise: it is scoped to values derived from a field **name**, which fail regardless of type.
