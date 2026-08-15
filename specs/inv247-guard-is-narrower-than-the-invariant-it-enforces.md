# The INV-247 guard is narrower than the invariant it enforces

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`tests/test_no_host_control_is_offered_as_a_question.py` is the registered enforcer of **INV-247**
(no session- or host-level control is presented as a bootcamp question). Its docstring discloses one
limit clearly and in a ⛔ block — that it cannot detect a question improvised at runtime, because the
reported defect existed in no file. It does **not** disclose a second limit, and that one is
invisible to a reader who trusts the first disclosure as complete.

The invariant governs a **class**: "a session- or host-level control". The guard tests a **closed
vocabulary** of eight literals:

```python
HOST_CONTROL = re.compile(
    r"(?i)auto[-\s]?mode|auto[-\s]?accept|permission[-\s]mode|plan[-\s]mode"
    r"|fast[-\s]mode|bypass[-\s]permission|background[-\s]task|/compact\b|/loop\b")
```

A pinned 👉 question offering any host control **not on that list** — a future `/thinking` toggle, a
renamed affordance, a control that ships after this guard was written — passes the guard while
breaching the invariant. The failure mode is exactly the one this skill ranks third by value: *a
guard narrower than the invariant it claims to enforce; read what a guard asserts, not its name.*

## Root cause

`specs/a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper.md` (implemented 2026-08-15,
commit `a60b669`) asked for a guard asserting "no 👉 line in any shipped file … names a host control
other than `/model` and `/effort`". "Names a host control" is only testable as a vocabulary match, so
the implementation is a faithful reading of the spec — and the resulting gap was never stated.

Two things make the omission worth correcting rather than shrugging at:

1. **The docstring's existing ⛔ disclosure sets an expectation of completeness.** It names one limit
   in emphatic terms and reads as *the* caveat. A reader who meets it reasonably concludes the
   remaining assertions are sound for the class the invariant names. That is the pattern
   `specs/coverage-reports-count-known-non-defects-as-hits.md` exists to stop, applied to this
   guard's own self-description.
2. **The list is the kind that rots silently.** It is a closed enumeration of third-party interface
   vocabulary — controls owned by the Claude Code CLI, which ships independently of this plugin —
   with nothing in an offline suite (INV-108) able to notice a new one. `conformance.py enumerations`
   does not flag it, because it scans `INVARIANTS.md`, not test source.

⚠️ **INV-247 itself is fine and needs no change.** Its governing clause is the class term
("a session- or host-level control"); the eight literals follow an em-dash as illustration, and the
sentence still binds a control that is not listed. The defect is in the guard's silence about the
gap between the two, not in the rule.

## Proposed change

**Do not attempt a complete list — there isn't one.** The controls belong to a host that ships
separately, so any enumeration is a snapshot. Two cheap changes that keep the guard honest:

1. **State the vocabulary limit in the docstring**, beside the runtime limit already there: the
   guard matches a fixed list of control names, so a control absent from that list passes it; the
   list is a snapshot of the Claude Code CLI's affordances as of 2026-08-15, and a green run is
   evidence about those names only.
2. **Name the list as the thing to extend** when a new host control appears, and add a test asserting
   the docstring carries both disclosures — so a later edit that broadens `HOST_CONTROL` without
   touching the caveat, or trims the caveat, fails.

Optionally, assert the positive direction the invariant actually cares about, which does not expire:
that the **only** pinned questions asking the bootcamper to operate a Claude-interface control are
the four model/effort forms. `test_the_model_effort_switch_is_still_asked_as_a_question` already
half-does this; making it an exact-set check would catch a new interface question regardless of the
vocabulary it uses. That is the stronger fix and is the one to prefer if only one is taken.

## Acceptance criteria

- [ ] The guard's docstring discloses **both** limits: that it cannot see a runtime-improvised
      question, and that it matches a closed, dated vocabulary of control names.
- [ ] A test fails if either disclosure is removed — **negative-controlled**, mutation verified to
      land, then reverted.
- [ ] `HOST_CONTROL` carries a comment naming it as a snapshot to extend, with its date.
- [ ] If the exact-set check is adopted: a new pinned 👉 question asking the bootcamper to operate any
      Claude-interface control fails the guard **even when its wording appears in no vocabulary list**.
- [ ] INV-247 is unchanged — the invariant is correct; only the guard's self-description moves.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_no_host_control_is_offered_as_a_question.py` — docstring disclosure, a dated comment on
  `HOST_CONTROL`, and (preferred) the exact-set assertion.
- `tests/test_guard_disclosures_survive.py` — new, or the assertion added to the file above.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15
  (`Source: self-observed (assistant retrospective)`). Found by forward-sweeping INV-247, an
  invariant registered earlier in the same session by the auditor.
- Priority: **Low**. No shipped 👉 question breaches INV-247 today — all 96 pinned questions across
  24 files were checked, and the only interface controls offered are the four sanctioned model/effort
  forms. This is guard hygiene against a future breach, not a live defect.
- MCP re-check: **n/a (no Senzing fact).** The plugin's conversational layer and its own test source;
  no MCP tool was called and no Senzing claim is asserted. Server **1.32.9** recorded this session
  (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper` (the
  implementation this critiques), `coverage-reports-count-known-non-defects-as-hits` (the
  over-claiming-guard pattern), and INV-247, INV-108, INV-246.
