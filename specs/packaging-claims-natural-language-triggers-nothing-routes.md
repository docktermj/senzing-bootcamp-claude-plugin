# `packaging.md` claims natural-language triggers, and nothing dispatches them

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`skills/bootcamp-onboarding/packaging.md:17` tells the reader how the flow is reached:

```text
Triggered by the `/package-bootcamp` command, or whenever the bootcamper says something
like "back up the bootcamp", "archive this", "move this to another machine", "zip it up",
or "send this to my colleague".
```

The command half is real. **The phrase half is reached by nothing.** The plugin's
`UserPromptSubmit` hook runs `scripts/feedback-capture.py`, which dispatches on the
feedback and note vocabularies only; no pattern in it — or in any other hook — matches
"back up", "archive", "zip" or "transfer". So those phrases reach the flow only if the
model has already loaded `packaging.md`, which it has no reason to do unless the command
was used.

⛔ **The wording is borrowed from a sibling that has the hook, which is what makes it
misleading.** `notes.md:16` reads *"Triggered by the plugin's `UserPromptSubmit` hook, by
the `/bootcamp-note` command, or whenever the bootcamper says something like…"* — three
routes, and the first genuinely exists. `packaging.md` drops the hook clause and keeps the
phrase clause, so the sentence reads as the same guarantee with one route fewer rather
than as a guarantee that was never implemented.

The cost is not that packaging is unreachable — `/package-bootcamp` works. It is that a
Bootcamper who says "can I archive this?" mid-module gets whatever the model improvises,
while a file in the plugin says that phrasing is a trigger.

## Root cause

The flow was written to the INV-254 any-time-flow precedent, and `notes.md` is that
precedent's shipped example. Its trigger sentence was carried across as a template. The
hook clause was correctly dropped, because no hook was added; the phrase list was not
re-examined, because it reads as prose rather than as a claim about machinery.

⚠️ **The spec did not ask for a hook and should not be read as having promised one.**
`specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` says the flow is
*"reachable at any point — onboarding, any module, graduation — from a new
`commands/package-bootcamp.md`"*. One route, the command. The overstatement was introduced
in implementation.

## Proposed change

Two options; the first is cheaper and is recommended.

**1. Say what is true.** State that the flow is reached by `/package-bootcamp`, and that the
listed phrasings are what the guide should **recognize as a request for it** — not phrases a
hook intercepts. One clause: *"there is no hook for these; recognize them and offer the
command."* That is honest, keeps the useful part (the guide knowing what the request sounds
like), and costs nothing.

**2. Add the dispatch.** Extend `feedback-capture.py` with a packaging vocabulary. ⛔ **This
is a bigger decision than it looks and should not be taken as the obvious fix.** That hook
runs on *every* prompt; it currently has two vocabularies with a documented precedence rule
between them (`notes.md`'s "when a message is both a note and a feedback report, it is
feedback"), and a third would need its own precedence — "back up my notes" is ambiguous
between two of the three. Defer it unless the maintainer wants the interception.

⚠️ **Whichever is chosen, check the sibling.** `notes.md`'s trigger sentence is accurate
today; this spec must not "harmonize" the two by copying packaging's corrected wording back
over a clause that is genuinely true of notes.

## Acceptance criteria

- [ ] `packaging.md`'s trigger sentence no longer implies a hook intercepts the listed
      phrasings — either by saying there is none, or because one was added.
- [ ] `notes.md`'s trigger sentence is unchanged; its `UserPromptSubmit` clause is accurate
      and must survive.
- [ ] A test asserts that a flow claiming hook-triggered dispatch names a vocabulary that
      `feedback-capture.py` actually carries. ⚠️ Derive the site set by scanning shipped
      any-time flows for the trigger-sentence shape (INV-246), not by naming the two known
      files — a third any-time flow inherits the same trap.
- [ ] Negative-controlled: restoring the current wording fails the test.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/packaging.md` — the trigger sentence
- `tests/` — a guard that a claimed hook trigger corresponds to a real dispatch vocabulary

## Source

- Feedback: n/a — found by `production-readiness-audit-2026-08-26` while checking Step 5's
  "every shipped surface is documented and reachable" against the new command;
  `Source: self-observed (assistant retrospective)`.
- Priority: Low — the feature is reachable by its command and nothing is broken. Filed because
  it is a claim about machinery that does not exist, which is the class that survives review by
  reading as prose.
- MCP re-check: n/a (no Senzing fact). Hook dispatch and trigger vocabularies are the plugin's
  own; no SDK method, flag, response shape or server behavior is asserted, and no absence is
  claimed.
- Upstream: not applicable.
- Related specs: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` (the flow),
  `specs/bootcamp-notes-capture-and-recap-section.md` (INV-254 and the `notes.md` precedent
  whose trigger sentence was the template)
