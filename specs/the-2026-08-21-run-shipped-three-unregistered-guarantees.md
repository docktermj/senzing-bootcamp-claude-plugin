# The 2026-08-21 implement run shipped hard rules on three subjects `INVARIANTS.md` does not cover, and two capture blocks cite the wrong invariant

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

An unattended run on 2026-08-21 implemented seventeen specs and added **37 new hard-rule lines**
(`⛔` / bolded MUST) across shipped prose. `conformance.py rules` held at **1** hard-rule line in a
section citing no invariant — unchanged from the session baseline — so by that measure the run was
clean. It is not.

**The check is section-scoped.** A section that cites *any* invariant passes, so a brand-new
unregistered rule is invisible whenever it lands beside an unrelated citation. Of the 37 new rules,
three subjects are durable guarantees that `INVARIANTS.md` mentions nowhere at all, and two more
blocks state a rule an *existing* invariant governs while citing three other ones.

This is the reverse-direction defect the audit exists for, and it is the second consecutive
occurrence: `production-readiness-audit-2026-08-17` found the same shape after the previous
unattended run (ten uncited sections, seven genuinely unregistered rules) and added the
`implement-spec` Step 5 guardrail — *an implementation shipping a hard rule owes the invariant or an
explicit deferral in the ledger entry.* This run followed that guardrail on **4 of 15** ledger
entries. The other eleven recorded only *"Establishes no invariant"*, which for these three subjects
was wrong.

## Root cause

### Three subjects with no invariant coverage

Searched `specs/INVARIANTS.md` for each subject in-sentence; none appears:

| Shipped rule | Site | Invariant covering it |
|---|---|---|
| Check whether the project sits on a mounted host filesystem and **measure** the datastore before creating it | `module-02-sdk-setup/SKILL.md`, Step 7 SQLite branch | **none** — INV-200 governs *where* files go, not that a crossing is detected or measured |
| Registration idempotency is **built into the sequence**, never dependent on catching an error | `module-06-data-processing/phaseA-build-loading.md` step 4a; `module-03-system-verification/phase1-verification.md` step 2 | **none** — no invariant mentions idempotency or re-runnability |
| The Poor quality band has **three outcomes**, and the Module 5 remap question is reachable only from the mapping-actionable one; a non-actionable finding still reaches the recap | `module-07-query-visualize-discover/phase1-query-visualize.md` step 3b | **none** — no invariant mentions the possible-match bands or their routing |

Each is a standing rule that binds future work: the first governs every SDK-setup run on a mounted
filesystem, the second governs generated registration code in two modules and is referred to by three
more, and the third governs where a quality verdict may route a Bootcamper. Nothing in the ruleset
records any of them, so nothing binds a later change and nothing notices a contradiction.

⚠️ **The second one is the widest.** `module-03b-truthset-visualization/phase1-visualization.md`,
`module-05-data-quality-mapping/phase3-test-load.md` and
`module-06-data-processing/phaseC-multi-source.md` all require registration "idempotently" **by
reference** to the two statement sites. So the guarantee has five sites and no invariant — precisely
the shape that let INV-134's rule be cited to INV-076.

### Two capture blocks cite the wrong invariant

`module-07-query-visualize-discover/phase1-query-visualize.md` and
`module-03b-truthset-visualization/phase1-visualization.md` both state:

> ⛔ **"No headless capability" is a conclusion the helper reaches and reports, never one you reach
> first.** Enter the silent-skip path on its **exit code** …

They cite `INV-185`, `INV-252` and (in one) `INV-179` — path resolution and state-it-once. The
invariant that actually governs the claim is **INV-122**, which already requires exactly this of the
capture helper:

> Capture MUST remain dependency-optional: when no headless backend is available it exits 2 with a
> message and the module continues unblocked (INV-052/INV-066/INV-048), and **the reason reported MUST
> distinguish "no headless capability" from "no requested tab exists"**.

So the rule is registered and the text does not say so. INV-183 requires a rule binding a step to be
nameable **at** that step; a `⛔` with three citations, none of them the governing one, is worse than
an uncited rule — a reader who checks the citations concludes the subject is covered by path
resolution.

⚠️ **This is not a Senzing fact and needs no re-check.** Every claim here is about the plugin's
agreement with its own ruleset. No MCP route was consulted and none is relevant.

## Proposed change

1. **Draft three invariants and get sign-off before recording any of them.** ⛔ Do not mint wording
   the maintainer has not approved — that is the rule this spec exists to respect, and the reason the
   2026-08-17 spec was deliberately left open. Drafts, for review rather than for merging:
   - *Where the SDK runs in a Linux environment while the project resides on a mounted host
     filesystem, the datastore's placement MUST be measured before it is created, using the
     diagnostic the server prescribes, and the measurement MUST be reported to the Bootcamper; the
     default location MUST NOT change without their explicit consent.*
   - *Generated data-source registration MUST be safe to re-run by construction — load, register,
     export, register the config, replace the default id — and MUST NOT depend on an error being
     raised for an already-registered code, which no route documents for any binding. A per-code
     catch is permitted as a fallback and MUST NOT be the mechanism.*
   - *A quality band MUST NOT by itself route the Bootcamper into remediation. Where a band's cause
     may be a data characteristic rather than a mapping defect, the step MUST establish which before
     offering a remediation loop, MUST state plainly when remediation would not help, and MUST record
     the finding either way.*
2. **Add the INV-122 citation at both capture blocks**, keeping INV-185/INV-252 (they govern the path)
   and INV-179 (it governs the not-restating). This is a citation fix, not a new rule.
3. **Sweep the remaining 37 rules once more with the section-scoping blind spot in mind**, rather than
   trusting the count. The eleven entries that said "Establishes no invariant" were not individually
   re-checked against `INVARIANTS.md` by subject; three were wrong, so the sample is not reassuring.
4. **Correct the eleven ledger entries** that recorded "Establishes no invariant" for a subject that
   turns out to be unregistered — by appending, never by rewriting: the ledger is append-only and the
   correction belongs beside the claim.

## Acceptance criteria

- [ ] Each of the three subjects either has a maintainer-approved invariant recorded with the next
      unused ID and an index entry in the same edit, or an explicit recorded decision not to register
      it with the reason.
- [ ] Both capture blocks cite INV-122 alongside their existing citations.
- [ ] The remaining new hard rules from the 2026-08-21 run are individually checked against
      `INVARIANTS.md` by subject, and the result recorded — not inferred from the `rules` count.
- [ ] Any ledger entry whose "Establishes no invariant" claim is corrected carries the correction as
      an append, with its date.
- [ ] No invariant is deleted or renumbered, and none is recorded without sign-off.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the three
      drafted rules are stated as properties, name no binding's syntax, and the mounted-filesystem one
      is silent where the condition does not arise.

## Affected files

- `specs/INVARIANTS.md` — three new invariants, pending sign-off.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` and
  `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — the
  INV-122 citation.
- `specs/IMPLEMENTED.md` — appended corrections to the affected entries.

## Source

- Audit: `production-readiness-audit`, 2026-08-21, run immediately after the same session implemented
  seventeen specs. Not from bootcamper feedback.
- Priority: **High.** An unregistered guarantee is the class that produced INV-134's wrong citation
  and INV-155's contradicted enumeration, and this is its second consecutive appearance after an
  unattended run.
- MCP re-check: n/a (no Senzing fact) — the subject is the plugin's agreement with its own ruleset.
- Upstream: not applicable.
- Related specs: `specs/seven-hard-rules-shipped-in-one-run-with-no-invariant.md` (the same finding,
  previous run, three invariants still awaiting sign-off),
  `specs/conformance-rules-cannot-see-a-new-rule-beside-an-old-citation.md`
