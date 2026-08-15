# The any-language contract guard checks a hardcoded requirement set

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`tests/test_any_language_contract_complete.py` enforces the INV-002/INV-090 boundary rule: a
requirement constraining the server **the Bootcamper builds** must be stated as behaviour in
`visualization-api-reference.md`, not only in the Python reference implementation. It checks a
hardcoded dict of five requirements:

```python
"inline-<script> escaping (stored-XSS guard, INV-106)": [...]
"HTML escaping of data-sourced strings (INV-106)": [...]
"offline rendering / no CDN (INV-091)": [...]
"tab identifiers and deep-linking (INV-124)": [...]
"data-source colours assigned from the data (INV-127)": [...]
```

A **sixth** requirement — a new invariant binding the Bootcamper-built server, stated only in
`senzing_viz_server.py` and never written into the contract — passes this guard silently. That is
precisely the failure the guard's own docstring records having already happened once:

> Offline rendering (INV-091) is stated in the build guidance in plain terms. **Escaping was not.**

⚠️ **There is no live gap today.** Every visualization-group invariant was checked against the
contract on 2026-08-15 and each is either stated as behaviour, or is plugin-side apparatus the
Bootcamper does not build (and so is INV-002-exempt):

| Invariant | Disposition |
|---|---|
| INV-106, INV-091, INV-124, INV-127 | stated; already in the guard's dict |
| INV-155 (six tabs) | stated — the tab table at `visualization-api-reference.md:663` |
| INV-232 / tab suppression | stated — the "Shown when" column at `:570-575` gives all three gates |
| INV-171 (idempotent view switch) | stated at `:694` |
| INV-153, INV-154, INV-221, INV-223 | cited in the contract |
| INV-122, INV-235 (capture helper), INV-107 (Python fallback constants) | plugin-side apparatus, INV-002-exempt |
| INV-130 (snapshot rebuild) | a module-flow rule, correctly in `phase2-close.md:85` and cited at `phase1-visualization.md:404` |

**The defect is structural**: nothing keeps that table true as invariants are added.

## Root cause

The dict encodes the requirements its author knew about, which is the same shape as
`guards-enforce-class-scoped-rules-from-hardcoded-site-sets` — the four guards converted to derived
site sets earlier the same day. **This is the fifth instance of that class**, and it was predicted:
that spec's `## Affected files` carries the warning *"This list is where the pattern was noticed, not
necessarily the whole set — re-derive by scanning rather than trusting these four."*

⚠️ **INV-246 does not cleanly bind it, which is why it survived that sweep.** INV-246 requires a
guard to derive its **site set** by scanning; here the members are *requirements*, and "a requirement
that binds the Bootcamper-built server" is a semantic judgement, not something a corpus scan
returns. The detector used earlier (module-level tuples of shipped-file constants, iterated) could
not see this file at all, for the same reason it missed `test_brand_sync.py`.

## Proposed change

Add a **derived proxy** alongside the existing five explicit checks — do not delete them, since each
carries phrase-level detail a scan cannot reproduce:

1. Derive the candidate set by scanning `specs/INVARIANTS.md` for invariants in the
   **"Visualization and screenshots"** index group (the group is already declared in the file, so the
   membership is data, not judgement).
2. For each, assert it is **either** referenced in `visualization-api-reference.md` (by ID or by an
   explicitly registered content phrase) **or** listed in a small, commented `APPARATUS_EXEMPT` set
   naming why the Bootcamper does not build it — capture helpers, PDF generators, the Python
   fallback constants.
3. The exempt set is the judgement half and must stay **small, explicit and reasoned**: an invariant
   added to it without a reason is how this rule would quietly become unenforceable. Adding a new
   visualization invariant then forces a deliberate choice — state it in the contract, or record why
   the Bootcamper does not build it — rather than defaulting to silence.

⛔ **Do not fix this by adding a sixth entry to the dict.** That is the remedy the four earlier
guards already tried.

## Acceptance criteria

- [ ] The guard derives its candidate set from the visualization index group in `INVARIANTS.md`,
      not from a list written in the test.
- [ ] Every derived candidate is either found in `visualization-api-reference.md` or present in an
      `APPARATUS_EXEMPT` set that carries a stated reason per member.
- [ ] The five existing explicit phrase checks survive unchanged — the derivation is additive, and
      deleting them would trade phrase-level precision for coverage.
- [ ] A new visualization invariant that is neither stated in the contract nor exempted fails the
      guard — **negative-controlled**: append a synthetic invariant to the index group, confirm the
      failure, then revert.
- [ ] The scan carries a non-vacuity floor, so a changed index-group heading fails loudly rather
      than reducing the guard to silence.
- [ ] No `plugins/` behaviour changes — this is entirely test-side.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_any_language_contract_complete.py` — add the derived candidate sweep and the reasoned
  exempt set.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15 (fourth run of the day)
  (`Source: self-observed (assistant retrospective)`). Found while checking INV-002's boundary test
  against the visualization group, an area three prior runs the same day had deferred.
- Priority: **Low**. No live gap — the contract is complete for every visualization invariant today,
  verified individually. It is a structural risk in the guard that exists specifically to stop a
  requirement being stated only in the Python reference, and that has already failed that way once
  (INV-106).
- MCP re-check: **n/a (no Senzing fact).** Internal consistency between the plugin's own contract,
  its reference implementation and its ruleset; no MCP tool was called for this finding and no
  Senzing claim is asserted. Server **1.32.9** was recorded this session.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `guards-enforce-class-scoped-rules-from-hardcoded-site-sets` (the same class, four
  instances, implemented 2026-08-15 — this is the fifth, and that spec predicted it), and INV-002,
  INV-090, INV-106, INV-246.
