# Don't gate auto-generated deliverables behind a yes/no question — generate and announce

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two low-stakes yes/no gates sit in front of generating deliverables the bootcamper
almost always wants. The bootcamper asked to remove both: always generate, and
simply announce (as a statement, not a question) what was created — one fewer
decision point each.

1. **Module 1 stakeholder summary** — Step 16 asks "👉 Would you like a one-page
   executive summary to share with your team?" before writing
   `docs/stakeholder_summary_module1.md`.
2. **Graduation production config** — Step 2 ends with "👉 Ready to generate the
   production configuration files (`.env.example`, `docker-compose.yml`,
   `.gitignore`)?" before Step 3 generates them.

## Root cause (confirmed)

Both are pinned 👉 gates by design:

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:121-128`
  — "## 16. Offer a stakeholder summary / 👉 **Would you like a one-page executive
  summary to share with your team?**" then, if yes, produce
  `docs/stakeholder_summary_module1.md`.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:197-200` — "👉 **Ready to
  generate the production configuration files (`.env.example`, `docker-compose.yml`,
  `.gitignore`)?**", leading into Step 3 (`:202-209`).

No invariant requires either gate. INV-012 (suppress output not important to the
bootcamper) actually favors dropping low-value confirmations. Note: the graduation
config-confirm question was previously *pinned* by `pin-visualization-offer-questions.md`
(then at `:192`); removing it partially supersedes that pinning for this one gate.

## Proposed change

- **Module 1 Step 16:** drop the 👉 gate. Always produce
  `docs/stakeholder_summary_module1.md` (problem, approach, data sources, key
  findings, next steps, ROI considerations) from `docs/business_problem.md`, then
  **state** at module completion (alongside the Module 1 summary, INV-032) that the
  stakeholder summary was created and where to find it.
- **Graduation Step 2→3:** drop the 👉 gate. Flow directly into Step 3 and generate
  `.env.example`, `docker-compose.yml`, `.gitignore`. Optionally print a one-line
  statement of what is being generated — as a statement, not a question.
- Leave the graduation overwrite/merge/abort gate for an existing `production/`
  (`graduation/SKILL.md:168-176`) intact — that is a genuine data-safety decision,
  not a low-stakes confirmation.

## Acceptance criteria

- [ ] `docs/stakeholder_summary_module1.md` is always generated in Module 1 (no 👉 gate), and its creation is announced as a statement at module completion (INV-032).
- [ ] Graduation generates the production config files without a 👉 gate; Step 2 flows directly into Step 3, optionally announcing generation as a statement.
- [ ] Neither removed gate leaves a dangling reference (step numbering/checkpoints reconciled); the graduation overwrite/merge/abort safety gate is unchanged.
- [ ] No new 👉 question is introduced; INV-005/INV-012 remain satisfied.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — remove the Step 16 gate (`:121-128`), always generate, announce at completion.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — remove the Step 2→3 config gate (`:197-200`), flow into Step 3 (`:202-209`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Always generate the stakeholder summary; announce it instead of gating it with a question" (2026-07-18, Module 1); "Don't gate production-config generation behind a yes/no question during graduation" (Graduation).
- Priority: Medium.
- Related specs: `pin-visualization-offer-questions.md` (previously pinned the graduation config gate — partially superseded here for that gate).
