# The readiness gate states the structural/semantic distinction, then fast-paths on structure anyway

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5's step 5a decides whether a CORD source may **skip the mapping phase entirely**. It names
the right distinction and then does not act on it.

`phase1-quality-assessment.md:107-113` says so plainly:

> **A stronger check, when the engine is available: ask Senzing how it reads the record.** The
> structural test above confirms the *shape*; **it cannot tell you whether an attribute name will
> actually participate in matching.** `getRecordPreview` returns Senzing's own interpretation of a
> record **without loading it**, which answers that directly.

But the value the fast-path is gated on comes from the *structural* test at `:96-105` — valid JSON,
the Entity Specification's structural indicators, `DATA_SOURCE`/`RECORD_ID` present or derivable.
That result is written as `senzing_ready` (`:143`) and the fast-path offer is presented on it
(`:146`). The stronger check is offered as advice, is conditional on the engine being available, and
**nothing consumes its result**.

The consequence, from the bootcamper's investigation: a real Las Vegas / `PPP_LOANS` record obtained
via `get_sample_data` mixes specification attributes with eleven raw source columns —

- mapped: `DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`, `BUSINESS_NAME_ORG`,
  `BUSINESS_ADDR_LINE1`/`CITY`/`STATE`/`POSTAL_CODE`
- unmapped: `Business_Type`, `CD`, `DateApproved`, `JobsReported`, `Lender`, `Loan_Range`,
  `NAICS_Code`, `NonProfit`, `OwnedBy`, `OwnedByRaceEthnicity`, `OwnedByVeteran`

— and satisfies every structural indicator. It would be classified `senzing_ready: true` and offered
the fast-path, skipping the decisions those eleven columns demand. **Structurally loadable is not
fully mapped, and the gate conflates them.**

**A second half compounds it.** The bootcamper's own run took the generated-business-case path — the
default when a bootcamper has no data of their own — which is backed by the `truthset` collection
(CUSTOMERS, WATCHLIST, REFERENCE). Those are genuinely fully mapped, all three were fast-pathed, and
the bootcamper reached graduation without writing a mapping. Their words: *"we need CORDs that are
not pre-mapped to the senzing format so that the bootcamper can learn how to map data"* and *"we
specifically want to practice the mapping and configuration changes based on different use cases"*.
So the one module whose stated purpose is mapping offers to skip itself, on the path taken by exactly
the bootcampers most likely to need it.

## Root cause

The fast-path exists for a good reason — INV-040/041 exempt CORD sources because routing already
load-ready data through mapping is pointless work — and step 5a was built to identify that class.
The structural test is the right *entry* test and was never paired with a completeness test, because
the class it was written for (`truthset`) has no partially-mapped members. `PPP_LOANS` is the case
the design did not have in front of it.

The `getRecordPreview` route was added later as the semantic answer, but it arrived with two
conditions that keep it out of the gate: it needs an engine, and `:115-118` records that preview
"requires the record's `DATA_SOURCE` code to be registered first, even though it writes nothing …
which is why the check fails where it is most natural to run". So the stronger check is documented,
correct, and structurally unable to be the gate.

Nothing catches this: the fast-path is *correct behaviour* for a fully-mapped source, so no test can
assert it never fires, and `senzing_ready` is a true statement about structure.

## Proposed change

1. **Separate the two questions the gate currently answers as one.** Keep the structural test as the
   entry condition — it is what INV-145 requires and it correctly admits both the `FEATURES` and the
   legacy flat shape. Add a **coverage** question on top: what proportion of a record's fields
   correspond to Entity Specification attributes, and which do not.
2. **Offer the fast-path only when coverage is high, and say the number either way.** When unmapped
   source columns are a meaningful share, route to mapping and **name the columns** — those eleven
   are the exercise. When coverage is high, present the offer with the figure, so skipping is an
   informed choice rather than a silent default.
3. **Do not silently skip the module's core skill.** When every selected source is fully pre-mapped,
   say so explicitly and offer mapping practice rather than omitting it — the bootcamper's
   suggestion (2): a raw variant of the same data, or a raw sample from the free-data catalog.
4. **Consider the generated-business-case default** (their suggestion 3): that path serves
   bootcampers with no data of their own, and currently hands them the one collection with nothing to
   map. Changing the default is a curriculum decision, not a defect fix — this spec records it and
   does not settle it.

⚠️ **The threshold is a design decision this spec deliberately does not make.** A fixed percentage
will misfire on payload-heavy sources, where many columns are legitimately `payload` rather than
unmapped — `payload` is a documented `mapping_workflow` disposition, so "not a feature attribute" is
not the same as "not dispositioned". The implementer should decide between a proportion, an absolute
count, or a preview-derived signal, and record which and why. Getting this wrong in the strict
direction re-introduces exactly the pointless-work problem the fast-path was built to remove.

⚠️ **Do not make `getRecordPreview` the gate.** `:115-118` already records why it cannot be: it needs
the `DATA_SOURCE` registered, which belongs to the loading phase. It stays the stronger *optional*
check.

## Acceptance criteria

- [ ] The readiness result distinguishes **structurally loadable** from **fully mapped**, and the
      fast-path offer is gated on the second, not the first.
- [ ] A source with a meaningful share of unmapped source columns is routed to mapping, and the
      unmapped columns are **named** to the bootcamper.
- [ ] The chosen threshold and its rationale are stated at the step, including how `payload`-worthy
      columns are prevented from counting as unmapped.
- [ ] When every selected source is fully pre-mapped, the bootcamper is told the mapping exercise is
      being skipped and offered an alternative — never silently routed past it.
- [ ] The structural test still admits **both** the `FEATURES` array and the legacy flat shape
      (INV-145), and CORD-only gating is unchanged (`:69`, `:164`).
- [ ] `getRecordPreview` remains the optional stronger check with its registration caveat intact
      (`:115-118`); it is not promoted to the gate.
- [ ] A test asserts the step names both questions and does not gate the offer on the structural
      result alone.
- [ ] **Not runtime-verified:** the `PPP_LOANS` field list is the bootcamper's observation from
      `get_sample_data` on 2026-07-27. Confirming it needs a `get_sample_data(dataset='las-vegas',
      source='PPP_LOANS')` call at implementation — and note that tool's documented caveat that
      record retrieval may be filtered to "Denied." via the public Connectors Directory.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  the readiness check (`:96-105`), the recorded result (`:143`) and the fast-path offer (`:146`).
- `tests/` — the two-questions assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "bootcampers can skip mapping entirely — need
  non-pre-mapped data, and a readiness check that distinguishes 'structurally loadable' from 'fully
  mapped'" (2026-07-27, Module: Data Quality, Mapping, and Transformation; Priority: Medium;
  `Source: bootcamper-reported`).
- Priority: **Medium**, as filed. Nothing breaks and no artifact is wrong; the cost is that the
  module's core learning objective can be skipped without the bootcamper knowing it happened.
- MCP re-check: **n/a for the defect itself (server 1.32.3, 2026-07-31).** The finding is about the
  plugin's own gate logic, not about Senzing behaviour. The two Senzing facts the step relies on —
  that the legacy flat shape is still supported, and that CORD ships both shapes — are already
  MCP-cited in the step at `:89-94` and are unchanged by this spec.
- Upstream: not applicable. The MCP server correctly serves the data it has, including
  partially-mapped sources; the routing decision is the bootcamp's.
- Related specs: `specs/module5-fastpath-cord-only-vs-senzing-ready.md` (reconciled the CORD-only
  implementation with the "already-Senzing-ready" wording), `specs/cord-fastpath-load-readiness.md`
  (Module 6's handling of a fast-pathed source), `specs/record-preview-requires-registered-source.md`
  (the registration caveat this spec preserves).

## Deviations from this spec, and why (2026-08-11)

**1. Criterion 3's premise is inverted, with the maintainer's agreement.** It asks the
implementation to state "how `payload`-worthy columns are **prevented** from counting as unmapped".
They cannot be, and the attempt is the defect in miniature: from the record alone a column the
publisher deliberately kept as payload and a column nobody dispositioned are the same thing — a
non-catalog key at the root — and `getRecordPreview` does not help, since it reports which features
Senzing read, never what the publisher intended. So they are not counted as *unmapped*; they are
counted as **undecided** and routed to `mapping_workflow` step 3, which is where `payload` is
actually assigned (one of `feature`, `payload`, `ignore`, `derived`, `extract` — confirmed against
the live tool schema, MCP server 1.32.8, 2026-08-11). A payload-heavy CORD source therefore costs
one mapping pass; the alternative was a gate deciding on the bootcamper's behalf, which is what this
spec exists to stop.

**2. The threshold is a count, not a proportion.** The spec left the choice open and required the
reasoning to be recorded; it is, at the step itself. A percentage has to be tuned against how wide
the source happens to be — `PPP_LOANS` is 11 unrecognised of 19 keys and any threshold catches it,
while one undecided column in thirty passes an 80% rule and still hides a decision.

**3. Criterion 8 was verified, not disclosed.** It marks the `PPP_LOANS` field list as the
bootcamper's 2026-07-27 observation and asks for a `get_sample_data` call at implementation. That
call was made — `get_sample_data(dataset=`'`las-vegas`'`, source=`'`PPP_LOANS`'`)`, MCP server
1.32.8, 2026-08-11 — and returned exactly the split described: eight specification attributes
(`DATA_SOURCE`, `RECORD_ID`, `RECORD_TYPE`, `BUSINESS_NAME_ORG`,
`BUSINESS_ADDR_LINE1`/`CITY`/`STATE`/`POSTAL_CODE`) and the eleven raw columns. The tool's
documented "Denied." filtering did **not** occur on this call.

**4. A hazard the spec did not anticipate: exact string matching.** The catalog names the
attributes `NAME_ORG` and `ADDR_LINE1`/`ADDR_CITY`, while `PPP_LOANS` ships `BUSINESS_NAME_ORG` and
`BUSINESS_ADDR_LINE1`. An exact-match coverage test would therefore report a genuinely mapped
source as 100% unmapped and route it into mapping — the strict-direction failure the spec warns
against, reached by a different road. The step rules exact matching out and shows the counter-
example. Note the honest limit: the Entity Specification documents usage types as "a short label
that distinguishes multiple instances of the same feature on one entity" (confirmed via
`search_docs(category=`'`data_mapping`'`)`, 1.32.8, 2026-08-11), but the indexed documentation does
not state the prefix **encoding** on a flat attribute name. That is marked in the step as an
observed shape rather than a specified rule (INV-080/INV-149).

**5. INV-040's parenthetical.** "CORD data does not require mapping nor transformation" now has a
counter-example. Surfaced to the maintainer before recording; resolved by INV-198 partly
superseding the parenthetical, with an in-place note on INV-040. Its main clause and INV-041/042's
fast-pathed-source exemptions are unchanged.

**6. Coherence edits beyond the Affected files list.** Step 5's "Categorize each data source" said
CORD sources "are eligible for the fast-path … route directly to Module 6", which after this change
was the same rule stated two ways with the copies disagreeing; it now defers to step 5a. The
`fast_path_reason` example string and one "Senzing-ready" reference inside the preview note were
updated to the new vocabulary.

## Invariants introduced

- `INV-198` — Module 5's CORD fast-path offer MUST be gated on a source being both structurally
  loadable **and** fully mapped, recorded as separate fields; a source with unrecognised keys is
  routed to mapping with every column **named**; payload-worthy columns are not excluded from the
  count; the threshold is a count rather than a proportion; and an all-pre-mapped run is told the
  mapping exercise is being skipped and offered an alternative. Partly supersedes INV-040's
  parenthetical (recorded in `specs/INVARIANTS.md`, indexed under **Data quality, mapping and
  validation gates**).
