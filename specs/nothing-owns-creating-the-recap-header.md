# Nothing owns creating the recap header

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

On a Core run, no module is instructed to create `docs/bootcamp_recap.md`'s
preamble header, and the one file that says who created it names a module that is
exempt from writing it at all. The recap can therefore reach graduation with no
`**Bootcamper:**`, `**Started:**`, `**Programming language:**`, `**Path:**` or
`**Plugin version:**` lines.

The failure is not silent, but it is late and it lands on the keepsake. The
generator warns and prints a placeholder on the signed certificate:

```text
WARNING: no bootcamper name found in docs/bootcamp_recap.md or
config/bootcamp_preferences.yaml; the Certificate of Completion will read
"<placeholder>". Add a "**Bootcamper:** <name>" line to the recap preamble to fix it.
```

Graduation also inserts the completion date "directly under the `**Started:**`
line" (`graduation/SKILL.md:372`) and expects `**Plugin version:**` to "already be"
present (`:382`) — both anchored to a header nobody wrote.

## Root cause

Two mutually reinforcing gaps, one root cause: header creation is unowned, and
each of the two files that mention it assumes the other did it.

1. **`plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md:86-87`**
   routes recap capture to "`../bootcamp-onboarding/module-completion.md` Step 2
   (**2b/2c**)". Step **2a** — "Create the recap on first module completion …
   If `docs/bootcamp_recap.md` does not exist, create `docs/` and write this
   header" (`module-completion.md:32-49`) — is the substep that applies, and it is
   the one omitted. In a Core run Module 0 is the **first** module to append a
   recap section, because Bootcamp preparation is recap-exempt, so Module 0 is
   exactly the module that hits the does-not-exist case. Following its own SKILL
   literally appends a `## Entity Resolution Concepts — …` section to a file with
   no preamble. Step **2d** (finalize the in-progress checkpoint) is omitted from
   the same citation.

2. **`plugins/senzing-bootcamp/skills/graduation/SKILL.md:218-219`** states the
   `**Bootcamper:**` preamble line is one "which **Bootcamp preparation wrote at
   the start of the run** from the auto-detected value". Bootcamp preparation
   writes no recap: it is apparatus-exempt and says so twice —
   `bootcamp-preparation/SKILL.md:27` and `:367` ("NOT written as a
   `docs/bootcamp_recap.md` section (INV-092)"). Its only writes are
   `config/bootcamp_preferences.yaml` and `config/bootcamp_progress.json`
   (`:322-360`). So graduation's instruction to amend that line describes editing
   something that may not exist, and its explanation of the line's provenance is
   false.

Module 1 is unaffected: `module-01-business-problem/phase2-document-confirm.md:266-267`
points at the whole module-completion process rather than at named substeps, so a
Customized run that drops Module 0 reaches 2a normally. Module 0 is the only module
that narrows the citation.

n/a — no Senzing fact is involved.

## Proposed change

1. `module-00-entity-resolution-concepts/SKILL.md` — change the citation from
   "Step 2 (2b/2c)" to Step 2 in full, and say explicitly that Module 0 is
   normally the **first** module to write the recap in a Core run, so 2a applies
   and creates the header. Keep the existing Step 3 exemption unchanged (Module 0
   still shows no bootcamper-facing end-of-module summary). Add 2d, or say why it
   does not apply.
2. `graduation/SKILL.md:218-219` — correct the provenance: the `**Bootcamper:**`
   line is written by **module-completion Step 2a, at the first module that
   appends a recap section** (Entity Resolution Concepts when selected, otherwise
   Discover the Business Problem), from the `name` detected in Bootcamp
   preparation. Keep the "both, not either" rule and the amend instruction, and
   add that if the preamble line is absent, graduation writes it rather than
   assuming an edit target.
3. Prefer removing the class over patching two sites: a citation that names
   specific substeps is the hazard. Either cite Step 2 whole everywhere, or state
   in `module-completion.md` Step 2a that it is unconditional at any module whose
   append finds no file — so a narrowed citation elsewhere cannot skip it.

## Acceptance criteria

- [ ] After a Core run reaches the end of Entity Resolution Concepts,
      `docs/bootcamp_recap.md` exists and carries all five preamble lines
      (`**Bootcamper:**`, `**Started:**`, `**Programming language:**`, `**Path:**`,
      `**Plugin version:**`) above the first `## ` section.
- [ ] `module-00-entity-resolution-concepts/SKILL.md` no longer cites Step 2 as
      "(2b/2c)", and states that 2a applies to it.
- [ ] `graduation/SKILL.md` no longer attributes the `**Bootcamper:**` line to
      Bootcamp preparation, and handles the line being absent.
- [ ] A test in the repo-level `tests/` asserts that no skill file narrows a
      `module-completion.md` Step 2 citation in a way that omits 2a — or, at
      minimum, that `module-00`'s citation covers the create-the-header case. It is
      negative-controlled by restoring the "(2b/2c)" text and confirming failure.
- [ ] `generate_recap_pdf.py`'s "no bootcamper name found" warning does not fire
      for a recap produced by a walk of Bootcamp preparation → Entity Resolution
      Concepts.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` —
  cite module-completion Step 2 in full; name 2a as applying.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — correct the
  `**Bootcamper:**` line's provenance and handle its absence.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/module-completion.md` —
  state 2a as unconditional at the first append, so a narrowed citation cannot
  skip it.

## Source

- Feedback: dry run phase 3, 2026-08-13 — hit while executing Module 0's
  "Record the recap, then hand off to Module 1" on a Core walk; the recap file did
  not exist and the module's own citation did not cover creating it
  (`Source: self-observed (assistant retrospective)`)
- Priority: High
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: `specs/empty-progress-file-makes-resume-unsatisfiable.md` (both are
  state files whose creation is assumed rather than owned)
