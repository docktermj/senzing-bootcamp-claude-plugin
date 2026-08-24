# Step 2 fixes the generated dataset's size before anything in the module measures the license

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On the synthesized-scenario path, the guide sized the generated dataset **down** — 538 records to
466 — specifically to stay under the 500-record built-in evaluation limit, reasoning that an absent
`license_record_limit` meant no custom license was configured. It then reached Step 8a, followed
its instruction to *measure* the limit rather than assume it, and found the workstation carries a
custom EVAL license with `recordLimit: 0` — no record cap at all. The downsizing was unnecessary
and was withdrawn.

This is the exact inference **INV-244** forbids — reading an absent `license_record_limit` as "no
custom license" rather than "never measured" — reached **on a module that already states the rule
in full**. `module-04-data-collection/SKILL.md:96-116` was corrected on 2026-08-14 by
`inv244-absent-license-branch-exists-in-module-4-too`, and the run that produced this report was on
plugin 0.5.1 with that fix in place. The text is right and it did not bind.

⚠️ **The harm this time was zero and that is not reassurance.** 466 records with 60 three-way and
93 two-way cross-source overlaps was ample for the scenario. The same mechanism on a scenario that
genuinely needed volume produces exactly the harm INV-244 records — a bootcamper whose license has
no cap steered to a smaller dataset — one module before Modules 6 and 7 have to demonstrate
cross-source resolution on it.

## Root cause

**The rule and the decision are in different places, and only the rule knows they are related.**

- The canonical framing lives at `module-04-data-collection/SKILL.md:82-121`, under
  `## License limit and dataset size (canonical framing)` — **above** `## Workflow` (`:172`). It
  fires "Before any license-based capacity or sampling decision" (`:86`).
- The decision is made at `### 2. For each data source, collect the data` (`:184`), in the
  `provenance: synthesized` branch (`:200-258`), which is where the record counts are actually
  chosen and the files written into `data/raw/`.
- **That branch never routes back to the framing.** It carries five ⛔/⚠️ directives about what the
  generated data must contain — mapping complexity (`:209`), quality gaps (`:215`), the band
  targets (`:224-232`), `quality_intent` (`:245`), never a gap in a record key (`:239`) — and not
  one word about how many records, or about measuring capacity before deciding.

Two things make the miss natural rather than careless:

1. **The framing reads as being about *sampling down an existing dataset*, not about *choosing how
   big to generate*.** Its trigger phrase is "capacity or sampling decision"; the branch beneath it
   is headed "Work with a smaller slice" and the whole `⛔ Sampling rule` block (`:133-163`) is
   about reducing a dataset that already exists. Deciding to emit 466 rather than 538 records is a
   capacity decision that never feels like sampling, because nothing is being cut.
2. **The measurement is six steps downstream of the decision.** The framing tells you to measure
   "by Step 8a's own procedure (sub-step 7 below)" (`:102`) — Step 8a is at `:686`, and by the time
   the guide is told to measure, the data is already generated and written.

Nothing upstream pins the size either: Module 1 Step 4a's generated-scenario invariants
(`module-01-business-problem/phase1-discovery.md:139-151`) require "at least two distinctly named
data sources, each with ≥1 record" and say nothing about a total. So the count is genuinely
first decided in Module 4 Step 2, at the site with no license guidance.

## Proposed change

1. **Route Step 2's synthesized branch to the framing, at the point of decision.** Add a directive
   in the `provenance: synthesized` branch, alongside the existing generation directives, that
   choosing the generated record counts **is** a license-capacity decision and must not precede the
   measurement — citing INV-244 and pointing at the canonical framing block above rather than
   restating its procedure (the same route-don't-restate discipline `:102-104` already uses).
2. **Make the framing's trigger name generation explicitly.** `:86`'s "Before any license-based
   capacity or sampling decision" should say, in as many words, that **choosing how many records to
   generate** is such a decision. Sizing a dataset into existence and sampling one down are the
   same decision under this rule, and only one of them is currently recognizable in the wording.
3. **Say what the answer usually is.** On a measured `recordLimit: 0` the generated dataset is
   sized by what the *scenario* needs, not by any cap — state that outcome, so the branch resolves
   rather than merely warning.

Do **not** move Step 8a's measurement procedure, and do not duplicate it into Step 2. The
`inv244-…` implementation already recorded that a third copy of the procedure would be the same
mistake one level down; what is missing is a **reference** at the decision site, not a fourth copy.

## Acceptance criteria

- [ ] `module-04-data-collection/SKILL.md`'s `provenance: synthesized` branch states that choosing
      the generated record counts is a license-capacity decision, cites INV-244, and routes to the
      canonical framing block rather than restating the measurement procedure.
- [ ] The canonical framing's trigger sentence (`:86`) names **generating** a dataset, not only
      sampling one, as a decision it governs.
- [ ] The branch states the `recordLimit: 0` outcome plainly: size the generated data by what the
      scenario needs.
- [ ] A test asserts the synthesized branch carries a license-capacity reference, and fails if it
      is removed — pinning the *mechanism* (measure before sizing) rather than merely that a token
      appears somewhere in the file, per the guard-strengthening note in
      `license-limit-assumed-when-it-could-be-measured`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the `provenance:
  synthesized` branch at `:200-258` (add the routing directive) and the framing trigger at `:86`.
- `tests/test_module06_license_reconciliation.py` — extend, or add a sibling; its
  `discover_branches()` derivation is the right shape to reuse (INV-246).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Data collection: dataset sized against an assumed limit before measuring the real one" (2026-08-15, Module Data collection; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). The finding is internal to the plugin — a correct rule that is not reachable from the site it binds. The Senzing facts the fix routes to, `SzProduct.get_license()` and `recordLimit`, are already cited in the file (server 1.32.9, 2026-08-14) and must be re-asked at implementation time per INV-080 rather than carried from here. `recordLimit` remains observation-only: `module-04-data-collection/SKILL.md:800` already records that `get_license` has no `response_schemas` entry.
- Upstream: not applicable — routed `plugin`.
- Related specs: `specs/inv244-absent-license-branch-exists-in-module-4-too.md` (fixed the branch this spec finds unreachable), `specs/license-limit-assumed-when-it-could-be-measured.md` (established INV-244), `specs/synthesized-scenarios-make-the-quality-gate-unreachable.md` (the sibling directive in the same branch)

## Why this is a third instance, not a repeat

The two prior specs each fixed a **site that reads `license_record_limit`**. This one is not such a
site: Step 2 never reads the field at all — it makes the decision the field exists to inform,
without consulting it. Sweeping every branch on `license_record_limit` (INV-246's derivation) will
never find it, because there is no branch to find. That is worth recording: a guard derived from
"every site that reads the field" is sound for the rule it enforces and structurally blind to the
site where the field is ignored entirely.
