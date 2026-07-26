# Stop asking how model guidance should be handled

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

During Bootcamp preparation Step 3a the bootcamper was asked:

> 👉 **How would you like model guidance handled? Reply with a number:**
>
> 1. **A one-line recommendation at each module** *(recommended)* — shown alongside the time estimate; never interrupts.
> 2. **Don't show it** — no model or effort guidance at all.
> 3. **Stop and ask me each time** — pause with a yes/no question whenever the recommendation changes.

They do not want the question asked at all. They always want to control model and effort
switches themselves, and never want a switch auto-picked or applied without explicit
confirmation — i.e. they want `model_guidance: prompt` hardcoded for every run, with no
choice presented.

They interrupted the pending Step 3a question with this feedback rather than answering it.

## Root cause

Not a defect — the current behavior is exactly as designed.

`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:140-160` presents the Step 3a
question once per run with `advisory` recommended, then holds the answer for the Step 6
consolidated write as `model_guidance: advisory | off | prompt`. There is no way to skip the
question or to pre-set the preference.

That design is **mandated** by INV-119, established one day earlier by
`model-effort-guidance-advisory-not-gate` (2026-07-25):

> Model/effort guidance … MUST be governed by a `model_guidance` preference
> (`advisory` | `off` | `prompt`), captured once in Bootcamp preparation as a single pinned
> 👉 question (INV-056) …

## ⚠️ Invariant conflict — read before implementing

**The requested change conflicts with INV-119**, which requires this preference to be
captured by a pinned 👉 question in Bootcamp preparation. Removing the question and
hardcoding a value cannot be done while INV-119 stands as written.

Two further considerations the maintainer should weigh, because they are not visible from the
feedback entry alone:

1. **`prompt` is the mode INV-119 was created to stop being the default.** The spec that
   established it exists because the unconditional blocking gate under `prompt` cost the
   bootcamper turns at every module boundary. Hardcoding `prompt` for **all** bootcampers
   re-imposes on everyone the friction that spec removed.
2. This is a **standing personal preference of one bootcamper**, not a defect report — which
   is a strong argument for a remembered-preference mechanism rather than a changed global
   default.

Recommended resolution, which satisfies the request without regressing other bootcampers:

- **Honor a pre-existing `model_guidance` value and skip the question when one is present.**
  If `config/bootcamp_preferences.yaml` already carries `model_guidance`, Step 3a states the
  mode in one line and asks nothing (INV-006 — never ask twice). This bootcamper sets it once
  and is never asked again, on any run, in any project that carries the file forward.
- If the maintainer instead wants the literal request — the question deleted and `prompt`
  hardcoded for every run — that requires a **new invariant superseding INV-119's
  question-capture clause**, recorded per the rules in `INVARIANTS.md` → "Maintaining this
  file". Do not silently drop the question while INV-119 reads as it does.

## Proposed change

Implement the pre-set-preference path (the recommended resolution above):

1. In Step 3a (`SKILL.md:140-160`), read `config/bootcamp_preferences.yaml` first. When
   `model_guidance` is already set to a valid value (`advisory` | `off` | `prompt`):
   - Do **not** present the question.
   - State the mode in one line as part of the setup-choices recap (INV-099), e.g.
     "Model guidance: stop and ask me each time (from your saved preferences)."
   - Carry the value into the Step 6 consolidated write unchanged.
2. When it is absent or unreadable, present the question exactly as today (INV-119 path
   unchanged), and keep the absent-preference default of `advisory`.
3. Document how to pre-set it durably, so the bootcamper can opt out of the question for
   good: `model_guidance: prompt` in `config/bootcamp_preferences.yaml` before starting. Note
   it alongside the existing "change model guidance" affordance (`SKILL.md:158`).
4. Extend `tests/test_model_guidance_modes.py` to cover the skip-when-present path.

If the maintainer chooses the hardcode-`prompt` route instead, the spec's scope becomes:
delete Step 3a, write `model_guidance: prompt` unconditionally in Step 6, and append a new
invariant superseding the question-capture clause of INV-119 — leaving the three runtime modes
themselves intact, since other surfaces read the preference.

## Acceptance criteria

- [ ] With `model_guidance: prompt` already present in `config/bootcamp_preferences.yaml`, a
      fresh run of Bootcamp preparation presents **no** model-guidance question and the run
      behaves in `prompt` mode throughout.
- [ ] With no `model_guidance` present, Step 3a presents the pinned question verbatim, exactly
      as it does today (INV-119 / INV-056 unaffected).
- [ ] The value persisted in Step 6 matches the pre-existing value; the pre-set value is never
      overwritten with the recommended default.
- [ ] The mode in force is stated once to the bootcamper in the setup-choices recap, whether it
      came from a question or from saved preferences (INV-099).
- [ ] `advisory` remains the behavior when the preference is absent or unreadable (INV-119).
- [ ] `tests/test_model_guidance_modes.py` covers both the asked and skipped paths and passes.
- [ ] If the hardcode route is taken instead, `specs/INVARIANTS.md` carries a new invariant
      superseding INV-119's question-capture clause, with provenance — INV-119 is edited in
      place only to note the supersession, never deleted or renumbered.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — Step 3a: read the
  preference first and skip the question when present; document pre-setting it.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — note that the mode
  may arrive from saved preferences rather than the Step 3a question.
- `tests/test_model_guidance_modes.py` — cover the skip-when-present path.
- `specs/INVARIANTS.md` — only if the hardcode route is chosen (new superseding invariant).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Skip the model-guidance question and
  always default to 'Stop and ask me each time'" (2026-07-25, Module Bootcamp preparation;
  `Source: bootcamper-reported`)
- Priority: Medium
- Related specs: `specs/model-effort-guidance-advisory-not-gate.md` (established INV-119/INV-120
  — the invariant this request conflicts with), `specs/model-effort-change-prompt.md` (INV-063),
  `specs/model-effort-switch-done-confirmation.md` (INV-069),
  `specs/auto-initialize-git-without-prompt.md` (precedent for removing a setup question
  outright).
