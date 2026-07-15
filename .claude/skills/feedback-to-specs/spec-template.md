# Spec template

Copy this structure into each generated `specs/<kebab-case-title>.md`. Keep it
terse and developer-facing, matching the existing specs. Delete guidance in
angle brackets. Use "fix the following issue" for bugs and "implement the
following improvement" for enhancements.

```markdown
# <Title>

Maintain the invariant conditions in @invariants.md and <fix the following issue | implement the following improvement>:

## Problem

<What the bootcamper experienced. Include the verbatim error/output when the
feedback provided one — it is the clearest repro signal.>

## Root cause

<The confirmed cause, grounded in code, citing file:line. If unconfirmed, write
"Unverified — needs investigation" and list what to check.>

## Proposed change

<Concrete change(s). For a fix: what to change and why it resolves the root
cause. For a feature: what to add and where it fits the module/flow.>

## Acceptance criteria

- [ ] <Observable, testable outcome that proves the item is resolved.>
- [ ] <Any additional outcome.>
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @invariants.md).

## Affected files

- `path/to/file` — <what changes and why>

## Source

- Feedback: `<feedback file path>` → "<entry title>" (<date>, Module <n>)
- Priority: <High | Medium | Low | pending>
- Related specs: <specs/<file>.md, or "none">
```
