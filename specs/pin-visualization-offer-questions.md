# Pin every choice/visualization-offer question verbatim with 👉

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-005 requires every question to be preceded by "👉"; INV-051 requires every
2+‑choice question to use a neutral lead + numbered list (never "or"); INV-056
requires every mandatory gate question to be pinned verbatim in the skill file so
it cannot drift at runtime. Most questions comply, but several bootcamper-facing
offers and one mandatory choice are authored as descriptive prose ("offer a
visualization", "present three paths") without a pinned 👉 question — leaving the
marker and wording to model improvisation, exactly the drift INV-056 exists to
prevent.

## Root cause (confirmed)

The global rule is stated (`skills/bootcamp-onboarding/ground-rules.md:26`,
"Prefix every input-requiring question with 👉"), but these sites do not pin it:

- `skills/module-01-business-problem/phase1-discovery.md:49-64` — Step 5 presents a
  **three-way choice with no 👉 and no neutral lead question** (the clearest gap;
  a mandatory decision left unformatted).
- `skills/module-05-data-quality-mapping/phase2-data-mapping.md:268` — an explicit
  question ("Would you like me to create a web page showing the quality
  analysis?") with **no 👉** (contrast the parallel offer at
  `skills/module-04-data-collection/SKILL.md:234`, which pins 👉).
- `skills/module-05-data-quality-mapping/phase1-quality-assessment.md:178` — "Offer
  to create a visual…", no 👉.
- `skills/module-06-data-processing/phaseD-validation.md:112-121` — a "Mandatory
  visualization offer (internal gate)" described in prose, question not pinned.
- `skills/module-07-query-visualize-discover/phase1-query-visualize.md:172,199` —
  steps 3c/3d defer to a "Visualization Protocol" that is an **unported later
  phase**, so the pinned question they rely on does not yet exist.
- `skills/graduation/SKILL.md:168,192` — the production overwrite/merge/abort choice
  and the config-confirm question are described in prose, not pinned (mandatory
  decisions, INV-056 territory even though not glyph-marked ⛔).

## Proposed change

For each site above, write the exact 👉 question verbatim in the skill file:

- Reformat `phase1-discovery.md:49-64` (Step 5) to a neutral lead question + a
  numbered list of the three paths, ending on a single 👉 (INV-005/008/051).
- Pin a single verbatim 👉 yes/no for each visualization offer
  (`phase2-data-mapping.md:268`, `phase1-quality-assessment.md:178`,
  `phaseD-validation.md:112-121`, `phase1-query-visualize.md:172,199`). Until the
  "Visualization Protocol" phase is ported, inline the pinned offer wording rather
  than referencing the unported protocol.
- Pin the two graduation decision questions (`graduation/SKILL.md:168,192`) as
  verbatim, unambiguous questions (the overwrite/merge/abort choice as a neutral
  lead + numbered list per INV-051; the config-confirm as a pinned yes/no).
- Keep all pinned wording unambiguous yes/no or neutral-lead+numbered-list, with
  no "or"-joined choices (INV-008/009/051).

## Acceptance criteria

- [ ] Every bootcamper-facing question in the audited sites is written verbatim in the skill file with a leading 👉 (no reliance on ground-rule 26 to supply it at runtime).
- [ ] `phase1-discovery.md` Step 5 is a neutral lead question + numbered list ending on one 👉 (INV-005/051).
- [ ] Every visualization offer is a pinned 👉 yes/no; none defers its wording to the unported "Visualization Protocol".
- [ ] The two graduation decision questions are pinned verbatim (INV-056), unambiguous (INV-008), and free of "or"-joined choices (INV-009/051).
- [ ] A repo-wide check finds no bootcamper-facing `?`-terminated offer in the skills that lacks a pinned 👉.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 5 three-way choice (`:49-64`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — viz offer (`:268`).
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — viz offer (`:178`).
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseD-validation.md` — mandatory viz offer (`:112-121`).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` — steps 3c/3d viz offers (`:172,199`).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — production and config-confirm questions (`:168,192`).

## Source

- Invariant audit, 2026-07-17 (deep-dive over the plugin), INV-005/INV-051/INV-056 findings — several offers authored as prose rather than pinned 👉 questions.
- Priority: Medium.
- Related specs: `interaction-or-questions.md` (INV-051, the "or" rule), `onboarding-explore-gate-wording.md` (INV-056, pinned gate wording). Bears on INV-005, INV-008, INV-009, INV-051, INV-056.
