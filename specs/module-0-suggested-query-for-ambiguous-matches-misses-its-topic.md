# Module 0's suggested query for ambiguous matches does not reach the ambiguous-match material

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`concepts.md` ships six suggested `search_docs` queries and vouches for all of them as a set:

> The list above is not decoration: `search_docs` is BM25, so phrasing decides what comes back,
> and **these are phrased the way the indexed documentation is**.

One of the six is not. `search_docs(query='entity resolution ambiguous match possible match')`
returns **none** of the ambiguous-match material. On MCP server **1.35.1**, docs index
**2026-08-29 16:10 UTC**, 2026-08-31, all three hits are chunks of
*"Entity Centric Learning vs. Record Matching Methods in Entity Resolution Systems"* — relevant
primer material, but silent on ambiguous matches, possible matches and invisible false positives.

This is precisely the failure shape the same file warns about two paragraphs above: a query that
misses is indistinguishable from documentation that does not cover the topic, and the honest-seeming
conclusion ("the docs are silent") either leaves the guide with nothing to say under the MCP-only
rule or makes a training-data fallback feel justified.

The blast radius is narrow but real. The primer's own *failure modes* bullet routes correctly —
it cites the **false-positives** query for this material, and that query does work — so a guide
teaching the primer top-to-bottom lands on the right page. The exposure is the **follow-up path**:
Module 0's "any questions" gate, its knowledge check, and its exploration gate all route
bootcamper questions through `search_docs`, and a bootcamper asking about ambiguous matches
invites the guide to pick the suggested query with "ambiguous match" in its wording.

## Root cause

`plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md:20` lists
`"entity resolution ambiguous match possible match"` among the suggested queries. The material it
is evidently meant to reach lives in *"What Is Entity Resolution? How It Works & Why It Matters."*
→ section **"What Are Ambiguous Matches and Invisible False Positives?"**, and that section's own
vocabulary is *"ambiguous matches"*, *"invisible false positive"*, *"arbitrarily assign"*,
*"possible match"* — but under BM25 the composed phrase loses to the Entity-Centric-Learning
chunks, which carry a denser concentration of `entity`/`resolution`/`match`.

The file's stated criterion for the list is that each query is "phrased the way the indexed
documentation is". Measured against that criterion this entry fails: the documentation's own
phrasing is the section title, and the section title reaches it decisively.

Measured on server **1.35.1**, index **2026-08-29 16:10 UTC**, 2026-08-31:

| Query | Reaches the ambiguous-match section? | Evidence |
|---|---|---|
| `entity resolution ambiguous match possible match` (shipped) | **No** | 3/3 hits are Entity Centric Learning chunks |
| `entity resolution false positives false negatives accuracy` (shipped) | Yes, at **rank 2** | rank 1 is a Verisk case study, as the file already documents |
| `What Are Ambiguous Matches and Invisible False Positives` | Yes, at **rank 1**, score 139.6 | the section's own title |

## Proposed change

1. Replace the suggested query at `concepts.md:20` with wording taken from the documentation's own
   section title — `"ambiguous matches invisible false positives"` — and re-verify it reaches the
   section before shipping. Keep the entry in the list; the topic belongs there, only the phrasing
   is wrong.
2. Add a one-line note beside the list recording that the entries are **measured**, not composed,
   with the server version and index date the measurement was taken on — so the next editor knows
   the list is a verified artifact rather than a plausible-looking set of phrases, and knows what
   to re-run.

⚠️ Do not "fix" this by adding a rule telling the guide to try harder. The ⛔ re-query rule already
present in this file is correct and is what limits the damage; the defect is that a query the file
vouches for is one the file's own criterion rejects.

## Acceptance criteria

- [ ] `search_docs` with the shipped ambiguous-match query returns the *"What Are Ambiguous Matches
      and Invisible False Positives?"* section within the top 3 results, verified live and recorded
      with server version and index date.
- [ ] The suggested-query list carries a dated note stating the entries were measured against a
      named server version and index date.
- [ ] The failure-modes bullet's existing cross-reference to the false-positives query still
      resolves — the fix must not silently re-route material that is already correctly routed.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — line 20:
  replace the ambiguous-match suggested query; add the dated measurement note beside the list.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Entity Resolution Concepts
  (`Source: self-observed (assistant retrospective)`) — found while sourcing a knowledge-check
  question, by using the shipped query and getting no ambiguous-match material back.
- Priority: Low
- MCP re-check: server **1.35.1**, docs index **2026-08-29 16:10 UTC**, 2026-08-31 — reproduces.
  `search_docs(query='entity resolution ambiguous match possible match', max_results=3)` returns
  three Entity-Centric-Learning chunks and no ambiguous-match content.
  owner-checked: `search_docs(query='What Are Ambiguous Matches and Invisible False Positives', max_results=3)`
  — returns the section at rank 1 (relevance 139.6), so the material is present and indexed; this is a
  query-phrasing defect, not a documentation gap.
- Upstream: not applicable — the defect is in the plugin's shipped query wording, not in the server.
- Related specs: none

## Deviations from this spec, and why (2026-09-01)

**A second entry in the same list was also wrong, and the spec did not know.** Criterion 2 asks the
list to carry a note stating *"the entries were measured"*. Shipping that claim having measured only
the entry this spec names would have been the very defect being fixed — a plausible statement with
one measurement behind it. So all six were run against server 1.35.3, docs index 2026-09-01 11:58
UTC, and:

| Query | Reaches its material? | What came back |
|---|---|---|
| `Senzing principle-based entity resolution approach` | Yes, rank 1 (138.8) | *What is Principle Based Entity Resolution?* |
| `entity resolution relationships disclosed discovered` | Yes, rank 1 (69.0) | *How Does Relationship Awareness Improve Entity Resolution?* |
| `entity resolution ambiguous match possible match` | **No** | 3/3 Entity-Centric-Learning chunks |
| `Senzing differentiators real-time explainability attribution` | Yes, rank 1 (103.3) | *Senzing Explainability* |
| `entity resolution pipeline standardization blocking scoring clustering` | **No** | rank 1 a customer case study, rank 2 the MCP server's own page |
| `entity resolution false positives false negatives accuracy` | Yes, rank 2 (66.6) | as the file already documents — rank 1 is a case study |

The pipeline entry names five real pipeline stages and reaches none of them. It is replaced with
`How does entity resolution work steps process`, which returns the *"How Does Entity Resolution
Work?"* section — the numbered pipeline itself — at **rank 1** (108.7). Both misses are recorded in
the shipped note **with what they actually returned**, so a later editor cannot restore them by feel.

⚠️ **Neither miss was findable by reading.** Both are well-formed, on-topic, and use the right
technical vocabulary. That is the point: under BM25 the words in a query are not evidence about what
it returns, so "review the list" is exactly the check that had already passed twice.

**An existing guard had pinned the wrong premise, and it is worth naming.**
`tests/test_concepts_teaching_section_claims_no_exemption.py` asserted that a pipeline query exists
by matching the literal terms `pipeline`, `blocking`, `clustering` in the query text. It therefore
certified a query it had never seen work, on the strength of the words the query contained — the
reasoning BM25 defeats. It now pins the **measured result** instead: `concepts.md` must record which
entry reaches the pipeline section, and that entry must be present in the list. Negative-controlled
both ways. Nothing was relaxed; the new form is strictly harder to satisfy than a term match.
