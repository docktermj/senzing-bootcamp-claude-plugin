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
   semantically wrong mapping and that the match-key audit is what does — this generalizes
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

## Deviations from this spec, and why (2026-07-31)

**Item 4 was already implemented, by work that predates this spec.** The spec calls it the part
"worth shipping even if 1–3 are deferred" and the one that "protects the next Bootcamper rather
than the next maintainer" — and it was already shipped:

- `module-05-data-quality-mapping/phase1-quality-assessment.md:285-291` already says the score
  measures "all *structural* properties of one source in isolation", "says nothing about whether a
  field will be mapped to a feature that **means** the same thing", that "a source can score 86%
  and still carry a mapping that suppresses legitimate merges", and that "semantic correctness is
  only established after loading, by the match-key audit in Data processing" — which names the
  match-key audit as what can, exactly as criterion 4 requires.
- `module-06-data-processing/phaseD-validation.md:179+` already carries the audit itself, opening
  with "Every mapping gate the bootcamp runs before this point is **static, single-source, and
  structural** — the analyzer, the verbatim check, the routing report, the quality score. None of
  them evaluates *meaning*" — and a worked example of **the same `EFX_YREST` / `REGISTRATION_DATE`
  case** this entry describes, noting "All five static gates passed; the quality score was 86.3%".

Both arrived in commit `0c0ec44` ("Add semantic mapping validation to modules 5 and 6"). So
**nothing was added for item 4.** It is instead *pinned* — `TheScoreCannotDetectSemanticsGuidanceStays`
asserts all four claims, because a criterion this spec names is a guarantee that should not be one
refactor from gone, and it was previously unasserted. `phase1-quality-assessment.md` is therefore in
this spec's Affected files but deliberately **unmodified**.

⚠️ Note the numbers differ between the two accounts of that case — this entry reports 345 of 2,651
comparisons (13.0%) and 826→876 entities; `phaseD-validation.md` reports "up to 676 records",
merges 1→4 and links 160→170. Different runs or different measurements; they are **not** reconciled
here and neither was edited to match the other.

**"Wherever a data-quality score is presented" was scoped by reading each site, not by
duplication.** Six shipped files mention a quality score. Two *present it as a decision* and both
carry the caveat: `phase1-quality-assessment.md` (the ≥80/70–79/<70 proceed gate) and
`phaseD-validation.md` (the iterate-vs-proceed gate). The other four do not and were left alone —
`module-04-data-collection/SKILL.md` (a passing "quality scored well" clause),
`module-05.../phase2-data-mapping.md` (a verbose-mode display), `module-06.../phaseC-multi-source.md`
(a summary-table column), and `module-07.../phase1-query-visualize.md` (a troubleshooting checklist
item when zero duplicates are found). Copying the paragraph into all four would fight the same
compaction principle this repo applies elsewhere, and none of them is where a Bootcamper decides
anything on the number. Recorded rather than silently narrowed.

**The trigger fires at the step, not only centrally.** A rule stated once in `ground-rules.md` is a
rule nobody reads at the moment it applies (INV-183), so the match-key audit gained a sixth step:
if a finding there changes or withdraws a mapping, file it *then*. `phaseD-validation.md` is not in
this spec's Affected files; it is the step that actually detects condition 1, so it is where the
obligation belongs.

**Dedup was added, unprompted.** With an in-run path *and* a graduation retrospective writing to one
file, the same finding gets filed twice. The in-run rule says to note that it filed; graduation's
Step 0 now reads existing entries first and skips anything already recorded. The spec does not
mention this and it would have been a visible defect on the first real run.

**No Senzing fact was promoted, and that is asserted.** The entry's `REGISTRATION_DATE` semantics,
TRUSTED_ID type interaction and `SCORE_BEHAVIOR` values stay out of the shipped rule.
`test_no_new_senzing_fact_was_added_to_the_shipped_rule` fails if any of them appears there —
mutation-proven by inserting one, which the guard catches (INV-080/INV-194).

**Not runtime-verifiable:** whether an in-run reversal actually gets filed can only be observed in a
live bootcamp with a loaded engine, which this environment does not have. What is verified here is
that the trigger, its three conditions, the silent non-blocking append, the sweep and the dedup are
all stated where they must be, and that an entry written to this template still parses with
`feedback_ledger.py check` (run, not asserted from the spec).

## Invariants introduced

- None. INV-012 (no interruption), INV-048 (never block), INV-116 (`Source:` distinguishes who
  noticed), INV-183 (rules at the step) and INV-080/INV-194 (no unverified Senzing fact) all already
  applied and are asserted here rather than extended. The durable half of this change is the named
  trigger itself, which is guidance rather than a new standing constraint.
