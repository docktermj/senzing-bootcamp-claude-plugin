# An already-installed V4 SDK is accepted as-is, with no check for a newer release and no offer to update

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`module-02-sdk-setup/SKILL.md` Step 1 detects an existing install and, for anything V4.0+,
stops looking:

```text
:85  **If the SDK is found and version is V4.0+:**
:87  Tell the user: "Senzing SDK is already installed (version [X]). No need to reinstall,
:88  skipping straight to configuration verification."
:90  - Skip Steps 2 and 3 entirely.
```

It reads the installed version and then only compares it against the **V4.0 floor**. A
Bootcamper on an older 4.x build is told "no need to reinstall" and never learns a newer
release exists, let alone gets offered it. The only upgrade branch that exists is for
`<V4.0` (`:104-106`).

A Bootcamper who wants to be current has to know to ask, and the bootcamp — whose whole
premise is guiding someone through Senzing — says nothing.

## What the server can and cannot answer

Verified 2026-07-31 against MCP server 1.32.2, docs indexed 2026-07-29 11:11 UTC. This
matters more than usual, because the obvious place to look does **not** have the answer.

**⛔ `get_capabilities` cannot answer it.** `server_info.senzing_version` is the string
`"current"` — not a version number. Concluding from that alone that the server cannot report
a version would be the INV-194 mistake.

**✅ `sdk_guide(topic='install', platform='linux_apt')` can.** Its `direct_download.packages`
array carries exact versioned filenames, each with a `sha256` and `size`:

```text
senzingsdk-runtime_4.3.3-26191_amd64.deb   sha256 451907b0…  (also arm64)
senzingsdk-setup_4.3.3-26191_amd64.deb     sha256 c8d1cf0a…  (also arm64)
senzingsdk-tools_4.3.3-26191_amd64.deb     sha256 42266d3e…  (also arm64)
install_command: sudo apt install ./senzingsdk-runtime_4.3.3-26191_amd64.deb
```

So "what is available" is `4.3.3-26191`, obtainable from the filename.

**The installed side is directly comparable — after one normalization.** Observed on a real
install in this environment, 2026-07-31:

| Source | Value |
|---|---|
| `dpkg-query -W -f='${Version}' senzingsdk-runtime` | `4.3.3-26191` |
| `direct_download` filename | `4.3.3-26191` |
| `/opt/senzing/er/szBuildVersion.json` → `BUILD_VERSION` | `4.3.3.26191` |
| `/opt/senzing/er/szBuildVersion.json` → `VERSION` | `4.3.3` |

⚠️ **`szBuildVersion.json`'s `BUILD_VERSION` uses a dot where the package version uses a
hyphen** (`4.3.3.26191` vs `4.3.3-26191`). Comparing those two raw strings reports a
difference where none exists. Step 1 currently reads its version from exactly this file
(`:81`), so this is the trap the implementation will walk into first.

**⛔ Availability is Linux-only.** `direct_download` is returned for `linux_apt` and
`linux_yum` only. `sdk_guide(topic='install', platform='macos_arm', language='python')`
returns **no install commands and no `direct_download` at all** — only a
`compatibility_notes` entry stating the Python SDK is Linux-only and pointing at Java, C#,
Docker or WSL2. So on macOS and Windows there is no server-reported version to compare
against, and the check must report itself **skipped** rather than silently passing (INV-163).

**⛔ There is no documented 4.x → 4.y update procedure, and this is the real risk.**
`search_docs(query='upgrade Senzing to a newer version existing installation')` returns only
**V3→V4 migration** material: the FAQ checklist (install V4 packages, `sz_dbupgrade` for the
schema, `sz_configupgrade` + `sz_configtool` for the config, verify with `sz_command`) and the
v4 breaking-changes pages. `sdk_guide` has no `upgrade` topic — its topics are install,
configure, load, export, redo, initialize, search, stewardship, delete, information,
error_handling, full_pipeline.

Whether a **point-release** update needs any of those schema/config steps is **not documented
and not verified**. Replacing binaries under a repository whose schema and config were created
by an older build is exactly the shape of change that breaks a working environment quietly.
The implementation must not invent a procedure to fill that gap.

## Root cause

Step 1's version check has one job — gate on the V4.0 floor — and was never asked a second
question. "Is it new enough to work?" and "is it the newest available?" are different
questions, and only the first has ever been asked. Nothing was wrong when it was written;
the omission only became visible once the server started publishing exact package versions
in `direct_download`.

## Proposed change

Add an update **offer** to Step 1's V4.0+ branch. Offer, not action: a working install stays
working unless the Bootcamper says otherwise.

1. **Determine the installed version**, preferring the package manager over the JSON file
   where available (`dpkg-query`/`rpm -q` give the same `4.3.3-26191` form the server
   publishes, so no normalization is needed). Fall back to `szBuildVersion.json`'s
   `BUILD_VERSION` and **normalize the separator** before comparing.
2. **Determine the available version** from `sdk_guide(topic='install', platform=…)`'s
   `direct_download` filenames. Where the platform returns no `direct_download` — macOS,
   Windows, Docker — **skip the check and say so** (INV-163). Do not guess, and do not treat
   "no data" as "up to date".
3. **When, and only when, the available version is newer, make one offer.** A single 👉
   question, its own turn, and the answer is genuinely optional (INV-012):

   > 👉 **Senzing 4.3.3-26191 is available and you have 4.3.2-xxxxx installed — would you
   > like to update?** (reply no to keep your current version; you can also name a specific
   > version)

   Accepting takes the latest by default. If the Bootcamper names a version instead, install
   that one — the `direct_download` URLs are versioned, which is the documented version-exact
   route. ⛔ Do **not** claim `apt install pkg=version` pinning works: the server does not
   document it.
4. **Declining is a first-class outcome.** On no, say one line confirming the current version
   is kept and continue to Step 4 exactly as today. No re-ask (INV-006), no repeat next
   session, nothing recorded as a problem.
5. **An update is an install, so the install rules all apply.** The EULA question at `:207-212`
   must be asked before any package is installed — the server's own `install_commands` say to
   ask before running the EULA export. Verify the `sha256` the server supplies for each
   downloaded package. And `direct_download` needs `mcp.senzing.com` reachable, with no inline
   fallback if it is not.
6. **State the undocumented-procedure risk in the offer, honestly and briefly.** The
   Bootcamper is agreeing to replace a working SDK, and the server documents no point-release
   procedure. Say that verification will re-run afterwards and that the fallback is
   reinstalling the version they had. Do not imply a schema or config migration is known to be
   unnecessary — it is simply undocumented.
7. **Re-verify after any update, and never leave a half-updated environment silently.** Step 4
   already exists and is a required stop; route through it. If verification fails after an
   update, say so plainly, name the previously-working version, and do not report Module 2
   complete.
8. **Never block.** A failed check, an unreachable download, or a failed update must warn and
   continue with the working install (INV-048). This is an improvement to a working state, not
   a prerequisite.

## Acceptance criteria

- [ ] Step 1's V4.0+ branch compares the installed version against the version the server
      publishes, instead of only against the V4.0 floor.
- [ ] The comparison normalizes `szBuildVersion.json`'s `4.3.3.26191` against the package
      form `4.3.3-26191`, so an up-to-date install is never reported as out of date. A test
      asserts this specific pair.
- [ ] The available version comes from `sdk_guide`'s `direct_download` filenames, and the
      guidance does **not** cite `senzing_version` for it (it is the string `"current"`).
- [ ] On a platform with no `direct_download`, the check is reported **skipped**, naming the
      platform, and "no data" is never rendered as "up to date" (INV-163).
- [ ] When a newer version exists, exactly **one** 👉 question offers the update, and it ends
      its turn (INV-005/INV-012).
- [ ] Declining keeps the install, says so in one line, and proceeds to Step 4 unchanged —
      with no re-ask and nothing recorded as a failure.
- [ ] Accepting installs the latest by default, or a Bootcamper-named version via the
      versioned `direct_download` URL. No `apt install pkg=version` pinning is claimed.
- [ ] The EULA question is asked before any package installs, reusing the existing wording at
      `:207-212` rather than a second copy.
- [ ] The `sha256` the server supplies is verified for each downloaded package before it is
      installed.
- [ ] The offer states that no 4.x→4.y procedure is documented, and does not assert that
      schema/config migration is unnecessary.
- [ ] After an update, Step 4 verification re-runs; on failure the previously-working version
      is named and Module 2 is not marked complete.
- [ ] Nothing in this path can block Module 2 (INV-048) — a failed check or download warns and
      continues on the working install.
- [ ] **MCP re-check clause:** implementing this requires `sdk_guide(topic='install',
      platform='linux_apt')` to still return `direct_download` with versioned filenames. If
      that field is gone, the availability half is unimplementable and only the skip-and-say-so
      path should ship. Re-ask before writing code; `4.3.3-26191` is a value that will change.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      noting that "holds" on macOS/Windows means the check correctly reports itself skipped.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 1's V4.0+ branch (`:85-95`), and the EULA reuse at `:207-212`.
- `tests/` — the version-normalization assertion, the skipped-platform assertion, and the one-question/declining-is-safe assertions.

## Source

- **Requested by the maintainer**, 2026-07-31: "In the SDK setup module, if a Bootcamper
  already has Senzing installed, and there is a newer version of Senzing available, offer to
  update the installed Senzing. Allow the Bootcamper to accept or reject the offer. If the
  Bootcamper accepts the offer, update the installed version to the latest version or to a
  specific versioned release, if requested by the Bootcamper."
- Priority: Medium. It is an improvement to a working state, not a defect — which is also why
  every failure path continues rather than blocks.
- MCP re-check: server 1.32.2, docs indexed 2026-07-29 11:11 UTC, verified 2026-07-31. Tools
  called: `get_capabilities` (`senzing_version` is `"current"`, not a number),
  `sdk_guide(topic='install', platform='linux_apt', language='python')` (`direct_download`
  carries `4.3.3-26191` filenames with sha256), `sdk_guide(topic='install',
  platform='macos_arm', language='python')` (no install commands, no `direct_download`),
  `search_docs(query='upgrade Senzing to a newer version existing installation')` (V3→V4
  migration only — no 4.x→4.y procedure), `get_sdk_reference(topic='response_schemas',
  filter='get_version')` (empty `data`; `SzProduct.get_version()` returns a plain string whose
  shape the server does not document — INV-149).
- **Observation-only, not an MCP fact:** the `szBuildVersion.json` contents and the
  `dpkg-query` output above were read from the install in this development environment
  (`4.3.3-26191`, build `2026_07_10__01_27`). They are an environment observation with their
  date, never laundered into an MCP-sourced claim (INV-080).
- ⚠️ **Not runtime-verifiable here:** this environment is already current (installed
  `4.3.3-26191` == available `4.3.3-26191`), so the newer-version-available branch cannot be
  exercised. The implementation must disclose that rather than tick it.
- Upstream: worth considering separately — the absence of a documented 4.x→4.y update
  procedure is a genuine coverage gap, and `sdk_guide` has no `upgrade` topic. Not filed by
  this spec.
- Related specs: `specs/show-plugin-version-and-record-environment.md` (version reporting
  discipline), `specs/robust-fpdf2-install.md` (INV-066 — an install that degrades rather than
  blocks), `specs/why-entities-default-flags-has-no-composite-members.md` (INV-194 — one
  tool's silence is not the server's, which is exactly why `senzing_version` being `"current"`
  did not end this investigation).

## Deviations from this spec, and why (2026-07-31)

**⚠️ This spec's central platform claim was wrong, and the maintainer caught it.** It states that
availability is obtainable on Linux only, and that macOS and Windows must report the check
**skipped**. Both halves are false.

The error was mine and it is instructive: I asked
`sdk_guide(topic='install', platform='macos_arm', language='python')` and got no install commands
and no `direct_download` — only a note that the Python SDK is Linux-only. I read that as *the
platform* having no install path. It is a **language** dead end. Asked with `language='java'`,
macOS returns a complete Homebrew-cask install path, and Windows returns a complete Scoop one.
That is the INV-194 lesson for the third time in this session: one tool *and its parameters*
answering nothing is not the server answering nothing. The spec was written on a
single-parameter-set conclusion, which is exactly what INV-194 forbids.

**What shipped instead: four mechanisms, because the package manager is the availability oracle
on every platform — not the MCP server.** Verified 2026-07-31, server 1.32.2:

| Platform | Installed | Available | Update |
|---|---|---|---|
| `linux_apt` | `dpkg-query -W` | `apt-cache policy` | `apt install` (+ versioned `direct_download` for version-exact) |
| `linux_yum` | `rpm -q` | `yum check-update` (`dnf` on RHEL 8+) | `yum install` |
| `macos_arm` | `brew info --cask` | `brew outdated --cask` | `brew upgrade --cask` |
| `windows` | `scoop info` | `scoop status` | `scoop update` |
| `docker` | — | — | none in place; the **image tag is the version** |

Five further things the spec did not know, all found while implementing:

1. **`linux_yum`'s `direct_download` is wrong for its own platform.** It returns **`.deb`**
   packages with `sudo apt install` commands. The spec asserted `direct_download` as a yum route;
   it is the apt/firewalled route only, and Step 1b now says so.
2. **macOS: a zero exit code from `brew` does not mean it installed.** With a wrong EULA variable
   the cask prints "No interactive terminal detected", purges the download, and **still prints its
   Caveats block listing install paths** — so it reads as success while installing nothing. This
   makes post-update artifact probing mandatory rather than advisory, and it is the single most
   dangerous thing about updating on macOS.
3. **The EULA variable differs per platform, and a wrong one is silently ignored** —
   `SENZING_ACCEPT_EULA=I_ACCEPT_THE_SENZING_EULA` on Linux and Windows, but
   `HOMEBREW_SENZING_ACCEPT_EULA=i_accept_the_senzing_eula` (**lowercase**) on macOS. The spec
   treated the EULA as one reusable question; the question is reusable, the variable is not.
4. **macOS `SENZING_ROOT` can move between versions.** The server's own upgrade note (for the
   unofficial tap) records the path changing, so env vars must be re-exported after an update
   rather than assumed.
5. **On Windows `szBuildVersion.json` is not under `%SENZING_DIR%`** — it installs to the
   *sibling* `data` directory. The spec's normalization advice was right but its location
   assumption was Linux-shaped.

**Criteria affected.** The criterion "on a platform with no `direct_download`, the check is
reported skipped, naming the platform" is **satisfied differently than written**: skipping is now
the fallback for *any* platform where the version cannot be determined, not the standing outcome
for macOS and Windows — which have real mechanisms. Every other criterion holds as written.

**Not runtime-verified, and disclosed rather than ticked:** this environment is Linux with
`4.3.3-26191` installed and `4.3.3-26191` available, so the **newer-version-available branch never
fires here**. The comparison inputs were read from the real install (`dpkg-query`,
`szBuildVersion.json`); the offer, the accept path, and every non-Linux mechanism are unexercised.
Exercising them needs a macOS or Windows machine, or an install deliberately held one release back.

**On the mutation testing:** two of ten mutations initially reported a missing target rather than a
passing test, because the phrases they aimed at are line-wrapped in the source. Re-run against the
wrapped forms, both are caught — 10 of 10. Worth noting since a "target missing" line looks like an
escaped mutation at a glance, and this is the second time this session that has happened.

## Invariants introduced

- None. INV-005/INV-006/INV-012 (one question, ask once, no needless interruption), INV-048 (never
  block), INV-129 (verify the artifact, not the exit code), INV-163 (report a skipped check) and
  INV-080/INV-194 (provenance, and one tool's silence is not the server's) all already applied and
  are asserted here rather than extended.

## Upstream: feature request sent 2026-07-31

Sent via `submit_feedback(category='feature')` after maintainer approval.
⛔ **Do not re-file.** Subject: **no documented procedure for updating an existing v4 install to
a newer v4 release (4.x → 4.y).**

Sent as `feature` rather than `bug` because nothing the server *returns* is wrong — a topic and
its documentation do not exist, which is coverage.

What the report carried, all re-confirmed the same day rather than recalled:

- `sdk_guide(topic='upgrade', platform='linux_apt')` → `MCP error -32603: Unknown topic
  'upgrade'`, with the full valid-topic enumeration quoted (install, configure, load, export,
  redo, initialize, search, stewardship, delete, information, error_handling, full_pipeline).
- **Two** differently-worded `search_docs` queries, the second deliberately point-release
  specific, both returning only V3→V4 material — so the absence is a corpus gap, not a phrasing
  artifact (INV-194's bar for asserting absence).
- Evidence it is not hypothetical: the server publishes `senzingsdk-runtime 4.3.3-26191` for
  Linux via `direct_download` while its own macOS guidance references cask **4.4.0.26206**, so a
  4.3 → 4.4 step exists in the field today with nothing documenting it.
- Four specific questions Senzing can answer directly (does it need `sz_dbupgrade`? does it need
  `sz_configupgrade` + `sz_configtool`? is package replacement sufficient, and for every 4.x→4.y
  pair or only within a minor line? any ordering constraint against a populated repository?), a
  suggested home (`topic='upgrade'`, or an upgrade section under `topic='install'`), and a
  three-step reproduction.

Anonymous, so **no reply is possible**; the server directs follow-up to support@senzing.com.

**Re-check on the next sweep:** if `sdk_guide` gains an `upgrade` topic, or `search_docs` starts
returning 4.x→4.y content, Step 1b's "Senzing documents no 4.x → 4.y update procedure" paragraph
is stale and must be replaced with the documented steps.

**Not filed, and still open:** `sdk_guide(topic='install', platform='linux_yum')` returns a
`direct_download` block whose packages are **`.deb` files with `sudo apt install` commands**,
which cannot work on an rpm system (verified 2026-07-31, server 1.32.2). That is a separate
subject and a `bug` rather than a `feature`; it was deliberately not bundled into this
submission, because two subjects in one message makes both harder to action. Step 1b already
warns readers off that field on yum.
