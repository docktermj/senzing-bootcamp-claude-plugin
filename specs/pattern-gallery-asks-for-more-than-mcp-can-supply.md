# The pattern gallery gives no query guidance, so one generic query looks like the server's coverage

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

> ⚠️ **This spec's diagnosis was wrong on first writing and was corrected before implementation.**
> It claimed `search_docs` covers only 4 of the 10 recognized categories and that the rest must
> therefore be named without detail. That was concluded from **two broad queries** — the same
> ask-the-wrong-route error that produced INV-208 earlier the same day (INV-194). Queried with each
> category's own sector vocabulary, the material is available for nearly every category. The gap is
> **query guidance**, not coverage. See "What the re-check found" below.

## Problem

Module 1 Step 3 tells the guide to present a design-pattern gallery covering the recognized
use-case categories, with **four attributes each**:

> Present an entity-resolution design-pattern gallery (recognized use-case categories below;
> pull real-world examples via `search_docs`: the full pattern gallery is a later porting
> phase). For each: the problem it solves, the goal, typical data sources, business value.
> — `module-01-business-problem/phase1-discovery.md:22-24`

Ten categories (`phase2-document-confirm.md:124-125`): Customer 360, Fraud Detection, Data
Migration, Compliance, Marketing, Healthcare, Supply Chain, KYC, Insurance, Vendor MDM.

**The step names the tool and says nothing about how to query it.** So the guide does the obvious
thing — one or two generic queries about entity-resolution use cases — reaches roughly four
categories, and is left choosing between two bad options at a bootcamper-facing moment:

1. Fill the rest from training data. A direct INV-080 violation, and an attractive one: the step
   implies a complete gallery, plausible business-value prose is trivial to generate, and the
   surrounding attribution line ("Sourced from Senzing docs via the MCP server") then launders it.
2. Present a partial gallery and improvise an explanation — what the dry-run walk did. Defensible,
   but unguided, so two guides produce materially different bootcamper experiences.

Neither is the specified behavior, and the parenthetical "the full pattern gallery is a later
porting phase" explains *why* the content feels thin without saying how to behave.

## What the re-check found (server 1.32.9, 2026-08-13)

The broad queries the first draft used — `entity resolution use cases KYC fraud detection customer
360 compliance` and `Senzing use cases master data management healthcare insurance supply chain` —
returned substantive material for Customer 360, Fraud Detection (with the USCIS case study), Vendor
MDM (the MDM integration FAQ) and Compliance/KYC, and **link stubs** (`[Read More](/risk-fraud-detection)`)
or nothing for the rest. That is what made "4 of 10" look like coverage.

Queried by **sector vocabulary** instead, the picture is different:

- `search_docs(query='total economic cost mismatched identity data by sector retail marketing
  government banking')` returns `local://economic-cost-mismatched-identity-data.md`, whose
  **"Estimated Annual Cost of Mismatched Identity Records"** table quantifies ten sectors —
  Marketing/Sales/CRM ($130–250B), Government, Financial Services, **Supply Chain & Procurement**
  ($55–100B), **Insurance** ($38–73B), **Healthcare** ($13.9–27.9B), Retail & E-Commerce,
  Telecommunications, cross-industry data quality — plus a sanctions & trade compliance line. That
  is the **business value** attribute, sourced and specific, for almost every recognized category.
- `search_docs(query='insurance claims fraud ring claimant witness medical provider cross-claim')`
  returns the same document's Insurance appendix (ER-attributable typologies: cross-carrier fraud
  rings, duplicate claims, synthetic identity applications, phantom providers) — richer than what
  the broad queries produced for Compliance.
- `search_docs(query='patient record matching healthcare provider duplicate medical records')`
  returns only generic ER material, so Healthcare's *use-case* prose is genuinely thin even though
  its cost line exists.

**Two homonym traps, both of which return confidently wrong results rather than nothing:**

- **Supply Chain** — already documented at Step 14 (`phase2-document-confirm.md:217-224`): BM25
  matches "chains" and the software sense, returning `senzing/libpostal`'s store-chains geodata
  scripts and a `sz_spark` "CI / supply chain" changelog heading.
- **Data Migration** — `search_docs(query='data migration consolidating systems merging databases
  legacy system retirement')` returns **V3→V4 SDK migration** steps (`sz_dbupgrade`,
  `sz_configupgrade`, Java/Python migration guides). This is the one category with no
  business-use-case material, and querying it plainly yields plausible, well-formed, *entirely
  wrong* content for a gallery.

## Root cause

The step specifies its output shape (4 attributes × 10 categories) and names its source, but gives
no **retrieval strategy** — and this corpus needs one, because category names are not the
documentation's vocabulary. `concepts.md` states the underlying rule in full for Module 0
(*"`search_docs` is BM25, so phrasing decides what comes back … treat an empty or off-topic result
as a query problem first"*), and Step 14 restates it with a measured example for its own step.
Step 3 — the step whose entire job is retrieving ten categories' worth of material — has neither.

So the failure is not that the server lacks the facts. It is that the obvious query does not reach
them, and a query that misses is indistinguishable from documentation that does not cover the topic.

## Proposed change

1. **Give Step 3 a retrieval strategy.** Query per category using its **sector/business
   vocabulary**, not the category label; name `economic-cost-mismatched-identity-data.md`'s sector
   cost table as the document that carries quantified **business value** for most categories, and
   the Senzing use-cases page plus the MDM and non-person-entity FAQs for problem/goal/sources.
2. **Point at the re-query rule rather than restating it** — `concepts.md`'s statement is the full
   one, and Step 14 already restates it once; a third copy is what drifts.
3. ⛔ **Name the two homonym traps** (Supply Chain, Data Migration) with what they wrongly return,
   because both produce confident wrong answers rather than empty ones.
4. ⛔ **Forbid training-data fill** for a category the searches do not reach, citing INV-080, and
   require such a category to be **named as available without invented detail**, with an offer to
   look it up on request.
5. **State that a bare link stub is not content** — the use-cases page returns several categories as
   `[Read More](/…)`, the shape most likely to be mistaken for coverage.
6. **Stop implying one query yields all forty facts:** the four attributes are filled from
   MCP-returned content, per category, and the gallery presents what the searches actually reached.
7. Keep the "later porting phase" note, separated from the behavioral instruction.

## Acceptance criteria

- [ ] Step 3 names the sector-vocabulary retrieval strategy and the specific documents that carry
      business value and problem/goal/sources.
- [ ] Step 3 names both homonym traps and what each wrongly returns.
- [ ] Step 3 carries an explicit ⛔ forbidding training-data fill, and requires an unreached category
      to be named without detail plus an offer to look it up.
- [ ] Step 3 states that a link-stub result is not substantive content.
- [ ] Step 3 points at `concepts.md`'s re-query rule rather than restating its reasoning.
- [ ] Step 3 no longer implies all ten categories carry all four attributes from a single query.
- [ ] A repo-level stdlib-only test asserts the above, and that the recognized-category list in
      `phase1-discovery.md` and `phase2-document-confirm.md` still agree — they are duplicated
      today, so they can drift.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 3.
- `tests/test_pattern_gallery_shortfall.py` — new guard.

## Source

- Feedback: none — dry run phase 3 (2026-08-13), conversational walk, Module 1 Step 3 reached with
  the maintainer answering as the Bootcamper (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — bootcamper-facing, and the failure it invites is fabricated Senzing content
  under an MCP attribution line, which is what INV-080 exists to prevent. Not a broken path, which
  is why three audits and the offline suite could not see it.
- MCP re-check: server 1.32.9, 2026-08-13 — **the re-check corrected this spec's own diagnosis.**
  Six queries, quoted above. Coverage is far wider than the first draft claimed; the gap is
  retrieval strategy. Data Migration is genuinely uncovered as a business use case and returns
  V3→V4 SDK content instead.
- Upstream: not applicable — the server's material is there; the plugin must know how to ask.
- Related specs: `specs/no-license-path-environment-variable.md` — the same
  concluded-absence-from-the-wrong-route error, made mechanical by INV-209.
