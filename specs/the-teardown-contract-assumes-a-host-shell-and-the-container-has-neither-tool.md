# The teardown contract's primary route and its fallback both assume a host shell — on the Docker path the container the bootcamp builds has neither `ps`/`pkill` nor `lsof`

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At the visualization teardown gate, inside the bootcamp's own container:

```text
$ docker exec senzing-bootcamp pkill -f senzing_viz_server.py
exec: "pkill": executable file not found in $PATH
```

`ps` is absent too. **The Bootcamper had just been told the server would be stopped, and it kept
serving** — discovered only when port 8080 was probed and still answered 200.

Two things make this worse than a missing package.

**The failure is reported by the Docker runtime, not by the command.** `exec: "pkill": executable
file not found` comes from the container layer, so a teardown that checks the invoked command's exit
status is reading the wrong thing — and a teardown that treats any nonzero as "already stopped, fine"
records success. Matthew's observation is exact: *"a teardown that checks only for a clean exit would
record the server as stopped while it kept serving."*

**The teardown gate is bootcamper-facing and its entire promise is that the server is stopped.**
Silently leaving it running contradicts what the Bootcamper was just told, in the one step whose
output is a claim about state rather than a piece of analysis.

## Root cause

The plugin's process-identification rule is **already correct and already shipped** — and every route
it names is a host route.

`plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md:1097-1113`
and `module-07-query-visualize-discover/phase1-query-visualize.md:538-546`:

- ⛔ **Never** `pkill -f <script name>` — correct, and for a better reason than this one: the pattern
  matches the invoking shell's own command line (observed 2026-08-13, exit 144, killed the shell
  mid-teardown), and the server is written in the Bootcamper's chosen language (INV-090) so there is
  no script name to match in general.
- **Terminate by the pid captured at launch** (INV-223) — `$!` in a POSIX shell, `$proc.Id` from
  PowerShell's `Start-Process … -PassThru`.
- **Fall back to the port:** `lsof -ti:<port>` (Linux/macOS) or `Get-NetTCPConnection -LocalPort
  <port>` (PowerShell).
- **Confirm the port is free before saying the server is stopped** — poll up to 5 seconds, treat the
  port being free as the exit condition, never a sleep.

That last rule would have caught this run. It did not bind, and the reason is structural rather than
a lapse: **all four routes are written for a shell on the host.** On the Docker path the server runs
*inside* the container, and:

- `$!` and `$proc.Id` name a process in the **host's** namespace when the launch went through
  `docker exec`/`docker run` — the handle you capture is the client, not the server.
- `lsof` is not present in the container either, so the documented fallback fails the same way
  `pkill` did.
- `Get-NetTCPConnection` is PowerShell on Windows, which is the host, not the Linux container.

**The container is one the bootcamp builds itself**, so the missing tools are the plugin's to fix or
to work around. `module-02-sdk-setup/SKILL.md:426` prescribes it:

> Instead, run a plain Linux container (e.g., `debian:bookworm-slim`) and follow the `linux_apt`
> steps inside it so SQLite keeps working.

A slim base image ships neither `procps` (which provides `ps` and `pkill`) nor `lsof`. Confirm both
absences against the image at implementation time rather than from this spec.

**And the Docker path is not a corner.** Routing rules 1, 2 and 4
(`module-02-sdk-setup/SKILL.md:386-395`) send Python-on-macOS/Windows, every Intel Mac, and Windows
without Scoop into a container. A whole class of platforms reaches a teardown whose every documented
route is unavailable, and the plugin's own port-verification rule is the only thing standing between
that and a false claim — which is precisely the rule that cannot run when `lsof` is missing.

A working alternative was found on the run and is language-agnostic in the sense that matters: scan
`/proc/*/cmdline` and signal the matches from a program written in the Bootcamper's own language
(`python3` was present because the SDK needs it). `/proc` is guaranteed on Linux, which is what the
container always is, whatever the host.

## Proposed change

1. **State that the teardown contract has a container variant, and give it.** Where the server was
   launched inside a container, the pid to record is the pid **in the container's namespace**, and
   the fallback is a `/proc` scan rather than `lsof`. Both belong beside the existing host routes in
   `visualization-api-reference.md` → "Identifying the server process", not as a separate document.

2. **Verify by probing the port, never by trusting the kill's exit status** — and say why: on the
   container path a missing executable surfaces as a *runtime* error on the Docker layer, so the exit
   status being nonzero (or zero) says nothing about whether the server stopped. The existing
   port-poll rule is the right check; it needs a probe that works from where the teardown runs
   (an HTTP request to the mapped port from the host is the simplest, and it is what actually caught
   this).

3. **Decide the `procps` question explicitly rather than leaving it implicit.** Either add `procps`
   (and `lsof`) to the container build in `module-02-sdk-setup/SKILL.md`, or commit to the `/proc`
   route and say the image deliberately carries no process tools. Adding the packages is the smaller
   change and makes the existing host guidance work unmodified inside the container; the `/proc`
   route needs no image change and survives someone else's image. Pick one and make the other
   unnecessary — shipping both leaves the next reader guessing which the plugin relies on.

4. **Keep the ⛔ on `pkill -f`.** It is right for its own reason (INV-223, the self-match) and this
   finding does not soften it. A container that *has* `pkill` would still be the wrong way to
   identify this server.

5. **Say what the Bootcamper is told when teardown cannot confirm.** If the port still answers after
   the attempt, the gate must say the server is **still running** and how to stop it, rather than
   reporting the stop it promised. The module already has this shape for the "leave it running" branch
   (`phase1-query-visualize.md:532-536`); it needs it for the failed-stop branch too.

## Acceptance criteria

- [ ] The teardown contract names a container variant for both pid capture (container namespace) and
      the port fallback (`/proc` scan, not `lsof`).
- [ ] Teardown confirms the stop by probing the port, and the guidance states that a container exec
      failure is reported by the runtime, so the command's exit status does not answer the question.
- [ ] The `procps`/`lsof` decision is made once — either the packages are added to the container build
      or the `/proc` route is committed to — and no shipped file relies on the route not chosen.
- [ ] The ⛔ on `pkill -f` is unchanged.
- [ ] When the port still answers after a teardown attempt, the Bootcamper is told the server is
      still running and how to stop it, rather than being told it stopped.
- [ ] Verified on the Docker path with a real container: the teardown stops the server and the port
      is free, and a deliberately failing kill is reported as a failure rather than a stop.
- [ ] The `procps`/`lsof` absences are confirmed against the actual base image at implementation time,
      not carried from this spec.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      container is Linux whatever the host, and the scan is written in the Bootcamper's chosen
      language (INV-090).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — "Server lifetime" → "Identifying the server process" (`:1085-1117`) gains the container variant
  and the exit-status caveat
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the teardown rule (`:538-546`) and the failed-stop branch
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` — the parallel
  teardown (`:99-102`)
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the container build (`:426`), if
  the `procps`/`lsof` route is chosen
- `tests/` — coverage for the failed-stop reporting path

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew.md` → "Improvement: the SDK container image
  ships no `ps` or `pkill`, so the visualization teardown silently fails" (2026-08-18, Module Query,
  Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact) — the missing executables are a property of the Debian slim
  base image the bootcamp itself prescribes, and the teardown contract is entirely the plugin's.
  Confirmed in the codebase: `module-02-sdk-setup/SKILL.md:426` prescribes `debian:bookworm-slim`,
  and every process-identification route the plugin documents (`$!`, `$proc.Id`, `lsof -ti`,
  `Get-NetTCPConnection`) is a host route.
- Upstream: not applicable — the entry routes this `plugin`, and the container is one the bootcamp
  builds.
- Related specs: `specs/visualization-server-teardown-does-not-record-a-pid.md`,
  `specs/visualization-server-lifetime-and-teardown-gate.md`,
  `specs/container-lifecycle-hooks-assume-docker.md`,
  `specs/docker-container-lifecycle-teardown-and-resume.md`,
  `specs/the-viz-contract-never-states-the-bind-host-so-a-port-conflict-can-succeed.md`
