# CORD is presented to the Bootcamper as "real-world-like" while the server says it is REAL data

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`get_sample_data`'s own tool contract carries a mandatory disclosure:

> **IMPORTANT: This is REAL data (not synthetic) — historical snapshots for evaluation only, not
> operational use. Always inform the user of this.**

The plugin never discharges it. Worse, the one place it characterizes CORD to the Bootcamper says
the opposite. `module-04-data-collection/SKILL.md:390` ships this pinned quote:

> "Senzing provides **CORD (Collections Of Relatable Data)**: curated, **real-world-like** datasets
> designed specifically for entity resolution evaluation."

"real-world-like" reads as *synthesized to resemble real data*. A Bootcamper told that will
reasonably conclude the records are fabricated. They are not. On MCP server **1.35.1**, 2026-08-31,
`get_sample_data(dataset='las-vegas', source='list')` returns **642,046 records across 11 sources** —
Equifax, the NPI provider registry, PPP loan recipients, ICIJ, Open Ownership, GLEIF, US Labor
Violations — that is real credit, healthcare-provider, federal-loan, beneficial-ownership and
labor-enforcement data about real named people and organizations.

A grep of every shipped Markdown file finds **no** occurrence of "evaluation only", "not
operational", "historical snapshot", or any equivalent of the tool's disclaimer.

Why this is more than a wording nit, in this plugin specifically:

1. The Bootcamper **loads these records into a local datastore** in Data processing and **queries
   named entities** in Query, Visualize and Discover.
2. Module 7's visualization renders entity names, and the module-completion screenshot flow
   **embeds those images into `docs/bootcamp_recap.md`**, which graduation renders into a keepsake
   PDF the Bootcamper is explicitly encouraged to **share with their team**. Real individuals'
   names can therefore reach a shared artifact from a dataset the Bootcamper was told was
   "real-world-like".
3. The plugin is otherwise scrupulous about this class of thing — `ground-rules.md` carries a
   whole ⛔ on stripping identifying details from upstream reports (INV-065), and Module 1 Step 1
   opens with a data-privacy reminder. The CORD path is the gap in an otherwise consistent posture.

## Root cause

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:389-397` composes its own
description of CORD rather than relaying the tool's. The surrounding guidance is careful about
*other* parts of the same contract — the very next paragraph (line 399) correctly requires
"Present the fetch URL from the response exactly as the tool gives it", and distinguishes
`download_url` from `source_download_url` in detail — so the omission is specific to the
data-provenance disclaimer, not a general disregard for the tool's contract.

`module-01-business-problem/phase1-discovery.md` Step 4b, which is where a generated scenario is
first *bound* to a CORD collection, likewise says nothing about it. Step 4b instructs
"Present values exactly as returned" for dataset names, sources and counts, but the disclaimer is
not a value in the payload — it lives in the tool's description — so a guide following Step 4b to
the letter never surfaces it.

## Proposed change

1. Replace "curated, real-world-like" at `module-04-data-collection/SKILL.md:390` with wording that
   states what the data is. Suggested: *"curated collections of **real** public and commercial
   records, assembled specifically for entity resolution evaluation"*.
2. Add the tool's disclosure to that same quoted block, as a Bootcamper-facing statement (never a
   👉 question — it needs no answer, and INV-012 forbids output they cannot act on): the data is
   real, it is a historical snapshot, and it is for evaluation rather than operational use.
3. Add a one-line pointer at `phase1-discovery.md` Step 4b's `cord` branch requiring the same
   disclosure at the point the scenario is bound to a CORD collection — that is the first moment the
   Bootcamper's scenario becomes real-people data, and it is several modules before Module 4's text
   would otherwise reach them.
4. Do **not** route this through a consent gate. The Bootcamper has already chosen sample data; this
   is a disclosure obligation the tool places on its caller, and turning it into a question would add
   a gate the plugin's own question-economy rules argue against (INV-247/INV-012).

## Acceptance criteria

- [ ] No shipped file describes CORD as "real-world-like" or otherwise implies the records are
      synthetic.
- [ ] The Bootcamper-facing CORD text states that the data is real, is a historical snapshot, and is
      for evaluation rather than operational use — as a statement, not a 👉 question.
- [ ] The disclosure is present on **both** paths that reach CORD: Module 1 Step 4b's `cord` branch
      (generated scenario) and Module 4's sample-data option.
- [ ] The existing correct guidance at `module-04-data-collection/SKILL.md:399-410` — presenting the
      fetch URL exactly as returned, and distinguishing `download_url` from `source_download_url` —
      is unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — line 390: replace
  "real-world-like"; add the disclosure to the quoted block.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 4b: add the
  same disclosure to the `cord` branch.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Discover the Business Problem Step 4b
  (`Source: self-observed (assistant retrospective)`) — found while calling `get_sample_data` to
  decide CORD-vs-synthetic for a generated scenario, by reading the tool's contract alongside the
  plugin's description of the same data.
- Priority: Medium
- MCP re-check: server **1.35.1**, 2026-08-31 — the disclaimer is live in the `get_sample_data` tool
  description ("This is REAL data (not synthetic) — historical snapshots for evaluation only, not
  operational use. Always inform the user of this."), and `get_sample_data(dataset='las-vegas',
  source='list')` returns 642,046 records across the 11 named real-world sources.
  owner-checked: not required — this spec asserts the **plugin** omits something, not that the server
  lacks anything; the server demonstrably carries it, quoted above.
- Upstream: not applicable — the defect is the plugin's, and the server's contract is correct.
- Related specs: none

## Deviations from this spec, and why (2026-09-01)

**Three acquisition paths, not two (INV-246).** The spec's `## Affected files` names Module 4 and
Module 1 Step 4b. Scanning for CORD **acquisition** — recommending it, binding a scenario to it, or
offering it as a substitute — found a third: `module-03b-truthset-visualization/phase1-visualization.md`
offers a non-deterministic CORD collection when the Truth Set is unavailable, and reaches the data
**without passing through Module 4's wording at all**. It now carries the disclosure. The guard
derives its site set by that scan rather than from this list.

**No record counts were shipped.** The spec cites *"642,046 records across 11 sources"* and names the
providers. That is a census — the exact shape
`specs/mcp-negative-markers-carry-rationale-nothing-reverifies.md`, implemented immediately before
this one in the same run, exists to remove — and it would be re-verifiable only by re-running the
tool. The shipped text states what the data **is** (real public and commercial records, historical
snapshots, evaluation rather than operational use), which is the disclosure the tool actually
requires and which does not expire when a collection is refreshed.

**Re-verified against server 1.35.3, not the 1.35.1 the spec swept.** The obligation is unchanged and
still verbatim in the `get_sample_data` tool description.

⚠️ **`module-05-data-quality-mapping/phase1-quality-assessment.md` was deliberately excluded.** Its
👉 names a CORD source ("Your CORD source [SOURCE_NAME] is already in Senzing-loadable form…"), so a
word-level scan flags it, but it *consumes* data Module 4 acquired — the file says so outright — and
requiring the disclosure there would restate it to a Bootcamper who has had the files on disk for two
modules. It is pinned in the guard as a must-not-match so a later widening cannot quietly add it.
