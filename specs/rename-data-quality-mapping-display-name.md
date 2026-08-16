# Rename the "Data quality & mapping" display name to "Data Quality, Mapping, and Transformation"

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamper asked to rename the module currently displayed as "Data quality & mapping" to **"Data
Quality, Mapping, and Transformation"**, and flagged that it touches many surfaces: the WELCOME
banner's module overview, the journey maps shown at every module start, `docs/bootcamp_recap.md`, and
the generated recap PDF.

Why it matters, in their words: "Module names appear in many independently-maintained places (banners,
tables, transition questions, recap templates); a rename done in only one place produces an
inconsistent bootcamp where some screens/documents say one thing and others say another."

This is a naming preference, not a bug — but INV-003 (consistent, coherent, complete) makes a
half-applied rename a real defect, which is what makes the inventory the substance of this spec.

## Root cause

Not a defect — the display name is simply hardcoded in many places. The work is a complete,
consistent sweep of **display text only**.

Confirmed inventory in this repo (20 lines across 12 files — broader than the 8 files / 13 lines the
feedback estimated, because the feedback's inventory was taken against the installed plugin cache and
missed `ground-rules.md` and `docs/model-selection.md`):

| File | Lines |
|---|---|
| `skills/module-05-data-quality-mapping/SKILL.md` | 3 (frontmatter `description`), 6 (`# Module 5: Data Quality & Mapping`) |
| `skills/module-05-data-quality-mapping/phase2-data-mapping.md` | 382 (completion-line template), 390 (step-ordering prose) |
| `skills/module-05-data-quality-mapping/phase3-test-load.md` | 8 |
| `skills/bootcamp-onboarding/onboarding-flow.md` | 106 (WELCOME module overview) |
| `skills/bootcamp-onboarding/ground-rules.md` | 18, 279 (model/effort guidance + per-stage table) |
| `skills/bootcamp-preparation/SKILL.md` | 55, 56, 61 (module table + prerequisite prose) |
| `skills/module-06-data-processing/SKILL.md` | 29 |
| `skills/module-06-data-processing/phaseA-build-loading.md` | 16 |
| `skills/module-06-data-processing/phaseD-validation.md` | 165 (the "go back to…" remediation message) |
| `skills/module-07-query-visualize-discover/phase1-query-visualize.md` | 160 (a pinned 👉 transition question) |
| `docs/model-selection.md` | 79, 100 |
| `docs/examples/bootcamp_recap.example.md` | 205, 227, 231 (a recap section header), 319 |

Two derived surfaces need **no** separate change:

- **The module-start banner.** No hardcoded "DATA QUALITY & MAPPING" banner text exists anywhere in
  `skills/` — INV-079 requires the banner to be built as "MODULE: [NAME IN CAPS]" from the module's
  name at runtime, so it follows the renamed display name automatically.
- **`docs/bootcamp_recap.md` and the recap PDF.** `scripts/generate_recap_pdf.py` parses `## {Module
  name}` headings generically (`parse_recap`, `generate_recap_pdf.py:134-149`) and hardcodes no module
  names, so both pick up whatever display name the completing module writes.

## Proposed change

1. **Rename the display name only, everywhere it appears** — all 20 lines above — to "Data Quality,
   Mapping, and Transformation".
2. **Leave every internal token unchanged:** the directory `module-05-data-quality-mapping`, the
   frontmatter `name:` field, the progress/preferences key `data_quality_mapping`, and the
   `modules_completed` token. INV-079 already requires numbers and tokens to stay internal; renaming
   them would break resume, `--expect-modules`, and recap reconciliation.
3. **Fix the two lines that also violate INV-079 while editing them.**
   `skills/module-05-data-quality-mapping/SKILL.md:6` currently reads `# Module 5: Data Quality &
   Mapping` and line 3 embeds "Bootcamp Module 5:". INV-079 requires bootcamper-facing references to
   use the name, not a fixed number. The heading is an internal document title (permitted by INV-079),
   but since it is also the most likely source an implementer copies the display name from, make it
   unambiguous. Do not renumber the module.
4. **Watch the two structured surfaces:**
   - `bootcamp-preparation/SKILL.md:55-56, 61` uses the name as a **prerequisite key** in prose ("Requires
     'Data quality & mapping'"). Rename consistently or the prerequisite text stops matching the module
     table's own label.
   - `module-07-query-visualize-discover/phase1-query-visualize.md:160` is a **pinned verbatim** 👉
     question (INV-056). Renaming it is a pinned-wording change; update it deliberately, keeping the
     question's single meaning intact (INV-008/INV-009).
   - `bootcamp_recap.example.md:231` is a `## ` recap **section header**, which `--check` and
     `--expect-modules` match by name (`generate_recap_pdf.py:232-254`). The shipped example must agree
     with the live name or the example stops demonstrating a valid recap.
5. **Note the comma in the new name.** "Data Quality, Mapping, and Transformation" contains commas, and
   `generate_recap_pdf.py:1203-1211` documents that `--expect-modules` is **semicolon**-separated
   precisely because names contain commas ("e.g. 'Query, Visualize and Discover'"). No code change is
   needed — but any call site passing this name must use the semicolon separator, and this is exactly
   the kind of thing a rename breaks silently.
6. **Capitalization.** The new name is title-case with internal commas, unlike the sentence-case
   neighbors ("Data collection", "Data processing"). That is what the bootcamper asked for; apply it
   verbatim rather than normalizing it, and use it identically in every one of the 20 places so the
   inconsistency is at least uniform.

## Acceptance criteria

- [ ] All 20 display-text occurrences render "Data Quality, Mapping, and Transformation"; a
      case-insensitive search for "data quality & mapping" and "data quality and mapping" across
      `plugins/senzing-bootcamp/` returns no bootcamper-facing hits.
- [ ] No internal token changed: the directory name, frontmatter `name:`, `data_quality_mapping` key,
      and `modules_completed` token are byte-identical to before.
- [ ] The module-start banner renders "MODULE: DATA QUALITY, MAPPING, AND TRANSFORMATION" with no
      hardcoded banner string added (INV-079).
- [ ] The completion line reads "✅ Module complete: Data Quality, Mapping, and Transformation"
      (INV-079).
- [ ] The pinned Module 7 return question (`phase1-query-visualize.md:160`) carries the new name and
      still has exactly one meaning (INV-008/INV-009/INV-056).
- [ ] `docs/examples/bootcamp_recap.example.md`'s section header matches, and
      `generate_recap_pdf.py --check` passes against it.
- [ ] Any `--expect-modules` call site carrying this name uses the semicolon separator.
- [ ] A recap generated after the rename shows the new name in `docs/bootcamp_recap.md` and in the PDF
      with no template change.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): a text-only
      change; verify no case-sensitive filename assumption is introduced.

## Affected files

All 12 files in the inventory table above. The highest-risk edits are
`plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` (pinned
question), `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` (prerequisite keys), and
`plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` (validated by `--check`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Rename 'Data quality & mapping' module to 'Data
  Quality, Mapping, and Transformation' everywhere it's displayed" (2026-07-24, cross-cutting)
- Priority: **High**
- Related specs: `specs/module-references-by-name-not-number.md` (established INV-079),
  `specs/recap-sections-name-based-and-complete.md`, `specs/refresh-example-recap.md`,
  `specs/doc-consistency-audit.md`

## Invariants introduced

None — a display-name content change governed by the existing INV-079 (name-based module references)
and INV-003 (consistent, coherent, complete). Enforcement against reintroducing the old name rides on
`tests/test_model_guidance_sync.py`'s shipped-and-repo-doc scan, added under `INV-114`.

## Implementation notes

The new name contains **two** commas, which makes `generate_recap_pdf.py --expect-modules`'s
semicolon separator load-bearing rather than incidental — verified that `--check` passes with the
name semicolon-separated and fails comma-separated. `README.md` also carried the old name and was
fixed, though the spec scoped the inventory to `plugins/`.
