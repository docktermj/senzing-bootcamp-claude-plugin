# `model-selection.md`'s per-skill table omits `bootcamp-preparation`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/docs/model-selection.md` carries **two** model/effort tables cut
differently, and they disagree about how many stages exist:

| Table | Cut by | Rows |
|---|---|---|
| `:84-96` — Skill / Workload / Best value / Rationale | skill file | **11** |
| `:157-170` — Stage / Recommended / CLI commands | stage | **12** |

Twelve skills ship under `plugins/senzing-bootcamp/skills/`. The per-skill table lists eleven; the
one it omits is **`bootcamp-preparation`**. Every other shipped skill has a row.

The per-stage table is complete and correct — `Bootcamp preparation | Sonnet 5, medium effort |
/model sonnet · /effort medium` at `:160` — so **INV-140 is satisfied** ("every stage … exactly one
row in the per-stage model/effort recommendation table, including the apparatus-exempt setup stages
(Onboarding, Bootcamp preparation, Entity Resolution Concepts …)"). That parenthetical naming
`Bootcamp preparation` explicitly is also the evidence this omission is an oversight rather than a
deliberate exemption.

What is missing is the **rationale**. The per-skill table is the only place that records *why* a
stage gets the model it gets — its Workload and Rationale columns are what a future re-assessment
reads. For `bootcamp-preparation` a reader finds a recommendation with no reasoning behind it, in a
file whose own header says the last re-assessment happened because *"the original 2026-07-16
evaluation was never re-read against the modules as they later became, and two rows had gone
stale."* A row that does not exist cannot be re-read at all.

## Root cause

The per-skill table is dated **"Re-assessed 2026-07-26"**; the Bootcamp preparation stage was
established by **INV-075**, which relocated the verbosity and language questions out of the preface
into a preparation module. The stage was added to the per-stage table and to INV-140's own
parenthetical, and the per-skill table was not extended with it.

Nothing catches this: INV-140 binds the *per-stage* table, which is complete, so the invariant is
honored while its sibling table is one row short. No test compares either table against the shipped
skills directory — a `ls plugins/senzing-bootcamp/skills/` versus table-rows check would have caught
it on the day the stage landed.

## Proposed change

1. **Add a `bootcamp-preparation` row** to the per-skill table at `:84-96`, positioned between
   `bootcamp-onboarding` and `module-00-entity-resolution-concepts` so the table's order continues to
   match the run order (and the per-stage table's order). Its recommendation must be the one already
   published for the stage — **Sonnet 5, medium** (`:160`) — and the Workload and Rationale columns
   should describe what the stage actually does: capture the setup preferences (verbosity, language,
   path choice and module selection) that INV-075 and INV-076 relocated there, a protocol-adherence
   and exact-wording workload rather than a code one, which is the same reasoning
   `bootcamp-onboarding` carries.
2. **Add a guard** asserting every directory under `plugins/senzing-bootcamp/skills/` has a row in
   **both** tables, so the next stage added cannot land in one and miss the other.

**What stays:** both tables, both cuts, and the ↑ markers recording which rows changed at the
2026-07-26 re-assessment. This adds a row; it removes nothing.

## Acceptance criteria

- [ ] The per-skill table at `:84-96` has a `bootcamp-preparation` row whose Best value is
      **Sonnet 5, medium**, matching `:160` exactly.
- [ ] The row names exactly one model and one reasoning effort, with no conditional or two-branch
      recommendation (**INV-141**).
- [ ] Its position keeps the table in run order.
- [ ] A test asserts every skill directory appears in **both** the per-skill and per-stage tables,
      and fails if either table gains or loses a stage without the other — **negative-controlled** by
      deleting one row from each table in turn, confirming both failures, then reverting.
- [ ] The per-stage table is unchanged; **INV-140 was already satisfied** and this spec does not
      alter it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/docs/model-selection.md` — one row added at `:84-96`.
- `tests/` — a new guard comparing both tables against the shipped skills directory.

## Source

- Skill: `production-readiness-audit`, 2026-08-13. Found by the **completeness** sweep while checking
  INV-140 and INV-141, both of which turned out to be honored — the defect is in the sibling table
  neither invariant binds.
- Priority: **Low.** Nothing a Bootcamper experiences changes: the stage has a published
  recommendation and the switch-question machinery reads the per-stage table. The cost is to future
  maintenance — the rationale that a re-assessment needs is absent for one stage.
- MCP re-check: **n/a (no Senzing fact)** — this is internal documentation consistency. Model names
  and prices in this file are Claude-platform facts, not Senzing facts, and are untouched here.
- Related: INV-140 (per-stage completeness, satisfied), INV-141 (one model + one effort, satisfied),
  INV-075 (which created the stage).
