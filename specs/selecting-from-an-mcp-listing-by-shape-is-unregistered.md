# Selecting from an MCP listing by shape, never by count or position, is a rule in two modules and no invariant

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two shipped steps face the same problem — an MCP tool returns a **listing** of snippets and the
step must pick one — and both solve it with the same rule, stated at length as a ⛔:

- `module-03-system-verification/phase1-verification.md:288-302` (Step 4, `full_pipeline`):
  > ⛔ **This returns MANY files, and which one you save decides whether Step 6 can run at all.**
  > […] **That figure is illustration, never a check to perform** […] So a count or a position is
  > precisely what selection must **not** depend on. […] match on the **shape** — does it open a
  > data file? — never on position in the list.

- `module-02-sdk-setup/SKILL.md:1466-1485` (Step 9, `initialize`), added 2026-08-23:
  > ⛔ **The response is a LISTING and nothing in it marks which snippet does this — pick by
  > shape.** […] ⛔ **A count or a position in the listing is NOT the selector**, and neither is
  > the filename.

**Neither cites an invariant for the selection rule**, and no invariant covers it. `INVARIANTS.md`
has been searched for the subject under *shape*, *position in the list*, *count*, *snippet count*
and *listing*; the nearest hits govern something else (below). So the guarantee exists in two
places in the product and nowhere in the ruleset — the reverse-contract defect INV-134 and INV-155
are the precedents for.

The consequence is not hypothetical: the rule exists **because the counts moved.** Module 3's own
text records `full_pipeline` going from 18 snippets across three groups (server 1.32.2, 2026-07-29)
to 22 across four (1.32.9, 2026-08-14) — a whole group appeared — while the two snippets it names
stayed where they were. A future step written against a count, or a guard asserting one, breaks
silently the next time the server indexes more.

## Root cause

A rule established twice, by two specs, neither of which registered an invariant. Module 3's
version predates the ruleset entry it would have needed; Module 2's was added by
`a-step-names-what-to-select-without-naming-the-route` (2026-08-23), whose ledger entry states it
"establishes no invariant" on the grounds that INV-212 already requires the retrieval strategy at
the step. ⚠️ **That reasoning is half right and is what hid this.** INV-212 requires the step to say
*what vocabulary to query with*; it says nothing about how to choose among what comes back. Naming
a route and selecting from its response are different acts, and only the first is registered.

**The adjacent invariants, and why each is not this rule:**

- **INV-234** governs how a call site must **document** a listing shape — "every shipped call site
  MUST either state that shape or cite the single central statement of it" — and how a derived
  prohibition must be worded. It is about disclosure, not selection.
- **INV-160** governs the elision shape wherever it appears (content absent, URL present).
- **INV-212** governs the retrieval strategy: query vocabulary, which documents hold the material,
  which obvious phrasing misleads.
- **INV-080** governs not filling a Senzing fact from training data.

A guide can satisfy all four and still pick the wrong snippet by counting.

⛔ **No Senzing fact is in question here.** Both sites' Senzing claims were re-verified when they
shipped (Module 2's on server 1.33.0, 2026-08-23: `generate_scaffold(language='python',
workflow='initialize')` returns 14 snippets with `content` absent and nothing flagging any as
engine-creating). What is missing is a plugin-side rule, so this needs no MCP call to resolve.

## Proposed change

1. **Register the rule.** Draft wording, for the maintainer's sign-off — the whole point of this
   spec is that it needs one:

   > **INV-NNN** — Where a step must choose one item from an MCP tool's **listing** response, the
   > selection criterion MUST be a **property of the item** the step can test — what the code does,
   > what a field contains — and MUST NOT be its position in the list, the list's length, or its
   > filename. Every such step MUST name the property, and MUST name at least one item the property
   > **excludes** where a plausible near-miss exists. A count or a group list quoted at such a step
   > is illustration only and MUST be marked as such: the server indexes more over time
   > (`full_pipeline` went 18/3 groups → 22/4 between server 1.32.2 and 1.32.9 while the named
   > items did not move), so a count that reads as a check breaks silently.

2. **Cite it at both sites**, at the rule (INV-183), and at any third site a scan finds.

3. ⛔ **Do not weaken either site to point at the other.** Both are points of use in different
   modules; INV-183 wants the rule reachable *at* the step. Cite the shared invariant from each
   rather than cross-referencing one module from the other.

## Acceptance criteria

- [ ] An invariant governing listing-item selection is registered, with the maintainer's sign-off
      on the wording, the next unused ID, and its index entry in the same edit.
- [ ] Both known sites cite it **at the rule**, and a scan confirms no third site states the rule
      uncited.
- [ ] A test derives the site set by **scanning** for the rule's subject rather than listing the
      two known paths (INV-246), and asserts each site names an excluding near-miss as well as the
      property — negative-controlled by removing the citation at one site and by reducing a site
      to "pick the right one".
- [ ] `conformance.py per-rule --uncited` no longer lists either site's selection rule.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      rule is about response shape, not platform, and both sites already say every language's set
      has the same pair.

## Affected files

- `specs/INVARIANTS.md` — the new invariant plus its index entry.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — cite it
  at Step 4's selection rule.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — cite it at Step 9's.
- `tests/` — the scanning guard.

## Source

- Feedback: none — found by `production-readiness-audit`, 2026-08-23, working
  `conformance.py since --since-last-audit` over the 19 hard-rule lines an unattended
  `/implement-spec` run had just added (`Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** Nothing is currently wrong in either module — both state the rule
  correctly. The cost is that nothing binds a third site to it, and the rule's own subject (counts
  that move) guarantees there will be more listing-selection steps.
- MCP re-check: n/a (no Senzing fact) — the subject is a plugin-side selection rule. Both sites'
  Senzing claims were re-verified on server 1.33.0, 2026-08-23 when they last shipped; this spec
  asserts nothing new about the server and no absence.
- Upstream: not applicable
- Related specs: `specs/a-step-names-what-to-select-without-naming-the-route.md` (the run that
  created the second site and recorded "establishes no invariant"),
  `specs/scaffold-snippet-count-and-group-list-are-stale.md` (the count that moved),
  `specs/download-resource-returns-a-url-not-the-specification.md` (INV-234's origin)

## Invariants introduced

- `INV-267` — Where a step must choose one item from an MCP tool's listing response, the selection criterion MUST be a testable property of the item and MUST NOT be its position, the list's length, or its filename; the step MUST name that property and at least one listed item the property excludes wherever a plausible near-miss exists; a quoted count or group list is illustration only and MUST be marked as such (recorded in `specs/INVARIANTS.md`, group *MCP sourcing and tool contracts*, alongside INV-160, INV-212 and INV-234).

Wording signed off by the maintainer on 2026-08-23 ("all"). The draft was extended with the **"creates an engine" cautionary example**, because that phrase — the one the earlier spec `a-step-names-what-to-select-without-naming-the-route` asked Module 2 Step 9 to use — is itself not a property: both `initialization/engine_priming.py` and `initialization/abstract_factory.py` call `create_engine()`. Recording it in the invariant is what stops the same non-criterion being reached for again.
