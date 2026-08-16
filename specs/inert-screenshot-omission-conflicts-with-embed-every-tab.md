# INV-123 offers "omit the image" for an inert capture; INV-146 forbids omitting any capture

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two live invariants give contradictory instructions for the same artifact — the Search /
Probe screenshot taken from the static snapshot rather than a live engine.

**INV-123** (`specs/INVARIANTS.md:374`) permits either remedy:

> Where a captured tab is inert because it was taken from the static snapshot rather than
> the live engine (Search / Probe), the caption MUST say so **or the image MUST be
> omitted**; it MUST NOT imply a result set that was not captured.

**INV-146** (`:350`) forbids the second one:

> Every screenshot a visualization capture produced MUST reach the recap. … Only a true
> duplicate — two images of the **same** tab, which per-tab capture should not produce —
> may be deleted.

An implementer who takes INV-123's second branch violates INV-146. An implementer who
follows INV-146 finds INV-123's disjunction offers an option that is never available.
Neither invariant mentions the other — verified: `INV-146` does not appear in INV-123's
text and `INV-123` does not appear in INV-146's.

**Why this is more than pedantry.** INV-146 exists precisely because a "best of" judgment
deleted the three *analytical* tabs from a six-tab app — its own text records that. The
Search / Probe tab is the one INV-123 singles out as inert, so it is exactly the tab an
implementer is most likely to reach for the omission branch on, and INV-146's stated failure
mode is a recap silently missing views the surrounding prose describes. The two rules
disagree on the single case where the disagreement does damage.

Both were recorded on **2026-07-26** from different specs
(`per-tab-screenshot-capture-and-grounded-captions` and `embed-every-captured-tab-in-tab-order`),
which is how they landed inconsistent without either noticing.

## Root cause

`per-tab-screenshot-capture-and-grounded-captions` wrote INV-123 as a *caption-truthfulness*
rule, and offered omission as the escape hatch for a caption that cannot be made truthful —
correct in isolation. `embed-every-captured-tab-in-tab-order` then established INV-146 as a
*completeness* rule that closes exactly that hatch, and did not sweep the existing
invariants for permissions it had just revoked.

The result is that INV-123's omission branch is **already unreachable** in conforming
behavior: given INV-146, the only conforming remedy for an inert capture is the caption. The
disjunction is dead text that reads as a live option.

**Unverified — needs investigation at implementation:** which branch the shipped guidance
actually takes. The implementer must check `module-completion.md`'s capture-time embed and
graduation's orphaned-screenshot backfill for any instruction to omit an inert Search / Probe
image, and whether `tests/test_screenshot_retention_and_order.py` or the caption tests pin
either branch. If shipped guidance omits, this is a live defect and not only a wording
conflict.

## Proposed change

1. **Remove the omission branch from INV-123 and state why it is unavailable.** The clause
   becomes: the caption MUST say the view is inert — and MUST NOT imply a result set that was
   not captured — with a note that omitting the image is **not** an available remedy because
   INV-146 requires every captured screenshot to reach the recap.
2. **Cross-reference both ways.** INV-123 cites INV-146 for the completeness requirement;
   INV-146 gains a parenthetical noting that it closed INV-123's omission branch, so the next
   reader of either finds the resolution without re-deriving it.
3. **Check and correct the shipped guidance** at both sites INV-146 binds — the capture-time
   embed and graduation's backfill — so neither instructs or permits dropping the inert
   image.

This narrows INV-123 by deleting a permission, which is arguably an in-place clarification
(the permission was already void under INV-146) rather than a change of meaning: no
conforming implementation loses an option it could legitimately have used.

⚠️ **If the maintainer instead judges the omission branch correct** — that an inert capture
is better absent than present with a caveat — then INV-146 is the invariant to amend, not
INV-123, and it needs a new invariant carving out the inert case rather than an in-place
edit, because that *would* change INV-146's meaning. This spec recommends the first
direction, because INV-146's "only a true duplicate may be deleted" is categorical and
INV-123's own primary branch (caption says so) already resolves the truthfulness problem
without deleting content.

## Acceptance criteria

- [ ] INV-123 no longer offers omission as a remedy for an inert capture, and states that
      the caption is the required remedy.
- [ ] INV-123 cites INV-146 as the reason omission is unavailable, and INV-146 records that
      it closed that branch. The cross-reference resolves in both directions.
- [ ] No invariant is deleted or renumbered; the edit is recorded as a dated in-place
      clarification, or as a new invariant if the maintainer rules it a meaning change.
- [ ] The capture-time embed (`module-completion.md`) and graduation's orphaned-screenshot
      backfill are both confirmed by **opening them** to instruct captioning rather than
      omitting — this criterion names two consumers and must be checked against each file,
      not against the invariant edit (INV-182).
- [ ] A test asserts that no shipped guidance permits dropping a captured screenshot for any
      reason other than a true same-tab duplicate.
- [ ] Any test that pinned the omission branch is repointed to the caption requirement, with
      a docstring stating what changed and when (INV-181).
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-123 (`:374`) and INV-146 (`:350`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` — the
  capture-time embed, if it permits omission.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the orphaned-screenshot backfill,
  same check.
- `tests/` — the no-omission assertion; and any existing caption/retention test that pinned
  the removed branch.

## Source

- **Found by:** maintainer question — *"Are there any invariants in @specs/INVARIANTS.md
  that conflict with each other?"* — 2026-07-31, by reading all 194 against each other.
- Priority: **Medium-High.** The two rules disagree on the one case where the disagreement
  loses a Bootcamper's screenshot, and INV-146 exists because that already happened once.
  Raised to High if the investigation finds shipped guidance taking the omission branch.
- MCP re-check: **n/a (no Senzing fact).** Both invariants govern the plugin's own capture
  and recap apparatus; no Senzing behavior is asserted and no MCP tool owns either claim.
- Upstream: not applicable.
- Related specs: `specs/per-tab-screenshot-capture-and-grounded-captions.md` (INV-123's
  source), `specs/enforce-screenshot-embed-and-backfill.md` and
  `specs/capture-visualization-screenshots-for-recap.md` (the embed/backfill consumers).

## Deviations from this spec, and why (2026-07-31)

**The spec's `Unverified — needs investigation` half resolved, and the mechanism is not the
one it predicted.** The spec said omission "loses a Bootcamper's screenshot" and set the
priority to rise to High if shipped guidance took the branch. Both halves needed correcting:

- **Shipped guidance did take it.** `module-completion.md:250` read *"caption it explicitly as
  the empty/inactive state **or omit it**"* — the disjunction verbatim, at the capture-time
  embed. So it was a live defect, not only a conflict between two invariant texts.
- **But omitting does not lose the image.** Graduation's orphaned-screenshot backfill
  (`graduation/SKILL.md:413-417`) scans `docs/visualizations/*.png` for PNGs *"not already
  referenced"* and embeds **all** of them, citing INV-122 against a count cap. An omitted
  Search / Probe capture is therefore recovered, and **INV-146 survives in outcome.**

**What is actually lost is the caption, which makes the defect self-defeating rather than
merely inconsistent.** The backfill captions from the tab slug — *"use the tab's display name
rather than inventing a description"* (`:433`) — and knows nothing about inertness. So taking
INV-123's omission branch produces an image of an empty search box captioned plainly
"Search / Probe", with nothing disclosing that the snapshot has no engine. That is precisely
the outcome INV-123 exists to prevent, **reached by following INV-123**. The recommendation in
`## Proposed change` was right; the reason recorded for it was wrong.

**One change beyond the spec's criteria, in a file it did list.** Criterion 4 asked only that
both sites "instruct captioning rather than omitting", and graduation's backfill already did
not omit — so it passed as written. But the backfill runs *precisely when the capture step's
own caption never happened* (an interrupted module, a skipped embed), which leaves the
slug-only caption reachable even with `module-completion.md` fixed. `graduation/SKILL.md` is in
the spec's `## Affected files`, so closing that residual hole is in scope: the backfill is now
required to say so when the image it opened shows an empty or inactive search state.

**Criterion 6 had no work, and that was verified rather than assumed.** It asked that any test
pinning the omission branch be repointed (INV-181). Grepping `tests/` for the removed wording
returns nothing — no test pinned it, which is *why* the defect shipped: `module-completion.md`
was swept by `test_screenshot_retention_and_order.py` for count caps and tab order, and nothing
looked for an offered omission.

**Two guards were written badly first, and both failures are worth recording because they are
the same class this repo keeps hitting.** The first sweep regex matched any `omit|drop|skip`
near an image word and fired on prose the rules *require* — the recap PDF "reports every one it
drops" is INV-162, and "the optional ones are yours to include or skip" is about modules —
while simultaneously **missing the actual shipped wording**, because it demanded an image noun
after "or omit it". Too broad and too narrow at once. It is now two narrow patterns, each with
positive controls (the exact clauses removed) and negative controls (the four benign phrases),
so it cannot go vacuous or fire on the rule it protects.

**Three mutations escaped and two were real gaps.** Putting the omission branch back into
INV-123's *ruleset text* broke nothing, because the shipped-guidance sweep reads `plugins/` and
never the invariants — fixed by a new `AnInertCaptureIsCaptionedNeverOmitted` class, which
also needed an `operative()` helper, since a dated in-place note must quote the wording it
removed and a naive absence check fires on that quotation. Downgrading the `⛔` gate to a plain
note also escaped: absence of the old wording is not presence of the new rule, so the gate
marker is now asserted directly. The third escape was an incomplete mutation, not a gap.
