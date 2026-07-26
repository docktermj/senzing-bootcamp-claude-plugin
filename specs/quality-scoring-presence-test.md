# Define the completeness presence test instead of leaving it to be re-invented

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5's per-source quality score is computed from field completeness, format consistency, and
duplicate rate, and the skill currently asks the assistant to author that computation fresh each run.
In one session the hand-written completeness helper reported **NOMINO-RISK identifier coverage as
100%** when the true figure was **0%** — `IDENTIFIER_LIST` was an empty array in all 14,119 records.
The error was caught and corrected in-session, and the correction documented in
`docs/data_source_evaluation.md`.

Completeness feeds the per-source quality score that **gates the module** (≥80% proceed / 70-79% warn
/ <70% strongly recommend fixing). An inverted coverage figure for the very field family that supplies
exclusive identifiers is a materially wrong input to mapping decisions — and it is the kind of wrong
number that looks entirely plausible on screen. Because the plugin asks the assistant to write this
helper fresh each run, the trap is available to **every session** rather than being fixed once.

## Root cause

**The durable, confirmed cause:** there is no defined presence test to implement against.

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md:144-145`
  says only "compute a quality score based on field completeness, format consistency, and duplicate
  rate" and then applies thresholds to the result. What counts as a *present* value is never stated.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md:35-39` confirms this is
  deliberate for now: "The standalone `QUALITY_SCORING_METHODOLOGY` guide is a later porting phase;
  for now use [the Phase 1 dimension definitions]." Those definitions name the dimensions but do not
  define their measurement.

So each run re-derives a presence predicate. Getting it wrong produces a number, not an error.

**The specific mechanism reported does not reproduce — flagged as Unverified.** The feedback entry
attributes the inversion to a falsy-membership trap in `value not in (None, "", [], {})`. Tested
directly on Python 3.12:

```text
False        not in (None, "", [], {})  -> True   (counted PRESENT)
0            not in (None, "", [], {})  -> True   (counted PRESENT)
empty list   not in (None, "", [], {})  -> False  (counted absent)   ← the reported case
empty dict   not in (None, "", [], {})  -> False  (counted absent)
empty tuple  not in (None, "", [], {})  -> True   (counted PRESENT)
```

That predicate counts an **empty list as absent**, which is correct — so it cannot have produced 100%
for an all-empty `IDENTIFIER_LIST`. The entry's stated defect and its stated fix also point in
opposite directions: it reports `False`/`0` being counted as present as the bug, while its suggested
fix asks that `False` and `0` **should** count as present (which is right — a boolean `false` and a
numeric `0` are real values, not missing data).

The symptom is real and was corrected in-session; the mechanism as written is not the one that bit.
**The most likely actual mechanism, needing investigation:** the helper tested for *key presence*
(`"IDENTIFIER_LIST" in record`) rather than *value emptiness* — which would yield exactly 100% when
every record carries the key with an empty array. A container-of-empty-values case
(`[{}]`, `[""]`) would do the same. Confirm against the session's `src/scripts/assess_sources.py` if
it is still available; otherwise treat the mechanism as unknown and fix the class.

Either way the fix is the same, and it does not depend on resolving which predicate was used: define
the test once so it is not re-derived.

## Proposed change

**1. Define the presence test in the Phase 1 dimension definitions**, as an explicit emptiness test
rather than a truthiness or membership test:

A field value is **present** unless it is:
- `null`/absent, or the key is missing from the record;
- an empty or whitespace-only string;
- an empty container (`len(value) == 0` for lists, dicts, sets, tuples);
- a container all of whose elements are themselves empty by these rules (e.g. `[""]`, `[{}]`) — the
  case that makes an "all records have the field" count read as full coverage.

Everything else is present. State explicitly that **`false` and `0` (and `0.0`) count as present** —
they are values, not absences — and that presence is a property of the **value**, never of the key.

**2. Add the pitfall as a one-line caution now**, in Module 5's "Quality scoring methodology"
reference note, since the standalone guide is a later porting phase and the helper is authored fresh
each run until then. Name the two traps concretely: never use a truthiness test (`if value:`), and
never use key presence as coverage.

**3. Require a sanity check on any 0% or 100% coverage figure before it feeds the gate.** A field
family reporting exactly full or exactly zero coverage across every record is the signature of a
presence test measuring the wrong thing. Print one sample value for such a field and confirm the
figure against it before the score routes the module. This is the same INV-115 discipline — a
suspicious uniform result is a probable plumbing failure first — applied to profiling rather than to
SDK responses.

**4. Carry the definition into the port.** When the quality-scoring guide and validator are ported,
implement presence exactly as defined above and record the pitfall in the ported methodology guide,
so the definition does not diverge from the interim guidance.

## Acceptance criteria

- [ ] Phase 1's dimension definitions state the presence test explicitly, covering null/missing keys,
      empty and whitespace-only strings, empty containers, and containers of empty values.
- [ ] The guidance states that `false`, `0`, and `0.0` count as present, and that presence is a
      property of the value and never of the key.
- [ ] A source whose field is an empty array in **every** record reports **0%** coverage for that
      field, not 100%.
- [ ] A source whose field is `false` or `0` in every record reports **100%** coverage for that field.
- [ ] A field reporting exactly 0% or exactly 100% coverage has one sample value shown and checked
      against the figure before the quality score routes the iterate/proceed thresholds.
- [ ] Module 5's "Quality scoring methodology" reference note carries the truthiness-test and
      key-presence cautions.
- [ ] The per-source quality score and its thresholds are otherwise unchanged — this defines a
      measurement, it does not move a gate.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      presence test is stated in terms of values and containers, not Python idioms, since the helper
      is written in the bootcamper's chosen language (INV-002).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  define the presence test alongside the dimension definitions and thresholds (`:144-165`); add the
  uniform-coverage sanity check.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md` — add the pitfall caution
  to the "Quality scoring methodology" reference note (`:35-39`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "quality-scoring completeness checks should treat
  `False` and `0` as present values" (2026-07-26, Module Data Quality, Mapping, and Transformation;
  `Source: self-observed (assistant retrospective)`)
- Priority: Low (as filed; note the impact is a materially wrong number feeding a module gate)
- Related specs: `specs/detect-dynamic-key-document-shaped-sources.md` (INV-118 — the sibling
  profiling sanity check, for implausible field counts),
  `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115 — treat a suspicious empty/uniform
  result as a plumbing failure first), `specs/post-load-match-key-semantic-audit.md` (INV-117 — what
  the structural score explicitly does not establish),
  `specs/mapping-workflow-truncated-validation-errors.md` (the other Module 5 finding from this
  session).

## Invariants introduced

- `INV-128` — Field completeness MUST use an explicit emptiness test on the value (`false`/`0`
  present; key presence is not coverage), and a uniform 0%/100% figure MUST be confirmed against a
  sample value before it feeds a gate (recorded in `specs/INVARIANTS.md`).
