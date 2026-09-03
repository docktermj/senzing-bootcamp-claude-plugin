# INV-124 is cited as the "binds every language" rule at four shipped sites, and it is not that rule

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`visualization-api-reference.md` cites **INV-124** four times as the authority for "this rule
binds a server in any language":

- `:212` — *"This binds a server in **any** language (INV-090/INV-124), not only the bundled
  Python"*
- `:647` — *"…language the server is written in (INV-090/INV-124): it is stated here because a
  rule that lives only…"*
- `:902` — *"**Node labels are painted AFTER every node (required — INV-090/INV-104/INV-124).**"*
- `:904` — *"⛔ **(INV-090/INV-104/INV-124) The natural structure is the defective one:**"*

INV-124 does not say that. It says:

> A visualization server, in whichever language it is generated (INV-090), MUST expose **the tab
> hooks the recap capture depends on**: the contract's tab ids as `tab-<id>` sections and
> `navbtn-<id>` nav buttons, a page-scope `activate(<id>)` function, and `?tab=<id>` / `?q=<text>`
> deep-linking…

It is a rule about **capture hooks**. Its "in whichever language it is generated" clause is a
*scope qualifier on its own subject*, not a general statement that the contract binds every
language. A reader who follows the citation to find out why a **rendering** rule binds their
Java implementation lands on a rule about tab ids and nav buttons, which does not answer them.

The invariants that actually carry it are **INV-002** (the SBCP is language-agnostic) and
**INV-090** (the visualization server is built in the Bootcamper's chosen language, *modeled on
the shipped reference and the `visualization-api-reference.md` contract* — which is what makes a
rule written in that contract binding). **INV-104** is defensible as a secondary, since it names
the contract as the source the app is built from; **INV-124 is not.**

## Root cause

A stock phrase in `specs/`, propagated into shipped text. Three specs carry
`INV-090/INV-104/INV-124` as a fixed string — `visualization-legibility-at-production-scale.md:28`,
`graph-nodes-are-colored-by-their-first-data-source.md:61`, and
`entity-graph-node-occludes-a-neighbors-label-at-small-n.md:53` — each using it to mean "the
visualization contract binds every language implementation". Implementing those specs copied the
trio into the contract file, where it now reads as an authority.

⚠️ **Two of the four sites were added on 2026-09-02 by this loop**, implementing the third of
those specs. The other two predate it, and the pair form `INV-090/INV-124` at `:212` and `:647`
has the same defect: `INV-124` is doing work it does not do. So this is not a new mistake being
reported by its own author — it is a pre-existing mis-citation that a spec's stock phrase kept
reproducing, and it was found by checking a citation added minutes earlier against the
invariant's actual text (the audit's Step 3 reverse sweep).

This is the INV-076/INV-134 class: `INV-076` was cited as the authority for the
name-detection rule, an invariant about the Core-vs-Customized path choice, which says nothing
about names. `citations.py verify` cannot see it — the ID resolves; only reading proves it is the
*right* ID.

## Proposed change

1. Replace `INV-124` with **`INV-002`** in the four "binds any language" citations, keeping
   `INV-090` (and `INV-104` where already present): the pairing that answers the reader's actual
   question is *language-agnostic by contract* plus *this file is the contract the server is built
   from*.
2. Leave INV-124 cited where it governs — the tab-hook requirements (`tab-<id>`, `navbtn-<id>`,
   `activate()`, deep-linking). Check each remaining INV-124 citation in the file rather than
   assuming the four above are the whole set.
3. Correct the stock phrase in the three specs that carry it, so implementing any of them again
   does not re-introduce it. ⚠️ Spec bodies are records; a dated note is preferable to a silent
   edit where the spec is already implemented.
4. ⛔ **Do not amend INV-124 to cover this.** Its wording is correct for its subject, and
   widening it to mean "the contract binds every language" would duplicate INV-002 and make a
   tab-hook rule the authority for every future rendering rule.

## Acceptance criteria

- [ ] No shipped file cites INV-124 as the reason a rule binds languages other than Python.
- [ ] Every remaining INV-124 citation in shipped text is attached to a tab-hook requirement.
- [ ] The four sites cite INV-002 (with INV-090) instead, and a reader following either ID
      reaches a rule that answers "why does this bind my language?".
- [ ] A test asserts that INV-124 is not cited in the same breath as an "any language" claim,
      scanning shipped text rather than the four known lines (INV-246).
- [ ] Negative control: reintroduce `INV-124` into an any-language citation, confirm the test
      fails, revert.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — the four citations
- `specs/visualization-legibility-at-production-scale.md`, `specs/graph-nodes-are-colored-by-their-first-data-source.md`, `specs/entity-graph-node-occludes-a-neighbors-label-at-small-n.md` — the stock phrase
- `tests/` — guard against the mis-citation shape

## Source

- Feedback: `/production-readiness-audit`, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — nothing stated is factually wrong and no behavior is affected, but a citation that does not govern is a rule a later editor cannot look up, and this one is actively reproducing itself through three spec bodies
- MCP re-check: **n/a (no Senzing fact).** Purely internal: the subject is which invariant governs a rule in the plugin's own visualization contract. No Senzing claim is asserted or re-asserted here (INV-080).
- Upstream: not applicable.
- Related specs: the three carrying the stock phrase, named above

## Deviations from this spec, and why (2026-09-02)

1. **The sweep found a FIFTH site, and it was correct — the spec's list of four was not the set.**
   `plugins/senzing-bootcamp/docs/model-selection.md:92` cites INV-124 for *"tab ids and
   deep-linking"*, which is precisely its subject. Left untouched. Proposed change 2 anticipated
   this ("check each remaining INV-124 citation rather than assuming the four above are the whole
   set"), and scanning rather than trusting the list is what found it (INV-246).

2. ⛔ **Removing the four citations left INV-124 stated nowhere in the contract, and an existing
   guard caught it.** `tests/test_any_language_contract_complete.py::test_every_candidate_is_stated_or_reasonably_exempt`
   failed: INV-124 binds the server the Bootcamper builds, so it must be stated in the
   any-language build guidance or recorded as apparatus they do not build — and it was neither
   once the four wrong citations were gone. The contract **did** state the requirement, in the tab
   table at `:688-704`, but cited INV-155 and INV-147 there and not INV-124. Fixed by citing
   INV-124 at that table, which is where it governs and where the ids are normative. ⚠️ **This is
   the finding one level down:** the mis-citation was masking a *missing* citation, so correcting
   it exposed a rule that was registered, guarded, and named at no step (INV-183 / the INV-212
   case). The spec did not anticipate it.

3. **Two existing guards pinned the wrong citation and were rescoped, not deleted.**
   `test_graph_label_distinctness::test_it_tells_a_non_python_implementer_the_rule_is_theirs`
   asserted the literal `INV-090/INV-124`. ⚠️ Corroboration that the correction is right came from
   the repo itself: the sibling guard in `test_any_language_contract_complete.py` already tells a
   failing reader to *"state it in the contract **(INV-002/INV-090)**"* — the pair this spec
   argues for, written before this spec existed.

4. ⛔ **My own new INV-124 citation tripped my own new guard, and the guard was wrong, not the
   citation.** The tab-table citation says the hooks *"bind the server in whichever language it is
   generated"* — an any-language claim beside INV-124, which is exactly the shape the scan
   flags. But there it is **correct**: that is INV-124's own wording about its own subject. The
   scan now exempts a window naming the tab-hook subject, which is the same discriminator the
   surviving-citations assertion applies from the other side, so the two agree instead of
   fighting. **The defect is a citation off its subject, not a citation near a word.**

5. **The spec-side scan in criterion 4 was written, run, and abandoned — deliberately.** It
   flagged **19** sites and every one was legitimate: `INVARIANTS.md` (INV-124's own text contains
   "in whichever language it is generated"), `IMPLEMENTED.md` ledger entries, this spec (which must
   state the defect to describe it), and the three dated correction notes. Four legitimate shapes
   indistinguishable from the defect by proximity; a scan needing to exempt each measures nothing,
   and the exemption list would be the hardcoded-site antipattern in a new hat. The reasoning is
   recorded as a comment where the class would have gone, so the next author does not re-derive
   it. The spec bodies are handled where they should be: corrected in place, each with a dated
   note.

6. **Two of my own guard's thresholds were wrong on the first run.** The sanity check asserted the
   any-language claim appears more than twice in shipped text; it appears exactly twice, so a
   correct tree failed. A threshold guessed rather than measured reports the wrong thing on day
   one — it is now `>= 2` with the measurement in the docstring.

## Invariants introduced

None. This corrects citations to invariants that already exist — **INV-002** and **INV-090** carry
the any-language claim, and **INV-124** keeps its own subject and now has a citation at the table
that states it. No new rule is established; what was missing was accuracy about which existing
rule governs, in both directions.
