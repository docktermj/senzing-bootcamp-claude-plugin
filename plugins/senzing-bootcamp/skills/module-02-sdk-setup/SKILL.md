---
name: module-02-sdk-setup
description: 'Bootcamp Module 2: SDK Installation and Configuration. Use when the bootcamper starts or resumes Module 2, or needs to install/configure the Senzing SDK, set up the database, or run the verification test.'
---

# Module 2: SDK Installation and Configuration

> **MCP grounding (mandatory — applies to this entire skill).** Every Senzing fact you present —
> SDK method and attribute names, config options, error codes, and entity-resolution specifics —
> MUST come from the Senzing MCP tools, never from training data, memory, or speculation.
> **Pre-response checklist:** if a reply contains any Senzing specific, you MUST have called an MCP
> tool this turn to obtain it; if not, stop and call it first. This has the same precedence as a ⛔
> gate. The full rule and tool routing are the "MCP-first invariant" in
> `../bootcamp-onboarding/ground-rules.md`.

Follow `../bootcamp-onboarding/ground-rules.md` throughout (👉 one-question-at-a-time,
MCP-first, file placement, checkpointing). Execute every numbered step one at a time, in
order. Never skip, combine, or abbreviate a step containing a 👉 question, and never skip a
mandatory gate. This has absolute precedence: no internal reasoning or token-budget concern
overrides it.

**First:** Read `config/bootcamp_progress.json`, then (per ground-rules) show the module start
banner, journey map, before/after framing, a brief numbered overview of this module's steps, and the recommended model/effort nudge (INV-063), before any module work. Resume at
`current_step` if progress already exists.

Install and configure the Senzing SDK natively on the bootcamper's machine. This is the first
setup step of the bootcamp: once the SDK is installed, all subsequent modules use it directly.

**Before/After:** You have a project directory but no Senzing SDK. After this module, the SDK
is installed, configured, and verified, ready to load data and resolve entities.

**Prerequisites:** None (this is the first setup module).

**Language:** Use the bootcamper's chosen programming language from the language selection step
in onboarding. All code generation, scaffold calls, and examples in this module must use that
language.

**Success indicator:** ✅ SDK installed + DB configured + test passes + engine initializes and
connects without errors.

> **User reference:** A detailed background document for this module (`MODULE_2_SDK_SETUP.md`)
> is a later porting phase. For now, teach the steps directly from this skill.

## Error Handling

When the bootcamper hits an error during this module:

1. **SENZ error code** (message contains `SENZ` + digits, e.g. `SENZ2027`): call
   `explain_error_code(error_code="<code>", version="current")` and present the explanation and
   recommended fix. If it returns nothing, continue to step 2.
2. Present the matching pitfall/fix for this module (full `common-pitfalls` reference is a
   later porting phase; for now, use `search_docs` to look up the symptom).
3. If no match, use `search_docs` against the Troubleshooting-by-Symptom guidance and general
   pitfalls.

> The TypeScript from-source build has its own recovery branch (see Step 3). A mid-build
> compile failure is handled there, not by this generic SENZ-code path.

## Step 1: Check for Existing Installation (MUST DO FIRST)

Before doing anything else in this module, check if the Senzing SDK is already installed and
working. There is no reason to re-install it.

Run a language-appropriate import/version check for the bootcamper's chosen language. Use
`sdk_guide(topic='install', platform='<user_platform>', language='<chosen_language>', version='current')`
to get the correct verification command.

**Filesystem fallback (if the import check fails):** When the language import check does not
succeed (e.g., `PYTHONPATH` is not configured or the package manager query finds nothing),
check for these sentinel files before concluding the SDK is not installed:

- `/opt/senzing/er/lib/libSz.so` (native shared library)
- `/opt/senzing/er/szBuildVersion.json` (build version metadata)

Both sentinel files must be present to conclude the SDK is installed via filesystem detection.
If both exist, read the version from `/opt/senzing/er/szBuildVersion.json`, report the SDK as
installed, skip Steps 2 and 3 entirely, and proceed to Step 4 verification. If only one file
or neither is found, proceed with the "SDK not found" path (Step 2).

**If the SDK is found and version is V4.0+:**

Tell the user: "Senzing SDK is already installed (version [X]). No need to reinstall, skipping
straight to configuration verification."

- Skip Steps 2 and 3 entirely.
- Jump to Step 4 (verify installation) to confirm it works with the chosen language.
- If Step 4 passes, proceed to Step 5 (License), which confirms the built-in evaluation license
  without prompting (the License Key gate is in Module 4, per INV-093). After Step 5, proceed to
  Step 6 (create the project directory structure), then Step 7 (database).
- Mark Module 2 as complete once verification passes.

> **Required stops:** These steps are NEVER skipped, even when the SDK is already installed:
>
> - **Step 4** (Verify Installation): confirms the SDK works with the chosen language.
> - **Step 5** (License): a brief, no-prompt confirmation that the built-in evaluation license is
>   active (the volume-gated License Key gate itself lives in Module 4, per INV-093).

**If the SDK is found but version is incompatible (<V4.0):**

Tell the user: "Senzing SDK found but it's version [X]. The bootcamp requires V4.0+. We'll need
to upgrade." Proceed with Steps 2-3 for the upgrade.

**If the SDK is NOT found:**

Tell the user: "Senzing SDK is not installed yet. Let's set it up, this is a one-time process."
Proceed with Step 2.

**Checkpoint:** write step 1 to `config/bootcamp_progress.json`.

## Step 2: Determine Platform

**Detect first, do not ask.** This gate is satisfied by *determining* the platform, not by asking
a question. Read `os`/`arch` from `config/bootcamp_preferences.yaml` (persisted during onboarding);
if absent, detect from the environment/system context (else run `uname`/`systeminfo`). State the
detected platform in one line and proceed — e.g. "Detected macOS on Apple Silicon; say so if that's
wrong." For macOS, also establish whether it is Apple Silicon (M1/M2/M3/M4) or Intel from the same
source.

**Fallback only** — when detection is genuinely unavailable or ambiguous, ask this pinned question
and wait:

👉 **What operating system are you on? Reply with a number:**

1. Linux
2. macOS
3. Windows

*(Internal: end the turn on this question and wait.)*

Then resolve the `sdk_guide` platform value using the rules below. Do NOT assume a native
install: several OS + language combinations require Docker. The MCP server is authoritative;
if uncertain, call `sdk_guide(topic='install')` with no platform to get the live decision tree.

**Platform options for `sdk_guide`:**

- `platform='linux_apt'`: Debian/Ubuntu/Mint (apt/dpkg)
- `platform='linux_yum'`: RHEL/Fedora/Amazon Linux (yum/dnf)
- `platform='macos_arm'`: macOS Apple Silicon (Homebrew cask)
- `platform='windows'`: Windows 10/11 (Scoop)
- `platform='docker'`: Platform-independent container; the fallback and the required path for
  several cases below

**Routing rules (apply in order):**

1. Chosen language is Python AND OS is macOS or Windows → **`platform='docker'`**. The Python
   SDK is only supported on Linux; on macOS/Windows it must run in a container.
2. macOS Intel → **`platform='docker'`**. There is no native Intel-Mac install: the Homebrew
   tap is Apple Silicon (ARM64) only.
3. macOS Apple Silicon (non-Python) → **`platform='macos_arm'`**.
4. Windows without Scoop (non-Python) → **`platform='docker'`**. With Scoop available →
   **`platform='windows'`**.
5. Linux → **`platform='linux_apt'`** or **`platform='linux_yum'`** based on the package
   manager.

When a learner lands on Docker because of these rules, briefly explain why (e.g., "The Senzing
Python SDK is Linux-only, so on macOS we'll run it in a container") so the redirect doesn't
feel arbitrary.

Use `sdk_guide` with `topic='install'`, the resolved `platform`, and the bootcamper's chosen
language as the `language` parameter to get current installation commands. The MCP server
always has the latest instructions.

**Checkpoint:** write step 2 to `config/bootcamp_progress.json`.

## Step 3: Install Senzing SDK

Follow the platform-specific instructions from `sdk_guide`. Installation has three phases.

**Before recommending any approach**, call `search_docs` with `category='anti_patterns'` to
check for known pitfalls on the user's platform.

**Phase 1: Install the SDK package (execute without stopping):**

For native installs (`linux_apt`, `linux_yum`, `macos_arm`, `windows`):

1. Add the Senzing package repository.
2. Install the Senzing SDK package.

For the `docker` path (Intel Mac, Python on macOS/Windows, or Windows without Scoop):

- **Do not use the pre-built `senzing/senzingsdk-tools` images.** They require PostgreSQL and
  do not support SQLite, which is the bootcamp default (Step 7). Instead, run a plain Linux
  container (e.g., `debian:bookworm-slim`) and follow the `linux_apt` steps inside it so SQLite
  keeps working.
- Mount the bootcamper's project directory into the container so all artifacts (database,
  config, source) land in the working directory, not inside an ephemeral container layer.
- Call `sdk_guide(topic='install', platform='docker', language='<chosen_language>')` for the
  current container commands and image names.
- Never drive interactive Senzing CLI tools (`sz_configtool`, `sz_explorer`): they require
  human input. Generate SDK code via `generate_scaffold` instead.
- Senzing publishes native ARM64 images, so no x86 emulation is needed on Apple Silicon.
- **Record the container for lifecycle tracking (INV-101).** When you `docker run` the container,
  give it a stable `--name` and append an entry to a `docker_containers` list in
  `config/bootcamp_progress.json` (at least its `name`; also `image` and `purpose` when handy).
  The `SessionEnd` hook stops recorded containers on exit (`docker stop`, not remove) and
  `SessionStart` surfaces them on resume so they can be restarted or regenerated.

**Phase 2: EULA acceptance (requires bootcamper input):**

The Senzing SDK requires EULA acceptance before use. Tell the bootcamper they can review it at
<https://senzing.com/end-user-license-agreement/>, then present the EULA question:

👉 **Do you accept the Senzing End User License Agreement (EULA)? Respond yes or no.**

*(Internal: end the turn on this question and wait. Do not proceed until the bootcamper
answers.)*

Once the bootcamper responds, act on their answer:

- **If they accept the EULA:** proceed to Phase 3 to install language-specific SDK bindings.
- **If they decline the EULA:** stop the installation. Explain: "The Senzing SDK cannot be used
  without EULA acceptance. The remaining installation steps and subsequent bootcamp modules
  require the SDK." Do not install language bindings and do not write the checkpoint. Stop here.

**Phase 3: Install language bindings (only after EULA acceptance):**

3. Install the language-specific SDK bindings. For Python, never use a bare `pip` (a stale shim on
   PATH may point at a deleted interpreter): use `python3 -m pip install senzing`, and if an
   externally-managed environment (PEP 668, common on macOS/Homebrew and many Linux distros)
   rejects it, install into a project-local virtualenv (`python3 -m venv <project-relative dir>`
   then `<dir>/bin/python -m pip install senzing`; on Windows `<dir>\Scripts\python -m pip install
   senzing`) and use that interpreter for the bootcamp's Python code. Never modify the global/system
   Python. For other languages, use that ecosystem's package manager (Maven/Gradle for Java, NuGet
   for C#, etc.).

**TypeScript/Node.js warning:** The TypeScript SDK (`sz-napi`) may require building from source
if prebuilt binaries are not available for the user's platform. This involves installing the
Rust toolchain, cloning `sz-rust-sdk` and `sz-rust-sdk-configtool` as Cargo dependencies, and
building the native addon with `napi-rs`. Warn the user upfront: "The TypeScript SDK setup is
more involved than other languages, it may require building native bindings from source, which
needs the Rust toolchain. If you'd prefer a faster setup, Java or C# typically have simpler
install paths." If they proceed with TypeScript, guide them through the full build sequence in
one go rather than letting them discover steps through trial and error.

**Windows-specific:** Building the TypeScript SDK from source on Windows requires Visual Studio
Build Tools (not the full IDE) with the "Desktop development with C++" workload. Install via
`winget install Microsoft.VisualStudio.2022.BuildTools` or download from
visualstudio.microsoft.com. The Rust toolchain installer (`rustup-init.exe`) will detect the
build tools automatically.

### Recovery: build-from-source failures (TypeScript)

> **Applies to the TypeScript from-source build only.** This branch handles a failure *during*
> the `sz-napi` from-source build described just above (the Rust toolchain / `napi-rs` /
> native-addon compile). It does not apply to other languages or to Senzing engine/runtime
> errors.

**1. Detection and routing.** If the from-source build exits non-zero, or reports a
native-addon, `node-gyp`, toolchain, or Node-version failure while compiling `sz-napi`, treat
it as a mid-build failure and enter **this** recovery branch. Do NOT fall through to the
module's generic Error Handling block (the `SENZ`-code → pitfalls → symptom path). That generic
path is tuned for Senzing engine/runtime errors and will not recognize a half-finished native
compile.

**2. Summarize before offering options.** Before presenting any options, state in plain
language which build stage failed and the single most likely cause, chosen from the known-cause
table below. Name the specific cause (for example, "the native addon failed to compile because
the C++ build toolchain is missing") rather than pasting the raw build log. If the failure
signal does not match any known cause, say so plainly ("this is an unrecognized build failure")
and still continue to the options: an unrecognized failure is never a dead end.

**3. Known-cause table.** Match the failure signal to one cause. The detailed per-cause fixes
live in a TypeScript "Common Environment Issues" reference (`lang-typescript.md`) that is a
later porting phase; until then, source the fixes from the Senzing MCP server (see item 5) and
the inline pointers here.

| Cause | Failure signal | Fix reference ("Common Environment Issues") |
|---|---|---|
| `NODE_VERSION` | `SyntaxError` on modern syntax, `ERR_UNSUPPORTED_ESM_URL_SCHEME`, Node.js older than 18 | "Node.js Version Conflicts" |
| `NATIVE_ADDON` | `gyp ERR! build error`, `Cannot find module '.../*.node'` | "Native Addon Build Failures (node-gyp)" |
| `TOOLCHAIN` | missing C++ compiler, missing Rust toolchain, or missing Visual Studio Build Tools | "Native Addon Build Failures (node-gyp)" plus the Windows note above in this Phase 3 |
| `MODULE_SYSTEM` | `ERR_REQUIRE_ESM`, `Cannot use import statement outside a module` | "ESM vs CommonJS Module Resolution" |
| `PKG_MANAGER` | `ERESOLVE unable to resolve dependency tree`, lockfile conflicts | "Package Manager Conflicts" |

**4. Offer targeted options.** After the summary, always offer, at minimum, these three:

- **Fix the common cause:** apply the fix for the matched cause (see sourcing in the next
  item), then retry.
- **Retry the build:** re-run the from-source build sequence.
- **Fallback path:** proceed without a successful from-source build (see item 6). One fallback
  is switching to a language with a simpler install path (Java or C# typically have simpler
  paths); another is any prebuilt/alternative install route the MCP server reports as available.

**5. Sourcing (no hardcoded URLs).** For the detailed fix steps, use the Senzing MCP server:
`sdk_guide(topic='install', platform='<user_platform>', language='typescript')` and
`search_docs(category='anti_patterns')`. Never paste external URLs into this recovery flow; all
external/toolchain knowledge comes from the MCP tools (and, once ported, the `lang-typescript.md`
reference). If an MCP tool is unavailable, the fallback path still applies, so guidance degrades
gracefully rather than dead-ending.

**6. Resume or continue Module 2.** Neither continuation requires deep toolchain debugging:

- **On a successful retry** (the build now succeeds), resume the normal sequence: continue
  Phase 3 (install the language bindings) and proceed to Step 4 (verify installation).
- **On the fallback path**, continue Module 2 without a successful from-source build: proceed to
  Step 4 verification using the prebuilt/alternative install (or the newly chosen language) so
  setup is never blocked on the from-source compile.

**7. Never a dead end.** There is always a way forward: retry after a fix, or the fallback path.
If a retry fails again, re-summarize against the known-cause table (re-classifying on the new
signal) and re-offer the options; do not silently loop on the same error. If every option has
genuinely been exhausted, do not re-run the same failing command: state the current blocker in
plain language and present the support / next-step options (for example, capture the failure
details for a support request via `search_docs`, or take the fallback path if not already
tried). This terminal state names the blocker and the next step rather than looping.

**🚨 NEVER modify the user's global shell configuration** (`~/.zshrc`, `~/.bashrc`,
`~/.profile`, etc.) to set Senzing environment variables. Instead, create a project-local
environment script at `src/scripts/senzing-env.sh` (or `.bat` for Windows) that sets
`SENZING_ROOT`, library paths, and any other Senzing-specific variables. Source this script
before running bootcamp tasks. This keeps the bootcamp self-contained and avoids side effects on
the user's system.

**Checkpoint:** write step 3 to `config/bootcamp_progress.json`.

## Step 4: Verify Installation

Generate a verification script in the bootcamper's chosen language using
`generate_scaffold(language='<chosen_language>', workflow='initialize', version='current')`.
The script should initialize the Senzing engine and print the version to confirm the SDK is
working.

If verification fails, use `explain_error_code` for any SENZ error codes and `search_docs` for
troubleshooting.

**Checkpoint:** write step 4 to `config/bootcamp_progress.json`.

## Step 5: License (built-in evaluation license active)

> **Internal note:** this step does NOT prompt for a License Key. The single, volume-gated
> Senzing License Key prompt is presented once, at the start of Data collection (Module 4),
> per INV-093. SDK setup only confirms that the built-in evaluation license is active; the
> "License Key" reference notes below are kept for context.

> **License check order:** Senzing checks for licenses in this order: project-local
> `licenses/g2.lic` → `SENZING_LICENSE_PATH` env var → system CONFIGPATH → built-in evaluation
> (500 records).

> **"Senzing License Key" vs. the EULA:** the **Senzing License Key** configured in this step is a
> *runtime-capacity* license (it sets how many records Senzing will resolve) — supplied as a `.lic`
> file or a Base64-encoded key, or the built-in evaluation license by default. It is distinct from
> the **Senzing End User License Agreement (EULA)** accepted during SDK install in Step 3. When
> this step says "License Key", it means the runtime license, never the EULA.

### 5a. Confirm the built-in evaluation license (no prompt)

**Already-licensed guard (check first).** Read `config/bootcamp_progress.json`. If a
`license_record_limit` field is present, a custom license has already been configured (its limit
was detected earlier, this session or a prior one). Acknowledge it: present the detected
`recordLimit` as the authoritative limit ("Your license allows up to N records," or "Your license
has no record cap (unlimited)" when it is `0`), and skip the evaluation-license note below. Do not
re-ask (INV-006). Confirm any SDK facts against the Senzing MCP server rather than training data.

Otherwise (only the built-in evaluation license is active), present this briefly — as a statement,
**not a question:**

"Your Senzing SDK uses a **built-in evaluation license limited to 500 records** automatically when
no custom license is present — no license file needed. That's enough for the demo modules that come
next (System verification and Truth Set visualization), which run on small synthetic and Truth Set
data. If your **own** data later exceeds the evaluation limit, we'll set up a Senzing License Key in
the Data collection module (Module 4), where your data volume is known. Nothing to do here."

When presenting the evaluation license's record capacity or validity period, retrieve those values
from a Senzing MCP server tool during this session and present exactly what the tool returns. The
**500 records** figure is a published value that can change: confirm it against the Senzing MCP
server rather than training data. Wait up to 30 seconds; if the tool does not return a value, omit
the specific figure and tell the bootcamper the current value is unavailable from the MCP server.
Never substitute a hardcoded or remembered figure.

> **Where the License Key is handled now:** the interactive License-Key setup (asking whether the
> bootcamper has a key, decoding/placing a `.lic` or Base64 key, wiring `LICENSEFILE`, requesting an
> evaluation license via the MCP server or Senzing support, and detecting the record limit) is the
> single, volume-gated gate at the start of Data collection (Module 4, Step 8a), per INV-093. SDK
> setup no longer performs it.

**Checkpoint:** write step 5 to `config/bootcamp_progress.json`.

## Step 6: Create Project Directory Structure

Create the organized project layout that all subsequent modules use, following the file
placement layout in `../bootcamp-onboarding/ground-rules.md` (`src/`, `src/scripts/`, `data/`,
`database/`, `docs/`, `config/`, `licenses/`, `src/resources/`, `data/mapping/`, `data/temp/`).
(The full Kiro agent-instructions directory-creation script is a later porting phase; create
the layout directly per the ground-rules placement rules for now.)

After creation, inform the user: "I've set up the project directory structure. All files will
be organized properly throughout the bootcamp."

**Checkpoint:** write step 6 to `config/bootcamp_progress.json`.

## Step 7: Configure Database

Ask: 👉 **Which database would you like to use? Reply with a number:**

1. **SQLite** — recommended for learning and evaluation.
2. **PostgreSQL** — better for production; can run in a Docker container (recommended when Docker is available), a local install, or an existing server.

*(Internal: end the turn on this question and wait.)*

**For SQLite** (recommended for bootcamp):

- Create the database directory: `mkdir -p database` (Linux/macOS) or
  `New-Item -ItemType Directory -Force -Path database` (PowerShell).
- Database path: `database/G2C.db`.
- No additional setup needed: SQLite is built in.
- **IMPORTANT:** Never use `/tmp/` or in-memory databases. If `generate_scaffold` or
  `ExampleEnvironment` defaults to `/tmp/`, override the path to `database/G2C.db`.

**For PostgreSQL** (production): first choose HOW to run it. Detect Docker availability
(`docker version`); when Docker is present, offer the container option **first and recommended** —
a real, production-style PostgreSQL with no system-wide install or admin rights, easy to tear down.
Pin this 👉 question verbatim (neutral lead + numbered list, INV-051/INV-056):

👉 **How would you like to run PostgreSQL? Reply with a number:**

1. **In a Docker container** — recommended when Docker is available; self-contained and production-style.
2. **Install PostgreSQL locally.**
3. **Use an existing PostgreSQL server.**
4. **Switch to SQLite** (the bootcamp default).

*(Internal: end the turn on this question and wait.)* When Docker is not available, omit option 1
and say so.

**MCP-first (INV-080):** confirm the current PostgreSQL connection-URL format, the schema-DDL path,
and the engine-config wiring from the Senzing MCP server at runtime — do not treat the values below
as authoritative. Use `search_docs(query='Senzing engine configuration PostgreSQL connection')` and
`search_docs(query='PostgreSQL schema DDL initialization', category='anti_patterns')`, and generate
the engine config with `sdk_guide(topic='configure', ...)` — never hand-construct
`SENZING_ENGINE_CONFIGURATION_JSON`.

**Option 1 — PostgreSQL in a Docker container:**

1. Run an official `postgres` image with a stable `--name`, a **project-local volume** (data
   persists in the working directory, not an ephemeral layer), and credentials:

   ```bash
   docker run -d --name bootcamp-postgres \
     -e POSTGRES_USER=senzing -e POSTGRES_PASSWORD=senzing -e POSTGRES_DB=G2 \
     -p 5432:5432 -v "$(pwd)/database/postgres:/var/lib/postgresql/data" postgres:16
   ```

2. Record the container for lifecycle tracking (INV-101): append it to `docker_containers` in
   `config/bootcamp_progress.json` (at least its `name`) so the SessionEnd hook stops it on exit
   and SessionStart offers to restart it.
3. Wait until the server is ready (poll `docker exec bootcamp-postgres pg_isready`).
4. Apply the Senzing PostgreSQL schema DDL **before any SDK use** — the SDK does NOT auto-create it
   (unlike SQLite). MCP confirms the DDL ships with the SDK install at
   `/opt/senzing/er/resources/schema/szcore-schema-postgresql-create.sql`; apply it against the
   container:

   ```bash
   docker exec -i bootcamp-postgres psql -U senzing -d G2 \
     < /opt/senzing/er/resources/schema/szcore-schema-postgresql-create.sql
   ```

   Re-confirm the exact path via MCP; the Windows/macOS SDK install path differs (see the
   initialization anti-patterns doc).
5. Wire the connection into the engine config (Step 8): the `SQL.CONNECTION` URL is
   `postgresql://user:password@host:port/database` (MCP-confirmed). Generate the full engine config
   via `sdk_guide(topic='configure', ...)` and save it to `config/engine_config.json`.

**Option 2 — Install PostgreSQL locally:** install and start a local PostgreSQL server, create the
Senzing database, apply the schema DDL as above (`psql -f .../szcore-schema-postgresql-create.sql`),
then wire the `postgresql://` connection via `sdk_guide(topic='configure', ...)`.

**Option 3 — Use an existing PostgreSQL server:** obtain the host/port/database/credentials, apply
the schema DDL to that database, and wire the `postgresql://` connection as above. Managed cloud
PostgreSQL typically requires SSL (`PGSSLMODE=require`) — confirm via MCP.

**Option 4 — Switch to SQLite:** proceed with the SQLite setup above.

SQLite remains the default recommendation for pure evaluation; PostgreSQL (especially via Docker)
is the production-style path. INV-037 is satisfied by any of these paths.

**Checkpoint:** write step 7 to `config/bootcamp_progress.json`.

## Step 8: Create Engine Configuration

**🚨 NEVER construct `SENZING_ENGINE_CONFIGURATION_JSON` manually.** Always use the exact JSON
returned by
`sdk_guide(topic='configure', platform='<user_platform>', language='<chosen_language>', version='current')`.
Do not guess paths for CONFIGPATH, RESOURCEPATH, or SUPPORTPATH based on directory patterns: the
correct paths vary by platform and installation method, and guessing causes engine
initialization failures (e.g., SENZ2027 when SUPPORTPATH is wrong).

Use `sdk_guide` with `topic='configure'` to generate the correct engine configuration JSON for
the user's platform and database choice. Save the MCP-returned JSON directly to
`config/engine_config.json`; do not modify the paths.

**On Windows, verify SUPPORTPATH exists before saving the configuration:**

After receiving the MCP-returned JSON, check that the SUPPORTPATH directory actually exists on
the filesystem. This is a targeted path verification, not manual JSON construction: the
MCP-returned JSON remains the starting point.

1. Extract the SUPPORTPATH value from the MCP-returned configuration JSON.
2. Use `Test-Path` in PowerShell to confirm the SUPPORTPATH directory exists:

   ```powershell
   Test-Path -Path "$SENZING_DIR\data"
   ```

3. If `$SENZING_DIR\data` does not exist, check `$SENZING_DIR\..\data` (one level up from the
   `er` directory):

   ```powershell
   Test-Path -Path "$SENZING_DIR\..\data"
   ```

4. If the parent-level path exists, update SUPPORTPATH in the configuration JSON to use
   `$SENZING_DIR\..\data` before saving to `config/engine_config.json`.
5. If neither path exists, report the error clearly: "SUPPORTPATH directory not found at either
   `$SENZING_DIR\data` or `$SENZING_DIR\..\data`. Please verify your Senzing installation."

> **Why the Scoop layout differs:** The unofficial Windows Scoop package places `SENZING_DIR`
> at the `er` subdirectory within the Scoop app folder (e.g.,
> `C:\Users\<user>\scoop\apps\senzing\current\er`). The `data` directory containing
> `g2SifterRules.ibm` and other GNR support files is at the Scoop app version root, one level
> above `er`, rather than inside it. This is why the fallback to `$SENZING_DIR\..\data` is
> needed for Scoop installs.

This SUPPORTPATH verification applies to Windows only. On Linux and macOS, use the MCP-returned
paths without modification.

**Checkpoint:** write step 8 to `config/bootcamp_progress.json`.

## Step 9: Test Database Connection

Use `generate_scaffold(language='<chosen_language>', workflow='initialize', version='current')`
to get the current V4 initialization and connection test pattern, then use that MCP-generated
initialization code to verify the database connection works.

Never generate direct SQL against `database/G2C.db`; all access goes through Senzing SDK
methods (per ground-rules).

**Checkpoint:** write step 9 to `config/bootcamp_progress.json`.

**Success indicator:** ✅ SDK installed + DB configured + test passes + engine initializes and
connects without errors.

## Success Criteria

- ✅ Senzing SDK installed natively.
- ✅ SDK imports/references work in the chosen language.
- ✅ Engine initializes without errors.
- ✅ Database connection works.
- ✅ Project directory structure created.

## Agent Behavior

- Always check for an existing installation first: if the SDK is present and V4.0+, do NOT
  reinstall. Skip to verification.
- Do NOT offer alternatives: install the SDK natively (or via Docker where the routing rules
  require it).
- Use the `sdk_guide` MCP tool for current platform-specific instructions.
- Use `search_docs` with `category='anti_patterns'` before recommending approaches.
- **NEVER construct engine configuration JSON manually:** always use the exact JSON from
  `sdk_guide(topic='configure')`. Do not guess CONFIGPATH, RESOURCEPATH, or SUPPORTPATH.
- Recommend SQLite for evaluation, PostgreSQL for production.
- Always use `database/G2C.db` for SQLite (never `/tmp/sqlite`).
- Verify installation before proceeding to the next module.

## Troubleshooting

- Installation fails? Use `explain_error_code` for SENZ errors.
- Platform not supported? Use `search_docs` for alternative installation methods.
- Database errors? Confirm path requirements against the file placement rules in ground-rules
  (the Kiro `FILE_STORAGE_POLICY.md` reference is a later porting phase).
- Permission issues? Ensure you have admin/sudo access for installation.
- Missing dependencies? A Kiro preflight script (`preflight.py`) is a later porting phase; for
  now, verify prerequisites directly and use `search_docs` for platform requirements.

## Module completion and transition

Once the SDK is installed and verified, run the standard **Module Completion** process in
`../bootcamp-onboarding/module-completion.md` (update progress, append the Module 2 recap section
to `docs/bootcamp_recap.md`, and present the end-of-module summary), then ask the single
transition question.

The next module in your selected sequence continues the bootcamp — when it is System verification, it verifies the full setup end-to-end with synthetic records (and, when the Truth Set visualization is selected, visualizes the Senzing Truth Set):

👉 **Are you ready to move on to the next module: {next module name}?**

*(Internal: end the turn on this question and wait.)* On module completion set `current_step` to
`null`.
