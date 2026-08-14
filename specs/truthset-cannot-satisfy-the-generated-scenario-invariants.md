# truthset cannot satisfy the generated-scenario invariants

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Step 4b tells the guide to pick a "fitting CORD dataset" to back a generated
business-case scenario, and Step 4a requires that scenario's data to be
mapping-complexity-rich. One of the four datasets the server offers —
**`truthset`** — is pre-mapped, so it can never satisfy that invariant. Nothing in
the step says so, and `truthset` is the most inviting choice: it is the smallest,
it is the one the rest of the bootcamp already uses, and its description says it is
used in quickstarts.

A guide that picks it produces a scenario that passes every check the step
enumerates except the one it structurally cannot meet, and the Data Quality,
Mapping, and Transformation module later has nothing to transform. There is a
second reason to exclude it that is also unstated: Truth Set visualization already
runs on the same data, so a scenario built on `truthset` collapses two modules onto
one dataset.

## Root cause

`plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:110-119`
requires the generated scenario to be "mapping-complexity-rich (needs at least one
transformation when mapped to the Senzing Entity Specification)", and `:129-141`
tells the guide to call `get_sample_data` and back the scenario with a fitting
dataset. Neither says which datasets can meet the invariant.

`get_sample_data(dataset='list')`, MCP server 1.32.9, checked 2026-08-13, returns
four datasets:

| Dataset | Sources | Fit for a generated scenario |
|---|---|---|
| `las-vegas` | 11 — Enformion, Equifax, GLEIF, ICIJ, NominoData Risk, NPI Registry, Open Ownership, OpenData.org, PPP Loans, Profound, US Labor Violations | usable; risk/ownership-shaped |
| `london` | 5 — GLEIF, GlobalData, ICIJ, OFAC, OpenSanctions | usable; sanctions-shaped |
| `moscow` | 6 — GLEIF, ICIJ, NominoData, OFAC, Open Ownership, OpenSanctions | usable; sanctions-shaped |
| `truthset` | 3 — Customers, Reference, Watchlist | **cannot** — pre-mapped |

The disqualifying fact is in the server's own tool description: truthset is "the
Senzing demo truth set: CUSTOMERS, REFERENCE, WATCHLIST — small, **pre-mapped**,
used in quickstarts" (`get_capabilities`, server 1.32.9, 2026-08-13).

A related gap, same step: the recognized category set at `:111-112` is ten
categories (Customer 360, Fraud Detection, Data Migration, Compliance, Marketing,
Healthcare, Supply Chain, KYC, Insurance, Vendor MDM), while all three usable CORD
collections are risk, sanctions and ownership data. For the categories a
bootcamper is most likely to pick — Customer 360 above all, since it is the
pattern gallery's most relatable entry — no CORD dataset fits, and the correct
outcome is the `synthesized` branch. The step does not say this, so the guide has
to rediscover it by reading four dataset descriptions and judging fit, with the
`cord` branch written first and reading like the default.

## Proposed change

1. In `phase1-discovery.md` Step 4b, state that **`truthset` is not eligible** to
   back a generated scenario, and give both reasons: it is pre-mapped, so it fails
   Step 4a's mapping-complexity invariant, and Truth Set visualization already
   uses it.
2. Say which datasets *are* eligible (`las-vegas`, `london`, `moscow`) and what
   they are shaped like, so the guide can judge category fit without inferring it
   from vendor names. Keep the list sourced from `get_sample_data` at runtime
   rather than hardcoding record counts.
3. Say plainly that the `synthesized` branch is the expected outcome for
   customer-facing categories (Customer 360, Marketing, Vendor MDM), so it does
   not read as a failure path. It is currently reachable only by concluding "none
   fit", which looks like giving up.

## Acceptance criteria

- [ ] `phase1-discovery.md` Step 4b names `truthset` as ineligible and gives both
      reasons.
- [ ] The step distinguishes the eligible CORD collections and what domain each
      covers, without hardcoding counts the server owns.
- [ ] The step states that `synthesized` is the expected outcome for
      customer-facing categories rather than a fallback.
- [ ] A walk that picks Customer 360 and accepts the Business Case Offer reaches
      the `synthesized` branch without the guide having to judge four datasets
      unaided.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` —
  Step 4b dataset eligibility and the `synthesized` framing.

## Source

- Feedback: dry run phase 3, 2026-08-13 — hit when the Business Case Offer was
  accepted for a Customer 360 scenario and the CORD branch had to be evaluated
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13 via `get_sample_data(dataset='list')` and `get_capabilities`. Four
  datasets returned as listed; truthset's "pre-mapped" description confirmed.
  Still reproduces.
- Upstream: not applicable — the server's data is fine; the plugin's step does not
  account for it.
- Related specs: `specs/pattern-gallery-sector-list-misdescribes-the-cost-table.md`
  (same step's other sourcing gap)
