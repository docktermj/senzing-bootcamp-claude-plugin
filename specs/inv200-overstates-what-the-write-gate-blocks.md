# INV-200 says the write-gate enforces the project boundary; it blocks temp and Downloads only

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

⚠️ **An invariant recorded today encodes a false premise about shipped behaviour.** INV-200 was
registered 2026-08-11 and states:

> Every file the bootcamp writes MUST live inside the Bootcamper's project directory. The
> `PreToolUse` write-gate MUST block a write whose **resolved** target lies outside it — system temp
> (`/tmp`, `$TMPDIR`, `%TEMP%`, `%TMP%`), `~/Downloads`, or any path escaping via `..` — …

**The gate does not do this.** Executed live against a real scratch project
(`$HOME/senzing-bootcamp-dryrun`) on 2026-08-11:

| Target | INV-200 says | Gate does |
|---|---|---|
| `config/x.yaml` | allow | **allow** ✅ |
| `/tmp/scratch.txt` | block | **block** ✅ |
| `~/Downloads/x.txt` | block | **block** ✅ |
| `../escape.txt` → `$HOME/escape.txt` | **block** | **ALLOW** ❌ |

`write-gate.py`'s location logic reads:

```python
if low == here_low or low.startswith(here_low + "/"):
    pass                                   # inside the project -> allowed
else:
    if any(low.startswith(p) for p in TEMP_PREFIXES) or any(s in low for s in TEMP_SUBSTRINGS):
        block(LOC_MSG)
    else:
        for var in ("TMPDIR", "TEMP", "TMP"):   # relocated temp dirs
            ...
                block(LOC_MSG)
        # <- falls through with NO block
```

There is no `block()` after the env-var loop. A path outside the project that is not system temp,
not `~/Downloads`, and not under a temp env var is **allowed**. The gate is a *temp-and-Downloads
blocker*, not a project-boundary enforcer.

**There is also no `..`-escape detection.** `norm()` resolves `..` before comparison, so an escaping
path is simply checked against the same location lists as any other. INV-200's *"or any path escaping
via `..`"* describes a check that does not exist.

**The test that appears to cover this does not.** `tests/test_write_gate.py::test_dotdot_escape_blocked`
constructs its target as `os.path.join(proj, "config/../../..") + "/tmp/evil.txt"` — the escape lands
**in `/tmp`**, so it is blocked as temp. Its own comment says so: *"blocked as `/etc` is not exempt
and (when it lands in `/tmp` via cwd) as temp; use an explicit escape."* The `..` is incidental.

**Why this matters more than an ordinary wrong claim.** INV-200 is the invariant a future spec would
read before touching this gate. As written it promises a boundary that does not exist, so an author
could reasonably delete a temp prefix believing the general boundary check still catches it — and
nothing would. An invariant encoding a false premise is worse than a missing one.

**Neither the ground rules nor INV-200 is wrong about intent.** `ground-rules.md:224` says *"ALL
files stay inside the working directory"*, which is the same claim. The gap is between what the
guidance promises the guide and what the hook enforces.

**No Senzing fact is involved.** Internal behaviour only; no MCP tool was called for this finding.

## Root cause

INV-200 was drafted from `ground-rules.md`'s statement of intent and from the *names* of the
write-gate's tests — twelve location tests reading as a boundary suite — rather than from the gate's
control flow. The tests all pass because every one of them targets a location the lists do name, so
the fall-through branch is never exercised by any of them.

The invariant was negative-controlled on the day it was written, and that control found a *different*
real gap (the env-var branch was untested) which was fixed. It did not find this one, because a
mutation test only probes the branches the suite reaches: deleting the fall-through `block()` is
impossible when there is no `block()` there to delete.

## Proposed change

**The maintainer chooses between two readings; this spec deliberately does not.**

- **(a) The invariant is wrong** → correct INV-200 **in place** with a dated note saying what was
  verified and when: the gate blocks system temp, `~/Downloads` and relocated temp dirs, and does
  **not** enforce a general project boundary; `..` is resolved before comparison, not detected.
  ⛔ Never delete or renumber it. Also reconcile `ground-rules.md:224`, whose "ALL files stay inside
  the working directory" is then guidance the hook does not fully enforce — which is legitimate
  (the guide is instructed, the hook is a backstop) but should say so rather than implying the gate
  catches everything.
- **(b) The gate is wrong** → add the missing `block(LOC_MSG)` on the fall-through, so any resolved
  target outside the project is blocked and INV-200 becomes true. This is a **behaviour change** and
  needs its own risk assessment: it would block every write outside the project during a bootcamp,
  including any the plugin legitimately makes to the user's Claude configuration or elsewhere. That
  set must be enumerated before choosing this, not assumed empty.

**Either way, fix the test.** `test_dotdot_escape_blocked` should target a path that escapes the
project and lands somewhere the location lists do **not** name — under (a) asserting it is allowed
and renamed to say so, under (b) asserting it is blocked. As written its name claims a guarantee its
body does not test.

## Acceptance criteria

- [ ] INV-200 and the gate agree. Under (a) INV-200 carries a dated in-place correction and is not
      deleted or renumbered; under (b) `write-gate.py` blocks the fall-through case.
- [ ] `test_dotdot_escape_blocked` targets a path outside the project that no location list names,
      and asserts the chosen behaviour — so its name and its body claim the same thing.
- [ ] A test covers the fall-through case explicitly, with a not-vacuous guard proving the probe path
      is not caught by any static list (the `test_the_relocated_temp_probe_is_not_caught_by_a_static_list`
      idiom already in that file).
- [ ] Under (a): `ground-rules.md:224` states that the write-gate backstops temp and Downloads while
      the in-project rule binds the guide, so the two are not read as identical guarantees.
- [ ] Under (b): the set of legitimate out-of-project writes is enumerated and shown to be empty, or
      exempted explicitly.
- [ ] Negative-controlled: the mutation that reintroduces the disagreement fails the suite. Verify
      the mutation actually landed.
- [ ] Holds on Linux, macOS and Windows; Windows is **not runtime-verified here** (no Windows host).

## Affected files

- `specs/INVARIANTS.md` — INV-200 (correction in place, under (a)).
- `plugins/senzing-bootcamp/scripts/write-gate.py` — the fall-through branch (under (b)).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:224` (under (a)).
- `tests/test_write_gate.py` — `test_dotdot_escape_blocked` plus the new fall-through case.

## Source

- Dry run: `dry-run` phase 2 (hooks and scripts), 2026-08-11, executed against
  `$HOME/senzing-bootcamp-dryrun` with the bootcamp active.
- Suite green at the time of the finding: 1596 passed, 3 skipped, 1263 subtests — this is invisible
  to all of them.
- **Self-reported:** INV-200 was drafted, approved and recorded by this same session earlier the
  same day, from the ground rules and the test *names* rather than from the gate's control flow.
  The phase-2 probe that found it is four `write-gate.py` invocations against a real project — the
  thing static analysis structurally cannot do.
- Priority: **Medium-high.** No live defect: the gate blocks what it always blocked and the
  Bootcamper is unaffected today. The cost is a false premise sitting in the ruleset that a future
  author would reasonably rely on.
- MCP re-check: **n/a — no Senzing fact.** No tool called for this finding.
- Related: `specs/write-gate-location-logic-is-unregistered.md` (registered INV-200),
  `specs/harden-write-gate.md` (INV-109, the secret half).

## Deviations from this spec, and why (2026-08-11)

**Reading (b) was chosen by the maintainer** — the gate was fixed, not the invariant. So
INV-200 stands **unedited**: it becomes true as written, including its *"or any path
escaping via `..`"* clause, because `norm()` resolves the escape and the new fall-through
blocks wherever it lands. `ground-rules.md:224` is likewise unedited — "ALL files stay
inside the working directory" and "the write-gate enforces the write half" are now both
accurate. Criterion 4 is (a)-only and is therefore **not applicable**, not unmet.

**Criterion 5 (the (b) risk assessment) was discharged before the change, and the set is
empty.** No file under `plugins/` names a write target outside the project: the feedback
file is `docs/feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md`, the environment script is
project-local by INV-166/167/175, and INV-199 already forbids out-of-project writes
categorically. The gate is also `PreToolUse` on **Write/Edit only** (`hooks/hooks.json:37`),
so SDK installs writing to `/opt/senzing` are `Bash` and unaffected; and it activates only
when the cwd holds `config/bootcamp_progress.json`, i.e. when the cwd *is* the project.
No exemption list was needed. **One consequence the spec did not name:** a Bootcamper's own
mid-bootcamp request to write outside the project (e.g. `~/notes.md`) is now blocked too.
That follows from INV-199 and was accepted as part of choosing (b).

**Three existing tests had to change their discriminator, and this is the substantive
deviation.** Under (b) every out-of-project path blocks, so the **exit code can no longer
say which branch blocked** — and a test meant to pin one branch starts passing for the wrong
reason. The env-var branch is the casualty: it becomes untestable by outcome, which is
exactly the branch `test_relocated_temp_dir_blocked_via_env_only` was added to guard nine
hours earlier. A second message (`OUTSIDE_MSG`) restores the distinction, and those cases
now assert the message:

- `test_relocated_temp_dir_blocked_via_env_only` — also asserts the temp message, so
  deleting the `TMPDIR/TEMP/TMP` loop fails again. **Verified by mutation:** with
  exit-code-only assertions that deletion left the suite green; with the message
  assertion it fails.
- `test_the_relocated_temp_probe_is_not_caught_by_a_static_list` — asserted ALLOW before;
  it cannot any more. Now asserts BLOCK **with the boundary message**, which still proves
  no static list names the probe.
- `test_home_personal_tmp_allowed` → renamed
  `test_home_personal_tmp_is_not_mistaken_for_system_temp`. It asserted ALLOW; `~/tmp` is
  outside the project so it now blocks, and what it must still prove — that `~/tmp` is not
  classified as *system* temp — is now proved by the message.

**The temp lists are no longer load-bearing for the block decision.** `TEMP_PREFIXES`,
`TEMP_SUBSTRINGS` and the env-var loop now only select the more specific message; the
fall-through blocks regardless. Recorded because it inverts the spec's own worry: an author
deleting a temp prefix no longer creates a hole, but one deleting a list *believing* it
still gates would be wrong about why it matters.

**Files changed beyond the spec's list:** `plugins/senzing-bootcamp/hooks/README.md` (two
places described the gate as blocking temp/Downloads only, which is now understated).
`specs/INVARIANTS.md` and `ground-rules.md` are **not** changed, per the (b) reading above.

**Criterion 7 — Windows is not runtime-verified.** No Windows host. The logic is
string-only (`norm()` case-folds and resolves without touching the filesystem) and the
`%TEMP%`/`%TMP%` and `/appdata/local/temp/` paths are exercised on Linux, but the platform
itself was not exercised. Unchanged from the spec's own statement of this criterion.
