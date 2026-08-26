# `README.md` tells the Bootcamper Claude Code has two interfaces; INV-098 handles four

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`README.md:44`, in the install walkthrough, before anything else:

```text
This is a Claude Code plugin.
Claude Code has two interfaces you can run it in.
Pick either:

- **Claude Desktop** — Claude Code inside the desktop application; …
- **Claude Code CLI** — Claude Code in a terminal; …
```

The plugin's own ruleset disagrees. **INV-098** requires the module/graduation-start
model/effort nudge to adapt to *four* contexts — *"on the Claude Code CLI it presents the exact
`/model` and `/effort` commands (INV-063); in **Claude Desktop**, the **Claude web app**, or a
**Claude IDE extension** …"*.

⛔ **So the plugin has interface-specific behavior for two contexts its own front door says do
not exist.** A Bootcamper running Claude Code in the web app or in a VS Code / JetBrains
extension reads "two interfaces, pick either", finds neither describes what they are using, and
has no install path — while the plugin, once started, would have handled them correctly.

This is not a stale count that merely undercounts. *"Pick either"* is an instruction, and it is
unanswerable for those readers.

## Root cause

**A count in prose, in the one file with no test over it, describing something outside the
plugin's control.**

The install walkthrough was written when two paths were offered and states that as a fact about
Claude Code rather than as the scope of the walkthrough. INV-098 was later written against the
fuller set — correctly, since the nudge has to work wherever the Bootcamper is — and nothing
connects the two: `README.md` is user-facing prose, INV-098 is the ruleset, and no test compares
a claim in one against an enumeration in the other.

⚠️ **The distinction that makes this fixable without inventing facts:** the walkthrough may
legitimately *support* two installation paths. What it may not do is assert that two is all
there are. Those are different sentences, and only the second is wrong.

⛔ **Do not "fix" this by adding walkthrough sections for the web app and IDE extensions** unless
someone has actually installed the plugin that way. The plugin cannot assert an install path it
has not verified (the same discipline INV-080 applies to Senzing facts, here applied to the
host). Scoping the sentence honestly is the fix; adding unverified instructions is a new defect.

## Proposed change

**1. Say what the walkthrough covers, not what exists.** Replace the count with scope — that the
walkthrough covers Claude Desktop and the Claude Code CLI, and that the plugin works wherever
Claude Code runs. One sentence, no number.

**2. Name the other contexts without inventing install steps for them.** A short line noting that
Claude Code also runs in the Claude web app and in IDE extensions, and that a Bootcamper there
installs the plugin the same way their client installs plugins, is enough to stop *"pick either"*
being unanswerable. ⚠️ State plainly if those paths are unverified rather than implying they were
tested (INV-111/INV-163's disclose-rather-than-imply discipline).

**3. Reconcile the direction, not just the text.** INV-098's enumeration is the authority here
because it is the one the plugin's behavior is built against. If it is itself incomplete, that is
a separate finding — but it is the fuller list, so `README.md` moves toward it.

## Acceptance criteria

- [ ] `README.md` no longer asserts a number of Claude Code interfaces.
- [ ] `README.md` no longer instructs the reader to "pick either" from a set that excludes
      contexts INV-098 handles.
- [ ] The Claude web app and IDE extensions are acknowledged, with any unverified install path
      disclosed as unverified rather than presented as tested.
- [ ] A test asserts `README.md` states no count of Claude interfaces, and that every context
      INV-098 enumerates is at least named somewhere in the user-facing docs. ⚠️ Derive the
      context list from INV-098's text rather than hardcoding it, so the guard cannot go stale in
      the same way the prose did.
- [ ] Negative-controlled: restoring the "two interfaces" sentence fails the test.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `README.md` — the interface sentence and the "pick either" instruction
- `tests/` — a guard on the count and on INV-098's contexts being named

## Source

- Feedback: n/a — found by `production-readiness-audit-2026-08-26b` while sweeping the
  user-facing docs for other hardcoded counts, which
  `specs/the-documented-command-set-has-drifted-from-the-shipped-one.md`'s proposed change 4
  asked for. That sweep found this; `Source: self-observed (assistant retrospective)`.
- Priority: **Medium** — user-facing, and it is an instruction rather than a description: a
  Bootcamper in the web app or an IDE extension cannot follow it. Not High only because such a
  reader can still install the plugin the way their client installs any plugin.
- MCP re-check: n/a (no Senzing fact). The subject is the Claude Code host's interfaces and the
  plugin's own ruleset; no SDK method, flag, response shape or server behavior is asserted, and no
  absence is claimed.
- Upstream: not applicable — not a Senzing MCP server matter.
- Related specs: `specs/the-documented-command-set-has-drifted-from-the-shipped-one.md` (the sweep
  that surfaced this, and the same hardcoded-count-in-prose habit)
