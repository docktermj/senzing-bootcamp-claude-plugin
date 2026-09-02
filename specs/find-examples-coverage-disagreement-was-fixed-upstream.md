# find_examples' coverage disagreement was fixed upstream and four sites still assert it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-280 and three shipped/test sites assert, in the present tense, that
`find_examples`' **declared description disagrees with `get_capabilities`** about what the
index covers — that the declared half "omits TypeScript and JavaScript from both the
language list and the indexed file extensions, and gives a lower repository count."

On **MCP server 1.36.0** that is false on all three counts. The plugin reported the
discrepancy upstream on 2026-08-27 (recorded at
`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md:375`) and
**the server acted on it.** The two sources now agree.

The consequence is not cosmetic. The `⛔` rule the plugin derives from the discrepancy —
*"Do not quote a repository count anywhere in this plugin — the two sources give different
numbers, so no count is citeable"* — now states a **false reason** for a rule that is still
worth keeping, and the guard enforcing it repeats that false reason in its own failure
message. Per `.claude/skills/dry-run/phase1-mcp-contracts.md`, that is the shape where "the
failure messages told the fixer the opposite of what the server said."

## Root cause

A dated cross-source *disagreement* claim, with no mechanism to notice it being resolved.

`coverage_reports.py negatives` cannot see this claim: it scans for "this MCP tool does
**not** contain X" phrasing, and this is a *two-sources-disagree* claim. `unmarked` cannot
see it either — both sites carry scan markers (`SEARCH-DOCS-CATEGORY-PROSE`,
`COVERAGE-FIGURE-SCAN: quoted-history`), so they read as already-managed. So the claim ages
exactly like a dated negative while sitting outside both reports that exist to re-ask them.

What the live server returns, read from the tool manifest via
`ToolSearch("select:mcp__senzing__find_examples")` and from `get_capabilities`, both on
**server 1.36.0, 2026-09-02**:

| Claim | `find_examples` declared description (1.36.0) | `get_capabilities` (1.36.0) | Agree? |
|---|---|---|---|
| repository count | "42 indexed Senzing GitHub repositories" | "42 GitHub repositories" | ✅ yes |
| indexed extensions | "(.py, .java, .cs, .rs, .ts, .js)" | "(.py, .java, .cs, .rs, .ts, .js)" | ✅ yes |
| languages | "Python, Java, C# (official SDKs) plus Rust and TypeScript/Node.js (community-maintained wrappers, not official)" | "Python, Java, and C# (the official Senzing SDKs) plus Rust and TypeScript/Node.js (community-maintained wrappers, not official Senzing SDKs)" | ✅ yes |

The four sites resting on the expired premise:

1. `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md:368-378`
   — the ⚠️ note asserting the declared half is stale, and the ⛔ no-count rule whose stated
   reason is "the two sources give different numbers".
2. `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:313-316` — the
   `COVERAGE-FIGURE-SCAN: quoted-history` block, dated "server **1.33.0**, 2026-08-28",
   quoting a declared description that no longer reads that way.
3. `specs/INVARIANTS.md:339` — INV-280. Its example clause is correctly scoped to "On server
   1.33.0", so it is a dated historical example rather than a false present-tense claim, but
   a reader checking its live premise finds it does not reproduce.
4. `tests/test_find_examples_coverage_is_uncitable.py:101-103` and `:107-113` — both failure
   messages state the expired premise ("The server gives two different numbers"; "which is
   the declared description's stale list").

⚠️ **INV-280's general rule is still correct and should not be weakened** — and a *live*
instance of it was found in the same sweep, which is what should replace the resolved
example: `search_docs`' declared description says the corpus is "~2175 chunks", while a live
`search_docs` response on **1.36.0, 2026-09-02** reports
`"metadata": {"documents_indexed": 14637, "index_built": "2026-09-02 14:17 UTC"}`. Declared
coverage prose still goes stale; only this particular pair stopped disagreeing.

## Proposed change

Rescope rather than delete — the rule survives, its premise changed.

1. **`phaseA-build-loading.md:368-378`** — rewrite the ⚠️ note in the past tense as a
   resolved upstream report ("reported 2026-08-27; the server aligned the two by 1.36.0,
   verified 2026-09-02"), and **re-base the ⛔ no-count rule on volatility rather than on
   disagreement**: a repository count is a server-side figure that changes as repos are
   indexed, so quoting it in shipped guidance goes stale whether or not the two sources
   currently agree. Keep the prohibition.
2. **`ground-rules.md:313-316`** — keep INV-280's general rule verbatim; replace the
   `quoted-history` example with the live `search_docs` "~2175 chunks" vs
   `documents_indexed: 14637` pair, dated to 1.36.0/2026-09-02, so the invariant is
   illustrated by a disagreement that currently exists.
3. **`specs/INVARIANTS.md:339`** — add a dated correction note recording that the
   `find_examples` example was **resolved upstream at server 1.36.0 (verified 2026-09-02)**
   and naming the `search_docs` pair as the live example. Do not retire INV-280; its rule is
   independent of which pair illustrates it.
4. **`tests/test_find_examples_coverage_is_uncitable.py`** — keep both assertions; rewrite
   the two failure messages to give the surviving reason (a coverage figure is volatile
   server-side state, so no count is citeable) instead of the expired one. Per the dry-run
   rule, invert or rescope a guard rather than deleting it — here the assertions are
   unchanged and only their explanations are wrong.

## Acceptance criteria

- [ ] No shipped file asserts, in the present tense, that `find_examples`' declared
      description disagrees with `get_capabilities` about count, extensions, or languages.
- [ ] The ⛔ no-repository-count rule survives in `phaseA-build-loading.md` and its stated
      reason is coverage-figure volatility, not the resolved disagreement.
- [ ] `tests/test_find_examples_coverage_is_uncitable.py` still fails when a shipped file
      states a repository count or enumerates extensions ending at `.rs`, and both failure
      messages name the volatility reason rather than "two different numbers".
- [ ] INV-280 carries a dated correction note naming server 1.36.0 / 2026-09-02 and the
      `search_docs` `documents_indexed` pair as its live example, and the invariant itself is
      not retired.
- [ ] A test asserts that INV-280's live illustrating example is a pair that currently
      disagrees — so the next resolution is noticed rather than silently carried forward.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — retire the disagreement claim, re-base the no-count rule on volatility
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — swap the expired example for the live `search_docs` one
- `specs/INVARIANTS.md` — dated correction note on INV-280
- `tests/test_find_examples_coverage_is_uncitable.py` — rewrite both failure messages, keep both assertions

## Source

- Feedback: `/dry-run` phase 1, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **server 1.36.0, 2026-09-02 — server no longer contradicts itself; the plugin's claim is now stale.** Tools called: `get_capabilities`; `find_examples`' declared description read from the tool manifest via `ToolSearch`; `search_docs(query='SzError BadInput already existing record error contract', category='sdk', max_results=2)` for the live `documents_indexed` figure. Not an absence claim — the finding is that two texts now AGREE, which is read directly from both.
- Upstream: not applicable — the upstream report was already sent 2026-08-27 and this spec records that it was **acted on**.
- Related specs: `specs/find-examples-self-describes-two-different-coverages.md` (the 2026-08-28 spec this supersedes the premise of)

