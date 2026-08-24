# Six hard rules become visible when the detector stops anchoring the stop sign, and none of them cites an invariant

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Fixing `conformance.py`'s hard-rule detector
(`the-hard-rule-detector-misses-every-rule-not-first-on-its-line`, implemented 2026-08-21) took
the section-scoped uncited count from **1 to 7**. The six new hits are rules that were in shipped
prose all along and that **no view could see**, so no audit ever triaged them:

| File | Line | The rule, in brief |
|---|---|---|
| `bootcamp-onboarding/ground-rules.md` | 463 | `${BASH_SOURCE[0]}` is bash-only and expands to *empty* under zsh, so a script locating itself that way breaks for a zsh Bootcamper |
| `bootcamp-onboarding/ground-rules.md` | 470 | a sourced script must never `exit` or `set -e` — it shares the Bootcamper's shell |
| `module-03-system-verification/phase1-verification.md` | 95 | a reachability probe must not be a blocking gate |
| `module-05-data-quality-mapping/phase2-data-mapping.md` | 98 | the source qualifier is required, not tidiness |
| `module-05-data-quality-mapping/phase2-data-mapping.md` | 1147 | `workspace_dir` is a **required** parameter on `analyze_record` |
| `module-06-data-processing/phaseA-build-loading.md` | 22 | do not run the test load here; Phase B step 5 runs it |

Each is a `⛔` rule in shipped guidance whose enclosing section cites no invariant at all — not
merely no *relevant* invariant. This is the reverse contract's own output, arriving for the first
time.

## Root cause

**Nothing is wrong with these rules; they were never triaged because the detector could not
report them.** Two of the six are the strongest candidates for registration and are worth naming:

- **The zsh/`BASH_SOURCE` rule and the sourced-script rule** (`ground-rules.md:463`, `:470`)
  are cross-platform correctness constraints on every generated script the Bootcamp emits, and
  INV-001 makes Linux, macOS and Windows supported while INV-002 makes the SBCP
  language-agnostic. macOS ships zsh as the default login shell, so the first rule governs the
  default experience on one of the three required platforms. Neither is a local instruction.
- **`workspace_dir` being required on `analyze_record`** is a Senzing fact, and it is the one
  item here that ⛔ **MUST be re-verified against the live MCP server** before anything is
  written about it (INV-080). Its truth is the server's to state, not this spec's.

The other three read as step-local sequencing or emphasis, and the honest disposition for them
may well be *not a durable rule* — which is a finding too, and the audit skill's Step 3 lists it
as one of the three valid verdicts.

⚠️ **Do not treat "the count went 1 → 7" as six new defects.** The count moved because the
instrument improved. What is new is the *obligation to triage them*, which is what this spec
records.

## Proposed change

1. **Triage each of the six** against `INVARIANTS.md` by subject, reaching one of the three Step 3
   verdicts: unregistered rule → draft an invariant; registered but uncited → add the citation
   (INV-183); not a durable rule → say so and move on. Record the verdict for all six, including
   the ones that need no change.
2. ⛔ **Re-verify the `analyze_record(workspace_dir=…)` claim against the live server first**, via
   `get_sdk_reference(topic='parameters', filter='analyze_record')`. If the server no longer makes
   it required, the shipped rule is the defect and the fix is to correct the prose, not to register
   an invariant for it.
3. ⛔ **Mint no invariant without the maintainer's explicit sign-off on the wording.** Draft, show,
   wait. This spec deliberately drafts nothing for that reason.
4. **Prefer a citation to a new invariant where one already governs.** The zsh rule may be
   reachable from INV-001/INV-002 as an application rather than a new guarantee; check before
   proposing.

## Acceptance criteria

- [ ] Each of the six has a recorded verdict — invariant drafted (pending sign-off), citation
      added, or explicitly judged not a durable rule with the reason.
- [ ] The `analyze_record(workspace_dir=…)` claim is re-verified against the live MCP server,
      with the tool, parameters, server version and date recorded.
- [ ] No invariant is recorded without the maintainer's sign-off on its wording.
- [ ] Any citation added lands at the step that states the rule (INV-183), not merely in the file.
- [ ] `conformance.py rules` reports fewer uncited sections afterwards, or the ones remaining are
      recorded as judged-not-durable so a later run reads them as triaged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      zsh rule is specifically about a platform whose default shell differs, which is the reason
      it matters.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — lines 463, 470.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — line 95.
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — lines
  98 and 1147.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — line 22.
- `specs/INVARIANTS.md` — only if the maintainer signs off on a drafted rule.

## Source

- Audit: `production-readiness-audit`, 2026-08-21 (iteration 2), as the direct output of fixing
  the detector in the same session. Not from bootcamper feedback.
- Priority: **Medium.** Nothing here is known to be wrong for a Bootcamper today — these are
  rules the plugin states and the ruleset does not record, which is the class that produced
  INV-134's wrong citation. Medium rather than high because the rules themselves appear correct;
  it is their registration that is missing. The `workspace_dir` item could become high if the
  server contradicts it.
- MCP re-check: **required for one item** — `analyze_record(workspace_dir=…)`. The other five are
  internal consistency and touch no Senzing fact. `owner-checked:` not applicable: no claim here
  rests on the server *lacking* anything.
- Upstream: not applicable.
- Related specs: `specs/the-hard-rule-detector-misses-every-rule-not-first-on-its-line.md` (the
  fix that surfaced these), `specs/the-2026-08-21-run-shipped-three-unregistered-guarantees.md`,
  `specs/seven-hard-rules-shipped-in-one-run-with-no-invariant.md`

## Deviations from this spec, and why (2026-08-21)

**The triage found no unregistered rule.** All six were **registered but uncited** — the second of
the three Step 3 verdicts, and the cheapest — so change 3's sign-off gate never engaged and nothing
was drafted. The spec expected the zsh and sourced-script rules to be the strongest candidates for
*registration*; in fact **INV-175** already states both of them almost verbatim, including
`${BASH_SOURCE[0]}` expanding to empty under zsh and the `return`-never-`exit`/`set -e` requirement.
That is the spec reasoning from the absence of a citation to the absence of a rule, which is the
same inference shape INV-194 forbids one level up.

| Rule | Verdict | Invariant |
|---|---|---|
| `${BASH_SOURCE[0]}` is bash-only under zsh | uncited | INV-175 |
| a sourced script must never `exit` or `set -e` | uncited | INV-175 |
| a reachability probe must not be a document search | uncited | INV-204 |
| the source qualifier is required | uncited | INV-177 |
| `workspace_dir` required on `analyze_record` | uncited | INV-136, + INV-200 for the location |
| do not run the test load in Phase A | uncited | INV-089 |

**A seventh rule was triaged beyond the spec's scope.** `phaseB-load-first-source.md:23` was the
long-standing single hit that made up the session baseline of 1, and it is governed by INV-089 for
the same reason as the Phase A rule. Citing it took `conformance.py rules` to **0 in a section
citing no invariant** — the first time this repository has measured zero.

**The MCP re-check confirmed the one Senzing fact.** `get_capabilities` on server **1.33.0**
(2026-08-21) describes `analyze_record` as taking a *"REQUIRED parameter: `workspace_dir` (a
writable directory where the analyzer script and any reports are saved); do NOT assume /tmp
exists"*. `get_capabilities` is the owning route because `workspace_dir` is a parameter of the
**MCP tool**, not of an SDK method, so `get_sdk_reference(topic='parameters')` would not carry it.
The provenance line was added beside the rule.

**Acceptance criterion not met as written:** *"`conformance.py rules` reports fewer uncited
sections afterwards, or the ones remaining are recorded as judged-not-durable."* It reports zero,
which satisfies the first branch, but the spec's expectation that some of the six would be judged
*not a durable rule* did not hold — all six were durable and registered. Nothing was judged
not-durable, so nothing needed recording under that head.
