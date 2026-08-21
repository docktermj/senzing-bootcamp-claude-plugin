# `HARD_RULE` anchors `⛔` to the start of a line, so 191 stop-sign rules — including every one in a numbered list — are invisible to all three conformance views

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py`'s `HARD_RULE` pattern is the definition of "hard rule" for the entire reverse
contract — `rules`, the new `per-rule` and `since` views, and `implement-spec` Step 5's
pre-entry check all inherit it. Its `⛔` alternative is **anchored**:

```python
r"^\s*>?\s*⛔"                                            # start of line, or a blockquote
r"|\*\*[^*]*\b(?:MUST|NEVER|ALWAYS)\b[^*]*\*\*"           # bolded MUST/NEVER/ALWAYS anywhere
r"|^\s*-?\s*\*\*.*?\*\*.*\b(?:MUST|NEVER)\b"
```

So a `⛔` rule counts only when the stop sign is the first thing on its line, optionally behind
`>` or a single `-`. Measured 2026-08-21 across `plugins/senzing-bootcamp/**/*.md`:

| | Count |
|---|---|
| Lines the pattern matches (the number every view reports) | **347** |
| Lines with a `⛔` that is **not** first on the line | **191** |
| …of those, matched by no other alternative either | **191** |

**Every one of the 191 is invisible to all three views**, because the bolded-MUST alternatives
do not save them: a rule written `⛔ **Strip everything identifying.** No hostname, …` has no
`MUST` inside its bold span, so nothing matches.

Three shapes recur, and two of the three are ordinary house style:

1. **A numbered-list item** — `2. ⛔ **Strip everything identifying.**` (`feedback.md:200`). The
   pattern admits `-` before `⛔` but not `1.`, so every hard rule in an ordered list is missed.
   Ordered lists are how this repo writes procedures, which is exactly where hard rules live.
2. **A rule appended to a list item's prose** — `- **`Upstream:`** … ⛔ **Do not offer …**`
   (`feedback.md:275`).
3. **A rule that continues a sentence** — `…else "Unknown". ⛔ Never found by searching`
   (`feedback.md:24`).

⚠️ **This was found by the tooling failing on its author's own rules.** Two `⛔` rules citing
INV-122 were added to the capture blocks on 2026-08-21; `since --ref HEAD` reported **0 added**
with both sitting uncommitted in the tree. The prose was reflowed so each `⛔` starts its line
and both appeared immediately. That fix is correct for those two and does nothing for the other
191.

## Root cause

**The anchor encodes a formatting convention as if it were the definition of a rule.** A hard
rule is a hard rule wherever the stop sign sits; the anchor was presumably chosen to avoid
matching prose that merely *mentions* `⛔`, and it does prevent some of that — `model-selection.md:72`
writes "(⛔ gates, INV-056 pinned wording)" about the concept, not as a rule.

So the correct fix is **not** simply dropping the anchor: that would add real rules and real
noise together, and a count nobody trusts is the failure mode `rules` already has. The
distinguishing signal is what **follows** the stop sign — a rule is `⛔` followed by a bolded
imperative or an imperative sentence; a mention is `⛔` used as a noun ("⛔ gates", "a ⛔",
"the ⛔ convention").

⚠️ **Note the interaction with the section-scoping defect** (`conformance-rules-cannot-see-a-new-rule-beside-an-old-citation`,
implemented 2026-08-21). These are independent and they compound: that one hides a rule whose
*section* cites something; this one hides a rule whose *stop sign* is not first on its line. A
rule can be missed by either, so neither count bounds the other, and the audit reports built on
them understate by an unknown amount in two dimensions at once.

## Proposed change

1. **Match `⛔` anywhere on the line, then discriminate on what follows it** rather than on
   where it sits. A bolded span or an imperative clause after the stop sign is a rule; the stop
   sign used as a noun is not. Keep the discriminator readable and commented — it is the part a
   future reader will need to justify.
2. **Report the two populations separately for one release**, so the change is auditable:
   line-anchored hits (the historical 347, comparable with every prior run's figure) and
   newly-visible mid-line hits. ⛔ Do not silently fold 191 lines into a headline count that
   past audit entries compare against — that would make every recorded figure look like a
   regression.
3. **Do not "fix" the corpus to satisfy the pattern.** Reflowing 191 lines so each `⛔` starts
   its line would be a large diff to shipped prose in service of a regex, and it would leave the
   next mid-line rule invisible again. The two capture blocks were reflowed because their prose
   read better that way; that is not a precedent for a sweep.
4. **State the residual limitation in the output.** After this change the detector still cannot
   see a hard rule written with no `⛔` and no bolded MUST — bare prose "must" was deliberately
   excluded because including it took the candidate list from 16 to 202. That exclusion is
   defensible and should be visible where the count is read.

## Acceptance criteria

- [ ] `HARD_RULE` (or its replacement) matches a `⛔` rule in a numbered-list item, appended to
      a list item's prose, and continuing a sentence.
- [ ] A `⛔` used as a noun in prose is **not** matched; `model-selection.md:72` is the fixture.
- [ ] `rules`, `per-rule` and `since` all inherit the change — no view keeps its own copy of the
      pattern.
- [ ] The output distinguishes line-anchored hits from newly-visible mid-line hits, so figures in
      prior ledger entries remain comparable.
- [ ] The residual limitation (no `⛔`, no bolded MUST) is stated where the count is printed.
- [ ] A test covers all three missed shapes and the noun-usage negative control, and asserts the
      three views agree on the pattern — negative-controlled by restoring the anchor and
      confirming the missed shapes stop being reported.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      `conformance.py` is stdlib-only maintainer tooling under `.claude/`, which `propagate.sh`
      does not ship.

## Affected files

- `.claude/skills/production-readiness-audit/conformance.py` — `HARD_RULE` and the output.
- `.claude/skills/production-readiness-audit/SKILL.md` — Step 1's and Step 3's description of
  what the views count.
- `tests/` — the shape coverage and the noun-usage control.

## Source

- Audit: `production-readiness-audit`, 2026-08-21 (iteration 2). Found while verifying the fix
  for the section-scoping defect: the new `since` view reported 0 added rules for a working tree
  that contained two, which is the tooling failing on its author's own rules in the same session
  it was written.
- Priority: **High.** It is the definition of "hard rule" for the whole reverse contract, the
  miss is 191 lines against 347 found, and it compounds with a defect just fixed for the same
  contract. Every audit figure of this kind understates by an unmeasured amount.
- MCP re-check: n/a (no Senzing fact) — maintainer tooling and the plugin's own prose conventions.
- Upstream: not applicable.
- Related specs: `specs/conformance-rules-cannot-see-a-new-rule-beside-an-old-citation.md` (the
  independent, compounding defect in the same detector),
  `specs/guards-enforce-class-scoped-rules-from-hardcoded-site-sets.md`,
  `specs/the-2026-08-21-run-shipped-three-unregistered-guarantees.md`
