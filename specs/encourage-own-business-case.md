# Encourage describing your own business case over accepting the generated scenario

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At Module 1 Step 4, the three discovery paths are presented as equally weighted, neutral
options. Because "Accept the Business Case Offer — I'll generate a realistic, multi-source
scenario" sits alongside "Describe a real business case" with no stated preference, it is
too easy/tempting to opt for the generated scenario. The bootcamper flagged that the
bootcamp is far more relevant when a bootcamper works through their *own* data, and asked
that describing your own case be framed as the encouraged default and the generated
scenario as an explicit fallback.

## Root cause

By design, `phase1-discovery.md` Step 4 presents all three paths neutrally:

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:44-51`
  — the 👉 lead question ("How would you like to define the business problem?") plus the
  numbered list: (1) Describe a real business case, (2) Adopt a design pattern, (3) Accept
  the Business Case Offer — with no nudge toward option 1 and no "fallback" framing on
  option 3.

No invariant requires neutrality *between* the options — INV-051 requires only that the
**lead question** be neutral and the choices not be joined with "or". A one-line
recommendation stated *before* the 👉 question (a statement, not part of the lead
question) and clearer option labels do not violate INV-051, INV-008, or INV-007 (the
bootcamper still makes the choice; the plugin does not assume it). INV-034 (the
bootcamper describes the business issue) is reinforced by this change.

## Proposed change

In `phase1-discovery.md` Step 4:

- **Add a one-line nudge before the 👉 question** (a statement): e.g. "For the most
  relevant bootcamp, I recommend describing your own business problem if you have one —
  you'll work through *your* real data. If you don't, I can generate a realistic scenario
  instead." Honor verbosity (suppress at the `minimal` preset).
- **Reframe option 3 as an explicit fallback** — e.g. "3. **I don't have my own data —
  generate a scenario for me** — I'll create a realistic, multi-source scenario so you can
  complete the full bootcamp." Keep option 1 as the encouraged default and option 2
  (adopt a design pattern) unchanged.
- Keep the lead question neutral and single-meaning (INV-008/INV-051); keep the numbered
  list; do not join choices with "or".
- Leave Step 4a/4b acceptance-handling logic unchanged (it already branches on which path
  the bootcamper picks).

## Acceptance criteria

- [ ] Step 4 states a one-line recommendation to describe your own business case *before* the 👉 question, suppressed at the `minimal` verbosity preset.
- [ ] Option 3 is labeled as an explicit fallback for bootcampers without their own data; option 1 (own case) reads as the encouraged default.
- [ ] The 👉 lead question stays neutral and single-meaning; choices are a numbered list, never joined with "or" (INV-008/INV-051).
- [ ] The bootcamper still chooses; no answer is assumed (INV-007). Step 4a/4b branching still works for all three paths.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — add the pre-question nudge and reframe option 3 as a fallback (`:40-56`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Business Case Offer is too easy to accept over describing your own scenario" (2026-07-18, Module: business_problem).
- Priority: Medium.
- Related specs: none.
