# Feedback-capture misses natural phrasings

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The `UserPromptSubmit` hook `feedback-capture.py` exists so that a bootcamper's
"I want to give feedback" request is handled the same way **anywhere** in the
bootcamp — it injects the whole feedback workflow (the pinned entry/exit banners, the
INV-067 append-and-verify rule, the INV-015 local-save-whatever-the-verdict rule, and
the INV-065 show-and-consent gate before anything is forwarded upstream).

Its trigger is a literal alternation of eight phrases, and it misses most of the ways
a person actually writes the request. Driven against the shipped hook inside a
scaffolded bootcamp project:

| prompt | result |
|---|---|
| `I have feedback` | HIT |
| `I have feedback on the mapping step` | HIT |
| `I have some feedback about module 5` | **miss** |
| `I'd like to give feedback` | **miss** |
| `can I give you some feedback` | **miss** |
| `I want to report a problem` | **miss** |
| `something is broken in this bootcamp` | **miss** |
| `report a bug` | HIT |
| `I found a bug` | **miss** |

Ten of thirteen natural paraphrases missed. The one-word gap between
`I have feedback` (hit) and `I have some feedback about module 5` (miss) is the shape
of the problem: the pattern is `i have feedback` as a contiguous string, so any
qualifier inside the phrase defeats it.

The consequence is a degradation rather than a break — the feedback workflow also
lives in `skills/bootcamp-onboarding/feedback.md` and in the explicit
`/bootcamp-feedback` command, so a miss means the assistant proceeds without the
injected guidance rather than refusing. What is actually lost on a miss is the
*guarantees*: the banners may not be presented, and the consent gate and
append-verify rules are not put in front of the model at the moment they apply.

## Root cause

`plugins/senzing-bootcamp/scripts/feedback-capture.py:30-33`:

```python
FEEDBACK = re.compile(
    r"bootcamp feedback|plugin feedback|power feedback|submit feedback|"
    r"provide feedback|i have feedback|report an issue|report a bug"
)
```

Every alternative is a fixed two-or-three-word collocation. There is no allowance for
an interposed qualifier (`some`, `a bit of`, `a little`), for the possessive/modal
forms (`I'd like to give`, `can I give you`), or for the noun on its own with a
different verb (`give feedback`, `share feedback`).

The verbosity branch (`:34-37`) has the same shape and the same gap — `be more concise`
hits, `can you be less wordy` misses — though with lower stakes, since verbosity is
re-adjustable at any time and carries no consent or durability guarantee.

## ⛔ The fix is NOT simply "add more words"

This is the part that matters, and it is why the pattern was probably written
narrowly in the first place.

The bootcamp spends Modules 5–7 having the bootcamper write and debug **their own
code**. In that context "I found a bug", "something is broken", and "this is wrong"
overwhelmingly refer to *the bootcamper's loader, mapper, or query* — not to the
plugin. Injecting the feedback workflow there is not a harmless false positive: it
prepends an instruction to open a feedback entry, present a banner, and gather
structured feedback on top of a turn where the bootcamper just wants their traceback
explained. That derails the module, and INV-054's reasoning applies by analogy — a
missed capture is far cheaper than a spurious one.

So the two halves of the vocabulary must be treated differently:

- **Unambiguous** — the word *feedback* in any construction, or an explicit reference
  to the bootcamp/plugin being at fault (`bug in the bootcamp`, `this plugin is
  broken`, `report a problem with the bootcamp`). These are safe to widen
  aggressively.
- **Ambiguous** — bare bug/broken/wrong/problem language with no
  bootcamp-or-plugin referent. These must **not** trigger the injection, and the
  current pattern is right to exclude them.

## Proposed change

1. Widen the unambiguous half. Replace the fixed collocations with patterns that
   allow a qualifier and the common verb forms — e.g. match `feedback` when it
   co-occurs with a giving/having/submitting verb anywhere in a short window, rather
   than as a fixed adjacent pair. `I have some feedback`, `I'd like to give
   feedback`, `can I give you some feedback`, `sharing feedback` should all hit.
2. Add the explicitly-attributed forms: bug/issue/problem/broken **when the same
   prompt also names the bootcamp, the plugin, a module, or "this tutorial"**. Keep
   the existing `report a bug` / `report an issue` for the case where the user has
   clearly framed it as a report.
3. Leave bare bug language alone, and record why in a comment at the pattern, so a
   future reader does not "fix" the gap by deleting the distinction. The comment is
   the durable half — the regex will be edited again, the reasoning will not be
   rediscovered.
4. Apply the same qualifier-tolerance to the verbosity branch (`less wordy`, `more
   brief`, `shorter answers`), where a false positive is cheap and self-correcting.

## Acceptance criteria

- [ ] Every prompt in the Problem table that names *feedback* in any construction
      triggers the injection, including `I have some feedback about module 5`,
      `I'd like to give feedback`, and `can I give you some feedback`.
- [ ] `I found a bug`, `something is broken`, and `this step is wrong` — with **no**
      bootcamp/plugin/module referent — still do **not** trigger it.
- [ ] The same words **with** a referent do trigger it: `I found a bug in the
      bootcamp`, `something is broken in this plugin`.
- [ ] The hook still emits nothing at all outside a bootcamp (no
      `config/bootcamp_progress.json`), which is the property that keeps it from
      touching unrelated Claude Code sessions.
- [ ] A repo-level test in `tests/` drives the hook's matcher over a table of
      hit/miss prompts covering all four rows above (stdlib only, no `plugins/`
      import — INV-108), negative-controlled by narrowing the pattern back and
      confirming it fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/feedback-capture.py` — the `FEEDBACK` and
  `VERBOSITY` patterns (`:30-37`) and the explanatory comment.
- `tests/test_feedback_capture_triggers.py` — new guard.

## Source

- Feedback: n/a — found by `/dry-run` phase 2 (hooks and bundled scripts), 2026-08-13
  (`Source: self-observed (assistant retrospective)`). The phase-2 procedure asks that
  this hook "inject guidance for a feedback prompt and stay silent on an unrelated
  one"; it stayed silent on a feedback prompt.
- Priority: Medium — the workflow is reachable by other routes (`/bootcamp-feedback`,
  `feedback.md`), so this loses guarantees rather than the feature. Raised above Low
  because the guarantees it loses include the INV-065 consent gate on the one path
  that can send data off the bootcamper's machine.
- MCP re-check: n/a (no Senzing fact) — this is local hook matching.
- Upstream: not applicable.
- Related specs: none.
