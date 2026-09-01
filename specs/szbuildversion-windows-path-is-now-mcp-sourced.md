# SDK setup calls the Windows `szBuildVersion.json` path an "environment observation, not an MCP-sourced fact" — the server now states it outright

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:99-105` gives the fallback route
for reading the SDK build version, then labels its own provenance:

> build metadata sits in `szBuildVersion.json`: on Linux under `/opt/senzing/er/` (and also
> `/opt/senzing/data/`), and on Windows in the **sibling** `data` directory, not under
> `%SENZING_DIR%` […] ⚠️ Those are **environment observations, not MCP-sourced facts** (Linux
> observed 2026-08-13; the macOS location is unknown) […]

The Windows half of that caveat is no longer true. As of server 1.35.1,
`sdk_guide(topic='install', platform='windows')` states the path itself, in a `gotchas[]` entry:

> SUPPORTPATH IS NOT UNDER `%SENZING_DIR%`. Scoop sets `SENZING_DIR=<scoop-app-dir>\er`, but the
> support data (`address_datamodel`, `*TransRules.sz` transliteration modules,
> **`szBuildVersion.json`**) installs to `<scoop-app-dir>\data` — a SIBLING of `er`, not a child.
> Use `%SENZING_DIR%\..\data`. […] Verified against the MSI Directory table for 4.3.3.26191
> (`ProgramFiles64Folder\Senzing\{data,er}`).

So the plugin's Windows path is **correct and MCP-sourced**, and is labeled as neither.

This matters more here than a stale caveat usually would, because INV-080 routes every Senzing
fact through the MCP server and the ⚠️ is what tells a reader which side of that line a
statement sits on. Mislabeling a served fact as a local observation degrades in two directions:
a guide that hits a mismatch has no reason to re-ask the server for the authoritative answer,
and a reader who trusts the ⚠️ discounts a path the server would confirm. The same paragraph is
the fallback the step reaches for *after* the SDK route fails, so it is consulted exactly when
the Bootcamper is already stuck.

The other two thirds of the caveat are fine and should stay:

- **macOS is still genuinely unknown.** `sdk_guide(topic='install', platform='macos_arm')`
  names no `szBuildVersion.json` anywhere (re-asked 2026-08-31, server 1.35.1); it names
  `address_datamodel`, `nomicon` and the `*TransRules.sz` modules as the support data under
  `$(brew --prefix)/opt/senzing/data`, and stops there.
- **Linux is still an environment observation, and it still holds.** Re-verified on this box
  2026-08-31 against a real 4.4.0 install: `/opt/senzing/er/szBuildVersion.json` and
  `/opt/senzing/data/szBuildVersion.json` both exist, both reading
  `{"PLATFORM":"Linux","VERSION":"4.4.0","BUILD_VERSION":"4.4.0.26242","BUILD_NUMBER":"2026_08_30__22_20"}`.
  No MCP route states it — `sdk_guide(topic='install', platform='linux_apt')` gives
  `default_paths` and a `ls /opt/senzing/er/lib/libSz.so` verification step and never mentions
  the file.

## Root cause

The paragraph was written 2026-08-13 against server 1.32.9, when no route carried any
`szBuildVersion.json` location, so a single blanket ⚠️ covering all three platforms was
accurate. The server has since gained the Windows path, and the caveat is phrased per-paragraph
rather than per-platform, so there is no way for it to become half-true — it simply became
wrong for one platform while reading as though it had been reviewed.

The `MCP-NEGATIVE` marker on the following line (`SKILL.md:107`) is **still true** and is not
the defect: it is scoped to `search_docs`, and `search_docs` still returns no file location on
any platform (re-asked 2026-08-31). Its `owner:` clause — "the SDK route is where the reader
must go" — is now *incomplete* rather than wrong: for Windows the fact is also served directly
by `sdk_guide(topic='install', platform='windows')`.

## Proposed change

1. **Split the ⚠️ per platform** at `SKILL.md:103-105`:
   - Windows — cite `sdk_guide(topic='install', platform='windows')` as the source, dated, the
     way other MCP-sourced facts in this file are cited. Drop it from the observation list.
   - Linux — keep as an environment observation; restamp the observation date to 2026-08-31
     and name the version it was observed against (4.4.0.26242), since the old note says only
     "Linux observed 2026-08-13".
   - macOS — keep "unknown", and name the route that was asked and came back without it, so the
     next reader does not re-ask the same question blind.
2. **Extend the `MCP-NEGATIVE` marker's `owner:` clause at :107** to record that the Windows
   path is served by `sdk_guide(install, windows)` while the `search_docs` claim is unchanged.
   Do not weaken or delete the claim — it still holds.

## Acceptance criteria

- [ ] The Windows `szBuildVersion.json` location at `SKILL.md:103` is attributed to
      `sdk_guide(topic='install', platform='windows')` with a server version and date, and is no
      longer listed under the "environment observations, not MCP-sourced facts" ⚠️.
- [ ] The Linux location remains an observation, restamped 2026-08-31 against 4.4.0.26242.
- [ ] The macOS location remains "unknown" and names the route that was asked
      (`sdk_guide(topic='install', platform='macos_arm')`).
- [ ] The `MCP-NEGATIVE` marker at :107 still asserts the `search_docs` claim unchanged, with an
      `owner:` clause recording the Windows route that does carry it.
- [ ] A repo-level test asserts the three platforms are attributed separately in this paragraph
      — one blanket provenance caveat spanning platforms is what allowed a half-stale note to
      read as reviewed. Negative-controlled: collapse the three back into one ⚠️ and confirm the
      test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the ⚠️ at :99-105 split per
  platform; the `MCP-NEGATIVE` `owner:` clause at :107 extended
- `tests/test_build_version_provenance_is_per_platform.py` — new guard

## Source

- Feedback: none — found by `/dry-run` phase 1 on 2026-08-31 while re-asking the `SKILL.md:107`
  negative against server 1.35.1 (`Source: self-observed (assistant retrospective)`)
- Priority: Low — the shipped path is correct; only its provenance label is wrong. It is worth
  fixing because this file's provenance discipline is what INV-080 rests on.
- MCP re-check: server 1.35.1, 2026-08-31 — **server now carries a fact the plugin says it does
  not**, for Windows only. Tools called: `sdk_guide(topic='install', platform='windows')` (names
  `szBuildVersion.json` under `<scoop-app-dir>\data`); `sdk_guide(topic='install',
  platform='macos_arm')` (names it nowhere); `sdk_guide(topic='install', platform='linux_apt')`
  (names it nowhere); `search_docs(query='szBuildVersion.json build version file location')`
  (ten hits, no path on any platform — the :107 claim still holds).
  owner-checked: `sdk_guide(topic='install', platform=<that platform>)` IS the route that would
  carry a per-platform support-data path — asked for all three; Windows returns it, macOS and
  Linux do not.
- Upstream: not applicable — the server is correct here; the plugin's label is what is stale
- Related specs: `mcp-negative-markers-carry-rationale-nothing-reverifies.md`

## Deviations from this spec, and why (2026-09-01)

**None to the substance — every claim was re-asked rather than carried over.** The spec was written
against server 1.35.1; all three routes were asked again on **1.35.3, 2026-09-01**, and all three
answers hold: Windows serves the path in `gotchas[]`, macOS names the support data without it, and
`linux_apt` never mentions it. The Linux **observation** was also re-taken on this machine rather
than restamped from the spec — both files present, identical, `BUILD_VERSION 4.4.0.26242`. Re-dating
an observation without re-observing it is the defect
`specs/mcp-negative-markers-carry-rationale-nothing-reverifies.md` addresses, and this spec is one
of the ones that report named.

**The rule was deferred rather than cited, and two candidate citations were rejected.** INV-080
states that Senzing facts come from MCP; INV-149 governs empty `response_schemas` results. Neither
says anything about the **granularity** at which provenance is recorded, which is the entire rule
here — so citing either would have been the wrong-citation class rather than a shortcut.

⚠️ **The guard tripped an existing guard, which is worth recording.** `test_dated_negatives_are_marked`
reported the new test file as carrying two malformed `MCP-NEGATIVE:` markers, because it quotes that
token as a **locator** to find the real marker in `SKILL.md` and assert its `owner:` clause.
Resolved with the sanctioned `MCP-NEGATIVE-SCAN: ignore-file` opt-out plus a note saying why: the
docstring's absence claims duplicate the ones the real marker already carries, and it is the marker
— not the test — that belongs on the re-ask worklist.
