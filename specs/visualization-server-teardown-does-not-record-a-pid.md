# Visualization server teardown does not record a PID

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Truth Set visualization starts a background web server in Phase 1 and terminates it
in Phase 2, but nothing in between records **which process** to terminate. Phase 1
says to start it "as a background process you can stop later in Step 4"; Step 4 says
"Send a termination signal to the visualization web service process started in Phase
1 (2.3)". Neither says to capture the PID, and no checkpoint field holds one.

With no PID, the obvious identification is a pattern match on the script name:

```bash
pkill -f senzing_viz_server.py
```

That **matches the shell running it**. The pattern appears in the killing command's
own command line, so `pkill -f` signals that shell too. On this walk it terminated
the shell with exit code 144 mid-cleanup, before the purge had run — leaving the
Truth Set records loaded and the module half torn down, with the failure looking
like the purge script crashing rather than the kill hitting the wrong target.

This is on the documented path of a module whose teardown is explicitly
irreversible and order-sensitive: `phase2-close.md:80-83` states that "the purge is
the LAST action of this module" and that a missed step "becomes permanent".

## Root cause

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md:255-262`
  (2.3 "Start the live web app") starts the server and does not record its PID. It
  *does* record the port when 8080 is taken (INV-172, `:237`), so the module already
  has the idea of remembering a runtime fact about the server — just not this one.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md:88-92`
  (Step 4.3) says to signal "the process started in Phase 1" and to force-stop it
  after 5 seconds, with no means of naming it.
- `config/bootcamp_progress.json` has a `truthset_visualization.checks.web_service`
  entry, which is where a PID and port would naturally live, and it holds neither.

The same shape recurs in Query, Visualize and Discover, which re-points this server
at the bootcamper's own data.

## Proposed change

1. **Record the PID at 2.3, next to the port**, in
   `truthset_visualization.checks.web_service` — `{"status": "passed", "port":
   <port>, "pid": <pid>}`. Capturing it is one shell variable at launch (`$!` in
   bash, `$LASTEXITCODE`-adjacent `$proc.Id` in PowerShell), and it is the only
   unambiguous handle.
2. **Terminate by PID at Step 4.3**, falling back to a port-based lookup
   (`lsof -ti:<port>` / `Get-NetTCPConnection -LocalPort <port>`) when the PID is
   missing — a resumed session, or a server started before this change.
3. ⛔ **Warn against `pkill -f <script name>` explicitly**, with the reason: the
   pattern matches the invoking shell's own command line, so it signals the caller.
   Naming the trap is worth more than the alternative command, because `pkill -f` is
   what anyone reaches for first and the failure does not look like what it is.
4. **Verify the port is released** after termination rather than assuming it, and
   only then run the purge — the step already requires waiting 5 seconds, so make
   the check the exit condition instead of the wait.

## Acceptance criteria

- [ ] Phase 1, 2.3 records the server PID alongside the port in
      `truthset_visualization.checks.web_service`.
- [ ] Step 4.3 terminates by PID, with a documented port-based fallback.
- [ ] Step 4.3 names `pkill -f <script>` as unsafe and says why.
- [ ] Termination is confirmed by the port being free, before the purge runs.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The PowerShell equivalents are named, and the server may be written in any of
      the five languages, so the handle must be the process id rather than anything
      script-name-shaped.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  2.3 records the PID.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` —
  Step 4.3 terminates by PID, warns about `pkill -f`, and verifies the port.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/` — same
  pattern where it re-serves this app.

## Source

- Feedback: dry run phase 3, 2026-08-13/14 — hit during Step 4 teardown; `pkill -f
  senzing_viz_server.py` killed the invoking shell (exit 144) with the purge not yet
  run (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — recoverable, but it fires during an irreversible,
  order-sensitive teardown and misattributes its own failure.
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: `specs/visualization-contract-and-reference-server-disagree-on-record-fields.md`
  (same module)

## Invariants introduced

- `INV-223` — A module that starts a background server MUST record its process id beside its port, MUST terminate by that pid (or by a port lookup), and MUST confirm the port is free before any subsequent step; identifying the server by a command-line match is forbidden. (recorded in `specs/INVARIANTS.md`, 2026-08-14; approved by the maintainer.)
