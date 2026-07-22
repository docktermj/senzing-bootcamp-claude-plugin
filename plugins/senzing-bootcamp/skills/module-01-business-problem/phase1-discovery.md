# Module 1, Phase 1: Discovery (steps 1–6)

Discovery and gap-filling. Follow the ground rules. `🛑`/`⛔` are internal directives: do not
render them; signal a stop by ending the turn on the single 👉 question and waiting.

## 1. Data privacy reminder (statement, no question)

"Before we proceed, a quick reminder about data privacy. We'll be working with potentially
sensitive data. Please ensure you have permission to use it, and consider anonymizing any PII
for testing. We'll set up proper security measures as we go."

**Checkpoint:** write step 1.

## 2. Offer the design pattern gallery (separate question)

👉 **Would you like to see examples of common business problems that entity resolution can solve?**

**Checkpoint:** write step 2.

## 3. If they want patterns

Present an entity-resolution design-pattern gallery (recognized use-case categories below;
pull real-world examples via `search_docs`: the full pattern gallery is a later porting
phase). For each: the problem it solves, the goal, typical data sources, business value.

Because this content is MCP-sourced, make that visible so the bootcamper can trust it is real,
not fabricated: add a brief inline attribution to the gallery — e.g. a one-line "*Sourced from
Senzing docs via the MCP server.*" note (or a per-item "(via Senzing docs)") — per the
visible-attribution convention in `../bootcamp-onboarding/ground-rules.md`. Keep it lightweight,
honor verbosity (suppress it at the `minimal` preset), and attribute to the MCP server only what
an MCP tool actually produced.

👉 **Do any of these patterns match your situation?**

If they pick one, use it as a template (pre-fill source types, suggest matching criteria,
adapt to their context). If none fit, they can accept the Business Case Offer in Step 4.

**Checkpoint:** write step 3.

## 4. Discovery prompt: three selectable paths

First state a one-line recommendation (a statement, not part of the lead question; honor
verbosity — suppress it at the `minimal` preset), then present the neutral lead question and the
numbered choices, ending the turn on the 👉:

For the most relevant bootcamp, I recommend describing your own business problem if you have one —
you'll work through *your* real data. If you don't, I can generate a realistic scenario instead.

👉 **How would you like to define the business problem? Reply with a number:**

1. **Describe a real business case** — tell me about the problem you're solving: what data you
   have, where it comes from, and what success looks like.
2. **Adopt a design pattern** (if you picked one in Step 3) — how does it apply: what data, from
   where, and what does success look like?
3. **I don't have my own data — generate a scenario for me** — I'll create a realistic,
   multi-source scenario so you can complete the full bootcamp (the Business Case Offer).

*(Internal: end the turn on this 👉 choice and wait. Do NOT generate a scenario before the
bootcamper explicitly accepts option 3.)*

**Checkpoint:** write step 4.

### 4a. Business Case Offer: acceptance handling (branch)

- **Accepted:** generate a complete scenario in-session: a non-empty problem description,
  exactly one use-case category from the recognized set (Customer 360, Fraud Detection, Data
  Migration, Compliance, Marketing, Healthcare, Supply Chain, KYC, Insurance, Vendor MDM), and
  a non-empty definition of success. If a pattern was picked in Step 3, the category must match
  it. Decide CORD vs. synthetic data per Step 4b. **Validate invariants** before recording: at
  least two distinctly named data sources, each with ≥1 record; the data is
  mapping-complexity-rich (needs at least one transformation when mapped to the Senzing Entity
  Specification); category is in the recognized set; problem and success are non-empty. On
  success, record artifacts in Phase 2 Step 11 (write `docs/business_problem.md` with the
  generated marker, and each source into `config/data_sources.yaml`), then continue at Step 5.
- **Declined:** continue with their own description (Path 1/2); do not generate a scenario.
- **Generation failed / invariants violated:** tell the bootcamper it couldn't complete, fall
  back to their own description, no generated `docs/business_problem.md`.

*(The Kiro helper `business_case_offer.py` encodes these invariants; the script port is a later
phase: validate them directly for now.)*

**Checkpoint:** write step 4a.

### 4b. CORD sourcing for the generated scenario (via MCP)

Treat the Senzing MCP server as the ONLY source of CORD facts: never training data. Call
`get_sample_data` and/or `search_docs(query='CORD datasets: names, contents, and availability
for entity resolution scenarios')` to learn which datasets exist and what they contain. Present
values exactly as returned. Wait up to 30s; retry once.

- **Fitting CORD dataset returned:** back the scenario with it, provenance `cord`.
- **None fit:** synthetic data, provenance `synthesized`.
- **Timeout/unreachable after one retry:** omit CORD facts, tell the bootcamper they're
  unavailable, use synthetic data (`synthesized`).

Either way the data must satisfy the Step 4a invariants.

**Checkpoint:** write step 4b.

## 5. Infer details from their response

Extract six categories: **A. Record types** (people/orgs/both); **B. Source count and names**;
**C. Problem category** (map to the recognized set); **D. Matching criteria** (attributes,
quality concerns); **E. Desired outcome** (format, frequency, integration); **F. Integration
targets** (specific software, pipeline mentions). Use "not yet determined" when unclear.

**Checkpoint:** write step 5.

### 5a. Record-count threshold check (compute-only — no license prompt here)

Compute the total record count across the mentioned sources and read `license_record_limit` from
`config/bootcamp_progress.json` (present only if a custom license was configured in a prior
session; normally absent at this point):

- **Present and > 0:** if the total exceeds it, the bootcamper will likely need a Senzing License
  Key — record `license_guidance_deferred: true` in `config/bootcamp_preferences.yaml`. Otherwise
  leave it unset. Either way, proceed to Step 6.
- **Present and = 0** (no cap): no license concern → proceed to Step 6.
- **Absent/null:** compare the total against the built-in evaluation capacity, confirmed via the
  Senzing MCP server (never a hardcoded figure). If the total exceeds it, record
  `license_guidance_deferred: true`; otherwise leave it unset. Either way, proceed to Step 6.

**The bootcamp does not ask about a Senzing License Key here.** The single, volume-gated License
Key prompt is presented once — at the start of Data collection (Module 4), after the actual data
volume is known and before any load — per INV-093. This step only records whether the anticipated
volume looks likely to exceed the limit, so Module 4's gate can pick it up (`license_guidance_deferred`).

**Checkpoint:** write step 5a to `config/bootcamp_progress.json`.

## 6. Confirm inferred details and fill gaps

Ask about only ONE undetermined item per turn; queue the rest for later turns. Don't re-ask
what they already covered.

### 6a. Present summary and confirm

"Based on what you've described: **Problem:** [...]; **Record types:** [...]; **Data sources:**
[...]; **Key attributes:** [...]; **Desired outcome:** [...]."

👉 **Does that summary capture your situation accurately?**

*(Internal: end the turn and wait.)* **Checkpoint:** write step 6a.

### 6b–6d. Ask only about "not yet determined" items, one per turn

- 6b (record types): 👉 **Which records are you working with? Reply with a number:** (1) people, (2) organizations, (3) both.
- 6c (source count): 👉 **How many distinct data sources will we work with?**
- 6d (desired outcome): 👉 **What does the end result look like? Reply with a number:** (1) a clean master list, (2) an API, (3) reports, (4) something else.

*(Internal: end each turn on its question and wait; checkpoint after each.)* When no
undetermined items remain, Phase 1 is complete — proceed to Phase 2 (load
`phase2-document-confirm.md`).

(The software-integration and deployment-target questions were relocated to **Bootcamp
preparation** — see `../bootcamp-preparation/SKILL.md` — where all setup questions live (INV-088).
Their answers are persisted in `config/bootcamp_preferences.yaml` (`integration_targets`,
`deployment_target`/`cloud_provider`) and read from there by the problem statement (Phase 2) and by
graduation; do not re-ask them here (INV-006).)
