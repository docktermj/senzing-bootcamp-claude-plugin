# Pattern gallery sector list misdescribes the cost table

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The design-pattern gallery step tells the guide which sectors the business-value
table quantifies, and its list does not match the table. One named item is not a
row at all, and the table's two largest-scope rows — including the single biggest
figure in it — are unnamed. A guide working from the plugin's list looks for a row
that is not there and never reaches the figure that fits the most common
bootcamper case.

## Root cause

`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:34-39`
states that the *"Estimated Annual Cost of Mismatched Identity Records"* table
"quantifies ten sectors, including Marketing/Sales/CRM, **Supply Chain &
Procurement**, **Insurance**, **Healthcare**, Government, Financial Services,
Retail, Telecommunications, and a sanctions & trade-compliance line."

Live check, `search_docs(query='total economic cost mismatched identity data by
sector')`, MCP server 1.32.9, docs indexed 2026-08-11 20:52 UTC, run 2026-08-13.
The document is `local://economic-cost-mismatched-identity-data.md` and the table
exists under that exact heading, so the citation is sound. Its rows are:

| Row | Est. annual cost | Midpoint |
|---|---|---|
| All Sectors: Cross-Industry Data Quality | $129B – $421B | $274.7B |
| All Sectors: Marketing, Sales & CRM | $130B – $250B | $190.0B |
| Government | $110.5B – $206.5B | $158.5B |
| Financial Services | $79.5B – $136.5B | $108.0B |
| Supply Chain & Procurement | $55B – $100B | $77.5B |
| Insurance | $38B – $73B | $55.4B |
| Rest of Economy *(indicative)* | $12B – $31B | $21.5B |
| Healthcare | $13.9B – $27.9B | $20.9B |
| Retail & E-Commerce | $5B – $12B | $8.4B |
| Telecommunications | $2B – $8B | $4.9B |

Two mismatches:

1. **Sanctions & trade compliance is not a row.** It is a $5–$15B sub-line *inside*
   the Rest of Economy row, described in the document's "Remaining Sectors"
   section alongside state & local government ($4–$8B) and residual sectors
   ($3–$8B), with derivations in the appendix. Listing it among the table's
   sectors sends the guide looking for a row that does not exist.
2. **The two "All Sectors" rows are unnamed**, and Cross-Industry Data Quality is
   the largest domain in the table ($274.7B midpoint). It is also the row that
   fits the most common bootcamper scenario — generic duplication across internal
   systems with no industry vertical — so its omission costs the gallery its most
   reusable business-value figure. Rest of Economy is likewise unnamed.

"Ten sectors" is correct: the document's own totals line reads "Expanded Estimate
(all 10 sectors)".

## Proposed change

Correct the enumeration in `phase1-discovery.md:36-39`:

- Name the two "All Sectors" rows, and lead with **Cross-Industry Data Quality**
  as the default row for a scenario with no clear industry vertical.
- Move sanctions & trade compliance out of the row list and describe it as a
  sub-line of Rest of Economy, reachable via the document's "Remaining Sectors"
  section and appendix — keeping it findable without implying it is a row.
- Keep the list explicitly non-exhaustive, and keep the existing instruction to
  cite figures as returned rather than from this file, so a future table revision
  changes numbers in one place only.

Consider whether the enumeration should exist at all: its job is to tell the guide
the table is worth querying, which one sentence naming the document and the table
heading already does. A shorter pointer cannot drift the way a ten-row list can.

## Acceptance criteria

- [ ] `phase1-discovery.md` no longer lists sanctions & trade compliance among the
      table's sectors, and describes it as a Rest of Economy sub-line.
- [ ] The two "All Sectors" rows are named, with Cross-Industry Data Quality
      identified as the row to use when the scenario has no industry vertical.
- [ ] The step still instructs the guide to cite figures as returned by
      `search_docs`, not from the plugin.
- [ ] The dated MCP verification (server version + date) is recorded wherever the
      plugin asserts what this document contains, per the marker convention.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` —
  correct the sector enumeration at Step 3.

## Source

- Feedback: dry run phase 3, 2026-08-13 — found while executing Step 3's
  business-value retrieval on a Core walk (`Source: self-observed (assistant
  retrospective)`)
- Priority: Low
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13 via `search_docs(query='total economic cost mismatched identity data
  by sector')` — the document and table exist as cited; the plugin's row list is
  what diverges. Still reproduces.
- Upstream: not applicable — the plugin's description is wrong, not the document.
- Related specs: none
