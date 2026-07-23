# Offer "generate data for me" as a numbered option in the Data collection menu

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

In Data collection (Module 4), Step 2 asks the bootcamper how to supply the data for a source
with a four-option numbered menu:

> 👉 **How would you like to provide the data for this source? Reply with a number:** (1) upload
> a file, (2) provide a URL or file path, (3) connect to a database, (4) use an API endpoint.

None of the numbered options offers to have the bootcamp generate/synthesize the data — even
though the earlier Discover the Business Problem module (Module 1) explicitly lists "generate a
scenario for me" as a numbered option in its own menu, and a bootcamper who took that path in the
same session reasonably expects the same generation option when the actual data files are
collected. The two modules are inconsistent about whether data generation is a selectable path.

## Root cause

The menus were authored with different structures for the equivalent generate-vs-provide decision:

- **Module 4** — `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:104-105`
  (Step 2): the numbered menu has exactly four options and no generation option. Synthesized/
  generated data appears only as **conditional prose fallback**, not a numbered choice:
  CORD as the primary alternative (`SKILL.md:109-122`), free-data + synthesized as secondary
  prose (`SKILL.md:124-131`, synthesized at `:130`), and the agent-behavior hierarchy that treats
  synthesized data "only as a last resort" (`SKILL.md:541-547`).
- **Module 1** — `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md:49-56`
  (Step 4): option **3** is `**I don't have my own data — generate a scenario for me**`, a
  first-class numbered choice (recommendation preface at `:46-47`).

So Module 1 surfaces generation as a numbered, clearly-labeled fallback option, while Module 4
buries the same capability in prose that only appears after the bootcamper indicates they lack
data.

## Proposed change

In Module 4 Step 2 (`SKILL.md:104-105`), add a numbered "generate/synthesize the data for me"
option to the data-provision menu, mirroring Module 1's treatment:

- Add it as an explicit **fallback-labeled** numbered option (e.g. `(5) I don't have my own data —
  generate/synthesize it for me`), consistent with Module 1's option-3 wording and with the
  plugin's "encourage your own data, generation as fallback" philosophy
  (`encourage-own-business-case.md`; the last-resort hierarchy at `SKILL.md:541-547`). Making the
  fallback a visible numbered choice does not promote it above the bootcamper's own data — Module 1
  already labels its generation option the same way.
- When the bootcamper picks it, route into the existing synthesized/CORD generation prose path
  (`SKILL.md:109-131`) rather than duplicating that logic, and record the resulting
  `provenance: synthesized` (or `cord`) exactly as today (`SKILL.md:209-220`).
- Keep the lead question neutral and single-meaning (INV-008/INV-051); keep the choices a numbered
  list, never joined with "or"; the bootcamper still chooses (no answer assumed, INV-007).

## Acceptance criteria

- [ ] Module 4 Step 2's numbered menu includes an explicit "generate/synthesize data for me" option, labeled as a fallback consistent with Module 1 Step 4 option 3.
- [ ] Selecting it routes into the existing synthesized/CORD generation path and records `provenance` in `config/data_sources.yaml` as today (no duplicate generation logic).
- [ ] The lead question stays neutral and single-meaning; choices remain a numbered list never joined with "or" (INV-008/INV-051); the bootcamper still makes the choice (INV-007).
- [ ] The "own data encouraged, generation as fallback" framing is preserved (does not contradict `encourage-own-business-case.md` or the `SKILL.md:541-547` hierarchy).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — add the numbered generate option to Step 2's menu (`:104-105`) and wire it to the existing generation prose (`:109-131`) and provenance recording (`:209-220`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Data collection's data-provision menu doesn't offer \"generate data for me\"" (2026-07-22, Module: Data collection)
- Priority: Medium
- Related specs: `encourage-own-business-case.md` (Module 1 Step 4 numbered generate option and the "own data encouraged" framing); none other.
