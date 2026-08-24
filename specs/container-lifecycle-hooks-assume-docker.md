# Container lifecycle names Docker unconditionally, so the hooks are inert and misleading on any other runtime

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-101 requires every container the bootcamp starts to be recorded and acted on at session
boundaries. The implementation assumes the runtime is Docker at three points, and only one of them
is a real dependency:

- `scripts/docker_lifecycle.py:45` reads the `docker_containers` list from
  `config/bootcamp_progress.json`.
- `docker_available()` gates every action on `shutil.which("docker")`.
- `stop_started_containers()` (`:72`) issues `docker stop`, and `resume_summary()` (`:123`) emits
  **"This bootcamp uses Docker container(s): "**.

A bootcamp that ran the Senzing runtime under **Apple's `container` CLI** — chosen because Docker
Desktop could not be installed non-interactively, since it needs interactive administrator
privileges an agent cannot supply — has no path here. The container was recorded under the
Docker-shaped key with `runtime: container` noted alongside, and the result was a persistent,
confidently-worded message at every session boundary naming the wrong tool:

> This bootcamp uses Docker container(s): senzing-bootcamp (unknown)

with a restart offer that would be attempted using a binary not present on the machine. Nothing
broke — the container survived the resume on its own — but the hook's report and its remediation
were both wrong, at every boundary, for the whole run.

**Why this platform matters.** macOS Apple Silicon is first-class in Module 2's routing (INV-001),
and Apple's `container` is a reasonable choice there precisely when Docker Desktop cannot be
installed. So the bootcamper who most needs the lifecycle tracking is the one it silently does
nothing for.

**Half the plumbing already tolerates the fix.** `_load()` at `:55-59` appends dict entries whole —
`out.append(entry)` — so a `runtime` key recorded alongside `name` already survives storage and
reaches the consumer. Only the dispatch and the wording ignore it.

## Root cause

The lifecycle was specified and built for Docker, and the runtime was encoded in three places that
each looked like a constant at the time: the progress key name, the availability probe, and the
user-facing string. Nothing recorded *which* runtime started a container because there was only one.

`shutil.which("docker")` returning `None` is indistinguishable, to the hook, from "no containers to
manage" — so the failure is silent by construction. INV-101's own text requires that all Docker
interaction warn-and-continue when `docker` is absent, which is exactly what happens; the hook is
behaving as specified. The specification is what assumes one runtime.

## Proposed change

1. **Record the runtime with the container.** Store `{"name": …, "runtime": "docker" | "container" |
   "podman"}` when the container is registered in Module 2. Storage already carries it (`:55-59`);
   Module 2's two registration sites (`module-02-sdk-setup/SKILL.md:383`, `:827`) are what must write
   it.
2. **Dispatch on the recorded runtime.** Replace the single `docker_available()` probe with one that
   resolves the CLI for the entry's runtime, and issue that CLI's stop command. Keep the
   warn-and-continue contract exactly as INV-101 requires — an unavailable CLI must still never block
   a hook.
3. **Word the message with the runtime actually used.** "This bootcamp uses Docker container(s)" is
   wrong for a `container` or `podman` runtime, and the wrongness is what makes the message
   untrustworthy rather than merely unhelpful.
4. **Default an entry with no `runtime` to `docker`**, so existing `config/bootcamp_progress.json`
   files from earlier runs keep working unchanged.
5. **Keep the `docker_containers` key name.** Renaming it to `containers` would read better and
   would break every in-flight bootcamp's progress file for a cosmetic gain. Note the mismatch in a
   comment instead — the bootcamper's own suggestion allowed for this.

⚠️ **Do not add a new dependency or probe for runtimes the bootcamp never starts.** The set is
whatever Module 2 can actually launch; adding speculative runtimes creates guidance nobody has
exercised, and INV-101 requires each to degrade gracefully.

⚠️ **Do not make the hook install or switch runtimes.** It stops and reports. A hook that reaches
for a different CLI than the one that started the container is how a bootcamper loses a container
they were told was stopped.

## Acceptance criteria

- [ ] A container is recorded with its runtime at both Module 2 registration sites (`:383`, `:827`),
      verified by **opening that file** rather than inferred from the script change (INV-182).
- [ ] `docker_lifecycle.py` dispatches stop/resume on the recorded runtime and resolves that
      runtime's CLI, not `docker` unconditionally.
- [ ] The session-boundary message names the runtime actually recorded; no message says "Docker" for
      a non-Docker entry.
- [ ] An entry with no `runtime` key still behaves exactly as today (treated as `docker`), so
      existing progress files are unaffected — asserted by a test with a legacy-shaped entry.
- [ ] Every path still warns-and-continues when the runtime's CLI is absent and never blocks a hook
      (INV-101, INV-052).
- [ ] The `docker_containers` key name is unchanged, with the reason recorded.
- [ ] Tests cover: a `docker` entry, a non-`docker` entry, a legacy entry with no runtime, and an
      entry whose CLI is absent — the last asserting the hook still exits cleanly.
- [ ] **Not runtime-verified:** Apple's `container` CLI is not present in this environment (Linux),
      so dispatch to it cannot be exercised here. The tests must therefore stub the CLI lookup rather
      than requiring the binary, and the disclosure is recorded in the ledger entry.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/docker_lifecycle.py` — `_load()` normalization (`:55-59`),
  `docker_available()`, `stop_started_containers()` (`:72`), `resume_summary()` (`:123`).
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the two registration sites
  (`:383`, `:827`).
- `tests/` — the four cases above.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "container-lifecycle tracking assumes Docker, so
  the SessionStart/SessionEnd hooks are inert for a bootcamp running on Apple's `container` CLI"
  (2026-07-27, Module: SDK setup — surfacing at every session boundary; Priority: Medium;
  `Source: self-observed (assistant retrospective)`).
- Priority: **Medium**, as filed. Nothing broke in the reported run, but the message is wrong at
  every session boundary and the remediation would call a missing binary — and a bootcamper who did
  need the container stopped would not get it.
- MCP re-check: **n/a (no Senzing fact), server 1.32.3, 2026-07-31.** Container lifecycle is entirely
  plugin-side — a progress key, a CLI probe and a hook message. No MCP tool owns any of it and none
  was called; stated rather than skipped per INV-080.
- Upstream: not applicable (plugin-side, as the entry itself routes it).
- Related specs: `specs/docker-container-lifecycle-teardown-and-resume.md` (INV-101's source, which
  established the Docker-only design this generalizes).

## Deviations from this spec, and why (2026-08-11)

Implemented as specified except for the following, all recorded here so the spec's text is
not mistaken for what shipped.

1. **Container state is probed only for runtimes with a verified `ps` interface.** The spec
   says to dispatch on the recorded runtime without distinguishing the *stop* command from
   the *state* read. `<cli> stop <name>` is common to all three runtimes, but
   `ps -a --filter name=^X$ --format '{{.Names}}\t{{.State}}'` is Docker's interface, shared
   by podman and **not** by Apple's `container`, whose list syntax differs. Rather than issue
   a command whose syntax this plugin has not verified — and which could only fail — the
   probe is restricted to `STATE_PROBE_RUNTIMES = ("docker", "podman")` and any other runtime
   reports state `unknown`. Evidence: Apple's `container` CLI is absent on this Linux
   development machine, so its list syntax could not be verified here; guessing it would ship
   exactly the kind of unexercised guidance the spec's first ⚠️ forbids.
2. **The runtime set is a closed allowlist, and an unrecognized runtime is reported but never
   executed.** The spec names `docker | container | podman`; the implementation additionally
   refuses to resolve a CLI for any other recorded string, so a value in
   `config/bootcamp_progress.json` cannot become a binary the hook invokes. Such an entry is
   still surfaced in the resume message under the name it was recorded with, so the guide can
   act on it. Asserted by `tests/test_container_lifecycle_runtimes.py`
   (`test_unknown_runtime_is_never_executed`).
3. **`docker_available()` was removed rather than kept alongside the new probe.** The spec
   says to replace it; a grep of the repo confirmed no consumer outside
   `docker_lifecycle.py` itself, so it was not retained as an alias. `runtime_cli(runtime)` is
   its replacement.
4. **Citation drift in the spec's Problem section, substance confirmed.** The spec attributes
   `out.append(entry)` to `_load()` at `:55-59`; the function is actually
   `tracked_containers()` and the append was at `:53`. The claim it supports — that dict
   entries are appended whole, so a `runtime` key already survives storage — was correct.
   Entries are now normalized through a copy, so `runtime` is always resolved on read while
   `image`/`purpose` and any other recorded keys are preserved.

**Not runtime-verified:** dispatch to Apple's `container` is asserted at the
command-construction level with a stubbed CLI lookup, not against the real binary, which is
not available on Linux. The spec's own acceptance criteria anticipated this and required the
stub.

## Invariants introduced

- `INV-195` — Every container the bootcamp starts MUST be recorded with the `runtime` that
  started it, and every lifecycle action MUST dispatch on that recorded runtime rather than
  assuming Docker; an entry with no `runtime` is treated as `docker`, a runtime outside the
  recorded set is reported but never executed, and no session-boundary message may name a
  tool that did not start the container. Generalizes INV-101 (recorded in
  `specs/INVARIANTS.md`, maintainer-approved 2026-08-11).
