# Module 3's connectivity probe still uses `search_docs`, which onboarding deprecated for exactly this purpose

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The onboarding preface reasoned its way off `search_docs` as a liveness probe and wrote the reasoning
down. Module 3's Step 1 does the thing that reasoning rejects.

**`bootcamp-onboarding/onboarding-flow.md:42-48`** — the MCP health check:

> **Probe:** call `get_capabilities` (about a 10-second timeout). This is the call `ground-rules.md`
> → "Session start" already requires once before any other Senzing MCP call, so it doubles as the
> reachability probe and the preface makes **one** MCP call here, not two.
>   - Do **not** probe with `search_docs`. It was specified here as "a lightweight call such as
>     `search_docs(query="health check")`", which it is not: that query returns a multi-page FAQ
>     article (~5 KB) for a question that only needed "did the server answer at all".

**`module-03-system-verification/phase1-verification.md:77-83`** — Step 1, MCP Connectivity Check:

> 1. Call `search_docs(query="Senzing SDK initialization")` with a 10-second timeout.
> 2. **If a response is received** (including empty results): MCP connectivity confirmed. Proceed
>    silently; do not display connectivity status to the bootcamper.

Same job — "did the server answer at all" — and the step is explicit that the *content* is
irrelevant, since empty results count as success. So it pays for a document search to learn a
boolean.

**Run live, server 1.32.9, 2026-08-12:** `search_docs(query='Senzing SDK initialization')` returns a
**TypeScript tRPC client** source file from `brianmacy/sz-napi` as its top hit — a code example whose
excerpt is truncated at 500 of 2,569 characters. The probe works (a response arrived), and the result
is unrelated to SDK initialization. That is fine for a liveness check and is exactly why it should not
be a document search: the retrieval quality is irrelevant, so the retrieval cost is pure waste. The
step also specifies no `max_results`, so the default page size applies.

**Why this is worth fixing rather than shrugging at.** Three reasons, in increasing order:

1. **Cost.** It is a needless multi-kilobyte response on a step whose output is discarded.
2. **Consistency.** The plugin now says two different things about how to probe the server, and one
   of them carries a ⛔ and a worked explanation of why the other is wrong.
3. **It is the same non-propagation pattern as two other findings from this run.** `concepts.md`'s
   re-query discipline never reached Module 1 Step 14
   (`specs/step14-value-proposition-query-is-bm25-hostile-with-no-fallback.md`), and
   `ground-rules.md`'s model-nudge trigger was summarised wrongly in Bootcamp preparation
   (`specs/preparation-summarises-the-model-nudge-trigger-as-the-forbidden-comparison.md`). A lesson
   learned in one module and not carried across skill boundaries is this plugin's recurring defect
   shape, and this is the third instance found in a single walk.

**Not a live defect.** Nothing fails, the Bootcamper sees nothing (the step is silent on success), and
connectivity is genuinely confirmed. This is waste plus a self-contradiction, not a break.

## Root cause

The `search_docs` probe predates the onboarding fix. `onboarding-flow.md`'s note is written in the
first person of that file — *"It was specified **here** as…"* — so the correction was scoped to the
preface's own line rather than searched for elsewhere. Nothing greps the plugin for other liveness
probes, and no invariant states which tool a reachability check must use, so Module 3's copy was never
implicated.

`get_capabilities` is also the natural replacement and was already the right answer at the time: the
session-start rule requires it once before any other Senzing MCP call, so by the time Module 3 runs it
has been called — which is precisely the argument the preface makes for itself.

## Proposed change

1. **Replace Step 1's probe with `get_capabilities`**, matching `onboarding-flow.md:42-45`, and keep
   everything else about the step (10-second timeout, retry once, the troubleshooting block, the
   silent-on-success rule, the `mcp_connectivity` checkpoint) exactly as it is. The step's contract is
   unchanged; only the call changes.
2. **Carry a one-line reason inline**, so the next editor does not "helpfully" restore a
   documentation search: a liveness probe must not be a document search, because the content is
   discarded — cite `onboarding-flow.md`'s note rather than restating it.
3. **Sweep for other instances.** Grep the plugin for any remaining reachability/liveness probe that
   calls `search_docs`, and fix any others found in the same change. The value of this spec is mostly
   in the sweep; a single-site fix leaves the pattern intact.
4. **Consider registering the rule.** A one-line invariant — *a reachability probe MUST use
   `get_capabilities`, never a content-returning tool* — would make this testable and stop the fourth
   instance. Offer it to the maintainer rather than assuming it; it may be too small to warrant an ID.

## Acceptance criteria

- [ ] Module 3 Step 1 probes with `get_capabilities`; no shipped step uses `search_docs` (or another
      content-returning tool) purely to test reachability.
- [ ] Step 1's timeout, single retry, troubleshooting list, silent-on-success behaviour and
      `mcp_connectivity` checkpoint are unchanged (`git diff` confined to the call and a reason line).
- [ ] A test asserts no shipped file pairs a liveness/connectivity/reachability probe with
      `search_docs`. Negative-controlled: restoring the `search_docs` probe fails the suite, with the
      mutation verified to land.
- [ ] `onboarding-flow.md:42-48` is unchanged — it is the correct model this spec propagates.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      documentation and a text assertion only.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — Step 1
  (`:77-83`).
- `tests/` — the guard.
- Any further site the Step 3 sweep turns up.

## Source

- Dry run: `dry-run` phase 3, extended into System verification at the maintainer's request,
  2026-08-12 (`Source: self-observed (assistant retrospective)`). Found by *running* Step 1's
  prescribed call and noticing the top hit was an unrelated TypeScript file — which prompted checking
  what the preface says about probing with `search_docs`.
- Priority: **Low.** Waste and a self-contradiction; nothing breaks and no Bootcamper sees it. Raised
  slightly by being the third cross-module non-propagation found in one walk.
- MCP re-check: **still reproduces** — probe run live on 1.32.9 today; response received (so the step
  passes), top result unrelated to the query.
- Upstream: not applicable — BM25 returned reasonable lexical matches; the plugin chose to use a
  search as a boolean.
- Related specs: `specs/step14-value-proposition-query-is-bm25-hostile-with-no-fallback.md` and
  `specs/preparation-summarises-the-model-nudge-trigger-as-the-forbidden-comparison.md` — the same
  lesson-not-propagated shape, both from this run.
