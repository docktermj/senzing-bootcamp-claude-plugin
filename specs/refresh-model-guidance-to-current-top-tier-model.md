# Update model guidance from Opus 4.8 to Opus 5, and give it a single source of truth

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Opus 5 has superseded Opus 4.8, but the plugin's model-recommendation guidance still names Opus 4.8 as
the top-tier model to switch to for correctness-critical work. The bootcamper was running on
`claude-opus-5`, so the recommendation the plugin printed was already behind the model actually in use.

Their point: the model nudge is one of the first things a bootcamper sees at the start of every heavy
module (INV-063). Recommending a superseded model undercuts the credibility of that guidance — and a
bootcamper who follows it literally would switch **down** from Opus 5 to Opus 4.8 at exactly the
correctness-critical moments the nudge exists to protect (SDK setup, Data quality & mapping, and
graduation).

## Root cause

**Confirmed: 17 hardcoded references across 4 files, with no single source of truth.** Verified by
grep; the count matches the feedback's inventory exactly.

| File | Hits | Lines |
|---|---|---|
| `docs/model-selection.md` | 10 | 59 (pricing table row), 75, 79, 82 (per-module recommendation rows), 100, 102 (per-stage table), 110, 112 (`/model claude-opus-4-8`), 116 |
| `skills/bootcamp-onboarding/ground-rules.md` | 5 | 18, 255 (the INV-063 nudge question), 273, 279, 281 (per-stage table) |
| `skills/graduation/SKILL.md` | 2 | 81, 91 (the graduation model-switch question) |
| `skills/bootcamp-onboarding/feedback.md` | 1 | 106 (example string in the feedback context template) |

The structural cause is duplication: `ground-rules.md:274` even instructs "keep in sync with
`../../docs/model-selection.md`", and `graduation/SKILL.md` carries a third copy. Content authored
against the model lineup at release time goes stale the moment a new model ships, and the sync is
manual. INV-063 explicitly makes the per-stage values *advisory* and *not part of the invariant*, so
updating them violates nothing.

## Proposed change

1. **Update every display name** `Opus 4.8` → `Opus 5` across all 17 sites.
2. **Update the model ID together with the name.** `docs/model-selection.md:112` embeds a
   copy-pasteable command, `/model claude-opus-4-8` → `/model claude-opus-5`. This is a **functional**
   change, not wording: if the name moves without the ID, the command the bootcamper pastes silently
   selects the old model. Verify the ID string against current Claude documentation at implementation
   time rather than trusting this spec.
3. **Do not carry the pricing figures forward.** `docs/model-selection.md:59` attaches "~$5 / ~$25" per
   Mtok to Opus 4.8. Relabeling that row "Opus 5" would silently attach stale numbers to a different
   model — a worse defect than the one being fixed. Either source the current figures from official
   Anthropic pricing at implementation time, or drop the pricing column and link out to it. **Do not
   estimate.** Pricing is the one field in this table that cannot be inferred.
4. **Establish one source of truth,** since this is the second time model guidance has gone stale.
   Keep the per-stage recommendation table in exactly one place — `docs/model-selection.md` — and have
   `ground-rules.md` and `graduation/SKILL.md` **reference** it rather than restating it. Remove the
   duplicated tables at `ground-rules.md:277-282` and the guidance at `graduation/SKILL.md:81`, leaving
   the pinned question wording (which must stay verbatim per INV-056) parameterized by the referenced
   values. INV-063 already declares these values advisory, so centralizing them is consistent with it.
   A future model refresh then becomes a one-table edit instead of a 17-site sweep.
5. **Sanity-check the direction of each recommendation after the rename.** The per-stage table puts
   Data processing on "Sonnet 5, high effort" while SDK setup and graduation move to Opus 5. On a
   session already running Opus 5, that stage's nudge becomes a **downgrade** presented in neutral
   tone. Flagging direction is specified separately in
   `specs/model-effort-guidance-advisory-not-gate.md`; if that spec is implemented first, this rename
   should land in the advisory format rather than the gate format. Implement whichever is scheduled
   first and note the dependency — do not implement the same lines twice.
6. **`feedback.md:106` is a template example string**, not guidance. Update it for consistency, but it
   carries no behavioral weight — the feedback template records whatever model the session is actually
   using.
7. **Add a staleness note** to `docs/model-selection.md` stating that model names, IDs, and pricing are
   point-in-time and must be re-verified against current Claude documentation, with the date of last
   verification. It will go stale again; the note makes that visible instead of silent.

## Acceptance criteria

- [ ] No occurrence of `Opus 4.8`, `opus 4.8`, or `claude-opus-4-8` remains anywhere under
      `plugins/senzing-bootcamp/`.
- [ ] Every switch command a bootcamper can copy resolves to the current top-tier model ID, verified
      against current Claude documentation at implementation time.
- [ ] The pricing row carries either current verified figures or no figures at all — never the old
      numbers under a new model name.
- [ ] The per-stage model/effort recommendation table exists in exactly one file
      (`docs/model-selection.md`); `ground-rules.md` and `graduation/SKILL.md` reference it instead of
      restating it.
- [ ] The pinned nudge and switch questions still satisfy INV-056 (verbatim wording) and INV-063 (the
      advisory-values clause), and INV-098's surface-aware phrasing is preserved on both the CLI and
      non-CLI branches.
- [ ] `docs/model-selection.md` carries a dated "re-verify against current Claude documentation" note.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md):
      documentation and guidance text only, with no platform- or language-specific behavior.

## Affected files

- `plugins/senzing-bootcamp/docs/model-selection.md` — lines 59, 75, 79, 82, 100, 102, 110, 112, 116;
  becomes the single source of truth and gains the staleness note
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — lines 18, 255, 273, 279, 281;
  the duplicated per-stage table is replaced by a reference
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — lines 81, 91
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — line 106 (template example only)

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Update model-recommendation guidance from Opus
  4.8 to Opus 5" (2026-07-24, General)
- Priority: Medium
- Related specs: `specs/model-effort-guidance-advisory-not-gate.md` (**touches the same lines — check
  sequencing**), `specs/model-effort-table-name-based.md`, `specs/skill-model-selection.md`,
  `specs/module-start-model-nudge.md`, `specs/surface-aware-model-effort-instructions.md` (INV-098)

## Invariants introduced

- `INV-114` — Bootcamper-facing model/effort guidance MUST name only current, non-superseded models
  and IDs, and the per-stage table MUST be identical wherever it appears — `ground-rules.md`
  authoritative, `docs/model-selection.md` derived and carrying a dated verification note;
  `tests/test_model_guidance_sync.py` enforces it. (Recorded in `specs/INVARIANTS.md`.)

## Implementation notes

Two corrections to this spec, both settled during implementation:

1. **The pricing caution does not apply.** Opus 5 is priced *identically* to Opus 4.8 ($5/$25 per
   MTok, verified against current Claude documentation on 2026-07-25), so relabeling the row does not
   attach stale figures. The figures were kept and a dated staleness note added instead.
2. **Criterion 4's direction was inverted, with maintainer approval (2026-07-25).** Deleting the
   `ground-rules.md` table would make the INV-063 module-start nudge depend on fetching a maintainer
   doc that is not auto-loaded — a silent-misfire risk. `ground-rules.md` is now the authoritative
   copy and `docs/model-selection.md` is marked derived; drift is prevented by
   `tests/test_model_guidance_sync.py` rather than by deletion.
