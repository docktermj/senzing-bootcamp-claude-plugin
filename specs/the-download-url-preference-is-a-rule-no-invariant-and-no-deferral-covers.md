# The `download_url` preference is a hard rule that neither an invariant nor a deferral covers

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-04-data-collection/SKILL.md:469` ships a hard rule:

> ⛔ **Prefer `download_url` (MCP-hosted) over `source_download_url` for every CORD fetch.** Both
> appear in the same `citation`, so both look equally available; they are not. […] Use
> `source_download_url` only when the full uncapped file is genuinely needed…

It is a durable guarantee about **which route the bootcamp fetches CORD data over**. It is:

- **not cited at its line** — no `INV-NNN` appears in it;
- **not named in any `DEFERRED INVARIANT` block** — the entry for
  `cord-source-download-url-403s-the-python-stdlib-client` defers exactly two rules, *"On 403, do
  not retry — switch URLs"* and *"Never set a misleading User-Agent to get around it"*, and this
  third one is not among them;
- **not reported by `conformance.py per-rule --uncited`**, because the paragraph two lines below it
  reads *"⚠️ **Observation, not an MCP-sourced fact (INV-080/INV-149).**"*, and `per-rule` counts an
  invariant cited in the **sentence beside** a rule as citing it.

INV-080 and INV-149 govern **the provenance of the 403 observation** below the rule. They say
nothing about route preference. So the accounting is satisfied by a citation that is about
something else — which is the precise shape `production-readiness-audit`'s Step 3 names: *"a
section that cites an invariant for a reason unrelated to the rule added below it … the shape that
hides a new rule."*

⚠️ **The guard that exists for this could not see it either.**
`tests/test_new_hard_rules_are_cited_or_deferred.py` asks "cited **or** deferred", and takes
`per-rule --uncited` as the authority on "cited". Because `per-rule` accepted the neighboring
citation, the rule never reached the deferral check. The guard is working as specified; the
specification has a gap where a rule's neighbor supplies its citation.

## Root cause

Two independent things line up:

1. **The implementation deferred two of the three rules it shipped.** The 403 spec's ledger entry
   was written from the two rules the INV-282 set difference reported, and that set difference is
   computed from `per-rule --uncited` — which had already absorbed this rule. So the deferral
   inherited the blind spot rather than causing it.
2. **`per-rule`'s "cited beside" rule has no relevance test.** It cannot, and should not try to —
   a regex cannot judge whether INV-080 is about route preference. But nothing downstream re-asks
   the question a reader would, and the two consumers (`per-rule --uncited`, and the guard built on
   it) both treat proximity as sufficient.

## Proposed change

1. **Decide what governs the preference and record it.** Either:
   - cite an existing invariant at the line if one genuinely governs choosing a provider-supplied
     route (⚠️ none was found on 2026-09-01 — INV-080 and INV-149 do not, and citing either would be
     the wrong-citation class); **or**
   - draft an invariant for it and record it as a `DEFERRED INVARIANT` in the ledger entry for
     `cord-source-download-url-403s-the-python-stdlib-client`, alongside the two already there.
     A candidate is already drafted in that entry and covers this rule's subject — *"Where a
     provider supplies more than one URL for the same content, the bootcamp MUST prefer the route
     served to programmatic clients and say why"* — so this may be a bookkeeping fix rather than a
     new draft: the deferral's **wording** covers the rule; its **list of rules** omits it.
2. **Report, do not silently widen `per-rule`.** Treating a neighbor's citation as insufficient
   would change the number every ledger entry has been measured against, and that is a maintainer
   decision with a large blast radius. What is cheap and safe is to make the *guard* stricter than
   the report: have `test_new_hard_rules_are_cited_or_deferred.py` require the citation to be **on
   the rule's own line** for rules added since the last audit, falling back to the deferral check
   otherwise.

⚠️ **Do not "fix" this by moving the observation paragraph.** The proximity is legitimate — the
observation belongs beside the preference it justifies. The defect is the accounting, not the
prose order.

## Acceptance criteria

- [ ] The `download_url` preference is either cited at its line by an invariant that genuinely
      governs it, or named in a `DEFERRED INVARIANT` block with drafted wording.
- [ ] The rule is no longer accounted for solely by a neighboring citation about provenance.
- [ ] A guard fails when a hard rule added since the last audit has no citation **on its own line**
      and no deferral naming it. Negative-controlled: strip the citation from a line-cited rule and
      confirm it fails; restore.
- [ ] `conformance.py per-rule`'s own counting is unchanged unless the maintainer chooses otherwise
      — every past ledger figure was measured against it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — line 469.
- `specs/IMPLEMENTED.md` — the `cord-source-download-url-403s-the-python-stdlib-client` deferral.
- `tests/test_new_hard_rules_are_cited_or_deferred.py` — the stricter line-level check.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, reading all 32 hard-rule
  lines the run added rather than trusting the guard that had passed on them
  (`Source: self-observed (assistant retrospective)`).
- Priority: Medium — no shipped guidance is wrong, and the rule itself is correct and well
  evidenced. What is wrong is that the mechanism built to stop unregistered guarantees shipping
  reported this one as accounted for. That mechanism is the reverse-contract defense, and a gap in
  it is worth more than the rule it missed.
- MCP re-check: n/a (no Senzing fact) — the rule's Senzing content was verified when it shipped
  (server 1.35.3, 2026-09-01); this spec is about its citation.
- Upstream: not applicable
- Related specs: `cord-source-download-url-403s-the-python-stdlib-client.md` (shipped the rule);
  `the-cord-disclosure-rule-cites-inv-012-where-inv-247-governs.md` (the other citation finding from
  the same audit).
