# Bootcamper-controlled module selection (Core vs Customized) and a Bootcamp preparation module

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamper wants to control which modules they go through, rather than being
locked into a fixed linear path. Concretely, across six related feedback entries
they asked for:

1. A redesigned WELCOME overview that lists the bootcamp as a **named module
   sequence**, plus a **"Customized bootcamp"** path where the bootcamper picks
   modules (subject to prerequisites) instead of only choosing Core vs Advanced.
2. Moving the **level-of-detail (verbosity)** question out of the preface into a
   new **"Bootcamp preparation"** module.
3. Adding **"Graduation"** as a mandatory module at the very end of the list.
4. Moving the **programming-language** question into the Bootcamp preparation module.
5. Moving the **initialize-git-repository** question into the Bootcamp preparation module.
6. Retiring **Module 0's own skip/keep gate** once "Entity Resolution Concepts" is
   a selectable (Optional) module — so the skip/keep decision is made once, during
   module selection, not twice.

The bootcamper's requested module list and rules (verbatim from feedback):

| Module | Rule |
|---|---|
| Bootcamp preparation | Mandatory |
| Entity Resolution Concepts | Optional |
| Business problem | Mandatory |
| SDK setup | Mandatory |
| System verification | Requires "SDK setup" |
| Truth Set visualization | Optional |
| Data collection | Mandatory |
| Data quality & mapping | Requires "Data collection" |
| Data processing | Requires "Data quality & mapping" |
| Query, Visualize and Discover | Requires "Data processing" |
| Graduation | Mandatory; Requires "Query, Visualize and Discover" |

## Root cause

Not a defect — this is a large architectural change over the current designed flow,
and it collides with several invariants (see **Conflict with invariants**).

- The preface offers only **Core Bootcamp vs Advanced Topics**, as a two-option
  numbered gate: `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:143-153`.
  There is no per-module picklist.
- The WELCOME banner + overview (which lists Modules 1-7 by name and describes the
  two tracks) is at `onboarding-flow.md:82-107`.
- The preface asks setup questions inline: verbosity `onboarding-flow.md:111-116`
  (step 4), language `onboarding-flow.md:174` (step 6), git-init
  `onboarding-flow.md:180-204` (step 6b). Step 7 (`:206-224`) does the consolidated
  preference write; step 8 (`:226`) hands off to Module 0.
- Module 0 has its **own** skip/keep gate:
  `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md:25`
  ("👉 Would you like to go through the Entity Resolution Concepts primer before Module 1?").
- Graduation is a non-numbered terminal **stage** (INV-047), not a member of any
  module list; "Truth Set visualization" is currently a mandatory step inside
  Module 3 System Verification (INV-038), not a standalone selectable module.
- The journey map covers "Modules 1–7 only" (`ground-rules.md:170-183`).

## Reconciliation decisions (resolved 2026-07-18)

The invariant conflicts below were opened to the maintainer and resolved as noted.
Implementation applies these decisions; `implement-spec` records the amendments.

- **INV-013** (all shipped modules run in order 1 → 7) — **Decision: amend for
  subsets.** Core runs all modules in order; Customized runs the *selected subset*
  in prerequisite/dependency order, with mandatory modules always included. The
  "all modules … in order" guarantee is scoped to Core (amended invariant).
- **INV-014** (modules not skipped unless requested) — **Decision: deselection is a
  requested skip.** A module left out during Customized selection counts as a
  requested skip (already permitted by INV-014's "unless requested"); reconcile the
  wording to name Customized selection as the request mechanism.
- **INV-024 / INV-026** (verbosity and language asked *in the preface*) —
  **Decision: relocate into the Bootcamp preparation module.** Amend both so the
  outcome occurs in that module, not the preface.
- **INV-025** (bootcamper asked to choose a *track*) — **Decision: replace.** The
  track question is replaced by the Core-vs-Customized choice plus module selection,
  asked in the Bootcamp preparation module (new invariant supersedes INV-025).
- **INV-072** (Module 0 offered via its **own** pinned skip/keep gate) —
  **Decision: retire the gate.** ER Concepts inclusion is driven solely by module
  selection (Core always includes it; Customized includes it only if chosen); amend
  INV-072 and delete the standalone gate.
- **INV-038** (Truth Set web-app visualization always shown in Module 3) —
  **Decision: make it a standalone Optional module.** Split "Truth Set
  visualization" out of Module 3 into its own Optional module; amend INV-038 so the
  visualization is guaranteed **only when that module is selected** (Core always
  includes it). ⚠️ This narrows INV-038's "ALWAYS sees … to verify that Senzing
  works" guarantee — a bootcamper who deselects it in Customized mode gets no
  workstation-verification visualization; surface this consequence in the overview.
- **INV-022 / INV-023** (WELCOME banner + overview) — no conflict; the banner stays
  and only the overview *content* changes.

## Proposed change

1. **Redesign the WELCOME overview** (`onboarding-flow.md:82-107`) to present the
   bootcamp as the named module sequence in the table above (keeping the
   INV-022 banner). Replace the Modules-1-7 parenthetical and the Core/Advanced
   framing.
2. **Offer two paths** in place of the current track gate (`onboarding-flow.md:143-153`):
   - **Core bootcamp** — all modules, in order.
   - **Customized bootcamp** — present the module list and let the bootcamper
     select, enforcing the prerequisite rules (a module cannot be chosen unless its
     prerequisite is also chosen). Mandatory modules are always included.
3. **Introduce a "Bootcamp preparation" module** as the first (mandatory) module,
   housing the setup questions: the path/module-selection choice itself, verbosity
   (item 2, from `onboarding-flow.md:111-116`), programming language (item 4, from
   `:174`), and git-init (item 5, from `:180-204`). The preface proper keeps only
   the WELCOME banner + overview and the administrative/MCP-health steps; the
   consolidated preference write (INV-058) moves to the end of Bootcamp preparation.
4. **Add "Graduation" as a mandatory terminal module** (item 3) in both the overview
   list and the Customized selection rules (requires "Query, Visualize and
   Discover"), reconciled with the existing graduation stage (INV-047).
5. **Retire Module 0's skip/keep gate** (item 6): delete the gate at
   `module-00-entity-resolution-concepts/SKILL.md:19-34`; run the primer iff
   "Entity Resolution Concepts" was selected (Core → always; Customized → if chosen).
6. **Split "Truth Set visualization" into a standalone Optional module** (maintainer
   decision): carve the Truth-Set web-app visualization out of Module 3 System
   Verification into its own Optional module. Core (and any selection that includes
   it) still runs the guaranteed visualization; when deselected in Customized mode no
   workstation-verification visualization runs, so amend INV-038 accordingly and note
   this consequence in the module overview.
7. **Reconcile the invariants** per the resolved decisions above.

Because items 2–6 all depend on the module-selection architecture (there is no
Bootcamp preparation module to move questions into, and no selection mechanism to
drive Module 0, until item 1 lands), they are specified together as one coherent
change.

## Acceptance criteria

- [ ] The WELCOME overview lists the bootcamp as the named module sequence (table above), with the INV-022 banner preserved.
- [ ] The bootcamper is offered **Core** (all modules in order) and **Customized** (per-module selection) as a single-meaning numbered gate (INV-005/008/051).
- [ ] In Customized, module selection enforces the prerequisite rules; mandatory modules are always included and cannot be deselected.
- [ ] A mandatory **Bootcamp preparation** module runs first and asks verbosity, programming language, and git-init; these are no longer asked in the preface, and each stays a pinned-verbatim (INV-056) single-meaning 👉 question.
- [ ] **Graduation** appears as a mandatory terminal module in the list and selection rules, consistent with the existing graduation stage (INV-047).
- [ ] Module 0's separate skip/keep gate is removed; whether the ER Concepts primer runs is driven solely by module selection.
- [ ] "Truth Set visualization" is a standalone Optional module; it runs the guaranteed visualization when selected (and always in Core), and INV-038 is amended to guarantee it only when selected. The overview surfaces that deselecting it skips workstation verification.
- [ ] The affected invariants (INV-013, INV-014, INV-024, INV-025, INV-026, INV-038, INV-072) are reconciled/amended and recorded per the resolved decisions; no plugin text advertises behavior that contradicts the reconciled invariants (INV-003).
- [ ] All choices persist via a single consolidated write (INV-058); no extra per-sub-step writes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — redesign overview (`:82-107`), replace the track gate with Core/Customized (`:143-153`), remove verbosity/language/git-init from the preface (`:111-116`, `:174`, `:180-204`), move them and the consolidated write (`:206-224`) into the new module.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/SKILL.md` — update the onboarding sequence (`:23-41`) and hand-off.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — module-order / journey-map framing (`:170-183`) to reflect selection + the new modules.
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — remove the skip/keep gate (`:19-34`); drive inclusion by selection.
- `plugins/senzing-bootcamp/skills/` — new **Bootcamp preparation** module, and new standalone **Truth Set visualization** Optional module split out of `module-03-system-verification` (amending INV-038).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — align graduation with its module-list membership.
- `specs/INVARIANTS.md` — reconcile INV-013/014/024/025/026/038/072 (amendments recorded by `implement-spec`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Redesign welcome banner + add bootcamper-controlled module selection (Core vs Customized track)" (2026-07-18, onboarding preface); "Move the 'level of detail' (verbosity) question into the new 'Bootcamp preparation' module"; "Add 'Graduation' as a mandatory module at the end of the module list"; "Move the 'programming language' question into the new 'Bootcamp preparation' module"; "Move the 'initialize git repository' question into the new 'Bootcamp preparation' module"; "Retire Module 0's skip/keep gate once 'Entity Resolution Concepts' is a selectable module".
- Priority: High (item 1); Medium (items 2–6).
- Related specs: `entity-resolution-module-zero.md` (INV-072, Module 0), `advanced-modules-8-11-scope.md` (track/module-scope reframing), `relocate-git-init-to-onboarding.md` (git-init currently in the preface — superseded by the move into the new module), `verbosity-minimal-preset.md` (verbosity presets, distinct), `module-references-by-name-not-number.md` (name-not-number, follows from customizable modules).

## Invariants introduced

- `INV-075` — Bootcamp preparation is the first mandatory module (path choice, module selection, verbosity, programming language, git-init; one consolidated write; lightweight, exempt from the per-module apparatus). Supersedes INV-024, INV-026. (recorded in `specs/INVARIANTS.md`)
- `INV-076` — Core-vs-Customized path: Core runs all modules in order; Customized runs the required modules plus selected optional ones in prerequisite order; a deselected optional module is a requested skip. Supersedes INV-013, INV-025. (recorded in `specs/INVARIANTS.md`)
- `INV-077` — The guaranteed Truth Set web-app visualization is delivered by the selectable Truth Set visualization module — produced when selected (always in Core). Supersedes INV-038. (recorded in `specs/INVARIANTS.md`)
- `INV-078` — Module 0 (Entity Resolution Concepts) runs iff selected during Bootcamp preparation; the skip/keep gate is retired. Supersedes the gate mechanism of INV-072. (recorded in `specs/INVARIANTS.md`)

Also amended in place: INV-014 clarified (Customized deselection is a requested skip); supersede markers appended to INV-013, INV-024, INV-025, INV-026, INV-038, INV-072.
