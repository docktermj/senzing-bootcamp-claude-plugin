# Verification grades the engine against the guide's own prediction

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

System verification's Step 2 asks the guide to invent synthetic records and then
**predict how Senzing will resolve them**, from its own reasoning. Step 7 then
validates the engine against that prediction and reports pass or fail. When the
prediction is miscalibrated, the module reports a **verification failure on a
perfectly healthy system** — and its success indicator ("✅ All 8 System
Verification checks report passed") gives the bootcamper no way to tell the two
apart.

This is not hypothetical. It happened on the first attempt of this walk, on a
working Senzing 4.3.4 install:

| Attempt | Synthetic records | Engine result | Step 7 verdict |
|---|---|---|---|
| 1 | 3 records for one person, first name varied `Marisol` / `Mari` / `Marisol`, one record with no `PHONE_NUMBER`; 1 distractor | **3 entities**, largest cluster 2 — `VERIFY-1002` stayed a singleton | ❌ FAILED |
| 2 | same 3 records, first name `Marisol` throughout, only phone/address *formatting* varied; same distractor | **2 entities**, largest cluster 3 | ✅ passed |

The engine was right both times. `Mari` versus `Marisol` is a nickname variant and
the record carrying it had one less corroborating feature, so declining to merge is
a defensible call — arguably the correct one. What failed was the guide's
expectation, and the module reported that as the *system* failing verification.

A bootcamper on the receiving end sees "results validation: failed" at the end of a
module whose whole purpose is to tell them their install works.

## Root cause

`plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md:163-198`
(Step 2) makes the prediction the guide's own:

> "Design them so resolution is deterministic and known in advance: **A merge
> cluster:** 2–3 records for the **same** synthetic person, sharing enough features
> (matching full name + date of birth + address, with only trivial variation) that
> Senzing resolves them into **one** entity."

and

> "**Record the expected outcome** (by construction) for Step 7 to validate against
> … These figures come from the records you just wrote; **never fetch them from
> anywhere**."

`:412-454` (Step 7, "Deterministic Results Validation") then compares the engine's
actual output against those stored figures and writes a pass/fail check.

Two problems compound:

1. **The prediction is a claim about engine behaviour, produced by the guide's own
   reasoning.** That is the one class of Senzing fact the MCP-first invariant
   exists to prevent (INV-080). Step 2 explicitly forbids fetching the figures,
   which is right about *not* inventing a source — but it leaves the guide asserting
   how Senzing resolves, unaided.
2. **"Trivial variation" is doing all the load and is undefined.** Nothing in the
   step says whether a nickname is trivial, whether a missing feature is trivial, or
   how much corroboration a merge needs. The two attempts above differ *only* in
   how that phrase was read, and they produce opposite verdicts.

The module has no mechanism to distinguish a miscalibrated expectation from a real
engine fault, so every failure of this check reads as the latter.

## Proposed change

1. **Make the merge cluster unambiguous by construction, not by judgement.** Spell
   out what the records must share and what may vary: identical `NAME_FIRST`,
   `NAME_MIDDLE` where present, and `NAME_LAST`; identical `DATE_OF_BIRTH`;
   identical address content; and variation limited to **formatting only**
   (punctuation, spacing, phone number formatting, an abbreviated middle name).
   ⛔ **Nicknames, initials-for-first-name, and omitted features are not trivial
   variation** — say so, and say why: they reduce corroboration and the engine may
   correctly decline the merge.
2. **Reframe Step 7's failure as diagnostic, not as a verdict on the install.** When
   the actual outcome differs from the expected one, the check must report *both*
   candidate explanations and give the guide a way to tell them apart — call
   `why_entities` / `why_records` on the pair that did not merge, and report the
   match key and the feature scores. If the engine explains its decision coherently,
   the expectation was wrong and the check should say so rather than failing the
   system.
3. **Do not let this check alone fail the module.** The other seven checks —
   MCP connectivity, engine initialization, SDK initialization, code generation,
   build, data-source registration, loading — are unambiguous pass/fail statements
   about the install. Results validation is the only one that depends on a
   prediction, and it should be reported separately, or downgraded to a warning when
   the engine's own explanation accounts for the difference.
4. Add the first attempt above to the step as a worked counter-example. It is
   short, it is real, and it makes "trivial variation" concrete in a way a
   definition will not.

## Acceptance criteria

- [ ] Step 2 defines the merge cluster by explicit sameness constraints and an
      explicit list of what may vary, with nicknames, initials and omitted features
      named as **not** trivial.
- [ ] Following Step 2 as written produces a cluster that resolves to one entity on
      a healthy install, reproducibly.
- [ ] A results-validation mismatch triggers a `why_entities` / `why_records`
      lookup, and the check reports the engine's own explanation alongside the
      counts.
- [ ] A mismatch the engine coherently explains does not report the bootcamper's
      system as having failed verification.
- [ ] The module's success indicator distinguishes install checks from the
      prediction-dependent check.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` —
  Step 2's record-design constraints; Step 7's mismatch handling.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — the
  success indicator's framing of the eight checks.

## Source

- Feedback: dry run phase 3, 2026-08-13 — composed Step 2's synthetic records and
  ran Step 7 for real against Senzing 4.3.4; the first, reasonable reading of
  "trivial variation" produced a false verification failure (`Source: self-observed
  (assistant retrospective)`)
- Priority: **High** — the module exists to tell a bootcamper their system works,
  and it can tell them it does not when it does.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13. Entity Specification attribute names (`NAME_FIRST`, `NAME_MIDDLE`,
  `NAME_LAST`, `DATE_OF_BIRTH`, `ADDR_LINE1`, `PHONE_NUMBER`, `RECORD_TYPE`, the
  `FEATURES` array) confirmed via `search_docs` before composing the records, so the
  records themselves are not the variable. The engine behaviour observed is this
  install's, not an MCP claim — observation-only (INV-080/INV-149).
- Upstream: not applicable — the engine behaved correctly in both runs.
- Related specs: `specs/statement-only-step-cannot-satisfy-one-question-per-turn.md`
  (same module, the whole-module non-yielding run)
