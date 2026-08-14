# Language gate does not say where its options render

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Bootcamp preparation's programming-language gate is the only ⛔ 👉 gate in the
module whose answer options are not written inside the pinned question, so nothing
decides whether the bootcamper sees

```text
1. Python — …
2. Java — …
👉 **Which programming language would you like to use for the bootcamp? Reply with a number:**
```

or

```text
👉 **Which programming language would you like to use for the bootcamp? Reply with a number:**

1. Python — …
2. Java — …
```

Both are defensible readings of the file, so the same gate can render differently
between runs. In the first form the question says "Reply with a number" while the
numbers sit above it, separated by the platform annotations — which on macOS and
Windows are several lines of per-language Docker routing, not the single Linux
sentence.

## Root cause

Steps 1, 2 and 3 each embed their numbered options inside the pinned blockquote,
immediately under the 👉 line:
`plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:106-111` (path),
`:145-151` (module selection), `:178-183` (verbosity).

Step 4 cannot do that, because its options come from `get_capabilities` at runtime
and so cannot be pinned. The file therefore splits them: "Present the MCP-returned
options as a **numbered list**" plus the platform annotation rules at `:279-296`,
and then the pinned question alone at `:298`. Read top to bottom that is
list-then-question; read against the pattern of Steps 1–3 it is
question-then-list.

`../bootcamp-onboarding/ground-rules.md:48-50` does not settle it. It says the
numbered choices "that are part of the question … are not 'after'" the 👉 — which
permits the options to follow the question but does not require it, and the same
paragraph's main rule ("anything meant to inform the answer goes BEFORE the 👉")
pulls the other way for a reader who treats a runtime-generated list as
informational rather than as part of the question.

n/a — no Senzing fact is involved. The option *content* is MCP-sourced and correct;
only its placement is unspecified.

## Proposed change

In `bootcamp-preparation/SKILL.md` Step 4, say where the list goes: the
MCP-returned options render **immediately beneath the 👉 question, as part of it**,
matching Steps 1–3, and the platform annotations that are not per-option (the
Linux "all languages install natively" sentence) stay **above** the 👉 with the
detected-platform line.

Keep the two kinds of prose distinct while doing it, since Step 4 mixes them:

- **Informational, goes before the 👉** — the detected-platform line, and any
  platform-wide statement such as the Linux one.
- **Per-option annotation, goes on its option** — the macOS/Windows Docker routing
  notes, which are already written per language at `:281-289`.

Add one sentence to `ground-rules.md:48-50` making the general rule explicit —
a 👉 question's answer options render directly beneath it, whether pinned or
generated at runtime — so the next runtime-generated numbered question does not
re-open this.

## Acceptance criteria

- [ ] `bootcamp-preparation/SKILL.md` Step 4 states that the MCP-returned options
      render directly beneath the 👉 question, and shows the resulting shape.
- [ ] Step 4 distinguishes platform-wide statements (before the 👉) from
      per-option annotations (on the option), for all four platform cases.
- [ ] `ground-rules.md` states the general placement rule for a 👉 question's
      answer options, covering runtime-generated lists as well as pinned ones.
- [ ] The pinned question text at `SKILL.md:298` is unchanged (INV-056).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — Step 4 says
  where the generated options render, and separates platform-wide prose from
  per-option annotations.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the
  conversation-protocol section states the general placement rule.

## Source

- Feedback: dry run phase 3, 2026-08-13 — observed while executing Bootcamp
  preparation Step 4 on Linux; the walk had to pick a rendering with nothing in
  the files deciding it (`Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none
