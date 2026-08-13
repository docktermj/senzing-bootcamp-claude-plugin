# INV-174 enumerates, no test cites it, and no audit has checked it against the shipped helper

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The 2026-08-13 audit prioritised invariants by intersecting two risk signals:

- **Enumerating** invariants — those stating an exact count, a closed list, or a series of three or
  more literals. An invariant stating a *property* survives change; one *listing members* breaks the
  moment a member moves, and it breaks silently because the list still reads authoritative.
  `conformance.py enumerations` finds **33 of 216**.
- **Cited by no test** — `coverage_reports.py invariants` finds **72 of 216**. This is where INV-060
  and INV-097 hid while standing unimplemented for six and seven weeks.

The intersection is only **three** invariants: **INV-141**, **INV-174**, **INV-177**. Two were checked
that day and both hold — INV-141 (the per-stage table names exactly one model and one effort per row)
and INV-177 (all three fixed `mapping_workflow` filenames carry `{source_name}_` qualifiers).

**INV-174 was not checked, and was disclosed as unchecked.** It is therefore the single
highest-risk-by-measure invariant in the repo: it enumerates, nothing asserts it, and nothing has
verified it against what ships.

What it requires:

> **INV-174** — A completeness, coverage or quality metric MUST NOT count against a record a field
> that cannot apply to it. Measure per record against the fields applicable to that record's kind —
> for Senzing data, its `RECORD_TYPE` — and aggregate those per-record results; never average one
> field's coverage across a whole source of mixed kinds. Applicability MUST be derived from the
> authority for the data (for mapped output, the Senzing Entity Specification via MCP, which marks
> type in its feature descriptions and section headings — `DOB` is "Person date of birth",
> `REGISTRATION_DATE` sits under "(organizations)") rather than from a list hardcoded in the plugin
> (INV-080), and fields that apply to every kind (`ADDRESS`, `PHONE`, `EMAIL`, identifiers) MUST NOT
> be excluded. Where a record's kind is unknown — `RECORD_TYPE` is "Recommended", not required — score
> it against kind-independent fields and report how many records were scored that way. This class of
> error fails toward false alarm: a sanctions list with NAME and ADDRESS on 100% of records scored 69%
> and was route[d] …

It carries **four separately-breakable enumerations**: the per-kind examples (`DOB`,
`REGISTRATION_DATE`), the kind-independent list (`ADDRESS`, `PHONE`, `EMAIL`, identifiers), the
"derive from MCP, not a hardcoded list" requirement, and the unknown-kind reporting requirement.

## Root cause

Why it is unchecked rather than uncheckable: verifying it means reading the **completeness helper's
algorithm**, and `module-05-data-quality-mapping/SKILL.md:40` says that helper is *"authored fresh each
run until that guide is ported"* — so there is no single shipped implementation to point a test at.
That is exactly what makes the invariant fragile: it constrains code the plugin **describes** rather
than ships, so conformance depends on the guidance stating the rule completely enough that a
fresh implementation each run gets it right — which is INV-002's boundary test ("a rule constraining
what the Bootcamper's code must do MUST be stated as behaviour in the any-language contract, never
only in a Python reference implementation").

## Proposed change

**Forward-sweep INV-174 against what ships, then guard the part that can be guarded.**

1. **Read the guidance that governs the metric** — `module-05-data-quality-mapping/SKILL.md` and
   `phase1-quality-assessment.md` — and check each of the invariant's four requirements is stated
   *where the helper is authored*, not one file away (INV-183):
   - per-record scoring against that record's `RECORD_TYPE`, aggregated — never a per-field average
     across a mixed source;
   - applicability derived from the Entity Specification **via MCP**, not a hardcoded list;
   - kind-independent fields not excluded;
   - unknown-kind records scored kind-independently **and counted in the report**.
2. **Re-ask the MCP fact the invariant rests on** (INV-080): that the Entity Specification marks
   feature type in descriptions and headings. `search_docs(category='data_mapping')` for the
   specification's type marking, and confirm the two cited examples still read as the invariant says.
   ⚠️ The ledger row `record-type-feature-applicability-table` records this as `keep-by-design` at
   server 1.32.2 and it has **not** been re-asked at 1.32.9 — so this check is due regardless.
3. **Where a requirement is missing from the guidance, add it as behaviour** in the any-language
   contract — not as a Python snippet (INV-002).
4. **Guard what is guardable.** The helper is authored per run, so a test cannot execute it. What a
   test *can* assert is that the guidance states all four requirements at the step that authors the
   helper — the same shape as the guards over other any-language contracts in this repo. That converts
   INV-174 from "cited by no test" to cited, which is the measure that flagged it.

## Acceptance criteria

- [ ] Each of INV-174's four requirements is confirmed present in the guidance at the step that
      authors the completeness helper, or added there — with `file:line` for each.
- [ ] The Entity Specification's type-marking fact is **re-asked at the current server version** this
      session and cited with tool, parameters, version and date. If the specification no longer marks
      type as the invariant describes, that is a **changed** outcome: report it and do not implement on
      the old premise.
- [ ] Anything added is stated as **behaviour in the any-language contract**, with no rule reaching
      generated code only through a reference implementation (INV-002).
- [ ] A test cites `INV-174` by ID and asserts the four requirements are stated at that step —
      **negative-controlled** by removing each requirement in turn, confirming failure, then
      reverting.
- [ ] `coverage_reports.py invariants` no longer lists INV-174 as uncited, and the enumerating ∩
      uncited intersection drops from 3 to 2.
- [ ] The `record-type-feature-applicability-table` coverage-ledger row is re-recorded at the current
      server version and docs index, whatever the outcome.
- [ ] INV-174 itself is **not edited** unless the server contradicts it, in which case it gets a dated
      correction note and is never renumbered or deleted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/SKILL.md` and
  `phase1-quality-assessment.md` — the requirements, if any are missing at the step.
- `tests/` — one new guard citing INV-174.
- `specs/mcp-coverage.jsonl` — an appended row for `record-type-feature-applicability-table`.

## Source

- Feedback: none — self-observed during the 2026-08-13 `production-readiness-audit`, which computed
  the enumerating ∩ uncited intersection, checked two of the three, and **disclosed INV-174 as
  unchecked** (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium-High.** The invariant's own text records what the defect costs: *"a sanctions list
  with NAME and ADDRESS on 100% of records scored 69%"* — a false alarm that routes a clean source
  into remediation. It fails toward alarm rather than silence, so a Bootcamper is misdirected rather
  than under-served, and nothing in the suite would notice.
- MCP re-check: **required at implementation, not done here.** This spec asserts no Senzing fact of
  its own; the Entity Specification type-marking claim quoted above is INV-174's, recorded at server
  1.32.2 on 2026-07-30, and must be re-asked before anything is written into the plugin (INV-080). The
  quotation is provenance, not a current claim.
- Upstream: not applicable.
- Related specs: INV-174's source spec, `record-type-feature-applicability-table` (the coverage-ledger
  row, `keep-by-design` at 1.32.2 and due for re-check), INV-002 (the any-language boundary test),
  INV-183 (state the rule at the step), INV-128 (the sibling emptiness-test rule, which *is* cited by
  tests).

## Deviations from this spec, and why (2026-08-13)

**The forward sweep found INV-174 already honoured — all four requirements present, at the step that
authors the helper, and the metric definition already cites the invariant by ID.** So proposed change
3 ("where a requirement is missing, add it as behaviour") was **not needed**: nothing was missing.
The work was entirely proposed change 4 — guard what is guardable — plus the re-ask.

Where each requirement lives, verified by opening the file:

| INV-174 requirement | `phase1-quality-assessment.md` |
|---|---|
| Per-record scoring against `RECORD_TYPE`, aggregated | `:350-352` (the metric's own definition, citing INV-174) and `:403-406` |
| Never one average per feature across the source | `:404`, with the worked failure at `:408-415` |
| Applicability derived from the specification, not a list | `:417-419`, naming `search_docs(query='what features to map', category='data_mapping')` |
| Kind-independent fields not excluded | `:428` — "either — do not exclude these" |
| Unknown `RECORD_TYPE` scored kind-independently **and counted** | `:435-440` |

Three things differ from the plan.

1. **The MCP fact is confirmed but the table's stamp was deliberately NOT advanced (INV-191).**
   `search_docs(query='Entity Specification features by record type person organization date of birth
   registration date', category='data_mapping')` on server **1.32.9**, 2026-08-13, confirms the
   *mechanism* INV-174 rests on: `REGISTRATION_DATE` sits under a heading marked **"(organizations)"**,
   and the "What features to map" table marks type in descriptions (`NATIONALITY` "Person
   nationality", `CITIZENSHIP` "Person citizenship", `PLACE_OF_BIRTH` "Person place of birth",
   `REGISTRATION_DATE` "Organization registration/incorporation date"). ⚠️ **The `DOB` row's exact
   wording was not in the retrieved excerpt**, so the table's "Verified against MCP server 1.32.2,
   2026-07-30" stamp stays as it is: advancing a date for a claim only partly re-verified in that pass
   is exactly what INV-191 forbids. The coverage-ledger row records the partial result in those terms.

2. **The guard pins structure, not the specification's wording — INV-219, registered hours earlier.**
   The table quotes the specification, and those quotes are the server's to change. Pinning "Person
   date of birth" would have failed whoever corrects the table after a rewording, with a message
   asserting the opposite of what the server says. So the tests assert that the table exists, maps
   features to PERSON / ORGANIZATION / either, marks shared fields not-to-exclude, and carries the
   re-read-rather-than-trust disclaimer. First application of INV-219 to new code.

3. ⚠️ **I made the over-report error the `invariants` report documents, and had to undo it.** The
   test's first docstring named **INV-141 and INV-177** as rationale ("the other two were checked and
   hold"). Because `coverage_reports.py invariants` greps `tests/` for an ID, that immediately scored
   both as "covered" while nothing asserts either — dropping the enumerating ∩ uncited intersection
   from 3 to **0** and making the repo look better than it is. That is precisely the failure that file
   records (one invariant named by five test files, every one as rationale, none its enforcer). The
   IDs were removed and the reason written into the docstring; the intersection is now honestly
   `{INV-141, INV-177}`, and INV-174 alone left it.

⚠️ **A process note worth keeping.** Negative control R5's first two attempts reported `OK` from a
**missing mutation target**, not an escaped mutation — first a newline typed as a space, then a
lower-case `re-read` where the file has `Re-read`. Only the `assert` in the mutation harness
distinguished them; without it, two clean-looking passes would have certified an untested guard. That
is the third time this hazard is recorded in this repo, and the argument for asserting the target
rather than eyeballing the loop's output.
