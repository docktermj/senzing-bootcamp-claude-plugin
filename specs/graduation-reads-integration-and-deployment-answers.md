# Graduation never reads the software-integration and deployment-target answers INV-097 requires it to read

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 1 Phase 2 Step 10a asks the bootcamper two pinned 👉 questions (INV-056) and persists the
answers:

- "Will your entity-resolution results need to interface with other software …?" → `integration_targets`
- "Where do you plan to deploy the final solution?" → `deployment_target` / `cloud_provider`

**Graduation never reads either one.** The `production/` project it hands over — the artifact whose
whole purpose is "the thing you deploy" — is generated without them. So a bootcamper who answered
"AWS, behind an API gateway" gets exactly the same `docker-compose.yml`, `.env.example`,
`production/README.md` and `MIGRATION_CHECKLIST.md` as one who answered "local, no integrations".

Two questions were asked, answered, written to disk, and then had no effect on anything the
bootcamper keeps. Per INV-170's reasoning, that is indistinguishable from never having asked.

## Root cause

INV-097 has two halves. Only the first was built.

> **INV-097** — … their answers (`integration_targets`, `deployment_target`/`cloud_provider`) are
> persisted to `config/bootcamp_preferences.yaml` there and read by the Module 1 problem statement
> **and by graduation**.

- **Half one, done.** `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:80`
  holds the values, `:85` and `:94` ask the two pinned questions, `:105-106` enumerate the
  `deployment_target` vocabulary, and `:148-151` / `:200` consume them in the problem statement.
- **Half two, absent.** `plugins/senzing-bootcamp/skills/graduation/SKILL.md` contains **zero**
  occurrences of `integration_targets`, `deployment_target`, or `cloud_provider`. Its Pre-checks
  (`:134`) extract `name`, `language`, `path`, `selected_modules`, `database`, `data_sources` — and
  stop there. The consumers that would use them are all parameterized without them:
  - `:596` Step 3 — `docker-compose.yml` and `.env.example`, "parameterized by the language and
    database from pre-checks"
  - `:605` Step 4 — `production/README.md`, and `MIGRATION_CHECKLIST.md` whose sixth section is
    literally **Deployment**
  - `:616` Step 5 — `GRADUATION_REPORT.md`

The originating spec stated the requirement explicitly as an acceptance criterion —
`specs/relocate-integration-deployment-questions-to-module1.md:48`:

```text
- [ ] `integration_targets` and `deployment_target`/`cloud_provider` are still persisted and read
      by the Module 1 problem statement and by graduation.
```

…and the spec is recorded as implemented (`specs/IMPLEMENTED.md:2041`, 2026-07-22) with
`graduation/SKILL.md` **not** in its Files-changed list. The criterion was never met; the ledger
entry outran the implementation. Nothing caught it: no test references INV-097.

This is not a Senzing-behavior defect. It is a plugin-internal data-flow break of the class
INV-170 names: "A value the Bootcamper was **asked for** MUST outrank any value auto-detected …
and MUST be persisted everywhere the artifact is generated from."

## Proposed change

1. **Read them in Pre-checks.** Add `integration_targets` and `deployment_target`/`cloud_provider`
   to the `graduation/SKILL.md:134` preference read. Absent is normal and must not warn or ask —
   Module 1 may have been deselected under a Customized path (INV-076), and the questions are
   asked once (INV-006). Treat absent as "not stated" and fall through to today's behavior.
2. **Use them where they change the deliverable**, and only there:
   - **Step 3** — when `deployment_target` names a container platform or cloud, say so in the
     `docker-compose.yml` header comment and in `.env.example`'s comments; do not invent
     provider-specific resources or credentials (placeholder values only, per the step's existing
     rule).
   - **Step 4** — `MIGRATION_CHECKLIST.md`'s **Deployment** section names the stated target and
     its checklist items; `production/README.md`'s Configuration/Usage sections name the stated
     `integration_targets` as the consumers the resolved data is meant to feed.
   - **Step 5** — `GRADUATION_REPORT.md` records both values alongside language and database, so
     the handover states what the project was aimed at.
3. **Do not add a question.** If a value is missing, graduation stays silent about it. Asking at
   graduation for something Module 1 owns would violate INV-006 and INV-097's "asked in Module 1"
   placement.
4. **Assert it**, so the second half cannot go missing again: a test that graduation's Pre-checks
   name both keys, and that each of the three consuming steps references them.

## Acceptance criteria

- [ ] `graduation/SKILL.md` Pre-checks read `integration_targets` and
      `deployment_target`/`cloud_provider` from `config/bootcamp_preferences.yaml`.
- [ ] Steps 3, 4 and 5 each state how a present value changes what they generate, and state that an
      absent value changes nothing and is never asked for.
- [ ] `MIGRATION_CHECKLIST.md`'s Deployment section and `production/README.md` reflect a stated
      deployment target and stated integration targets when present.
- [ ] A test asserts graduation names both keys and that no graduation step asks a 👉 question for
      either (INV-006/INV-097).
- [ ] The whole path stays non-blocking: a missing, empty, or unparseable preferences file leaves
      graduation behaving exactly as it does today (INV-048).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — this is
      Markdown guidance plus generated project text, unaffected by OS or chosen language.

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Pre-checks (~`:134`); Step 3 (~`:596`);
  Step 4 (~`:605`); Step 5 (~`:616`).
- `tests/test_graduation_reads_module1_answers.py` (new) — or extend an existing graduation suite.
- `specs/relocate-integration-deployment-questions-to-module1.md` — append a dated note that
  criterion 4 was found unmet on 2026-07-29 and is discharged by this spec. Do **not** edit the
  criterion's text (INV-181's append-not-edit discipline).
- `specs/IMPLEMENTED.md` — when this spec is implemented, correct the 2026-07-22 entry's record by
  appending, not rewriting, so the ledger stops asserting a completion that did not happen.

## Source

- Feedback: n/a — found by the deep-dive invariant-conformance audit of 2026-07-29, run at the
  maintainer's request; `Source: self-observed (assistant retrospective)`.
- Priority: **High** — two pinned questions with zero effect on any artifact, in the terminal
  module, and an invariant clause standing unimplemented since 2026-07-20 (INV-088) while recorded
  as done.
- MCP re-check: n/a (no Senzing fact — plugin-internal data flow). Server **1.32.2** confirmed
  current at triage time via `get_capabilities`, 2026-07-29.
- Upstream: not applicable.
- Related specs: `specs/relocate-integration-deployment-questions-to-module1.md` (the originating
  spec whose criterion this discharges), `specs/relocate-setup-questions-to-bootcamp-preparation.md`
  (INV-088, superseded), `specs/certificate-name-must-reach-the-generator.md` (INV-170 — the same
  answer-does-not-reach-the-generator class),
  `specs/deep-dive-audit-2026-07-29-minor-fixes.md` (item 4 — the ledger-verification gap that let
  this criterion be recorded as met).

## Note on scope

Do **not** widen this into "graduation should tailor the production project to the deployment
target" as a feature. INV-097 requires the values be *read*; the smallest change that makes them
visibly affect the three deliverables satisfies it. Provider-specific infrastructure generation is
an Advanced-Topics follow-up (INV-013's parenthetical), not this spec.

## Deviations from this spec, and why (2026-07-29)

- **Implemented in one pass with two sibling specs**, all three landing in `graduation/SKILL.md`:
  `graduation-prechecks-read-the-keys-that-are-written` (whose corrected Pre-checks table carries
  these two keys) and `normalize-production-markdown-at-graduation`. One shared test file,
  `tests/test_graduation_reads_persisted_answers.py`, asserts all three specs' properties — the
  cheaper alternative to three files re-parsing the same skill.
- **Criterion count.** This spec carries **six** acceptance criteria. A seventh `- [ ]` appears in its
  Root cause section, but that is a *quotation* of the originating spec's unmet criterion
  (`relocate-integration-deployment-questions-to-module1.md:48`), not a criterion of this spec.
- **The "how a present value changes the deliverable" guidance is deliberately declarative.** Steps 3
  and 4 name the target and adjust which checklist items appear; they do **not** generate
  provider-specific infrastructure, credentials, ARNs or account identifiers. The spec's own scope
  note asked for this, and it is restated as a ⛔ in the skill, because a wrong infrastructure guess
  in a handed-over project is worse than a generic one.
- **Not runtime-verified:** nothing needed a live engine. Each of the six criteria is static guidance
  plus a test; the guards were mutation-tested by dropping each key's table row and by stripping the
  keys out of Step 4, and reverted.
