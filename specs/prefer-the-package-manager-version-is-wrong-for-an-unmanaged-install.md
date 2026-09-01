# "Prefer the package manager's version string" is wrong for an install the package manager does not own

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md` Step 1b → "Comparing the two versions" resolves the disagreement
between the two version sources with an unconditional rule:

> **Prefer the package manager's version string**; when only the JSON is available, normalize the
> separator before comparing.

The section's worked example is a **separator** artifact — `4.3.3-26191` from `dpkg-query` versus
`4.3.3.26191` from `szBuildVersion.json`, the same version written two ways — and for that case the
rule is right. But it is stated unconditionally, and it is wrong whenever the SDK on disk was not
put there by the package manager.

Observed live on 2026-08-31, Ubuntu 24.04.4:

| Source | Value |
|---|---|
| `dpkg-query -W -f='${Version}' senzingsdk-runtime` | `4.3.4-26210` |
| `apt-cache policy senzingsdk-runtime` → Candidate | `4.3.4-26210` |
| `/opt/senzing/er/szBuildVersion.json` → `BUILD_VERSION` | `4.4.0.26242` (built `2026_08_30__22_20`) |

Normalizing the separator gives `4.3.4.26210` versus `4.4.0.26242` — a genuine version difference,
not a formatting one. The library that will actually load from
`/opt/senzing/er/lib/libSz.so` is the **4.4.0** one; `dpkg` describes a package whose files are no
longer what is there.

**The authoritative route settles it.** Once Step 3's environment script exported
`PYTHONPATH` and `LD_LIBRARY_PATH`, `SzProduct.get_version()` — the primary route Step 1 names —
returned `VERSION: 4.4.0`, `BUILD_DATE: 2026-08-30`, `BUILD_NUMBER: 2026_08_30__22_20`. That agrees
with `szBuildVersion.json` and disagrees with `dpkg-query`, confirming that the package manager is
describing a package whose files are no longer the ones that load.

Following the rule as written reports the installed version as **4.3.4-26210**. Step 1 then tells
the Bootcamper *"Senzing SDK is already installed (version 4.3.4-26210)"* — a wrong number, stated
as fact, about the thing this whole module exists to establish.

**This is not only a developer-machine artifact.** The route that produces it is one the server
itself documents. `sdk_guide(topic='install', platform='linux_apt')` carries, on server 1.35.1:

> If you cannot run `apt install` (containers, CI, no sudo), extract the packages directly instead:
> `dpkg-deb -x senzingsdk-runtime_*.deb /opt/senzing && dpkg-deb -x senzingsdk-setup_*.deb /opt/senzing`

On that route `dpkg-query` reports **nothing at all**, because no package was ever registered — and
`szBuildVersion.json` is the only correct source. The rule sends the guide to the source that is
empty and away from the one that is right, in an environment class (containers, CI, no sudo) the
server calls out explicitly.

## Root cause

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md`, Step 1b → "Comparing the two
versions". The section was written from a single observation — "a real 4.3.3-26191 install,
2026-07-31" — where the only discrepancy available to observe was the separator. The rule
generalizes that one case into a precedence order between two sources that can disagree for a
second, entirely different reason.

Two nearby pieces of the file already know better and are not connected to it:

- Step 1's version-reading guidance names the **primary** route as the language version check or
  `SzProduct.get_version()`, with `szBuildVersion.json` as the fallback — the package manager is not
  in that chain at all.
- Step 1b's own INV-163 clause already treats "an install that no package manager owns" as an
  **unknown** case — but only for the *available* version, never for the *installed* one.

The failure is reachable precisely when the primary route is unavailable, which is common: on this
machine `SzProduct.get_version()` could not run at Step 1, because the import fails until Step 3's
environment script exports `LD_LIBRARY_PATH`.

## Proposed change

1. Restate the precedence so it resolves the case it was written for without over-reaching.
   Suggested shape:

   > The two sources disagree for two different reasons, and only one of them is cosmetic.
   > **Same version, different separator** — `4.3.3-26191` vs `4.3.3.26191` — is a formatting
   > artifact: normalize and treat them as equal. **Genuinely different values** mean the install on
   > disk is not the one the package manager records — an extracted, POC or hand-placed install —
   > and then `szBuildVersion.json` describes what will actually load, so it wins.

2. Add one line stating that where `dpkg-query` / `rpm -q` returns nothing, the install is not
   package-manager-owned; that is not "not installed", and `szBuildVersion.json` is the source.

3. Point the reader back at `SzProduct.get_version()` as the tiebreaker once Step 3's environment
   script has run, since that is authoritative for the library that loads and is reachable by then
   even when it was not at Step 1.

## Acceptance criteria

- [ ] The section distinguishes a separator-only difference from a genuine version difference, and
      prescribes a different resolution for each.
- [ ] Where the package manager reports no version, the guide reads `szBuildVersion.json` rather
      than concluding the SDK is absent or reporting an empty version.
- [ ] The version reported to the Bootcamper at Step 1 is the one belonging to the library that will
      load.
- [ ] The existing separator guidance and its dated observation are preserved, not deleted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 1b, "Comparing the two
  versions".

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, SDK setup Step 1b
  (`Source: self-observed (assistant retrospective)`) — found by running Step 1b's own plugin-owned
  commands on a machine where the two sources genuinely disagree.
- Priority: Low
- MCP re-check: server **1.35.1**, 2026-08-31 —
  `sdk_guide(topic='install', platform='linux_apt', language='python')` documents the `dpkg-deb -x`
  extraction route for containers/CI/no-sudo, which is the generalizing case: on it no package is
  registered and `dpkg-query` has nothing to report.
  owner-checked: not required — this spec asserts the plugin's precedence rule is wrong, not that the
  server lacks anything.
- Upstream: not applicable
- Related specs: `specs/step-1-says-skip-step-3-entirely-then-says-not-entirely.md` — same step, and
  the reason the primary version route was unavailable here.
- ⚠️ Representativeness caveat, recorded deliberately: the machine this was found on carries 32 POC
  SDK builds and is not a typical Bootcamper environment. The *mechanism* generalizes (the server
  documents the extraction route), but the specific 4.3.4-vs-4.4.0 split is a maintainer-box artifact
  and should not be cited as a Bootcamper-facing frequency claim.
