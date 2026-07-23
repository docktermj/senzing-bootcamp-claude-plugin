# Open Graduation with the full module preface

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Graduation opens with only the GRADUATION banner followed immediately by the model/effort switch
prompt, then jumps into pre-checks/Step 1. Every content module opens with a consistent preface —
banner, journey map, before/after framing, a "what we'll do" step overview, and an estimated
time — but graduation skips all of it. The abrupt jump from banner straight to the model/effort
prompt breaks the rhythm the bootcamper has come to expect from every module, including the final
one.

## Root cause

Graduation is **explicitly self-declared** exempt from the per-module apparatus in its own skill:

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md:31-37` — "Graduation is a terminal bookend
  module, not a content module: it presents the GRADUATION banner and the model/effort nudge, but
  is exempt from the per-module apparatus (INV-029–032) — no journey map, before/after framing,
  step overview, or `✅ Module complete` line — since no next-module transition applies."
- Opening flow: banner (`SKILL.md:44-48`) then the model/effort prompt (`SKILL.md:50-61`, CLI form
  at `:56`), then pre-checks/Step 1. No journey map, before/after, step overview, or estimated
  time is present. Contrast a content module, e.g. `module-04-data-collection/SKILL.md:22`, which
  requires the journey map, before/after framing, numbered overview, and model/effort nudge.

**Invariant status (reconcile, don't silently override).** The exemption is a *skill-level design
choice*, not an invariant guarantee. No invariant grants graduation an apparatus exemption — the
only apparatus exemptions on record are Bootcamp preparation (INV-075) and Module 0 (INV-078), and
INV-096 (estimated time) is scoped to "numbered content modules," explicitly excluding only prep
and Module 0. INV-029–032 speak of "each module." So adding the preface to graduation aligns it
with INV-029–032 and does **not** violate any invariant; the change is to graduation's own
exemption note (`SKILL.md:31-37`), which the bootcamper explicitly disagrees with. Two clauses do
need adapting to graduation's terminal nature (below), and estimated-time for graduation is an
extension beyond INV-096's "numbered content module" scope that should be recorded if adopted.

## Proposed change

At graduation start, present the same preface content used by content modules, adapted to a
terminal module, **before** the model/effort prompt:

- **Journey map** — show all completed modules ✅ and graduation as the current/final stage, with
  no upcoming modules after it.
- **Before/after framing** — before: all modules done, entities resolved; after: a populated
  `production/` project and the `docs/bootcamp_recap.pdf` keepsake.
- **Step overview** — enumerate what graduation does (recap PDF, populate `production/`,
  revisit/resume bundle per INV-094, terminal banner).
- **Estimated time** — an honest, range-based estimate caveated per INV-096's style (varies with
  workstation, PDF render, backup size), or "hard to estimate" if none is meaningful.
- **What's next (INV-032 adaptation)** — since no next module applies, frame "what's next" as life
  after the bootcamp / the END OF SENZING BOOTCAMP close (INV-057), not a next-module transition.

Keep the model/effort prompt and its confirmation gate (INV-063/INV-069) after the preface, and
keep the terminal END OF SENZING BOOTCAMP banner as the final output (INV-057). Update the
exemption note at `SKILL.md:31-37` to reflect the preface now being shown. Honor verbosity
(suppress/shorten under `minimal`/`concise`, INV-011/INV-012).

## Acceptance criteria

- [ ] Graduation opens with the GRADUATION banner, then a journey map (all modules complete, graduation current), before/after framing, a step overview, and an estimated time — then the model/effort prompt.
- [ ] The "what's next" framing is adapted to graduation being terminal (no next-module transition), and the run still ends on the single END OF SENZING BOOTCAMP banner (INV-057).
- [ ] The model/effort switch offer and confirmation gate are unchanged in wording and ordering (INV-063/INV-069/INV-098).
- [ ] The preface content respects the active verbosity preset (INV-011/INV-012).
- [ ] `graduation/SKILL.md:31-37`'s exemption note is updated to match; if estimated-time-for-graduation is adopted, the extension beyond INV-096's "numbered content module" scope is recorded in `INVARIANTS.md`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — add the preface before the model/effort prompt and update the exemption note (`:31-37`, `:44-61`).
- `specs/INVARIANTS.md` — only if estimated-time-for-graduation is adopted as an extension of INV-096.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Graduation should open with the full module preface" (2026-07-23, Module: Graduation)
- Priority: Medium
- Related specs: `module-preface-time-estimate.md` (INV-096 estimated-time apparatus, scoped to numbered content modules), `module-start-model-nudge.md`/`model-effort-change-prompt.md` (INV-063 nudge preserved), `end-of-bootcamp-banner.md` (INV-057 terminal banner preserved), `graduation-revisit-resume-bundle.md` (INV-094 step in the overview).

## Invariants introduced

- `INV-102` — Graduation runs the module-start apparatus adapted to a terminal module (journey map, before/after framing, step overview, estimated time) after the GRADUATION banner and before the model/effort prompt; it stays terminal (no next-module transition, no `✅ Module complete` line, ends on the END OF SENZING BOOTCAMP banner) and is no longer apparatus-exempt. Applies INV-029–032 and extends INV-096 to graduation (recorded in `specs/INVARIANTS.md`, maintainer-approved).
