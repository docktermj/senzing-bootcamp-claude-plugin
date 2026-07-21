# Module 2 license clarity: "Senzing License Key" terminology and a full post-request install flow

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two related clarity gaps in Module 2's license-configuration step:

1. **Ambiguous "license" terminology.** Step 5 asks "Do you have a Senzing
   license?" The phrase "Senzing license" is easily confused with the Senzing **End
   User License Agreement (EULA)** accepted during SDK install — also a "license."
   The bootcamper suggests "Senzing License Key" to make clear this is a
   runtime-capacity license (record limit), not the install-time EULA.
2. **Under-explained post-request flow.** When the bootcamper chooses option 4 ("No
   — request a free evaluation license now through the bootcamp"), the request is
   submitted but the full sequence after that is not laid out. The bootcamper wants
   it explicit: (1) wait for the email, (2) download the license from the email, (3)
   the bootcamp prompts for the path to the file containing the Base-64 text, (4) the
   bootcamp generates a `.lic` license from that Base-64 text.

## Root cause (confirmed)

- "Senzing license" is used for the runtime-capacity license at
  `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:393-398` (four-option
  form), `:402-406` (three-option form), `:337`, `:528`, while the EULA is named
  "Senzing End User License Agreement (EULA)" at `:183-197` (Step 3, Phase 2). The
  two share the word "license" and are never cross-referenced, so they can be
  conflated.
- After a successful in-flow request, the module only says to check email and follow
  Step 5d: `SKILL.md:519-521` ("instruct the bootcamper to check the email … once
  they confirm receipt, follow the Step 5d configuration steps"). It does **not**
  enumerate wait → download → provide Base-64 file path → decode to `licenses/g2.lic`
  → wire `LICENSEFILE` (Step 5d, `:537-549`) → detect the record limit (Step 5e,
  `:551-582`). Gap: Step 5d covers only the `.lic`-already-present case and does not
  restate the Base-64 decode command from Step 5c (`:416-440`), so an email-delivered
  Base-64 key has no explicit decode instruction on the 5c→5d path.

## Proposed change

1. **Terminology.** In `module-02-sdk-setup/SKILL.md` (Steps 5, 5a–5d and any other
   bootcamper-facing text), use "Senzing License Key" (or "license key") for the
   runtime-capacity license, reserving "EULA" / "End User License Agreement" for the
   install-time agreement. E.g. change "Do you have a Senzing license?" (`:393-398`,
   `:402-406`) to "Do you have a Senzing License Key?", and adjust the evaluation-
   license explanation (`:335-343`) wording to match. Keep questions single-meaning
   (INV-008) and options numbered (INV-051).
2. **Post-request flow.** After the in-flow `submit_feedback` `license_request` path
   (option 4 → Step 5c, `:511-535`), add explicit guidance walking through: (a) wait
   for the Senzing email, (b) download the license file/key from the email, (c)
   prompt for the path to the file containing the Base-64 license text, (d) decode
   that Base-64 text to `licenses/g2.lic` and wire `LICENSEFILE` (Step 5d), then (e)
   detect the record limit (Step 5e). Make clear the bootcamp can continue on the
   built-in evaluation license meanwhile and apply the emailed key whenever it
   arrives. Ensure the 5c→5d path includes the Base-64 decode command for an
   email-delivered key.

## Acceptance criteria

- [ ] The runtime-capacity license is consistently called "Senzing License Key" in bootcamper-facing Module 2 text; "EULA" / "End User License Agreement" is used only for the install-time agreement, and the two are no longer conflatable.
- [ ] The Step 5 question reads "Do you have a Senzing License Key?" and stays single-meaning (INV-008) with numbered options (INV-051).
- [ ] After an in-flow license request, the module explains the full post-request sequence (wait → download → provide Base-64 file path → decode to `licenses/g2.lic` → wire `LICENSEFILE` → detect record limit), including the Base-64 decode command on the 5c→5d path.
- [ ] It is stated that the bootcamp continues on the built-in evaluation license until the emailed key is applied.
- [ ] License establishment still satisfies INV-036; Senzing facts/figures still come from the MCP server (no hardcoded record limits).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — terminology across Step 5 (`:337`, `:393-398`, `:402-406`, `:528`, `:335-343`); post-request flow after Step 5c (`:511-535`), reconciled with Step 5d (`:537-549`) and Step 5e (`:551-582`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Use 'Senzing License Key' to distinguish runtime-capacity license from the EULA" (2026-07-18, Module 2); "After in-flow license request (option 4), explain the full post-request install flow" (Module 2).
- Priority: Medium.
- Related specs: `license-request-option.md` (added option 4 / the in-flow request — this extends it with terminology and post-request guidance).
