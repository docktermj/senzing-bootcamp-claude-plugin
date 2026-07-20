# Split Truth Set Visualization into its own standalone module (structural split from Module 3)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

System Verification and Truth Set Visualization must be **two distinct modules**. Today they are
distinct at the *experience* level — separate selection entries (INV-077), separate banners,
journey-map entries, recap sections, `modules_completed` tokens, and completion summaries (INV-086)
— but they are **not structurally distinct**: both live in one skill directory
(`module-03-system-verification/`), and Truth Set Visualization is literally "Module 3, Phase 2."
To a bootcamper the two read as one merged module (the originating feedback), and the shared
directory / shared Phase 3 close is why.

This finishes an intent that was already committed but never implemented:
`customizable-module-selection.md` (implemented; INV-077) lists as an affected file a *"new
standalone Truth Set visualization Optional module split out of `module-03-system-verification`"* —
that structural carve-out was never done. This spec completes it.

## Root cause

The two modules share one skill and one close, so they cannot present as fully separate:

- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — one `SKILL.md` documents
  both; Phases section (`:104-124`) lists Phase 2 as part of Module 3; the "TruthSet source" section
  (`:64-85`) is Truth-Set-only content living in the System Verification skill.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-visualization.md` — the whole
  Truth Set Visualization module, titled "Module 3, Phase 2."
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — a single
  close for **both** modules: the pre-advancement viz self-check (`:6-30`), the `web_service`/`web_page`
  completeness gate (`:32-46`), Step 11 web-service termination + Truth Set data purge (`:122-159`),
  and Step 12 dual recording/recap/summary/transition (`:161-199`).
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:51` — maps "Truth Set visualization"
  to `module-03-system-verification` Phase 2 (step 9), not a directory of its own.
- Invariants tie the split to phases of one module: **INV-077** ("Module 3, Phase 2"), **INV-082**
  (Phase 1 vs Phase 2 Truth-Set boundary), **INV-083** (register-before-load for both loads),
  **INV-086** ("Module 3 close records `truthset_visualization`").

## Proposed change

Carve Truth Set Visualization into its own skill directory so the two are genuinely separate
modules that each run the full per-module apparatus and their own close.

1. **New skill directory.** Create a standalone module directory and move the Truth Set files into
   it: `phase2-visualization.md` → its phase file, plus `visualization-api-reference.md`. Give it
   its own `SKILL.md` (frontmatter `name`/`description`, the mandatory MCP-grounding clause per
   INV-080, before/after, prerequisites "Requires System verification", and the "TruthSet source"
   section moved out of Module 3's `SKILL.md`).
   - **Directory name (maintainer decision).** Recommend **`module-03b-truthset-visualization`** —
     it preserves the prerequisite adjacency (runs right after System Verification, before Data
     Collection) with no renumbering of `module-04…07`, and avoids the `module-08`–`module-11`
     names conceptually reserved for the Advanced-Topics discussion in
     `advanced-modules-8-11-scope.md`. Directory numbers are internal; run order is driven by
     `selected_modules` (INV-076), not the directory name (INV-079).
2. **System Verification keeps Phase 1 + its own close.** Module 3 retains `phase1-verification.md`
   and a report/close that covers **only** System Verification: the 8-check Verification Report,
   the synthetic `VERIFY` data purge, `system_verification` recording + recap section + completion
   summary, and its transition question. Remove the Truth-Set-only content (pre-advancement viz
   self-check, `web_service`/`web_page` gate, Truth Set data purge, `truthset_visualization`
   recording) from Module 3's close.
3. **Truth Set Visualization owns its own close.** The new module runs its full apparatus at start
   (already specified, INV-086) and its **own** close: the pre-advancement viz self-check + snapshot
   guarantee (INV-077), the `web_service`/`web_page` completeness gate, web-service termination, its
   own Truth Set data purge (the two datasets are independent — Phase 1 uses synthetic `VERIFY`,
   this module acquires/loads the Truth Set itself, per Module 3 `SKILL.md:64-71`), and
   `truthset_visualization` recording + recap + summary + transition.
4. **Rewire the flow/handoff.** System Verification → (when selected) Truth Set Visualization →
   Data Collection. Each module now runs `module-completion.md` **once** at its own close, so the
   Module-3 "more than one module completed this turn" special case (module-completion.md Steps 3–4;
   phase3 Step 12 dual recording) is no longer needed for this pair — reconcile that guidance
   (keep the general multi-module capability only if another skill still needs it).
5. **Selection + progress state.** Update `bootcamp-preparation/SKILL.md:50-51` to map "Truth Set
   visualization" to the new directory. Decide the progress-state key: keep the viz checks under a
   Truth-Set-specific key (e.g. `truthset_visualization.checks.web_service/web_page`) while still
   reading legacy `module_3_verification.checks.*` for resume/back-compat, and document the move.
6. **Reconcile invariants (INV-003).** Update in place, no meaning change where possible: INV-077,
   INV-082, INV-083, INV-086 to reference the **standalone Truth Set visualization module** instead
   of "Module 3, Phase 2"; INV-086's "Module 3 close records both" becomes "each module records
   itself at its own close." Where meaning changes, add a new invariant per the maintenance rules.
7. **Sweep cross-references.** `graduation/SKILL.md` reconcile (both sharing `module-03-system-verification/`),
   `ground-rules.md` journey-map framing, and any other text that calls Truth Set Visualization
   "Module 3 Phase 2."

## Acceptance criteria

- [ ] Truth Set Visualization is its own skill directory with its own `SKILL.md` (name, MCP-grounding clause per INV-080, prerequisites, before/after); `phase2-visualization.md` and `visualization-api-reference.md` no longer live under `module-03-system-verification/`.
- [ ] System Verification's close records only `system_verification` and purges only synthetic `VERIFY` data; Truth Set Visualization's close records only `truthset_visualization`, runs the snapshot/self-check guarantee (INV-077), and purges only the Truth Set data.
- [ ] Each module runs its own module-completion once at its own close (no dual-recording turn); the two present as separate modules end-to-end (banner, journey map, recap section, `✅ Module complete` line, transition).
- [ ] Run order and prerequisites are preserved: System Verification → Truth Set Visualization (when selected) → Data Collection; deselecting Truth Set Visualization remains a requested skip (INV-014/077) with no workstation-verification visualization.
- [ ] INV-077/INV-082/INV-083/INV-086 (and any cross-references) are reconciled to the standalone module with no behavior contradicted anywhere in plugin text (INV-003); recap remains name-based and complete (INV-085).
- [ ] Resume works across the rename: an in-progress `module_3_verification.checks.*` state is still honored, or migrated, so a mid-visualization resume re-opens the right module.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/` (new) — `SKILL.md`, the visualization phase file (from `phase2-visualization.md`), `visualization-api-reference.md`, and its own close.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — drop Phase 2 / "TruthSet source"; scope to System Verification only.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase3-report-close.md` — remove Truth-Set-only close content; keep the 8-check report, `VERIFY` purge, and `system_verification` close/transition.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — handoff now goes to the standalone module (when selected).
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — module-list mapping (`:50-51`) and selection wording.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — reconcile the Module-3 multi-module-per-turn case.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md`, `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — cross-reference sweep.
- `specs/INVARIANTS.md` — reconcile INV-077/INV-082/INV-083/INV-086 to the standalone module.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Truth Set visualization needs its own full module apparatus, distinct from System verification" (2026-07-20, Module 3), extended by the maintainer to a full **structural** split (own skill directory), 2026-07-20.
- Priority: High
- Related specs: `customizable-module-selection.md` (INV-077; named this split but left it unimplemented — this completes it), `truthset-visualization-full-apparatus.md` and `record-truthset-visualization-completion.md` (INV-086; apparatus/recording, now applied to a standalone module), `module3-synthetic-verification-data.md` (INV-082/083), `advanced-modules-8-11-scope.md` (module-08–11 naming reservation), `recap-sections-name-based-and-complete.md` (INV-085).

## Invariants introduced

- `INV-087` — Truth Set visualization is a standalone module (`module-03b-truthset-visualization`), separate from System Verification, presenting its apparatus at its own module start and recording itself at its own close; supersedes INV-086's "Phase 2 start" / "Module 3 close records both" recording-location framing (recorded in `specs/INVARIANTS.md`).
