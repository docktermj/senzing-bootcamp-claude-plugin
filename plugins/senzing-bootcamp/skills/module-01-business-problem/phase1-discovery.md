# Module 1, Phase 1: Discovery (steps 1–9)

Discovery and gap-filling. Follow the ground rules. `🛑`/`⛔` are internal directives: do not
render them; signal a stop by ending the turn on the single 👉 question and waiting.

## 1. Initialize version control (optional)

Check whether this is already a git repo:

```bash
git rev-parse --git-dir 2>/dev/null   # Linux/macOS
```

- **Already a repo:** skip the question, checkpoint, proceed to Step 2.
- **Not a repo:** ask: 
  👉 **If you don't know what "git" is, just skip this. It's optional: would you like me to initialize a git repository for version control?**

  *(Internal: end the turn here and wait.)* If yes, `git init`; if no, skip. Then checkpoint.

**Checkpoint:** write step 1 to `config/bootcamp_progress.json`.

## 2. Data privacy reminder (statement, no question)

"Before we proceed, a quick reminder about data privacy. We'll be working with potentially
sensitive data. Please ensure you have permission to use it, and consider anonymizing any PII
for testing. We'll set up proper security measures as we go."

**Checkpoint:** write step 2.

## 3. Offer the design pattern gallery (separate question)

👉 **Would you like to see examples of common business problems that entity resolution can solve?**

**Checkpoint:** write step 3.

## 4. If they want patterns

Present an entity-resolution design-pattern gallery (recognized use-case categories below;
pull real-world examples via `search_docs`: the full pattern gallery is a later porting
phase). For each: the problem it solves, the goal, typical data sources, business value.

👉 **Do any of these patterns match your situation?**

If they pick one, use it as a template (pre-fill source types, suggest matching criteria,
adapt to their context). If none fit, they can accept the Business Case Offer in Step 5.

**Checkpoint:** write step 4.

## 5. Discovery prompt: three selectable paths

Present the neutral lead question, then the numbered choices, ending the turn on the 👉:

👉 **How would you like to define the business problem? Reply with a number:**

1. **Describe a real business case** — tell me about the problem you're solving: what data you
   have, where it comes from, and what success looks like.
2. **Adopt a design pattern** (if you picked one in Step 4) — how does it apply: what data, from
   where, and what does success look like?
3. **Accept the Business Case Offer** — I'll generate a realistic, multi-source scenario so you
   can complete the full bootcamp without supplying your own.

*(Internal: end the turn on this 👉 choice and wait. Do NOT generate a scenario before the
bootcamper explicitly accepts option 3.)*

**Checkpoint:** write step 5.

### 5a. Business Case Offer: acceptance handling (branch)

- **Accepted:** generate a complete scenario in-session: a non-empty problem description,
  exactly one use-case category from the recognized set (Customer 360, Fraud Detection, Data
  Migration, Compliance, Marketing, Healthcare, Supply Chain, KYC, Insurance, Vendor MDM), and
  a non-empty definition of success. If a pattern was picked in Step 4, the category must match
  it. Decide CORD vs. synthetic data per Step 5b. **Validate invariants** before recording: at
  least two distinctly named data sources, each with ≥1 record; the data is
  mapping-complexity-rich (needs at least one transformation when mapped to the Senzing Entity
  Specification); category is in the recognized set; problem and success are non-empty. On
  success, record artifacts in Phase 2 Step 12 (write `docs/business_problem.md` with the
  generated marker, and each source into `config/data_sources.yaml`), then continue at Step 6.
- **Declined:** continue with their own description (Path 1/2); do not generate a scenario.
- **Generation failed / invariants violated:** tell the bootcamper it couldn't complete, fall
  back to their own description, no generated `docs/business_problem.md`.

*(The Kiro helper `business_case_offer.py` encodes these invariants; the script port is a later
phase: validate them directly for now.)*

**Checkpoint:** write step 5a.

### 5b. CORD sourcing for the generated scenario (via MCP)

Treat the Senzing MCP server as the ONLY source of CORD facts: never training data. Call
`get_sample_data` and/or `search_docs(query='CORD datasets: names, contents, and availability
for entity resolution scenarios')` to learn which datasets exist and what they contain. Present
values exactly as returned. Wait up to 30s; retry once.

- **Fitting CORD dataset returned:** back the scenario with it, provenance `cord`.
- **None fit:** synthetic data, provenance `generated`.
- **Timeout/unreachable after one retry:** omit CORD facts, tell the bootcamper they're
  unavailable, use synthetic data (`generated`).

Either way the data must satisfy the Step 5a invariants.

**Checkpoint:** write step 5b.

## 6. Infer details from their response

Extract six categories: **A. Record types** (people/orgs/both); **B. Source count and names**;
**C. Problem category** (map to the recognized set); **D. Matching criteria** (attributes,
quality concerns); **E. Desired outcome** (format, frequency, integration); **F. Integration
targets** (specific software, pipeline mentions). Use "not yet determined" when unclear.

**Checkpoint:** write step 6.

### 6a. Record-count threshold check

Compute the total record count across mentioned sources. Read `license_record_limit` from
`config/bootcamp_progress.json` (Module 2 writes it):

- **Present and > 0:** if total exceeds it, license guidance required → Step 6b; else → Step 7.
- **Present and = 0** (no cap): skip license guidance → Step 7.
- **Absent/null:** compare against the built-in evaluation capacity, confirmed via the Senzing
  MCP server (never a hardcoded figure). If total exceeds it → Step 6b; else → Step 7.

### 6b. License guidance trigger (only if total exceeds the evaluation limit)

Explain that the built-in evaluation license processes a limited number of records (confirm the
figure via MCP), so a full license is needed for more.

👉 **Do you already have a Senzing license?**

*(Internal: end the turn and wait.)* Yes → 6c; No → 6d.

### 6c. Already has a license

1. Ask for the Base64-encoded license string.
2. Decode to `licenses/g2.lic`: `echo "<string>" | base64 --decode > licenses/g2.lic`
3. Add `LICENSEFILE` to the engine config PIPELINE section pointing at the file.
4. Record `license: custom` in `config/bootcamp_preferences.yaml`. Proceed to Step 7.

**Checkpoint:** write step 6c.

### 6d. Does not have a license

Consult MCP first: `search_docs(query='temporary or larger evaluation license for more than 500
records')` and present the guidance. Then call `get_capabilities` to check whether the
`submit_feedback` tool is available (wait up to 30s):

- **Available:** present all three paths.
- **Unavailable / error / no response:** omit the in-flow path, present the other two.

Paths:

1. **Request via MCP (in-flow):** *only if `submit_feedback` is available.* Invoke
   `submit_feedback` once with the `license_request` category; the license arrives by email
   with a download link. (In the Kiro Power this tool was disabled by default in `mcp.json`; in
   the Claude plugin, ensure the senzing MCP server's `submit_feedback` tool is enabled in
   Claude Code: reconcile this when finalizing the plugin's MCP config.)
2. **External channel:** email <support@senzing.com>, mention the Senzing Bootcamp, include
   name, org, expected record count, use case. Response in 1–2 business days.
3. **Apply an existing license:** follow Step 6c.

Retrieve any validity period / capacity figures from MCP at runtime; never substitute a
remembered figure.

👉 **Which would you like to do? Reply with a number:**

1. Request via the MCP server (if available).
2. Request through the external channel.
3. Apply a license you already have.
4. Defer for now.

*(Internal: end the turn and wait.)* Act on the choice; defer → Step 6e.

**Checkpoint:** write step 6d.

### 6e. Deferral

Record `license_guidance_deferred: true` in `config/bootcamp_preferences.yaml`. Note Module 2
Step 5 handles license configuration as a mandatory gate. Proceed to Step 7.

**Checkpoint:** write step 6e.

## 7. Confirm inferred details and fill gaps

Ask about only ONE undetermined item per turn; queue the rest for later turns. Don't re-ask
what they already covered.

### 7a. Present summary and confirm

"Based on what you've described: **Problem:** [...]; **Record types:** [...]; **Data sources:**
[...]; **Key attributes:** [...]; **Desired outcome:** [...]."

👉 **Does that summary capture your situation accurately?**

*(Internal: end the turn and wait.)* **Checkpoint:** write step 7a.

### 7b–7d. Ask only about "not yet determined" items, one per turn

- 7b (record types): 👉 **Which records are you working with? Reply with a number:** (1) people, (2) organizations, (3) both.
- 7c (source count): 👉 **How many distinct data sources will we work with?**
- 7d (desired outcome): 👉 **What does the end result look like? Reply with a number:** (1) a clean master list, (2) an API, (3) reports, (4) something else.

*(Internal: end each turn on its question and wait; checkpoint after each.)* When no
undetermined items remain, proceed immediately to Step 8 in the same turn (Step 8's question is
the closing question).

## 8. Software integration (separate question)

👉 **Will the results need to interface with other software (CRM, search engine, data warehouse, API gateway, downstream app)? If so, which systems?**

Record specific systems (e.g. Elasticsearch, Salesforce) for the problem statement and solution
approach. *(Internal: end the turn and wait.)* **Checkpoint:** write step 8.

## 9. Deployment target (Advanced Topics track only)

Read `track` from `config/bootcamp_preferences.yaml`.

**If `advanced_topics`:** ask (separate question):

👉 **Where do you plan to deploy the final solution? Reply with a number:**

1. A cloud hyperscaler (AWS/Azure/GCP).
2. A container platform (Kubernetes/Docker Swarm).
3. Local / on-premises.
4. Not sure yet.

Reassure: "We'll develop everything locally first; deployment is addressed in the graduation production project and migration checklist." Persist
`deployment_target` (`aws`/`azure`/`gcp`: also set `cloud_provider`; `kubernetes`/
`docker_swarm`; `local`/`on_premises`; or `undecided`). **Checkpoint:** step 9 "completed".

**If not `advanced_topics` (or unset):** skip; do not persist `deployment_target`.
**Checkpoint:** step 9 "skipped_not_applicable". Proceed to Phase 2.
