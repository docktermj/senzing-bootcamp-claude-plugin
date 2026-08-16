# Per-module outcome invariants omit the apparatus-exempt carve-out

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-029, INV-030, INV-031 and INV-032 each say the apparatus is presented at "the beginning of
**each** module" (or "the end of each module"), with no exemption recorded:

- **INV-029** — At the beginning of each module, show modules completed, the current module, and upcoming modules.
- **INV-030** — At the beginning of each module, explain what is true before the module and what will be true after completing the module.
- **INV-031** — At the beginning of each module, enumerate the steps that will be taken in the module.
- **INV-032** — At the end of each module, give the Bootcamper a list of what was accomplished, what files were produced, why it matters, and what's next.

Two shipped modules deliberately do none of this, and say so:

- `bootcamp-preparation/SKILL.md:26` — "per-module completion apparatus (no journey map, no
  before/after framing, no …)"
- `module-00-entity-resolution-concepts/SKILL.md:29` — "map of its own, no before/after framing,
  no step overview, and no bootcamper-facing end-of-module …"

So the ruleset asserts a guarantee stronger than the plugin makes. A reader auditing INV-031
against Bootcamp preparation finds a violation that is not one — or, worse, "fixes" Bootcamp
preparation to present a step overview and thereby breaks INV-075.

## Root cause

The carve-out exists and is authoritative, but it lives **only** on the invariants that create the
exemption, never on the invariants that are exempted:

- `specs/INVARIANTS.md:539` — **INV-075** — Bootcamp preparation "is a lightweight setup module,
  exempt from the per-module completion apparatus (no journey map, before/after framing, step
  overview, `docs/bootcamp_recap.md` section, or `modules_completed` entry)".
- `specs/INVARIANTS.md:542` — **INV-078** — Module 0 "remains a lightweight preamble exempt from the
  per-module completion apparatus".
- `specs/INVARIANTS.md:556` — **INV-092** — reinstates *part* of it for Module 0 (recap section and
  `modules_completed`) while leaving "the rest of the module-start apparatus" exempt.

This is a one-directional link, and it breaks the file's own convention. Every comparable case in
`INVARIANTS.md` carries the pointer on the **narrowed** invariant, not only on the narrowing one:

- **INV-013** — "(An optional, non-counted Module 0 preamble is exempt from this ordering — see INV-072.)"
- **INV-014** — "(Skipping the optional Module 0 preamble is a permitted, requested skip — see INV-072.)"
- **INV-028** — "(Superseded by INV-079: the banner is 'MODULE: [title]' …)"
- **INV-038** — "(Superseded by INV-077 …)"
- **INV-040**–**INV-043** — each carries its CORD fast-path caveat.

INV-029–INV-032 sit in the same block as INV-028 and INV-038, between invariants that both carry
their pointers, and carry none. Nothing indicates the omission was a decision.

The gap is invisible to every existing check: INV-029–INV-032 are cited by **no test**
(`coverage_reports.py invariants` classes them as bootcamp-outcome invariants routed to `dry-run`
phase 3), and `citations.py verify` proves only that IDs resolve, never that a rule's scope matches
the plugin's. `final-review-doc-coherence` fixed the neighbouring stale citations
(INV-028→INV-079, INV-072→INV-078) and made the journey-map derivation explicit for exactly these
two apparatus-exempt modules — and still did not annotate INV-029–INV-032.

## Proposed change

Append a dated clarification to each of INV-029, INV-030, INV-031 and INV-032 naming the exemption
and its authority. This is a **clarification with no meaning change**, permitted by
`INVARIANTS.md` rule 2; the plugin's behaviour does not change and no invariant is renumbered or
deleted. Suggested form, matching the INV-013/INV-014 idiom:

> (The apparatus-exempt setup modules — Bootcamp preparation, INV-075; Module 0, INV-078 — are
> exempt; Module 0's recap section and `modules_completed` entry are reinstated by INV-092.
> Clarified YYYY-MM-DD, no meaning change.)

INV-032's note additionally carries INV-092, since Module 0 *does* append its own recap section
while presenting no bootcamper-facing end-of-module summary.

⛔ Do **not** "fix" the two modules to present the apparatus. The plugin is correct here; the
ruleset is what overstates.

## Acceptance criteria

- [ ] INV-029, INV-030, INV-031 and INV-032 each carry a dated clarification naming the
      apparatus-exempt setup modules and citing INV-075 and INV-078 (and INV-092 on INV-032).
- [ ] No invariant is renumbered, deleted, or changed in meaning; the additions are parenthetical
      clarifications only.
- [ ] `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` and
      `module-00-entity-resolution-concepts/SKILL.md` are unchanged — the exemption is real and the
      ruleset is what moves.
- [ ] A test asserts that each of INV-029–INV-032 names the exemption, so a later edit cannot drop
      it back to the unqualified "each module" form — **negative-controlled**, mutation verified to
      land, then reverted.
- [ ] `citations.py verify` stays clean and the full suite stays green.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — four in-place clarifications on INV-029, INV-030, INV-031, INV-032.
- `tests/test_apparatus_exempt_carve_out_is_recorded.py` — new.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15, forward invariant sweep
  (`Source: self-observed (assistant retrospective)`). Found by re-sweeping INV-028–INV-049, which
  the 2026-08-14b audit explicitly disclosed as **not** re-swept.
- Priority: **Medium**. Nothing a Bootcamper can see today; the risk is a future implementer
  reading INV-031 literally and adding a step overview to Bootcamp preparation, which would breach
  INV-075. Cheap to close and it removes a standing false premise.
- MCP re-check: **n/a (no Senzing fact).** This is internal consistency between the plugin's own
  files and its own ruleset; no MCP tool was called and no Senzing claim is asserted. Server
  **1.32.9** was recorded this session (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `final-review-doc-coherence` (fixed the neighbouring stale citations and touched
  the same two modules without annotating these four), and INV-075, INV-078, INV-092.

## Deviations from this spec, and why (2026-08-15)

- **The site set is FIVE invariants, not the four this spec enumerates — and the fifth needed the
  opposite note.** Writing the guard to derive its sites by scanning `INVARIANTS.md` for the
  "At the beginning/end of each module" phrasing (INV-246, rather than hardcoding the four IDs this
  spec lists) immediately matched **INV-028** as well. INV-028 is genuinely *not* exempt: Bootcamp
  preparation "presents its own banner" (`bootcamp-preparation/SKILL.md:24`) and Module 0 presents
  "its ENTITY RESOLUTION CONCEPTS banner" (`module-00/SKILL.md:26`). So it received a note saying the
  setup modules are **NOT** exempt from it — the inverse of what this spec prescribes for its four.
  Had the guard hardcoded the spec's list, INV-028 would have stayed silent directly above four
  carved-out neighbours, where silence reads as the same carve-out. This is the failure INV-246
  exists for, caught by the mechanism INV-246 requires, on the first spec implemented after it.
- **The guard therefore asserts a *disposition*, not an exemption.** Each member of the phrasing
  class must state which side it is on — carved out, or explicitly not — because a guard demanding
  only the exemption note would have forced a false one onto INV-028.
- **No `Enforced by` clause was added to the five invariants**, deliberately: it would add five
  entries to `tests/test_invariant_enforcer_citations.py`'s pinned pair count for no discoverability
  gain the test docstring does not already provide, in a file this skill's own guidance flags for
  bulk.
- **No Senzing fact required re-verification.** `get_capabilities` was called this session to date
  the run (server **1.32.9**, 2026-08-15), confirming the spec's `MCP re-check: n/a`. The spec's
  factual claims are about this repo's own files and were re-read directly rather than trusted.
