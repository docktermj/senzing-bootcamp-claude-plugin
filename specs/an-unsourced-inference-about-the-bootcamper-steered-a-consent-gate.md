# An unsourced inference about the Bootcamper's employer steered the license consent gate

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At the Senzing License Key gate (Module 4, Step 8a), the Bootcamper selected option 4 — *request a
free evaluation license now through the bootcamp*. Before sub-step 6a asked for a single value, the
guide volunteered an advisory it had no source for. Their report:

> the guide volunteered — before collecting any values — that the bootcamper's account email was on
> the `senzing.com` domain, and that "if you're at Senzing, you very likely have access to a license
> through internal channels, which would be faster and wouldn't consume the one-per-email public
> evaluation request."

The Bootcamper asked whether that was correct. It was half-and-half, and the split is the whole
finding:

- **Sourced and correct** — "one per email, re-requestable after 30 days", and the duration/volume
  terms, came verbatim from the MCP server's `get_capabilities` description of `submit_feedback`'s
  `license_request` category.
- **Unsourced** — "you very likely have access to a license through internal channels" was the
  guide's own inference about how Senzing employees obtain licenses. It was stated flatly, not
  hedged, and used to steer a decision the Bootcamper had made one turn earlier.

Their words:

> "I don't want assumptions presented as fact."

⛔ **The placement is what makes this more than a stray sentence.** Sub-step 6a is the only step in
the entire bootcamp that transmits the Bootcamper's personal details off their machine, and the
gate immediately before it has real consequences the guide had just described — one request per
email, a 30-day wait before another. An unsourced advisory delivered *there*, arguing against the
option they had just picked, is the worst possible location for the plugin's sourcing discipline to
lapse.

A second concern the Bootcamper raised: their email address is supplied to **identify** them, not
as a premise to reason from. Inferring an employer from the domain and redirecting a decision on
that basis goes beyond identification.

## Root cause

**The MCP-first invariant is scoped to Senzing *technical* facts, and this was a claim about
Senzing's *business practices*.**

`plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:169-176`:

```text
## MCP-first invariant (absolute precedence)

- ALL Senzing facts come from the Senzing MCP tools - never from training data. […]
- **Pre-response checklist:** if your response contains Senzing SDK method names, attribute
  names, config options, error codes, or entity-resolution technical details, you MUST have
  called an MCP tool this turn to get them. If not, stop and call it first.
```

The checklist enumerates its own scope: *SDK method names, attribute names, config options, error
codes, entity-resolution technical details*. **INV-080** repeats exactly that enumeration. "Senzing
employees very likely have internal license access" is none of those, so the guide had no rule
telling it that this sentence needed a source — and treated it as ordinary conversational
helpfulness.

**The adjacent invariant governs questions, not volunteered statements.** INV-247 requires every 👉
question to trace to a step in a shipped skill file. It is the closest rule on the books and it does
not reach this: nothing was *asked*. An improvised advisory that reshapes a decision sits in the gap
between "every question has an origin" and "every Senzing fact has a source".

**Sub-step 6a authorizes nothing of the kind.**
`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:905-912` specifies exactly what
precedes the value questions:

```text
1. **Confirm the current requirements from the tool itself** before asking for anything, so you
   request exactly the fields it needs and no more. Never collect a field "in case".
2. **Ask for the values, one 👉 question per turn (INV-251)**, saying plainly that a work email is
   required and that a personal address will be rejected.
```

Confirm requirements, then ask. There is no step between them, and nothing in Step 8a's option list
invites the guide to re-argue an option the Bootcamper already chose.

**Nothing anywhere governs what the guide may infer from identifying context.** A search of
`ground-rules.md` for `email`, `employer`, `identify` and `identifying` returns nothing — the file
has no rule about using the Bootcamper's identity as a premise. INV-065's identifier-stripping
discipline is about what leaves the machine in a *bug report*, and sub-step 6a already states that
it cannot apply here because the license call does not work without those details. So the
collection side is governed and the **reasoning** side is not.

## Proposed change

Three changes, smallest first. All are prose; none touches the license flow's mechanics.

**1. Widen the sourcing rule in `ground-rules.md` from Senzing *facts* to Senzing *assertions*.**
Beside the MCP-first invariant, state that an assertion about Senzing — the company, its licensing,
its support, its internal practices, its customers — is subject to the same discipline as an SDK
fact: it comes from an MCP tool, from a shipped skill file, or from something measured on this
machine. Anything else is either labeled as an inference **at the point it is made** or not said at
all. Keep the existing pre-response checklist verbatim and add the business-practice class to it, so
the enumeration stops reading as exhaustive of "things needing a source".

⚠️ **Label-or-omit, not label-and-proceed.** The remedy is not a hedge bolted onto the same
advisory. At a consent gate the Bootcamper has already answered, the correct action is silence — the
inference has no bearing they asked for. The labeling half of the rule is for the case where the
Bootcamper *asks* something the plugin cannot source.

**2. State in Module 4 Step 8a that the gate's options are the options.** Once the Bootcamper has
selected one, the guide proceeds with it. It does not re-argue the choice, advocate an option that
is not on the list, or introduce a consideration no step supplies. If new information genuinely
invalidates a selection — a tool reports the category unavailable — that is a reported failure with
its own branch, not an advisory.

**3. Add the identity rule, in `ground-rules.md` where identity is discussed.** The Bootcamper's
identifying context — name, email address, account details — is for identification and for fields a
tool explicitly requires. It is **not** an input to the guide's reasoning about what they should
choose. Do not infer employer, affiliation, seniority or entitlement from an email domain or any
other identifying detail, and never use such an inference to steer a decision.

## Acceptance criteria

- [ ] `ground-rules.md`'s MCP-first section states that assertions about Senzing's business
      practices — licensing, support, internal process — require a source on the same footing as
      SDK facts, and that an unsourceable assertion is labeled as an inference at the point it is
      made or not made at all.
- [ ] The pre-response checklist no longer reads as an exhaustive list of the only claim classes
      needing a source.
- [ ] `ground-rules.md` states that the Bootcamper's identifying context is never a premise for the
      guide's reasoning about what they should choose, naming the email-domain-to-employer
      inference as the worked example.
- [ ] Module 4 Step 8a states that after a selection the guide proceeds with the selected option and
      does not re-argue it or introduce an option the step does not list.
- [ ] A new invariant records the sourcing rule for non-technical Senzing assertions, and a test
      asserts the rule is present in `ground-rules.md`. ⚠️ The runtime behavior itself is not
      statically testable — the offending sentence existed in no file (the INV-247 guard has the
      same limit, disclosed in `tests/test_no_host_control_is_offered_as_a_question.py`). State that
      limit in the guard's docstring rather than implying coverage it cannot have.
- [ ] Sub-step 6a's consent discipline, pinned wording and field list are unchanged — this spec adds
      a constraint on what may precede it, and changes nothing the tool is sent.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — widen the MCP-first
  sourcing rule beyond technical facts; add the identity-is-not-a-premise rule
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — Step 8a: the gate's options
  are the options, no re-arguing a selection
- `specs/INVARIANTS.md` — register the sourcing rule for non-technical Senzing assertions
- `tests/` — a guard asserting the rule ships in `ground-rules.md`, with its runtime limit disclosed

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: Guide presented an unsourced
  inference about employer licensing as fact" (2026-08-25, Module: Data collection;
  `Source: bootcamper-reported`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact). This spec asserts nothing about Senzing behavior — its
  diagnosis rests on the scope of the plugin's own sourcing rule at `ground-rules.md:169-176` and on
  what Module 4 sub-step 6a specifies, both verified in the shipped files on 2026-08-25. ⚠️ The
  Senzing MCP server was **unreachable at triage time** (the connector requires authorization and
  this session is non-interactive), so the entry's own citation of the `license_request` terms was
  not re-confirmed; nothing in this spec depends on it, and the license flow's own MCP-sourced
  wording is untouched.
- Upstream: not applicable — the defect is the plugin's sourcing rule, not server behavior.
- Related specs: `specs/a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper.md`
  (INV-247, the questions half of the same gap),
  `specs/inv247-guard-is-narrower-than-the-invariant-it-enforces.md`,
  `specs/mcp-grounding-in-every-skill.md` (INV-080)
