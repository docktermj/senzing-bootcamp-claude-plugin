# Stop enumerating which `reporting_guide` topics gate; always pass `language`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`specs/reporting-guide-topics-gate-on-language.md` (implemented earlier today) fixed six
call sites and recorded, in `bootcamp-onboarding/ground-rules.md:100`, **which** topics
gate:

> `topic='evaluation'` and `topic='graph'` both gate, and `topic='data_mart'` gates again
> on `scale`. `topic='quality'` does **not** …

That list is **incomplete**, and the omission was found one sweep later.
`reporting_guide(topic='entity_views')` also gates — verified on server 1.32.2, docs
indexed 2026-07-29 11:11 UTC, 2026-07-30 — and it returns **less** than the others:

```text
reporting_guide(topic='entity_views')
  → needs_input on `language`
  → sdk_patterns: []   sql_patterns: []   visualization: []
  → anti_patterns: []  next_steps: []     dependencies: []
```

Every section empty. `evaluation` and `graph` at least return their `anti_patterns`, so a
caller sees *something*; `entity_views` returns a decision tree and nothing else.

Two concrete consequences:

1. **`ground-rules.md:100` reads as exhaustive and is not.** A reader deciding whether a
   given topic needs `language` will consult that list, find `entity_views` absent, and
   conclude it is in the same category as `quality`. This directly violates **INV-192**,
   recorded the same day: *"where a tool gates on only some inputs the guidance MUST say
   which"* — an enumeration that omits a gating topic fails that clause more misleadingly
   than saying nothing would.
2. **The regression guard does not cover it.**
   `tests/test_mcp_call_contracts.py::TestGatingTopicsAlwaysPassLanguage` scans for
   `GATING_TOPICS = ("evaluation", "graph", "data_mart")`. A future bare
   `reporting_guide(topic='entity_views')` passes the suite. The one shipped
   `entity_views` call (`module-07-query-visualize-discover/phase2-discover.md:15`) is
   currently correct only because it was changed on the *inference* that graph-adjacent
   topics gate — the inference happened to be right, and nothing was holding it.

## Root cause

The enumeration is itself the defect. "Which topics gate" is a **per-topic fact about the
server**, held in the plugin, that no test can refresh — precisely the maintenance
liability this sweep exists to find. It was accurate as to what had been probed and was
disclosed as partial in the spec and the ledger, but `ground-rules.md` carries no such
caveat, so the list reads as complete. Enumerating four topics bought a rule that needs
re-verification every time Senzing adds a topic; the sweep found it stale after one pass.

## Proposed change

Replace the enumeration with an unconditional rule that needs no maintenance.

1. **`ground-rules.md:100`** — every `reporting_guide` call passes
   `language='<chosen_language>'`, whatever the topic. Drop the which-topics-gate list.
   Passing it where the topic does not gate is harmless — on `topic='quality'` it only
   adds `sdk_patterns`, which is strictly more content — so the rule costs nothing and
   cannot go stale. Keep the two things that are *not* per-topic facts: that a
   `needs_input` response is a **gate, not an answer**, and that some topics gate a second
   time on a further parameter (`data_mart` on `scale`), so the rule is "satisfy every
   gate the response asks for", not "pass language once and assume content".
2. **`tests/test_mcp_call_contracts.py`** — replace `GATING_TOPICS` with a scan of **every**
   `reporting_guide(topic=…)` call, asserting each carries `language`. Removing the topic
   list removes the thing that goes out of date. Keep the not-vacuous guard.
3. **Add `language='<chosen_language>'` to the two bare `topic='quality'` calls**
   (`module-06-data-processing/phaseD-validation.md:199` and `:87`). The previous spec
   deliberately left these alone because `quality` does not gate, which was right under
   the enumerate-the-gating-topics rule and is wrong under this one: a blanket rule with
   two documented exceptions is not a blanket rule, and the next reader cannot tell an
   intentional omission from an oversight.

**Not in scope, and now demoted from "unknown" to "moot":** `topic='reports'`,
`topic='dashboard'` and `topic='export'` were listed as unprobed by the previous spec. The
plugin does not call any of them (`grep` over `plugins/senzing-bootcamp/skills/` returns
no call site), so whether they gate cannot affect the bootcamp, and the blanket rule
covers them if one is ever added. They are recorded as not-called rather than left as an
open risk.

## Acceptance criteria

- [ ] `ground-rules.md` states the unconditional rule and no longer enumerates which
      topics gate; the gate-not-an-answer rule and the second-gate warning (`data_mart` →
      `scale`) both survive.
- [ ] Every `reporting_guide(topic=…)` call in `plugins/senzing-bootcamp/skills/` passes
      `language`, including the two `topic='quality'` calls.
- [ ] The guard in `tests/test_mcp_call_contracts.py` scans **all** `reporting_guide`
      calls with no topic allowlist, and its not-vacuous check still fails if the glob
      drifts. Mutation-test it by reverting one call site.
- [ ] **Re-verification clause:** implementing this requires
      `reporting_guide(topic='entity_views')` to still return `needs_input` with empty
      payload sections. If it no longer gates, the specific claim is stale but the
      unconditional rule still stands on `evaluation` / `graph` / `data_mart` — re-verify
      those before weakening anything.
- [ ] INV-192 is satisfied rather than merely cited: no shipped text names a subset of
      gating inputs as though it were the whole set.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the rule at ~line 100.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — lines 87, 199 (`topic='quality'`).
- `tests/test_mcp_call_contracts.py` — `TestGatingTopicsAlwaysPassLanguage`.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-07-30 (sixth pass — both server axes unchanged, so
  the run covered un-ledgered sites only), ledger key `reporting-guide-entity-views-gates`
- Verdict: `contradicted` — shipped guidance enumerates a subset as though complete.
- MCP evidence: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, 2026-07-30 —
  `reporting_guide(topic='entity_views')` returned `needs_input` on `language` with every
  payload section empty. Quoted above.
- Priority: Medium — no call site is wrong today; the guard and the guidance are, so the
  next one will be and nothing will catch it.
- Upstream: not applicable. (A schema marking `language` required for the gating topics
  would remove the class entirely — worth raising if it recurs.)
- Related specs: `specs/reporting-guide-topics-gate-on-language.md` (this corrects the
  enumeration that spec introduced; its six call-site fixes stand).
