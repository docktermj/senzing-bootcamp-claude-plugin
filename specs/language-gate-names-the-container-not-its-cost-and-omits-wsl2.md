# The Python-on-Windows annotation names the container and not its price, and the routing rule it cites has no WSL2 branch at all

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A Bootcamper on Windows 11 chose Python at the Bootcamp preparation programming-language gate.
**Two modules later**, at SDK setup, platform routing revealed that the Senzing Python SDK is
Linux-only. Continuing with Python cost them a WSL2 install, a machine reboot, and a new Ubuntu
user account before any Senzing work could start. In their words: it wasted their time installing
WSL2 halfway through the bootcamp.

The annotation the gate showed was, verbatim, the one the rules prescribe:

```text
1. Python — runs via Docker (the SDK doesn't install natively on Windows)
```

That is true and it is not the information the choice needs. It names a **mechanism** where the
Bootcamper needs a **price**: install system-level virtualization software, obtain administrator
rights, reboot. Nothing at that gate inspects the machine for the prerequisite the annotation
implies, so a Bootcamper with neither Docker nor WSL2 installed is told "runs via Docker" and
discovers what that means at Step 3 of Module 2.

**Two modules of sunk cost is the whole defect.** This is a reversible choice presented as a
costless one, at the only point where reversing it is free.

## Root cause

Three sites, and the third is the one that makes the annotation wrong rather than merely thin.

1. **The annotation rule prescribes the mechanism, not the cost.**
   `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md:301`:

   > **Windows:** per-option — Python runs via Docker; other languages need Scoop, else Docker.
   > (rules 1 and 4)

   and the worked shape at `:330` — `1. Python — runs via Docker (the SDK is Linux-only)`. The
   rule is satisfied literally and not in effect: it discloses the routing outcome and none of
   what the outcome costs.

2. **Nothing at the gate checks whether the container runtime exists.** The step's instructions
   (`SKILL.md:260-307`) call `get_capabilities` for the language set and then present it. There is
   no probe for Docker or WSL2 — so the annotation asserts a route whose availability was never
   established, on the one platform where it is least likely to already be there.

3. **The routing rule the annotation cites offers Docker only — WSL2 is not in it.**
   `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:386-387`, routing rule 1:

   > Chosen language is Python AND OS is macOS or Windows → **`platform='docker'`**. The Python
   > SDK is only supported on Linux; on macOS/Windows it must run in a container.

   The Bootcamper was offered WSL2 and took it, resolving the platform to `linux_apt` — an outcome
   rule 1 does not describe. And the preparation skill's own prose at `SKILL.md:274-276` already
   says the route is "Docker **or WSL2** on macOS/Windows", then points at annotation rules that
   name only Docker. The plugin holds both halves and they disagree.

**The live server states both routes, and always has as far as this triage can see.**
`sdk_guide(topic='install', platform='windows', language='python')` on **server 1.33.0, verified
2026-08-21**, returns exactly one `compatibility_notes` entry:

> "The Senzing Python SDK is ONLY supported on Linux. It is NOT supported on macOS or Windows —
> even if pip install appears to succeed, it is unsupported and may produce runtime errors. You
> have two options: (1) Pick a different language — Java and C# are officially supported on macOS
> and Windows; Rust and TypeScript are community-supported on all platforms. (2) Pick a different
> environment — **use Docker or WSL2** to run Python inside a Linux container."

So the server offers **two** environment routes and **two** language alternatives, and the
plugin's Windows annotation relays one environment route and no language alternative. The
Bootcamper's actual choice — keep Python, install WSL2 — is the server's own second option,
reached in spite of the plugin's text rather than because of it.

The server does not state the *cost* of either route (admin rights, reboot, a new Linux user), and
it should not have to: that is bootcamp-side framing of a decision the bootcamp owns.

⚠️ **Adjacent server inaccuracy, recorded and deliberately not acted on here.** The same note on
`platform='macos_arm'` reads "To use Python, switch to Docker or WSL2 (Linux container)" — WSL2
does not exist on macOS. Do not relay that clause verbatim on a Mac. Filed as an observation, not
part of this spec's change.

## Proposed change

1. **Say what the choice costs, at the gate.** Replace the Windows and macOS Python annotations
   with one that names the price rather than the mechanism — that choosing Python on this platform
   means installing and running a Linux environment (Docker Desktop or WSL2), which needs
   administrator rights and, for WSL2, a reboot. Keep it to one clause on the option; the gate is
   a numbered list, not a briefing.

2. **Relay both environment routes, because the server states both.** The annotation must not
   name Docker alone. Take the route list from
   `sdk_guide(topic='install', platform=<detected>, language='python')` at gate time rather than
   from this spec (INV-080), and reconcile the macOS case against the WSL2-on-macOS error above.

3. **Give routing rule 1 the WSL2 branch it is missing.**
   `module-02-sdk-setup/SKILL.md:386-387` must describe both outcomes — container (`docker`) or a
   WSL2 Linux environment resolving to `linux_apt` — since the second is what a Bootcamper who
   prefers a native-feeling toolchain will pick, and the module already has to handle it. The
   preparation skill's `:274-276` prose and the annotation rules at `:296-306` must then agree.

4. **Probe for the prerequisite before the annotation claims it.** At the gate, check whether a
   container runtime or WSL2 is already present, and annotate accordingly — "already available on
   this machine" versus "needs installing first". A silent, best-effort check (INV-095); never a
   question, never a blocker, and on failure fall back to the unqualified cost statement rather
   than asserting availability. This is what turns a generic warning into a decision the
   Bootcamper can actually make.

⛔ **Do not turn this into a recommendation against Python.** The gate presents the server's
language set and the Bootcamper chooses; the change is disclosure, not steering (INV-006).

## Acceptance criteria

- [ ] On Windows and macOS, the Python option's annotation states the cost of the choice
      (installing a Linux environment, administrator rights, and — for WSL2 — a reboot), not only
      the routing mechanism.
- [ ] The annotation names every environment route the server's `compatibility_notes` returns for
      the detected platform, and the WSL2 clause is suppressed on macOS.
- [ ] `module-02-sdk-setup/SKILL.md` routing rule 1 resolves both a container platform and a WSL2
      Linux platform, and no shipped file says the route is Docker only.
- [ ] The gate performs a silent presence check for the container runtime / WSL2 and reflects the
      result in the annotation; a failed check degrades to the unqualified cost statement and never
      asserts availability.
- [ ] A guard asserts that no shipped file annotates the Python option on Windows or macOS with a
      mechanism and no cost.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — annotation rules (`:296-306`),
  the worked shape (`:330`), and the `:274-276` prose that already names WSL2; add the presence
  check to the step
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — routing rule 1 (`:386-387`)
  gains the WSL2 outcome
- `tests/` — new guard for the cost-vs-mechanism annotation

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Improvement: Python-on-Windows
  unsupported, discovered only at SDK setup" (2026-08-18, Module SDK setup;
  `Source: bootcamper-reported`)
- Priority: High
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces, and widens**.
  `sdk_guide(topic='install', platform='windows', language='python')` confirms the Linux-only
  exclusion and names **two** environment routes, "use Docker or WSL2"; the plugin relays one.
  `sdk_guide(topic='install', platform='macos_arm', language='java')` carries the same note with
  the WSL2-on-macOS error recorded above. No absence is asserted against the server here.
- Upstream: already sent 2026-08-18 (per the entry's `Upstream:` field — the OS-by-language matrix
  gap in Senzing's v4 System Requirements page). No follow-up: nothing has been learned since that
  Senzing could act on.
- Related specs: `specs/language-gate-does-not-say-where-its-options-render.md`,
  `specs/auto-detect-platform.md`, `specs/senzing-python-sdk-must-not-be-pip-installed.md`
