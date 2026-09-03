# The owner-side detector reads a pointer as an owner, because it keys on a phrase not a subject

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`tests/test_a_single_statement_claim_names_its_authority.py` exempts owner-side declarations
from INV-300's owner-naming obligation, detected by:

```python
OWNER_SIDE = re.compile(r"(?:this\s+is|is)\s+the\s+canonical\s+statement", re.I)
```

That matches the phrase wherever it appears, including inside a **pointer**. All four matching
sites in shipped markdown, read:

| Site | Text | Actually |
|---|---|---|
| `module-02-sdk-setup/SKILL.md:718` | *"**This is** the canonical statement of the rule; other modules link here…"* | owner ✅ |
| `module-04-data-collection/SKILL.md:153` | *"**This is** the canonical statement; every other place… refers here"* | owner ✅ |
| `module-04-data-collection/SKILL.md:488` | *"**This is** the canonical statement; do not restate it elsewhere"* | owner ✅ |
| `module-04-data-collection/SKILL.md:1116` | *"see the [sampling rule](#overlap-preserving-sampling) in Step 6, **which is** the canonical statement; do not restate it here"* | **pointer** ❌ |

⛔ **The fourth is a pointer being granted the owner's exemption.** It says *another* passage is
the canonical statement. Nothing is wrong at that site today — it names its owner twice over,
by anchor and by step — so obligation (a) holds there in fact. What is wrong is that it holds
**unasserted**: strip the anchor and the step from that sentence and the guard stays green,
because the exemption swallowed it. The same phrasing in a new pointer would be unchecked from
the day it was written.

A second consequence: the owner-side clause added to INV-300 on 2026-09-03 — *carry the rule
in full, cite this invariant* — is now asserted **of a pointer**, where "carry the rule in
full" is exactly what the pointer must **not** do.

## Root cause

The detector keys on the phrase rather than on its **subject**, and the subject is the whole
distinction: an owner says *"**this** is the canonical statement"* (self-reference); a pointer
says *"X …, **which** is the canonical statement"* (reference to elsewhere). The regex's
`(?:this\s+is|is)` alternation makes the bare `is` branch match the pointer form, and the
pointer form is the one that arrives with a link in front of it.

⚠️ **It was written and negative-controlled the same hour, and the control did not catch this**
— the controls planted a *missing citation* and a *missing owner*, never a *misclassified
site*. A negative control proves the assertion fires; it says nothing about whether the
population it fires over is the right one.

## Proposed change

1. **Require the self-referential subject:** match `this is the canonical statement` (and
   `this … is the canonical statement of`), not a bare `is the canonical statement`. Measured
   against the corpus: all three owners keep the exemption and `:1116` correctly loses it,
   while still passing obligation (a) on its own anchor and step reference — so the fix
   changes classification without changing any site's verdict today.
2. **Say what the tightened detector cannot see**, in the guard: an owner-side declaration
   phrased another way (*"the canonical statement is here"*, *"this step owns the rule"*) will
   be treated as a pointer and required to name an owner it cannot name. ⚠️ The failure
   message must therefore tell the reader that remedy — *phrase a canonical declaration as
   "This is the canonical statement"* — or the next author will add an owner reference that
   points at itself to silence the guard.
3. **Assert the distinction on fixtures**, one owner form and one pointer form, so the
   classifier's population is pinned rather than only its assertion.

## Acceptance criteria

- [ ] `module-04-data-collection/SKILL.md:1116` is classified as a pointer and passes
      obligation (a) on its existing anchor/step reference.
- [ ] The three owner-side declarations keep the exemption and keep passing the owner-side
      citation assertion.
- [ ] Fixture tests pin both classifications — a self-referential owner and a `which is the
      canonical statement` pointer.
- [ ] Negative-controlled by removing the anchor **and** the step reference from `:1116`,
      which must now fail obligation (a); it passes today only because the exemption hides it.
- [ ] The guard's failure message names the owner-side phrasing, so a false positive is
      answered by rewording rather than by pointing a site at itself.
- [ ] Full suite green; `citations.py verify` clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_a_single_statement_claim_names_its_authority.py` — `OWNER_SIDE`, its docstring,
  and the fixture assertions

## Source

- Feedback: none — self-observed during `production-readiness-audit-2026-09-03g`, cycle 1 of the
  second unattended loop (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: **n/a (no Senzing fact).** The subject is a regex in one of the plugin's own
  guards (INV-080).
- Upstream: not applicable
- Related specs: `specs/the-inv-300-guard-checks-one-of-the-invariants-three-obligations.md`,
  `specs/inv-300-is-drafted-from-the-pointer-side-and-cited-at-owner-side-declarations.md`

## Blocked (unattended run 2026-09-03)

**Blocked on criterion 4 — the negative control — which cannot be satisfied by a regex over
this corpus. All partial work was reverted; the tree was left clean at `9f94062`.**

⛔ **The classifier half works and is not the problem.** Tightening `OWNER_SIDE` to require the
self-referential subject (`this is the canonical statement`) classifies all four sites
correctly — `module-02-sdk-setup/SKILL.md:718`, `module-04-data-collection/SKILL.md:153` and
`:488` as owners, `:1116` as the pointer it is — and fixtures pinned both forms. That change
was built, verified, and then reverted with the rest, because on its own it does not satisfy
this spec and the loop reverts a blocked spec's partial work rather than leaving a half-fix the
ledger cannot describe honestly.

**What blocks it: obligation (a)'s check cannot be made to fail on a site that names nothing.**
Three measured attempts:

| attempt | result |
|---|---|
| the shipped pattern (any quoted run of 4+ chars) at ±6 lines | control green — `"this language needs nothing extra"`, prose four lines away in another passage, satisfied it |
| a tightened pattern (link, backticked `.md`/`.py`, `→ "Section"`, italic section, `Step N`, anchor) at ±6 | 0 false positives, control still green |
| the same pattern at ±3 — the tightest sound scope measured (±2 yields 1 false positive, ±1 yields 7) | **control still green** |

⛔ **The leak is structural, not a matter of a better regex.** The italic-section alternative
`\*[A-Z][^*]{3,}\*` also matches **bold** runs, and bold is everywhere in this corpus — within
±3 of `:1116` it matches *"Where 2+ sources are present, …"*, which is ordinary emphasis, not a
reference. Removing that alternative breaks the one site that genuinely names its owner as an
italicized section (`module-02-sdk-setup/SKILL.md:821` → *The launch environment*), which is
how the same pattern reaches zero false positives in the first place. **Markdown does not
distinguish "emphasis" from "section name", so no pattern over it distinguishes a reference
from a phrase.**

⚠️ **A British spelling also turned the suite red during the attempt** (the `-our-` form of
*neighboring*, third occurrence in this session), caught by INV-253's guard. Reverted with the
rest.

### The question that unblocks it

👉 **Which of these, for obligation (a)?**

1. **Ship the classifier fix alone**, with criterion 4 struck: the pointer/owner distinction is
   worth having even where the owner-naming check stays weak, and the weakness is now measured
   and recorded here.
2. **Assert obligation (a) structurally instead of textually** — require a **markdown link or a
   backticked file path** in the claim's own sentence, and reword the handful of sites that
   name their owner in prose (`:821`'s *The launch environment*, and any the scan finds) so
   they carry a link. That makes the obligation checkable, at the cost of editing shipped prose
   to fit a guard — which needs your call, since it is the tail wagging the dog.
3. **Drop obligation (a)'s automated check**, record in INV-300's coverage note that only
   obligation (b) is asserted, and leave owner-naming to review. Honest, and one fewer guard
   that cannot fail.

## Unblocked and implemented (2026-09-03)

✅ **The maintainer chose option 1: ship the classifier fix, strike criterion 4.** The
`## Blocked` section above stands as the record of why that criterion cannot be met — three
measured attempts, and the structural reason markdown defeats them — and is the evidence the
decision was made on.

⛔ **Criterion 4 is STRUCK, not silently dropped, and it is the only one.** It asked for a
negative control that removes a pointer's anchor and step and sees obligation (a) fail. That
control cannot fire for the reason recorded above, so it is retired by decision rather than
left as an unticked box a later reader would try to satisfy. Every other criterion is met:

- Criterion 1 ✅ — module 4's sample gate is classified a **pointer** and passes obligation (a)
  on its existing link and step reference.
- Criterion 2 ✅ — the three owner-side declarations keep the exemption and keep passing the
  owner-side citation assertion.
- Criterion 3 ✅ — fixtures pin both forms, including the real pointer that was misread.
- Criterion 5 ✅ — obligation (a)'s failure message names the owner-side phrasing as the
  remedy, so a false positive is answered by rewording and not by pointing a site at itself.

**A standing control replaces the struck one, and it is a property rather than a count.** The
classifier must discriminate on the **shipped corpus** in both directions: at least one passage
classified owner-side (or the exemption is dead code), and at least one passage that names
*another* location as the canonical statement classified as a pointer (or the loose form is
back). ⛔ **Negative-controlled by reverting `OWNER_SIDE` to `(?:this\s+is|is)`**, which fails
that assertion — naming all four sites the loose form swallows — plus two fixture subtests.
Deliberately not a count of either set: a guard pinned to today's number would have accepted
the wrong one before it.

⚠️ **One defect of my own, found while adding that control:** the new docstring quoted the loose
regex in a non-raw string, so `\s` was an invalid escape sequence — a `SyntaxWarning` today and
an error in a future Python. Made raw, and the other 200-odd test modules were swept for the
same: **zero** carry it. ⛔ **Worth knowing: `tests/test_python_sources_compile_cleanly.py` did
not catch this**, because it compiles without escalating warnings — so a latent syntax defect
passes the suite today.
