# The eval-license request calls `how_heard` optional; the server requires it

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:636-637` tells the guide what
the evaluation-license call needs:

> The `submit_feedback` tool's `license_request` category **requires** a first name and a **work**
> email address (personal domains are rejected), **optionally a last name and how they heard about
> Senzing**

**The server says `how_heard` is required, not optional.** Verified live on **MCP server 1.32.9,
2026-08-12**, from two independent places in the same session:

- the `submit_feedback` tool schema's own property description —
  `how_heard`: *"How the requester heard about Senzing **(required for license_request)**"*,
  against `lastname`: *"Last name of the requester **(optional** for license_request)"*;
- `get_capabilities`' tool manifest — *"set category to 'license_request' and provide firstname
  (required), lastname (optional), email (work email required — personal domains rejected), and
  how_heard."*

The plugin groups `lastname` and `how_heard` together as the optional pair. The server splits
them: `lastname` optional, `how_heard` required.

**Why this one costs more than a missing parameter usually does.** This is the plugin's *only*
step that transmits the Bootcamper's personal details off their machine (INV-135), and it is
reached only after a pinned 👉 consent gate. So the failure sequence is: the Bootcamper is asked to
consent to sending their name and work email, says yes, and the call is then built without a field
the server requires. Whatever the server does with it, the Bootcamper has been walked through a
privacy gate for a request that may not produce the license — and this is the route a Bootcamper
without a license takes to get one, so failing it blocks the licensed path (INV-036/INV-093).

INV-135 additionally requires the pinned question to state **what is sent**. A question built from
this text describes a payload that is not the payload.

**A guard already knows the truth and does not assert it.** `tests/test_mcp_call_contracts.py:129-135`
classifies `submit_feedback` under `CONDITIONALLY_REQUIRED` and says, correctly:

> requirement depends on `category`: license_request needs firstname + work email + **how_heard**

So the repo holds both the right answer and the wrong one, in a test and in the shipped guidance,
and nothing compares them.

## Root cause

Two things, and the second is the reusable lesson.

1. **The requirement is not in the JSON Schema.** `submit_feedback`'s schema has **no `required`
   array at all** — every property is nullable with `default: null`. `how_heard`'s requirement
   exists only in the property's *description* prose. A reader checking "what does the schema mark
   required?" correctly concludes "nothing", and INV-136 is phrased around *"required parameters as
   the live schema states them"*. This is precisely the class **INV-192** exists for — *a parameter
   an MCP tool's schema marks optional may still be mandatory to its answer* — applied to a request
   the plugin never makes in call form, so no `needs_input` gate ever surfaces it.

2. **`TestLicenseRequestIsConsentGated` checks the gate, not the payload.** Its two assertions are
   that a pinned 👉 consent question sits near the `license_request` mention, and that
   `feedback.md` scopes its identifier-stripping rule. Neither reads the field list, so the
   `CONDITIONALLY_REQUIRED` comment that names `how_heard` is documentation inside a test rather
   than an assertion — the same guard-narrower-than-its-claim shape recorded twice already today.

## Proposed change

1. **Correct `module-04-data-collection/SKILL.md:636-637`** so the required set is first name, work
   email **and** how they heard about Senzing, with only `lastname` optional. Carry the provenance
   inline (tool, server version, date) per INV-080.

2. **Make the pinned consent question state the real payload.** INV-135 requires it to say what is
   sent; if it enumerates the fields, it gains the third. Whatever the Bootcamper is asked for must
   be asked one question per turn, as INV-135 already requires.

3. **Assert the field list**, not only the gate: extend `TestLicenseRequestIsConsentGated` so the
   license step names all three required fields, and so the `CONDITIONALLY_REQUIRED` comment and the
   shipped text cannot drift apart again.

⛔ **Do not add a call form.** The plugin deliberately describes `submit_feedback` in prose rather
than writing an invocation (see `test_mcp_call_contracts.py:187`, which notes the paren-only scan
would otherwise report it uncalled). This spec corrects what the prose says, not how it is written.

⛔ **Do not invoke `submit_feedback` to confirm the failure mode.** A dry run must never file
upstream or transmit a name and email. The requirement is established from the schema and the
manifest; the runtime consequence is stated as unverified below and must stay that way.

## Acceptance criteria

- [ ] `module-04-data-collection/SKILL.md` states that `license_request` requires first name, work
      email **and** how they heard about Senzing, with `lastname` the only optional field. Verified
      by opening the file.
- [ ] The claim carries its provenance — tool, **server 1.32.9**, date — in the shipped text
      (INV-080), scoped to that paragraph rather than relying on another stamp on the page.
- [ ] The pinned consent question's statement of what is sent matches the corrected field list
      (INV-135). Verified by opening the question.
- [ ] `tests/test_mcp_call_contracts.py`'s license tests assert the step names **all three**
      required fields, not only that a consent gate exists.
- [ ] **Negative-controlled, mutation verified to land:** removing `how_heard`/"how they heard" from
      the license step fails the new assertion; removing the consent question still fails the
      existing one. Revert both.
- [ ] The `CONDITIONALLY_REQUIRED["submit_feedback"]` comment and the shipped text agree — asserted,
      not merely both present.
- [ ] **No call to `submit_feedback` is added**, and none is made while implementing. Verified by
      `git diff` showing no new `submit_feedback(` invocation.
- [ ] Full suite passes (baseline **1756 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); cross-platform and language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`
- `tests/test_mcp_call_contracts.py`

## Source

- Dry run, **phase 1 (MCP call contracts)**, 2026-08-12. Found by enumerating every
  `action=`/`topic=`/`category=` literal the plugin uses and checking each against the live schema:
  `category='license_request'` appeared in no call form, which led to reading the prose that
  describes it.
- **MCP:** server **1.32.9**, 2026-08-12. Tools called: `get_capabilities`, plus the
  `submit_feedback` schema loaded via `ToolSearch`. **`submit_feedback` was NOT invoked** — the dry
  run's absolute rule forbids it.
- ⚠️ **Not runtime-verified, and cannot be here.** That the server *rejects* a `license_request`
  missing `how_heard` is inferred from its schema description and manifest, not observed. Confirming
  it would require sending a real name and work email upstream. The documentation discrepancy is
  established; the runtime consequence is not.
- Priority: **Medium-high.** Narrow path — only Bootcampers who request an evaluation license — but
  on that path it follows a privacy consent gate, and the plugin's statement of what is sent is
  wrong regardless of what the server does with the call.
- Related: INV-135 (consent gate and payload statement), INV-192 (schema-optional but
  answer-mandatory), INV-136 (satisfy required parameters as the schema states them),
  INV-201 (`test_mcp_call_contracts.py` must classify every tool).

## Invariants introduced

**None proposed.** INV-192 already states the governing rule — a parameter the schema marks optional
may still be mandatory — and INV-135 already requires the consent question to state what is sent.
This is an unapplied instance of both, plus a guard that documents the requirement without
asserting it.

## Deviations from this spec, and why (2026-08-12)

**The guard took three attempts, and the two failures are worth recording because both were caught
only by running the mutation — neither was visible by reading.**

1. **The first version asserted the wrong thing.** It checked that the token `how_heard` appeared
   somewhere in the license-step window. Reverting the prose to the defective *"optionally a last
   name and how they heard about Senzing"* left that token intact further down, inside the quoted
   `get_capabilities` manifest added as provenance — so the mutation **passed**. A guard a restored
   defect satisfies is worse than no guard.
2. **The fix then failed on the correct tree.** Widening to "no 'optional' near 'heard'" fired on
   the same quoted manifest, which legitimately reads *"lastname (optional), email (…), and
   how_heard"*. Correct text, failing guard.

Resolved by asserting the **claim where the claim is made** — the field-list statement, cut at the
following ⛔ — with the quoted provenance deliberately out of scope, and an assertion that the
statement still precedes that ⛔ so the scoping cannot silently drift. Both the mutation and the
correct tree now behave.

**The pinned consent question's wording changed** (INV-056 wording is pinned, and this spec's
Proposed change §2 authorized it): it now reads *"including your name, work email, and how you heard
about us"*. The pre-existing guard matches on the question's prefix, so it still passes untouched —
verified rather than assumed.

**No other deviation.** Every criterion holds; the only one not runtime-verified is the one the spec
already marked so — that the server *rejects* a request missing `how_heard` is inferred from its
schema and manifest, never observed, because confirming it would mean sending a real name and work
email upstream.
