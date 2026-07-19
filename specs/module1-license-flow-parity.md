# Bring Module 1's license flow to parity with Module 2: "License Key" wording, file-path capture + filename hint, and a post-request confirmation gate

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 1's license-guidance flow (`phase1-discovery.md` Steps 5b–5e) lags behind the
richer Module 2 license flow (already delivered by `module2-license-clarity.md`) in three
ways the bootcamper hit in one session:

1. **Imprecise terminology.** The pinned question asks "👉 Do you already have a Senzing
   license?" — bare "license" is ambiguous (it collides with the install-time EULA). It
   should read "Senzing License Key".
2. **No confirmation after an in-flow request.** After requesting a free evaluation
   license via `submit_feedback` (Step 5d path 1), the flow proceeds without checking
   whether the email arrived and the key was installed — so a bootcamper can be left
   stranded without a working license going into later modules.
3. **Capture prompt only accepts a pasted base64 string.** Step 5c asks only for the
   base64 string; it does not offer the (simpler, less error-prone) option of pointing at
   a downloaded license file, and gives no hint about the file's likely default name.

## Root cause

Confirmed in `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md`:

- **Terminology:** Step 5b question is "👉 **Do you already have a Senzing license?**"
  (`:119`). Module 2 was already updated to "Senzing License Key" by
  `module2-license-clarity.md` (implemented) — Module 1 was not, so the two modules are
  now inconsistent (violates INV-003 coherence).
- **No confirmation gate:** Step 5d lists the request paths (`:141-162`); after path 1
  (in-flow `submit_feedback`) the instruction is only "Act on the choice; defer → Step 5e"
  (`:162`). There is no gate confirming the emailed key arrived/installed before Step 6's
  summary-confirmation (`:183`).
- **String-only capture:** Step 5c step 1 is "Ask for the Base64-encoded license string"
  (`:125`), decoding to `licenses/g2.lic` (`:126`). No file-path alternative, no filename
  hint. Module 2 already prompts for "the path to the file containing the Base-64 license
  text" (per `module2-license-clarity.md`), so Module 1 is behind.

## Proposed change

In `phase1-discovery.md` (reuse Module 2's established wording/flow for consistency):

1. **Terminology.** Change Step 5b's question to the pinned form "👉 **Do you already have
   a Senzing License Key?**" and use "Senzing License Key" consistently across Steps 5b–5e.
   Keep it single-meaning (INV-008) and, as a pinned gate, verbatim (INV-056).
2. **File-path capture + filename hint.** In Step 5c, offer both capture options — paste
   the base64 string, or give the path to a downloaded license file — as a neutral lead
   question with a numbered list (INV-051), decoding/copying to `licenses/g2.lic` either
   way. When asking for the file path, hint the likely default filename (`senzing-license.txt`).
3. **Post-request confirmation gate.** After Step 5d path 1 (in-flow `submit_feedback`
   request), insert a pinned confirmation gate (INV-056) asking whether the evaluation
   email arrived and the key has been installed/applied, before continuing to Step 6. Make
   clear the bootcamp can continue on the built-in evaluation license meanwhile and apply
   the emailed key whenever it arrives (as Module 2 already states). Keep it a single
   yes/no gate (INV-008), its own yielding turn (INV-005/INV-006).

Prefer pointing at / reusing Module 2's flow rather than duplicating capacity figures —
license figures still come from MCP at runtime, never hardcoded.

## Acceptance criteria

- [ ] Steps 5b–5e call the runtime-capacity license the "Senzing License Key"; the Step 5b gate reads "👉 Do you already have a Senzing License Key?" and is pinned verbatim (INV-056), single-meaning (INV-008).
- [ ] Step 5c offers both the base64-string paste and the downloaded-file-path capture options (numbered list, INV-051), and hints the likely default filename `senzing-license.txt` when asking for the path.
- [ ] After an in-flow (Step 5d path 1) license request, a pinned confirmation gate asks whether the email arrived and the key is installed before any later step runs; it is stated that the bootcamp continues on the evaluation license until the key is applied.
- [ ] Module 1 and Module 2 license terminology and capture options are consistent (INV-003); license establishment still satisfies INV-036; no capacity figure is hardcoded (MCP-sourced).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 5b terminology + pinned wording (`:119`); Step 5c dual capture + filename hint (`:123-130`); Step 5d post-request confirmation gate (`:141-164`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "License flow — wrong terminology, and no confirmation gate before proceeding" (2026-07-18, Module: business_problem); "License-capture prompt should also accept a downloaded license file path" (2026-07-18, business_problem); "Hint the likely default license filename when asking for its path" (2026-07-18, business_problem).
- Priority: Medium.
- Related specs: `module2-license-clarity.md` (established the "License Key" terminology and file-path/post-request flow in Module 2 — this brings Module 1 to parity), `license-request-option.md` (the in-flow request path this gates).
