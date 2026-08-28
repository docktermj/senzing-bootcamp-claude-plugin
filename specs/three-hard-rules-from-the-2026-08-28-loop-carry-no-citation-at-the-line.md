# Three hard rules shipped by the 2026-08-28 loop carry no invariant at their own line, and one ledger entry claimed otherwise

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py since --since-last-audit` attributes **16** hard-rule lines to the 2026-08-28
unattended loop. Thirteen cite an invariant at the line. **Three do not**, and one of them is
covered by a deferral while two are simply missing a citation:

| Site | Line | Status |
|---|---|---|
| `module-01-business-problem/phase1-discovery.md` | `⛔ **Size the generated scenario to about 10,000 records …**` | **Covered** — a deferred invariant with drafted wording is recorded in the `scenario-generation-has-no-size-cap-or-load-time-warning` ledger entry. The citation is un-writable until the id is minted. |
| `module-05-data-quality-mapping/phase1-quality-assessment.md` | `⛔ **Do not pin an attribute count in this file** …` | **Uncited.** A distinct rule. Its parent (the plain-text parse rule) cites INV-115; this sub-bullet cites nothing. |
| `module-05-data-quality-mapping/phase1-quality-assessment.md` | `⛔ **The applicability set is authored by hand per source …**` | **Uncited.** A ⛔-marked rationale clause inside the INV-174/INV-264 rule's paragraph. |

⚠️ **Nothing here is an unregistered guarantee.** Both uncited lines sit inside paragraphs whose
governing rule *is* cited, so the ruleset covers them. **INV-183 is about the line a reader is
standing on**, not the paragraph — a rule with no id beside it is one a later editor cannot look up,
and "tidy" is what happens to rules nobody can trace.

⛔ **A ledger entry claimed the opposite, and that is the more serious half.** The
`applicability-and-attribute-catalog-are-authored-by-hand-and-fail-silently` entry states that *"all
four hard-rule lines cite one of those at the line"*. Two of the four do not. The claim was written
from a `per-rule --uncited | grep` narrowed to two phrases, which matched neither of the lines that
were actually uncited — the same too-narrow-spot-check method
`production-readiness-audit-2026-08-28` already recorded as unsound, repeated three cycles later.
The entry has been **corrected in place** with a dated note pointing here; this spec exists for the
citations themselves.

## Root cause

Two causes, one per half.

**The citations.** A ⛔ inside a paragraph reads, while writing, as covered by the paragraph's
citation — and it is, for registration purposes. `conformance.py per-rule` measures something
narrower and more useful, and the writing habit does not match the measurement. Sub-bullets and
rationale clauses that carry a ⛔ are exactly where this lands, because they feel like continuations
rather than rules.

**The false claim.** `per-rule --uncited` output is long, so it gets grepped. A grep needs the
phrases you already suspect, which is the opposite of what the check is for — it can only confirm
lines you thought of, and the uncited ones are by construction the ones you did not. The reliable
method is the programmatic cross-reference of `since` output against `per-rule` output, which is
what found this and what the earlier audit entry recommended.

## Proposed change

1. **Cite an invariant at each of the two uncited lines.** `Do not pin an attribute count` is INV-080
   applied to a document figure — a value not re-measured is not asserted — and the applicability
   rationale is INV-174's. Add the ids inline, matching the file's existing `⛔ **(INV-nnn) …**`
   convention.
2. **Leave the scenario-ceiling line uncited until its invariant is minted.** Citing something
   else there would be worse than the gap: it would attach the rule to a governing invariant that
   does not govern it. The deferral already names the site.
3. **Replace the grep with the cross-reference in the loop's own practice.** `unattended-spec-loop`'s
   per-spec step says to check `since` and `per-rule` before writing the entry; it does not say
   *how*, and a grep is the natural reading. State that the check is a set difference between the
   two outputs, not a search of one for phrases you already have in mind.
4. ⛔ **Do not rewrite the false claim out of the ledger.** It is corrected in place with a dated
   note, per the ledger's append-or-correct rule. An entry that quietly becomes true is one nobody
   can learn from.

## Acceptance criteria

- [ ] `per-rule --uncited` lists neither `Do not pin an attribute count` nor `The applicability set
      is authored by hand`.
- [ ] The scenario-ceiling line is still uncited, and its deferral still names it — verified by
      reading the ledger entry, not by the absence of a hit.
- [ ] `.claude/skills/unattended-spec-loop/SKILL.md` states that the reverse-contract check is a
      cross-reference of `since` against `per-rule`, and that grepping `per-rule` for expected
      phrases cannot find what it is for.
- [ ] A test asserts that every hard rule added since the newest audit's recorded commit cites an
      invariant at the line **or** is named in a `DEFERRED INVARIANT` block in the ledger — so the
      two legitimate states are distinguished and silence is neither. Stdlib only, no `plugins/`
      import (INV-108).
- [ ] Negative-controlled: removing either new citation fails the test, and so does deleting the
      scenario ceiling's deferral while leaving the rule shipped.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  two citations
- `.claude/skills/unattended-spec-loop/SKILL.md` — how the reverse-contract check is performed
- `tests/` — a guard distinguishing cited, deferred and silent

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-28, cycle 1 of the second
  unattended loop (`Source: self-observed (assistant retrospective)`). Found by the programmatic
  cross-reference of `since --since-last-audit` against `per-rule --uncited`, which is the method the
  prior audit entry recommended after the same spot-check error.
- Priority: **Low.** No guarantee is unregistered and no bootcamper is affected; both uncited lines
  sit under cited parents. It is filed rather than dropped because the ledger claim was false, and a
  ledger nobody can trust is worth more to fix than two missing ids.
- MCP re-check: **n/a (no Senzing fact).** The subject is citation coverage in this repo's own
  shipped prose and the accuracy of its ledger. `get_capabilities` was called this session to date
  the run: server **1.33.0**, 2026-08-28.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/seven-hard-rules-shipped-in-one-run-with-no-invariant.md` and
  `specs/the-2026-08-21-run-shipped-three-unregistered-guarantees.md` (the same reverse-contract
  class, both about genuinely unregistered rules rather than uncited ones)

## Deviations from this spec, and why (2026-08-28)

**None on content.** All six criteria met. The two uncited lines now cite **INV-080** (a figure not
re-measured is not asserted) and **INV-174** (per-record applicability) at their own lines;
`per-rule --uncited` lists neither. The scenario-ceiling line is deliberately **still uncited** —
citing something else there would attach the rule to an invariant that does not govern it, and its
deferral names the site.

**MCP re-check: n/a, re-confirmed rather than assumed.** The subject is citation coverage in this
repo's own prose and the accuracy of its ledger. `get_capabilities` dated the run: server
**1.33.0**, 2026-08-28.

⛔ **The guard distinguishes three states, not two, and the third is the point.** A hard rule added
since the last audit is **cited**, **deferred by name**, or **silent** — and only silence fails.
Encoding the deferral escape hatch matters because without it the guard would punish exactly the
sanctioned path `implement-spec` Step 5 prescribes when the maintainer is unavailable, where the
citation is un-writable because the id does not exist yet.

⚠️ **A negative control revealed a scope limit, and it is recorded rather than plugged.** Deleting a
citation that was added *after* the newest audit's commit reverts the line to its committed form, so
`since` stops reporting it and the guard is unmoved. That is inherent to a since-last-audit scope
and is the correct behavior: the standing backlog belongs to `per-rule --uncited`, which is far
larger. Re-controlled with a **genuinely new** uncited rule, which fails it as claimed, and the limit
is now written into the guard's docstring so a future reader does not mistake it for coverage.

**The loop skill got the more durable half of the fix.** The citations close two instances; what
caused them is that `unattended-spec-loop` said to *check* `since` and `per-rule` without saying how,
and a grep is the natural reading of that. It now states the check is a **set difference** and ships
the exact script, with the reason: a grep can only confirm lines you already suspect, and the uncited
ones are by construction the ones you did not.
