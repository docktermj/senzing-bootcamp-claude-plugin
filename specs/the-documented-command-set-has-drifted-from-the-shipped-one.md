# The user-facing docs claim three slash commands; the plugin ships five

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/commands/` ships **five** commands:

```text
/bootcamp-feedback  /bootcamp-note  /graduate  /package-bootcamp  /start-bootcamp
```

The two user-facing documents that describe them are both wrong, in two ways each:

- `docs/README.md:76` — prose: *"The plugin ships **three** slash commands."* A hardcoded
  count, wrong by two.
- `docs/README.md:80-83` — the table lists `/start-bootcamp`, `/bootcamp-feedback` and
  `/graduate`. **`/bootcamp-note` and `/package-bootcamp` appear nowhere in it.**
- `README.md:92` — *"(Or use the `/start-bootcamp` command. See [Bootcamp commands] for the
  other **two**.)"* A second hardcoded count, wrong by the same two.

⛔ **This is the class a prior audit already found and fixed once**: *"two of three shipped
slash commands documented nowhere"*. It has recurred because the fix was to write the missing
rows, not to pin the set.

The cost is entirely user-facing and silent. A Bootcamper reading the documentation cannot
discover that they can capture a note at any time, or that they can package the bootcamp to
move it to another machine — the second being the whole point of a feature added the same day.
Nothing errors; the docs simply describe a smaller plugin than the one installed.

## Root cause

**Nothing pins the documented command set to the shipped one, and both places state a count
in prose.**

Claude Code discovers `commands/*.md` by convention — `.claude-plugin/plugin.json` does not
enumerate them, correctly. So the shipped set is a directory listing, the documented set is two
hand-maintained lists, and no test compares them. Adding a command touches neither document
unless the author remembers.

⚠️ **The hardcoded counts are the sharper half.** A missing table row is an omission a reader
may not notice; *"the plugin ships three slash commands"* is a positive false statement that
reads authoritative, and *"the other two"* silently redefines itself as commands are added. This
is the stale-enumeration class the audit method lists (Step 7 class 4) applied to prose rather
than to an invariant — and the remedy is the same: state a property, not a count.

**Attribution, since it matters for whether this is a regression.** `/bootcamp-note` predates
the 2026-08-26 session and was already undocumented; `/package-bootcamp` was added by that
session (`specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`) and its
implementation did not update either document. So the defect is partly pre-existing and partly
new, and the count was already wrong before the new command made it wronger.

## Proposed change

**1. Add the two missing rows** to `docs/README.md`'s table — `/bootcamp-note` and
`/package-bootcamp` — each in the table's existing voice, with the plain-English equivalent the
other rows carry.

**2. Remove both hardcoded counts.** `docs/README.md`'s prose becomes a statement that does not
carry a number ("The plugin ships these slash commands…"), and `README.md:92` points at the
table without counting ("See [Bootcamp commands] for the rest.").

**3. Pin the set with a test.** A repo-level test that lists `plugins/senzing-bootcamp/commands/*.md`
and asserts every command appears in `docs/README.md`'s table. stdlib only (INV-108). ⛔ **Assert
both directions**: a documented command that no longer ships is equally a defect, and it is the
direction a delete-and-forget produces.

⚠️ **Do not assert a count in the test either.** A test that pins "five commands" fails on the
next legitimate addition and teaches whoever fixes it to bump a number — reproducing this defect
in the guard. Compare the two **sets**.

**4. Check `README.md` for other stale counts while there.** The same author habit produced two;
a third is cheap to look for and expensive to find later.

## Acceptance criteria

- [ ] `docs/README.md`'s command table lists all five shipped commands, each with its
      plain-English equivalent.
- [ ] Neither `docs/README.md` nor `README.md` states a hardcoded number of commands.
- [ ] A test compares the shipped command set against the documented set in **both** directions
      and names any command missing from either, deriving both sets rather than hardcoding them.
- [ ] The test asserts neither set is empty (INV-265) — an empty glob or a failed table parse
      would satisfy a set comparison trivially.
- [ ] Negative-controlled: removing a row fails the test, and adding a documented command that
      does not ship fails it too.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `docs/README.md` — the two missing rows; the prose count removed
- `README.md` — the "other two" count removed
- `tests/` — the set-comparison guard

## Source

- Feedback: n/a — found by `production-readiness-audit-2026-08-26b` checking Step 5's "every
  shipped surface is documented" against the command added earlier the same day;
  `Source: self-observed (assistant retrospective)`.
- Priority: **Medium** — user-facing and silent. Raised above Low because one of the two
  undocumented commands is the only route to a feature whose entire purpose is letting the
  Bootcamper take their work elsewhere, and because the same class was found and fixed before.
- MCP re-check: n/a (no Senzing fact). Command inventory and documentation are the plugin's own;
  no SDK method, flag, response shape or server behavior is asserted, and no absence is claimed.
- Upstream: not applicable.
- Related specs: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` (added
  `/package-bootcamp` without updating either document),
  `specs/bootcamp-notes-capture-and-recap-section.md` (added `/bootcamp-note`, likewise)
