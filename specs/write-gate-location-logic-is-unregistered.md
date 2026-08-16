# The write-gate's location logic — the plugin's base file-placement guarantee — is in no invariant

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The plugin's most basic guarantee about where it writes is enforced by a `PreToolUse` hook and 12
dedicated tests, and registered in **no invariant**.

`plugins/senzing-bootcamp/scripts/write-gate.py` blocks any write outside the project. Its own
comment states the purpose (`:97`): *"gate's intent is 'don't write outside the project'"*, and it
blocks with `LOC_MSG` (`:20-21`): *"Write blocked: use a project-relative path, not a system temp or
Downloads …"*. `bootcamp-onboarding/ground-rules.md:224-225` states the same rule to the guide:

> ALL files stay inside the working directory. Never `/tmp`, `%TEMP%`, or `~/Downloads`.
> Override MCP-suggested paths (e.g. `/tmp/`, `ExampleEnvironment`) to project-relative ones.

`tests/test_write_gate.py` holds it with 12 location tests — `test_system_tmp_blocked`,
`test_downloads_blocked`, `test_windows_temp_env_blocked`, `test_tmpdir_env_blocked`,
`test_dotdot_escape_blocked`, `test_project_under_tmp_path_allowed`,
`test_home_relative_downloads_blocked`, `test_home_relative_windows_temp_blocked`,
`test_home_personal_tmp_allowed`, `test_case_variant_in_project_allowed`,
`test_project_relative_allowed`, `test_absolute_in_project_allowed`.

**And INV-109 proves the gap rather than filling it.** It is the one invariant about this hook, and
its wording draws the line itself:

> **INV-109** — The PreToolUse write-gate (`write-gate.py`) MUST detect, at minimum, PEM private
> keys, AWS access-key IDs, and Senzing `AQAAAD` license blobs, blocking the write with `SECRET_MSG`;
> **the secret check runs independently of the location logic** and fails closed.

So the ruleset knows the location logic exists, references it by name, and governs only its sibling.
`write-gate.py`'s sole invariant citation is INV-001, and that one is **correct and unrelated** — it
sits at `:117` explaining why all three of `TMPDIR`/`TEMP`/`TMP` are consulted, *"so no platform is
covered less well than the others"*, which is exactly INV-001's subject.

**The consequence.** Relax the location logic tomorrow — widen an allow-prefix, drop the `..`-escape
check, stop consulting `%TEMP%` — and `INVARIANTS.md` does not notice. The tests would fail, which is
real protection; but a spec that deliberately changed the behaviour would simply update them, and
nothing in the ruleset would say the guarantee had been traded away. That is the reverse-sweep
failure this audit exists for: the guarantee lives in the product and nowhere in the rules.

**The inversion makes it visible.** As of 2026-08-11, INV-199 registers a *narrower, purpose-scoped*
slice of the very same territory — files written **to configure the Bootcamper's environment** — and
it is cited in the second half of the same `ground-rules.md` bullet whose first half states the
general rule with no citation at all. The specific case is bound; the general case is not.

**No Senzing fact is involved.** Internal consistency only; no MCP tool was called for this finding.

## Root cause

The rule predates the invariant-registration discipline and reads like plumbing rather than a
guarantee — it is a hook's behaviour, not a step's instruction, so no spec ever proposed promoting
it. `harden-write-gate` (2026-07-24) registered INV-109 for the half it was *changing* (secrets) and
left the half it was not touching unregistered, which is reasonable spec hygiene and exactly how a
gap of this shape opens.

It survived the `production-readiness-audit` run of the same morning, and survived an edit to the
very bullet that states it: INV-199's citation was added to that bullet's second half hours earlier
without anyone noticing the first half had none. `conformance.py rules` cannot surface it, because
that scan reports hard rules whose **section** cites no invariant — this section now cites INV-199,
so the section reads covered while its broader claim is not.

## Proposed change

**Register the invariant** (wording needs the maintainer's sign-off — never record one they have not
agreed to), at the next unused ID, index entry in the same edit:

> **INV-NNN** — Every file the bootcamp writes MUST live inside the Bootcamper's project directory.
> The `PreToolUse` write-gate MUST block a write whose resolved target lies outside it — including
> system temp (`/tmp`, `$TMPDIR`, `%TEMP%`, `%TMP%`), `~/Downloads`, and any path escaping the
> project via `..` — and MUST allow a project-relative or in-project absolute path, including a
> project that legitimately lives beneath a temp directory. Where an MCP tool suggests a path outside
> the project (`/tmp/…`, `ExampleEnvironment`), the guide MUST override it to a project-relative one
> rather than following it. (Complements INV-109, which governs the same hook's independent secret
> check, and INV-199, which governs the narrower environment-configuration case.)

**Add the citation at both sites**: `ground-rules.md:224` (the guide-facing statement) and
`write-gate.py`'s location block (the enforcement). Two sites, because the incomplete-application
class is the one this audit ranks first — and because this spec exists *because* a rule stated in two
places was registered from neither.

**Add no new test.** `tests/test_write_gate.py`'s 12 location tests already hold the behaviour; what
is missing is the citation linking them to a rule. Add the invariant ID to that file's docstring so
`coverage_reports.py invariants` stops reporting the new invariant as unenforced, and so a reader of
either file can find the other.

**What stays.** All of it. This registers an existing guarantee; it changes no behaviour and removes
nothing.

## Acceptance criteria

- [ ] The invariant is recorded at the next unused `INV-NNN` with maintainer-approved wording, an
      index entry in the same edit, and provenance naming this spec.
- [ ] `ground-rules.md:224` and `write-gate.py`'s location block both cite the new ID.
- [ ] `tests/test_write_gate.py` cites it, so the coverage report sees the enforcement that already
      exists.
- [ ] INV-109 is **unchanged** — it correctly governs the secret half, and this spec does not touch
      it. Verified by opening it.
- [ ] `write-gate.py:117`'s INV-001 citation is **left alone** — it is correct: it explains covering
      all three platforms' temp-var conventions equally, which is INV-001's subject, not this rule's.
- [ ] No behaviour changes: `tests/test_write_gate.py` passes unmodified apart from the docstring
      citation.
- [ ] Holds on Linux, macOS and Windows (the gate already consults `TMPDIR`/`TEMP`/`TMP`); Windows
      enforcement is **not runtime-verified here** — no Windows host — and that is disclosed rather
      than omitted.

## Affected files

- `specs/INVARIANTS.md` — the new invariant + index entry.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:224`, add the citation.
- `plugins/senzing-bootcamp/scripts/write-gate.py` — the location block, add the citation.
- `tests/test_write_gate.py` — docstring citation only.

## Source

- Audit: `production-readiness-audit`, 2026-08-11 (second run, scoped to the delta since the first
  and to the gaps the first disclosed). Step 3, reverse sweep.
- Suite green at the time of the finding: 1594 passed, 3 skipped, 1259 subtests.
- Priority: **Medium-high.** Nothing is broken and the tests do protect the behaviour today; the gap
  is that a deliberate future change would face no rule, only tests it would update in the same
  commit.
- MCP re-check: **n/a — no Senzing fact.** No tool called for this finding.
- Related: `specs/harden-write-gate.md` (registered INV-109 for the secret half),
  `specs/never-modify-global-shell-config-is-unregistered.md` (INV-199, the narrower case).

## Deviations from this spec, and why (2026-08-11)

**1. The rule binds SIX shipped sites; this spec named two.** A sweep before implementing found it
stated at `ground-rules.md:224` and `write-gate.py` (both named) **and** at
`module-05/phase3-test-load.md:250`, `module-05/phase2-data-mapping.md:134`,
`module-07/phase1-query-visualize.md:173` and `graduation/SKILL.md:926`. A **second** enforcing test
file was also missed: `tests/test_mcp_call_contracts.py:50,128` pins `workspace_dir` against
`FORBIDDEN_WORKSPACE_DIRS`. This is the incomplete-application class the audit ranks first, in the
audit's own spec, for the third time in one day.

**2. That discovery widened the invariant.** INV-200 as recorded binds MCP tool **arguments**, not
only file writes — `mapping_workflow` and `analyze_record` both require `workspace_dir`, and the
server's own contract warns *"do NOT assume /tmp exists"* (`get_capabilities`, MCP server 1.32.8,
re-confirmed this session). The spec's draft covered the write path alone. Citations went to the
canonical statement, the enforcement, and **both** enforcing test files rather than to all six
prose sites, which would be noise; the rule is stated once and the sites inherit it.

**3. ⚠️ The negative control found the invariant claiming enforcement that did not exist — mine,
minutes old.** INV-200 names `$TMPDIR`, `%TEMP%` and `%TMP%`. Deleting the entire
`for var in ("TMPDIR", "TEMP", "TMP")` loop from `write-gate.py` left the suite **green**.

Two tests look like they cover that branch and neither does:

- `test_tmpdir_env_blocked` uses `tempfile.mkdtemp()`, which on Linux returns `/tmp/...` — caught by
  the static prefix before the env-var branch is reached.
- `test_windows_temp_env_blocked` passes the **literal string** `%TEMP%\\out.txt` — caught by the
  substring list, not by expanding an env var.

The branch exists for the platforms this suite does not run on: macOS `/var/folders/...` and Windows
`C:\\Users\\...\\AppData\\Local\\Temp`, neither enumerable by a static prefix. This is exactly the
"guard narrower than the invariant it claims to enforce" class the audit ranks third, and it was
invisible until the mutation ran. `test_relocated_temp_dir_blocked_via_env_only` now targets a path
no static list matches, so only the env-var branch can block it, with
`test_the_relocated_temp_probe_is_not_caught_by_a_static_list` guarding that the probe stays outside
the static lists — otherwise the new test would start passing for the wrong reason.

**4. A test was therefore added, against the spec's instruction.** The spec says "Add no new test",
on the premise that the 12 existing location tests already held the behaviour. They do not hold all
of it. Two tests added; behaviour unchanged.

**MCP re-check:** the rule asserts no Senzing fact. The one Senzing detail written into shipped text
— that `mapping_workflow` and `analyze_record` require `workspace_dir` and that the server warns
"do NOT assume /tmp exists" — was re-confirmed this session via `get_capabilities` on server 1.32.8,
not carried from the spec.

## Invariants introduced

- `INV-200` — Every file the bootcamp writes MUST live inside the Bootcamper's project directory;
  the write-gate MUST block a resolved target under system temp, `~/Downloads` or reached by `..`,
  while allowing project-relative and in-project absolute paths including a project beneath a temp
  directory; and the rule binds MCP tool arguments (`workspace_dir`), not only file writes
  (recorded in `specs/INVARIANTS.md`, indexed under **Platform, shell, encoding and file
  placement**).
