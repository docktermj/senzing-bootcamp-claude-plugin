# The CORD disclosure rule cites INV-012 where INV-247 governs the thing it forbids

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-04-data-collection/SKILL.md:420` ships:

> ⛔ **(INV-012) The two sentences about real data are a statement, not a question — and they are
> not optional.** … Do **not** turn this into a gate — they have already chosen sample data, and a
> 👉 here would ask a question with no action behind it.

The rule has two halves and the citation covers only one of them:

- *"not optional"* — the disclosure must be made. INV-012 is a reasonable fit: output relative to
  the Bootcamper's point of view.
- *"do not turn this into a gate"* — **INV-012 does not govern this.** Its text is *"All output MUST
  be relative to the Bootcamper's point of view. Output that is not important to the Bootcamper is
  suppressed."* That is about what output is **shown**, not about whether the guide may **originate
  a gate**.

**INV-247 is the invariant that governs it, exactly:** *"Every 👉 question presented to the
Bootcamper MUST trace to a step in a shipped skill file; the guide MUST NOT originate a gate the
bootcamp does not specify."* Converting a disclosure into a 👉 is originating a gate the bootcamp
does not specify — the prohibition INV-247 exists for, almost word for word.

## Root cause

The originating spec (`cord-is-described-as-real-world-like-but-the-server-says-it-is-real`) named
**both** invariants in its `## Proposed change` item 4 — *"a gate the plugin's own question-economy
rules argue against (INV-247/INV-012)"* — and the implementation carried only the second into the
shipped line. INV-012 is the weaker of the two for this claim, and it is the one that shipped.

⚠️ This is the **wrong-citation** class, which this repository has paid for twice before (INV-077
cited where INV-129 governs; INV-076 cited as the authority for the name-detection rule). The cost
is not that the citation resolves to nothing — `citations.py verify` is clean and stays clean — it
is that a reader who looks INV-012 up finds a rule about output suppression and cannot tell whether
the gate prohibition is registered anywhere. It is; they just were not sent to it.

## Proposed change

1. Cite **INV-247** at the gate half of the rule at `module-04-data-collection/SKILL.md:420`,
   keeping INV-012 for the not-optional half. Both are correct for their own clause.
2. Check the two sibling disclosure sites added by the same spec —
   `module-01-business-problem/phase1-discovery.md` Step 4b's `cord` branch and
   `module-03b-truthset-visualization/phase1-visualization.md`'s substitute offer — and cite
   INV-247 wherever they repeat the do-not-gate instruction.
3. ⚠️ Do **not** remove the deferred invariant drafted for these rules in the ledger. It covers the
   *disclosure obligation* (that CORD is real data, at every acquisition path), which INV-247 does
   not touch. Only the gate clause is already registered.

## Acceptance criteria

- [ ] The do-not-gate clause cites INV-247 at its line.
- [ ] The not-optional clause still carries a citation appropriate to it.
- [ ] `citations.py verify` stays clean and no invariant is renumbered or deleted.
- [ ] The ledger's deferred invariant for the CORD disclosure is unchanged — it governs a different
      guarantee.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — line 420.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` — Step 4b `cord`.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md`.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, reading every citation the
  unattended run added rather than trusting that a citation exists
  (`Source: self-observed (assistant retrospective)`).
- Priority: Low — nothing is broken and no rule is unregistered; a reader is sent to the wrong rule.
- MCP re-check: n/a (no Senzing fact) — entirely an internal citation question.
- Upstream: not applicable
- Related specs: `cord-is-described-as-real-world-like-but-the-server-says-it-is-real.md` — the spec
  that shipped the rule, and which named both invariants correctly.
