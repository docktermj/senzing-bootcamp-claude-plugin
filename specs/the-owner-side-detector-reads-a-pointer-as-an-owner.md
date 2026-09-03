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
