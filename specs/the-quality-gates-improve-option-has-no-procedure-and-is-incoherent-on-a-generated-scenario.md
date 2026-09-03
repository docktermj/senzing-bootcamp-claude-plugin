# The quality gate's "improve the data first" option has no procedure behind it, and on a bootcamp-generated scenario it asks the Bootcamper to undo the previous module's required work

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Both quality gates in Data Quality, Mapping, and Transformation offer an "improve the data first"
option, and **no step in the plugin defines what the guide does when it is chosen.** The turn ends
on the question; there is no procedure, no loop-back, no re-score, and no re-entry point.

`module-05-data-quality-mapping/phase1-quality-assessment.md:774-787`:

> 👉 **Your data quality is acceptable but has some gaps. What would you like to do? Reply with a number:**
>
> 1. Improve the weakest fields first.
> 2. Continue to mapping now.

and, for the `<70` band:

> 1. Work on improving the data first.
> 2. Proceed anyway, knowing the results may be limited.

After those two blocks the file continues to *"Success indicator"* and *"Checkpoint: write step 7"*
and Phase 1 ends. `phase2-data-mapping.md` has no mention of `improve`, of a quality choice, or of
re-entry. Grepping the whole module directory for the option's own wording returns the gate itself
and nothing else.

Hit on this walk (2026-08-28): CRM_EXPORT scored **75.1** (the 70-79 band), the gate was presented
as pinned, the Bootcamper chose **1**, and there was nothing to execute.

## Root cause

Two distinct gaps, and the second is the one that makes this more than a missing paragraph.

**1. The option is undefined.** The `<70` branch's *prose* at `:612-615` gets closest — *"Help the
user identify the biggest quality issues and create a remediation plan"* — but that is guidance for
what to say when presenting the band, not a step the guide executes on a selection, and the 70-79
branch has no counterpart at all. Neither says what "improved" data means operationally, where the
improved file goes, whether the source is re-scored, or how the Bootcamper returns to the gate. So
the guide must improvise the entire path — which is what the pinned-wording discipline (INV-056) and
INV-247's "every 👉 question traces to a step in a shipped skill file" exist to prevent on the *ask*
side, left unguarded on the *answer* side.

**2. On a generated scenario the option is incoherent, because the gaps are deliberate.** This is
the common path, not an edge case. `module-04-data-collection/SKILL.md` Step 2 **requires** the
generator to manufacture exactly these gaps (INV-239):

> ⛔ **Generate realistic quality gaps too, not only structural complexity (INV-239).** […] the
> generated data must also carry: **missing values in non-key fields**, enough to put **at least one
> source in the 70-79% band**. […] That band opens the remediation conversation, so it has to be
> reachable.

So Module 4 is instructed to synthesize a source into the 70-79 band **specifically so this gate
fires**, and then this gate offers to remove the gaps that put it there. Choosing "improve" on a
synthesized source means regenerating the data the bootcamp authored minutes earlier to be
imperfect — undoing the previous module's required work, and making the quality step vacuous in
exactly the way INV-239 exists to prevent. The Bootcamper cannot know any of this: from where they
sit, "improve the weakest fields first" is an ordinary and sensible choice.

⚠️ **The two gaps compound.** Because the option is undefined, a guide facing it improvises; because
the data is synthetic, the most natural improvisation — regenerate with smaller gaps — is the one
that defeats the module. Nothing in either file warns against it.

## Proposed change

1. **Define the improve path, for both bands.** State what the guide does on the "improve" selection:
   which fields it names (the score already identifies the worst — this walk reported `phone` missing
   60%, `address` 44%, `dob` 34%), what the Bootcamper is asked to supply or change, where an improved
   file is written, and that the source is **re-scored and the gate re-presented** with the new figure.
   ⛔ Re-presenting the gate after a re-score is not an INV-006 breach — the score changed, so it is a
   new question about a new state — and saying so explicitly is what stops a guide suppressing it.
2. **Branch the option on provenance, exactly as Module 4's Step 2 branches on it.** For a
   `provenance: synthesized` source, the honest answer is that the gaps are deliberate. Either:
   - **Suppress the improve option** on a synthesized source and state why in one line — the gaps
     were generated so the quality assessment has something to find, so improving them would remove
     the teaching; or
   - **Keep it and disclose** — say plainly that this data is bootcamp-generated and its gaps are
     intentional, so "improving" means regenerating, and let the Bootcamper choose informed.

   The disclosure has to precede the 👉 either way (ground rules: anything meant to inform the answer
   goes before the question).
   ⛔ **Whichever is chosen, do not silently regenerate.** Rewriting the Bootcamper's data as the
   answer to a question they were not told meant that is the failure this spec is filed to prevent.
3. **Decide whether the option should exist on a real-data source at all**, or whether it should
   instead route out of the module (collect better data / go back to Data collection) rather than
   implying an in-module editing loop the bootcamp does not otherwise have. This is a design call for
   the maintainer, not something to settle in implementation.

## Acceptance criteria

- [ ] Selecting the "improve" option in either band leads to a defined, executable path — named
      fields, a stated action, a written artifact, a re-score, and a re-presented gate — rather than
      ending the turn with nothing to run.
- [ ] The improve path is provenance-aware: on a `provenance: synthesized` source the guide either
      suppresses the option with a one-line reason or discloses that the gaps are deliberate
      **before** the 👉, per the maintainer's decision on item 3.
- [ ] Re-presenting the gate after a re-score is explicitly sanctioned in the file, so it is not
      suppressed as an INV-006 repeat.
- [ ] A repo-level test asserts every option offered by a pinned gate in this module has a
      corresponding handling step in the same or a named downstream file (stdlib only, no `plugins/`
      import — INV-108), negative-controlled by deleting the new improve-path section.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  the two gate branches (`:770-790`) and a new improve-path section
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — optionally cross-reference
  from the INV-239 generation block, so the two ends of the contradiction cite each other (INV-183)
- `tests/` — a guard that every pinned gate option has a handling step

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-28, in the analysis stretch, on the first
  phase-3 walk to reach Data Quality, Mapping, and Transformation with a real generated dataset
  (`Source: self-observed (assistant retrospective)`). Surfaced by the maintainer answering **1** to
  a gate the walk had just presented as pinned, on a source the walk's own previous module had been
  required to degrade into that exact band.
- Priority: **Medium.** It does not corrupt data or block the bootcamp — "continue to mapping" is
  always available and is the path most Bootcampers take. It is Medium rather than Low because it is
  a **dead end in a pinned gate**: the plugin asks a question in its own prescribed wording and then
  has no answer for half of it, which is the unsatisfiable-instruction shape that teaches a guide to
  read the surrounding ⛔ rules as advisory. The provenance incoherence raises it further — the
  bootcamp is offering to undo work another module's invariant required.
- MCP re-check: **n/a (no Senzing fact).** The defect is a missing branch in the plugin's own gate
  logic. `get_capabilities` was called at the start of this run to date it: server **1.33.0**,
  2026-08-28. The Entity Specification retrieval that precedes this step was verified live in the
  same session (73,051 bytes, matching the recorded `size_bytes`).
- Upstream: not applicable — plugin-side only.

## Invariants introduced

- `INV-284` — Every option a pinned gate offers MUST have a handling step (a section in the same
  skill file, or an inline branch at the gate) saying what the guide does when it is chosen and
  where the flow resumes; and where that step changes the state the gate measured, re-presenting the
  gate is NOT an INV-006 repeat (recorded in `specs/INVARIANTS.md`, 2026-08-31, on the maintainer's
  sign-off).

## Deviations from this spec, and why (2026-08-31)

- **Item 3 (the maintainer's design call) resolved to "split by what is fixable".** The quality
  score's three dimensions are not equally repairable: `format_consistency` (0.25) and
  `duplicate_rate` (0.05) are mechanical and the guide performs them; `completeness` (0.70) cannot be
  fixed here, because **a missing value cannot be invented** and offering to fill one is offering to
  fabricate data — so that half routes back to Data collection for a better export. This was chosen
  over a pure in-module editing loop (which implies the Bootcamper can supply missing values on the
  spot) and over routing out entirely (which sends away a Bootcamper whose problem is format drift in
  data they already have).
- **Item 2 resolved to "disclose, then keep the option".** On a `provenance: synthesized` source the
  disclosure precedes the 👉 and says the gaps were generated deliberately so the assessment would
  have something to find, and that improving them means regenerating data the bootcamp just authored.
  Both pinned questions are unchanged, byte for byte (INV-056), and the alternative — suppressing the
  option — was declined because it would have required a second pinned form of the gate and would
  take the remediation conversation away from the very source Module 4 was required to build to host
  it.
- ⛔ **The spec named two gates; the scan found six options across three files (INV-246).** Module 5
  Phase 2 offers three more remediation options and Phase 3 a fourth, none of them mentioned in the
  finding. All four were **already discharged** — Phase 2 by `### 17. Iterate`, Phase 3 by an inline
  `**If rejected:** … return to Phase 2 to adjust their mapping` branch — so nothing needed fixing
  there, but the guard covers them, and finding that a handling step ships in **two different
  shapes** is what stopped the guard from requiring a heading and reporting Phase 3's correct prose
  as a defect.
- ⚠️ **The guard's first two versions reported correct prose, both caught by running it.** Matching
  any occurrence of "improve" made *"Iterate to improve the data"* demand an `improve` section when
  its action is *iterate* — already handled — so matching moved to the option's **leading verb**.
  Matching any numbered line then flagged an instruction step in `SKILL.md` (on the word "fix") and
  one of the improve path's own numbered steps, so option extraction is now scoped to lists that
  follow a 👉. Both are recorded because a guard that flags correct text is the one that gets
  relaxed away.
