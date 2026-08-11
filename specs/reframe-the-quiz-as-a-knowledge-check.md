# The optional quiz is worded as a test, which is what makes people decline it

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Module 0's optional assessment is framed as an examination throughout
`module-00-entity-resolution-concepts/concepts.md`:

- `:113` — section heading "Optional knowledge-check **quiz** (offer before the readiness gate)"
- `:115` — "offer an optional short **quiz**"
- `:127` — the pinned question: **"👉 Would you like to test your knowledge of entity resolution with
  a short quiz?"**

A bootcamper reported that words like "quiz", "test" and "evaluation" *"can cause people to recoil"*,
and asked for the offer to be framed as something that improves their learning rather than as an
assessment of it.

The framing works against the module's own stated intent. `:116` says the exercise "reinforces the
concepts and drives curiosity" — that is the pitch, and the bootcamper never sees it; what they see
is an offer to be tested. The gap is between what the module says the exercise is *for* and how it
asks.

**This is not a low-stakes wording nit, because the offer is guaranteed.** INV-112 requires the
pinned question to be presented verbatim on **every run** — "optional" describes the bootcamper's
*answer*, never whether the question is asked — and requires `quiz_offered` to be asserted before the
module closes. So every bootcamper who runs Module 0 meets this exact sentence, once, at a point
where they have just met the material and have no evidence they have absorbed it. A decline here
costs the plugin its only comprehension signal for the primer.

## Root cause

The wording predates the framing at `:116`. "Quiz" was a working label for the mechanism, and the
pinned question was written from the mechanism rather than from the benefit — the same shape as
naming a feature after its implementation. Nothing since has revisited it, because it is not wrong,
merely off-putting, and no test or invariant governs tone.

## Proposed change

1. **Rename the exercise** in `concepts.md`'s heading and prose to a learning frame — "knowledge
   check" or "Q&A" — dropping "quiz". The heading already contains "knowledge-check", so this is
   mostly deleting the word that undercuts it.
2. **Rewrite the pinned question to offer a benefit rather than an assessment**, keeping it a single
   unambiguous yes/no (INV-008) with no "or" (INV-009/INV-051), e.g. *"👉 Would you like a few quick
   questions to help the concepts stick?"* — the exact wording is the maintainer's call; what matters
   is that it names the gain, not the measurement.
3. **Update the pinned question everywhere it is pinned.** INV-056 requires the wording be fixed in
   the skill file, so the change must land in the one authoritative place and nowhere else — and the
   shipped example recap (`docs/examples/bootcamp_recap.example.md:32`, `:52`) quotes the old
   wording, so it needs regenerating to stay reproducible (INV-065).
4. **Change nothing about the mechanism.** The questions, their difficulty, sourcing, and the
   wrong-answer handling settled by `dry-run-phase3-interaction-prose-defects` all stand. This is
   framing only.

⚠️ **Do not soften it into ambiguity.** "Would you like to explore the concepts further?" is friendly
and unanswerable — the bootcamper cannot tell what they are agreeing to. INV-008 requires the
yes/no to be unambiguous, and a vague offer is a worse defect than a blunt one.

⚠️ **Do not make it conditional or two-branch.** INV-112 requires the same pinned question every run;
adapting the wording to how the bootcamper seems to be doing would break the pin and the test that
enforces it.

## Acceptance criteria

- [ ] `concepts.md` no longer frames the exercise as a quiz or a test in its heading, its prose, or
      the pinned question.
- [ ] The pinned question offers a learning benefit, is a single unambiguous yes/no (INV-008), and
      contains no "or" (INV-009/INV-051).
- [ ] The wording is pinned verbatim in exactly one authoritative place (INV-056), and INV-112's
      every-run guarantee plus the `quiz_offered` / `quiz_taken` progress keys are unchanged — the
      keys are internal state, not bootcamper-facing text, and renaming them is out of scope.
- [ ] `docs/examples/bootcamp_recap.example.md` is regenerated so the shipped example quotes the
      current question, and its PDF remains reproducible from it (INV-065) — checked by **opening
      that file** (INV-182).
- [ ] Any test asserting the old wording is repointed to the requirement rather than the phrase, with
      a docstring saying what changed and when (INV-181).
- [ ] The quiz mechanism — question count, difficulty, sourcing, wrong-answer handling — is unchanged.
- [ ] **Not runtime-verified:** whether the new framing actually reduces declines is a conversational
      outcome only `dry-run` phase 3 could begin to observe, and one run would not establish it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — `:113`,
  `:115-116`, `:127`.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and its `.pdf` — the quoted
  question at `:32` and the summary line at `:52`.
- `tests/` — any assertion pinning the old phrase.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Rebrand the optional \"quiz\" as a \"Q&A\" or
  \"knowledge check\"" (2026-07-27, Module: Entity Resolution Concepts; Priority: not specified — the
  bootcamper moved to the next module before being asked; `Source: bootcamper-reported`).
- Priority: **Low.** Nothing is broken and no artifact is wrong. It is worth doing because the
  question is guaranteed to every bootcamper by INV-112, so a small deterrent applies universally.
- MCP re-check: **n/a (no Senzing fact), server 1.32.3, 2026-07-31.** Module wording is entirely
  plugin-side; no MCP tool owns it and none was called.
- Upstream: not applicable.
- Related specs: `specs/guarantee-quiz-offer-is-presented.md` (INV-112 — the every-run guarantee this
  preserves), `specs/concepts-module-verified-qa-and-quiz.md` and
  `specs/concepts-questions-before-quiz.md` (the mechanism and its ordering, both unchanged here),
  `specs/example-recap-reference.md` (INV-065 — why the example must be regenerated).

## Deviations from this spec, and why (2026-08-11)

**1. Criterion 5 was vacuous as written, so it was met a different way.** It asks that "any test
asserting the old wording is repointed to the requirement rather than the phrase". No test asserted
the old pinned wording — grep across `tests/` found only a recap **fixture** string and two
docstring mentions, none of them an assertion on the question. Repointing nothing would have left
the change unguarded, so a `TheKnowledgeCheckOffersABenefitNotAnAssessment` class was added to
`tests/test_phase3_interaction_prose.py` pinning the **requirement** (benefit frame, unambiguous
yes/no, no "or", heading and prose no longer framing an assessment) alongside the current string,
with the INV-181 docstring the criterion asks for. Side effect worth naming: INV-112 — the every-run
guarantee this spec depends on — **was cited by no test in the suite**; it now is.

**2. The example PDF regeneration broke an unrelated test, and the test was fixed, not the source.**
Re-rendering shifted pagination enough to push the licence-measurement line onto a page boundary.
`test_example_recap_sync.test_source_lines_appear_in_the_pdf` compares a 50-character window of each
source line, and the page-number footer landed inside it — `…assuming it 23 recordLimit: 0…` — so a
line that is genuinely in the PDF read as missing. That module's own `sampled_lines` docstring
already describes this hazard for `_NEW_LINE_LABELS`; it reaches ordinary prose too, and which line
it hits depends only on where pagination falls, so any edit anywhere can move it. Added
`pdf_text_without_page_footers`, which drops digit-only `Tj` fragments, and the test now accepts a
match in either haystack. Verified by mutation that staleness is still caught: adding a sentence to
the source without re-rendering still fails the test. (INV-181 — correct the assertion's model of
the artifact, not the artifact.)

**3. Scope beyond the Affected files list.** The spec named `concepts.md`, the example recap and
`tests/`. Three more files carried the same vocabulary and would have left two copies of one word
disagreeing: `module-00-entity-resolution-concepts/SKILL.md` (8 references, including the recap
subsection instructions), `docs/model-selection.md` (the Module 0 row), and the recap fixture in
`tests/test_recap_pdf_guard.py`.

**4. One "quiz" deliberately survives** in `concepts.md`, in the new rule that names "quiz", "test"
and "evaluation" as the words to avoid. That is a mention, not a use, and the test that forbids the
others exempts exactly that line.

**5. Cosmetic re-wrapping.** "Knowledge check" is longer than "quiz", so several lines exceeded the
file's ~100-column style; they were re-wrapped. Two lines over that width in `SKILL.md` (the
frontmatter `description` and line 27) pre-date this change and were left alone.

## Invariants introduced

- None. Confirmed with the maintainer on 2026-08-11: INV-056 already pins the wording in one
  authoritative place and INV-112 already guarantees the question is asked every run, so the
  framing change adds no standing rule. It is guarded by
  `tests/test_phase3_interaction_prose.py::TheKnowledgeCheckOffersABenefitNotAnAssessment` and by
  the reason note recorded beside the wording in `concepts.md`.
