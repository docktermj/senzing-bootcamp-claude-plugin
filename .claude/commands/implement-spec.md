---
description: Implement one or more specs from specs/ and record them in specs/IMPLEMENTED.md (maintainer tool).
argument-hint: "[spec-name ...] (filename without .md; omit to choose from unimplemented specs)"
---

Maintainer request: implement specs from the `specs/` directory.

Invoke the `implement-spec` skill and follow it end to end.

Spec(s) to implement: $ARGUMENTS

- If `$ARGUMENTS` is **empty**, run the skill's discovery mode: list every spec
  under `specs/` that is not yet recorded in `specs/IMPLEMENTED.md` and ask which
  one(s) to implement. Do not choose for the maintainer.
- If `$ARGUMENTS` is **given**, treat each token as a spec filename without the
  `.md` suffix (e.g. `stop-hook-issue` → `specs/stop-hook-issue.md`) and
  implement each.

For every spec: confirm its root cause in the code, **re-verify every Senzing fact
the spec asserts against the live Senzing MCP server before changing anything** (the
server ships independently of this plugin, so a spec's facts may be stale, already
fixed, or now contradicted — the server wins, and the deviation gets recorded), make
the change while honoring `specs/INVARIANTS.md`, verify it against the spec's
acceptance criteria, and only then record it in `specs/IMPLEMENTED.md`. Report what
the re-check found and the server version it ran against, and name any criterion that
could not be run in this environment rather than ticking it. Do not commit unless
asked.
