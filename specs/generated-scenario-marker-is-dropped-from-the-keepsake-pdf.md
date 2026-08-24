# The generated-scenario marker is dropped from the keepsake PDF

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Every bootcamp-generated scenario ends graduation with a dropped-character warning it cannot act on.

Module 1 Step 11 requires the marker `> 🤖 Bootcamp-generated business case` on its own line
directly below the title of `docs/business_problem.md`
(`module-01-business-problem/phase2-document-confirm.md:169-171`). Graduation Step 5b then renders
that same file as a keepsake PDF (`graduation/SKILL.md:937-945`). The PDF is set in Latin-1 core
fonts, so U+1F916 ROBOT FACE cannot be rendered and is dropped, and the generator reports it:

    WARNING: 1 distinct character(s) in 1 passage(s) cannot be rendered by this PDF's built-in
    fonts and were dropped from the page: ROBOT FACE. First affected passage:
    "> \U0001f916 Bootcamp-generated business case".

Observed on a phase-3 walk, 2026-08-22, rendering with `generate_document_pdf.py` (fpdf2, content
retained 99%).

Two things make this worth fixing rather than tolerating:

1. **It fires on every Core run that accepts the Business Case Offer** — the most common path
   through Module 1 — so it is a guaranteed warning, not an edge case.
2. **Neither remedy the warning offers applies.** Its guidance branches on "if it NAMES an entity"
   (use the verified Latin-script name) and "if the dropped text IS the subject" (keep it and add an
   ASCII description). The marker is neither: it is a machine-readable flag the plugin itself
   mandates, whose loss from the PDF costs nothing. A guide following the warning literally has no
   correct action, which is the shape that teaches warnings are ignorable.

## Root cause

Two correct requirements meeting at a renderer neither of them knows about: the marker must be an
emoji-bearing line in the Markdown (several steps branch on it — Module 4 Step 2, Module 6 Phase C
step 13, Module 7 step 25a), and Step 5b renders that Markdown unmodified.

The marker's *purpose* is served entirely by the Markdown file. Nothing reads it from the PDF.

## Proposed change

Give Step 5b a one-line instruction: when rendering `docs/business_problem.md`, the
`> 🤖 Bootcamp-generated business case` marker's ROBOT FACE is expected to be dropped and needs no
action — the marker is a machine-readable signal in the Markdown, and its loss from the PDF is
harmless. Say so where the warning will be met, so the guide does not go looking for a fix.

Optionally, teach `generate_document_pdf.py` to recognize this exact marker line and omit it from
the warning tally (not from the page) — but the documentation fix is the one that matters, and the
suppression must not extend to any other dropped character.

⛔ Do **not** solve it by removing the emoji from the marker: several modules branch on that exact
string, and changing it is a rename across four files with a silent-mismatch failure mode.

## Acceptance criteria

- [ ] `graduation/SKILL.md` Step 5b states that the generated-scenario marker's dropped ROBOT FACE
      is expected and requires no action.
- [ ] The marker string itself is unchanged in `module-01-business-problem/phase2-document-confirm.md`
      and in every step that reads it.
- [ ] If the generator is changed, a test asserts that only this exact marker line is exempt and that
      any other unrenderable character still warns.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 5b note.
- `plugins/senzing-bootcamp/scripts/generate_document_pdf.py` — optional, targeted exemption.
- `tests/` — guard for the exemption if implemented.

## Source

- Feedback: `/dry-run` phase 3, graduation Step 5b (2026-08-22;
  `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact — a font-coverage limitation of the bundled renderer)
- Upstream: not applicable
- Related specs: none
