# Twelve hard rules cite no invariant, and each needs one of three different fixes

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py rules` reports hard rules — the repo's `⛔` / bolded MUST/NEVER convention — whose
enclosing section cites no invariant. After the 2026-08-13 audit fixed one of them, **14 remain out of
213 hard-rule lines, across 12 files.** Two were resolved that day (`:197` gained INV-218; Step 1's
fallback region gained INV-001/INV-163); the rest are untriaged:

| `file:line` | The rule, abbreviated |
|---|---|
| `graduation/SKILL.md:920` | ⛔ When `database_type` is indeterminate, do not guess a branch — determine the engine from … |
| `module-00-entity-resolution-concepts/concepts.md:29` | ⛔ Prefer these queries, and when a query returns nothing relevant, RE-QUERY with … |
| `module-01-business-problem/phase2-document-confirm.md:7` | ⛔ Branch on scenario provenance first — never ask a bootcamper for diagrams of a scenario … |
| `module-02-sdk-setup/SKILL.md:1178` | NEVER construct engine configuration JSON manually: always use the exact JSON from … |
| `module-03b-truthset-visualization/phase1-visualization.md:347` | ⛔ If the visualization's code changes for any reason after 2.2 … |
| `module-03b-truthset-visualization/visualization-api-reference.md:718` | No redundant inline record listings. Where an entity list offers the Records action … |
| `module-03b-truthset-visualization/visualization-api-reference.md:833` | Legible labels when shown. On-canvas node labels MUST avoid unreadable overlap … |
| `module-05-data-quality-mapping/SKILL.md:40` | ⛔ Because the completeness helper is authored fresh each run until that guide is ported … |
| `module-05-data-quality-mapping/phase1-quality-assessment.md:14` | ⛔ Do not take the source list from `docs/business_problem.md` … |
| `module-05-data-quality-mapping/phase2-data-mapping.md:482` | ⛔ Before you advance, check the profile for a second entity hiding in a column … |
| `module-05-data-quality-mapping/phase2-data-mapping.md:1058` | ⛔ Before starting the next source's `mapping_workflow(action='start')` … |
| `module-05-data-quality-mapping/phase3-test-load.md:264` | ⛔ Before fixing anything, sort the findings the way `phase2-data-mapping.md` requires … |
| `module-06-data-processing/phaseC-multi-source.md:153` | ⛔ Same batch-drain requirement as Phase B, step 9 — read it there rather than re-deriving it |
| `module-07-query-visualize-discover/phase2-discover.md:44` | ⛔ Declining skips the walkthrough, not the findings … |

Each is **one of three things**, and they need different fixes:

- **An unregistered rule** — the plugin guarantees something the ruleset does not record. Nothing
  binds future work to it and nothing notices a later contradiction. This is the mechanism behind
  INV-134, INV-155 and INV-218.
- **A missing citation** — the rule *is* registered and the text just does not say which invariant
  governs. Not cosmetic: INV-183 requires a step that generates an artifact to name its governing
  rules **at that step**, and a rule with no ID is one a later editor cannot look up.
- **Not a durable rule** — a local instruction, one-off phrasing, or pedagogy. Out of scope.

Several are visibly likely to be the middle case — `:153` is an explicit cross-reference to Phase B,
`:264` points at `phase2-data-mapping.md`'s ordering, `:1058` is the per-source workspace hygiene
INV-177 governs — but *which* invariant governs each requires reading the rule and searching
`INVARIANTS.md` for its subject, which no regex can do.

## Root cause

The scan is a lead generator and was built as one. Its output has been read opportunistically —
whichever hits a given audit happened to pass through — so the list persists at roughly constant size
while individual entries turn over. The 2026-07-31 audit measured 16 uncited of 162; today it is 14 of
213, so the *rate* improved while the backlog never cleared.

There is no record of a decision on any individual line, which is the compounding cost: a later run
cannot tell "examined and judged not durable" from "never looked at", so it re-derives.

## Proposed change

**Triage all 14, one at a time, and record a verdict per line so no future run re-derives it.** For
each: read the rule, search `INVARIANTS.md` for its subject, and assign exactly one of the three
verdicts above.

Then, by verdict:

- **Missing citation** → add the citation inline. Cheapest and highest-value; do these first.
- **Unregistered rule** → draft the invariant and get the maintainer's sign-off before recording
  (`implement-spec` Step 5). ⛔ **Do not batch-register.** Each proposed invariant is permanent and
  binds every future spec, so each needs its own decision, and a run that proposes ten at once will
  get a rubber stamp or a refusal rather than a judgement.
- **Not durable** → record the verdict and the reason, so the line is not re-triaged.

**Where to record the verdicts.** They are per-line decisions about the plugin's own ruleset, which is
`INVARIANTS.md`-adjacent but not an invariant. Put them in this spec's ledger entry as a table, in the
`deep-dive-audit-*` precedent's style — one row per line, verdict, and what was done. That keeps them
in the record `implement-spec` Step 1 already reads.

**Sequence it so a partial run is still useful:** do the citations first, then the not-durable
verdicts, then propose invariants one at a time. A run that gets through half has still permanently
removed half the backlog, and the ledger says which half.

## Acceptance criteria

- [ ] All 14 lines have a recorded verdict — `missing citation`, `unregistered rule`, or
      `not a durable rule` — with the reason, in the ledger entry as a table.
- [ ] Every `missing citation` line names its governing invariant inline, and the invariant's subject
      genuinely matches the claim (checked by reading `INVARIANTS.md`, not by ID plausibility — the
      INV-129/INV-218 defect was a citation that existed and was wrong).
- [ ] No invariant is recorded without the maintainer's explicit sign-off on its wording, and none is
      proposed in a batch.
- [ ] `conformance.py rules` reports a count reduced by the number of lines that got a citation, and
      the remainder is accounted for by the recorded `not a durable rule` verdicts.
- [ ] No rule's **text** is weakened, shortened, or reworded to satisfy the scan — a citation is
      added, or a verdict is recorded. ⛔ Rationale is never cut (the `deep-dive-audit-2026-07-28b`
      precedent: a corrected example with its reason stripped got "helpfully" corrected back).
- [ ] Full suite green, `citations.py verify` clean **after** the entry is written.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- Up to 12 files under `plugins/senzing-bootcamp/skills/`, citation-only edits.
- `specs/INVARIANTS.md` — only for lines judged `unregistered rule`, and only with sign-off.
- `specs/IMPLEMENTED.md` — the per-line verdict table.

## Source

- Feedback: none — self-observed; the list is `conformance.py rules` output from the 2026-08-13
  `production-readiness-audit`, which triaged one line and disclosed the rest as untriaged
  (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium.** No bootcamper-facing behaviour changes. The value is that the reverse
  direction of the invariant contract is where this repo has repeatedly lost weeks — INV-060 and
  INV-097 each stood unimplemented for over a month, invisibly, because no test cited them.
- MCP re-check: **n/a (no Senzing fact)** for the triage itself. ⚠️ Several candidate lines *contain*
  Senzing facts (`:1178`'s engine-configuration JSON rule, `:1058`'s `mapping_workflow` sequencing,
  `:29`'s prescribed queries). Any fact quoted or restated while adding a citation MUST be re-asked
  against the live server that session (INV-080) — adding a citation is not licence to carry the
  surrounding fact forward unverified.
- Upstream: not applicable.
- Related specs: `install-verification-has-no-invariant-so-inv129-is-borrowed` (the one line already
  triaged, and the wrong-citation case the scan cannot see), INV-183 (name the governing rule at the
  step), INV-182 (per-criterion evidence in the ledger).

## Invariants introduced

- `INV-220` — Where a step branches on material the bootcamp may have authored itself, the branch
  MUST be taken from the **provenance already recorded earlier in the run** — never from a second
  mechanism introduced at that step, and never from a question to the Bootcamper, since a question
  about a scenario the bootcamp invented has no true answer (recorded in `specs/INVARIANTS.md`,
  indexed under *Questions, gates and bootcamper-facing conversation*).
- `INV-221` — Where a bootcamper-facing surface offers an action that opens a piece of content, that
  surface MUST NOT also render the same content inline (recorded in `specs/INVARIANTS.md`, indexed
  under *Visualization and screenshots*).

Both were approved by the maintainer on 2026-08-13, each on its own decision rather than as a batch,
per this spec's ⛔ on batch registration. The maintainer chose the **generalized** wording for
INV-221 over the narrow entity-lists-only form that matched the shipped text exactly.

## Deviations from this spec, and why (2026-08-13)

- **The engine-configuration line's fix changed, and the change came from the MCP re-check the spec
  itself demanded.** The spec listed `module-02-sdk-setup/SKILL.md:1178` (now `:1210`) as a
  citation-only edit and flagged that it *contains* a Senzing fact to re-ask. Re-asked on server
  **1.32.9, 2026-08-13:** `sdk_guide(topic='configure', language='python')` returns the
  config-bootstrap code (`init_default_config.py`) and **no `engine_config` block at all**;
  `sdk_guide(topic='configure')` with no language returns the language decision tree; only
  `sdk_guide(topic='configure', platform='linux_apt', language='python')` returns
  `environment.engine_config` carrying CONFIGPATH, RESOURCEPATH and SUPPORTPATH. The bullet named the
  route **without `platform`**, so the call as written returns nothing to use — while Step 8's
  canonical statement at `:965` has always passed `platform` and is correct. The edit therefore added
  the citation **and** corrected the call, with the dated evidence inline. This exceeds
  "citation-only edits" in `## Affected files`; it does not weaken the rule (criterion 5) — the rule
  gained a ⛔ and lost nothing.
- **No line was judged `not a durable rule`,** so criterion 4's arithmetic does not hold as written:
  it predicted a reduced count with "the remainder accounted for by the recorded not-a-durable-rule
  verdicts", and the remainder is **zero** — 12 citations plus 2 registered invariants closed all 14.
  The hard-rule **total** rose 213 → 214 because the correction above added a new ⛔ line, which sits
  in a section that now cites INV-080.
- **A guard shipped beyond the acceptance criteria.** `tests/test_hard_rule_citations.py` (6 tests,
  5 mutations, all caught) asserts both new citations and both new invariant texts. No criterion asked
  for it; INV-220 and INV-221 were scored uncited by `coverage_reports.py invariants` the moment they
  were appended, which is precisely the blind spot this spec's `## Root cause` is about.
