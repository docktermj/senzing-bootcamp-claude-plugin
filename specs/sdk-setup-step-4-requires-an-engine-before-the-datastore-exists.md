# SDK setup Step 4 requires an engine before the datastore exists

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

SDK setup's Step 4 (Verify Installation) tells the guide to build a script that
"initialize[s] the Senzing engine **and** print[s] the version". On a correctly
installed, fully current SDK, that script **cannot succeed at Step 4**. Creating an
engine needs an engine configuration and a datastore holding a registered default
config — and those are built in Steps 7, 8 and 8a, three to four steps later.

The failure is not a clean "not configured yet" message. It is:

```text
SzBadInputError - SENZ7426|Transliteration failed: No transliteration rules found!
Transliteration requires at least one module.
```

which routes the Bootcamper straight into this module's own error handling
(`explain_error_code` first, per `SKILL.md:53-55`). That returns advice to check
`SUPPORTPATH`, and platform-specific fixes for macOS Homebrew and Windows Scoop —
sending someone with a perfectly healthy install to hunt a path problem that does
not exist. `explain_error_code('SENZ7426')` even names the symptom exactly:

> "Fails on getEngine()/getDiagnostic()/addRecord() while SzProduct keeps working
> (it needs no support data), so the install looks healthy"

That is precisely the Step 4 script: the `SzProduct` half prints 4.3.4 and the
engine half dies.

Worse, the module already knows where the engine call belongs. Its own success
indicator at `SKILL.md:43-44` reads: "an engine-class call (`SzEngine`/`SzDiagnostic`)
succeeds — a version query alone does not qualify (**Step 9**)". Step 9 is "Test
Database Connection", after the database and the seeded config exist. Step 4
duplicates Step 9's requirement four steps too early.

## Root cause

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:696-703` defines the
Step 4 script as engine-initialization **plus** version-print, and justifies the two
`generate_scaffold` calls by that pairing:

> "The script should initialize the Senzing engine **and** print the version to
> confirm the SDK is working. Those are two different `generate_scaffold`
> workflows, so it takes **two** calls"

The pairing is what is wrong, not the two-call rule. The two-call rule is correct
and well-evidenced (`workflow='initialize'` genuinely has no version snippet; the
version lives in `workflow='information'`). But `workflow='initialize'`'s snippets
are factory/engine **lifecycle**, and running any of them requires the datastore
that Step 7 creates and the default config Step 8a seeds.

Step order in the module: 4 Verify → 5 License → 6 Directory structure →
7 Configure database → 8 Engine configuration → 8a Seed default config →
9 Test database connection. Step 4 is the only one of these that needs an engine
and does not have one available.

### What actually happens, measured

Live on the dry-run machine, 2026-08-13, Senzing SDK **4.3.4** (build 4.3.4.26210),
`senzingsdk-runtime` 4.3.4-26210, Linux x86-64 — a healthy, current install:

| Script, run as Step 4 would | Result |
|---|---|
| `SzProduct.get_version()` | ✅ `4.3.4 (build 4.3.4.26210)` |
| `create_engine()`, `SENZING_ENGINE_CONFIGURATION_JSON` unset (Step 4's real state) | ❌ `SzBadInputError - SENZ7426` |
| `create_engine()` with `CONFIGPATH`/`RESOURCEPATH`/`SUPPORTPATH` from `sdk_guide` and `SQL.CONNECTION=internal://` | ❌ `SzConfigurationError - SENZ7220\|No engine configuration registered in datastore` |

The second row is Step 8's work; the third is Step 8a's. Both failures are the
step order, not the install. Reproduced identically with the PyPI bindings and with
the SDK-shipped bindings at `/opt/senzing/er/sdk/python`, so it is unrelated to
`specs/senzing-python-sdk-must-not-be-pip-installed.md`.

MCP calls made: `generate_scaffold(language='python', workflow='information',
version='current')` and `workflow='initialize'` (server 1.32.9, 2026-08-13),
`explain_error_code(error_code='SENZ7426', version='current')`,
`sdk_guide(topic='install', platform='linux_apt', language='python')`.

## Proposed change

1. **Narrow Step 4 to what it can actually verify: the language binding loads and
   the SDK answers.** That is the `SzProduct.get_version()` half — the factory
   constructs, the native library loads, the binding is wired. Say plainly that
   this is a *binding* check, not an engine check, and that the engine-class call
   is Step 9's job, citing `SKILL.md:43-44`'s own success indicator.
2. **Keep the two-call rule and its evidence**, but re-purpose it: the
   `workflow='initialize'` call is what tells the guide the factory/lifecycle
   shape it will need at Steps 8–9, not what Step 4 executes. If nothing at Step 4
   uses those snippets, drop the second call from Step 4 and move it to Step 8,
   preserving the ⛔ that `workflow='initialize'` alone cannot print a version.
3. **Add the expected-failure note either way.** If a guide does attempt an engine
   call before Step 7, `SENZ7426` and `SENZ7220` are the *expected* results, not
   defects — say so, so the module's error handling is not entered for a
   configuration step that has simply not run yet. This is the same class as
   INV-163: name what you could not verify rather than reporting a false negative.
4. Consider whether Step 9's success indicator should be restated at Step 4 as
   "deferred to Step 9", so a reader of Step 4 alone cannot conclude the engine
   must work here.

## Acceptance criteria

- [ ] Step 4 verifies the binding and version only, and states that the
      engine-class call is Step 9's.
- [ ] Following Step 4 on a healthy install with no database configured produces a
      pass, not `SENZ7426`.
- [ ] The two-`generate_scaffold`-call evidence is preserved wherever the
      `initialize` snippets are actually needed, including the ⛔ that
      `workflow='initialize'` prints no version.
- [ ] The module says `SENZ7426` and `SENZ7220` before Step 7 mean "not configured
      yet", so the SENZ-code error path is not entered for them.
- [ ] `SKILL.md:43-44`'s success indicator and Step 4 no longer disagree about
      where the engine-class call happens.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The failure is not Python-specific — it is the engine's support/config data,
      which every binding needs.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 4's script
  definition; the placement of the `workflow='initialize'` call; the
  expected-failure note.

## Source

- Feedback: dry run phase 3, 2026-08-13 — executed Step 4 for real on a machine
  with Senzing 4.3.4 installed and current (`Source: self-observed (assistant
  retrospective)`)
- Priority: **High** — it breaks a documented path, and the failure misdirects: a
  healthy install produces an error whose documented remediation is to go chasing
  `SUPPORTPATH`.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13. `generate_scaffold` confirmed to return a listing with no inline code
  (the plugin's ⛔ at `:725-731` is accurate), `workflow='initialize'` confirmed to
  carry no version snippet (14 snippets under `python/initialization/` and
  `python/configuration/`), and `explain_error_code('SENZ7426')` confirms the
  SzProduct-works-while-engine-fails signature. Still reproduces.
- Upstream: not applicable — the server is right; the plugin's step order is the
  problem.
- Related specs: `specs/senzing-python-sdk-must-not-be-pip-installed.md` (same
  module, independent defect — this one reproduces with both binding sets)
