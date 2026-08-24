# The env-script template enumerates every platform export except `PYTHONPATH`, so the shipped bindings lose to a PyPI install

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The environment script Step 3 writes exported `LD_LIBRARY_PATH` but not `PYTHONPATH`.
On a workstation carrying a PyPI `senzing` distribution, `import senzing` therefore
resolved to the user's local site-packages (4.1.2) rather than the SDK-shipped
bindings at `/opt/senzing/er/sdk/python` (4.3.4).

⛔ **The import succeeded.** Nothing raised, nothing was logged, and every later module
ran against a different SDK version than the one the module had just verified. It was
caught by printing `senzing.__file__`, not by any failure.

This still reproduces on the dry-run machine at triage time (2026-08-24):

```text
$ python3 -c "import senzing; print(senzing.__file__)"
/home/senzing/.local/lib/python3.12/site-packages/senzing/__init__.py

$ ls -d /opt/senzing/er/sdk/python
/opt/senzing/er/sdk/python
```

The SDK-shipped bindings are present on disk and unreachable on `sys.path`.

⚠️ **This is the mirror of a defect the plugin already fixed, produced by that fix's own
emphasis.** `specs/ld-library-path-relayed-as-conditional-on-a-stock-linux-apt-install.md`
addressed an env script that set `PYTHONPATH` and omitted `LD_LIBRARY_PATH`. The remedy
correctly foregrounded `LD_LIBRARY_PATH` — and the template it left behind now names that
variable and never names the other one. The failure swapped ends rather than closing.

## Root cause

Two sites, and the first is sufficient on its own.

### 1. The template's export placeholder never names `PYTHONPATH`

`plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md:714` is the comment that
tells the author which variables belong in the generated script:

```text
# Platform-specific exports (SENZING_ROOT, DYLD_LIBRARY_PATH / LD_LIBRARY_PATH, jar
# paths) go here — take them from sdk_guide(topic='install', platform=…, language=…),
# never from memory or from this file (INV-080).
```

Three examples, none of them `PYTHONPATH`. The ⚠️ note immediately below
(`:718-725`) is the corrective from the earlier spec and is entirely about
`LD_LIBRARY_PATH` — it warns that `env_vars` hedges that one variable while the
language-specific `gotchas[]` entry requires it. So both the enumeration and the
warning beside it point the author at the native-library variable, and the Python
path variable appears in neither.

Step 3's install prose does state the requirement, correctly and at length
(`:493-505`: *"On `linux_apt` with Python, BOTH `PYTHONPATH` and `LD_LIBRARY_PATH` are
required — set both"*). But that is 200 lines above the template, in the phase that
installs the bindings rather than the one that writes the script, and the template is
the artifact the author is copying at the moment they write the exports.

### 2. Step 4 cannot see the skew, and the existing-install path skips the only check that can

`module-02-sdk-setup/SKILL.md:824-826` scopes Step 4 to the binding: the factory
constructs and `SzProduct.get_version()` answers. That version is read **through the
native library**, so it reports the engine's version — 4.3.4 — while saying nothing
about which `senzing` package was imported. A shadowed install passes Step 4 with a
current-looking version.

The only detection that would catch it is Step 3's `senzing.__file__` check at `:545`,
and `:121` routes an existing install past it: *"jump to Step 4 (verify installation)"*.
`specs/skipping-step-3-on-an-existing-install-skips-the-env-script.md` already
established that this skip loses the env script; it also loses the shadowing check, and
the two compound — no `PYTHONPATH` export **and** no verification that the export was
needed.

### What the live server returns

⛔ **The entry's stated cause does not hold, and the spec is written against the corrected
one.** The entry recorded its divergence as *"`env_vars` carries `LD_LIBRARY_PATH` but no
`PYTHONPATH` entry for the SDK's Python directory"*. That is false on the current server.

`sdk_guide(topic='install', platform='linux_apt')` — MCP server **1.33.0**, **2026-08-24**
— returns:

```json
"env_vars": {
  "LD_LIBRARY_PATH": "/opt/senzing/er/lib (only needed if native lib not found automatically)",
  "PYTHONPATH": "/opt/senzing/er/sdk/python (required for Python SDK — the senzing and senzing-core packages ship with senzingsdk-runtime here)"
}
```

The same two keys come back from `sdk_guide(topic='install', platform='linux_apt',
language='python')`, byte-identical. So `PYTHONPATH` is present **with or without** the
`language` argument — the call the entry names in its "behind the scenes" line would have
returned it — and it is the only one of the two the server marks `required`, while
`LD_LIBRARY_PATH` carries the hedge.

The `gotchas[]` array in the same payload repeats it unconditionally for Python, unchanged
from the 1.32.9 reading the plugin already quotes:

> "Python SDK: The senzing and senzing-core packages are included in senzingsdk-runtime at
> /opt/senzing/er/sdk/python. Do NOT pip install them — instead set
> PYTHONPATH=/opt/senzing/er/sdk/python:$PYTHONPATH and
> LD_LIBRARY_PATH=/opt/senzing/er/lib:$LD_LIBRARY_PATH"

**The server supplied the variable; the template did not ask for it.** That moves the whole
defect inside the plugin and removes any basis for an upstream report on this entry.

⚠️ **The resolution order itself is observation-only** (INV-080/INV-149). That a
site-packages `senzing` wins over an unset `PYTHONPATH`, and that prepending the SDK path
reverses it, is CPython `sys.path` behavior observed on this machine (Python 3.12, Senzing
SDK 4.3.4-26210, apt install at `/opt/senzing`, 2026-08-24). No MCP route reports it.

## Proposed change

1. **Name `PYTHONPATH` in the template's export placeholder** (`:714`), so the
   enumeration the author copies from lists the language variable alongside the native
   one. Keep the values sourced from `sdk_guide` at run time rather than hardcoded
   (INV-080) — this changes which variables are named, not where they come from.
2. **Generalize the placeholder rather than lengthening the list.** The list is
   examples, and a second omission is the same defect again. State the rule that
   governs: every variable the language-specific `gotchas[]` entry names must be
   exported, and the enumeration is illustrative. The existing ⚠️ already routes the
   author to `gotchas[]`; make its scope the whole variable set instead of
   `LD_LIBRARY_PATH` alone.
3. **Add a resolved-binding check to Step 4**, not only to Step 3. Print the resolved
   `senzing.__file__` and the binding's own version beside `SzProduct.get_version()`, and
   state what a mismatch means: the two versions come from different places — the engine
   through the native library, the binding through `sys.path` — so agreeing is
   the thing being verified. This is the check that survives the existing-install skip
   at `:121`.
4. **Say why the check exists, at the check.** A shadowing install produces a working
   import and a plausible version, so a step that merely reports success is what the
   defect hides behind (the same fail-loudly reasoning INV-111 applies to generators).

## Acceptance criteria

- [ ] The env-script template's export guidance names `PYTHONPATH`, and states the
      language-specific `gotchas[]` entry as the authority for the full variable set
      rather than presenting its own list as complete.
- [ ] The generated script for Python on `linux_apt` exports both `PYTHONPATH` and
      `LD_LIBRARY_PATH`, with both values taken from `sdk_guide` at run time and neither
      hardcoded in the prose.
- [ ] Step 4 reports the resolved binding path and the binding version alongside the
      engine version, and states that a path outside the SDK's Python directory means
      PyPI packages are shadowing the shipped ones.
- [ ] The Step 4 check is reachable on the existing-install path that skips Steps 2 and 3.
- [ ] A repo-level test fails if the template's export guidance names `LD_LIBRARY_PATH`
      without naming `PYTHONPATH` (stdlib only, no `plugins/` import — INV-108),
      negative-controlled by restoring the reported wording and confirming the test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The asymmetry is relayed, not invented: the Python SDK is Linux-only per the server's
      own `platform_note`, so `PYTHONPATH` has no macOS/Windows counterpart to add, and the
      `DYLD_LIBRARY_PATH` and `senzing-env.bat` guidance must be left intact.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the template's export
  placeholder and its ⚠️ note (`:714-725`); Step 4's verification (`:822-856`); the
  existing-install route at `:121`.
- `tests/` — new guard on the template's export enumeration.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: PyPI `senzing` package silently shadows the SDK-shipped bindings" (2026-08-24, Module SDK setup, step 3; `Source: self-observed (assistant retrospective)`)
- Priority: High — a silent version skew that persists through every later module, on a path the module reports as clean.
- MCP re-check: server **1.33.0**, **2026-08-24** — **the entry's diagnosis is corrected; the plugin defect stands.** Called `sdk_guide(topic='install', platform='linux_apt')` and `sdk_guide(topic='install', platform='linux_apt', language='python')`; both return `install.platform.env_vars` carrying **both** `LD_LIBRARY_PATH` and `PYTHONPATH`, with `PYTHONPATH` marked required and `LD_LIBRARY_PATH` hedged, plus the unconditional Python-SDK `gotchas[]` line quoted above. The entry's claim that `env_vars` omits `PYTHONPATH` is contradicted, including for the language-less call it names. No absence claim is made in this spec, so no `owner-checked:` clause is required. The `sys.path` resolution order is engine/interpreter behavior and is observation-only.
- Upstream: not applicable — the server returns the variable; the plugin's template does not ask for it. The separate `LD_LIBRARY_PATH` hedge in the same payload was already sent 2026-08-16 and is unchanged on 1.33.0; do not re-file it.
- Related specs: `specs/ld-library-path-relayed-as-conditional-on-a-stock-linux-apt-install.md` (the mirror defect, whose remedy produced this one), `specs/skipping-step-3-on-an-existing-install-skips-the-env-script.md` (the skip that also loses the detection check), `specs/senzing-python-sdk-must-not-be-pip-installed.md` (INV-222; the shadowing hazard and the `senzing.__file__` check it added at Step 3), `specs/env-script-must-be-shell-portable.md`

## The general shape

A corrective that names one variable teaches the reader that variable, and an enumeration
offered as an example is read as a checklist. Both prior versions of this template were
complete for the failure most recently observed and silent about the other end. The durable
form is not a longer list — it is a pointer to the route that owns the whole set, with the
list marked as illustrative, which is what proposed change 2 asks for.
