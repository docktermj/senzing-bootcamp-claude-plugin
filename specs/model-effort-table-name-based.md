# Make the model/effort recommendations name-based (remove ambiguous "Module N")

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`ground-rules.md`'s agent-facing model/effort guidance refers to modules by bare number
("heavier Modules 2 and 5 … warrant Opus 4.8 + high effort"; a table row "Modules 2, 5 →
Opus 4.8, high" and "Module 6 → Sonnet 5, high"). Those numbers follow the `module-0X-*`
**skill-directory** scheme (Module 2 = `module-02-sdk-setup`, Module 5 =
`module-05-data-quality-mapping`, Module 6 = `module-06-data-processing`).

But the plugin has a second, conflicting numbering: `bootcamp-preparation/SKILL.md`'s module
list — the declared "source of truth for selection and the journey map" — numbers modules
**1–11** (Module 2 = Entity Resolution Concepts, Module 5 = System verification, Module 6 =
Truth Set visualization). Under that catalog, "Modules 2, 5 → Opus" would assign the heavy
model to the two lightweight optional modules and misses SDK setup / Data quality entirely.

Because these instructions are executed by an LLM agent, the collision is a functional risk:
the agent can apply the Opus/high-effort recommendation to the wrong module. The
component-level table in `docs/model-selection.md` already avoids this by naming skills
directly (`module-02-sdk-setup → Opus 4.8`, etc.); `ground-rules.md` is the one place that
still uses bare, ambiguous numbers. It also runs against the spirit of INV-079 (prefer module
*names* over numbers).

## Root cause

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:18` — prose "heavier
  Modules 2 and 5 … warrant Opus 4.8 + high effort" uses bare directory-scheme numbers.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:277-280` — the
  model/effort table rows key on "Modules 1, 3, 4, 7", "Modules 2, 5", "Module 6" (bare
  numbers) while already naming "Truth Set visualization", "Bootcamp preparation",
  "Onboarding", and "Graduation".
- Collides with the 1–11 catalog in
  `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:46-58`.

## Proposed change

Replace the bare "Module N" tokens in `ground-rules.md`'s model/effort guidance (prose at
line 18 and the table at lines 277-280) with module **names** — the same names used in the
journey map and in `docs/model-selection.md`'s per-skill table. No recommendation changes;
only the labels do:

- Opus 4.8 / high: **SDK setup**, **Data quality & mapping**, **Graduation**.
- Sonnet 5 / high (Opus if bespoke load code): **Data processing**.
- Sonnet 5 / medium: **Onboarding, Bootcamp preparation, Discover the Business Problem,
  System verification, Data collection, Query/Visualize/Discover, Truth Set visualization**.

Keep `docs/model-selection.md` (already name-based) as the authoritative mirror and ensure
the two stay in sync (per the existing "keep this table in sync" note; see
`specs/audit3-minor-fixes.md`). If any bare "Module N" reference is intentionally retained
for an internal cross-reference, disambiguate it by naming the scheme.

## Acceptance criteria

- [ ] `ground-rules.md`'s model/effort prose and table no longer use bare "Module N" tokens
      for the recommendation keys; each row/mention names the module.
- [ ] The name→model/effort mapping matches `docs/model-selection.md`'s per-skill table
      (SDK setup, Data quality & mapping, Graduation → Opus 4.8/high; Data processing →
      Sonnet 5/high; the rest → Sonnet 5/medium).
- [ ] No bootcamper-facing output changes (INV-079 already forbids showing module numbers to
      the bootcamper); this is an internal-instruction clarity fix.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — name-based
  model/effort prose (line ~18) and table (lines ~277-280).
- `plugins/senzing-bootcamp/docs/model-selection.md` — confirm it remains the name-based
  mirror; no numbering change expected.

## Source

- Claude Code Review, `Senzing/senzing-bootcamp-claude-plugin` PR #4 (comment 5073711304),
  Parts 4 & 5 — "Dual 'Module N' numbering schemes".
- Priority: Medium (functional risk for LLM-executed instructions; no user-visible change).
- Related specs: `specs/module-references-by-name-not-number.md`, `specs/audit3-minor-fixes.md`,
  `specs/surface-aware-model-effort-instructions.md`.
