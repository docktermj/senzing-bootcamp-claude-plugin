# `business_problem.md` keeps only the refined wording, so the confirmation gate cannot catch a changed meaning

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`docs/business_problem.md` records the guide's **refined** rendering of each interview answer and
preserves nothing of what the Bootcamper actually said. They asked that their own language be kept
alongside it:

> "capture the exact language of the user in the bootcamp in addition to the refined version"
>
> "It's good to have captured for later use."

Checking the document against the transcript turned this from a preference into a defect. Asked
about downstream integration, the Bootcamper said:

> "Yes. **possible fraud** needs to feed our fraud tool and possible matches need to feed into
> service now."

`docs/business_problem.md` line 43 rendered that as:

> "Internal fraud tool (**confirmed fraud cases**); ServiceNow (possible matches for review)."

*Possible* became *confirmed*. That is a different routing rule — it changes which entities reach
the fraud tool and how large that queue is. Line 37 of the same document still read "Possible-fraud
entities routed to the internal fraud tool", so **the document contradicted itself** and carried
nothing that could settle which reading was right.

⛔ **It then propagated three modules downstream.** Module 7 step 1 derives query requirements *from
this document*, and requirement 7 was consequently titled "Confirmed-fraud candidate list for the
internal fraud tool". The Bootcamper accepted the derived requirements (`no` to *"Is there anything
you'd like to adjust?"*) — reviewing, again, only the refined artifact.

## Root cause

**The template has no place for the Bootcamper's own words.**
`plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md:117-168`
defines what Step 11 writes, and every field is a rendering:

```markdown
## Problem Description
[One sentence]
…
## Integration Requirements
**Downstream systems** / **Integration method** / **Systems mentioned** (from `integration_targets` in `config/bootcamp_preferences.yaml`, captured in Phase 2 Step 10a — INV-097)
```

`[One sentence]`, `[Measurable outcome 1..3]`, the `Integration Requirements` line — each instructs
the guide to *summarize*. Nothing instructs it to *quote*, and no section exists to quote into. The
answers reach the file only through the refinement, so once Step 11 runs the original phrasing is
gone from the project entirely.

**The gate that is supposed to catch a bad refinement cannot see one.**
`phase2-document-confirm.md:258-262`:

```text
## 15. Get confirmation

👉 **Does this accurately capture your problem and approach?**
```

The Bootcamper is shown the refined document and asked to approve it. With the original wording
visible nowhere, the check is *"does this plausible-sounding text sound right?"* rather than *"does
this match what I said?"* — and a single substituted adjective inside an otherwise-accurate sentence
survives it. It did: this document was confirmed as accurate at the time, and the substitution went
through anyway.

⚠️ **This is why the fix is a correctness measure, not an archival nicety.** A gate that cannot show
both versions cannot reliably catch a one-word change, and `docs/business_problem.md` is the durable
input every later module reads — Module 7 derives requirements from it directly, and graduation
carries it into the production project and renders it as a keepsake PDF.

## Proposed change

**1. Add verbatim capture to the Step 11 template.** For each interview answer that becomes prose,
record the Bootcamper's own words alongside the refined text. A `> "…"` blockquote directly beneath
the refined statement is enough, and keeps the two adjacent where a reader compares them without
scrolling. The refined version stays the working text — every downstream consumer keeps reading what
it reads today.

Apply it to the sections that carry *interpreted* answers, not to the mechanical ones: Problem
Description, Success Criteria, Desired Output, Integration Requirements, Notes. `Use Case Category`,
`Deployment Target` and `Entity Types` are selections from fixed vocabularies with nothing to
preserve.

⚠️ **Where an answer was a selection rather than prose, omit the quote rather than manufacturing
one.** This is the same rule the acknowledge clause already applies to bare option numbers
(`ground-rules.md:145`), and an invented "verbatim" line is worse than none.

**2. Make Step 15's gate show both.** The confirmation question is unchanged and stays pinned
verbatim (INV-056) — what changes is what precedes it: the Bootcamper reviews a document in which
their own wording sits beside each refinement, so the comparison the gate asks for is one they can
actually perform. State plainly that the quoted lines are theirs and the prose is the guide's
rendering, and that a mismatch is what the question is for.

**3. State the rule that generalizes it.** Where the guide refines a Bootcamper's answer into a
durable artifact, the original is preserved beside the refinement. Refinement is not transcription,
and a document that keeps only the refinement cannot be checked against what was meant.

⚠️ **Scope this to `docs/business_problem.md` and its confirmation gate.** Do not retrofit verbatim
capture into every module's write-ups in this spec — the business problem statement is the one
artifact that is (a) built entirely from interview prose and (b) read as an input by later modules.
Widening it is a separate decision with its own cost in document length.

## Acceptance criteria

- [ ] The Step 11 template in `phase2-document-confirm.md` carries a verbatim-quote slot for the
      interpreted sections (Problem Description, Success Criteria, Desired Output, Integration
      Requirements, Notes), with the refined prose retained as the working text.
- [ ] The template states that a section whose answer was a fixed-vocabulary selection gets no quote
      rather than an invented one.
- [ ] Step 15 presents the document with both versions visible and states that the quoted lines are
      the Bootcamper's own words; the pinned question wording is unchanged (INV-056).
- [ ] `docs/business_problem.md` remains self-contained and readable as a deliverable — the added
      quotes must not break the graduation PDF render (`generate_recap_pdf.py` / the Step 5b
      document render) or the production-project copy.
- [ ] Downstream consumers that read the document — Module 7 step 1's requirement derivation,
      graduation's production project — continue to read the **refined** text, not the quotes.
- [ ] A test asserts the template carries the verbatim slot and that Step 15 references it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — Step 11
  template gains verbatim slots; Step 15 shows both versions
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  step 1's derivation reads the refined text; state which of the two it consumes so the added quotes
  cannot be mistaken for requirements input
- `specs/INVARIANTS.md` — register the preserve-the-original-beside-the-refinement rule
- `tests/` — a guard asserting the template and gate carry it

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: business_problem.md records only
  the refined phrasing, losing the bootcamper's exact words" (2026-08-25, Module: Discover the
  Business Problem; `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). The defect is in the plugin's own document template and
  confirmation gate; no SDK method, attribute, flag, response shape or server behavior is asserted.
  Verified in the shipped files on 2026-08-25.
- Upstream: not applicable.
- Related specs: `specs/verbatim-check-cannot-see-field-name-derived-values.md` (a different
  "verbatim" — the mapping-layer value check, unrelated mechanism),
  `specs/capture-reversed-decisions-during-the-run.md`,
  `specs/relocate-integration-deployment-questions-to-module1.md` (Step 10a, where the misrendered
  answer was collected)
