# Newly minted invariants carry no shipped citation

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

**All eight invariants registered on 2026-08-14 — INV-222 through INV-229 — are cited
by no file under `plugins/`.** Verified by grep: zero hits for `INV-22[2-9]` across the
entire shipped tree.

Each rule *is* stated in shipped prose. What is missing is the ID, so the rule exists
in the product and in `INVARIANTS.md` with no link between them:

| Invariant | The shipped text that states the rule, carrying no ID |
|---|---|
| INV-222 | `module-02-sdk-setup/SKILL.md:468`, `:483` (pip prohibition + why it succeeds) |
| INV-223 | `visualization-api-reference.md:990-1015`; `module-07/phase1-query-visualize.md:500`; `module-03b/phase2-close.md:96` |
| INV-224 | `bootcamp-preparation/SKILL.md:283` (options follow the question) |
| INV-225 | `ground-rules.md:53`, `:58`, `:118`, `:450`; `module-03/SKILL.md:22`; `phase1-verification.md:9` |
| INV-226 | `graduation/SKILL.md:220`, `:233` (module-completion Step 2a) |
| INV-227 | `bootcamp-onboarding/SKILL.md:30`, `:34`, `:38`; `scripts/session-start.py:24` |
| INV-228 | `module-03b/phase1-visualization.md:137`; `module-04/SKILL.md:267` |
| INV-229 | `phase1-verification.md:522`; `module-03/SKILL.md` (success indicator) |

This is the class INV-183 governs — a rule binding a step must be reachable **at** that
step — and the cost is not cosmetic. A rule with no ID is one a later editor cannot look
up, cannot tell from local phrasing, and will "tidy" away: that is the documented cause
of the corrected-back-to-broken example in `deep-dive-audit-2026-07-28b`. It also
breaks the audit's reverse direction, because a rule stated in prose and registered
under an ID that appears nowhere near it reads, from the shipped side, exactly like an
unregistered rule.

The same run found one more instance of the missing-citation class, from the other
detector: `visualization-api-reference.md:977` — ⛔ "A visualization server, once
started, stays up until the bootcamper has explicitly approved teardown" — cites no
invariant, while both its sibling subsections do (`:1000` INV-172, `:1025` INV-056).
It is registered: **INV-131** makes irreversible teardown the module's last action,
"after every step that needs the data or the running service (snapshot rebuild,
live-server screenshot capture, endpoint verification)", which is precisely the claim
`:977` makes. `conformance.py rules` reports it as the only hard rule in the plugin
whose section cites nothing.

## Root cause

**`implement-spec` never runs the report that would catch it.** `SKILL.md:283-289`
names three coverage reports to run when a spec touches the ledger:

```bash
python3 .claude/skills/dry-run/coverage_reports.py invariants   # invariants no test cites
python3 .claude/skills/dry-run/coverage_reports.py affected     # predicted-but-unrecorded files
python3 .claude/skills/dry-run/coverage_reports.py negatives    # dated "tool lacks X" claims
```

`shipped` — *invariants that bind a shipped artifact and that no shipped file cites* —
is absent from that list, even though it exists in the same script, is wired into
`both`, and was added for exactly this purpose two days earlier (`921c9c2`). So the
skill that mints an invariant checks whether a **test** cites it and never whether the
**plugin** does.

The 2026-08-14 batch then hit the case the omission is worst for. The maintainer's
decision that run was to **queue** new invariants for approval rather than write them,
so every implementation shipped while its ID did not yet exist — the citation was
un-writable at the moment the prose was written. The eight IDs were minted in one later
commit (`4d26f28`), and nothing in the workflow sends the implementer back to the prose
once an ID exists.

The evidence that this is a recurring class, not a one-off: `aa013dc` (2026-08-13)
—"cite the 13 invariants no shipped file named" — fixed thirteen instances by hand one
day before these eight accrued.

**No Senzing fact is at issue.** This is the plugin's own citation discipline; nothing
here asserts engine or server behavior (INV-080 untouched).

## Proposed change

1. **Add the citation at each site in the table above**, in the file's existing idiom
   (`(INV-nnn)` inline, or `Full rule: … (INV-nnn)` where the site already points at a
   canonical section). Where one invariant binds several files, cite it at each — that
   is the point of INV-183, and the INV-229 sites are the proof: the two files that
   *were* edited state the rule, and the third graded it binary for a day.
2. **Cite INV-131 at `visualization-api-reference.md:977`**, so the server-lifetime
   rule is looked-up-able like its two siblings. Note in the same edit that the
   explicit-approval half is the teardown gate below (INV-056), so a reader is not left
   thinking INV-131 covers the whole section.
3. **Add `shipped` to `implement-spec`'s report list** at `SKILL.md:283-289`, with one
   line saying what it answers, so the shipped side is checked at the moment an
   invariant is registered rather than at the next audit.
4. **Make the back-citation an explicit step for a queued invariant.** Where a run
   queues invariants for approval, the prose ships before the ID exists, so registering
   the ID must be followed by adding the citation to every site the invariant's own
   `Enforced by` / provenance names. State it where the skill describes minting an
   invariant, and name the reason: a citation that cannot be written when the prose is
   written will not be written at all unless something asks for it.

## Acceptance criteria

- [ ] Every one of INV-222 – INV-229 is cited by at least one file under `plugins/`, at
      a site that states the rule it governs.
- [ ] `visualization-api-reference.md:977` cites INV-131, and
      `conformance.py rules` reports zero hard-rule lines in a section citing no
      invariant.
- [ ] `coverage_reports.py shipped` reports no invariant naming a shipped artifact that
      shipped text does not cite (subject to
      `shipped-citation-report-cannot-see-a-module-display-name`, which must land first
      or the check is vacuous for 7 of these 8).
- [ ] `implement-spec/SKILL.md` lists `shipped` alongside `invariants`, `affected` and
      `negatives`, and states that a newly minted invariant must be cited in the shipped
      text that states its rule before the spec is recorded as implemented.
- [ ] `citations.py verify` stays clean after the edits (every added ID resolves).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Source

`production-readiness-audit`, 2026-08-14. Found by the reverse sweep (Step 3) plus a
direct grep for the eight IDs registered that day; `conformance.py rules` supplied the
INV-131 instance.

- Related: `shipped-citation-report-cannot-see-a-module-display-name` (why the report
  surfaced 1 of these 8 rather than all 8) and
  `verification-report-cannot-express-an-expectation-mismatch` (the same batch's
  incomplete application, found the same way).
- Establishes no new invariant. INV-183 already requires a rule to be reachable at the
  step it binds; this is that rule applied to eight new IDs and one section.

## Deviations from this spec, and why (2026-08-14)

- **Two invariants beyond the eight were cited: INV-140 and INV-214.** They were not in this spec's
  table because the report could not see them either — widening the filter
  (`shipped-citation-report-cannot-see-a-module-display-name`, implemented first) surfaced them as
  pre-existing gaps of exactly this class. Criterion 3 is written absolutely ("reports **no**
  invariant naming a shipped artifact that shipped text does not cite"), so satisfying it as written
  required citing them; `aa013dc` citing thirteen at once is the precedent. INV-140 is cited at
  `docs/model-selection.md`'s per-stage table, INV-214 at `ground-rules.md`'s prescribed-shape rule.
- **INV-229's citations landed in the sibling spec's edits**, since the rule and its ID were being
  written into the same sentences there. Recorded in that spec too, so neither reader is left
  wondering which change added them.
- **One citation was written in the forbidden bold form and corrected**: `**…anti-pattern**
  (INV-222)**.**` moved to `**…anti-pattern.** (INV-222 — …)`, keeping the terminal punctuation
  inside the bold span.
