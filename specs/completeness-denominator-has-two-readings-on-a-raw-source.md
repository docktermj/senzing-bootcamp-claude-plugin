# The completeness denominator has two readings, and they differ by "undefined vs 100%"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5 Phase 1 step 6 opens by insisting the quality score must be reproducible between guides:

> ⛔ **Compute it this way — the number routes a gate banded to the percentage point, so two guides
> must reach the same figure.** The bands below (≥80 / 70-79 / <70) were precise while the arithmetic
> feeding them was never written down, which meant the score was reproducible only by accident

It then defines the completeness denominator like this:

> **completeness (0-100)** — the mean, across records, of the share of **applicable** fields that are
> present in that record … **Which fields count:** every field that **resolves to** an Entity
> Specification attribute or a structural key, **plus** any source field already dispositioned in
> mapping. A raw source column the bootcamper has not yet been asked about does **not** count.

On a **raw source** — the "Needs mapping" category, which is this module's central case — that
sentence has two defensible readings that give different answers:

**Reading A — key identity.** "Resolves to" means *the key itself is a catalog attribute*, possibly
carrying a usage-type label. This is exactly how the same phase uses the word twelve steps later, in
Step 5a's coverage check:

> **specification attributes** — keys that **resolve to** an attribute in the Entity Specification
> you retrieved in Step 3 … ⛔ **Do not resolve the second set by exact string match against the
> attribute catalog.** A catalog attribute can arrive carrying a leading label … `BUSINESS_NAME_ORG`
> and `BUSINESS_ADDR_LINE1` … while the specification's catalog names the attributes `NAME_ORG` and
> `ADDR_LINE1`

Under A, a fully raw source has **zero** countable fields — `account_id`, `full_name`,
`mailing_address`, `phone`, `email_address`, `created_date` are none of them catalog attributes, with
or without a label — nothing is dispositioned yet, so completeness is **0/0 and the score that gates
the module is undefined.**

**Reading B — mapping intent.** "Resolves to" means *the field has a specification counterpart*, as
identified in **Step 4**, which runs immediately before and does exactly that comparison ("Identify
which fields map directly to attributes defined in the Entity Specification"). Under B the
denominator is well defined.

**Observed live, phase-3 dry run, 2026-08-14.** Three raw sources scored under **reading B**
(denominators of 5, 9 and 8 applicable fields per record) and produced 100.0 / 100.0 / 100.0. Under
reading A the same three sources produce no score at all. The walk chose B, said so to the maintainer,
and reported the ambiguity rather than presenting the figure as unambiguous.

The tie-breaker sentence is what keeps A alive: *"A raw source column the bootcamper has not yet been
asked about does not count."* Under B, `full_name` has not been asked about either — it is simply a
column the guide judged has a counterpart — so the sentence reads as excluding it.

### Why the step's own evidence points at B, and still does not settle it

The presented example is a raw-looking CRM source with source-native field names:

```text
Source: CUSTOMERS_CRM
  Field completeness:  82%  (name: 99%, phone: 75%, email: 68%)
```

`name`, `phone`, `email` are not catalog attribute codes (`NAME_FULL`, `PHONE_NUMBER`,
`EMAIL_ADDRESS`), which suggests source fields — reading B. But they are also not the source's column
names in any stated schema, so the example is illustrative rather than decisive.

And the PPP_LOANS figure quoted in the same bullet — *"scored 100% on its 8 resolving fields and
94.4% averaged over all 19 root keys"* — is a **partly** compliant CORD source, where A and B nearly
coincide. Every worked number in the step comes from a case that does not discriminate the two
readings.

⚠️ **Confidence note.** Reading A may simply be a misreading on my part, and the step may be entirely
clear to its author. It is filed because the step **states reproducibility between two guides as its
purpose**, and on the module's most common input the two readings differ by "no score" versus "100%".
If a reviewer judges B obviously intended, the correct outcome is a one-sentence clarification (or
closing this with that conclusion recorded), not a redesign.

## Root cause

`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`,
step 6's "Which fields count" bullet — it defines membership by a verb ("resolves to") that the same
phase uses in a narrower sense for a different purpose in Step 5a, and its clarifying sentence
("a raw source column … does not count") is the half that pulls toward the narrower sense.

The deeper cause is that the bullet was written to fix a real false-alarm (INV-174: don't score a
source down for work the module has not done yet) and the fix was expressed as an exclusion, without
stating what the denominator *is* for a source where nothing is dispositioned at all.

## Proposed change

**Say which fields count for a raw source, positively and with a worked example.** In step 6's
bullet:

1. **State the intended reading explicitly.** Presumed B: a source field counts once the guide has
   identified an Entity Specification counterpart for it in **Step 4** — cite Step 4 by number, so
   the dependency is visible and the reader knows where the set comes from.
2. **Distinguish it from Step 5a's use of "resolve".** One clause: Step 5a asks whether the **key
   itself** is a catalog attribute (a CORD-shaped question about an already-Senzing-ready source);
   step 6 asks whether the **field has a counterpart** (a raw-source question). Same word, two
   questions, and naming that is cheaper than renaming either.
3. **Keep the exclusion, narrowed to what it was for.** A source column with **no** specification
   counterpart and no disposition stays out of the denominator — that is INV-174's false-alarm fix and
   it is correct. What must not be excluded is a column whose counterpart Step 4 just identified.
4. **Add a worked example on a fully raw source**, since every existing example is a partly compliant
   one. A three-column CRM (`full_name` → `NAME_FULL`, `phone` → `PHONE_NUMBER`, `created_date` →
   undecided) makes the denominator unambiguous in two lines.
5. **State what happens if the denominator is genuinely empty** — a source where no column has any
   counterpart. Completeness is undefined, so say so and route it to "Needs enrichment" rather than
   emitting a score; a 0/0 must never be reported as 0%, which would route a gate to
   "Recommend fixing before mapping" on arithmetic rather than evidence.

## Acceptance criteria

1. Step 6 states positively which source fields enter the completeness denominator on a raw source,
   citing Step 4 as where the set is established.
2. Step 6 distinguishes its use of "resolves to" from Step 5a's, in one clause, without changing
   Step 5a (asserted unchanged).
3. The INV-174 exclusion survives for columns with no counterpart and no disposition.
4. A worked example on a fully raw source is present, with its denominator shown.
5. The empty-denominator case is handled: completeness is reported as undefined and the source routed
   to "Needs enrichment"; a test asserts no instruction permits reporting 0/0 as 0%.
6. The formula, the three bands, the presence test (INV-128) and the per-`RECORD_TYPE` applicability
   rule (INV-174) are all asserted **unchanged** — this clarifies the denominator's membership only.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
- `tests/test_completeness_denominator.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, computing step 6's score for three raw
  synthesized sources and having to choose between two readings of the denominator rule to produce a
  figure at all (`Source: self-observed (assistant retrospective)`). Reading B was used, disclosed to
  the maintainer at the time, and the resulting 100% scores were sanity-checked against sample values
  per the step's own ⛔.
- Priority: **Low-Medium.** No bootcamper is misled — a guide taking reading B gets a sensible number
  — but the step names cross-guide reproducibility as its reason for existing, and on the module's
  most common input the two readings do not agree. Cheap to settle either way.
- MCP re-check: n/a (the formula, bands and denominator are the plugin's own; no Senzing fact).
  Server version this session is **1.32.9** (`get_capabilities`, 2026-08-14).
- ⚠️ **Related:** `specs/synthesized-scenarios-make-the-quality-gate-unreachable.md` from the same
  walk. If that one lands first, generated sources will carry real gaps and the denominator question
  becomes *more* visible, not less — a partially populated raw source is where the two readings
  diverge in the reported percentage rather than only in definedness.

## Invariants introduced

- `INV-238` — A computed metric whose denominator can be empty MUST define that case explicitly and
  report it as **undefined**, never as zero; and where a gate's stated purpose is reproducibility
  between two guides, the metric's membership rule MUST be stated positively and MUST NOT rest on a
  verb the same document uses in a narrower sense elsewhere (recorded in `specs/INVARIANTS.md`).

## Deviations from this spec, and why (2026-08-14)

- **Reading B was adopted as the spec presumed, and the ambiguity resolved by stating the rule
  positively rather than by re-defining "resolves to".** Step 5a is untouched and asserted unchanged;
  step 6 now names the difference between the two questions, which is what the spec asked for and is
  cheaper than renaming either use.
- **The spec's quotation of Step 5a adds emphasis the file does not carry.** Step 5a reads "keys that
  resolve to an attribute in the Entity Specification", unbolded; the spec renders it "keys that
  **resolve to** an attribute". The assertion pins the file's actual text. Nothing was changed in
  Step 5a to match the quotation.
- ⚠️ **Criterion 5's sweep took four formulations, and the three discarded ones are recorded in the
  test because each looked correct.** (a) Detecting a *zero* claim with `\b` after `0%` can never
  match — `%` and the following comma are both non-word characters, so the pattern matched nothing
  while appearing to work. (b) Segmenting text by `[^.]*\.` is unusable on this page: a fenced
  example contains no period, so one "sentence" spanned hundreds of characters and absorbed an
  unrelated negation. (c) Requiring a negation near the claim fails on this very page, whose worked
  example legitimately ends "not 3, and not 0". The shipped form states the requirement positively —
  wherever an empty denominator is named, "undefined" must be named with it.
- ⚠️ **The sweep's control is an insertion, not an edit**, and getting that wrong is what hid its
  emptiness for three attempts: for a "no instruction permits X" sweep, deleting every mention passes
  *correctly*, so editing the block under test can never demonstrate the sweep works. Verified by
  inserting "If the completeness denominator is empty, report 0/0 as 0% and continue." into
  `phase2-data-mapping.md`, which the sweep catches. The handling's existence is pinned by three
  separate tests, each verified to fail when the block is removed.
- **Two earlier mutations also escaped for the same reason and are not counted as guard weaknesses:**
  replacing only a bold lead sentence left the following sentence stating the same rule, so the
  assertion still matched. A mutation that does not remove the behavior proves nothing.
