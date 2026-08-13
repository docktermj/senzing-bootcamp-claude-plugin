# The pattern gallery asks for more content than MCP supplies, with no guidance for the gap

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 1 Step 3 tells the guide to present a design-pattern gallery covering the recognized
use-case categories, and to give **four specific things for each**:

> Present an entity-resolution design-pattern gallery (recognized use-case categories below;
> pull real-world examples via `search_docs`: the full pattern gallery is a later porting
> phase). For each: the problem it solves, the goal, typical data sources, business value.
> — `module-01-business-problem/phase1-discovery.md:22-24`

The recognized set has **ten** categories (`phase2-document-confirm.md:124-125`, restated at
`phase1-discovery.md:66-68`): Customer 360, Fraud Detection, Data Migration, Compliance,
Marketing, Healthcare, Supply Chain, KYC, Insurance, Vendor MDM.

`search_docs` does not return per-category detail for all ten. In the dry-run walk (server
1.32.9, 2026-08-13) two calls — `search_docs(query='entity resolution use cases KYC fraud
detection customer 360 compliance')` and `search_docs(query='Senzing use cases master data
management healthcare insurance supply chain')` — returned substantive, quotable material for
four: **Customer 360** (the use-cases page's duplicate-elimination and customer-network line),
**Fraud Detection** (its bad-actor line, plus the USCIS case study), **Vendor MDM** (the MDM
integration FAQ, including free resolution vs forced separation via a Trusted ID), and
**Compliance/KYC** (regulatory-compliance framing only). The Senzing use-cases page's remaining
entries came back as bare link stubs (`[Read More](/risk-fraud-detection)`) with no problem, goal,
sources, or value text. Nothing surfaced for Data Migration, Marketing, Healthcare, Supply Chain,
or Insurance.

So the step asks for forty facts and the server supplies roughly a dozen. **The step says nothing
about what to do with the shortfall**, which leaves the guide choosing between two bad options at
a bootcamper-facing moment:

1. Fill the gap from training data — a direct INV-080 violation, and an attractive one because the
   surrounding text implies a complete gallery is the deliverable, and because plausible
   business-value prose for "Healthcare" is trivially easy to generate.
2. Present a partial gallery and improvise an explanation — what the walk did, but unguided, so
   two guides produce different bootcamper experiences and neither is the specified one.

The parenthetical "the full pattern gallery is a later porting phase" explains *why* the content is
thin but reads as an authoring note, not an instruction. It tells the guide the gallery is
incomplete without telling it how to behave when it is.

## Root cause

The step specifies its output shape (four attributes × ten categories) independently of what its
named source can actually produce, and has no shortfall branch. This is structurally the same gap
INV-192 addresses for a gated MCP response — a call that returns less than the caller assumed —
except here the response is not gated, merely thin, so no `needs_input` signal marks it.

The plugin handles this pattern correctly elsewhere, which is what makes the omission visible:

- `module-02-sdk-setup/SKILL.md` Step 5a instructs the guide to present the record limit from MCP
  and, "If it returns no figure, drop the parenthetical entirely and say the current limit is
  unavailable from the MCP server" — an explicit shortfall branch for one value.
- `phase1-discovery.md:28-31` already tells the guide to "attribute to the MCP server only what an
  MCP tool actually produced", which forbids option 1 but does not say what to do instead.

## Proposed change

Add a shortfall branch to Step 3, and make the gallery's contract "as many as the server covers"
rather than "all ten":

1. State that the gallery presents the categories for which `search_docs` **returned substantive
   content this session**, with the four attributes filled from that content only.
2. ⛔ Require the remaining recognized categories to be **named as available without invented
   detail**, together with an offer to look any of them up on request. A category the bootcamper
   asks about gets its own `search_docs` call at that point.
3. ⛔ State plainly that per-category detail MUST NOT be supplied from training data when the
   search returns none, citing INV-080 — the gallery is bootcamper-facing content presented as
   Senzing-sourced, so a fabricated entry is attributed to the server by the surrounding
   attribution line.
4. Note that a bare link stub in a `search_docs` result (`[Read More](/…)`) is **not** content:
   the Senzing use-cases page returns several categories this way, and a stub is the shape most
   likely to be mistaken for coverage.
5. Keep the "later porting phase" note, but separate it from the behavioural instruction so it
   reads as background rather than as the guidance.

## Acceptance criteria

- [ ] Step 3 names the four attributes as coming from MCP-returned content only, and does not
      imply all ten categories carry them.
- [ ] Step 3 carries an explicit ⛔ forbidding training-data fill for an uncovered category, and an
      explicit instruction to name uncovered categories without detail plus offer a lookup.
- [ ] Step 3 states that a link-stub result is not substantive content.
- [ ] A repo-level stdlib-only test asserts Step 3 contains the shortfall branch and the
      no-training-data ⛔, and that the recognized-category list in `phase1-discovery.md` and
      `phase2-document-confirm.md` still agree (they are duplicated today, so they can drift).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 3.
- `tests/test_pattern_gallery_shortfall.py` — new guard.

## Source

- Feedback: none — dry run phase 3 (2026-08-13), conversational walk, Module 1 Step 3 reached with
  the maintainer answering as the Bootcamper (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — bootcamper-facing, and the failure mode it invites (fabricated Senzing content
  under an MCP attribution line) is exactly what INV-080 exists to prevent. Not a broken path: the
  step still functions, which is why three audits and the offline suite could not see it.
- MCP re-check: server 1.32.9, 2026-08-13 — the shortfall is the finding and it reproduces. Two
  `search_docs` calls (queries quoted above) returned substantive material for 4 of 10 categories
  and link stubs or nothing for the rest. No plugin claim is contradicted by the server; the gap is
  between what the step asks for and what the server holds.
- Upstream: not applicable — the server's coverage is what it is; the plugin must handle it.
- Related specs: none
