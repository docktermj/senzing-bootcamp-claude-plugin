# The "never modify the user's global shell configuration" guarantee is registered nowhere

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`module-02-sdk-setup/SKILL.md:502-508` states a safety guarantee about the Bootcamper's machine, at
the plugin's highest emphasis level:

> **🚨 NEVER modify the user's global shell configuration** (`~/.zshrc`, `~/.bashrc`,
> `~/.profile`, etc.) to set Senzing environment variables. Instead, create a project-local
> environment script at `src/scripts/senzing-env.sh` (or `.bat` for Windows) that sets
> `SENZING_ROOT`, library paths, and any other Senzing-specific variables. Source this script
> before running bootcamp tasks. This keeps the bootcamp self-contained and avoids side effects on
> the user's system.

**Nothing registers it and nothing enforces it.** Verified 2026-08-11:

- `grep -inE 'zshrc|bashrc|shell configuration|global shell|profile file' specs/INVARIANTS.md` →
  **no match**. No invariant states it.
- `grep -rn 'zshrc\|bashrc\|global shell' tests/*.py` → **no match**. No test asserts it.
- `tests/test_env_script_shell_portability.py` exists and covers the *portability* of
  `senzing-env.sh` (INV-166/INV-167/INV-175 territory) — the **positive** half. The **prohibition**
  is uncovered.

So the guarantee exists in the product and in one file's prose, and in neither the ruleset nor the
suite. Nothing binds future work to it, and nothing notices if a later change contradicts it — which
is precisely the reverse-sweep failure the audit skill records having cost weeks twice (INV-134's
name rule shipped unregistered and was then mis-cited to INV-076; INV-155's tab removals registered
nothing and left the shipped app contradicting a standing invariant).

**Why this one matters more than most unregistered rules.** It is the only statement in the plugin
that constrains what the bootcamp may do to files **outside the project directory**. Every other
file-placement rule (INV-050, INV-108, the `docs/` rules) governs where things go *inside* the
generated project. A future step that "helpfully" persists `SENZING_ROOT` to `~/.zshrc` — which the
MCP server's own macOS install guidance suggests for a human operator, *"Add to ~/.zshrc to
persist"* — would violate this guarantee, break the bootcamp's self-containment, and pass the entire
suite.

**No Senzing fact is at issue.** The rule is about the plugin's behaviour on the Bootcamper's
machine. The `sdk_guide` install text quoted above is context for *why the rule is easy to breach*,
not a claim this spec asserts; it was returned by `sdk_guide(topic='install', platform='macos_arm',
language='java')` on server 1.32.8, 2026-08-11.

## Root cause

The rule predates the invariant-registration discipline: it reads like operational advice inside a
setup step, not like a guarantee, so no spec ever proposed promoting it. `conformance.py rules`
finds it because its section cites no invariant — one of 15 such hard-rule lines, and the only one
in the batch that turned out to be a durable, unregistered, machine-affecting guarantee. The other
hits triaged as local instructions or as rules already covered elsewhere.

## Proposed change

**Register the invariant** (wording needs the maintainer's sign-off before it is recorded — never
record one they have not agreed to), at the next unused ID, with its index entry in the same edit:

> **INV-NNN** — The bootcamp MUST NOT create or modify any file outside the generated project
> directory in order to configure the Bootcamper's environment — specifically never a global shell
> profile (`~/.zshrc`, `~/.bashrc`, `~/.profile`, PowerShell `$PROFILE`, or equivalent) — and MUST
> instead write a project-local environment script (`src/scripts/senzing-env.sh`, or the platform
> equivalent per INV-166/INV-167/INV-175) that the Bootcamper sources per session. Guidance the MCP
> server returns for a human operator MAY recommend persisting variables to a shell profile; the
> bootcamp MUST NOT act on that recommendation on the Bootcamper's behalf, and where it relays such
> guidance it MUST say that the bootcamp itself does not do it.

**Add the citation at the site.** `module-02-sdk-setup/SKILL.md:502` gains the `INV-NNN` reference,
so a later editor can look the rule up (INV-183's requirement that a step name its governing rules
at that step).

**Add the guard.** A test asserting no shipped skill or script instructs writing to a global shell
profile: scan `plugins/` for `~/.zshrc`, `~/.bashrc`, `~/.profile`, `$PROFILE` and assert every hit
is inside a prohibition or a quoted-from-MCP block, never an instruction. Include the not-vacuous
guard — the scan must find the known prohibition site, or a pattern drift makes it pass on nothing.

**What stays.** The whole passage, including its reason (*"keeps the bootcamp self-contained and
avoids side effects on the user's system"*) — that sentence is why the rule survives contact with a
plausible-sounding suggestion to do otherwise.

## Acceptance criteria

- [ ] The invariant is recorded at the next unused `INV-NNN` with maintainer-approved wording, an
      index entry in the same edit, and provenance naming this spec (per `INVARIANTS.md` rules).
- [ ] `module-02-sdk-setup/SKILL.md:502` cites the new ID.
- [ ] A test asserts no shipped file instructs modifying a global shell profile, with a
      not-vacuous guard that fails if the scan matches nothing.
- [ ] The test is negative-controlled: adding an instruction to append to `~/.zshrc` fails it.
- [ ] The existing `senzing-env.sh` portability coverage
      (`tests/test_env_script_shell_portability.py`) is unchanged — this adds the prohibition half,
      it does not touch the positive half.
- [ ] Windows is covered explicitly (PowerShell `$PROFILE`), since INV-001 makes it supported and
      this environment cannot exercise it — disclose rather than omit.
- [ ] Stdlib-only, no `plugins/` import (INV-108); language-agnostic (INV-002).

## Affected files

- `specs/INVARIANTS.md` — the new invariant + index entry.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:502`, add the citation.
- `tests/` — the new prohibition guard.

## Source

- Audit: `production-readiness-audit`, 2026-08-11. Step 3 (reverse sweep), from
  `conformance.py rules` — 177 hard-rule lines, 15 in a section citing no invariant, across 11
  files; this was the one that resolved to an unregistered durable guarantee.
- Suite was green at the time of the finding: 1587 passed, 3 skipped, 1253 subtests.
- Priority: **Medium-high.** Nothing is broken today, but it is the plugin's only guarantee about
  files outside the project, it is unenforced, and the most likely way to breach it is by following
  install guidance that the plugin itself relays.
- MCP re-check: **n/a for the rule — no Senzing fact.** The `sdk_guide` quotation is context, taken
  from `sdk_guide(topic='install', platform='macos_arm', language='java')` on server 1.32.8,
  2026-08-11.

## Deviations from this spec, and why (2026-08-11)

**1. The rule has TWO authoritative sites; this spec named one.** It cites only
`module-02-sdk-setup/SKILL.md:502`. `bootcamp-onboarding/ground-rules.md:226` also states it —
"Never modify global shell config." — under **File placement**, and that is the always-loaded rules
file, arguably the more binding of the two. Both now carry the prohibition, the Windows path, the
project-local alternative and the `INV-199` citation. This is the incomplete-application class the
`production-readiness-audit` skill ranks first, occurring inside the audit's own spec: the search
that found the rule (`conformance.py rules`, which reports hard rules whose section cites no
invariant) surfaces one line per section, so the second site was never in view.

**2. Windows was uncovered at every site.** Every statement named `~/.zshrc`, `~/.bashrc` and
`~/.profile` — all POSIX — while INV-001 makes Windows supported. PowerShell `$PROFILE` is now named
at both sites and in INV-199, and `test_both_sites_name_windows_not_only_posix` pins it. The spec
anticipated this in its criteria but described it as a disclosure; it was a real gap in the rule.

**3. Prior art the spec did not cite.** `specs/macos-jvm-launch-environment-guidance.md:36,62,85`
already treats this as an existing rule and builds on it — it is where the project-local wrapper is
called "the natural and only home" precisely because `~/.zshrc` is off-limits. That spec did not
register an invariant either, so the gap is real, but the rule was load-bearing for other work
before today and the spec should have said so. Found by a dedup pass over `specs/` before
implementing — the pass whose absence produced a wholly wrong finding earlier the same day.

**4. Two defects in the guard, both mine, both caught before the suite ran.**
(a) The scan matched line-by-line, so the prohibition's own wrapped continuation lines — which carry
`~/.profile` without carrying the word "never" — were reported as violations of the rule they state.
It now matches per paragraph. This is the "guard spans lines" trap `compact-dev-environment`
documents, and the code comment acknowledged the risk before failing to it.
(b) An assertion matched literal prose that ships with backticks and bold markers, so it failed on
correct text. Emphasis is now stripped before matching.

**MCP re-check.** The relayed quotation was re-confirmed this session, not carried from the spec:
`sdk_guide(topic='install', platform='macos_arm', language='java')` on **server 1.32.8, 2026-08-11**
returns *"DYLD_LIBRARY_PATH must be set at the shell level before any JVM or Python launch. Add to
`~/.zshrc` to persist"*. Note the spec's first probe used `language='python'`, which short-circuits on
macOS (Python is Linux-only) and returns no install block at all — the binding must be one macOS
supports or the call answers a different question.

## Invariants introduced

- `INV-199` — The bootcamp MUST NOT create or modify any file outside the generated project
  directory to configure the Bootcamper's environment (never a global shell profile, including
  PowerShell `$PROFILE`), MUST write a project-local environment script instead, and where it
  relays MCP install guidance recommending persistence to a shell profile MUST state that the
  bootcamp does not act on it (recorded in `specs/INVARIANTS.md`, indexed under **Platform, shell,
  encoding and file placement**).
