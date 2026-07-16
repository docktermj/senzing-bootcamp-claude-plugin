# Surface the in-flow evaluation-license request as a choice on the license question

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 2 Step 5b's numbered 👉 question — "Do you have a Senzing license?" —
offers three choices: (1) a `.lic` file, (2) a Base64 key, (3) No — I need to
obtain one. The in-flow option to **request a temporary evaluation license through
the bootcamp** (the MCP `submit_feedback` `license_request` path, which avoids
waiting for email) is described only in Step 5a prose and handled at the Step 5c
no-license branch; it is **not** a selectable option on the question itself. A
bootcamper skimming the numbered options may not realize they can obtain a real
evaluation license directly through the bootcamp without leaving the flow.

## Root cause

`module-02-sdk-setup/SKILL.md:370-379` (Step 5b) presents exactly three fixed
options and does not include the in-flow request. The in-flow path is documented
at `:347-354` (Step 5a, option 1) and reached only indirectly via option 3 → the
Step 5c no-license branch (`:422+`). Its availability is already conditioned on the
`submit_feedback` tool being enabled and reported by the MCP server (`:351`) — the
same availability concept the fourth option would reuse.

## Proposed change

When the `submit_feedback` tool is available (per `get_capabilities`, the check
already referenced at Step 5a/5c), present Step 5b as **four** options, adding a
distinct fourth choice — e.g. "(4) No — request a free evaluation license now
through the bootcamp." Keep option 3 as the general no-license path (an existing
license obtained elsewhere / Senzing support). Route the fourth option to the
existing in-flow `submit_feedback` `license_request` handling at Step 5c. When
`submit_feedback` is unavailable, fall back to the current three options. Pin both
the three-option and four-option forms verbatim in the skill.

## Acceptance criteria

- [ ] When `submit_feedback` is reported available, Step 5b presents a fourth option to request an evaluation license in-flow, and selecting it runs the existing `submit_feedback` `license_request` path (no new mechanism invented).
- [ ] When `submit_feedback` is unavailable, Step 5b shows the current three options (graceful fallback).
- [ ] Options are mutually exclusive and distinctly worded (option 3 vs. option 4); the question keeps the neutral-lead + numbered-list format (INV-051) and its wording is pinned verbatim for both forms (INV-056).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5b: add the availability-gated fourth option, pin both forms, and route option 4 to the existing Step 5c in-flow `license_request` handling.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Offer \"request an evaluation license via the bootcamp\" as a choice on the license question" (2026-07-16, Module 2 Step 5b).
- Priority: Medium.
- Related specs: `interaction-or-questions.md` (INV-051), `onboarding-explore-gate-wording.md` (INV-056 pinned gate wording).
