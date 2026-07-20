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
- If Step 4 passes, proceed to Step 5 (Configure License). This step is mandatory and must
  always run regardless of SDK installation status. After Step 5, proceed to Step 6 (create the project directory structure), then Step 7 (database).
- Mark Module 2 as complete once verification passes.

> **Required stops:** These steps are NEVER skipped, even when the SDK is already installed:
>
> - **Step 4** (Verify Installation): confirms the SDK works with the chosen language.
> - **Step 5** (Configure License): license configuration is always required.

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

**Phase 2: EULA acceptance (requires bootcamper input):**

The Senzing SDK requires EULA acceptance before use. Present the EULA question:

👉 **Do you accept the Senzing End User License Agreement (EULA)? You can review it at <https://senzing.com/end-user-license-agreement/>. Please respond yes or no.**

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

## Step 5: Configure License

> **Internal, mandatory gate:** never skip this step, even if the SDK is already installed.
> Announce that you are proceeding with license configuration and execute it.

> **License check order:** Senzing checks for licenses in this order: project-local
> `licenses/g2.lic` → `SENZING_LICENSE_PATH` env var → system CONFIGPATH → built-in evaluation
> (500 records).

> **"Senzing License Key" vs. the EULA:** the **Senzing License Key** configured in this step is a
> *runtime-capacity* license (it sets how many records Senzing will resolve) — supplied as a `.lic`
> file or a Base64-encoded key, or the built-in evaluation license by default. It is distinct from
> the **Senzing End User License Agreement (EULA)** accepted during SDK install in Step 3. When
> this step says "License Key", it means the runtime license, never the EULA.

### 5a. Explain the built-in evaluation license

**Custom-license guard (check first).** Read `config/bootcamp_progress.json`. If a
`license_record_limit` field is present, a custom license has already been configured (its
limit was detected in Step 5e, this session or a prior one). In that case, present the detected
`recordLimit` as the authoritative limit ("Your license allows up to N records," or "Your
license has no record cap (unlimited)" when it is `0`) and do NOT restate the 500-record figure
or the "SENZ9000 error at record 501" claim as the authoritative limit. Skip the built-in
evaluation explanation below; it applies only when no custom license is active. Confirm any SDK
facts against the Senzing MCP server rather than training data.

When no `license_record_limit` field is present (only the built-in evaluation license is
active), proceed with the explanation below.

Before checking for license files or asking the bootcamper anything, proactively present this:

"Here's what you need to know about your Senzing License Key before we continue. Senzing includes a
**built-in evaluation license limited to 500 records**. No license file is needed: the SDK uses
this automatically when no custom license is present. This is enough for the bootcamp's demo
modules and small datasets.

If you load more than 500 records, the SDK returns a **SENZ9000 error at record 501**. For
larger datasets, you need a custom license file placed at `licenses/g2.lic`."

When presenting the evaluation license's record capacity or validity period, retrieve those
values from a Senzing MCP server tool during this session and present exactly what the tool
returns. The **500 records** figure above is the current published value; confirm it against
the Senzing MCP server rather than presenting it as authoritative from training data. Wait up
to 30 seconds for a response; if the tool does not return a value, or the MCP server cannot be
reached within that time, omit the specific figure and tell the bootcamper the current value is
unavailable from the MCP server. Never substitute a hardcoded or remembered figure.

If a larger or temporary evaluation license is needed, **consult the Senzing MCP server:** call
`search_docs(query='request a larger or temporary evaluation license')` and present the
returned guidance; this avoids waiting for email responses.

**If you need more than the built-in evaluation license allows**, there are three ways to
obtain a license. This is informational only: you'll choose and carry out a path later, at the
no-license branch of Step 5c; nothing needs to be selected here.

1. **Request a temporary evaluation license through the MCP server (in-flow):** the bootcamp
   can ask the Senzing MCP server to generate a temporary evaluation license by invoking the
   `submit_feedback` tool with the `license_request` category, which avoids waiting for email.
   This path depends on the `submit_feedback` tool being reported as available by the MCP server
   (checked at runtime via `get_capabilities`), so it may be unavailable in a given session and is
   not guaranteed.
2. **Apply a license you already have:** if you already hold a `.lic` file or a Base64-encoded
   license key, you can place it at `licenses/g2.lic`.
3. **Request a license through Senzing support:** request an evaluation license through
   Senzing support's external channel.

Selecting and carrying out one of these paths happens at the Step 5c no-license branch, not
here.

**When you summarize this explanation aloud (rather than reading it verbatim), your summary
must keep the in-flow option and its caveat.** State that, when more than the evaluation
license's record limit is needed, the bootcamp can help request a temporary evaluation license
in-flow through the MCP server, in addition to applying a license you already have and
requesting one through Senzing support. Carry the caveat that the in-flow path depends on the
`submit_feedback` tool being available and may be unavailable in a given session.

### 5b. Ask about the bootcamper's license situation

**Availability check first.** Call `get_capabilities` on the Senzing MCP server to determine
whether the `submit_feedback` tool is reported available (the same in-flow `license_request` path
introduced in Step 5a and handled at Step 5c). Present the **four-option** form when it is
available, otherwise the **three-option** form. Pin whichever form you present verbatim.

Four-option form (when `submit_feedback` is available):

👉 **Do you have a Senzing License Key? Reply with a number:**

1. Yes — a license file (`.lic`).
2. Yes — a Base64-encoded license key.
3. No — I'll obtain one another way (a license I get elsewhere, or Senzing support).
4. No — request a free evaluation license now through the bootcamp.

Three-option form (when `submit_feedback` is unavailable):

👉 **Do you have a Senzing License Key? Reply with a number:**

1. Yes — a license file (`.lic`).
2. Yes — a Base64-encoded license key.
3. No — I need to obtain one.

*(Internal: end the turn on this question and wait. Do not proceed until the bootcamper
answers.)*

**Routing.** Options 1–2 → the corresponding Step 5c apply-a-license branch; option 3 → the Step 5c
no-license branch. Option 4 (four-option form only) → the Step 5c no-license branch, proceeding
directly with the in-flow `submit_feedback` `license_request` path (re-verify availability and
invoke once, per the existing Step 5c handling) rather than re-presenting the 5c sub-menu.

### 5c. Handle the response

**IF the bootcamper has a Base64-encoded license string:**

**🚨 NEVER ask the user to paste a license key into chat.** Direct them to decode the string to
`licenses/g2.lic` using the command for their platform:

**Linux / macOS:**

```bash
echo '<BASE64_STRING>' | base64 --decode > licenses/g2.lic
```

**Windows (PowerShell):**

```powershell
[System.Convert]::FromBase64String('<BASE64_STRING>') |
  Set-Content -Path licenses\g2.lic -AsByteStream
```

After decoding, verify the file is binary (not leftover text):

```bash
file licenses/g2.lic
```

The output should indicate a binary/data file, not ASCII text. If it shows text, the Base64
string may have been copied incorrectly.

Confirm: "License decoded and saved to `licenses/g2.lic`."

**IF the bootcamper has a `.lic` file directly:**

Guide them to copy it into the project:

```bash
cp /path/to/g2.lic licenses/g2.lic
```

Confirm: "License file placed at `licenses/g2.lic`."

**IF the bootcamper has no license:**

Confirm: "No problem, the built-in 500-record evaluation license is active automatically.
That's enough for the bootcamp demo modules."

If the bootcamper wants a license for larger datasets, present the licensing paths below.
**Consult the Senzing MCP server first:** call
`search_docs(query='larger evaluation license for datasets over 500 records')` and present the
returned guidance. (A `licenses/README.md` reference doc is a later porting phase; teach the
paths directly for now.)

**Check the in-flow option's availability before presenting choices.** Within this same
licensing interaction, call `get_capabilities` on the Senzing MCP server to determine whether
the `submit_feedback` tool is reported as available. Wait up to 30 seconds for a response, then
apply this decision:

- **`submit_feedback` reported available** → present all three licensing paths below (in-flow
  MCP request, external request, and apply-an-existing-license).
- **`submit_feedback` reported unavailable, an error response is returned, or no response
  arrives within 30 seconds** → omit the in-flow MCP request path, present only the external
  request and apply-an-existing-license paths, and tell the bootcamper the in-session
  license-request capability is unavailable for the current session.

Present the available paths as distinct, individually selectable options:

1. **Request an evaluation license through the MCP server (in-flow):** *present this option
   only when `submit_feedback` is reported available.* This path asks the Senzing MCP server to
   generate an evaluation license by invoking the `submit_feedback` tool with the
   `license_request` category. The evaluation license is delivered by email, and the email
   contains a download link. This option requires the `submit_feedback` tool, which the flow
   verifies is available before presenting it.
2. **Request a license through the external channel:** Contact <support@senzing.com> to
   request an evaluation license. Mention that you are using the Senzing Bootcamp and provide
   your name, organization, expected record count, and use case description. Expect a response
   within 1-2 business days. For production licenses, contact <sales@senzing.com>.
3. **Apply an existing license:** if you already have, or later obtain, a `.lic` file or
   Base64-encoded license string, follow the Step 5d configuration steps to save and wire it.

When presenting the evaluation license's validity period or record capacity, retrieve those
values from a Senzing MCP server tool during this session and present exactly what the tool
returns. If the tool does not return a value, or the MCP server cannot be reached, omit the
specific figure and tell the bootcamper the current value is unavailable from the MCP server.
Never substitute a hardcoded or remembered figure.

Ask the bootcamper which path they would like to take.

👉 **Which would you like to do? Reply with a number:**

1. Request through the MCP server (if available).
2. Request through the external channel.
3. Apply a license you already have.

*(Internal: end the turn on this question and wait.)*

Once the bootcamper responds, act on their choice:

- **In-flow MCP request:** if `submit_feedback` is not enabled/available, tell the bootcamper
  this option requires the `submit_feedback` tool and guide them to enable it in the Claude
  plugin's MCP config. After they confirm it is enabled, re-verify availability by calling
  `get_capabilities` again before invoking. If they decline to enable it, present only the
  remaining paths (external request and apply existing). When availability is confirmed, invoke
  `submit_feedback` exactly once with the `license_request` category. On a response with no
  error, tell the bootcamper the request was submitted, then walk them through the post-request
  sequence below. If the invocation returns an error or no response within 30 seconds, tell
  the bootcamper the license request did not complete, present the remaining paths (external
  request and apply existing), and do not automatically re-invoke `submit_feedback`.
- **External request:** request via the external channel above; follow the post-request
  sequence below once you have the license file.
- **Apply an existing license:** follow the configuration steps in Step 5d.

**After an evaluation-License-Key request (in-flow or external), walk the bootcamper through the
full post-request sequence** — and make clear the bootcamp **continues on the built-in evaluation
license** in the meantime, so they are never blocked waiting for the email:

1. **Wait for the email.** The Senzing License Key arrives by email at the address tied to the
   request; it can take some time.
2. **Download the key.** Save the attached/linked file from the email — it contains the
   Base-64-encoded License Key text.
3. **Provide the path.** Ask the bootcamper for the path to that downloaded file. Do NOT ask them
   to paste the key into chat.
4. **Decode to `licenses/g2.lic`.** Decode the Base-64 text from that file into the binary license
   using the platform command from Step 5c above (Linux/macOS `base64 --decode`, Windows
   `[System.Convert]::FromBase64String(...)`), reading from the provided file instead of an inline
   string, then verify it is binary with `file licenses/g2.lic`.
5. **Wire and detect.** Follow Step 5d (add `LICENSEFILE`) and Step 5e (detect the record limit).
   The emailed key can be applied whenever it arrives, even in a later session.

If at any point the bootcamper reveals they already have a Senzing License Key (or indicated in
Step 5b that they have a `.lic` file or Base64-encoded license key), omit the in-flow MCP
request option and route them to the apply-an-existing-license path in Step 5d.

If the bootcamper's response does not match any presented path, tell them the prior response
was not recognized, re-present the same options unchanged, and do not advance past Step 5c.

Record in `config/bootcamp_preferences.yaml`: `license: evaluation`.

### 5d. Configure LICENSEFILE in engine config

When a project-local license exists at `licenses/g2.lic`, add `LICENSEFILE` to the engine
config PIPELINE section:

```json
"PIPELINE": { "LICENSEFILE": "licenses/g2.lic" }
```

Record in `config/bootcamp_preferences.yaml`: `license: custom`.

If no custom license was placed, skip this: the SDK uses the built-in evaluation license
automatically.

### 5e. Detect the active license's record limit

**Only run this sub-step when a custom license was configured in Step 5d** (`license: custom`
in `config/bootcamp_preferences.yaml`, i.e., a `.lic` file was placed at `licenses/g2.lic`). If
no custom license was placed, skip 5e entirely: the built-in evaluation license needs no
detection, and later modules fall back to the evaluation capacity automatically.

When a custom license is active, read its real record limit now so every later capacity or
sampling decision (Modules 1, 4, and 6) uses the license the bootcamper actually supplied
instead of the built-in evaluation figure.

**Confirm the SDK facts from the Senzing MCP server first.** Do not rely on training data for
how `SzProduct.get_license()` behaves or what `recordLimit` means. Call
`sdk_guide(topic='configure', platform='<user_platform>', language='<chosen_language>', version='current')`
(and `search_docs` if needed) to confirm the `get_license()` call and that `recordLimit` is the
active cap, where **0 means no record cap (unlimited)** and a positive integer is the cap.

1. **Generate a scaffold that reads the license.** Start from
   `generate_scaffold(language='<chosen_language>', workflow='initialize', version='current')`
   and adapt it to call `SzProduct.get_license()` and print the returned JSON. Save that JSON to
   `config/license.json`.
2. **Persist the detected limit.** Parse `recordLimit` from `config/license.json` and write a
   `license_record_limit` field into `config/bootcamp_progress.json` (`0` = unlimited, positive
   = cap). (The Kiro bundled helper `detect_license_limit.py` encoded this parse-and-persist
   step; the script port is a later phase, so parse `recordLimit` and write the field directly
   for now.)
3. **Report the detected limit to the bootcamper.** Present exactly what was detected, for
   example, "Your license allows up to 50,000 records" or, when `recordLimit` is `0`, "Your
   license has no record cap (unlimited)." Once a custom license is active, do not restate the
   built-in evaluation figure as the authoritative limit.

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
2. **PostgreSQL** — better for production.

*(Internal: end the turn on this question and wait.)*

**For SQLite** (recommended for bootcamp):

- Create the database directory: `mkdir -p database` (Linux/macOS) or
  `New-Item -ItemType Directory -Force -Path database` (PowerShell).
- Database path: `database/G2C.db`.
- No additional setup needed: SQLite is built in.
- **IMPORTANT:** Never use `/tmp/` or in-memory databases. If `generate_scaffold` or
  `ExampleEnvironment` defaults to `/tmp/`, override the path to `database/G2C.db`.

**For PostgreSQL** (production):

- User needs PostgreSQL installed and running.
- Create a database for Senzing.
- Use `sdk_guide` with `topic='configure'` for PostgreSQL setup.

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
