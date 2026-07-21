# Final-review coherence nits: brand color, layout tree, stale citations, name/token drift, journey map

Maintain the invariant conditions in @INVARIANTS.md and fix the following issues:

## Problem

Coherence/consistency nits (INV-003) surfaced by the final review:

1. **D1 (INV-081).** `generate_recap_pdf.py`'s inlined brand fallback `LINE = (229, 223, 214)` is
   out of sync with `brand_tokens.WARM_LINE = "#E5DFD3"` = `(229, 223, 211)`, contradicting the
   block's own "keep in sync with brand_tokens.py" comment. Only manifests when `brand_tokens.py` is
   absent, but it is a real, verifiable divergence.
2. **D2 (INV-050).** Two config files the skills create at runtime — `config/license.json`
   (`module-02:601`) and `config/cord_metadata.yaml` (`module-04:200`) — are missing from the
   INV-050 `config/` tree.
3. **D3 (INV-050).** `module-03/SKILL.md:42-43` points bootcampers to
   `docs/modules/MODULE_3_SYSTEM_VERIFICATION.md`, which is never created and not in the tree, with
   no "later port" caveat (its siblings all carry one).
4. **E3 (INV-003).** Stale invariant-ID citations for current mechanisms: `ground-rules.md:207` and
   `module-00/SKILL.md:24` cite INV-072 for the retired skip/keep gate (retirement is INV-078);
   `bootcamp-preparation/SKILL.md:128` cites INV-028 for the module banner (superseded by INV-079).
5. **E4 (INV-079).** Module 1 name drift: the bootcamp-preparation journey list called it "Business
   problem" while the module and its INV-073-pinned gate use "Discover the Business Problem".
6. **C3 (INV-003).** Provenance-token drift: `phase1-discovery.md` recorded synthetic data as
   `generated`, but Module 4's authoritative provenance enum (`module-04:216`) uses `synthesized`.
7. **B3 (INV-029).** `bootcamp_preparation` and `entity_resolution_concepts` are in
   `selected_modules` (which drives the journey map) but are apparatus-exempt and never added to
   `modules_completed` — so if ✅ derived from `modules_completed` they would render ⬜ forever in
   every content module's journey map.

## Root cause

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py:266`
- `specs/INVARIANTS.md` — INV-050 `config/` tree
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md:42-43`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:196,207`
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md:24`
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:48,128`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:92,94`

## Proposed change

1. `LINE` fallback → `(229, 223, 211)`.
2. Add `config/license.json` and `config/cord_metadata.yaml` to the INV-050 `config/` tree (clarifies the layout; no structural change).
3. Reword the `docs/modules/` reference as a later porting phase not yet created.
4. Update the three stale citations (INV-072 → INV-078 ×2; INV-028 → INV-079).
5. Align the journey-list label to "Discover the Business Problem".
6. `generated` → `synthesized` in `phase1-discovery.md` (match the enum).
7. Clarify the journey-map rule in `ground-rules.md`: ✅/🔄/⬜ is determined by position relative to
   `current_module` (before = ✅, including the apparatus-exempt Bootcamp preparation and Module 0
   which are never in `modules_completed`; equal = 🔄; after = ⬜).

## Acceptance criteria

- [x] `generate_recap_pdf.py` `LINE` fallback matches `brand_tokens.WARM_LINE` (`229,223,211`).
- [x] The INV-050 `config/` tree lists `license.json` and `cord_metadata.yaml`.
- [x] The `docs/modules/` reference no longer points to a nonexistent file as if it exists.
- [x] No current mechanism cites a superseded invariant ID (INV-072→078, INV-028→079).
- [x] Module 1 is labeled "Discover the Business Problem" consistently (journey list = module = gate).
- [x] `phase1-discovery.md` uses the `synthesized` provenance token, matching Module 4's enum.
- [x] The journey-map ✅ derivation is explicit and renders the exempt modules correctly (not ⬜ forever).
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py`
- `specs/INVARIANTS.md`
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md`
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md`
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` (provenance token)

## Source

- Audit (fourth deep-dive, final review), 2026-07-19 — coherence nits; maintainer chose "fix all verified findings".
- Priority: Low.
- Related specs: `specs/layout-tree-reconciliation.md`, `specs/apply-senzing-style-guide-to-deliverables.md`.
