# macOS strips `DYLD_*` through protected launchers, so the backgrounded visualization server cannot find the native library

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Starting the visualization server as a background process via `nohup` failed with:

```text
java.lang.UnsatisfiedLinkError: no Sz in java.library.path
```

**despite `DYLD_LIBRARY_PATH` being correctly set in the parent shell.** macOS System Integrity
Protection sanitizes `DYLD_*` out of the environment whenever a **protected** binary execs a child,
and `/usr/bin/nohup`, `/usr/bin/env` and `/bin/bash` are all protected. Confirmed directly on the
reporting workstation:

```text
$ echo $DYLD_LIBRARY_PATH              -> /opt/homebrew/opt/senzing/er/lib:...
$ bash -c 'echo $DYLD_LIBRARY_PATH'    -> (empty)
$ nohup bash -c '...'                  -> (empty)
```

⚠️ **Foreground batch programs worked throughout, which is what makes it confusing.** They are direct
children of the shell that exported the variable, so nothing is stripped. The failure appears only
when a process is **backgrounded or wrapped** — which is exactly what the bootcamp asks for.

**The plugin already gets the hard part right, and that is why this is a narrow gap rather than a
rewrite.** `module-02-sdk-setup/SKILL.md:793-799` states the load-bearing fact correctly:
`DYLD_LIBRARY_PATH` must be set at the shell level before the JVM starts, and `-Djava.library.path`
**alone is insufficient** — *"the opposite of the natural guess."* `phase1-visualization.md:355-370`
correspondingly sources the env script on its own line in the current shell and backgrounds with a
plain `&`, which is correct and does **not** trip SIP.

**What is missing is the warning about how the variable is lost.**

1. `DYLD` appears in exactly **one** shipped file — `module-02-sdk-setup/SKILL.md`. A `grep` across
   `plugins/` for `nohup`, "protected binary" or "protected launcher" near a DYLD or library term
   returns **nothing**.
2. The two places that actually start a long-running SDK process —
   `module-03b-truthset-visualization/phase1-visualization.md:357` (*"Start the server as a
   background process"*) and Module 7's equivalent — say nothing about it, and they are several
   modules away from the one file that discusses `DYLD_*` at all.
3. The error names `java.library.path`, so the obvious response is to add `-Djava.library.path=…`,
   which the plugin already documents as insufficient and which does not fix it. **Nothing points at
   the launcher**, so the diagnosis has nowhere to go.

⚠️ **This is macOS-only and silent on Linux, so it will not reproduce for a maintainer testing
there** — including in this triage, which ran on Linux.

## Root cause

The SIP behavior is documented once, in the module where the environment is set up, and the hazard
fires in a different module where a process is launched. Between them the variable is correct and
everything works, so nothing prompts a re-read. The plugin's own launch example is safe by
construction — plain `&` from the sourced shell — but it does not say *why* it is written that way,
so any deviation that wraps the launch (a `nohup` for durability, an `env` prefix, a nested
`bash -c` from a tool harness) silently removes the variable the whole setup existed to provide.

## Proposed change

1. **Add a one-line macOS caution wherever the bootcamp starts a long-running SDK process** — at
   minimum `phase1-visualization.md` 2.3 and Module 7's server launch. Content: on macOS, start it as
   a **direct child of a shell that has sourced `senzing-env.sh`** — never through `nohup`, `env`, or
   a nested `bash -c`, because SIP strips `DYLD_*` when a protected binary execs a child.
2. **Say what the symptom looks like**, because the symptom is what a Bootcamper will search for:
   `UnsatisfiedLinkError: no Sz in java.library.path` from a backgrounded process whose parent shell
   has the variable set. ⛔ **And say that adding `-Djava.library.path` does not fix it**, pointing at
   the existing statement in module-02 rather than restating the reasoning (INV-179).
3. **Explain why the plugin's own launch line is written the way it is** — one clause on the existing
   `&` line noting it is a direct child on purpose — so an editor does not "improve" it into a
   `nohup` later.
4. ⛔ **Do not make this a platform-gated instruction that Linux readers skip.** INV-001 makes all
   three platforms first-class; state it as a macOS-specific hazard inside guidance every platform
   reads, so a macOS Bootcamper meets it without a branch that hides it from everyone else.

## Acceptance criteria

- [ ] Every shipped step that starts a long-running SDK process carries the macOS caution, with the
      site set derived by scanning for the launch pattern rather than a hardcoded file list
      (INV-246).
- [ ] The caution names `nohup`, `env` and nested `bash -c` explicitly as protected launchers.
- [ ] The caution names the `UnsatisfiedLinkError: no Sz in java.library.path` symptom.
- [ ] The caution states that `-Djava.library.path` does not fix it and cites module-02 rather than
      restating the reasoning (INV-179).
- [ ] The existing plain-`&` launch example is unchanged in behavior.
- [ ] A test asserts the caution is present at every launch site the scan finds. Stdlib only, no
      `plugins/` import (INV-108).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      hazard is macOS-specific, the guidance is read by all three, and the JVM example is
      illustration only (INV-002).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  section 2.3 at `:355-370`
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the equivalent server launch
- `tests/` — a scanning guard for the caution at every launch site

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: macOS strips DYLD_* through
  protected launchers, so a backgrounded SDK process cannot find the native library" (2026-08-25,
  Module: Query, Visualize and Discover, Priority: Medium; `Source: self-observed (assistant
  retrospective)`).
- Priority: **Medium**, as filed. It blocks the visualization server on macOS whenever the launch is
  wrapped, and the error points away from the cause — but the plugin's own example is already safe,
  so a guide following it literally does not hit this.
- MCP re-check: **n/a (no Senzing fact).** The subject is macOS System Integrity Protection behavior
  and this plugin's launch guidance; no Senzing behavior, SDK surface or server claim is asserted.
  `get_capabilities` was called this session to date the triage: server **1.33.0**, 2026-08-28.
  ⚠️ **The SIP behavior was NOT reproduced during triage** — this machine is Linux, where `DYLD_*`
  does not exist and the stripping cannot occur. It rests on the reporter's three-line direct
  demonstration quoted above, on Darwin 25.5.0 arm64, and is marked observation-only
  (INV-080/INV-149). Re-confirm on macOS before or during implementation.
- Upstream: not applicable — an OS behavior and a plugin documentation gap, not a Senzing defect.
- Related specs: `specs/macos-jvm-launch-environment-guidance.md` (established the SIP/`DYLD_*`
  guidance in module-02, already implemented — this spec carries it to the launch sites and adds the
  protected-launcher case it does not cover); `specs/env-script-must-be-shell-portable.md` and
  `specs/env-script-template-names-every-export-but-pythonpath.md` (the `senzing-env.sh` lineage)
