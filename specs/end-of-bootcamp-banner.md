# Add an "END OF SENZING BOOTCAMP" closing banner

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

After graduation completes and the bootcamper indicates they are done, there is
no distinct closing banner to signal the bootcamp has truly ended — the session
just trails off after the final 👉 question. The bootcamp uses banners as
bookends (WELCOME at the start, GRADUATION at the finish); a terminal
"END OF SENZING BOOTCAMP" banner would give a clear, satisfying sense of finality
and match the established visual language.

## Root cause

`plugins/senzing-bootcamp/skills/graduation/SKILL.md:143-158` ("Mandatory closing
step") ends on the single 👉 question "Is there anything else you would like to
explore?" and defines **no** end-of-bootcamp banner. The WELCOME
(`onboarding-flow.md:91-95`) and GRADUATION (`graduation/SKILL.md:28-32`) banners
exist, but there is no closing bookend.

## Proposed change

Add a mandatory closing banner rendered **exactly once**, **after** the
guaranteed-recap announcement and **after** the bootcamper declines further
exploration (answers "no" to the closing question) — not before, so it does not
pre-empt continued exploration. Format it like the other banners:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓🎓🎓  END OF SENZING BOOTCAMP  🎓🎓🎓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Pair it with guidance that, once the banner is shown, the Stop-hook nudge stands
down (the bootcamp is complete → no further closing-question prompts),
coordinating with the disable/stand-down switch in `stop-hook-false-positive.md`.

## Acceptance criteria

- [ ] `graduation/SKILL.md` defines the END OF SENZING BOOTCAMP banner and renders it exactly once, after the bootcamper declines further exploration.
- [ ] The banner does not appear while exploration continues, and never more than once per bootcamp.
- [ ] Guidance states the Stop-hook nudge stands down after the banner (no post-bootcamp closing-question prompts).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — add the closing banner + stand-down note to the mandatory closing step.
- `plugins/senzing-bootcamp/scripts/stop-nudge.py` — coordinate with the stand-down/disable switch from `stop-hook-false-positive.md`.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Add an \"END OF SENZING BOOTCAMP\" closing banner for finality" (2026-07-16, Graduation)
- Priority: Low
- Related specs: `stop-hook-false-positive.md` (Stop-hook stand-down after the banner)

## Invariants introduced

- `INV-057` — A terminal "END OF SENZING BOOTCAMP" banner MUST be presented exactly once, as the final output, after the Bootcamper declines further exploration at the end of graduation, and never while exploration continues (recorded in `specs/INVARIANTS.md`).
