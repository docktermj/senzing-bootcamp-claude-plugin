# INV-244 still carries the writer count its own guard rejects, and three sites still gloss a measured field as "never asked"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On 2026-08-28, `counting-the-writers-of-license-record-limit-is-the-wrong-invariant` established
that **counting the writers of `license_record_limit` is the wrong shape** — the count had been
wrong in every version it ever had — and replaced it at three shipped sites with the property it
actually rests on: *every step that writes the field writes only a measured value*. The guard
written for it, `tests/test_license_limit_is_written_only_from_a_measurement.py`, rejects **any**
count, including the true one, because "a guard accepting today's right number would have accepted
both previous wrong ones."

**The invariant those sites cite was never brought forward.** `specs/INVARIANTS.md`'s INV-244
still reads:

> The **only writer** of `license_record_limit` is Module 4's Step 8a gate, which is
> **volume-gated by design** and never fires for a small dataset — so the field is absent no
> matter what license is installed.

That sentence is the first of the three wrong counts the spec enumerates — *"the only writer … is
Module 4's Step 8a"* — quoted verbatim in the spec as false. The real set was already five write
sites across four steps at that point, and SDK setup's Step 5a was added as a writer on 2026-08-31.

**This is measured, not inferred:** running the guard's own count-matchers against INV-244's line
fires on `(?:its|the field's|the|a)\s+(?<![-\w])only\s+writer\b`. The claim the plugin spent a
spec, a rename and five negative controls eradicating from shipped prose still stands in the
invariant that every one of those sites cites as its authority — invisible to the guard only
because it scans `plugins/` (`PLUGIN.rglob("*.md")`, line 111) and `specs/INVARIANTS.md` is
dev-side.

**A second, smaller consequence of the same omission.** INV-244's general clause says absence
*"means **not asked**"*, and three sites mirror that word for a field nothing ever asks about:

- `module-06-data-processing/phaseA-build-loading.md:101` — *"that means "never asked", not "no
  custom license""*
- `module-06-data-processing/phaseA-build-loading.md:197` — ⛔ **this means "never asked", not "no
  custom license". Measure it, do not assume it.** (INV-244)
- `module-06-data-processing/phaseB-load-first-source.md:136` — ⛔ **"never asked", not "no custom
  license": measure before warning.** (INV-244)

Module 4 says the accurate thing at both of its sites — `module-04-data-collection/SKILL.md:112`
(⛔ **this means "never measured"**) and `:368` (*"means **never measured**, never "no custom
license""*) — as does SDK setup at `module-02-sdk-setup/SKILL.md:1193` (*"no measurement has been
taken yet"*). ⛔ **Each Module 6 site contradicts its own next sentence**, which explains that
absence is *"a measurement that did not happen"*.

"Asked" is not a neutral synonym here. INV-170 gives it a specific meaning in this ruleset — *"A
value the Bootcamper was **asked for** MUST outrank any value auto-detected"* — so glossing a
measured-only field as "never asked" points at the wrong remedy: ask the Bootcamper, when the
remedy is one SDK call. INV-134's *"detected, never asked"* vocabulary makes the collision worse.

## Root cause

Two halves of one omission: the 2026-08-28 property fix changed the shipped sites and the guard
and stopped there.

1. **The invariant's reason clause was not corrected.** It sits inside the "Observed 2026-08-14"
   narrative, which is a defensible reading of why it was left — a dated observation records what
   was true when taken. But it is written in the present tense as the standing premise for the
   rule, it is the sentence a reader consults to learn *why* absence is uninformative, and the
   plugin's own guard classes that phrasing as the defect. Whichever reading is right, the remedy
   is the same and costs nothing: a dated correction note, in place, changing no rule.
2. **The gloss was never unified.** INV-244 is a *general* rule about conditionally-written state
   fields, and for most of them "not asked" is exactly right. It is wrong only for a field written
   solely from a measurement — which is the one instance the invariant names.

## Proposed change

1. **Append a dated correction note to INV-244**, per `INVARIANTS.md`'s own maintenance rules —
   in place, never deleted or renumbered, changing no rule. It should say what was verified and
   when: the writer set is five write sites across four steps as of 2026-08-28, six with SDK
   setup's Step 5a from 2026-08-31, that the count is the wrong shape, and that the property the
   rule rests on is *written only from a measurement*. Cite the spec that established it.
2. **Unify the gloss at the three Module 6 sites** to the measured-field wording Module 4 and SDK
   setup already use, so no site contradicts its own explanation. Keep INV-244's general
   *"not asked"* clause as the general rule it is.
3. **Extend the guard to the ruleset, or state why not.** The cheapest correct option is to add
   `specs/INVARIANTS.md` to the count-matcher's corpus — the patterns already exist and already
   fire. ⚠️ **If it is extended, the exemption question must be answered explicitly**: a dated
   observation quoting a past state is a legitimate thing for an invariant to contain, so the
   guard needs either a scoped exemption for a quoted/dated clause or a decision that the
   correction note is sufficient and the invariant text must simply stop stating a count. Do not
   ship a guard whose only way to pass is deleting history.

## Acceptance criteria

- [ ] INV-244 carries a dated correction note recording the true writer set, that a count is the
      wrong shape, and the property the rule actually rests on; the rule itself is unchanged, and
      the invariant is neither deleted nor renumbered.
- [ ] Running the count-matchers from
      `tests/test_license_limit_is_written_only_from_a_measurement.py` over `specs/INVARIANTS.md`
      either reports nothing, or reports only clauses a stated, tested exemption covers.
- [ ] No shipped file glosses an absent `license_record_limit` as "never asked"; all six sites use
      the measured-field wording, and no site contradicts its own next sentence.
- [ ] INV-244's general *"not asked"* clause is preserved for conditionally-written fields
      generally — the fix must not narrow the invariant to the license case.
- [ ] The existing guard stays green, and its site set is still derived by scanning (INV-246).
- [ ] Negative-controlled: restoring "never asked" at one Module 6 site fails; restoring a writer
      count in INV-244 fails if the guard was extended.
- [ ] `citations.py verify` clean; full suite green.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-244 gains a dated correction note
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — the gloss
  at `:101` and `:197`
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — the
  gloss at `:136`
- `tests/test_license_limit_is_written_only_from_a_measurement.py` — corpus extension and the
  exemption decision, only if (3) extends it

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03b`
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **n/a (no Senzing fact).** The subject is the plugin's own state field, its own
  invariant's reason clause, and its own guard's corpus. The `recordLimit: 0` observation quoted in
  the existing sites is a dated environment observation and is not re-claimed here (INV-080).
- Upstream: not applicable
- Related specs: `specs/counting-the-writers-of-license-record-limit-is-the-wrong-invariant.md`,
  `specs/sdk-setup-step5a-reads-absence-as-the-built-in-license.md`,
  `specs/sdk-setups-license-reconciliation-does-not-say-whether-to-persist.md`

## Deviations from this spec, and why (2026-09-03)

- **Proposed change 3 was taken in its "extend" form, and the exemption question is answered
  by the correction note itself.** `specs/INVARIANTS.md` is now in the count-matcher's corpus,
  entry by entry, and a count inside an invariant entry is permitted **only** where that entry
  also carries a `SUPERSEDED-COUNT:` marker. That cannot be satisfied by accident, because
  writing the marker means writing the correction — and it keeps `INVARIANTS.md` append-only,
  which the spec required: no guard here can be satisfied by deleting history.
- **Two edits the spec did not predict, both forced by editing the rule line.**
  `test_new_hard_rules_are_cited_or_deferred` reads `conformance.py since` at **line** level, so
  changing the gloss made `phaseA-build-loading.md:197` a newly-added hard rule — and its
  `(INV-244)` sat on the *next* line, which the guard correctly refuses. The citation is now
  inside the bolded rule (`⛔ **(INV-244) this means "never measured"…**`), which is what INV-183
  asks for anyway. ⚠️ **The identical shape at `module-04-data-collection/SKILL.md:112` was
  changed too, though no guard demanded it** — the sibling statement of one rule should not
  differ in form from the one just corrected (INV-246).
- **The gloss guard matches the paired shape, not the words.** *"never asked"* has legitimate
  uses in these same files — *"a Bootcamper may hold a license the bootcamp never asked
  about"*, three lines from a site that had to be caught — so the matcher requires
  `(?:never|not) asked` within 40 characters of `no custom license`. Calibrated against the
  pre-fix text: **3 hits, exactly the three defective sites, 0 elsewhere.**
