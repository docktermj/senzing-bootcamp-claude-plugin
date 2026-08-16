# No report says which invariants the shipped plugin never cites

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The repo has two reports for the invariant→enforcement link and **neither looks at shipped
text**:

- `coverage_reports.py invariants` — invariants no **test** file cites.
- `conformance.py rules` — hard rules in shipped text whose section cites **no** invariant.

The second is the closest, and it has a documented blind spot: it is satisfied by *any*
`INV-NNN` in the enclosing section, so a section that cites one invariant is "covered" even
where a different invariant is the rule doing the work. That is how the INV-129/INV-218
borrowed citation survived, and it is how **INV-212 came to be cited nowhere near the step it
was registered from**: `module-01-business-problem/phase1-discovery.md` cites INV-080, so the
scan reported 0 while INV-212's own originating instance named it nowhere
(`production-readiness-audit-2026-08-13`, secondary finding).

Nothing answers the simpler question underneath: **which invariants does the shipped plugin
never mention at all?** Measured 2026-08-13 at 220 defined invariants:

| | count |
|---|---|
| cited somewhere under `plugins/` | 148 |
| **cited nowhere under `plugins/`** | **72** |
| cited by neither `plugins/` nor `tests/` | 39 |
| INV-150+ (development-era), uncited in `plugins/`, not self-declared superseded | **35** |

An invariant in that last column binds the product and is unreachable from it. INV-183 exists
because "a binding rule one file away is unreachable in practice" — a rule zero files away from
any step is the same failure, one degree worse, and no report names it.

## Root cause

Both existing reports were built from the *test* side of the contract, because that is where
the first losses were noticed (INV-060 and INV-097 each stood unimplemented for over a month,
invisible because no test cited them). The shipped side was never given the same treatment, so
the reverse-direction sweep in `production-readiness-audit` has to be done by reading, and
30-odd invariants is more than a run reliably covers — which is exactly how the 2026-08-13 audit
came to disclose "32 of 33 enumerating invariants not re-checked this run".

## Proposed change

Add a **`shipped`** report to `.claude/skills/dry-run/coverage_reports.py` (stdlib-only,
alongside `invariants` / `affected` / `negatives` / `unmarked`), listing every invariant that no
file under `plugins/` cites.

⛔ **The report is worth building only if its output is worth reading, and a raw list of 72 is
not.** Roughly nine of the 35 in the actionable slice — INV-182, INV-191, INV-207, INV-209,
INV-213, INV-216, INV-217, INV-219 among them — govern **specs, the ledger, markers and tests**.
They *should* never appear in `plugins/`; flagging them trains the reader to skip the report,
which is worse than not having it.

**So the design work is the exemption rule, and it is the decision this spec exists to force:**

1. **Preferred: reuse `INVARIANTS.md`'s own "Index by subject".** Its last group is literally
   *"The development record itself — rules governing specs, the ledger and provenance"*, which
   is the exemption, already maintained, already asserted by `tests/test_invariants_index.py`.
   ⚠️ It is **not** a clean partition today: INV-209 and INV-213 are development rules filed
   under *"MCP sourcing and tool contracts"*. Decide whether to (a) accept per-ID exemptions on
   top of the group, or (b) re-file those IDs — noting that re-filing edits the index, which is
   allowed, versus (c) adding a marker to each exempt invariant's own text, which is the most
   explicit and the most work.
2. Whatever the rule, the exemption MUST be **stated in the data, not hardcoded in the script**,
   so an invariant added later is classified by its author rather than by whoever next edits the
   report.
3. Report the remainder in **descending ID order**: a newly registered invariant with no shipped
   citation is the highest-value hit, because it is the case where the rule was written for a
   specific site and the citation was simply never added — INV-212's shape exactly.

Report only. Like the other four, it is a lead generator, not a gate: an invariant may
legitimately be honored without being named, and the report must say so in its own preamble
rather than implying every hit is a defect.

## Acceptance criteria

- [ ] `python3 .claude/skills/dry-run/coverage_reports.py shipped` lists every invariant no file
      under `plugins/` cites, excluding those the agreed exemption rule marks as development-only,
      newest ID first, exit 0, stdlib-only.
- [ ] `both` (or its successor) keeps working, and the four existing reports are unchanged —
      asserted, not assumed.
- [ ] The exemption set is read from the data (`INVARIANTS.md`), not hardcoded in the script, and
      the script fails loudly if an invariant is in no group at all rather than silently exempting it.
- [ ] The report's preamble states that a hit is a lead and not a defect, in the idiom the other
      reports use.
- [ ] A test asserts the report is **not vacuous** — that a scratch tree with one cited and one
      uncited invariant produces exactly one hit — and is negative-controlled. Stubbing the finder
      to `return []` must fail (the `find_malformed_negatives` precedent, where exactly that
      stub left the suite green).
- [ ] INV-212's state is a fixture of the test, not merely a motivating anecdote: an invariant
      cited in `tests/` but in no `plugins/` file MUST appear in this report, since that is the
      case `coverage_reports.py invariants` scores as covered.
- [ ] `production-readiness-audit` names the new report in its Step 1 lead-generator list, and
      `dry-run` consumes it wherever it consumes the others.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — the new report.
- `.claude/skills/dry-run/SKILL.md` — the report list.
- `.claude/skills/production-readiness-audit/SKILL.md` — Step 1's lead generators, and Step 3's
  reverse-sweep instructions, which currently have only `conformance.py rules`.
- `tests/test_coverage_reports.py` — the non-vacuity and exemption tests.
- `specs/INVARIANTS.md` — **only** if the maintainer picks option (b) or (c) above, and only for
  the index/annotation edit; no invariant is proposed by this spec.

## Source

- Feedback: none — self-observed. Raised as loose thread 2 of `production-readiness-audit-2026-08-13` and sized at the maintainer's request the same day (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium.** No bootcamper-facing behavior changes and nothing is broken today. The value is that the reverse direction of the invariant contract is where this repo has repeatedly lost weeks, and it is currently the only direction with no mechanical report — the same argument that produced `list_specs.py` (INV-216) and INV-207: mechanize the check that was correct-but-not-followed rather than restating it more firmly.
- MCP re-check: **n/a (no Senzing fact).** This spec concerns this repo's own reference graph only. Note INV-207: any claim it makes about that graph must be re-verified **after** the change, not before — the counts in `## Problem` were measured at 220 defined invariants on 2026-08-13 and will have moved.
- Upstream: not applicable.
- Related specs: `the-invariant-to-enforcing-test-link-is-asserted-nowhere` (the same gap on the test side, and the precedent for how to report it), `triage-the-twelve-uncited-hard-rules` (closed `conformance.py rules` to 0, which is what made this gap the next one), `globalization-retrieval-names-a-query-that-returns-homonyms` (the INV-212 instance this would have caught first).

## Decisions taken at implementation (2026-08-13)

Both were the maintainer's, asked before any code was written, because the spec exists to force
them:

- **Exemption — option (b), re-file.** INV-201, INV-209 and INV-213 moved into *"The development
  record itself"*; the exemption is then exactly that group, with nothing else to keep in sync.
  The group's own index entry now **declares** that it is the exemption, so an author filing a
  new invariant there can see what it turns off.
- **Scope — report only invariants whose text names a shipped artifact.** A rule naming a file,
  module, step or bundled script is one INV-183 requires to be reachable at that step; a rule
  stating a general property with no artifact is honored by behavior and is not expected to be
  cited anywhere in particular.

Measured effect: **57 → 51** from the exemption alone, **51 → 14** once the artifact filter is
applied. The second filter is what makes it a report rather than a backlog.

## Deviations from this spec, and why (2026-08-13)

- **The spec's framing under-counted the problem, and the maintainer was shown that before
  choosing.** It described the exemption as the decision; measuring it showed the exemption moves
  the count by six and the artifact filter moves it by thirty-seven. The scope question was added
  to the decision and is recorded above.
- **INV-001–INV-050 are out of scope, which the spec did not say.** They are the bootcamp's own
  outcomes, `INVARIANTS.md` states they are deliberately not indexed ("everything below is a
  development rule"), and being unindexed the exemption cannot classify them either way. They are
  honored by the flow existing rather than by any file naming them. Excluded, with the reason in
  the code, and a test pins it.
- ⚠️ **The report surfaced a re-filing candidate on its first live run: INV-108** ("dev-only tests
  MUST live in the repo top-level `tests/`"). It is a development rule filed under *Platform,
  shell, encoding and file placement*, and it matches the artifact filter because its text names
  `plugins/`. **Deliberately not re-filed at implementation time** — the maintainer approved three
  specific IDs, and quietly extending that list is how a data-driven exemption becomes a hardcoded
  one. It stood as the report's first genuine finding about itself.
  **Resolved later the same day (2026-08-13): the maintainer ruled it a development rule and it was
  re-filed** into *The development record itself*. It governs where the repo's own dev-only tests
  live and what they may import, so no shipped file should ever cite it; it surfaced only because
  its text names `plugins/` in a **prohibition**. The report is now at **13** hits. The artifact
  filter was deliberately **not** special-cased to hide the phrasing, which would have made the
  next genuine hit worded that way invisible.
- **Five bugs were found by *running* the report, none by reading it.** `INV_REF` captures the
  three digits rather than the whole ID, so both the citation set and — worse — the **exemption
  set** compared against `INV-NNN` and matched nothing, silently disabling the exemption
  entirely; `_read` raised `UnicodeDecodeError` on the certificate PDF and screenshot assets under
  `plugins/`; a `print("… %d …")` was never given its argument; and the superseded filter searched
  for `"superseded by INV"` inside an **already-lowercased** string, so every retired invariant was
  reported on the first run. Each is now covered by a mutation.
- ⚠️ **One of my mutations was invalid, and ruling it so produced a better test.** "Re-file INV-209
  out of the development group" was MISSED — correctly: under the chosen rule the group *is* the
  exemption, so re-filing is a permitted maintainer edit rather than a regression, and a test
  failing on it would freeze the classification. Replaced with the coupling that can genuinely
  rot: the index must keep **declaring** that group as the exemption, and must keep a name the
  script recognizes. Both mutations are caught.
- **Fixture invariant IDs are assembled at runtime.** Written as literals, `INV-800`/`801`/`802`/
  `900`/`999` read as citations of undefined invariants and failed `citations.py verify` with five
  dangling references — the trap `implement-spec` Step 4 documents, hit here for real.
  `test_citation_census.py` takes the file-level `citations.py: ignore-file` route; that is right
  for the file which tests the scanner and wrong here, since this file carries **eight real**
  citations that must stay verified.
