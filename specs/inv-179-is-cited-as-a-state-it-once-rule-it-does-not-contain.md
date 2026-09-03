# INV-179 is cited as a state-it-once rule it does not contain

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**INV-179 is cited at ten shipped sites for two subjects it says nothing about.** Its
registered text is entirely about SDK response flags: *"Before writing code that reads a field
from an SDK response, the guide MUST confirm the flag that populates **that field** is present
in the flag composite actually in force, reading its `composite_members`"*, and the three causes
of a blank field. It contains no clause about duplicated prose, no clause about pointing at a
single statement of record, and nothing about macOS, System Integrity Protection, `DYLD_*`, or
how a process is started.

A guide that follows the citation to learn why it must not restate a procedure — or why the
visualization server has to be a direct child of the shell — arrives at a rule about flag
composites. Two of the ten are ⛔ **hard rules** carrying the citation in the leading
`(INV-nnn)` governance form, which is the form that reads as authority.

This is the same class as `inv-124-is-cited-as-the-any-language-rule-it-is-not` (fixed
2026-09-02, four sites) recurring at two and a half times the size, and the class INV-134's
history records: a rule whose real authority is elsewhere accumulates citations to whatever
invariant was nearby.

## Root cause

INV-179 became a catch-all for two unrelated ideas. The sites split cleanly into two groups by
which rule they actually mean.

**Group A — the intended rule is INV-183's name-and-link clause** (*"The rule MUST be **named
and linked, never restated or forked** at the step (INV-080's no-fork discipline), so one
statement of record stays authoritative"*), which is exactly what each of these sentences
asserts:

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md:333` —
  the Java JSON-library procedure is *"stated once in `module-02-sdk-setup/SKILL.md`… follow it
  there rather than a copy here (INV-179)"*.
- `.../module-03-system-verification/phase1-verification.md:454` — the `register_data_source`
  reasoning is *"stated once at `phaseA-build-loading.md` step 4a item 2 (INV-179); do not
  restate it here."*
- `.../module-04-data-collection/SKILL.md:288` — the quality arithmetic is stated once in
  Module 5 (cited there as INV-174), *"so the two cannot drift (INV-179)"*.
- `.../module-06-data-processing/phaseA-build-loading.md:103` — *"follow the three branches
  … rather than restating them here (INV-179)"*.
- `.../module-07-query-visualize-discover/phase1-query-visualize.md:755` — the capture helper's
  procedure *"stays stated once in `module-completion.md` — this is the tool's identity, not a
  copy of its manual (INV-179)"*.
- `.../module-03b-truthset-visualization/visualization-api-reference.md:1121` — *"follow it
  there rather than re-deriving it (INV-179)"*.
- `.../graduation/SKILL.md:568` — *"a fourth copy is the **state-it-once violation**
  (INV-179)"*. This site names the principle outright and attributes it to INV-179, which is
  the clearest statement of the wrong premise.

**Group B — the intended rule is the platform rule, and the plugin already cites it correctly
one file away.** The macOS SIP/`DYLD_*` direct-child rule is stated three times. The canonical
statement in the contract cites **INV-001, INV-002**; the two module copies cite INV-179:

- `.../module-03b-truthset-visualization/visualization-api-reference.md:1103` — ⛔ **(INV-001,
  INV-002)** — the canonical statement, with the Darwin 25.5.0 demonstration. **Correct.**
- `.../module-07-query-visualize-discover/phase1-query-visualize.md:805` — ⛔ **(INV-179)** On
  macOS, start it as a DIRECT CHILD… **Wrong.**
- `.../module-07-query-visualize-discover/phase1-query-visualize.md:810` — the pointer at the
  canonical statement, *"→ 'Server lifetime' (INV-179)"*. **Wrong**, and it sends the reader to
  a section that cites INV-001/INV-002, so the ID does not even match the destination.
- `.../module-03b-truthset-visualization/phase1-visualization.md:393` — ⛔ **(INV-179)** The
  launch below backgrounds with a plain `&`… **Wrong.**

**Corroboration from the repo itself, which is what makes this a mis-citation rather than a
judgment call:** `module-05-data-quality-mapping/phase2-data-mapping.md:245` states the same
no-fork idea in the same vocabulary — *"the two cannot drift apart (INV-183)"* — so the plugin
already knows which invariant governs group A, and group B's own canonical site already cites
the right pair.

**Left alone deliberately, and named so a later pass does not "fix" them:** four sites cite
INV-179 where the surrounding subject genuinely *is* flags and blank fields —
`phase1-query-visualize.md:318` and `:427` (the `CONFIRMATIONS[]` present-but-empty
discriminator and `WHY_KEY_DETAILS`, both instances of INV-179's cause 2 versus cause 3),
`phase2-discover.md:188` and `:331`. So are all three script-side citations,
`senzing_viz_server.py:403`, `:407` and `:1972` (the absorb/`export_flags` coupling). These are
correct.

**Why no existing check sees it.** `conformance.py rules` and `per-rule` ask whether a rule
carries *an* invariant id; all ten do. `citations.py verify` proves the id resolves; INV-179
exists. `test_any_language_citations_name_the_right_rule.py` — written for the INV-124 instance
— pins one claim shape ("binds any language") and not this one. Nothing compares a citation's
subject with the invariant's subject, and nothing can in general.

## Proposed change

1. **Group A → INV-183** (add INV-080 where the sentence is about not forking a rule's wording
   rather than about where it is stated). Seven sites, listed above.
2. **Group B → INV-001, INV-002**, matching what `visualization-api-reference.md:1103` already
   cites for the canonical statement. Three sites, listed above.
3. **Leave the eleven correct INV-179 citations untouched**, and do not add a citation to the
   four flag-subject sites named above as defensible.
4. **Add a guard for the shape, narrow enough to be worth keeping.** A near-duplicate detector
   over shipped markdown that reports pairs of rule lines whose text is similar and whose cited
   invariant sets are **disjoint** — one rule under two authorities means at least one is wrong,
   and both pass every existing check because both carry an id. Measured while triaging this
   finding: at a similarity floor of 0.68 over the 201 cited rule lines it reports **exactly one
   pair, the group-B macOS pair, with no false positives**. ⚠️ It found one of the three group-B
   sites, not all three — `phase1-visualization.md:393` states the rule in different enough words
   to fall under the floor — so the guard's claim must be that it catches a *restated* rule whose
   authority disagrees, never that it enumerates every mis-citation. Group A is out of its reach
   entirely and must be fixed by the citation edits, not by the scan.
5. ⛔ **Do not attempt a general "does this citation's subject match the invariant" scanner.** The
   2026-09-03 audit's retracted finding is the precedent: a line-level citation scanner produced a
   false positive and a corpus figure whose examined hits were both correct. The honest unit is the
   passage, which is more than a regex should attempt.

## Acceptance criteria

- [ ] No shipped file cites INV-179 for a claim about restating, copying, forking, or drifting
      prose; the seven group-A sites cite INV-183 (with INV-080 where the subject is the wording).
- [ ] No shipped file cites INV-179 for the macOS SIP / `DYLD_*` / direct-child rule; the three
      group-B sites cite INV-001, INV-002 — the pair the canonical statement already carries.
- [ ] `phase1-query-visualize.md:810`'s pointer names the same invariant as the section it points
      at.
- [ ] The eleven flag-subject INV-179 citations are unchanged, asserted so the sweep cannot
      over-reach.
- [ ] A new test in `tests/` reports near-duplicate rule lines whose cited invariant sets are
      disjoint, is green after the fix, and is negative-controlled by restoring one group-B
      mis-citation.
- [ ] The guard's docstring states what it does **not** establish — that it cannot see a rule
      restated in different words, nor a citation wrong for any reason other than disagreeing with
      a near copy.
- [ ] `citations.py verify` clean; `coverage_reports.py shipped` clean; full suite green.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — two
  group-A citations (`:333`, `:454`)
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — one group-A citation
  (`:288`)
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — one
  group-A citation (`:103`)
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md`
  — one group-A citation (`:755`) and two group-B (`:805`, `:810`)
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — one group-A citation (`:1121`)
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  one group-B citation (`:393`)
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — one group-A citation (`:568`)
- `tests/test_a_restated_rule_keeps_its_authority.py` (new) — the disjoint-citation guard

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03b`
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **n/a (no Senzing fact).** The subject is which of the plugin's own invariants
  governs three of its own rules. No Senzing claim is asserted or re-asserted (INV-080); the
  macOS SIP behavior at `visualization-api-reference.md:1103` is an existing dated environment
  observation and is not re-claimed here.
- Upstream: not applicable
- Related specs: `specs/inv-124-is-cited-as-the-any-language-rule-it-is-not.md`,
  `specs/the-cord-disclosure-rule-cites-inv-012-where-inv-247-governs.md`,
  `specs/a-check-whose-scope-is-wider-than-its-claim-passes-without-establishing-it.md`

## Deviations from this spec, and why (2026-09-03)

- **Group A cites INV-183 alone. INV-080 was NOT added anywhere**, though criterion 1
  permitted it "where the subject is the wording". INV-080's registered subject is that every
  skill able to produce Bootcamper-facing Senzing content must carry an MCP-grounding /
  no-speculation clause — it is about where **Senzing facts** come from, not about duplicated
  procedure prose. The phrase "INV-080's no-fork discipline" is **INV-183's own gloss** of it,
  and citing INV-080 beside a Java-JSON-library procedure or a quality-score formula would have
  created a fresh instance of exactly the defect this spec fixes. INV-183 carries the no-fork
  clause internally, so a reader following it arrives at the rule either way.
- **An existing guard had encoded the mis-citation, and correcting the prose turned it red.**
  `tests/test_server_launch_warns_about_protected_launchers.py`'s
  `test_it_says_the_jvm_flag_does_not_fix_it` asserted `inv-179` appears near the
  `no Sz in java.library.path` symptom, with the message *"the reasoning is restated rather than
  cited to module-02, which owns it"* — so the id was a **proxy for "carries a citation"**, and
  pinning it meant the suite actively held the wrong id in place. Rescoped to what the message
  actually claims: the window must name `module-02-sdk-setup` (the owner) and carry some
  `inv-\d+` citation. Negative-controlled by replacing the pointer with a restatement.
  ⚠️ This was not predicted by the spec, and it is the same shape as
  `test_license_limit_has_exactly_two_writers.py` pinning a wrong count into the suite.
- **The guard's exemption mechanism** is a tuple of phrase-fragment pairs (`EXEMPT_PAIRS`),
  empty today, rather than file:line pairs — line numbers move with every edit above them.
- **Criterion 4 is satisfied by a property, not a count.** "The eleven flag-subject citations
  are unchanged, asserted" is enforced as *every surviving INV-179 citation sits in a passage
  about flags*, checked over a ±8-line window, plus an assertion that at least one such
  citation still exists. ⚠️ **Its recall was measured rather than assumed: 6 of the 10 removed
  mis-citations, no false positives.** The four it misses mention "flag" or "field"
  incidentally nearby. A count of citations was deliberately not used — that is the shape
  `counting-the-writers-of-license-record-limit-is-the-wrong-invariant` exists to forbid.
