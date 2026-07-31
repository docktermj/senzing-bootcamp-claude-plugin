# Graduation renders two keepsake PDFs and never tells the Bootcamper they exist

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Graduation Step 5b renders two styled PDFs — `docs/business_problem.pdf` and
`docs/data_source_evaluation.pdf` — and instructs the guide to surface them elsewhere
(`plugins/senzing-bootcamp/skills/graduation/SKILL.md:869`):

> Name the ones that succeeded **in the closing summary** alongside the recap PDF; never turn
> a failure into a 👉 question or a to-do for the bootcamper.

**There is no such naming in the closing summary.** Graduation's "Mandatory closing step"
(`:962-973`) enumerates exactly what to announce:

> **Emit one closing announcement** naming only the artifacts confirmed to exist. State that
> the recap PDF at `docs/bootcamp_recap.pdf` … and that the source lives at
> `docs/bootcamp_recap.md`. Name the `production/` project and its `GRADUATION_REPORT.md` and
> `MIGRATION_CHECKLIST.md`.

and its pinned example blockquote (`:973`) names the same four things. Neither mentions either
new PDF. A guide following Step 7 literally announces recap + `production/` and stops.

Confirmed by exhaustive search: `business_problem.pdf` and `data_source_evaluation.pdf` appear
in **exactly two places in the whole plugin** — the Step 5b invocation
(`graduation/SKILL.md:833`) and the renderer's own docstring example
(`scripts/generate_document_pdf.py:19`). Nowhere else.

**What it costs.** The files are written correctly and verified; nothing errors. They simply sit
in `docs/` unmentioned. Step 5b's own framing is what makes that a real loss:
`business_problem.pdf` is *"the document a stakeholder is most likely to be shown"* and
`data_source_evaluation.pdf` is *"the reference a team returns to when someone asks 'why wasn't
field X mapped?'"*. A keepsake the Bootcamper is never told about is, from their side,
indistinguishable from one that was never produced — and graduation is terminal, so there is no
later step to surface it.

**A second consumer is missing too.** INV-050's layout tree names every other keepsake PDF the
flow produces — `docs/bootcamp_recap.pdf` and `docs/bootcamp_data_discoveries.pdf` — and does
not name these two. The tree is explicitly *"not an exhaustive whitelist"*, so a `.pdf` under
`docs/` is permitted; but the 2026-07-26 deep-dive audit specifically **added** three
always-produced deliverables it had omitted, establishing that deliverables of this class get
named. These are the same class by the plugin's own taxonomy — Step 5b opens by saying the
bootcamp *"treats 'rendered as a styled PDF' as the signal that a document is a keepsake rather
than a working file."*

## Root cause

`render-any-bootcamp-document-as-a-styled-pdf` (implemented 2026-07-31) added Step 5b. Its
acceptance criteria named the closing summary twice:

- `:64` — "…extracting text as Step 1b requires (INV-129), **and announce them in the closing
  summary**."
- `:80` — "- [ ] Graduation renders both PDFs after Step 5a, verifies each by text extraction,
  **announces** …"

and its `## Affected files` named it explicitly:

- `:98` — "`graduation/SKILL.md` — the new render step after Step 5a, **and the closing summary**."

Only the render step shipped. The ledger entry lists `graduation/SKILL.md` under Files changed,
so the entry *looks* complete — the file was touched, just not at the second site.

**This is the third recorded instance of one failure mode**, and `implement-spec` Step 4 already
names the first two as the reason that step exists:

| Spec | Criterion named a second consumer | What shipped |
|---|---|---|
| `relocate-integration-deployment-questions-to-module1` | "read by the Module 1 problem statement **and by graduation**" | graduation never touched (INV-097 unimplemented 7 weeks) |
| `defer-commonmark-to-graduation` | "over `docs/*.md` **and the generated `production/*.md`**" | only `docs/` (INV-060 unimplemented 6 weeks) |
| **this one** | "renders … **and announces** them in the closing summary" | only the render step |

So INV-182 — added *because* of the first two — did not prevent the third. It requires each
criterion be "checked individually with its evidence named" and that "a criterion naming a file,
a module, or a **second consumer** MUST be verified by opening that file". A criterion walk was
performed and recorded; it still passed a criterion whose second half was unbuilt, because the
walk confirmed the *render* half and read the criterion as satisfied.

Nothing mechanical could catch it: no test asserts what graduation announces, `coverage_reports.py
affected` compares a spec's predicted paths against the entry's `Files changed:` list and
`graduation/SKILL.md` **is** in that list, and INV-182 is cited by no test.

## Proposed change

1. **Add the two PDFs to graduation's closing announcement**, conditional on existence — Step 7
   item 2 already requires "naming only the artifacts confirmed to exist", so the mechanism is
   there. One clause naming each and what it is for, in the wording Step 5b's descriptions
   already supply.
2. **Update the pinned example blockquote** (`:973`) so it models the announcement including
   them, since the example is what a guide pattern-matches. Keep it conditional in the prose
   ("when they were produced") rather than making the example imply they always exist — Step 5b
   is non-blocking and either can legitimately be absent (INV-048).
3. **Name both PDFs in INV-050's layout tree**, beside `bootcamp_recap.pdf` and
   `bootcamp_data_discoveries.pdf`, as a dated in-place clarification recording what the flow
   produces. This is the same correction the 2026-07-26 audit made for three other deliverables
   and changes no behaviour.
4. **Close the class, not just the instance.** Add a test that every artifact graduation is
   instructed to *produce* is also named in its closing announcement — so the next artifact added
   to graduation cannot repeat this. That is the durable half; items 1-3 are the instance.

⚠️ **Do not make the announcement unconditional.** Step 5b warns-and-continues when a source
document is absent, refused, or fails verification (INV-048), and Step 7 item 1's rule is "Never
announce an artifact you have not confirmed exists at its path." Announcing a PDF that was not
produced is a worse defect than not announcing one that was.

## Acceptance criteria

- [ ] Graduation's closing announcement names `docs/business_problem.pdf` and
      `docs/data_source_evaluation.pdf` when each exists, saying in one clause what each is for.
- [ ] The announcement stays conditional: the instruction is explicit that an absent or refused
      PDF is simply not named, consistent with Step 7 item 1 and INV-048.
- [ ] The pinned example blockquote models the announcement with them included, without implying
      they are always present.
- [ ] Step 5b's instruction at `:869` now resolves — the site it delegates to exists, verified by
      **opening the closing step** rather than by the edit to Step 5b (INV-182).
- [ ] INV-050's layout tree names both PDFs, as a dated in-place clarification stating no meaning
      change; nothing deleted or renumbered.
- [ ] A test asserts that every PDF graduation is instructed to produce is also named in its
      closing announcement, and is not vacuous — it fails if either new PDF is removed from the
      announcement.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean and the
      full suite passes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the closing step (`:962-973`),
  including the pinned example. Step 5b itself needs no change; its instruction becomes correct
  once its target exists.
- `specs/INVARIANTS.md` — INV-050's layout tree, `docs/` block.
- `tests/` — the produce-implies-announce assertion.

## Source

- **Found by `production-readiness-audit`, 2026-07-31** — the first run of that skill. Reached
  via Step 7 class 1 (a rule applied to some of the sites it binds), from the observation that
  `generate_document_pdf.py` was the newest shipped script and therefore the least swept.
- Priority: **Medium.** Nothing breaks and no Bootcamper sees an error; two keepsakes the plugin
  deliberately produces are simply never surfaced, and graduation is terminal so nothing later
  can surface them. Raised by the fact that this is the third instance of a failure mode an
  invariant already exists to prevent.
- MCP re-check: **n/a (no Senzing fact).** Every claim here is internal consistency between
  graduation's own steps, its own renderer and its own layout invariant. No MCP tool owns any of
  it and none was called.
- Upstream: not applicable.
- Related specs: `specs/render-any-bootcamp-document-as-a-styled-pdf.md` (added Step 5b; its
  criteria named the closing summary and the ledger recorded it done),
  `specs/relocate-integration-deployment-questions-to-module1.md` and
  `specs/defer-commonmark-to-graduation.md` (the two prior instances INV-182 was written for).

## Deviations from this spec, and why (2026-07-31)

**No deviation in the fix; one in the guard, and it is the same class the audit that wrote this
spec was hunting.**

Criterion 6 asked for a test that "every PDF graduation is instructed to produce is also named in
its closing announcement", deriving its subject list rather than hardcoding it. The first version
derived from `--output <path>.pdf` occurrences in graduation's bash blocks. That returned
**`['docs/business_problem.pdf']`** — one of the two artifacts — because Step 5b shows a single
worked invocation and names the second document only as `docs/data_source_evaluation.md` in prose,
saying "Render each". `data_source_evaluation.pdf` did not appear anywhere in graduation before this
spec's own edit, so there was nothing for an `--output` sweep to find.

The guard therefore passed while the artifact it was written to protect was dropped from the
announcement — verified by mutation, not inferred: removing `docs/data_source_evaluation.pdf` from
both the instruction and the example was **caught by neither** assertion. That is a guard narrower
than the property it claims, which is `production-readiness-audit` Step 7 item 3 and the **third
instance of that class in a single day** (the omission sweep that fired on INV-162's required prose,
the ruleset text no shipped-guidance sweep reads, and now this).

Fixed by unioning two derivations — `--output` targets *plus* Step 5b's own list of source
documents mapped `.md` → `.pdf` — with `test_output_paths_are_found` asserting at least two are
discovered, so a narrowing of the derivation fails loudly instead of silently reducing coverage.
Eight mutations then all caught, including the class test: a third document added to Step 5b's list
and left unannounced fails.

**A second, smaller instance in the same guard.** `test_each_output_path_is_named_in_the_closing_step`
checked presence anywhere in the closing section — which contains the example — so dropping an
artifact from the *instruction* while the example kept it passed. The instruction and the example are
now sliced apart and asserted separately: the instruction is what the guide is told to do, the
example is what it pattern-matches, and both must name every artifact.

**Nothing else deviated.** The two PDFs are named in the instruction and the example, conditionally;
INV-050's tree names both with the best-effort qualifier; Step 5b's delegation now resolves, verified
by opening the closing step rather than by the edit to Step 5b (INV-182).
