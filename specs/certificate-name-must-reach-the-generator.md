# The certificate name the bootcamper was asked for never reaches the generator

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Graduation's pre-check did everything right: it detected the auto-detected handle `docktermj`,
correctly judged it not certificate-quality, asked the pinned certificate-name question (INV-113), and
persisted the answer as `name` in `config/bootcamp_preferences.yaml` — exactly as the skill instructs.

**The rendered certificate still printed `docktermj`** — the very value the pre-check had rejected —
while exiting 0 with 99% content retention and no warning. Only an artifact probe
(`pdftotext | grep`) caught it.

This is an INV-065 violation reached through a documented, correctly-followed path. Every gate was
green, the bootcamper answered a question whose answer was then discarded, and the wrong name is
permanent and prominent: the certificate prints it largest, and it is the one artifact a bootcamper
shares.

## Root cause

**The pre-check and the generator disagree about where the name lives.**

- Graduation's pre-check writes the answer to preferences:
  `plugins/senzing-bootcamp/skills/graduation/SKILL.md:167` — *"Persist the answer as `name` in
  `config/bootcamp_preferences.yaml` so a re-render or a resumed session uses it."*
- The generator never reads preferences. `generate_recap_pdf.py` takes the certificate name from the
  recap Markdown: `recap_certificate_name()` (`:1418`) and `recap_missing_certificate_name()`
  (`:1403`) read the `**Bootcamper:**` preamble line, and `_cert_fields()` (`:1329`) — the single
  source both renderers use (`:1776`, `:2227`) — prints what that returns.

`docs/bootcamp_recap.md`'s `**Bootcamper:**` line was written by **Bootcamp preparation, at the start
of the run**, from the auto-detected handle. So the recap still carries the pre-detection value, the
pre-check's correction lands in a file the generator does not consult, and the two never meet.

**Why nothing caught it.** The generator's own name warnings (`:2796`, `:2810`) fire only when the
recap has *no* name or an unprintable one — a present-but-rejected name is indistinguishable from a
good one at that layer, because the layer that knows it was rejected is the pre-check, which does not
write where the generator reads. The retention figure cannot see it either: the wrong name *is*
rendered, so no content is missing (INV-110 measures loss, not correctness).

## Proposed change

1. **Make the generator prefer the persisted answer.** Read `name` from
   `config/bootcamp_preferences.yaml` and use it for the certificate when present, falling back to the
   recap's `**Bootcamper:**` line and then to `CERTIFICATE_NAME_PLACEHOLDER`. Preferences is where the
   bootcamper's *answer* lives (INV-113), so it outranks a value written before the question was
   asked. Keep the read tolerant: a missing file, absent key or unreadable YAML degrades to today's
   behavior rather than failing the render (INV-048).
2. **Have the pre-check also update the recap.** Writing preferences alone leaves the recap carrying a
   value the bootcamper rejected, which is wrong on its own terms — the recap is a deliverable a
   reader sees. Update the `**Bootcamper:**` line too. (This is a preamble meta line, not a completed
   module section, so amending it does not violate the recap's append-only rule, INV-085.)
3. **Do both, not either.** Change 1 makes the certificate correct even for an already-written recap
   (a resumed or re-rendered session); change 2 makes the recap itself correct. Either alone leaves one
   artifact wrong.
4. **Make the disagreement detectable.** When the generator finds a name in **both** places and they
   differ, print one stderr line naming both and which it used. A silent divergence is what let this
   ship; INV-111 already requires a generator to say when it chose between paths.

## Acceptance criteria

- [ ] With `name: Dana Reyes` in `config/bootcamp_preferences.yaml` and `**Bootcamper:** docktermj` in
      the recap, the rendered certificate prints **Dana Reyes**.
- [ ] With preferences absent, unreadable, or carrying no `name`, the certificate still renders from
      the recap line exactly as today, and the render never fails on a preferences read (INV-048).
- [ ] After the pre-check asks the INV-113 question, the recap's `**Bootcamper:**` line carries the
      answer too — so a later re-render from the recap alone is also correct.
- [ ] A name present in both sources and differing produces one stderr line naming both values and the
      one used (INV-111).
- [ ] The existing no-name and unprintable-name warnings still fire on their own conditions
      (INV-113/INV-143/INV-159), and the placeholder is still used rather than a blank recipient line.
- [ ] A `pdftotext` probe of the certificate page finds the persisted name and not the rejected handle
      — the check that caught this originally (INV-129).
- [ ] `tests/test_recap_pdf_certificate.py` covers the precedence order and the divergence warning.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      generator is a bundled Python script the flow runs whatever language the bootcamper chose, and
      the YAML read uses no platform-specific paths.

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `recap_certificate_name()` (`:1418`),
  `recap_missing_certificate_name()` (`:1403`) and `_cert_fields()` (`:1329`): consult preferences
  first; `main()` (`:2796`, `:2810`): the divergence warning.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — the pre-check (`:137-167`): also update the
  recap's `**Bootcamper:**` line, and state that the generator prefers preferences.
- `tests/test_recap_pdf_certificate.py` — precedence and divergence coverage.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Certificate name comes from the recap Markdown,
  so the INV-113 fix does not reach it" (2026-07-28, Module Graduation;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin`; `Upstream: n/a (plugin-side)`)
- Priority: High (not stated by the reporter; assessed from impact — an INV-065 violation via a
  correctly-followed path that prints a rejected value, permanently and prominently, at exit 0)
- MCP re-check: n/a (no Senzing fact — the defect is a disagreement between two bundled plugin
  components). Server 1.32.1 was current at triage, 2026-07-28.
- Upstream: not applicable
- Related specs: `specs/certificate-name-fallback-at-graduation.md` (INV-113 — established the
  question this spec makes effective; that spec asked it, this one delivers the answer),
  `specs/certificate-of-completion-from-template.md` (INV-156 — the certificate layout),
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md` (INV-110/INV-111 — why retention could
  not catch this, and the reporting rule the divergence warning follows),
  `specs/artifact-level-verification-for-deliverables.md` (INV-129 — the probe that caught it)

## Invariants introduced

- `INV-170` — A value the Bootcamper was asked for MUST outrank any value auto-detected before the
  question was asked, MUST be persisted everywhere the artifact is generated from, and a generator
  choosing between two sources MUST prefer the answer and report a disagreement on stderr (recorded
  in `specs/INVARIANTS.md`).
