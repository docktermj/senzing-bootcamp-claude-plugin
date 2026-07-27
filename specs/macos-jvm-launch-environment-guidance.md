# Document the macOS + JVM launch environment in SDK setup (SIP/DYLD, classpath order, zsh, no `timeout`)

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Four independent environment problems cost real time during SDK setup and then recurred as constraints for
the rest of the session. None is documented in the plugin.

1. **`java.library.path` / macOS SIP.** `System.loadLibrary("Sz")` resolves via `java.library.path`, and
   macOS System Integrity Protection **strips `DYLD_*` variables when spawning protected binaries** — so
   exporting `DYLD_LIBRARY_PATH` is not enough, and the failure presents as `no Sz in java.library.path`.
   Every JVM launch needs an explicit `-Djava.library.path=${SENZING_ROOT}/lib`.
2. **Classpath ordering.** `java -cp "$SENZING_JAR:build"` failed to find the main class; the build
   directory must precede the SDK jar.
3. **zsh does not word-split unquoted variables.** `java $SENZING_JAVA_OPTS` passed two flags as a single
   argument. Solved by a wrapper script with explicit flags rather than a variable.
4. **No `timeout`/`gtimeout` on stock macOS.** Any guidance assuming GNU coreutils fails; a background-PID
   plus polling loop is needed.

The durable fix that emerged was a **wrapper script** (`src/scripts/run-java.sh`) used for every JVM launch
thereafter — which worked well and is worth prescribing rather than leaving each bootcamper to rediscover.

Why it matters, in the reporter's words: "macOS on Apple Silicon is a first-class supported path
(`platform='macos_arm'`, Homebrew cask), and Java is a first-class language choice. This combination hits
all four issues, and each presents as a confusing error far from its cause — the SIP one especially, since
the environment variable is set and simply ignored. A bootcamper without deep macOS knowledge could stall
here for a long time in the module whose whole purpose is getting the SDK working."

## Root cause

**Confirmed: the plugin documents installation and never documents the runtime launch environment.**

Grep across `skills/module-02-sdk-setup/` for `java.library.path`, `DYLD`, SIP, System Integrity,
classpath, zsh, `timeout`, `gtimeout`, wrapper script, and launcher returns exactly **one** hit — and it is
unrelated: `SKILL.md:309`, the rule never to modify the user's global shell configuration (`~/.zshrc`,
`~/.bashrc`).

That one hit is significant in a different way: because the plugin (correctly) forbids touching the global
shell config, a **project-local wrapper script is the only place these launch flags can live**. The
constraint already points at the solution.

`macos_arm` is a first-class platform in the module's own decision tree (`SKILL.md:140`, `:151`), and Java
is explicitly recommended as a language with a *simpler* install path (`SKILL.md:233`, `:283`) — so this
combination is one the plugin actively steers bootcampers toward. `sdk_guide(topic='install', …)` covers
installation; nothing covers what a JVM needs at launch.

Note that issue 4 (`timeout` absent) is not Java-specific: it affects any guidance that shells out with a
timeout on macOS, in any language.

## Proposed change

Add a **"macOS + JVM languages"** section to `module-02-sdk-setup/SKILL.md`, referenced from the
`sdk_guide(topic='install', platform='macos_arm')` flow, covering:

1. **The SIP / `DYLD_*` interaction**, stated as cause-and-symptom so the bootcamper can recognize it:
   setting `DYLD_LIBRARY_PATH` appears to work and is silently ignored; the symptom is `no Sz in
   java.library.path`. Require an explicit `-Djava.library.path=<senzing lib dir>` on **every** JVM launch.
2. **Prescribe generating a project-local launcher script** and using it for every subsequent JVM
   invocation — not an exported variable, which zsh will not word-split (issue 3) and which SIP may strip
   (issue 1). The wrapper is the single fix for three of the four issues. Since `SKILL.md:309` forbids
   touching `~/.zshrc`, the project-local wrapper is the natural and only home; make that connection
   explicit so the two rules read as one policy rather than a prohibition plus a gap.
3. **Note the classpath-ordering requirement** — the build/output directory must precede the SDK jar.
4. **Warn that `timeout` is absent on stock macOS** and give the background-PID + polling alternative. Place
   this where it is discoverable beyond the Java path, since it affects any timed shell-out on macOS.
5. **Frame all four as launch-environment issues, not SDK issues**, so a bootcamper does not go hunting for
   a Senzing misconfiguration. This framing is the highest-value sentence in the section.
6. **Confirm the specifics against the Senzing MCP server at implementation time** — the exact library
   directory, jar name, and any required flags (the reported session also needed
   `--enable-native-access=ALL-UNNAMED`) must come from `sdk_guide` / `search_docs` this session, not from
   this spec. The plugin's MCP-grounding rule applies to every Senzing specific written into a skill file.
7. **Check the equivalent gap on the other platforms.** The same launcher-script pattern likely helps
   Windows (`platform='windows'`) and Linux JVM launches, and INV-001/INV-002 mean the section must not read
   as macOS-only trivia. Where a platform needs nothing extra, say so — an explicit "not needed here" stops
   the next reader from wondering.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md` has a macOS + JVM launch-environment section covering all four
      issues, reachable from the `macos_arm` install path.
- [ ] The SIP/`DYLD_*` behavior is described as cause *and* symptom (`no Sz in java.library.path`), with
      `-Djava.library.path=…` required on every JVM launch.
- [ ] The section prescribes generating a project-local launcher script and explicitly ties that to the
      existing "never modify global shell config" rule (`SKILL.md:309`).
- [ ] Classpath ordering (build dir before SDK jar) is stated.
- [ ] The absent-`timeout` warning and its background-PID + polling alternative are documented somewhere
      discoverable to non-Java paths.
- [ ] All Senzing specifics (library path, jar name, required JVM flags) are MCP-sourced at implementation
      time, not copied from this spec.
- [ ] The section states which of these apply to Windows and Linux JVM launches, including explicit "not
      needed" where that is the answer (INV-001).
- [ ] A bootcamper on macOS Apple Silicon choosing Java reaches a working JVM launch without needing macOS
      expertise.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the section is
      scoped as "JVM languages on macOS" guidance within a language-agnostic module, adds no requirement
      for non-JVM languages, and does not make Java a privileged path.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — new macOS + JVM section; cross-reference
  from the platform decision tree (lines ~138-154) and the verify step (line ~318); connect to the
  global-shell-config rule at line ~309

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Ship a macOS + Java environment gotchas reference
  (SIP, classpath order, zsh, no timeout)" (2026-07-25, SDK setup; `Source: self-observed (assistant
  retrospective)`)
- Priority: Medium
- Related specs: `specs/java-scaffold-json-dependency-gap.md` (the other undocumented Java-path gap —
  consider implementing in the same pass), `specs/auto-detect-platform.md`,
  `specs/cross-platform-hook-execution.md`, `specs/mcp-grounding-in-every-skill.md`,
  `specs/graduation-assistant-retrospective-feedback.md` (the retrospective that surfaced this)
