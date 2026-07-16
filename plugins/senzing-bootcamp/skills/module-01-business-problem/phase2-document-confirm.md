# Module 1, Phase 2: Document and Confirm (steps 10–18)

Continues from Phase 1. Follow the ground rules; `🛑`/`⛔` are internal directives.

## 10. Encourage visual explanations

Ask for diagrams of data architecture, data flows, or example records. If an image contains
placeholders like `[variable]`, ask what each represents. **Checkpoint:** write step 10.

## 11. Identify the scenario

Categorize as Customer 360, Fraud Detection, Data Migration, Compliance, Marketing, etc. If a
pattern was selected, it's already identified. **Checkpoint:** write step 11.

## 12. Create the problem statement document

Save to `docs/business_problem.md` using this template:

```markdown
# Business Problem Statement

**Date**: [Current date]
**Project**: [Project name]
**Design Pattern**: [Pattern name if selected, or "Custom"]

## Problem Description
[One sentence]

## Use Case Category
[Customer 360 / Fraud Detection / Data Migration / Compliance / Marketing / Healthcare /
 Supply Chain / KYC / Insurance / Vendor MDM]

## Design Pattern Reference
[If a pattern was selected: Pattern, Standard Goal, Customizations]

## Data Sources
1. **[Source name]**: Type / ~Records / Entity type / Update frequency / Access
2. **[Source name]**: [same structure]

## Entity Types
[People / Organizations / Both / Other]

## Key Matching Criteria
- **[Attribute]** (High/Medium/Low priority): [why]

## Success Criteria
- [Measurable outcome 1..3]

## Desired Output
**Format**: [Master list / API / Reports / Export]  **Use case**: [One-time / Ongoing /
Real-time]  **Integration**: [Standalone / Integrated with [systems]]

## Integration Requirements
**Downstream systems** / **Integration method** / **Systems mentioned** (from Step 8)

## Deployment Target
[If `deployment_target` present in preferences: Platform / Category (Cloud/Container/Local/
Undecided) / Note "development proceeds locally first; infra configured in Module 11". If
"not sure yet": Platform "To be determined", Category "Undecided". If absent: "Not applicable
: current track does not include Module 11."]

## Timeline
**Target completion** / **Key milestones**

## Notes
[Constraints, context]
```

**Generated scenario (Business Case Offer accepted):** produce the SAME artifacts a real case
would, plus:

- Insert the generated marker on its own line directly below the `# Business Problem Statement`
  title, exactly: `> 🤖 Bootcamp-generated business case`.
- Record each distinct scenario source into `config/data_sources.yaml` (one entry per source).
- Keep `docs/business_problem.md` self-contained (problem, category, sources, success), not
  dependent on the registry.
- Never embed CORD names/counts from training data: retrieve via MCP (`get_sample_data`,
  `search_docs`) at runtime.

**If writing an artifact fails:** say WHICH artifact failed; do not report Module 1 complete
until the bootcamper is told. **If artifacts are later missing/unreadable:** tell the
bootcamper the generated data is unavailable and let them supply real data.

**Checkpoint:** write step 12.

## 13. Update README.md

Fill the Overview and Business Problem sections with what was gathered; mention the design
pattern if one was selected. **Checkpoint:** write step 13.

## 14. Propose the solution approach

Explain how Senzing solves this and which modules are most relevant. If a pattern was selected,
reference how the bootcamp implements it.

- **If the problem involves search/lookup:** clarify the correct layering: Senzing first for
  entity resolution, THEN a search index (Elasticsearch/OpenSearch) over resolved entities.
  This prevents a common architecture mistake. (Full `design-patterns` reference is a later
  porting phase; use `search_docs` for specifics.)
- **If integration targets were identified in Step 8:** reference them and use `search_docs`
  for Senzing's guidance on integrating with those systems.

**Checkpoint:** write step 14.

## 15. Senzing value restatement

Before confirming, reinforce why Senzing ER is valuable for THIS problem. Use
`search_docs(query='value proposition <use_case_category>', version='current')` and tie the
value to the bootcamper's specific data, sources, and outcomes (not generic marketing). If
integration targets exist, explain how Senzing fits alongside them as a foundational layer.

**Checkpoint:** write step 15.

## 16. Get confirmation

👉 **Does this accurately capture your problem and approach?**

*(Internal: end the turn and wait.)* **Checkpoint:** write step 16.

## 17. Offer a stakeholder summary

👉 **Would you like a one-page executive summary to share with your team?**

*(Internal: end the turn and wait.)* If yes, produce `docs/stakeholder_summary.md` covering
problem, approach, data sources, key findings, next steps, and ROI considerations, filled with
Module 1 context from `docs/business_problem.md`. (The Kiro `templates/stakeholder_summary.md`
port is a later phase; compose the summary directly for now.) **Checkpoint:** write step 17.

## 18. Module completion and transition to Module 2

Run the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md` (update progress, append the Module 1 recap
section to `docs/bootcamp_recap.md`, and present the end-of-module summary), then ask the single
transition question.

Modules run in ascending numeric order (Module 1 → Module 2 → … → Module 7). After the business
problem is defined, the next module installs and configures the Senzing SDK:

👉 **Module 1 complete. Ready to install and configure the Senzing SDK in Module 2?**

**Checkpoint:** write step 18. On module completion set `current_step` to `null`.

**Success indicator:** ✅ Clear problem statement + identified data sources + defined success
metrics + bootcamper confirmation + `docs/business_problem.md` created + Module 1 recap section
appended.
