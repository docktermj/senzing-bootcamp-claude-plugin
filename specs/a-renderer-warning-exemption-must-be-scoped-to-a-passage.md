# A renderer-warning exemption must be scoped to a passage, and the rule that shipped is registered nowhere

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`generated-scenario-marker-is-dropped-from-the-keepsake-pdf` (implemented 2026-08-23) added the
plugin's **first exemption from the dropped-character report**, and with it a ⛔ rule in
`graduation/SKILL.md`:

> ⛔ **This exemption is the marker line and nothing else.** The renderer suppresses only the tally
> entry whose passage *is* that line; a ROBOT FACE anywhere else in the document, and every other
> unrenderable character, still warns […]

Its ledger entry records the deferral honestly: *"this ships one hard rule to shipped markdown with
no invariant registered […] The candidate, for their decision."* This spec is that decision, written
down so it does not stay in a ledger summary.

**Why it needs registering rather than leaving as a local note.** The dropped-character report is
the only thing standing between a Bootcamper and silent content loss on the artifact they frame —
INV-143 forbids substituting `?`, INV-159 requires the loss be reported, and the audit history
records a Bootcamper receiving `?? (Li Ming)` at 34 pt with exit 0 and no warning. An exemption
mechanism inside that report is a hole by construction, and the rule keeping it narrow lives in one
module's prose. A second exemption added elsewhere — plausibly for another plugin-mandated emoji
marker — has nothing binding it to the same discipline.

## Root cause

`specs/INVARIANTS.md` has been searched for the subject under *exempt* + *character*/*passage*/
*drop* and under *dropped character*: **no hit.** The invariants that govern the surrounding
behavior each stop short of the exemption:

- **INV-143** — a character the core fonts lack is **dropped**, never encoded as `?`. Governs the
  substitution, not the reporting.
- **INV-159** — the loss is reported rather than silent. Governs that a warning exists, and says
  nothing about a warning being suppressible.
- **INV-113** — the pinned question that asks the one person who knows how a non-Latin name should
  be spelled. Downstream of the warning.
- **INV-048** — non-blocking: the PDF still ships. Why the warning is a warning.

So the ruleset says the loss must be reported and does not constrain what may be exempted from the
report — which is exactly the surface where an exemption widens quietly. The implementation is
correct today (verified: the exemption keys on the **passage**, checks before excerpt truncation,
and leaves the character dropped from the page), and nothing binds the next one.

⛔ **No Senzing fact is in question.** This is a font-coverage property of the bundled renderer and
the plugin's own marker convention, so it needs no MCP call to resolve.

## Proposed change

1. **Register the rule.** Draft wording, carried forward from the deferral in the
   `generated-scenario-marker-is-dropped-from-the-keepsake-pdf` ledger entry and sharpened:

   > **INV-NNN** — An exemption from a generator's dropped-character report MUST be scoped to an
   > **identified passage**, never to a character, and MUST leave the character dropped from the
   > rendered page (INV-143). Every exemption MUST name the exact passage it covers, MUST be
   > evaluated against the full normalized passage **before** any excerpt truncation, and MUST NOT
   > prevent the same character being reported when it appears anywhere else in the document —
   > including when the exempt passage is rendered first. An exemption is admissible only where the
   > dropped text is a **machine-readable marker the plugin itself mandates**, read from the source
   > document and never from the rendered artifact, so that neither remedy branch of the warning
   > applies; ⛔ **an exemption MUST NOT be added because a warning is frequent or inconvenient.**
   > (A guaranteed warning with no correct response is what teaches that warnings are ignorable —
   > which is the reason the first exemption exists, and the reason a second needs the same test.)

2. **Cite it** at `graduation/SKILL.md`'s exemption rule and beside `_EXPECTED_DROP_PASSAGE` in
   `generate_recap_pdf.py`, at the rule (INV-183).

3. ⛔ **Do not loosen the existing implementation to match a simpler invariant.** The
   character-is-still-dropped, checked-before-truncation and does-not-consume-the-collector-slot
   properties are each already asserted by
   `tests/test_generated_scenario_marker_drop_is_exempt.py`, each with a landed negative control.
   The invariant should record what is built, not a weaker version of it.

## Acceptance criteria

- [ ] An invariant governing dropped-character-report exemptions is registered, with the
      maintainer's sign-off on the wording, the next unused ID, and its index entry in the same
      edit.
- [ ] `graduation/SKILL.md`'s exemption rule cites it at the rule, and `generate_recap_pdf.py`'s
      `_EXPECTED_DROP_PASSAGE` block cites it in its comment.
- [ ] `coverage_reports.py shipped` stays clean — the new invariant names a shipped artifact, so it
      must be cited in shipped text, which is the check that caught eight uncited invariants on
      2026-08-14.
- [ ] The existing guard gains one assertion: that the number of exempt passages the generator
      recognizes is the reviewed count, so a second exemption fails until it is argued for —
      negative-controlled by adding a second exempt passage.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — core
      font coverage is a property of the renderer, not the platform.

## Affected files

- `specs/INVARIANTS.md` — the new invariant plus its index entry.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — cite it at the Step 5b exemption rule.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — cite it beside
  `_EXPECTED_DROP_PASSAGE`.
- `tests/test_generated_scenario_marker_drop_is_exempt.py` — the exempt-count assertion.

## Source

- Feedback: none — the deferral was recorded in the
  `generated-scenario-marker-is-dropped-from-the-keepsake-pdf` ledger entry on 2026-08-23 and
  promoted to a spec by `production-readiness-audit` the same day
  (`Source: self-observed (assistant retrospective)`)
- Priority: **Medium.** The implementation is correct and guarded; what is missing is the rule
  binding the *next* exemption. Rated here rather than lower because the surface it guards is the
  one thing preventing silent content loss on a keepsake artifact.
- MCP re-check: n/a (no Senzing fact) — a font-coverage limitation of the bundled renderer and the
  plugin's own marker convention. This spec asserts nothing about the server and no absence.
- Upstream: not applicable
- Related specs: `specs/generated-scenario-marker-is-dropped-from-the-keepsake-pdf.md` (where the
  rule shipped and the deferral was recorded),
  `specs/the-cjk-drop-remedy-assumes-the-non-latin-text-is-a-label-not-the-finding.md` (the two
  remedy branches, neither of which applies to a marker),
  `specs/generators-warn-on-dropped-unencodable-characters.md` (INV-159's origin)

## Invariants introduced

- `INV-266` — An exemption from a generator's dropped-character report MUST be scoped to an identified passage, never to a character; MUST leave the character dropped from the page; MUST be evaluated against the full normalized passage before any excerpt truncation; MUST NOT prevent the same character being reported elsewhere in the document, including when the exempt passage is rendered first; and is admissible only for a plugin-mandated machine-readable marker read from the source rather than the artifact (recorded in `specs/INVARIANTS.md`, group *Generator behavior: rendering, encoding, reporting*, alongside INV-143 and INV-159).

Wording signed off by the maintainer on 2026-08-23 ("all"), as drafted in this spec.
