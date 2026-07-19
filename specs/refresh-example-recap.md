# Refresh the shipped example recap to match the current bootcamp

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The canonical example recap shipped with the plugin —
`plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` and its rendered
`bootcamp_recap.example.pdf` — is a pre-rework artifact on **every** axis, yet it is the
document bootcampers are pointed at as the model of their trophy
(`skills/bootcamp-onboarding/onboarding-flow.md:95`, `skills/graduation/SKILL.md:76`). It now
advertises a format and flow the plugin no longer produces:

1. **Legacy numbered headers** — every section is `## Module N: …` (`:10,65,107,147,182,217,260`),
   but the current convention is name-based `## {Module name} — {ISO 8601 timestamp}` (INV-085).
2. **Retired Truth-Set-based Module 3** — the Module 3 section (`:107-143`) narrates System
   Verification as acquiring/loading/visualizing the Senzing Truth Set with the old 10-check set
   (`truthset_acquisition`, `web_service`, `web_page`, "Downloaded the 159-record TruthSet",
   `PurgeTruthSet.java`). System Verification now verifies with **synthetic** `VERIFY` records
   (8 checks, no Truth Set) — INV-082.
3. **Module set no longer matches the catalog** — labeled "Core / 7 of 7", but a Core run now
   experiences **Entity Resolution Concepts** and a standalone **Truth Set visualization** as
   distinct recap sections (`skills/graduation/SKILL.md:88-91`). The example has neither and
   collapses System Verification + Truth Set into one old section.
4. **No screenshots** — the recap trophy now embeds curated visualization screenshots
   (`skills/bootcamp-onboarding/module-completion.md` → "Capturing visualization screenshots");
   the example demonstrates none.
5. **Dates, not ISO 8601 timestamps** in the headers (`— 2026-07-16`).

## Root cause

The file is dated 2026-07-17, predating INV-082 and INV-085 (both 2026-07-19). It was not
refreshed when Module 3 was reworked to synthetic-data verification, when recap headers became
name-based, or when the screenshot feature landed. INV-065's *letter* is still met (it ships, the
PDF regenerates, no PII), but its purpose as a **coherent reference** (INV-003/INV-004) is broken.

## Proposed change

Regenerate `docs/examples/bootcamp_recap.example.md` so it models a current **Core** graduation,
then re-render `bootcamp_recap.example.pdf` from it via `scripts/generate_recap_pdf.py` (INV-065
requires the PDF stay regenerable from the `.md`):

- **Name-based headers** `## {Module name} — {ISO 8601 timestamp}` for every section (INV-085).
- **Sections matching the current Core catalog** in experienced order: Entity Resolution Concepts
  (if represented), Business problem, SDK setup, **System verification** (synthetic `VERIFY`
  records, ~8 checks, register-before-load, no Truth Set download/purge framing), **Truth Set
  visualization** (its own section — the Truth Set web app), Data collection, Data quality &
  mapping, Data processing, Query/Visualize/Discover. Each carries the four labeled subsections.
- **Rewrite the System Verification section** to synthetic-data verification (INV-082/083); move
  all Truth Set narrative into the separate Truth Set visualization section.
- **Embed 1–2 screenshots** (`![caption](docs/visualizations/…png)`) in a visualization section to
  demonstrate the feature; keep them non-PII.
- Keep all data **synthetic / non-PII** (INV-065).
- Re-render the committed `.example.pdf`; `--check` must pass and the PDF must render (fpdf2 and
  stdlib fallback).

## Acceptance criteria

- [ ] `bootcamp_recap.example.md` uses name-based `## {Name} — {ISO 8601 timestamp}` headers throughout (no `## Module N:`).
- [ ] Its Module-3/verification content describes synthetic-record verification (no Truth Set acquisition/download/purge in System Verification); the Truth Set appears only in a separate Truth Set visualization section.
- [ ] Its section set matches a current Core graduation (`modules_completed`), including a standalone Truth Set visualization section.
- [ ] At least one embedded screenshot is present; no real PII anywhere.
- [ ] `generate_recap_pdf.py --check` passes on it, and `bootcamp_recap.example.pdf` is re-rendered from it (INV-065 regenerable).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` — full refresh.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf` — re-render from the `.md`.

## Source

- Audit (deep-dive conformance/coherence review), 2026-07-19 — finding #1 (MAJOR).
- Priority: High.
- Related specs: `module3-synthetic-verification-data.md` (INV-082/083), `recap-sections-name-based-and-complete.md` (INV-085), `capture-visualization-screenshots-for-recap.md`, `example-recap-reference.md` (INV-065 — this refreshes that shipped asset).
