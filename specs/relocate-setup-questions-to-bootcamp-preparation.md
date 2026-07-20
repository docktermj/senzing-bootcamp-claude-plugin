# Relocate the software-integration and deployment-target questions to Bootcamp preparation

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two feedback items with the same shape. Module 1 (Discover the Business Problem), Phase 1 asks:

- **Software integration** (Step 7): "Will the results need to interface with other software
  (CRM, search engine, data warehouse, API gateway, downstream app)?"
- **Deployment target** (Step 8): "Where do you plan to deploy the final solution?"
  (cloud / container / local / not sure).

The bootcamper reads both as *setup* questions that should be grouped with the other setup
questions in the **Bootcamp preparation** module (path, module selection, verbosity, language,
version control), rather than being split into a content module. Grouping all setup keeps the
flow coherent.

## Root cause

Not a defect — a scoping decision. The two questions currently live in business-problem discovery:

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:241-247` — Step 7
  (software integration); on "yes" it asks a follow-up ("Which systems?") and records named
  systems for the problem statement and solution approach.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:249-264` — Step 8
  (deployment target); optional context, persists `deployment_target`/`cloud_provider`, "helps
  tailor" the graduation production project and migration checklist.

Bootcamp preparation (`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md`) consolidates
"all setup" in one place (INV-075) but does **not** include these two questions; the current design
classifies them as business-problem discovery, not setup.

## Design tension (do not silently override — surface for the maintainer)

Both questions depend on the business problem being defined, and Bootcamp preparation runs
**before** Module 1:

- Software integration feeds the problem statement / solution approach (Step 7 records the named
  systems). Asking it before the problem is described (or, for the Business Case Offer, before the
  scenario is generated) inverts that dependency.
- Deployment target is optional tailoring; for a **bootcamp-generated** scenario there is no real
  deployment context to capture at all.

Moving them to preparation is therefore a genuine judgment call. This spec encodes the requested
move; the implementer must confirm with the maintainer whether the placement is desired given the
dependency, and if kept in Module 1 instead, record that decision rather than doing nothing.

INV-075 enumerates Bootcamp preparation's remit; adding these two questions extends it. Lock the
new placement by clarifying INV-075's wording in place (maintenance rule 2) or adding a new
invariant — the maintainer decides at implementation.

## Proposed change

1. **Remove Steps 7–8 from `phase1-discovery.md`.** Close Phase 1 at Step 6 and route Step 6 →
   Phase 2 with no dangling references to the removed steps.
2. **Add both questions to `bootcamp-preparation/SKILL.md`** as new setup steps — each a pinned
   verbatim 👉 question (INV-056) ending its own turn (INV-005), neutral-lead + numbered list
   where multiple choices exist (INV-051). Persist `integration_targets` and
   `deployment_target`/`cloud_provider` in the single consolidated preference write (INV-058), not
   a per-question write.
3. **Reconcile downstream readers** that expect `deployment_target` from Module 1 (graduation's
   production project and migration checklist) to read it from `config/bootcamp_preferences.yaml`
   as written in preparation.
4. **Invariant:** if the placement is to be locked, update INV-075's enumerated setup questions in
   place (wording clarification, no meaning change) or add a new INV recording the moved questions.

## Acceptance criteria

- [ ] The software-integration and deployment-target questions are asked in Bootcamp preparation, each as its own pinned verbatim 👉 question ending its turn (INV-005/INV-051/INV-056), and no longer in Module 1 Phase 1.
- [ ] `integration_targets` and `deployment_target` (and `cloud_provider` when applicable) are persisted in the Bootcamp-preparation consolidated write (INV-058); graduation still reads `deployment_target` for the production project / migration checklist.
- [ ] Module 1 Phase 1 flows Step 6 → Phase 2 with no reference to the removed Steps 7–8.
- [ ] The dependency tension (questions precede the business-problem definition; generated scenarios have no real target) is resolved by an explicit maintainer decision recorded at implementation.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — remove Steps 7–8; close Phase 1 at Step 6.
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — add the two setup questions and their consolidated-write keys.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` (and any other consumer of `deployment_target`) — read the target from preferences.
- `specs/INVARIANTS.md` — INV-075 remit clarification (only if the new placement is to be locked).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Move software-integration question to Bootcamp Preparation" and "Move deployment-target question to Bootcamp Preparation" (2026-07-20, Module 1)
- Priority: Medium
- Related specs: none (touches INV-075)

## Invariants introduced

- `INV-088` — The software-integration and deployment-target questions are asked in Bootcamp preparation (not Module 1), each pinned-verbatim, persisted in the consolidated write, and read from `config/bootcamp_preferences.yaml` by Module 1's problem statement and graduation (recorded in `specs/INVARIANTS.md`; extends INV-075).

## Maintainer decision (2026-07-20)

Proceed with relocating **both** questions into Bootcamp preparation (maintainer selected this spec for implementation). The dependency tension (both questions run before the business problem is defined) is resolved by phrasing them as forward-looking intent, answerable up front and persisted to preferences for later consumption; the answers no longer appear as a recapped Module 1 Q&A because Bootcamp preparation is apparatus-exempt (INV-075). The shipped example recap (`docs/examples/bootcamp_recap.example.md`) still shows the integration question under a module section — a fixture refresh is a separate follow-up (INV-065 / `refresh-example-recap`).
