# Relocate the integration and deployment questions from Bootcamp preparation to Discover the Business Problem

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The software-integration question ("will your entity-resolution results need to
interface with other software") and the deployment-target question ("where do you
plan to deploy the final solution") are asked during Bootcamp preparation — before
the business scenario exists. The bootcamper wants **only those two** relocated to
Module 1 (Discover the Business Problem), asked after the scenario is chosen but
before the documentation artifacts are written, so the answers flow directly into
`docs/business_problem.md`. The programming-language question stays in preparation
(it drives platform/SDK routing and is independent of the scenario).

## Root cause

Both questions currently live in `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md`:
`## 4a. Software integration` (`:178-190`, question at `:184`, persists
`integration_targets`) and `## 4b. Deployment target` (`:192-209`, question at
`:198`, persists `deployment_target`/`cloud_provider`). Module 1 today only **reads**
them (`module-01-business-problem/phase1-discovery.md:239-243`; consumed in Phase 2 at
`phase2-document-confirm.md:62`, `:64-69`, `:109`). The natural insertion point is
between Module 1 Phase 2 Step 10 (scenario finalized, `phase2-document-confirm.md:18-21`)
and Step 11 (artifacts written, `phase2-document-confirm.md:23-93`).

**Invariant conflict (do not silently override):** this **reverses INV-088**, which
put both questions in Bootcamp preparation and had Module 1 read them from
`config/bootcamp_preferences.yaml` (established by
`relocate-setup-questions-to-bootcamp-preparation`). It also touches INV-075's
cross-reference note. Implementing this requires amending INV-088 (for these two
questions only) and reconciling INV-075's note.

## Proposed change

Move §4a and §4b out of `bootcamp-preparation/SKILL.md` and into Module 1 Phase 2,
asked after Step 10 (scenario finalized) and before Step 11 (artifact generation),
each as its own pinned-verbatim 👉 question (INV-056). Keep §4 programming-language in
preparation unchanged. Preserve the persisted keys `integration_targets` and
`deployment_target`/`cloud_provider` in `config/bootcamp_preferences.yaml` so
graduation and the Module 1 problem statement still read them. Amend INV-088 to scope
these two questions to Module 1.

## Acceptance criteria

- [ ] The integration and deployment questions are asked in Module 1 after the scenario is chosen and before `docs/business_problem.md`, `config/data_sources.yaml`, and `README.md` are written; they are no longer asked in Bootcamp preparation.
- [ ] The programming-language question remains in Bootcamp preparation.
- [ ] `integration_targets` and `deployment_target`/`cloud_provider` are still persisted and read by the Module 1 problem statement and by graduation.
- [ ] Each relocated question stays pinned verbatim (INV-056), unambiguous (INV-008), and uses a neutral lead + numbered list where it offers 2+ choices (INV-051).
- [ ] `INVARIANTS.md` is updated to amend INV-088 (and reconcile INV-075's note).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — remove §4a (`:178-190`) and §4b (`:192-209`).
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — add the two questions between Step 10 and Step 11.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — update/remove the "relocated, read-only" note (`:239-243`).
- `specs/INVARIANTS.md` — amend INV-088.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Move integration / deployment questions from Bootcamp preparation into Discover the Business Problem (keep programming language in preparation)" (2026-07-22, Module Bootcamp preparation / Discover the Business Problem)
- Priority: Medium
- Related specs: `specs/relocate-setup-questions-to-bootcamp-preparation.md` (this reverses it for the two questions; INV-088); INV-075
