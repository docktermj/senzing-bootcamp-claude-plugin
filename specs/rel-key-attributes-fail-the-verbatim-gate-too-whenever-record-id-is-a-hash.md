# The verbatim check's un-re-run limitation now has its run — and it refines the entry: `REL_ANCHOR_KEY` and `REL_POINTER_KEY` fail too whenever `record_id_source` is `RECORD_HASH`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`phase2-data-mapping.md` records three `sz_verbatim_check.py` limitations and flags limitation 2 —
`REL_ANCHOR_DOMAIN` / `REL_POINTER_DOMAIN` / `REL_POINTER_ROLE` rejected — as **the one entry never
re-run**, naming exactly what would confirm it: *"a source carrying disclosed relationships"*. A run
on 2026-08-18 had one.

**It fires, exactly as described.** And it refines the entry in a way that matters, because the
plugin's current text tells the reader to expect something that did not happen.

The text says `REL_ANCHOR_KEY` and `REL_POINTER_KEY` **pass** "because those do carry source
values". That holds only when `record_id_source` names a source field. On this run the embedded
master used the `RECORD_HASH` sentinel, so the key is a **derived hash that appears nowhere in the
source** — and both KEY attributes failed alongside the DOMAIN and ROLE attributes.

Measured, and self-reconciling:

```text
83,338 offenders  =  25,000 senders      x 3 pointer attributes (DOMAIN, KEY, ROLE)
                  +   4,169 beneficiaries x 2 anchor  attributes (DOMAIN, KEY)
```

`75,000 + 8,338 = 83,338`. Every offender was relationship scaffolding; **no data value was
implicated.** The arithmetic closing exactly is what establishes that both KEY attributes are in the
offender set rather than a subset of records being at fault.

**Why the current wording costs more than a missing detail.** A reader following it expects KEY to
pass. When it fails they have been told, in effect, that the cause identified for DOMAIN/ROLE does
*not* apply here — so the natural reading is *a mapping defect in my keys*, not *the same checker
limitation, one field wider*. The step's own gate wording ("a code bug: fix the mapper … Do NOT
proceed until it passes") points the same direction. That is an iterate-forever loop on correct
code, which INV-048/INV-173 exist to prevent, entered through the sentence meant to prevent it.

**And this is the normal case, not an edge one.** `RECORD_HASH` is what an `embedded_master` uses —
a name embedded in someone else's row has no per-record natural key of its own
(`phase2-data-mapping.md:320-322`) — and `embedded_master` is the disposition that *produces* REL_*
scaffolding in the first place. So the configuration where the current text is wrong is the
configuration that reaches limitation 2.

## Root cause

**The claim about KEY was reasoned from the mechanism, not measured.**
`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:818-830`,
limitation 2:

> ⚠️ **This is the one entry still NOT re-run** — "expect this, and check". Confirming it needs a
> source carrying disclosed relationships. … These are structural constants that by definition have
> no source value, so the harvester cannot see them and `is_exempt()`'s waiver — `DATA_SOURCE`,
> `RECORD_ID`, and any attribute ending `_TYPE` — does not cover them. `REL_ANCHOR_KEY` and
> `REL_POINTER_KEY` **pass**, because those do carry source values, which is what identifies the
> cause.

The mechanism is right and the KEY conclusion overreaches it. The harvester's scope is **source
values**; `is_exempt()` waives `DATA_SOURCE`, `RECORD_ID` and `*_TYPE`. A REL_*_KEY carries a source
value **only when the RECORD_ID it mirrors came from a source field.** When RECORD_ID is a hash, the
key is derived, the harvester cannot see it, and `is_exempt()` does not waive it — the same two
conditions that fail DOMAIN and ROLE. The text stated an unconditional pass for a conditional case,
and the condition it depends on is invisible in the sentence.

**This is the class INV-169 governs**, reached from the positive side: a single configuration's
observation ("KEY carries a source value") generalized into an absolute about the attribute. And it
is the same root cause as `verbatim-check-cannot-see-field-name-derived-values` — the harvester's
value-only scope — reaching a different attribute family by a different route (a hash rather than a
field name).

**Freshness re-checked, server 1.33.0, 2026-08-21.** The mechanism the refinement depends on is
still current: `mapping_workflow`'s step-2 advance schema still documents `record_id_source` as
*"field name of the stable natural key (PREFERRED), or RECORD_HASH only when no stable unique field
exists"*, and its step-4 instructions still say that on the sentinel the mapper must *"generate
RECORD_ID as a deterministic hash over that entity's stable IDENTITY fields only"*. So a
`RECORD_HASH` RECORD_ID is still a computed value with no source occurrence, which is the whole
refinement. Both re-read from the live step-2 and step-4 responses.

⚠️ **The end-to-end rejection itself is observation-only** (INV-080/INV-149): it was measured on the
Bootcamper's engine and data, and no MCP route can report what the delivered script does to a
particular mapping. Record it with its conditions — SDK/plugin version, `embedded_master` with
`RECORD_HASH`, 2026-08-18 — never as an MCP-sourced claim.

## Proposed change

1. **Retire the "NOT re-run" caveat on limitation 2.** It has been run. Replace it with the
   confirmation and its date, matching how limitations 1 and 3 are already stamped
   ("CONFIRMED CURRENT — server …"), and note that the confirmation is an engine-side observation
   rather than an MCP re-read.

2. **Correct the KEY claim to the conditional it actually is.** `REL_ANCHOR_KEY` and
   `REL_POINTER_KEY` pass **only** when `record_id_source` names a source field; when it is the
   `RECORD_HASH` sentinel they fail alongside DOMAIN and ROLE, because the key is then derived and
   the harvester cannot see it either. Say which condition the reader is in — they chose it at
   step 2 and can check it.

3. **Say that the RECORD_HASH case is the expected one for `embedded_master`,** so the reader meets
   the wider failure set already expecting it rather than diagnosing it. Cross-reference `:320-322`,
   where the sentinel is introduced.

4. **Record the offender-count reconciliation as the procedure, not just as evidence.** The way to
   tell this limitation from a real mapping defect is that the offender count reconciles to
   `records x REL_* attributes` and every offender is scaffolding. A reader who can check that can
   take the exemption path with confidence instead of iterating. Give them the arithmetic.

5. **Fold the finding into the shared root cause.** Limitation 2 and
   `verbatim-check-cannot-see-field-name-derived-values` are one mechanism — the harvester sees
   source *values* only — with three known reachings: non-string values, values derived from a field
   *name*, and values derived from a *hash*. State it once as the general rule and list the three,
   so the fourth is recognized on sight rather than filed as a new discovery.

## Acceptance criteria

- [ ] Limitation 2 no longer carries the "NOT re-run" caveat and records its confirmation date and
      conditions, marked observation-only.
- [ ] The KEY claim is conditional on `record_id_source`, and names the `RECORD_HASH` case as
      failing.
- [ ] The text says `embedded_master` normally uses `RECORD_HASH`, so the wider failure set is the
      expected outcome on the disposition that produces REL_* scaffolding.
- [ ] The offender-count reconciliation is given as the test that distinguishes this limitation from
      a mapping defect.
- [ ] The harvester's value-only scope is stated once with all three known reachings (non-string,
      field-name-derived, hash-derived).
- [ ] No shipped file states that `REL_ANCHOR_KEY` or `REL_POINTER_KEY` passes the verbatim check
      unconditionally, and a guard asserts it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` —
  limitation 2 (`:818-830`), the freshness header (`:792-800`), and the shared-root-cause statement;
  cross-reference from `:320-322`
- `tests/` — guard against an unconditional REL_*_KEY pass claim

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew.md` → "Improvement: REL_* attributes fail the
  verbatim gate — the un-re-run limitation, now confirmed and refined" (2026-08-18, Module Data
  Quality, Mapping, and Transformation; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**. The mechanism the refinement rests
  on is current: `mapping_workflow` step 2's advance schema documents `record_id_source` as *"field
  name of the stable natural key (PREFERRED), or RECORD_HASH only when no stable unique field
  exists"*, and step 4's instructions still prescribe a deterministic hash over identity fields on
  the sentinel — both re-read from a live workflow run (start → step 4). The end-to-end rejection is
  engine-side and marked observation-only. No absence is asserted against the server.
- Upstream: already offered and **declined by the maintainer** (per the entry's `Upstream:` field).
  The plugin fix stands on its own.
- Related specs: `specs/reverify-the-three-verbatim-check-limitations.md`,
  `specs/verbatim-check-cannot-see-field-name-derived-values.md`,
  `specs/verbatim-check-rejects-extract-and-relationship-scaffolding.md`,
  `specs/verbatim-check-numeric-source-values.md`

## Deviations from this spec, and why (2026-08-21)

**Implemented as one commit with its two sibling Module 5 specs, not three.** All three edit
`phase2-data-mapping.md`, and their changes interleave inside one block — the freshness header, the
field-count block, limitation 2 and step 10. Splitting them into three commits would have produced
**red intermediate commits**: each prose change has a guard pinning the claim it replaces, so a
commit carrying the prose without its guard update (or the reverse) fails the suite. The repo's
one-commit-per-spec pattern assumes specs touch disjoint files; here it would trade a clean history
for commits that do not individually pass. The commit message names all three specs.

**Eight guard assertions were inverted rather than deleted.** Across
`tests/test_verbatim_check_limitation.py` and `tests/test_verbatim_check_limitations_freshness.py`,
assertions pinning "limitation 2 is un-re-run", "the field-count warning no longer fires" and the
retired `MCP-NEGATIVE` marker asserted claims these changes disprove. Each was rewritten to assert
the new claim with a docstring recording what changed and why keeping the old one would be worse
than no guard — the freshness guard had even written down its own trigger condition (*"needs a source
with disclosed relationships, which was not available"*), and that condition was met on 2026-08-18.
