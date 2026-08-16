# Module 7 Step 3b's quality lookup returns vendor-selection guidance, and the step omits the server's evidence requirement

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two defects in one step, found together. The second is the serious one.

### 1. The supplementary lookup returns the wrong kind of "evaluation"

`module-07-query-visualize-discover/phase1-query-visualize.md:283-285`:

> Call `reporting_guide(topic='quality', language='<chosen_language>', version='current')` for
> the quality-evaluation methodology, then `search_docs(query='entity resolution quality
> evaluation', version='current')` for additional context on interpreting results.

The first call is correct. The second returns material about evaluating an ER **vendor**, not about
interpreting ER **output**. Run live on **MCP server 1.32.9, docs index 2026-08-11 20:52 UTC,
2026-08-12**, `search_docs(query='entity resolution quality evaluation')` returns as its top hit
*Entity Resolution Buyer's Guide* → **"The Steps To Evaluating Entity Resolution"** (relevance 67.9):
a nine-step purchasing guide covering deployment method, full-stack vs API, cloud vs on-prem, total
cost of ownership, and a side-by-side comparison checklist.

BM25 matched "evaluation" in the procurement sense. A guide relaying that as "additional context on
interpreting results" presents purchase-evaluation criteria to a Bootcamper who asked whether their
entities resolved correctly.

**The tool that owns the material is one call away and the step never makes it.**
`reporting_guide(topic='evaluation', language='python')` — same server, same date — returns the
**4-Point ER Evaluation Framework** (sanity check, over-matching, under-matching, match principles),
the `MATCH_LEVEL_CODE` reference (`POSSIBLY_SAME`, `POSSIBLY_RELATED`, `DISCLOSED_RELATION`), the
export-iteration stats methodology, and three evaluation anti-patterns. The tool's own contract
distinguishes the two topics explicitly: `quality` is "precision/recall/F1, split/merge detection,
review queues, sampling strategies"; `evaluation` is the "4-point ER evaluation framework with
evidence requirements".

### 2. The step's own "Acceptable" script is the server's canonical example of a bad assessment

`reporting_guide(topic='evaluation')` carries a section titled **Evidence Requirement for ER
Evaluation**, described as the hallucination-prevention mechanism. Verbatim (1.32.9, 2026-08-12):

> CRITICAL: Every evaluation finding MUST be supported by specific evidence — actual records, entity
> IDs, and data values. … An LLM can easily generate plausible-sounding evaluation narratives without
> actually examining the data. … **Bad:** *"The resolution quality looks good with reasonable
> compression rates."*

`phase1-query-visualize.md:304` prescribes, verbatim, the line the guide is to say:

> - **Acceptable:** "Your entity resolution quality looks good. Let's proceed to visualizations."

That is the server's **Bad** example almost word for word, and it is the branch that **ends the
quality gate and proceeds**. The step reaches it from a summary table of three aggregate indicators
(`:289-293` — entity-to-record ratio, possible matches, cross-source match rate), which the same
response names as an anti-pattern in its own right:

> **Pattern:** Evaluating ER quality without reviewing sample entities.
> **Correct:** Never assess ER quality from aggregate statistics alone. Always retrieve and show
> specific records from multi-record entities, possible match pairs, and large entities. The evidence
> requirement prevents hallucinated evaluations.

Of the three verdict branches, only **Marginal** shows the Bootcamper any records (`:305-306`).
**Acceptable** proceeds on a bare qualitative claim, and **Poor** presents recommendations. So the
one path that certifies the load as good is the one with no evidence behind it — which is precisely
the failure the server's framework exists to prevent, in the module whose output the Bootcamper
carries into graduation.

**Severity: medium-high.** Nothing crashes. The cost is a quality verdict a Bootcamper is invited to
trust, produced in the shape the authoritative source calls unreliable, plus a supplementary lookup
that can put procurement advice into an engineering explanation.

## Root cause

Two independent gaps, both from the same habit of composing a query instead of routing to the tool.

1. **The `search_docs` call was composed, not executed.** It is the same class as
   `step14-value-proposition-query-is-bm25-hostile-with-no-fallback`: an abstract phrase assembled
   from the topic name rather than a phrasing that was run and inspected. Step 3b also carries no
   re-query rule, so an off-topic result has no recovery path — the discipline
   `module-00-entity-resolution-concepts/concepts.md:29-43` states and Step 3b never inherited.
2. **The evidence requirement lives in the tool response, and the step summarises the response
   instead of relaying it.** Step 3b tells the guide to *call* `reporting_guide(topic='quality')` and
   then supplies its own verdict bands and scripts. Those scripts were written independently of what
   the tool returns, so nothing carried the Evidence Requirement across — and `topic='evaluation'`,
   where it lives, is never called at all.

Nothing in the suite could catch either: both need the network, and the Acceptable script is
well-formed prose that no offline check has reason to question.

## Proposed change

1. **Replace the supplementary `search_docs` call with `reporting_guide(topic='evaluation',
   language='<chosen_language>')`.** Same position in the step, same purpose ("additional context on
   interpreting results"), the tool that owns the fact. Do not keep the `search_docs` call as a
   fallback — a second, worse source for material the first call already carries is how the wrong
   one gets quoted.
2. **Relay the Evidence Requirement into the verdict bands.** Every branch, including **Acceptable**,
   must cite specific entity IDs and show actual records before stating a verdict. Replace `:304`'s
   script with one that does: name the entities examined, show what merged and on which match key,
   then give the assessment. Keep the bands' thresholds as they are — they are not what is wrong.
3. **Carry the aggregate-statistics anti-pattern beside the indicator table**, with its provenance,
   so the table is read as the *entry point* to evidence review rather than as the assessment.
4. **Add the re-query/fallback rule** to Step 3b, deferring to `concepts.md` rather than restating
   it, for the same reason Step 14 needed it.
5. **Guard it.** Assert that Step 3b routes quality-interpretation to `reporting_guide` and not to a
   documentation search; that no verdict branch presents a bare qualitative statement without an
   evidence instruction; and that the anti-pattern and its provenance are present. Remove the
   `entity resolution quality evaluation` row from `tests/test_prescribed_search_queries.py`'s
   allowlist — that entry exists only to record this defect, and its own note says so.

**Re-verify before implementing (INV-080).** Call `reporting_guide(topic='evaluation')` and quote
what it returns then. If the Evidence Requirement has been reworded or moved, relay the current text.

## Acceptance criteria

- [ ] Step 3b no longer calls `search_docs` for quality context; it calls
      `reporting_guide(topic='evaluation', language=…)`, and the shipped text carries the server
      version and date of the call that established it.
- [ ] Every verdict branch — **Acceptable**, **Marginal** and **Poor** — requires specific entity IDs
      and actual record data before its statement. No branch ships a bare qualitative verdict; the
      `:304` "looks good" script in particular is gone.
- [ ] The "never assess ER quality from aggregate statistics alone" anti-pattern is relayed beside
      the indicator table with its provenance (tool, parameters, server version, date).
- [ ] Step 3b carries a re-query instruction for an empty or off-topic result, deferring to
      `concepts.md` for the reasoning rather than restating it.
- [ ] `tests/test_prescribed_search_queries.py` no longer lists `entity resolution quality
      evaluation`, and its guard still passes with the remaining seven prescribed queries.
- [ ] A test asserts the routing, the evidence requirement in every branch, and the anti-pattern
      relay. Negative-controlled: restoring the `search_docs` call, or restoring the bare
      "looks good" script, fails the suite — with each mutation verified to land.
- [ ] The quality **thresholds** are unchanged (`< 5%`, `5–15%`, `> 15%`) — this spec changes what
      the guide must show, not where the bands sit. Confirm by `git diff`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      `reporting_guide` call passes the Bootcamper's chosen language, and the rest is prose.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  Step 3b (`:281-308`): the lookup at `:283-285`, the indicator table at `:287-293`, and the verdict
  scripts at `:302-308`.
- `tests/test_prescribed_search_queries.py` — drop the allowlist row.
- `tests/` — the new guard.

## Source

- Implementation run: `implement-spec`, 2026-08-12, while verifying the eight prescribed
  `search_docs` literals for `step14-value-proposition-query-is-bm25-hostile-with-no-fallback`
  (`Source: self-observed (assistant retrospective)`). Found by executing the query rather than
  reading it; defect 2 was found by then reading what the correct tool returns and noticing the
  plugin's script inside it, as the example of what not to say.
- Priority: **Medium-high.** Defect 1 is a wrong-material lookup on a documented path. Defect 2 puts
  a Bootcamper-facing quality verdict in the shape the authoritative source calls unreliable, on the
  branch that proceeds.
- MCP re-check: **server 1.32.9, docs index 2026-08-11 20:52 UTC, 2026-08-12 — still reproduces, and
  the server supplies the fix.** Tools called: `search_docs(query='entity resolution quality
  evaluation', max_results=1)` → *Entity Resolution Buyer's Guide* → "The Steps To Evaluating Entity
  Resolution"; `reporting_guide(topic='evaluation', language='python')` → 4-Point ER Evaluation
  Framework, Evidence Requirement, `MATCH_LEVEL_CODE` reference, three evaluation anti-patterns.
- Upstream: **not applicable.** The server is correct and more complete than the plugin; the plugin
  is the stale party. Nothing to file.
- Related specs: `specs/step14-value-proposition-query-is-bm25-hostile-with-no-fallback.md` (same
  composed-query class, and the guard whose allowlist recorded this finding);
  `specs/relay-the-default-flags-production-caution.md` (same "the server states it and the plugin
  never relays it" shape); `specs/module6-validation-routing-not-reports-sql.md` (same defect of
  routing to the wrong `reporting_guide` topic).

## Deviations from this spec, and why (2026-08-12)

Re-verified at implementation time on **server 1.32.9, docs index 2026-08-11 20:52 UTC**. Both
defects reproduce exactly as written, and the fix went in as designed. Four things differed.

1. **The aggregate-statistics anti-pattern is in BOTH topics, not just `evaluation` — which makes the
   finding worse than this spec says.** This spec attributes it to `topic='evaluation'` (*"Never
   assess ER quality from aggregate statistics alone"*). Calling `topic='quality'` at implementation
   time found the same warning there: *"Only checking aggregate statistics for quality → Aggregate
   stats (entity count, compression ratio) hide errors. Always sample and manually review specific
   entities — especially large entities, possible matches, and ambiguous matches. Use `why_entities`
   to understand individual resolution decisions."* Step 3b **already called that topic**. So the
   plugin was not missing the warning for want of asking — it fetched the response containing it and
   then shipped a script contradicting it. Both quotes are now relayed, attributed to their
   respective topics.

2. **The `quality` topic supplied concrete sampling criteria the spec did not name**, so the new
   sample-and-show instruction could be specific rather than exhortative: review queues are built
   from possible matches, ambiguous matches, large entities, and "review features" (an entity
   carrying two different DOBs or SSNs), and `why_entities` is the call for investigating a flagged
   pair. Those are in the shipped text.

3. **The allowlist row was commented out, not deleted.** Criterion 5 says the row should no longer be
   listed, and it is not — but the phrasing is retained as a comment in
   `tests/test_prescribed_search_queries.py` recording that it was OFF TARGET, when, and what
   replaced it. A deleted row is an invitation to reintroduce the query; the guard's active set is
   unchanged either way, and its dead-entry check still passes.

4. **INV-192 caught the provenance citation.** The Evidence Requirement quote initially cited
   `reporting_guide(topic='evaluation')` with no `language`, which `test_mcp_call_contracts.py`
   rejects — correctly, since most topics withhold content without it. Fixed by citing the call that
   was actually made, `language='python'`. Worth recording because the citation is provenance rather
   than an instruction, and the guard is right anyway: a provenance stamp that names parameters the
   caller did not pass is not reproducible.

Also of note for the guard: its first form asserted the bad query string was **absent** from Step 3b,
and failed against correct shipped text — the ⛔ has to name the query in order to forbid it. It now
requires every occurrence to sit inside a prohibition, the same prescription-versus-prohibition
distinction `tests/test_mcp_output_is_never_suppressed.py` had to make.
