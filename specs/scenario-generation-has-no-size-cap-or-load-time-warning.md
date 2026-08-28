# Scenario generation has no size cap and no load-time warning, so a Bootcamper can scale to 94,000 records without being told what that costs

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A Bootcamper on the generated-scenario path was offered a 3-source, ~7,081-record scenario, said it
"doesn't seem enough" against a claimed 100,000-record POC license, and was given a 5-source
**~93,999-record** scenario instead — with no statement that loading and resolving that volume would
take substantially longer than the rest of the bootcamp assumes.

`module-01-business-problem/phase1-discovery.md:151-160` (**Step 4a, Business Case Offer:
acceptance handling**) tells the guide to *"generate a complete scenario in-session"* and to
**"Validate invariants** before recording", and the invariants it names are about mapping complexity
and use-case category. **Nothing in the step bounds record volume, and nothing ties volume to a
time expectation.** Step 4b decides CORD versus synthetic; it does not decide size either.

**Why the absence matters more than a slow load.** A bootcamp is a guided walkthrough meant to
finish in a session. The cost of an oversized scenario is not paid in Module 1 — it is paid in
Modules 4, 6 and 7, where the data is collected, loaded, redo-drained and queried, by which point
the choice is many steps behind and expensive to reverse. The Bootcamper who made the choice was
never told there was a cost to weigh.

⚠️ **This entry and `license-record-limit-has-a-detected-only-contract-nothing-enforces` are the
same session and compound.** The 94,000-record scenario was sized against a **stated** 100,000-record
entitlement that had never been applied; the install's measured limit was **500**. So the scenario
was scaled toward a ceiling that did not exist, and the step that would have caught it — Module 4's
Step 8a License Key gate — is *suppressed* when `license_record_limit` exceeds the dataset size.
Fixing either one alone leaves the other's failure reachable.

## Root cause

Step 4a validates the scenario's **shape** (mapping complexity, category coverage, non-empty
description) and never its **size**, because the generated-scenario path was designed around
producing a realistic problem rather than a loadable one. The load-time consequence is owned by
later modules, and no signal travels backward: Module 4's Step 8b judges load time from the
collected total, and Module 6 sizes the loader from the production-volume tier, but by then the
scenario is fixed.

The Bootcamper's own framing names the missing thing exactly: *"keep it at 10k max if they go over
send them a warning just that it will take them longer."*

## Proposed change

1. **Give Step 4a a default size ceiling** for generated scenarios — the reporter proposed
   **~10,000 records** — stated as the default the guide generates to unless the Bootcamper asks for
   more. This is a default, not a cap: the point is that the larger number is chosen rather than
   drifted into.
2. **Warn before generating, not after.** When a Bootcamper asks for a scenario above the ceiling,
   say plainly, in one line, that the larger volume will make Data collection and Data processing
   take noticeably longer, and then generate what they asked for. ⛔ **Do not refuse and do not
   re-ask** — INV-006 forbids re-asking a settled question, and the Bootcamper's choice stands.
3. **Do not tie the ceiling to the license limit at this step.** Module 1 has not measured the
   license and INV-093 forbids a license prompt here; the sibling spec covers the licensing half.
   The ceiling is about bootcamp duration, which is knowable now.
4. ⛔ **Do not state a wall-clock figure.** Load time depends on the workstation, the database and
   the language, none of which Module 1 knows. Say "noticeably longer" and name the modules that
   absorb it, rather than inventing a minutes figure the run will contradict.

## Acceptance criteria

- [ ] `phase1-discovery.md` Step 4a states a default generated-scenario size ceiling and generates
      to it unless the Bootcamper asks for more.
- [ ] Asking for more produces a one-line time-cost statement naming the modules that absorb it,
      **before** the scenario is generated, and then generates the requested size.
- [ ] The warning is not a 👉 question and does not re-ask a settled choice (INV-006, INV-251).
- [ ] No wall-clock or records-per-second figure appears in the shipped text.
- [ ] A test asserts Step 4a names both the ceiling and the over-ceiling warning, so a later edit
      cannot drop one and keep the other. Stdlib only, no `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 4a at
  `:151-160`
- `tests/` — a guard for the ceiling and the warning

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: No warning about load time when
  scaling a generated scenario near the license limit" (2026-08-25, Module: Discover the Business
  Problem, Priority: Medium; `Source: bootcamper-reported`). A human hit this and stopped to report
  it, including the remedy in their own words.
- Priority: **Medium**, as filed. Nothing breaks and the scenario is usable; the cost is a bootcamp
  that runs far longer than intended, decided at a step that never surfaced the trade-off.
- MCP re-check: **n/a (no Senzing fact).** The defect is a missing bound and a missing statement in
  this plugin's own scenario-generation step. The "100,000-record POC license" in the report is a
  **Bootcamper claim**, not a server fact, and is not relied on here — the sibling spec covers what
  went wrong with it. `get_capabilities` was called this session to date the triage: server
  **1.33.0**, 2026-08-28.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/license-record-limit-has-a-detected-only-contract-nothing-enforces.md` (the
  same session's other half — the ceiling this scenario was sized against did not exist);
  `specs/generated-dataset-is-sized-before-anything-measures-the-license.md` (the mirror-image
  defect: sizing *down* on an unmeasured license, already implemented);
  `specs/load-time-warning-ignores-the-license-cap-decided-one-step-earlier.md` (Module 4's Step 8b
  load-time warning, already implemented — downstream of this choice)

## Deviations from this spec, and why (2026-08-28)

**None on content.** The root cause was re-confirmed in the file before anything changed: Step 4a at
`phase1-discovery.md:151-175` validates category, source count, cross-source mapping divergence and
quality variation, and no clause bounds record volume or mentions a time cost.

**MCP re-check: n/a, re-confirmed rather than assumed.** The change asserts no Senzing fact — it adds
a size default and a time-cost statement to this plugin's own generation step. The report's
"100,000-record POC license" is a Bootcamper claim, not a server fact, and is deliberately not relied
on; its sibling spec covers what went wrong with it. `get_capabilities` was called this session to
date the run: server **1.33.0**, 2026-08-28.

⚠️ **Two criteria are implemented but NOT runtime-verified**, and are disclosed rather than ticked:
that a live run generates to the ceiling by default, and that it emits the warning *before*
generating a larger scenario. Both describe what a conversational step does in a turn, which no
offline suite can assert (INV-108). Verifying them needs a `dry-run` phase-3 walk through Module 1's
generated-scenario path, asking for a scenario above the ceiling.

**The guard asserts three absences as well as two presences**, because the spec's ⛔ items are as
load-bearing as its asks: no wall-clock figure, no licensing tie, and no gate. The gate assertion is
the one most likely to be eroded by a well-meaning edit — "warn them" reads naturally as "ask them" —
so it is pinned explicitly and negative-controlled.

**One invariant is DEFERRED** — see the ledger entry. Only the maintainer may sign off on wording.
