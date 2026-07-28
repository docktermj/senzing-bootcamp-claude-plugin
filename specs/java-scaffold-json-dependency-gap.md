# Flag that MCP Java scaffolds need a JSON-P implementation the Senzing install does not provide

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The authoritative Java scaffolds returned by `generate_scaffold`
(`loading/LoadWithInfoViaFutures.java`, `redo/RedoContinuous.java`,
`configuration/RegisterDataSources.java`) `import javax.json.*` and use `Json.createReader(...)` to parse
both input records and `WITH_INFO` responses.

`javax.json` (JSON-P) is **not** present in a stock Senzing installation. The reporter verified it: no jars
in `$SENZING_ROOT/lib`, and `sz-sdk.jar` contains zero `javax/json` or `jakarta/json` classes (checked via
`ls $SENZING_ROOT/lib/*.jar`, a `find` for `*json*.jar`, and `unzip -l sz-sdk.jar | grep -ci "javax/json"`
→ 0). **The scaffolds therefore do not compile as written** on a stock Homebrew install with plain `javac`.

The workaround was to keep every SDK call exactly as the scaffold specified and substitute a
dependency-free JSON reader, documenting both deviations in the source headers.

Why it matters, in the reporter's words: "`generate_scaffold` is presented as the authoritative, MCP-first
alternative to hand-written SDK code, and the plugin instructs the assistant to prefer it precisely because
hand-written code gets method names wrong. That trust is undermined if the returned code cannot compile in
the environment the plugin just finished setting up. A bootcamper is then left debugging an import error in
code they were told was known-good, with no signal about whether the fault is theirs, the SDK's, or the
scaffold's."

And the sharp edge: "The risk is not just friction: a bootcamper might 'fix' it by rewriting the SDK calls,
which is exactly the failure mode the scaffolds exist to prevent."

## Root cause

**Confirmed: nothing in the plugin mentions `javax.json`, JSON-P, or `jakarta.json`** — grep across the
whole plugin returns zero hits. So there is no warning, no dependency note, and no guidance on what is safe
to change when a scaffold does not compile.

The mismatch is structural: the scaffolds come from a repository that presumably builds with a dependency
manager, while **the bootcamp compiles with plain `javac` and never installs one**. Module 2 mentions
"Maven/Gradle for Java" only in passing as an ecosystem package manager (`module-02-sdk-setup/SKILL.md:225`)
and never sets one up; the module actively recommends Java as having a *simpler* install path
(`SKILL.md:233`, `:283`), which makes the plain-`javac` route the expected one.

Two parts of this are outside this repository and must be handled differently:

- **`generate_scaffold`'s response** is produced by the Senzing MCP server. The plugin cannot change what
  it returns, so the plugin-side fix is guidance for handling it. The MCP-side improvement (declaring
  dependencies) should be filed upstream.
- **Whether `javax.json` is absent from every Senzing install**, or only from the Homebrew cask on macOS
  arm64, is **unverified** — one workstation was checked. The guidance must therefore be written as
  "verify, then handle" rather than asserting universal absence.

## Proposed change

Plugin-side (what this spec delivers):

1. **Add a dependency note to the Java path in `module-02-sdk-setup`.** If the project builds with plain
   `javac` (no Maven/Gradle), an MCP scaffold that imports `javax.json` will not compile until either a
   JSON-P implementation is added or the scaffold's JSON handling is replaced.
2. **State the safety asymmetry explicitly — this is the most important line.** Replacing the JSON library
   is **safe**; altering SDK calls is **not**. A bootcamper hitting an import error must be told which half
   of the file they may touch, or they will "fix" the wrong one. Require that any such substitution be
   documented in the source header, so the take-home code records what deviated from the authoritative
   scaffold and why.
3. **Check for the dependency before compiling, not after.** Where the plugin generates Java from a
   scaffold — `module-06-data-processing/phaseA-build-loading.md` step 3 and the redo/register-data-sources
   flows — add a pre-compile check: if the scaffold imports a package the environment does not provide,
   resolve it before compiling rather than surfacing a raw `javac` import error. Verify availability at
   that moment (inspect the SDK jar and the install's lib directory) rather than assuming either way.
4. **Prefer a dependency-free reader for the bootcamp's own code.** Since the bootcamp's scaffolding is
   plain-`javac`-based, generated Java should not depend on JSON-P. The reporter reused a dependency-free
   JSON reader already written for the mappers — worth prescribing that pattern so the same substitution
   is not reinvented per module.
5. **Do not silently strip the import.** The scaffold is authoritative for SDK usage; the deviation must be
   visible in the code the bootcamper takes home, not hidden.

Upstream (out of scope here — **FILED 2026-07-28**):

6. Have `generate_scaffold` / `sdk_guide` state each snippet's **external dependencies** alongside the code,
   so a caller knows a JSON-P implementation is required before compiling. Ideally, offer a dependency-free
   variant of the Java snippets.

   **Correction applied 2026-07-28.** This item previously asserted that the response "already includes a
   `dependencies` field for `com.senzing:sz-sdk-java`" and that JSON-P belongs there. Verified against
   server version 1.32.1: **neither tool returns a `dependencies` field.**
   `sdk_guide(topic='load', language='java', record_count=1000)` returns `code`, `notes`, `anti_patterns`,
   `next_steps`, and `compatibility_notes` (licensing, hardware sizing, mapping only); `generate_scaffold`
   returns `access_steps`, `snippets`, and `anti_patterns`. The ask is therefore to **add** dependency
   reporting, not to populate an existing field — any implementation of this spec must not assume the field
   exists.

   **Upstream request FILED 2026-07-28** via `submit_feedback` as category `feature`, at the maintainer's
   direction, after the exact message text was reviewed and approved. The message named both tools, quoted
   the `import javax.json.*;` / `Json.createReader(...)` usage in `LoadViaFutures.java` against its "real,
   compilable code" label, stated the server version, scoped the install evidence to the single workstation
   checked, and carried no hostname, username, email, or path (INV-065 discipline). It was reworded first so
   it no longer rests on the corrected `dependencies`-field premise above. Submissions are anonymous — the
   server records no sender identity, so there is no reply channel; the plugin-side guidance in items 1-5
   stands as the mitigation until upstream lands, and should be trimmed then.

## Acceptance criteria

- [ ] `module-02-sdk-setup/SKILL.md`'s Java path documents that MCP scaffolds may import JSON-P, that a
      plain-`javac` project does not provide it, and how to resolve it.
- [ ] The guidance states plainly that replacing the JSON library is safe while altering SDK calls is not,
      and requires the substitution to be recorded in the source header.
- [ ] Java scaffold consumers (notably `phaseA-build-loading.md` step 3) check for unavailable imports
      **before** compiling, verifying availability against the actual install rather than assuming.
- [ ] Generated Java for the bootcamp uses a dependency-free JSON reader by default, with the pattern
      stated once and reused rather than re-derived per module.
- [ ] No SDK method name, signature, or flag is altered while substituting the JSON library.
- [ ] The guidance is written as "verify, then handle", not as an assertion that `javax.json` is absent
      everywhere — only one workstation was checked.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the note is
      scoped to the Java path within a language-agnostic module, adds no requirement for other languages,
      and the availability check works on all three platforms.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the Java path (near line ~225, the
  Maven/Gradle mention): the dependency note and the safe-to-change guidance
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — step 3 (lines
  ~99-120) and the redo flow: the pre-compile availability check
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — where mapper
  code is generated; the dependency-free JSON-reader pattern should be stated once and shared

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Flag that MCP Java scaffolds require javax.json,
  which the Senzing install does not provide" (2026-07-25, cross-cutting; `Source: self-observed (assistant
  retrospective)`)
- Priority: Medium
- Related specs: `specs/macos-jvm-launch-environment-guidance.md` (the other undocumented Java-path gap —
  consider implementing in the same pass), `specs/mcp-grounding-in-every-skill.md`,
  `specs/graduation-assistant-retrospective-feedback.md` (the retrospective that surfaced this)
