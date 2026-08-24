# The INV-251 relabel missed six sites its own guard cannot see

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`993df3a` registered **INV-251** (a turn MUST NOT carry two or more 👉) and relabeled the sites
that had been citing INV-005 for the count. It shipped with a guard,
`tests/test_one_question_per_turn_is_registered.py`, that sweeps shipped Markdown for lines stating
the count and fails any that cite INV-005/008/009.

**The guard passes. Six wrong citations survive it**, because its `COUNT_RULE` regex enumerates the
phrasings its author happened to think of, and the corpus uses others.

**Four still state the count and should cite INV-251:**

| Site | Text |
|---|---|
| `bootcamp-preparation/SKILL.md:174` | "INV-005 requires the 👉 question to **end the turn**, so nothing can follow it" |
| `bootcamp-preparation/SKILL.md:256` | "*(Internal: end the turn on this **single** 👉 question and wait — INV-005.)*" |
| `module-00-entity-resolution-concepts/concepts.md:150` | see the double-citation defect below |
| `module-02-sdk-setup/SKILL.md:298` | "**One 👉 question, its own turn** (INV-005), and it ends the turn" |

**Two state the ZERO case and should cite INV-225**, not INV-005 — and not INV-251 either, since
INV-251 deliberately covers only the two-or-more half:

| Site | Text |
|---|---|
| `module-01-business-problem/phase1-discovery.md:14` | "a turn ending here would end with **zero** 👉, which INV-005 forbids" |
| `module-03-system-verification/phase1-verification.md:12` | "a turn ending on a step that asks nothing would end with zero 👉 (INV-005)" |

⛔ **And one defect was INTRODUCED by the relabel itself.** `concepts.md` reads, after `993df3a`:

```markdown
- Ask a **short** series (about 3-5) of entity-resolution questions, **one 👉 question per turn** (INV-251)
  (INV-005), evaluating the bootcamper's answer each turn before asking the next.
```

Before the relabel it was one wrapped sentence whose citation sat on the continuation line:

```markdown
- Ask a **short** series (about 3-5) of entity-resolution questions, **one 👉 question per turn**
  (INV-005), evaluating the bootcamper's answer each turn before asking the next.
```

The edit appended `(INV-251)` to the first line without reading the second, so the sentence now
renders **"one 👉 question per turn (INV-251) (INV-005)"** — a double citation, the second of which
is the very misattribution the commit existed to remove.

## Root cause

**A guard whose site set is a list of phrasings, in a corpus that phrases things freely.**
`COUNT_RULE` matches `exactly one 👉`, `one 👉 question per turn`, `one question per turn`,
`turn carries exactly one`, `two or more 👉` and two `ends the turn on …` forms. The corpus also
writes:

- *"end the turn on this **single** 👉 question"*
- *"**One 👉 question, its own turn**"*
- *"INV-005 requires the 👉 question to **end the turn**"*
- *"would end with **zero** 👉"*

None matches. So the guard is green while six sites carry the defect it was written to prevent —
**defect class 3 exactly: a guard narrower than the invariant it claims to enforce.**

⚠️ **The guard also scans `plugins/**.md` only.** The `tests/` and `.claude/` sites were corrected
by hand in `993df3a` and nothing holds them there; a future edit reverting
`transcript_lint.py`'s finding code in a differently-worded line would pass.

⛔ **This is the third undercounting sweep of the same session, and that is the finding worth
carrying forward.** (1) `production-readiness-audit-2026-08-15k`'s first sweep required "per turn"
near "one" and reported *"no test enforces it"* — wrong; a backgrounded grep caught three files it
missed, and enforcement existed in `transcript_lint.py`. (2) The corrected sweep found 13 shipped
sites; this run finds the relabel still left six. (3) The `inv077-…` spec claimed its class had one
instance because its sweep scanned `plugins/` only, and two more sat in `tests/`. **Every one was a
pattern-list sweep over a corpus that does not restrict itself to the author's patterns**, which is
INV-246's reasoning applied to phrasing rather than to paths.

## Proposed change

1. **Fix the six citations** — four to INV-251, two to INV-225.
2. **Fix the double citation** at `concepts.md:149-150`: one citation, INV-251, on the sentence.
3. **Widen the guard's reach so it stops depending on a phrase list.** The robust signal is not the
   wording but the **conjunction**: a line that mentions 👉 *and* a turn-count concept *and* cites
   one of INV-005/008/009. Match on that shape — 👉 within a line that also contains `turn` and a
   count word (`one`, `single`, `two`, `zero`, `exactly`) — and require the citation to be INV-251
   (two-or-more) or INV-225 (zero), with an explicit allow-list for the marker/shape uses of
   INV-005/051 that are **correct**.
4. **Extend the scan to `tests/` and `.claude/`**, which currently hold corrected-by-hand sites with
   nothing guarding them.
5. ⛔ **State in the guard's docstring that its reach is a heuristic over phrasing**, and that a
   clean run means "no line matching these shapes is misattributed" — not "no misattribution
   exists". The previous docstring disclosed the *runtime* limit and not this one, which is how a
   green guard read as complete coverage.

## Acceptance criteria

- [ ] The four count citations name INV-251; the two zero-case citations name INV-225.
- [ ] `concepts.md` carries exactly one citation on that sentence, and it is INV-251.
- [ ] The guard fails on every one of the six sites when they are reverted — **negative-controlled
      site by site**, not by one representative mutation, since the whole defect is that one
      phrasing passing does not imply the others do.
- [ ] The guard's scan covers `tests/` and `.claude/` as well as `plugins/`.
- [ ] The guard's docstring states that its matching is a phrasing heuristic and what a clean run
      therefore does and does not mean.
- [ ] The correct INV-005 uses survive — `phase2-data-mapping.md:226` ("carries **no 👉** … breaching
      INV-005 and INV-051") is the **marker** rule used rightly and MUST NOT be rewritten.
- [ ] ⛔ Not runtime-verified: whether a guide ends a turn on one question remains a live-turn
      property (INV-251's own disclosure). This spec only fixes *labels* and the guard's reach.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — `:174`, `:256`.
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — `:149-150`.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:298`.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — `:14`.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — `:12`.
- `tests/test_one_question_per_turn_is_registered.py` — the regex, the scan's reach, the docstring.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15l
  (`Source: self-observed (assistant retrospective)`). Found by self-auditing `993df3a`, this
  session's own work — the same practice that found the defect in `c9dfe60` during audit **g**.
- Priority: **Medium.** No bootcamper is affected: every site still *states the rule correctly*, and
  only the ID beside it is wrong. But the commit that existed to remove this misattribution left six
  instances and added a seventh, while its guard reported success — and a guard that reads as
  complete is worse than no guard, because the next audit trusts it.
- MCP re-check: **n/a (no Senzing fact).** Internal: invariant IDs against the claims they are
  attached to. No Senzing claim asserted, no absence about the server relied on. Server **1.32.9**
  (`get_capabilities`, 2026-08-15) recorded earlier this session.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `the-one-question-per-turn-rule-is-registered-nowhere` (the commit this corrects),
  `inv077-supersession-dropped-the-visualization-verification-guarantee` (same session, same
  undercounting-sweep root cause), `guards-enforce-class-scoped-rules-from-hardcoded-site-sets`
  and `any-language-contract-guard-checks-a-hardcoded-requirement-set` (the INV-246 family this
  extends from paths to phrasings), and INV-005, INV-051, INV-225, INV-246, INV-251.

## Deviations from this spec, and why (2026-08-15)

- ⛔ **The spec said six sites. There were TWELVE.** Widening the guard found six more that no
  sweep in this session had reached, and each was found only after a further widening:
  - `tests/test_sdk_update_offer.py:295` and `.claude/skills/dry-run/phase3-conversational.md:171`
    — found by extending the scan **beyond `plugins/`**. The second matters most: it is `dry-run`
    **phase 3's own interaction checklist**, so a live-turn breach would have been reported against
    INV-005.
  - `ground-rules.md:39` — *"**Exactly one** 👉 question ends each yielding turn (zero or
    two-or-more is a violation)"*, a canonical statement of **both** halves carrying **no citation
    at all**. The guard could not see it because it flags *wrong* citations, not missing ones.
  - `tests/test_non_yielding_steps.py:52`, and `tests/test_phase3_interaction_prose.py:18` and
    `:221` — found only after the detector stopped requiring a quantity word.
- ⛔ **The guard's matching unit was wrong TWICE, and site-by-site negative control is the only
  reason that surfaced.** The spec's criterion — *"negative-controlled site by site, not by one
  representative mutation"* — earned itself immediately:
  - **Per line** (as shipped in `993df3a`): 3 of 8 mutations **escaped**. The corpus wraps prose,
    so a citation and the 👉 it refers to sit on different physical lines.
  - **Per paragraph**: fixed those three and produced **4 false positives** — consecutive
    non-blank lines merge a whole bullet list, pairing a correct INV-251 bullet with an unrelated
    INV-008 citation three bullets away.
  - **Per window around the citation** (±140 chars of the joined paragraph): correct on both
    counts, and what shipped.
  A single representative mutation would have printed `LANDED` at every stage.
- **The detector's third conjunct was still too narrow after all that.** It required a quantity
  word, so *"INV-005 requires the 👉 question to **end the turn**, so nothing can follow it"* — a
  turn-shape claim with no number in it — escaped. Widened to *quantity **or** ends-the-turn*,
  which immediately surfaced the two `test_phase3_interaction_prose.py` sites.
- **An `EXEMPT` clause was needed for correct text that names the wrong invariant deliberately.**
  A passage saying *"interprets INV-251 … **not INV-005**"* states the distinction rather than
  breaching it; without the carve-out the guard fails on its own corrections.
- **One existing guard moved with the fix** — `test_non_yielding_steps.py` pinned
  *"which INV-005 forbids"* for the zero case, which is INV-225. That failure was the guard working.
- **Establishes no invariant.** This corrects labels and widens a guard; INV-251 and INV-225 were
  already registered and their conditions are untouched.
- ⛔ **Not runtime-verified.** Whether a guide ends a turn on one question remains a live-turn
  property — INV-251's own disclosure. This work fixed *labels* and the guard's reach, nothing
  about behavior.
