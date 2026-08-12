# A generalized invariant leaves no pointer on the rule whose scope it widened

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

When a later invariant **widens the scope** of an earlier one, `INVARIANTS.md` normally
annotates the *earlier* rule so a reader who lands there is routed forward. The convention is
well established and reads as a warning at the point of use:

```text
INV-083  (⚠️ **See INV-089 before implementing, 2026-08-11.** … satisfying this invariant
          alone leaves the later loads unguarded.)
INV-101  (⚠️ **Its Docker-only scope is superseded by INV-195** … an implementation written
          from this invariant alone would be Docker-only and wrong. Read INV-195 first.)
```

Also on INV-040→INV-198, INV-164→INV-183, INV-162→INV-193, INV-123→INV-146, INV-104→INV-155,
INV-110→INV-048, INV-086→INV-087. **Two pairs are missing it**, and in both the narrower rule
is the one an implementer reaches first.

**1. INV-107 → INV-184.** `specs/INVARIANTS.md:482` binds the inlined brand-palette fallbacks
in `senzing_viz_server.py` and `generate_recap_pdf.py`. `specs/INVARIANTS.md:341` (INV-184)
widens this to *"every shipped generator that inlines a fallback copy of the brand palette"*
and diagnoses the narrowness in as many words:

> INV-107 named two generators; the property belongs to the *pattern*, and the third
> (`generate_discoveries_pdf.py`) drifted out of scope unnoticed while its own comment
> claimed a test asserted it.

INV-107's text is unchanged and names no successor. A reader arriving at INV-107 — the rule
that names the actual constants, so the one a palette change reaches first — still sees a
two-generator rule, which is exactly the scope that let the third drift.

**2. INV-050 → INV-202.** `specs/INVARIANTS.md:152-237` holds the project-layout tree.
`specs/INVARIANTS.md:315` (INV-202) requires every leaf entry to be referenced under
`plugins/` or annotated reserved/superseded/legacy/future, and requires an unproduced entry to
**gain the annotation rather than be deleted**. That rule binds every edit to the tree; the
tree has been amended on 2026-07-20, -26, -28 and -31, and carries no pointer to it.

**The guarantees themselves are intact — this is a routing defect, not a coverage gap.**
`tests/test_brand_sync.py:42-56` does cover the third generator, and
`tests/test_invariant_layout_tree.py` does enforce INV-202. Nothing is unenforced today.

**One citation is genuinely missing**, and it is the Step 2 "enforced by a test that does not
name it" case. `tests/test_brand_sync.py` discharges INV-184 and cites only INV-107 — its
module docstring (lines 1-2) names two generators, and the third generator's own test
docstring narrates INV-184's exact reasoning without naming it:

```text
tests/test_brand_sync.py:45   INV-107 names `senzing_viz_server.py` and `generate_recap_pdf.py`
                              only, so this one's copies could drift silently.
```

So `coverage_reports.py invariants` lists INV-184 as cited by no test, when a test enforces it.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

Different for each pair, and neither was careless.

1. **INV-107 → INV-184.** INV-184 was established by the 2026-07-30 deep-dive audit, whose
   subject was the *unguarded third generator*. The fix landed on the test and on the new
   invariant; the narrower invariant was correct as written for the two files it names, so
   nothing forced a re-read of it. This is the same class-drift shape INV-184 itself
   describes, recurring one level up: the record of the widening lives only on the wide rule.

2. **INV-050 → INV-202.** `specs/inv050-tree-has-no-reachability-guard.md` **explicitly
   forbade** editing INV-050 — *"INV-050 is not shortened, renumbered, annotated or otherwise
   edited: this spec adds a guard only, and the tree is already correct"* — a deliberate guard
   against re-enshrining the false claim of the spec it superseded. That was right. The
   consequence, unconsidered at the time, is that a forward pointer was ruled out along with
   the edits the criterion was actually aimed at.

Measured 2026-08-12: a directional scan over all 204 invariants produced **17** candidate
one-way links; **15 were false positives** — sentences naming an ID precisely to record that
it is *unchanged* (INV-041/INV-042 under INV-198, INV-070/INV-071 under INV-077, INV-046
under INV-155). Only the two above survive reading.

## Proposed change

1. **Append a dated clarification to INV-107** naming INV-184 and stating that the rule binds
   every shipped generator with an inlined fallback, not the two files INV-107 enumerates.
   Wording clarified in place, no meaning change (maintenance rule 2).

2. **Append a dated clarification to INV-050's trailing note block** naming INV-202 and
   stating the annotate-never-delete requirement that binds every edit to the tree. The tree
   itself is **not** touched — no entry added, removed, reworded or reordered.

3. **Cite INV-184 in `tests/test_brand_sync.py`** — in the module docstring and in
   `test_discoveries_pdf_fallback_in_sync`'s docstring, which already narrates the reasoning.
   No assertion changes.

4. **Pin both pairs in `tests/test_invariant_crossreferences.py`**, whose stated defect mode is
   *"a later edit trimming the reconciliation back out"*. Assert the requirement, not a phrase,
   in the style that file already uses.

## Acceptance criteria

- [ ] INV-107's entry in `specs/INVARIANTS.md` names **INV-184** and states that the
      requirement binds every shipped generator carrying an inlined fallback palette. Verified
      by opening `specs/INVARIANTS.md` at INV-107, not from this spec.
- [ ] INV-050's trailing clarification block names **INV-202** and states the
      annotate-rather-than-delete rule for leaf entries.
- [ ] **The INV-050 tree is byte-identical apart from the appended note.** Verified by
      `git diff` on the fenced block showing zero changed lines inside it, and by
      `tests/test_invariant_layout_tree.py` still passing with its pinned entry counts
      unchanged (a changed count means the tree was edited and the change must be reverted).
- [ ] Neither edit changes the meaning of INV-107 or INV-050; both are dated in place per
      maintenance rule 2, and **no ID is renumbered, deleted or reused**.
- [ ] `tests/test_brand_sync.py` cites `INV-184`, and
      `python3 .claude/skills/dry-run/coverage_reports.py invariants` no longer lists INV-184
      as cited by no test. Record the uncited count before and after (79 before).
- [ ] `tests/test_invariant_crossreferences.py` gains an assertion that INV-107 names INV-184
      and one that INV-050 names INV-202, each asserting the **requirement** so a reworded
      note that still carries the link passes — matching that file's existing idiom.
- [ ] **Negative-controlled, with the mutation verified to land:** removing the INV-184
      reference from INV-107 fails the new assertion, and removing the INV-202 reference from
      INV-050 fails the other. Revert both.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` reports **clean**,
      with 204 invariants defined and every citation and Source resolving.
- [ ] `python3 -m unittest discover -s tests` passes in full (baseline: 1,740 tests, OK,
      3 skipped). Record the new total.
- [ ] Stdlib-only, no `plugins/` import in tests (INV-108); holds on Linux, macOS and Windows
      and stays language-agnostic (INV-001/INV-002).

## Affected files

- `specs/INVARIANTS.md` — INV-107 and INV-050 clarification notes.
- `tests/test_brand_sync.py` — INV-184 citation in two docstrings.
- `tests/test_invariant_crossreferences.py` — two new pinned pairs.

## Source

- Audit: `compact-dev-environment`, 2026-08-12 (`Source: self-observed (assistant
  retrospective)`). Found by a directional cross-reference scan over all 204 invariants
  during Step 2, then confirmed by reading every hit.
- Evidence established by opening the files, not inferred: `specs/INVARIANTS.md:482`
  (INV-107, no successor named), `:341` (INV-184's diagnosis of it), `:152-237` (INV-050
  tree), `:315` (INV-202); `tests/test_brand_sync.py:42-56` (third generator covered) and
  `:45` (the uncited narration); `tests/test_invariant_layout_tree.py:1-9` (INV-202 enforced).
- Priority: **Low.** No live defect, nothing a Bootcamper sees, no guarantee currently
  unenforced. The value is that both rules are ones a future maintainer reaches *first* and
  would implement too narrowly from.
- MCP re-check: **n/a — no Senzing fact.** No tool was called for this finding.
- Related specs: `specs/inv050-tree-has-no-reachability-guard.md` (established INV-202 and
  deliberately forbade editing INV-050 — see Root cause 2); `specs/deep-dive-audit-2026-07-30.md`
  (established INV-184).

## Invariants introduced

**None — recorded as a stop-marker instead, pending the maintainer's decision.**

The candidate rule is: *a later invariant that widens an earlier one's scope MUST leave a
dated forward pointer on the earlier one.* It is not registered here, following the
instance-threshold discipline `senz7221-now-names-its-own-remedy` set and
`guards-pinning-a-dated-negative-outlive-it` followed.

Honest count: this exact shape (scope widened, no pointer back) is at **instance 2**.
`tests/test_invariant_crossreferences.py` records three pairs from 2026-07-31, but those are
invariants that *interact* — one constraining, one bounding, one scoping another — not one
widening another's scope, so they should not be counted toward this threshold to make it look
met. Registering an invariant from two instances would also make the ruleset assert a
maintenance rule about itself that only two data points support.

## Deviations from this spec, and why (2026-08-12)

**One acceptance criterion rested on a false premise and was not ticked as written.**

The criterion read: *"`tests/test_brand_sync.py` cites `INV-184`, and `coverage_reports.py
invariants` no longer lists INV-184 as cited by no test. Record the uncited count before and
after (79 before)."* The first half holds. **The second half was never true**: INV-184 was
already absent from that report before any change here, and the uncited count is **79 both
before and after** — it did not move, and could not have.

The Problem section's sentence *"So `coverage_reports.py invariants` lists INV-184 as cited by
no test, when a test enforces it"* is therefore **wrong**, and is left in place per this
skill's no-editing-spec-content rule; this note is the correction.

**What was actually true, on evidence.** INV-184's only prior mention in `tests/` was
`tests/test_recap_pdf_text_column.py:44` — an *analogy inside a comment about a different
guard*:

```text
#: brand palette drifted out of INV-107's scope until INV-184 was needed.
```

So the report scored INV-184 as covered on the strength of a passing reference in a file that
does not enforce it, while the file that does enforce it named only INV-107. That is the
tool's own documented proxy weakness — *"an ID mentioned only in a test's comment or docstring
counts as cited here"* — producing a **false positive for coverage** rather than the
under-report the tool warns about. The finding is unchanged in substance and slightly sharper
in kind: the citation was genuinely missing from the enforcing test, and the coverage report
was structurally unable to say so.

**No other deviation.** Every other criterion holds as written, all are runtime-verified, and
both mutation controls landed and were reverted from `tmp/INVARIANTS.backup` (not `git
restore`, which would have discarded the uncommitted fix alongside the mutation).
