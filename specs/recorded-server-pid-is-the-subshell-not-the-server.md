# The recorded visualization-server pid can be the subshell, not the server

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Truth Set visualization records the visualization server's process id at launch (Phase 1, 2.3) and
uses it at teardown (Phase 2, Step 4) as "the only unambiguous handle on the server". On a phase-3
walk (2026-08-22) the recorded pid was **not the server's**: `kill <recorded pid>` returned success,
the process disappeared, and port 8080 stayed bound by the still-running server.

    $ kill 963346          # the recorded pid — exits 0
    port 8080 STILL BOUND after 5s
    $ ss -ltnp | grep 8080
    LISTEN 127.0.0.1:8080  users:(("python3",pid=963351,fd=6))

The cause is composition. Step 2 requires the project environment to be sourced before anything
that touches the Senzing library:

> "run everything with the project env sourced … `source src/scripts/senzing-env.sh` on
> Linux/macOS" — `phase1-visualization.md:226-229`

and 2.3 gives the launch as a bare backgrounded command whose `$!` is therefore the server:

> `python3 <viz-server-path> … --port 8080 &` — `phase1-visualization.md:344-350`, with
> "⛔ **Record the process id along with the port** — `$!` in a POSIX shell as above"

Composed the obvious way — `. src/scripts/senzing-env.sh && python3 <server> … &` — the `&`
applies to the **whole `&&` list**, so the shell backgrounds a subshell, `$!` names that subshell,
and the server is its child with a different pid. Killing the recorded pid orphans a running
server holding the port.

## Root cause

Two correct instructions in different sections that produce a wrong value when combined, and
nothing in either section flags the interaction. The pid is described as unambiguous precisely
because the server may be written in any of the five languages (INV-090), so there is no script
name to match on and no other handle — which makes a silently-wrong pid worse than a missing one:
`phase2-close.md`'s fallback ("If no pid was recorded … find the listener by the recorded port")
triggers on **absence**, and this failure presents as **presence**.

What contained it is already in the file, and it worked exactly as designed:

> "**Confirm the port is free** rather than assuming it: poll it for up to 5 seconds" —
> `phase2-close.md:113`, and the docker branch's "The kill's exit status is not evidence the server
> stopped; the port is."

That poll is what turned a silent orphan into a visible failure, after which the port-based route
(`lsof -ti:8080` → pid 963351) stopped the real server and the port freed immediately.

No Senzing fact is involved; this is shell semantics plus the plugin's own instructions.

## Proposed change

At 2.3, make the launch shape one the composition cannot break, and say why:

- Source the env script in the **current** shell first, as its own statement, then background only
  the server command, so `$!` is the server:

      . src/scripts/senzing-env.sh
      python3 <viz-server-path> … --port 8080 &
      VIZ_PID=$!

- Add one line stating the hazard: if the launch is written as `A && B &`, `$!` is the subshell,
  not the server — record the pid only from a line whose sole backgrounded command *is* the server.
- In `phase2-close.md` Step 4, extend the fallback from "no pid was recorded" to "the recorded pid
  is gone but the port is still bound": that is the same port-based lookup, and it is the case that
  actually occurred.

The PowerShell counterpart (`Start-Process … -PassThru`, `$proc.Id`) does not have this hazard and
needs no change.

## Acceptance criteria

- [ ] `phase1-visualization.md` 2.3 shows the env-sourcing as a separate statement from the
      backgrounded launch, and states that `$!` after `A && B &` names the subshell.
- [ ] `phase2-close.md` Step 4's port-based fallback covers a recorded pid that is dead while the
      port is still bound, not only a missing pid.
- [ ] A test asserts 2.3's launch example does not chain the env-sourcing into the backgrounded
      command with `&&`.
- [ ] The port-confirmation poll stays mandatory before the purge — it is what detected this.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — 2.3
  launch shape and the `$!` hazard note.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` — Step 4
  fallback wording.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — "Server lifetime" → "Identifying the server process", if it restates the launch shape.
- `tests/` — a guard on 2.3's launch example.

## Source

- Feedback: `/dry-run` phase 3, Truth Set visualization teardown (2026-08-22;
  `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact — shell process semantics and plugin instructions)
- Upstream: not applicable
- Related specs: `specs/a-step-names-what-to-select-without-naming-the-route.md`
