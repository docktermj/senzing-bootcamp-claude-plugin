# Enumerate `selected_modules` explicitly on the Core path

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamper chose **1. Core bootcamp** at Bootcamp preparation Step 1, which the same
step documents as "every module, in order, from preparation through graduation". When the
consolidated preferences were written in Step 6, `selected_modules` in
`config/bootcamp_preferences.yaml` and `config/bootcamp_progress.json` contained
`system_verification` and `truthset_visualization` but **omitted
`entity_resolution_concepts`**.

Onboarding therefore handed off straight to `business_problem` (Discover the Business
Problem). The Entity Resolution Concepts primer never appeared in the journey map, never
ran, and nothing told the bootcamper a module had been dropped. They expected Core to run
literally every module as documented, and the omission was silent.

## Root cause

`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:77-78` — the Core branch of
Step 1 is prose only:

```markdown
- **Core** → all modules are selected, in order. **Hold** `path: core` and the full ordered
  `selected_modules` list for the consolidated write in Step 6; skip Step 2.
```

"All modules are selected, in order" never names them. The only place the full set exists is
the human-readable module-list table above it (`SKILL.md:47-58`), whose rows carry display
names and a "Maps to" skill directory — not the `selected_modules` state tokens. The Step 6
YAML example (`SKILL.md:235-237`) shows `entity_resolution_concepts` annotated
`# optional — present only if selected`, which reads as *exclude unless chosen* and pulls in
the opposite direction on the Core path.

So the agent must derive an eleven-token ordered list by translating display names into state
tokens with no canonical list to copy. That derivation dropped the one module labeled
"optional" — exactly the failure the reasoning invites. The skill's documented *behavior* is
correct; the skill gives the agent no literal artifact to reproduce it from.

The same gap makes the Customized path fragile: Step 2 (`SKILL.md:94-104`) also resolves a
selection to an ordered token list by prose rule.

## Proposed change

Replace the derivation with an enumerated, copyable list.

1. **Add the canonical ordered token list to Step 1's Core branch**, verbatim and complete,
   so the Core path is a copy rather than a translation:

   ```yaml
   selected_modules:
     - bootcamp_preparation
     - entity_resolution_concepts
     - business_problem
     - sdk_setup
     - system_verification
     - truthset_visualization
     - data_collection
     - data_quality_mapping
     - data_processing
     - query_visualize_discover
     - graduation
   ```

   State explicitly that on the Core path **all three deselectable modules
   (`entity_resolution_concepts`, `system_verification`, `truthset_visualization`) are
   included** — "optional" describes what Customized may drop, never what Core omits.

2. **Add the state token to the module-list table** (`SKILL.md:47-58`) as a column, so
   display name → token is a lookup, not an inference. Keep it internal (INV-012/INV-079):
   the table is already documented as not being rendered to the bootcamper.

3. **Fix the misleading annotation** in the Step 6 example (`SKILL.md:237`): change
   `# optional — present only if selected` to note that Core always includes it and only
   Customized may omit it.

4. **Verify before handing off.** At the end of Step 6, check the written
   `selected_modules` against the canonical list when `path: core`; if any module is
   missing, correct the file before the handoff in Step 7 rather than after the next module
   has started. This is a self-check, not a bootcamper-facing gate.

## Acceptance criteria

- [ ] On the Core path, `selected_modules` in both `config/bootcamp_preferences.yaml` and
      `config/bootcamp_progress.json` contains all eleven tokens above, in that order.
- [ ] `entity_resolution_concepts` is present on every Core run, and the primer runs
      immediately after Bootcamp preparation and before Discover the Business Problem.
- [ ] The journey map shown at the first module start lists Entity Resolution Concepts.
- [ ] Step 1's Core branch contains the literal ordered token list; no step asks the agent
      to derive it from display names.
- [ ] The Step 6 YAML example no longer implies `entity_resolution_concepts` is excluded by
      default.
- [ ] A Customized run that selects "none" still yields exactly the eight required modules,
      in order — the enumeration does not leak Core's optional modules into Customized.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — enumerate the Core
  token list in Step 1; add the state-token column to the module table; correct the Step 6
  example annotation; add the pre-handoff self-check.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Core path selection omitted the
  optional 'Entity Resolution Concepts' module" (2026-07-25, Module Bootcamp preparation;
  `Source: bootcamper-reported`)
- Priority: High
- Related specs: `specs/customizable-module-selection.md` (established the Core/Customized
  paths and INV-076), `specs/entity-resolution-module-zero.md`,
  `specs/guarantee-quiz-offer-is-presented.md` (INV-112 — same defect shape one level down:
  a documented-as-guaranteed step that was not reliably reached).
