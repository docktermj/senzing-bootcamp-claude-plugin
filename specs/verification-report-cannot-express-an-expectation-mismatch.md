# The verification report cannot express an expectation mismatch

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

INV-229 shipped on 2026-08-14 (`89e8edd`): System verification's Step 7 no longer
reports a results mismatch as an installation failure. When the engine explains its
decision coherently, the step now says plainly that **the expectation was wrong and
the install is fine**, and marks the check as reported separately from the other
seven.

**Step 9, one step later, has no representation for that outcome — and Step 9 is
what the bootcamper actually sees.** It records "Pass or fail status" per check,
branches on "If ALL checks passed" / "If ANY checks failed", and gates the rest of
the module on that binary. So on the exact path INV-229 was written for — engine
resolves 3 entities where the guide predicted 2, engine explains why, install is
healthy — the guide reaches Step 9 holding a check that is not `passed`, and Step 9
fires:

```text
⚠️  SYSTEM VERIFICATION: FAILURES DETECTED

Failed checks:
• results_validation: <error_summary>
  Fix: <Fix_Instruction>

Please resolve the issues above and re-run system verification.
```

That is the bootcamper-facing failure INV-229 exists to prevent, relocated one step
later and made worse by two side effects the check itself does not have:

1. **The module strands.** `:79-81` — "If any checks failed: do NOT proceed to
   cleanup. Advise the bootcamper to fix the issues and re-run System verification
   from the beginning." Step 10's purge of the synthetic `VERIFY` records never
   runs, so they stay in the database on the way into the next module, and the
   bootcamper is told to redo a module that worked.
2. **The keepsake records a false claim.** `:125` instructs the recap to "capture
   that all 8 checks passed" — unconditionally. On this path the guide is told to
   write something untrue into the durable artifact, or to deviate from a numbered
   instruction. Both readings are damaging, and the second is the one that teaches a
   guide to read numbered steps as advisory.

## Root cause

The INV-229 fix reached the file that **performs** the check and the file that
**summarises** the module, and not the file that **grades** it.

Applied: `phase1-verification.md` Step 7 (`:495-523`) and `SKILL.md`'s success
indicator (7 installation checks, results validation reported separately, "is an
expectation mismatch, **not** a failed verification").

Not applied — `plugins/senzing-bootcamp/skills/module-03-system-verification/phase2-report-close.md`:

| Line | What it still says |
|---|---|
| `:17-18` | "For each check, record: **Pass or fail status**" — two-valued |
| `:22` | "**If ALL checks passed:**" → success banner |
| `:36` | "**If ANY checks failed:**" → FAILURES DETECTED + "re-run system verification" |
| `:55` | module `"status": "passed\|failed"` |
| `:63` | `"results_validation": {"status": "passed\|failed", …}` |
| `:72` | `fix_instructions` — "one entry per failed check, each with … remediation text" |
| `:79-81` | all passed → cleanup; any failed → **do NOT proceed to cleanup**, re-run from the beginning |
| `:125` | recap: "capture that all 8 checks passed against the synthetic `VERIFY` data" |

The same two-valued enum also appears in the file the fix *did* reach:
`phase1-verification.md:531`, Step 7's own checkpoint block, still writes
`"results_validation": {"status": "passed|failed", …}` — eight lines below the prose
defining the third outcome. So the outcome INV-229 requires is unrepresentable in
the machine-readable state as well as in the report, which matters because
graduation and the resume bundle read `config/bootcamp_progress.json`, not the prose.

**Why no test caught it.** `tests/test_results_validation_is_diagnostic.py` opens
`phase1-verification.md` and `SKILL.md` only (`:40`); `phase2-report-close.md` is
never read. Its 24 assertions include `test_a_coherent_explanation_does_not_fail_the_system`
and `test_it_forbids_the_false_report_here_too` — both of which sound like they
cover this and neither of which can see the file that decides what is displayed.
This is the "guard narrower than the invariant it claims to enforce" class: the
guard certifies the two files the implementer edited, which is the one place a
regression will not come from.

**No Senzing fact is at issue.** This is internal consistency between three files
of one module; nothing here re-asserts engine behaviour, so no MCP re-verification
was needed to establish it (INV-080 untouched).

## Proposed change

1. **Give the check three outcomes wherever its outcome is written.** Add
   `expectation_mismatch` alongside `passed`/`failed` in the `results_validation`
   entry at `phase2-report-close.md:63` and `phase1-verification.md:531`, and state
   at both that it means *the install is working and the guide's prediction was
   wrong* — the wording Step 7 already uses.
2. **Make Step 9's branching read the install checks.** "If ALL checks passed" and
   "If ANY checks failed" should be scoped to the **seven installation checks**,
   with `results_validation` reported beneath the banner as its own line. The
   success banner stays reachable on an explained mismatch, since the environment
   *is* verified — that is the whole content of INV-229.
3. **Do not gate cleanup on the diagnostic check.** `:79-81` should proceed to Step
   10 when the seven install checks pass, whatever `results_validation` says. An
   expectation mismatch leaves nothing to fix and nothing to re-run, and skipping
   the purge is a real cost (INV-131 makes teardown the module's last action, and it
   is the synthetic data's only removal point).
4. **Make the recap line conditional.** `:125` should capture what actually
   happened: the seven install checks with their status, and results validation with
   its outcome — including, on a mismatch, the engine's own explanation, which is
   the most interesting thing in the module and is currently thrown away.
5. **Set the module `status` at `:55` from the install checks**, so a healthy
   install is never recorded as a failed module.
6. **Widen the guard** to open `phase2-report-close.md` and assert each of the
   above, so the class cannot recur in the file that displays the result.

## Acceptance criteria

- [ ] `phase2-report-close.md` Step 9 branches on the seven installation checks, and
      an explained `results_validation` mismatch reaches the success banner rather
      than "FAILURES DETECTED … re-run system verification".
- [ ] `results_validation` carries a third outcome in every schema block that
      records it (`phase2-report-close.md:63`, `phase1-verification.md:531`), with
      its meaning stated at both sites.
- [ ] Step 10 (Cleanup) runs when the seven install checks pass, regardless of the
      results-validation outcome; the `VERIFY` purge is never skipped by a
      mismatch the engine explained.
- [ ] The recap instruction at `:125` records the actual per-check outcome and, on a
      mismatch, the engine's explanation — it no longer asserts "all 8 checks passed"
      unconditionally.
- [ ] The module `status` at `:55` reflects the install, not the prediction.
- [ ] `tests/test_results_validation_is_diagnostic.py` reads
      `phase2-report-close.md` and fails if the binary branching, the two-valued
      `results_validation` enum, the cleanup gate, or the unconditional recap line
      returns. Negative-controlled: reintroduce each and confirm the test goes red.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Source

`production-readiness-audit`, 2026-08-14. Found by checking whether INV-229 — one of
the eight invariants registered that day — was honoured at every site it binds,
rather than at the site the spec that produced it named.

- Related: `verification-grades-the-engine-against-the-guides-own-prediction`
  (the spec that shipped INV-229 into Step 7 and `SKILL.md`).
- Establishes no new invariant. INV-229 already governs; this is the invariant
  applied to the third of its three sites.

## Deviations from this spec, and why (2026-08-14)

- **The success banner's text was reworded, which the spec did not ask for.** Proposed change 2 said
  the banner "stays reachable on an explained mismatch" and stopped there — but the banner read
  "**All checks passed.** Your environment is verified…", which is false on exactly that path, and
  it is bootcamper-facing. It now reads "Your environment is verified and ready for subsequent
  modules." — true in both cases, box alignment preserved (58-column interior, recomputed rather
  than eyeballed). No test or invariant pinned the old wording (checked before changing it).
- **`engine_explanation` was added to both checkpoint schemas**, beyond the spec's "third outcome"
  criterion. Step 7 computes the match key and feature scores and Step 9 is asked to report them, so
  without a field to carry them the instruction cannot be followed across a step boundary.
- **The `(INV-229)` citations added here belong to
  `newly-minted-invariants-carry-no-shipped-citation`**, which was implemented in the same session.
  They landed in this spec's edits because the rule and its ID were being written into the same
  sentences; the effect is that INV-229 was already cited when the shipped-citation report was
  re-run, which is why it correctly does not appear in that spec's demonstration set.
