# Senzing Python SDK must not be pip-installed

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 2 Phase 3 Step 3 instructs the bootcamper to install the Senzing Python SDK
with `python3 -m pip install senzing`. The live Senzing MCP server flags exactly
that command as an **error-severity anti-pattern**: the `senzing` and `senzing_core`
packages ship *inside* `senzingsdk-runtime` at `/opt/senzing/er/sdk/python`, and the
PyPI packages of the same name are, in the server's words, "for unsupported community
projects only".

The failure is silent and deferred. `pip install senzing` succeeds, so Module 2
reports a clean install; the PyPI packages then **shadow** the SDK-shipped ones on
`sys.path`, and the breakage surfaces one module later as an import that cannot find
the native library:

```text
senzing.szerror.SzSdkError: failed to load the Senzing library
ERROR: Unable to load the Senzing library: libSz.so: cannot open shared object file:
No such file or directory
        Did you remember to setup your environment?
```

That is Module 3's SDK-initialization check failing for a reason Module 2 created,
which routes the bootcamper into `explain_error_code` / env-var remediation for a
problem whose actual cause is the install command they were given.

This is not hypothetical. The plugin's own shipped example recap already records it
happening on a real run — `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:123`
calls it "a significant environment issue", names the exact versions that shadowed
(`senzing` 4.1.2, `senzing_core` 1.0.3 in `~/.local/lib/python3.12/site-packages`),
and cites the same server anti-pattern this spec is about. So the plugin documents
the hazard in `docs/` while instructing it in `skills/`.

The dry-run machine reproduces the shadowed state: `senzing` imports from
`/home/senzing/.local/lib/python3.12/site-packages/senzing/`, `import senzing_core`
raises the error above, and it succeeds only when `LD_LIBRARY_PATH=/opt/senzing/er/lib`
is supplied manually.

**The skew is now quantified** (phase 3 walk, 2026-08-13, same machine). Executing
Module 2 Step 1 for real produced:

| What | Version |
|---|---|
| pip-installed `senzing` | 4.1.2 |
| pip-installed `senzing_core` | 1.0.3 |
| native runtime (`SzProduct.get_version()`, `LD_LIBRARY_PATH` supplied) | **4.3.4** (build 4.3.4.26210, 2026-07-29) |
| `dpkg-query senzingsdk-runtime` | 4.3.4-26210 |
| `PYTHONPATH` | *empty* — `/opt/senzing/er/sdk/python` is not on the path at all |

So the bindings in front of the engine are two minor versions behind it, and the
SDK-shipped bindings that match the engine are unreachable. This strengthens the
detection check in "Proposed change" step 2: comparing `senzing.__file__` against
`/opt/senzing/er/sdk/python` catches it, and comparing the binding version against
`SzProduct.get_version()` quantifies how far apart they have drifted.

It also shows the hazard is **invisible to Module 2 as written**. Step 1's version
read reports 4.3.4 — the *engine's* version, via the native library — and says
nothing about the 4.1.2 bindings that will actually be imported. Module 2 therefore
reports a clean, current install on a machine that is already in the broken state.

## Root cause

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:448-455` hand-writes the
Python install command instead of routing it through `sdk_guide`, which is the
INV-080 violation in miniature: a Senzing fact (how the Python SDK is installed)
sourced from outside the MCP server.

The wrong instruction is well-camouflaged because it is *correct about a different
question*. INV-066 requires that any Python package install the plugin instructs use
an explicit interpreter (`python3 -m pip`, never bare `pip`) and survive PEP 668 by
falling back to a project-local virtualenv. Step 3 satisfies INV-066 precisely — bare
`pip` avoided, PEP 668 handled, global Python untouched. It applies that rule to a
package that must not be pip-installed **at all**, and no invariant carved out the
Senzing SDK from INV-066's scope. A reviewer checking Step 3 against INV-066 finds it
compliant, which is how it survived three audits.

The plugin holds the correct fact 300 lines further down and does not act on it:
`module-02-sdk-setup/SKILL.md:772` already states that
`sdk_guide(topic='configure', language='python', platform='linux_apt')` returns
`LD_LIBRARY_PATH` and `PYTHONPATH` — the two variables that exist *because* the
packages are already on disk rather than pip-installed.

### What the live server returns

`sdk_guide(topic='install', platform='linux_apt', language='python')` — MCP server
**1.32.9**, **2026-08-13**:

- `install.platform.env_vars.PYTHONPATH`:
  `"/opt/senzing/er/sdk/python (required for Python SDK — the senzing and senzing-core packages ship with senzingsdk-runtime here)"`
- `install.platform.gotchas[]` carries verbatim:
  > "Python SDK: The senzing and senzing-core packages are included in senzingsdk-runtime
  > at /opt/senzing/er/sdk/python. Do NOT pip install them — instead set
  > `PYTHONPATH=/opt/senzing/er/sdk/python:$PYTHONPATH` and
  > `LD_LIBRARY_PATH=/opt/senzing/er/lib:$LD_LIBRARY_PATH`"
- `install.platform.install_commands[]` installs the SDK as OS packages
  (`sudo apt install -y senzingsdk-runtime senzingsdk-setup`), with a
  `dpkg-deb -x` extraction path for no-sudo environments.

`generate_scaffold(language='python', workflow='full_pipeline')` — same server and
date — returns the same rule as a first-class `anti_patterns[]` entry applying to
**every** workflow (`initialize`, `configure`, `add_records`, `delete`, `query`,
`redo`, `stewardship`, `information`, `error_handling`, `full_pipeline`):

```json
{"pattern": "pip install senzing",
 "correct": "The senzing and senzing-core Python packages ship with senzingsdk-runtime at /opt/senzing/er/sdk/python. Set PYTHONPATH=/opt/senzing/er/sdk/python:$PYTHONPATH — do NOT pip install them. The PyPI packages are for unsupported community projects only.",
 "severity": "error", "category": "install", "language": "python"}
```

Both routes agree, and both are the routes that own the fact. There is no condition
(platform, SDK version, binding) under which the plugin's instruction is the correct
one — `platform_note` on the same response restricts the Python SDK to Linux
regardless.

## Proposed change

1. In `module-02-sdk-setup/SKILL.md`, replace the Python branch of Phase 3 Step 3 so
   that Python is **not** a pip install. The Python SDK arrives with the
   `senzingsdk-runtime` package installed earlier in the module; Step 3's Python work
   is to confirm `/opt/senzing/er/sdk/python` exists and to export `PYTHONPATH` (and
   `LD_LIBRARY_PATH` when the native library is not found automatically), taking both
   values from `sdk_guide(topic='install', platform=…, language='python')` rather than
   hardcoding them.
2. Add an explicit ⛔ warning naming `pip install senzing` / `pip install senzing-core`
   as an error-severity anti-pattern, and say *why* it is dangerous rather than merely
   wrong: it succeeds, then shadows the real packages, so the damage appears in
   Module 3 as a library-load failure. Include the detection step — if
   `python3 -c "import senzing; print(senzing.__file__)"` resolves outside
   `/opt/senzing/er/sdk/python`, PyPI packages are shadowing and must be uninstalled
   or the SDK path prepended.
3. Keep the other languages unchanged: Maven/Gradle, NuGet etc. remain correct, and
   the TypeScript `sz-napi` build-from-source warning is unaffected.
4. Scope INV-066 so it cannot be read as authorizing this again — it governs the
   plugin's *own* tooling installs (`fpdf2`, `playwright`), not Senzing SDK packages,
   which are never pip-installed. Register the carve-out as a new invariant (INV-222)
   rather than silently narrowing INV-066, and cross-reference the two.

## Acceptance criteria

- [ ] No file under `plugins/` instructs `pip install senzing` or
      `pip install senzing-core` in any form (bare, `python3 -m pip`, or inside a
      virtualenv).
- [ ] Module 2 Phase 3 installs the Python SDK by putting
      `/opt/senzing/er/sdk/python` on `PYTHONPATH`, with the value obtained from
      `sdk_guide` at run time rather than hardcoded in the prose.
- [ ] Module 2 states the shadowing hazard and gives the
      `import senzing; senzing.__file__` detection check with its remedy.
- [ ] INV-066 and the new SDK carve-out invariant each name the other, so a future
      reader of INV-066 cannot conclude that `python3 -m pip install senzing` is
      compliant.
- [ ] A repo-level test in `tests/` fails if any `plugins/` file reintroduces a
      `pip install senzing*` instruction (stdlib only, no `plugins/` import — INV-108),
      negative-controlled by reintroducing the line and confirming the test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      Note the asymmetry deliberately: the Python SDK is Linux-only per the server's
      own `platform_note`, so the macOS/Windows guidance is to choose another language
      or use Docker/WSL2 — which Module 2 already says elsewhere.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — replace the Python
  branch of Phase 3 Step 3 (lines 448-455); add the anti-pattern warning and the
  shadowing detection check.
- `specs/INVARIANTS.md` — register the SDK-is-not-a-pip-package invariant; cross-link
  INV-066.
- `tests/test_no_pip_install_senzing.py` — new guard.

## Source

- Feedback: n/a — found by `/dry-run` phase 1 (MCP call contracts), 2026-08-13, Module 2
  (`Source: self-observed (assistant retrospective)`). Corroborated by the plugin's own
  shipped artifact `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:123`,
  which records the same defect hitting a real bootcamp run.
- Priority: High — it breaks a documented path. Module 2 reports success, Module 3's
  SDK-initialization check fails, and the failure is attributed to the environment
  rather than to the instruction that caused it.
- MCP re-check: server **1.32.9**, **2026-08-13** — **server now contradicts the plugin**.
  Tools called: `sdk_guide(topic='install', platform='linux_apt', language='python')`
  and `generate_scaffold(language='python', workflow='full_pipeline')`; both return the
  "do NOT pip install" rule, the latter at `severity: error` for every workflow. No
  absence claim is made in this spec, so no `owner-checked:` clause is required.
- Upstream: not applicable — the plugin is wrong here, not the server.
- Related specs: none. Interacts with **INV-066** (`robust-fpdf2-install`), which
  remains correct for the plugin's own tooling installs.

## Deviations from this spec, and why (2026-08-14)

⛔ **This spec is deliberately NOT recorded in `specs/IMPLEMENTED.md`.** Five of its six
acceptance criteria hold and shipped in `acfb056`; **criterion 4 does not**, and it cannot be
satisfied without the maintainer:

> - [ ] INV-066 and the new SDK carve-out invariant each name the other, so a future reader of
>   INV-066 cannot conclude that `python3 -m pip install senzing` is compliant.

Registering an invariant requires the maintainer's sign-off on its wording (`implement-spec`
Step 5), and the standing instruction for this unattended batch (2026-08-14) was to **queue**
invariants rather than write them. Marking the spec done with an unmet criterion is what the
skill's first guardrail forbids, so the ledger is left without an entry and this note records
the state instead.

**What shipped** (criteria 1, 2, 3, 5, 6):

- No file under `plugins/` instructs a pip install of the SDK, in any spelling. The remaining
  occurrences are the prohibition itself and the example recap's record of the defect hitting a
  real run.
- Module 2 Phase 3 Step 3's Python branch makes the shipped packages importable instead of
  fetching them, with `PYTHONPATH` and `LD_LIBRARY_PATH` taken from
  `sdk_guide(topic='install', platform=…, language='python')` at run time rather than hardcoded.
- The shadowing hazard is stated with **why it is dangerous rather than merely wrong** (it exits
  0, so the module reports success and the damage appears a module later as
  `libSz.so: cannot open shared object file`), plus the `senzing.__file__` detection check and
  both remedies.
- `tests/test_no_pip_install_senzing.py` — 13 tests, **11 mutations all caught**, including the
  reported instruction restored verbatim.
- Java, C#, TypeScript unchanged; the Linux-only asymmetry relayed from the server's own
  `platform_note`.
- INV-066's scope is stated **in Module 2's prose**, which is the mitigation available without
  minting an invariant: it governs the plugin's own tooling installs (`fpdf2`, Playwright) and
  never authorizes pip for the Senzing SDK. That is weaker than criterion 4 asks for — the
  cross-reference lives in one shipped file rather than in `specs/INVARIANTS.md` — and is why the
  criterion is reported unmet rather than reinterpreted as met.

**MCP re-check, server 1.32.9, 2026-08-14 — confirmed, unchanged from the spec's 2026-08-13
reading.** `sdk_guide(topic='install', platform='linux_apt', language='python')` still returns
the `PYTHONPATH` env var with its "ship with senzingsdk-runtime here" note and the verbatim
"Do NOT pip install them" gotcha; `generate_scaffold(language='python',
workflow='full_pipeline')` still returns the `pip install senzing` anti-pattern at
`severity: error` with all ten workflows listed, and the Linux-only `platform_note`. One small
correction to the spec's phrasing: that `anti_patterns[]` entry keys its scope as `workflows`
(plural), and the `platform_note` is on the **`generate_scaffold`** response — the `sdk_guide`
response carries no `platform_note` field at all.

**To finish this spec**, the maintainer needs to approve wording for the carve-out. Proposed:

> **INV-NNN** — The Senzing SDK's language packages MUST NOT be installed from a language
> package manager; they ship with the Senzing SDK runtime and are made available by path.
> INV-066's explicit-interpreter and PEP 668 rules govern the plugin's own tooling installs
> only.

and INV-066 needs a pointer back to it. `tests/test_no_pip_install_senzing.py` enforces the rule
in the meantime, so the defect cannot silently return while the wording is pending.

## Invariants introduced

- `INV-222` — The Senzing SDK's language packages MUST NOT be installed from a language package manager; they ship inside the Senzing SDK runtime and are made available by path. INV-066's explicit-interpreter and PEP 668 rules govern the plugin's own tooling installs only, and the two invariants name each other. (recorded in `specs/INVARIANTS.md`, 2026-08-14; approved by the maintainer.)
