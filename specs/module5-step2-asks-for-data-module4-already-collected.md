# Module 5 Step 2 asks the Bootcamper to place data its own prerequisite says is already there

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

`module-05-data-quality-mapping/phase1-quality-assessment.md:14-24` — Step 2, "Request sample
data" — instructs the guide:

> For each data source, **ask the user to place sample files in `data/raw/` or `data/samples/`**:
> CSV files (first 10-20 rows) / JSON samples / Database schema with sample values / Screenshots of
> data tables / Text descriptions of fields and data types

**The module's own prerequisite says this is already done.** `module-05-data-quality-mapping/SKILL.md:28`:

> **Prerequisites:** ✅ Module 4 complete (**data sources collected, files in `data/raw/`**).

Data collection is a **required** module that runs immediately before this one (the canonical table
in `bootcamp-preparation/SKILL.md:57-58`), and its whole job is acquiring sources and registering
them in `config/data_sources.yaml`. So on every conforming Core run, Step 2 asks the Bootcamper to
supply files that the previous module already fetched, counted and registered.

**What the Bootcamper experiences.** A 👉 question asking them to go and place data files, when
`data/raw/` already contains them. Best case they answer "they're already there" and the step is a
wasted turn; worst case they believe the previous module failed and re-fetch, which on a CORD source
is a second download of up to 10,000 records and — per `cord-download-rate-limit-is-saved-as-data`
(2026-08-12) — a live rate-limit hazard. Either way it costs a question the bootcamp did not need
to ask (INV-006/INV-012).

**The module knows how to avoid this everywhere else.** Fifty lines later, step 5a says of the same
data (`:78`):

> already retrieved in Step 3: **do not download it again**

So the "don't redo what an earlier step did" idea is present in this very file — it just never
reaches Step 2.

**Step 1 has the milder form of the same defect.** `:9-10` says *"Recap the data sources identified
during the business problem discussion. Review `docs/business_problem.md` for the list."* — naming
only the Module 1 aspirational list, never `config/data_sources.yaml`, which is the registry of what
was **actually** collected and is what every later step in this module reads (`:74`, `:202`, `:431`).
Where the collected set differs from the discussed set — routine, since Data collection is where a
Bootcamper substitutes CORD sources for data they cannot share — Step 1 recaps a list that is not
the list about to be processed.

**No Senzing fact is involved.** Internal consistency only.

## Root cause

Steps 1–2 are written for a **pre-Module-4 world**, and were not revisited when Data collection
became a required module in front of them.

Their shape — "recap what you discussed, now go and put some samples somewhere" — is the shape of a
module that receives nothing and must ask for everything. That was correct when quality assessment
followed the business-problem discussion directly. Once Data collection was inserted between them,
the input contract changed from *"the Bootcamper will bring files"* to *"files are in `data/raw/`
and registered in `config/data_sources.yaml`"*. `SKILL.md`'s Prerequisites line was updated to say
so; Steps 1–2 were not.

Nothing caught it because no test reads a step's instruction against the module's own prerequisite,
and a prose audit reads Step 2 as a perfectly sensible instruction — it is only wrong *relative to
what already happened*, which is exactly the class a conversational walk surfaces and static review
does not.

## Proposed change

1. **Rewrite Step 2 to verify rather than request.** Read `config/data_sources.yaml`, confirm each
   registered source's file is present in `data/raw/` at the recorded count, and report what was
   found. Ask the Bootcamper for files **only** for a source that is registered but missing, or when
   the registry is empty — which is the one case the current wording is right for.

2. **Point Step 1 at the registry.** Recap from `config/data_sources.yaml` (what was collected),
   using `docs/business_problem.md` for the *why* — the business context that motivated each source.
   Where the two lists differ, say so plainly rather than silently preferring either.

3. **Keep a genuine no-data path.** A Bootcamper who reaches this module with an empty registry must
   still be able to supply files; the fix is to make that the exception rather than the default.

⛔ **Do not delete Step 2.** The bring-your-own-data path is real — it is the route for a Bootcamper
whose data cannot leave their machine, and Module 4 supports exactly that. This spec re-frames the
step's default branch, it does not remove the capability.

## Acceptance criteria

- [ ] Step 2 reads `config/data_sources.yaml` and verifies files in `data/raw/` before asking for
      anything, and asks the Bootcamper to place files **only** when a registered source's file is
      missing or the registry is empty. Verified by opening the file.
- [ ] Step 1 recaps from `config/data_sources.yaml`, and uses `docs/business_problem.md` for
      business context rather than as the source list. Verified by opening the file.
- [ ] Step 1 states what to do when the collected set and the discussed set differ.
- [ ] The bring-your-own-data branch still exists and is reachable — verified by reading the step,
      not inferred from the diff.
- [ ] A test asserts Step 2 does not unconditionally instruct the guide to ask for sample files —
      i.e. that the ask is guarded by a registry/missing-file condition. **Not vacuous:** it asserts
      it found and parsed the step, naming it.
- [ ] **Negative-controlled, mutation verified to land:** restoring the unconditional "ask the user
      to place sample files" wording fails the test. Revert.
- [ ] Full suite passes (baseline **1756 passed, 3 skipped**). Record the new total.
- [ ] Stdlib-only, no `plugins/` import (INV-108); cross-platform and language-agnostic.

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md`
- `tests/` — one new guard.

## Source

- Dry run, **phase 3 (conversational walk)**, 2026-08-12, maintainer answering as the Bootcamper.
  Found on the second turn of a Module 5 walk, by reading Step 2 against the module's own
  Prerequisites line before presenting it. The project carried a real, count-verified
  3,488-record `PPP_LOANS.jsonl` in `data/raw/`, registered in `config/data_sources.yaml` — the
  exact state Step 2's prerequisite describes, and the state in which its instruction is wrong.
- Priority: **Medium-low.** No data loss and nothing unrecoverable; a wasted 👉 question on the
  required path for every Bootcamper, with a re-download hazard if they take it literally.
- MCP re-check: **n/a — no Senzing fact.** `get_capabilities` reported server **1.32.9** this
  session; `get_sample_data(dataset='las-vegas', source='list')` was called to build the fixture,
  not to establish anything this spec asserts.
- Related: `cord-download-rate-limit-is-saved-as-data` (why a re-fetch is not free), INV-203 (the
  count-verified collection this module's prerequisite assumes), INV-006/INV-012 (the wasted ask).

## Invariants introduced

**None proposed.** INV-006 (ask once) and INV-012 (suppress what the Bootcamper does not need)
already govern; this is an unapplied instance, and a step whose default branch contradicts its
module's stated input contract is a defect against INV-003 rather than a new rule.
