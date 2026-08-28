# The `Upstream:` outcome vocabulary is a closed set bound by no invariant, and its newest value reached two of its three sites

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The feedback system has **two** closed vocabularies. One is registered as an invariant and one is
not, and the unregistered one has just drifted.

**Registered.** The routing taxonomy is `plugin | mcp-server | both | host | unclear`, and
**INV-248** binds it explicitly: *"the closed set … and **every** shipped site stating that set MUST
state all five."* **INV-249** governs which of its verdicts may be forwarded.

**Unregistered.** The `Upstream:` outcome vocabulary — what happened to a finding routed upstream —
is equally closed, is stated at **three** sites, and **no invariant binds it**:

| # | Site | Vocabulary as stated |
|---|---|---|
| 1 | `plugins/…/bootcamp-onboarding/feedback.md:134` (entry template) | `not applicable \| offered, declined \| submitted YYYY-MM-DD \| submission failed: reason \| submission blocked: reason` |
| 2 | `plugins/…/bootcamp-onboarding/feedback.md:232` (Step 3 outcome list) | same five |
| 3 | `.claude/skills/feedback-to-specs/spec-template.md:50` (spec-side) | `not applicable \| already sent <date> (per the entry) \| sent <date> via submit_feedback \| declined by the maintainer` |

`submission blocked: <reason>` was added on 2026-08-28 by
`graduation-upstream-offer-collides-with-the-dry-run-no-send-rule`, for a send the answerer
**consented to** that the runner was forbidden to make. It reached sites 1 and 2. **It did not reach
site 3**, and site 3's nearest value — `declined by the maintainer` — reproduces the exact
misrepresentation the fix was written to remove, one level up: a maintainer who **approved** a send
that a dry run could not make is recorded as having declined it.

⛔ **This is not hypothetical; the run that shipped the fix demonstrated it.** Two specs from the
2026-08-27 dry run had to record their blocked sends as free text —
*"Upstream: **not yet sent — needs maintainer approval**"* — because the spec-side vocabulary had no
value for the state. Free text in a field other tooling reads is the symptom the entry-side fix was
meant to end.

**Second consequence: the rule shipped with no invariant to cite.** `feedback.md:235` is a ⛔
hard rule (*"`submission blocked:` is for a *consented* send … not a synonym for the other three"*),
and `conformance.py per-rule --uncited` reports it as carrying **no invariant citation at the line** —
because there is no invariant to cite. INV-183 requires a rule binding a step to be reachable at that
step. Its sibling vocabulary has INV-248 for precisely this purpose.

## Root cause

The two vocabularies were registered asymmetrically. The routing taxonomy got INV-248 when a run
found its five values stated inconsistently across sites; the `Upstream:` vocabulary never had that
run, so nothing binds its sites to agree and nothing forced a new value to reach all of them.

The 2026-08-28 fix inherited that gap rather than creating it — but it is also the first change to
**add** a value, which is the operation an unbound closed set cannot survive. Its guard
(`tests/test_blocked_submission_has_a_vocabulary_value.py`) scans `plugins/` only, so it is
structurally incapable of seeing site 3: `.claude/` does not ship, and the guard's corpus is the
shipped tree.

⚠️ **The guard is not wrong to scan `plugins/`** — that is the right default for a rule about shipped
prose. What is missing is that this particular vocabulary has a maintainer-side member, so its site
set is larger than the shipped tree.

## Proposed change

1. **Add the blocked value to the spec-side vocabulary** at `spec-template.md:50` — a value meaning
   *the send was consented to and could not be made*, distinct from `declined by the maintainer`.
   Match the entry-side naming so the two read as one vocabulary.
2. **Say, at `feedback-to-specs/SKILL.md` Step 1**, that a blocked entry still owes an upstream
   report — it is the one outcome where the finding is unsent **and** nobody declined it, so it must
   not be filtered out the way a decline reasonably is.
3. **Register the invariant this vocabulary has always needed**, mirroring INV-248's shape: the
   `Upstream:` outcome vocabulary is a closed set and every site stating it MUST state the same
   values. ⚠️ **Wording needs the maintainer's sign-off** — a draft is in the acceptance criteria.
4. **Widen the existing guard's corpus for this one rule** so it covers the maintainer-side
   enumeration as well as the shipped ones, deriving sites by scanning both trees (INV-246).
5. ⛔ **Do not "fix" this by deleting `declined by the maintainer`.** It is a real and distinct
   outcome. The defect is a missing value, not a wrong one.

## Acceptance criteria

- [ ] `.claude/skills/feedback-to-specs/spec-template.md:50` carries a blocked-send value, named
      consistently with `feedback.md`'s `submission blocked: <reason>`.
- [ ] `feedback-to-specs/SKILL.md` Step 1 states that a blocked entry still owes a report, so it is
      not triaged as though it were declined.
- [ ] The two specs that recorded free text (`find-examples-self-describes-two-different-coverages`,
      `java-initialize-scaffold-snippet-references-the-wrong-class`) are **not** rewritten — both
      have since been sent, and their `Upstream:` lines now record that. This criterion exists to
      say so explicitly, so a later run does not "tidy" them.
- [ ] An invariant binds the vocabulary. Draft for sign-off: *"**INV-NNN** — The `Upstream:` outcome
      vocabulary is a closed set, and **every** site stating it — shipped or maintainer-side — MUST
      state the same values. A consented send that could not be made MUST have its own value,
      distinct from a declined one, because the two differ in whether a report is still owed."*
      ⛔ Written as `INV-NNN`, not a literal id: spelling an unminted id creates a citation of an
      undefined invariant and turns `citations.py verify` red.
- [ ] `tests/test_blocked_submission_has_a_vocabulary_value.py` derives its site set from **both**
      `plugins/` and the maintainer-side skills that state the vocabulary, and fails when a value is
      present in one tree and absent in the other. Stdlib only, no `plugins/` import (INV-108).
- [ ] Negative-controlled: removing the value from either tree fails the guard.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      change is prose and a guard, not a binding.

## Affected files

- `.claude/skills/feedback-to-specs/spec-template.md` — the spec-side vocabulary at `:50`
- `.claude/skills/feedback-to-specs/SKILL.md` — Step 1's triage of the field
- `specs/INVARIANTS.md` — the new invariant, after sign-off
- `tests/test_blocked_submission_has_a_vocabulary_value.py` — widen the corpus

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-28, cycle 1 of the unattended
  implement→audit loop (`Source: self-observed (assistant retrospective)`). Found by the reverse
  sweep: `conformance.py since --since-last-audit` attributed 26 hard-rule lines to the round, and
  reading them showed 5 with no invariant cited at the line, of which four are covered by deferred
  invariants already recorded and **one was not** — which led to asking what binds that vocabulary,
  and finding that nothing does while its sibling has INV-248.
- Priority: **Medium.** Nothing a bootcamper sees is broken — site 3 is maintainer-side. It is filed
  Medium rather than Low because the missing value's nearest substitute (`declined by the
  maintainer`) actively misrecords consent, and `feedback-to-specs` reads that field to decide
  whether a report is still owed; a blocked send filed as a decline is a finding nobody forwards.
- MCP re-check: **n/a (no Senzing fact).** The subject is two of this repo's own vocabularies and
  their agreement with each other. No Senzing behavior, SDK surface or server claim is asserted, so
  there is nothing to re-verify and no absence claim to substantiate. `get_capabilities` was called
  this session to date the run: server **1.33.0**, 2026-08-28.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/graduation-upstream-offer-collides-with-the-dry-run-no-send-rule.md` (added
  the value to the two shipped sites; this spec completes the set and registers the rule);
  `specs/feedback-routing-has-no-verdict-for-a-defect-neither-component-owns.md` (the sibling gap in
  the routing taxonomy, which INV-248 now binds)

## Deviations from this spec, and why (2026-08-28)

**None on content.** All three sites were re-read before changing anything and the diagnosis held:
`feedback.md:134` and `:232` carried `submission blocked:`, `spec-template.md:50` did not, and its
nearest value was `declined by the maintainer`.

**MCP re-check: n/a, and re-confirmed as n/a rather than assumed.** The subject is two of this
repo's own vocabularies agreeing with each other; no Senzing behavior, SDK surface or server claim
is involved. `get_capabilities` was called this session to date the run: server **1.33.0**,
2026-08-28.

**The guard's corpus was widened rather than a second guard written.** The existing
`test_blocked_submission_has_a_vocabulary_value.py` already owned this rule; giving it a
`vocabulary_corpus()` that spans `plugins/` **and** `.claude/skills/` keeps one guard per rule and
makes the cross-tree assertion possible. It recognizes the spec-side spelling of the same closed set
(`already sent` / `declined by the maintainer`) as well as the entry-side one, since the two halves
name the same states in different words. The new `test_both_trees_state_the_value` counts the value
per tree and fails when it is present in one and absent in the other — which is precisely the state
this spec was filed for, and it is negative-controlled in **both** directions.

⚠️ **`conformance.py since` reports zero hard-rule lines added, and that is correct rather than a
miss.** Every change here is under `.claude/`, which does not ship; that scan reads shipped markdown
only. The ⛔ added to `feedback-to-specs/SKILL.md` is a maintainer-side instruction and sits outside
the shipped-rule reverse contract — noted so a later reader does not read the zero as evidence the
change added no rule at all.

**One invariant is DEFERRED** — see the ledger entry. The spec asks for one and only the maintainer
may sign off on wording.
