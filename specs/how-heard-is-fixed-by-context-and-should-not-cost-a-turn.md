# The license request asks "How did you hear about Senzing?" of someone who is, at that moment, taking the Senzing bootcamp

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

At Data collection Step 8a's in-flow evaluation-license request, the plugin asked the Bootcamper
three separate questions before showing the draft and asking for consent to send:

> What first name should I use for the license request?
> What work email address should the license be sent to?
> **How did you hear about Senzing?**

The Bootcamper answered the third with "I am taking the bootcamp" and then said the question did
not need to be asked. In their words: **"no need to ask."**

They are right. The context answers it. A person being asked how they heard about Senzing, inside
the Senzing bootcamp, by the Senzing bootcamp plugin, is being asked something the asker already
knows. It costs a turn on a flow that already costs four of them (three fields plus the pinned
consent gate), on the one path a Bootcamper without a license must walk to get one.

## Root cause

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:861-862`, sub-step 6a step 2:

> **Ask for the values, one 👉 question per turn (INV-251)**, saying plainly that a work email is
> required and that a personal address will be rejected.

"The values" is every field the call needs, undifferentiated. Step 1 immediately above it
(`:860`) is careful about *which* fields to collect —

> **Confirm the current requirements from the tool itself** before asking for anything, so you
> request exactly the fields it needs and no more. Never collect a field "in case".

— and that discipline is about the field **list**, not about where a value comes from. So the step
distinguishes needed from unneeded fields and never distinguishes a field whose value is
**contextually fixed** (how they heard about Senzing) from one that is genuinely Bootcamper-specific
(name, work email). Every accepted field becomes a question by default.

`how_heard` is genuinely required — that is settled and correct in the plugin already
(`:827-836`), and re-confirmed on **server 1.33.0, 2026-08-21**: `submit_feedback`'s `how_heard`
property description reads *"How the requester heard about Senzing (required for
license_request)"*, against `lastname`'s *"(optional for license_request)"*, and
`get_capabilities`' manifest repeats the split. **Nothing about the requirement says the value must
come from a question.** The server needs a string; the bootcamp knows the string.

## Proposed change

1. **Default `how_heard` and drop the question.** Send a fixed, accurate value — "Senzing Bootcamp"
   (or "Claude Code / Senzing Bootcamp plugin"). Pick one and use it verbatim everywhere; it is
   telemetry Senzing reads, so consistency across runs is worth more than variety.

2. **Disclose the default in the pinned consent question, because INV-135 requires the question to
   state what is sent.** The current wording (`:867`) is:

   > 👉 **Send this evaluation-license request, including your name, work email, and how you heard about us, to Senzing? Reply with a number:**

   "how you heard about us" described an answer the Bootcamper gave. Once it is a default, the
   question must show the value rather than name the field — the Bootcamper is consenting to a
   payload, and a payload containing a string they never saw is not one they consented to. Show the
   draft with the literal value in it, as step 3 already requires ("Show the exact request").

3. **Keep an override available without spending a turn on it.** The consent gate is already a
   numbered choice; a Bootcamper who wants to say something else can say so there. Do not add a
   fourth option that re-asks — that trades the saved turn straight back.

4. **State the rule, so the next field with a contextually fixed value does not become a fourth
   question.** One clause in sub-step 6a: a required field whose value is determined by the
   bootcamp context is defaulted and disclosed, not asked; only Bootcamper-specific values are
   asked. Name `how_heard` as the instance.

⛔ **Do not extend this to the name or the work email.** Those are the Bootcamper's personal
details, the reason this gate exists (INV-135), and neither is inferable. A `git config user.name`
read is not consent to transmit a name to a third party.

## Acceptance criteria

- [ ] The in-flow license request sends `how_heard` without asking for it, using one fixed value.
- [ ] The pinned consent question and the shown draft both carry the literal `how_heard` value that
      will be transmitted — no field named without its value (INV-135).
- [ ] The flow reaches the consent gate in two questions (first name, work email), not three.
- [ ] Sub-step 6a states the defaulted-versus-asked distinction and names `how_heard` as the
      contextually-fixed case.
- [ ] `how_heard` is still present in every call — the existing guard on its requirement
      (`:827-836`) continues to pass.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — sub-step 6a: step 2's
  field-collection instruction (`:861-862`), the pinned consent question (`:867`), and the new
  defaulted-versus-asked clause
- `tests/` — the existing `license_request` field-list guard, extended to assert the consent
  question carries the `how_heard` value rather than only the field name

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Improvement: License-request flow asks
  \"how did you hear about Senzing\" unnecessarily" (2026-08-18, Module Data collection;
  `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**. `get_capabilities` →
  `submit_feedback`: `how_heard` is *"(required for license_request)"* in its property description,
  with no `required` array on the schema, and the tool manifest repeats it. The requirement stands;
  what is not required is that the value come from a question. No absence is asserted against the
  server.
- Upstream: not applicable — the server requires the field and says so; the number of turns spent
  collecting it is the plugin's choice.
- Related specs: `specs/license-request-omits-a-required-field-the-server-demands.md`,
  `specs/license-request-option.md`, `specs/module1-license-flow-parity.md`
