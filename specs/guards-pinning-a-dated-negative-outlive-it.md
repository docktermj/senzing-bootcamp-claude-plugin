# A guard that pins a dated negative about an MCP tool keeps enforcing it after the server fixes it

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin has a known failure class: it records a **negative** about a Senzing MCP tool's content
("`explain_error_code` returns only generic causes and names no connection to `SUPPORTPATH`"), routes
around the tool on that basis, and dates the claim honestly — after which the server gains the
coverage and nothing re-asks, because a negative cannot go stale detectably without calling the tool,
which INV-108 forbids the suite from doing. Two instances so far:
`senz7221-now-names-its-own-remedy` (2026-07-30) and `explain-error-code-now-owns-senz7426`
(2026-08-12).

**This spec is about a distinct and worse variant that the second instance exposed: the stale
negative was also written into the guards.** Implementing that spec on 2026-08-12 required changing
three assertions in `tests/test_engine_verification_and_senz2027.py` before the correct fix could
pass:

1. `test_the_supported_form_names_the_tool_that_states_it` asserted that module 2 **must** say
   `explain_error_code('SENZ7426')` returns "generic … no connection … makes no" —
   `self.assertRegex(text, r"(?i)explain_error_code\('SENZ7426'\)[^.]{0,200}(?:generic|no connection|makes no)")`
   — with the failure message *"where module 2 makes the SUPPORTPATH link it must also say that
   explain_error_code does NOT make it"*.
2. `test_module_03_does_not_relay_the_generic_explanation` asserted that Module 3 **must** contain
   `do **not** relay` — i.e. the suppression instruction itself was a required string.
3. `test_senz7426_is_never_tied_to_supportpath_unconditionally` carried a `denial` exemption that
   skipped its check for any window in which `explain_error_code` was described as "generic / makes
   no / no connection", commented *"the safety text, not the claim"*.

All three were **correct when written** and became enforcement of a false claim the moment
`explain_error_code('7426')` started ranking SUPPORTPATH as `common_causes[0]`. The suite stayed green
the entire time. Correcting the prose *failed* the suite, and the failure messages told the fixer the
opposite of what the server says — so the cheapest response available to anyone in a hurry was to
revert the correct fix.

**Why this is worse than the prose variant.** Shipped prose carrying a dated Senzing claim is
readable, is bound by INV-080's provenance convention, and gets re-asked by dry runs and
`delegate-to-mcp-server` sweeps. A guard is the thing that is supposed to *catch* drift. When the
guard is the stale party it inverts: it converts from protection into enforcement, and it is
consulted precisely when someone is trying to fix the underlying claim.

**Nothing lists them.** There is no way today to answer "which assertions encode a dated claim about
what an MCP tool does or does not contain, and how old is the newest re-check?" — the dates live in
docstring prose, in no machine-readable form.

## Root cause

Three things that are each individually reasonable.

1. **The suite is offline and stdlib-only (INV-108).** No test may call the server, so a claim about
   a tool's content is unfalsifiable from inside the suite. That is the right constraint and is not
   what should change.
2. **The provenance convention does not reach tests.** INV-080 makes shipped Senzing facts carry
   tool, parameters, server version and date, and `refresh-reverified-provenance-stamps` (2026-07-31)
   established the practice of refreshing those stamps when the version moves. That practice operates
   on shipped text; test files carry their dates as prose inside docstrings
   (`tests/test_engine_verification_and_senz2027.py:113-114` was *"re-verified 2026-07-31, still
   true"*), which no sweep can enumerate.
3. **The report pattern exists but has no entry for this.** `.claude/skills/dry-run/coverage_reports.py`
   already reports two blind spots the suite cannot see — `invariants` (invariants no test cites) and
   `affected` (predicted-but-unrecorded files) — and `implement-spec` Step 4 runs them. There is no
   third report for dated MCP negatives.

The near-precedent is `tests/test_deferral_freshness.py`, which solves the same "the note outlived
the condition" shape for "later porting phase" deferrals. It works because a deferral is
**self-invalidating evidence**: it names a path that should *not* resolve, so a filesystem check
settles it offline. A dated Senzing negative has no offline equivalent — which is exactly why it
needs a *report* that routes it to the one place that can settle it (a live re-check), rather than a
test that pretends to.

## Proposed change

1. **Give a dated MCP negative a machine-readable marker**, usable in a test file or in shipped text,
   on the line above the claim:

   ```text
   MCP-NEGATIVE: explain_error_code('SENZ7426') — no SUPPORTPATH cause — server 1.32.3, 2026-07-31
   ```

   One line: the tool and parameters, what is claimed absent, the server version, the date. The point
   is enumerability, not ceremony.

2. **Add a third report to `coverage_reports.py`** — `negatives` — listing every marker with its
   server version and date, oldest first, and flagging any whose recorded version is behind the
   server version the caller passes (or simply reporting age when offline, since the script is
   stdlib-only and must stay so). Wire it into the existing `choices=("invariants", "affected",
   "both")` CLI and into whatever "run these reports" instructions already cite the other two.

3. **Make the dry run consume it.** `dry-run/phase1-mcp-contracts.md` already re-verifies MCP calls
   against the live server; the `negatives` report is the worklist it currently lacks — every marker
   older than the current server version is a claim to re-ask that phase. This is the step that turns
   the marker from bookkeeping into a check.

4. **Require the marker on any *test* that encodes such a claim, and prefer asserting the present
   truth over the absent future.** Where a guard can be written to assert what *is* true
   (`module 2 names the tool that states the link`) rather than what must *not* be said
   (`module 2 must say the other tool does not`), the second form is what goes stale — instance 2's
   assertion 1 is that mistake exactly, and the fix for it was to rescope to attribution.

5. **Consider registering the rule.** A candidate: *a test assertion that encodes a dated claim about
   an MCP tool's content MUST carry an `MCP-NEGATIVE` marker.* Offer the wording to the maintainer
   rather than assuming it. Note the threshold question: `senz7221-now-names-its-own-remedy`'s ledger
   entry set *"a fifth instance of this class"* as the trigger for an invariant, and this is instance
   **2** — the argument for acting early is that the guard variant defeats the mechanism that would
   otherwise surface instances 3, 4 and 5.

**Out of scope:** re-litigating INV-108. The suite stays offline; this spec adds a worklist for the
runs that are already online.

## Acceptance criteria

- [ ] A documented `MCP-NEGATIVE` marker format exists, and the three sites from instance 2 that
      still describe a dated tool-content claim carry it (or are confirmed to no longer make one).
- [ ] `python3 .claude/skills/dry-run/coverage_reports.py negatives` lists every marker with its
      tool, claim, server version and date, oldest first, and exits 0. The script remains
      stdlib-only and imports nothing from `plugins/` (INV-108).
- [ ] The report is non-vacuous: a test asserts it finds the known markers, so an empty result
      cannot pass as "nothing to re-check".
- [ ] `dry-run/phase1-mcp-contracts.md` names the report as the source of its re-verification
      worklist, and says what to do when a marker's claim no longer holds (correct the claim, and
      invert or rescope the guard rather than deleting it — the `senz7221` precedent).
- [ ] A guard fails when a test file asserts a tool-content negative without a marker.
      Negative-controlled: adding such an assertion without the marker fails the suite, with the
      mutation verified to land.
- [ ] The existing two reports (`invariants`, `affected`) are unchanged in output and still work via
      `both`; `tests/test_coverage_reports.py` still passes.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      marker is a text convention and the report is `pathlib`-based stdlib Python.

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — the third report.
- `.claude/skills/dry-run/phase1-mcp-contracts.md` — consume it as the re-verification worklist.
- `.claude/skills/dry-run/SKILL.md` and `.claude/skills/implement-spec/SKILL.md` — wherever the other
  two reports are already cited, so the third is not orphaned.
- `tests/test_engine_verification_and_senz2027.py` — carry the marker on whatever dated claim
  remains after `explain-error-code-now-owns-senz7426`.
- `tests/test_coverage_reports.py` — cover the new report.
- `tests/` — the marker guard.
- `specs/INVARIANTS.md` — only if the maintainer approves the rule in Proposed change §5.

## Source

- Implementation run: `implement-spec`, 2026-08-12, implementing
  `explain-error-code-now-owns-senz7426` (`Source: self-observed (assistant retrospective)`). Found
  because the correct fix would not pass: three assertions had to be inverted, rescoped or removed,
  and the spec being implemented had predicted only one of them.
- Priority: **Medium.** Nothing is broken today — instance 2's guards were corrected when it was
  implemented. The cost is that the next instance is invisible for as long as the last one was, and
  the guard variant actively resists the fix.
- MCP re-check: **n/a (no Senzing fact).** This spec proposes a mechanism for re-checking Senzing
  facts; it asserts none of its own. The instance-2 facts it cites were verified on server 1.32.9,
  2026-08-12 and are recorded in `specs/explain-error-code-now-owns-senz7426.md`.
- Upstream: **not applicable** — this is entirely a development-process gap in this repo.
- Related specs: `specs/senz7221-now-names-its-own-remedy.md` (instance 1),
  `specs/explain-error-code-now-owns-senz7426.md` (instance 2, and the source of this finding),
  `specs/refresh-reverified-provenance-stamps.md` (the same problem for shipped stamps, solved as a
  one-off refresh rather than a standing mechanism),
  `specs/deep-dive-audit-2026-07-29-minor-fixes.md` (added `coverage_reports.py` and its two existing
  reports).

## Deviations from this spec, and why (2026-08-12)

Implemented as specified. Three things are worth recording, one of which changed what got marked.

1. **The marked sites are not the ones this spec predicted, because instance 2's three sites no
   longer make a negative claim.** Criterion 1 allows for that ("or are confirmed to no longer make
   one"), and confirming it is the right outcome: `explain-error-code-now-owns-senz7426` replaced all
   three with positive statements earlier the same day. Marking them would have been marking nothing.
   A sweep for live dated negatives found **two** real ones instead, and the report is non-vacuous on
   its own evidence rather than on a fixture:

   - `bootcamp-preparation/SKILL.md:270` — *"`sdk_guide(topic='install', platform=…)` … returns no
     language list at all"*, dated **server 1.32.2, 2026-07-29**. The server is now at 1.32.9, so
     this is exactly the class: a negative nothing has re-asked across seven releases. It is the
     first row the report prints.
   - `module-02-sdk-setup/SKILL.md:964` — *"with `language='python'` … returns no install detail at
     all"*, dated **1.32.9, 2026-08-12**, added hours earlier by
     `explain-error-code-now-owns-senz7426`. Current, and now enumerable.

   The report therefore produced a genuine finding on its first run, which is the outcome that
   justifies the mechanism.

2. **The unmarked-negative guard polices assertion lines only, not whole files.** The spec says
   "a test that encodes such a claim". Implemented as: a line performing an assertion that contains
   both an MCP tool name and negative phrasing, in a file with no marker. Docstrings and comments are
   excluded deliberately — several test files *narrate* the historical SENZ7426 claim in prose
   (`test_mcp_output_is_never_suppressed.py` quotes it at length), and that narration is the record
   of why the guard exists, not a live claim. Flagging it would have made the guard unusable on the
   very files that document the defect. The detector is pinned against **both** historical offenders
   verbatim, and against a positive assertion it must not flag, so it cannot be quietly narrowed.

3. **Non-vacuity is a floor, not an exact count.** `test_the_scan_is_not_vacuous` asserts at least
   one marker. Removing one of the two leaves the suite green — correct, since one live negative is a
   legitimate state — while removing **both** fails it. Verified by mutation in that order, so the
   threshold is a stated choice rather than an untested assumption.

No invariant was recorded. Proposed change §5 offers one and this spec's own text flags the conflict:
the `senz7221` entry set instance **5** as the threshold, and this is instance 2. The mechanism ships
either way; the rule is written into `implement-spec`'s Step 3.4 as a ⛔ rather than into
`specs/INVARIANTS.md`, which is where an unpromoted convention belongs until the maintainer promotes
it.
