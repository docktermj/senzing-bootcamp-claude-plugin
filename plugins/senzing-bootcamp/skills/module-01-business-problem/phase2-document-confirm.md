# Module 1, Phase 2: Document and Confirm (steps 9–17)

Continues from Phase 1. Follow the ground rules; `🛑`/`⛔` are internal directives.

## 9. Encourage visual explanations

Invite the bootcamper to share any diagrams. Ask this single, pinned 👉 question, verbatim
(INV-056), and end the turn on it:

👉 **Do you have any diagrams of your data architecture and flows you'd like to share?**

It has exactly one meaning each (INV-008): "yes" means they will share diagrams (data
architecture, data flows, or example records); "no" alone means proceed with the scenario as
described. Do NOT fold the "proceed" branch into the question — no "or"-joined choices
(INV-009/INV-051). If they share an image containing placeholders like `[variable]`, ask what
each represents. **Checkpoint:** write step 9.

## 10. Identify the scenario

Categorize as Customer 360, Fraud Detection, Data Migration, Compliance, Marketing, etc. If a
pattern was selected, it's already identified. **Checkpoint:** write step 10.

## 10a. Software integration and deployment target

Now that the scenario is identified — and **before** the problem-statement artifacts are written
in Step 11 — capture two forward-looking attributes of the business problem so they flow straight
into the problem statement and the graduation production project (INV-097). Ask each as its own
pinned 👉 question (INV-056), one per turn (INV-005), and persist the answers to
`config/bootcamp_preferences.yaml`.

First, software integration:

👉 **Will your entity-resolution results need to interface with other software (CRM, search engine, data warehouse, API gateway, downstream app)?**

*(Internal: end the turn and wait.)* On **yes**, ask one follow-up on the next turn — "👉 **Which
systems do you expect to integrate with?**" — and persist the named systems (e.g. Elasticsearch,
Salesforce) as `integration_targets`. On **no**, persist `integration_targets: []`.

Then, deployment target — a separate, pinned 👉 question (neutral lead + numbered list, INV-051):

👉 **Where do you plan to deploy the final solution? Reply with a number:**

1. A cloud hyperscaler (AWS/Azure/GCP).
2. A container platform (Kubernetes/Docker Swarm).
3. Local / on-premises.
4. Not sure yet.

*(Internal: end the turn and wait.)* Reassure: "We'll develop everything locally first; deployment
is addressed in the graduation production project and migration checklist." Persist
`deployment_target` (`aws`/`azure`/`gcp` — also persist `cloud_provider`; `kubernetes`/
`docker_swarm`; `local`/`on_premises`; or `undecided` for option 4) to
`config/bootcamp_preferences.yaml`. **Checkpoint:** write step 10a.

## 11. Create the problem statement document

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
**Downstream systems** / **Integration method** / **Systems mentioned** (from `integration_targets` in `config/bootcamp_preferences.yaml`, captured in Phase 2 Step 10a — INV-097)

## Deployment Target
[If `deployment_target` present in preferences: Platform / Category (Cloud/Container/Local/
Undecided) / Note "development proceeds locally first; infrastructure is a production follow-up
covered by the graduation production project and migration checklist". If "not sure yet":
Platform "To be determined", Category "Undecided". If absent: "Not applicable: deployment target
not captured for this track."]

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

**Checkpoint:** write step 11.

## 12. Update README.md

Fill the Overview and Business Problem sections with what was gathered; mention the design
pattern if one was selected. **Checkpoint:** write step 12.

## 13. Propose the solution approach

Explain how Senzing solves this and which modules are most relevant. If a pattern was selected,
reference how the bootcamp implements it.

- **If the problem involves search/lookup:** clarify the correct layering: Senzing first for
  entity resolution, THEN a search index (Elasticsearch/OpenSearch) over resolved entities.
  This prevents a common architecture mistake. (Full `design-patterns` reference is a later
  porting phase; use `search_docs` for specifics.)
- **If integration targets were identified** (`integration_targets` in `config/bootcamp_preferences.yaml`, captured in Phase 2 Step 10a — INV-097): reference them and use `search_docs`
  for Senzing's guidance on integrating with those systems.

**Checkpoint:** write step 13.

## 14. Senzing value restatement

Before confirming, reinforce why Senzing ER is valuable for THIS problem. Use
`search_docs(query='value proposition <use_case_category>', version='current')` and tie the
value to the bootcamper's specific data, sources, and outcomes (not generic marketing). If
integration targets exist, explain how Senzing fits alongside them as a foundational layer.

**Checkpoint:** write step 14.

## 15. Get confirmation

👉 **Does this accurately capture your problem and approach?**

*(Internal: end the turn and wait.)* **Checkpoint:** write step 15.

## 16. Generate the stakeholder summary

Always produce `docs/stakeholder_summary_module1.md` — no gate, no 👉 question. It covers problem,
approach, data sources, key findings, next steps, and ROI considerations, filled with Module 1
context from `docs/business_problem.md`. (The Kiro `templates/stakeholder_summary.md` port is a
later phase; compose the summary directly for now.) Do not ask whether to create it; announce it
as a statement in the end-of-module summary (Step 17) — noting the file was created and where to
find it — via the module-completion "Files produced" list. **Checkpoint:** write step 16.

## 17. Module completion and transition to Module 2

Run the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md` (update progress, append the Module 1 recap
section to `docs/bootcamp_recap.md`, and present the end-of-module summary), then ask the single
transition question.

After the business problem is defined, the next module in your selected sequence continues the
bootcamp:

👉 **Are you ready to move on to the next module: {next module name}?**

**Checkpoint:** write step 17. On module completion set `current_step` to `null`.

**Success indicator:** ✅ Clear problem statement + identified data sources + defined success
metrics + bootcamper confirmation + `docs/business_problem.md` created + Module 1 recap section
appended.
