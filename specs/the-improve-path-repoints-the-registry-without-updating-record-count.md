# The improve path repoints a source's `path` and leaves `record_count` describing the file it replaced

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5's new improve path (`phase1-quality-assessment.md` → `### 7a`) instructs the guide to
**resolve duplicate records** and then repoint the source's `path` in `config/data_sources.yaml` at
the improved file. Resolving duplicates removes records, so the improved file has **fewer records
than the registry says it does** — and nothing in the step updates `record_count`.

That figure is load-bearing, not descriptive. `module-04-data-collection/SKILL.md:475-481` states:

> Record **both** counts in the source's `config/data_sources.yaml` entry — `record_count` (what you
> counted) and `expected_record_count` (what the server stated) … (INV-243: a per-source figure is
> reconciled against that source's own input before it is shown, and this registry entry is where
> that reconciliation stays checkable — **Module 6 Phase B compares its loaded count against the
> `record_count` written here**.)

So a Bootcamper who takes the improve path and resolves duplicates reaches Module 6 and is told their
load is short by exactly the number of duplicates the bootcamp asked them to remove — a correct load
reported as a discrepancy, one module away from the step that caused it.

Two smaller instances of the same shape in the same step:

- `expected_record_count` and the `validation_checks` (`http_status_ok`,
  `record_count_matches_expected`) describe a **fetch**. The improved file was not fetched, so those
  fields now describe an operation that never happened to the file the entry points at.
- Module 4's Step 8a and Step 8b compute the collected total from this registry to drive the
  License-Key gate and the SQLite load-time warning; both would use the pre-dedupe figure.

## Root cause

The improve path was written against the *quality score* — which is what the gate measures — and the
registry entry was updated only where the score's inputs live (`path`). The score has no record-count
term, so nothing in the step's own subject pointed at the field that moves.

⚠️ **The fix that introduced this cited INV-050 for where the file goes and did not ask what else the
registry entry promises about that file.** That is the "rule applied to some of the sites it binds"
class, reached from the other end: the site was updated, but only the field the change was thinking
about.

## Proposed change

1. **Re-measure and rewrite `record_count` from the improved file** in the same step that repoints
   `path`, and say the count changed and why (duplicates resolved), naming both figures.
2. **Say what happens to the fetch-provenance fields.** Either keep `expected_record_count` and
   `validation_checks` describing the original fetch and record that the entry now points at a
   derived file, or move them alongside the recorded original path. Whichever is chosen, the entry
   must not imply the improved file was fetched and count-verified.
3. **Cross-reference INV-243** at the step, so the reason the count matters (Module 6 Phase B's
   comparison) is reachable where the count is changed (INV-183).

## Acceptance criteria

- [ ] The improve path re-measures and rewrites `record_count` whenever it changes the file, and
      states both figures to the Bootcamper.
- [ ] The registry entry never describes a derived file as fetched and count-verified.
- [ ] A repo-level test asserts the improve path names `record_count` alongside `path` (stdlib only,
      no `plugins/` import — INV-108), negative-controlled.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — the
  `### 7a` improve path's registry step
- `tests/` — the guard

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-31, auditing this same session's
  own work (`Source: self-observed (assistant retrospective)`), by asking what else the registry
  entry promises about the file whose path was being changed.
- Priority: **Medium.** It does not corrupt data and only fires on the improve path with duplicates
  present, but its symptom appears in a later module as a load discrepancy, which is the shape that
  costs the most time to diagnose.
- MCP re-check: **n/a (no Senzing fact).** Registry bookkeeping internal to the plugin.
- Upstream: not applicable — plugin-side only.

## Deviations from this spec, and why (2026-08-31)

- **The change is larger than the spec's Proposed change, because the registry entry promises more
  than the two fields the spec named.** The spec asked for `record_count` and a decision on the
  fetch-provenance fields. Reading `module-04-data-collection/SKILL.md`'s entry contract
  (`:583-598`) showed the entry is a **set of claims about the file it points at** — so repointing it
  also falsifies `file_size_bytes`, `quality_score` and `updated_at`. All five are now update
  bullets, and the fetch-provenance fields (`expected_record_count`, `validation_status`,
  `validation_checks`) are explicitly kept describing the original fetch, with INV-203 cited for
  why: the improved file was derived, not fetched, so re-pointing them would assert a check nobody
  ran.
- ⛔ **A third defect in the same paragraph, found while fixing the second: the step named a registry
  field that does not exist.** It said *"point that source's `path`"*; the registry's field is
  **`file_path`**, and no entry has ever carried a `path` key. Nothing would have caught it — the
  guard written alongside the improve path asserted the option had a *handler*, not that the handler
  named real fields. It is now pinned by `test_it_names_registry_fields_that_actually_exist`, whose
  mutation restores the wrong spelling.
- ⛔ **The guard's first version PASSED its mutation, and this is the third time in one session.**
  `test_it_updates_every_registry_field_the_new_file_changes` first asserted the bare substring
  `record_count` anywhere in the improve path — and deleting the entire `record_count` update bullet
  left the word standing in the ⛔ prose that explains *why* it matters, so the guard certified the
  field was updated while the instruction to update it was gone. Rewritten to match the **update
  bullet** (`^- **\`<field>\`** →`), it now fails on that mutation. The recurring shape is worth
  naming: **an assertion a neighboring sentence can satisfy is not an assertion about the claim**,
  and every instance this session was caught by running the mutation rather than by reading the
  guard.
- **Two citations were added after the fact, which the suite caught.**
  `test_new_hard_rules_are_cited_or_deferred` failed on the first full run: the new `record_count`
  and fetch-provenance rules shipped without an `INV-nnn` at the line, even though both invariants
  were named in the surrounding prose. INV-243 and INV-203 are now cited at the rules themselves
  (INV-183).
