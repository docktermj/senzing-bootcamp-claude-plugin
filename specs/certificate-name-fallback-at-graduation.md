# Ask for the certificate name at graduation rather than silently printing "Bootcamper"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The bootcamper asked that, in the Graduation module, before building the recap/certificate PDF, if the
bootcamper's name is not already known, the skill should ask what name they'd like printed on the
"Certificate of Completion."

The name is auto-detected during Bootcamp preparation and never asked (by design). If detection fails
or returns something unsuitable for a certificate — a system username, an empty value, or a git handle
rather than a real name — graduation has no fallback: it either omits the name or uses the bad value.
A certificate is the one keepsake artifact where a wrong or generic name is immediately visible and
permanently wrong.

## Root cause

**Confirmed.** The generator silently substitutes a placeholder, and the skill never checks.

`scripts/generate_recap_pdf.py:617-636` extracts the certificate name and ends with:

```python
name = name or "Bootcamper"
```

So a missing or empty name yields a Certificate of Completion reading "Bootcamper" — a valid PDF, no
warning, exit 0. The stdlib fallback renderer builds the same certificate
(`generate_recap_pdf.py:902-936`), so the placeholder appears on both paths.

`skills/graduation/SKILL.md:111` reads the value with no validation:

> 1. **Read preferences:** load `config/bootcamp_preferences.yaml` and extract `name`, `language`,
>    `path` …

There is no check that `name` is present, non-empty, or display-quality, and no fallback question
anywhere in the graduation skill. INV-100 requires the certificate to carry "the bootcamper's name" but
does not say what happens when there isn't one — so the generator's placeholder satisfies the letter of
the invariant while defeating its purpose.

The upstream detection is intentional and should not change: `specs/bootcamp-prep-name-never-asked.md`
established auto-detection with no prompt. This spec adds the *downstream recovery path* that design
never described.

## Proposed change

1. **Validate the name in graduation's Pre-checks**, extending `skills/graduation/SKILL.md:111`. Treat
   the name as unusable when it is missing, empty/whitespace, or clearly not a display name — e.g. it
   looks like a shell/system account (`root`, `ubuntu`, `ec2-user`), contains no letters, is a single
   token with no capitalization that matches the OS username, or is an email address or `@handle`
   rather than a person's name. Keep the test conservative: a plausible real name must never trigger
   the prompt, because asking someone their name after auto-detecting it correctly is its own defect
   (and would violate the ask-once intent of INV-006).
2. **Ask once, only when unusable**, as a single pinned 👉 question (INV-005/INV-056) before Step 1
   renders the PDF — for example:

   > 👉 **What name would you like printed on your Certificate of Completion?**

   Pin the wording verbatim so it cannot drift.
3. **Persist the answer** to `config/bootcamp_preferences.yaml` as the `name` preference, so a re-render
   or a resumed session does not ask again (INV-006).
4. **Never block graduation.** If the bootcamper declines or gives no usable answer, proceed with the
   existing placeholder rather than stalling — graduation is non-blocking by design. But the placeholder
   must then be a *chosen* outcome, not a silent one.
5. **Make the generator's substitution visible.** In `generate_recap_pdf.py`, when the placeholder is
   used, write a warning to stderr naming it (e.g. `WARNING: no bootcamper name found; certificate
   shows "Bootcamper"`). Today it is indistinguishable from success. Keep the fallback itself — a
   certificate must still render — but stop it from being silent, consistent with the fail-visibly
   direction of `specs/recap-pdf-generator-fail-loudly-on-content-loss.md`.
6. **PII boundary.** The name goes only into the local recap and PDF. `skills/graduation/SKILL.md:168`
   already forbids recording hostname, username, IP, or other host identifiers in the recap (INV-065) —
   the fix must not launder a rejected *system username* into the recap by way of this prompt. If the
   detected value was rejected as a system account, do not print it anywhere; ask, and use the answer.

## Acceptance criteria

- [ ] Graduation's Pre-checks validate the detected `name` against a stated, conservative
      unusable-name test before the recap PDF is rendered.
- [ ] When the name is usable, **no** question is asked (auto-detection behavior is unchanged, per
      `specs/bootcamp-prep-name-never-asked.md`).
- [ ] When it is unusable, one pinned verbatim 👉 question asks for the certificate name, and the answer
      is persisted to `config/bootcamp_preferences.yaml` so it is never asked twice.
- [ ] Declining does not block graduation; the PDF still renders.
- [ ] `generate_recap_pdf.py` emits a stderr warning whenever the `"Bootcamper"` placeholder is used, in
      both the fpdf2 and stdlib renderers.
- [ ] A rejected system-account value is never printed on the certificate or written into the recap
      (INV-065).
- [ ] The Certificate of Completion continues to satisfy INV-100 (name, date, modules completed;
      landscape) on both renderers.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      unusable-name test must not assume a POSIX username shape, and must behave identically where
      `git config user.name` is unset.

## Affected files

- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Pre-checks (line ~111): add the name
  validation and the pinned fallback question before Step 1's PDF render
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — lines ~617-636 (`name = name or
  "Bootcamper"`): warn on stderr when the placeholder is used; same for the stdlib certificate path
  (~902-936)
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — no behavior change; confirm the
  auto-detection contract still reads as "detect, never ask" with this downstream recovery noted

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Ask the bootcamper's preferred name for the
  certificate of completion, if unknown, before building the recap PDF" (2026-07-24, Graduation)
- Priority: Medium (the bootcamper moved to the next item before assigning one; defaulted to the
  session's standard)
- Related specs: `specs/landscape-certificate-of-completion.md` (established INV-100),
  `specs/bootcamp-prep-name-never-asked.md` (established detect-never-ask),
  `specs/recap-pdf-generator-fail-loudly-on-content-loss.md`

## Invariants introduced

- `INV-113` — Graduation MUST verify a certificate-quality name before rendering the recap PDF and,
  only when it is unusable, ask one pinned 👉 question and persist the answer; a rejected
  system-account value is never printed or recorded (INV-065), and the generator MUST warn on stderr
  whenever it renders the placeholder name. (Recorded in `specs/INVARIANTS.md`.)

## Implementation notes

The naive fix — warning from inside `_cert_fields` — fires **twice**: the fpdf2 renderer runs a
measure pass (to compute TOC page numbers) plus a real pass, so that helper is called once per pass.
The warning belongs in `main()`, via the extracted `recap_missing_certificate_name()` predicate.
