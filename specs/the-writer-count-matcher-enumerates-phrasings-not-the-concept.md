# Two more writer-count sites survived the guard written to remove them, because the matcher enumerates phrasings rather than the concept

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`counting-the-writers-of-license-record-limit-is-the-wrong-invariant` (`829bbb5`) replaced the
writer count with the measured-only property at three sites and added
`tests/test_license_limit_is_written_only_from_a_measurement.py` to keep any count out. **Two more
sites survived it**, found by grep in the next audit pass:

- `module-06-data-processing/phaseA-build-loading.md:104` — *"⛔ **Do not measure it again here**:
  **Module 4 Step 8a is its only writer**, and a second SDK call is the way two answers start to
  differ."* ⚠️ Written by this same loop, in `step1-license-framing-ignores-the-measured-record-limit`
  (`2a94863`), hours before the count was recognized as the wrong shape.
- `module-04-data-collection/SKILL.md:99` — *"(INV-244) **The field's only writer is Step 8a
  below**, which is volume-gated by design."* Pre-existing, and false in the same file: `:110` is a
  second write.

**The guard could not see either.** Its `WRITER_COUNT` patterns require the field name adjacent to
the claim — `the only writer of\s*license_record_limit`, `license_record_limit is written only by` —
and neither site names the field in that sentence. One says *"its only writer"*, the other *"the
field's only writer"*, both relying on a subject established a line earlier.

⛔ **This is the fourth instance of one failure shape in a single day, and the third at one remove.**
The count was wrong; the correction minted a new count; the guard against counts enumerated the
phrasings that had been seen rather than the thing being claimed. Each fix was correct about its
instance and reproduced the instance-shaped thinking one level up.

⚠️ **The conclusion at both sites still holds and the guidance is still safe to follow** — Step 8a
is volume-gated, so absence really is uninformative, and `phaseA:104`'s point ("do not measure it
again here") is right regardless of how many writers exist. Only the stated reason is false. That is
why this is Medium and not High: nothing a Bootcamper does changes.

## Root cause

A matcher written from examples matches examples. Both surviving sentences use an **anaphor** — *its
only writer*, *the field's only writer* — where the subject is the previous sentence's, so no
pattern keyed to the field name can reach them. The concept being asserted is "this field has
exactly N writers", and the field is often named nowhere near the claim.

The deeper cause is the one this repo keeps re-learning: a guard built by generalizing from the
sites you already fixed is blind in exactly the direction you were blind when you fixed them.
`INV-246` states this for *paths*; the same reasoning applies to *phrasings*, and nothing states it
for those.

## Proposed change

1. **Fix both sites** with the measured-only property, keeping each one's actual point —
   `phaseA:104`'s is that re-measuring here risks two divergent answers, which does not need a
   writer count at all; `module-04:99`'s is that Step 8a is volume-gated.
2. **Rewrite the matcher against the concept, not the phrasings.** A writer-count claim is any
   `only writer` / `sole writer` / `N writers` / `written only by` construction appearing in a file
   that discusses `license_record_limit` — with no requirement that the field name be adjacent,
   since an anaphor is the normal way to write the second sentence about a subject.
3. **Pin every phrasing that has actually shipped** in the anti-vacuity test, including the two
   anaphoric ones, so the matcher's blind spot is recorded as a fixture rather than as a memory.
4. **Consider registering the generalization**, since it now has four instances in one day:
   *a guard derived from the sites it just fixed inherits their blind spot; derive it from the claim
   instead.* ⚠️ Wording needs the maintainer's sign-off — a draft is in the acceptance criteria. This
   is the half worth more than either site fix.
5. ⛔ **Do not widen the matcher to every "only" in the corpus.** The scope is files that discuss
   this field; a corpus-wide ban on the word would fire on unrelated correct prose and get relaxed
   within a week, which is worse than the gap.

## Acceptance criteria

- [ ] Neither `phaseA-build-loading.md:104` nor `module-04-data-collection/SKILL.md:99` states a
      writer count; both keep their original point.
- [ ] The matcher catches an anaphoric claim — *"its only writer"*, *"the field's only writer"* —
      with the field named only in a previous sentence.
- [ ] The anti-vacuity test pins all **six** phrasings that have shipped: `the only writer of X`,
      `X is written only by`, `written only by Module 4`, `exactly two writers`, `its only writer`,
      `the field's only writer`.
- [ ] The matcher still passes the property wording and the replace-only distinction.
- [ ] An invariant is drafted for sign-off. Draft: *"**INV-NNN** — A guard enforcing a rule across
      shipped prose MUST derive its matcher from the CLAIM being made, not from the phrasings
      already observed at the sites it was written to fix. Where a claim can be made about a subject
      established in an earlier sentence, the matcher MUST NOT require the subject to appear
      adjacent to it. (Extends **INV-246** from a guard's set of FILES to its set of PHRASINGS: both
      fail by inheriting the blind spot of whoever last fixed the instances.)"* ⛔ Written as
      `INV-NNN`, not a literal id.
- [ ] Negative-controlled: each of the six phrasings, planted at a real site, fails the guard.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — `:104`
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — `:99`
- `tests/test_license_limit_is_written_only_from_a_measurement.py` — the matcher
- `specs/INVARIANTS.md` — the new invariant, after sign-off

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-28, cycle 4 of the second
  unattended loop (`Source: self-observed (assistant retrospective)`). Found by grepping the corpus
  for the *concept* after the guard reported clean — the check the guard itself should have been.
- Priority: **Medium.** Both conclusions still hold and no Bootcamper-visible behavior changes; only
  the stated reasons are false. Filed at Medium rather than Low because one of the two was written
  by this same loop hours earlier, so the class is actively reproducing, and because the
  generalization in item 4 is worth more than either site.
- MCP re-check: **n/a (no Senzing fact).** The subject is this plugin's prose about its own state
  field, and a test's matcher. `get_capabilities` dated the run: server **1.33.0**, 2026-08-28.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/counting-the-writers-of-license-record-limit-is-the-wrong-invariant.md`
  (`829bbb5`, whose guard this completes);
  `specs/step1-license-framing-ignores-the-measured-record-limit.md` (`2a94863`, which introduced
  `phaseA:104`); `specs/mcp-negative-markers-must-name-the-owning-route.md` (INV-246's lineage — the
  same blind-spot argument, applied to paths rather than phrasings)

## Deviations from this spec, and why (2026-08-28)

**None on content.** Both sites are corrected keeping their own point: `phaseA:104` now says the
value *"was already measured and persisted by the step that owns this question"* — which is its
actual argument against re-measuring and needs no writer count — and `module-04:99` states the
measured-only property before naming Step 8a's volume gating. A corpus grep for the concept returns
**nothing** outside the one legitimate compound adjective.

**MCP re-check: n/a, re-confirmed rather than assumed.** `get_capabilities` dated the run: server
**1.33.0**, 2026-08-28.

⛔ **Rewriting the matcher against the concept immediately produced a false positive, which is the
other half of the lesson.** The first concept-level pattern matched `\bonly\s+writer\b`, which fires
on **"a stdlib-only writer"** — a real string in `generate_discoveries_pdf.py` that states no writer
count. A guard that flags correct prose gets relaxed, so the pattern now carries a negative
lookbehind excluding the compound adjective, and that string is pinned in the must-pass set. ⚠️
**Widening a matcher and tightening it are the same edit**: the concept-level version has to exclude
what the phrasing-level version excluded by accident.

**All six shipped phrasings are fixtures, not memory.** Each was planted at a real site and each
fails the guard: `the only writer of X`, `X is written only by`, `written only by Module 4's
volume-gated Step 8a`, `exactly two writers`, `its only writer`, `the field's only writer`. The last
two are the anaphoric pair that survived the previous version, recorded as fixtures precisely
because that is how the blind spot recurred.

⚠️ **`conformance.py since` reports zero rules added, and the new cited-or-deferred guard SKIPS**
with *"no hard rules added since the newest audit entry"*. Both are correct: this change **removed**
false claims rather than adding rules. The skip is the guard saying so rather than passing silently
(INV-265), and it is the first time that branch has been exercised.

**One invariant is DEFERRED** — criterion 5, and the half worth more than either site fix. See the
ledger entry.
