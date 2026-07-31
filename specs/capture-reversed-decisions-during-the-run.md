# Capture the bootcamp's own reversed decisions when they happen, not only from recall at graduation

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

A Bootcamper asked that the bootcamp determine — **during** the run as well as at graduation —
whether it made decisions that were wrong or had to be reversed, and capture them silently as
bootcamp feedback so future bootcamps do not repeat them.

The graduation half is already specified: `graduation/SKILL.md` runs a retrospective that
files entries with `Source: self-observed (assistant retrospective)`, and
`specs/graduation-assistant-retrospective-feedback.md` covers it. **The in-run half does not
exist.** No gate, hook, or checkpoint fires when a decision is reversed mid-bootcamp, so the
record depends entirely on the assistant remembering to write it down later — across a session
that had already crossed a compaction boundary when this was reported.

What that lost, from one run:

**Reversed after being acted on**

1. **`EFX_YREST` mapped to `REGISTRATION_DATE`.** Equifax's "year business established" was
   mapped onto the feature already carrying Enformion's incorporation `FilingDate`. A business
   commonly trades for years before incorporating, so the sources systematically disagreed and
   Senzing correctly suppressed merges over a conflict that was an artifact of the mapping — on
   345 of 2,651 cross-source comparisons (13.0%). Withdrawing it raised cross-source entities
   from 826 to 876. **Every static quality gate passed while this was wrong, and the
   data-quality score went UP when the bad mapping was added.** Only the match-key audit —
   reading the engine's own output — exposed it.
2. **Three defects in the quality-scoring implementation**, all authored by the assistant:
   person-oriented features averaged across organization records; linkage-only records scored
   as full profiles; partial addresses credited as complete. Correcting the second honestly
   *lowered* the reported score.

**Caught before being acted on**

3. **A proposed `TRUSTED_ID` remap**, presented as a fix for TRUSTED_ID comparisons scoring
   zero. Checking the Entity Specification first showed different TRUSTED_ID *types* do not
   interact, and the engine's own `SCORE_BEHAVIOR` values confirm it. Implementing it would
   have merged legally distinct entities across the whole dataset.

Items 1 and 3 are the significant ones: both are entity-resolution **semantics** errors —
mapping two differently-meaning source fields onto one feature, and misreading identifier-type
interaction — and both are the kind a Bootcamper working alone would plausibly make and not
catch. Item 1 actively degraded results (50 real customer matches suppressed) while every
automated indicator stayed green.

Four smaller in-flight corrections were also lost, two of which are the **same shape** the
skills already warn about — the half-populated row (INV-148): reusing `find_network` flags on
`find_path`, and omitting `SZ_ENTITY_INCLUDE_ENTITY_NAME` from `why_entities`. Both are now
separately specced, but their recurrence is itself evidence: the plugin warns about the pattern
and it still happened twice in one module.

## Root cause

The retrospective is specified at exactly one point — graduation — and depends on recall of a
session that may have been compacted. Nothing observes a reversal as it happens. This is the
same structural gap as `specs/nothing-writes-the-recap-checkpoint.md`: the consumer of a
record is specified and the producer is not.

## Proposed change

1. **Name the trigger, not the intention.** "Capture reversals" is unactionable; a condition
   is. The reporting entry supplies the reliable one: **the engine's own output, never a static
   gate.** All three significant errors were found by reading match keys, `SCORE_BEHAVIOR`, or
   the Entity Specification — not by any score or linter. So the in-run trigger should fire
   when *an audit of engine output causes a prior decision to be withdrawn* — concretely: a
   match-key audit finding leads to a mapping being changed or removed, a scoring
   implementation is corrected, or a proposed change is abandoned after an Entity
   Specification check. That would have caught items 1, 2 and 3 automatically.
2. **Append at the moment of reversal**, using the existing feedback machinery and
   `Source: self-observed (assistant retrospective)` — the same template, written when the
   reversal happens rather than recalled later. Silent, per the Bootcamper's request: no 👉
   question, no interruption (INV-012).
3. **Make graduation's retrospective sweep rather than recall.** It should explicitly look for
   withdrawn mappings, corrected scoring code, and abandoned proposals, instead of relying on
   what is still in context.
4. **Record the static-gate lesson where the gates live.** The most valuable single sentence in
   this entry is that a data-quality score *rose* when a bad mapping was added. Wherever the
   plugin presents a quality score, it should say plainly that the score cannot detect a
   semantically wrong mapping and that the match-key audit is what does — this generalises
   INV-174's applicability rule from *fields* to *mappings*.

Item 4 is worth shipping even if 1–3 are deferred: it is the part that protects the next
Bootcamper rather than the next maintainer.

## Acceptance criteria

- [ ] A named, checkable in-run trigger exists — not "notice reversals" but the specific
      conditions above — and firing it appends a feedback entry with
      `Source: self-observed (assistant retrospective)`.
- [ ] The append is silent: no 👉 question, no gate, nothing shown to the Bootcamper (INV-012).
- [ ] Graduation's retrospective explicitly sweeps for withdrawn mappings, corrected scoring
      code, and abandoned proposals, rather than relying on recall.
- [ ] Wherever a data-quality score is presented, the guidance states that the score cannot
      detect a semantically wrong mapping and names the match-key audit as what can.
- [ ] The feedback file's existing format is reused unchanged, so
      `feedback_ledger.py check` still parses entries the new path writes — verified by running
      it against a file containing one.
- [ ] Nothing in this path can block a module or graduation (INV-048).
- [ ] MCP re-check: n/a for the mechanism. ⚠️ The Senzing facts *quoted in the examples* —
      `REGISTRATION_DATE` semantics, TRUSTED_ID type interaction, `SCORE_BEHAVIOR` values — are
      **field observations from one run** and MUST NOT be written into shipped guidance without
      re-asking the server (INV-080). If the implementation cites any of them, it re-verifies
      first and carries the provenance.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — the in-run append path.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the retrospective sweep.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — where the trigger condition is stated once and linked.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — the score-cannot-detect-semantics note.
- `tests/` — the trigger assertion and the ledger-parses-it check.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Detect and capture the bootcamp's own bad
  or reversed decisions, during the run and at graduation" (2026-07-30, Module: Query,
  Visualize and Discover, raised as cross-module; `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a for the mechanism; the entry's illustrative Senzing facts are marked
  observation-only above and are **not** promoted by this spec (INV-080/INV-149).
- Upstream: not applicable.
- Related specs: `specs/graduation-assistant-retrospective-feedback.md` (**the graduation half,
  already implemented — this adds only the in-run half**),
  `specs/nothing-writes-the-recap-checkpoint.md` (the same specified-consumer /
  unspecified-producer shape), `specs/find-path-and-find-network-links-diverge.md` and
  `specs/why-entities-default-flags-has-no-composite-members.md` (two of this entry's smaller
  items, specced separately).
