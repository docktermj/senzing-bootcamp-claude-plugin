# Module 5 fast-path: reconcile "CORD only" implementation with "already-Senzing-ready" wording

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 5's fast-path (skip mapping, route a source directly to loading) is described for the class
"CORD / already-Senzing-ready sources," but implemented for CORD sources **only**. A non-CORD source
that is already Entity-Specification-compliant is therefore forced through Phase 2 mapping, and the
skill contradicts itself between Step 5 and Step 5a.

## Root cause (confirmed)

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md:57-58`
  (Step 5): "CORD / **already-Senzing-ready** sources are eligible for the fast-path (Step 5a) —
  route directly to Module 6 (loading), skipping mapping."
- Contradicted by the Step 5a heading `:67` "(**CORD sources only**)" and `:106-107`:
  "**Non-CORD sources:** Skip this step entirely. **Never present the fast-path offer for sources
  with provenance other than `cord`.**"
- `INV-041` (and INV-042/INV-043) name the exempt class as "CORD / already-Senzing-ready fast-pathed
  sources ... route directly to loading with no mapping." Module 4 explicitly recognizes non-CORD
  pre-mapped data (`module-04-data-collection/SKILL.md:130-131`), yet such a source can never be
  fast-pathed.

## Proposed change

Reconcile wording and behavior so the fast-path eligibility class is stated identically in Step 5,
Step 5a, and the invariants. **Maintainer decision required** between:

- **(a) Narrow to CORD (recommended, lower risk).** Treat CORD as *the* trusted already-Senzing-ready
  class. Change Step 5's bullet to say "CORD" (drop the broader "already-Senzing-ready" phrasing that
  implies non-CORD eligibility). This also touches INV-041/042/043 wording, so it requires maintainer
  sign-off per `INVARIANTS.md` (clarification, not a meaning change — CORD already *is* the fast-path
  class in the code).
- **(b) Broaden Step 5a.** Offer the fast-path to any source detected Entity-Specification-compliant
  (not just `provenance: cord`), gated behind a Senzing-readiness verification so an incorrectly
  "compliant" source is not fast-pathed into a bad load.

Either way, eliminate the Step 5 vs Step 5a self-contradiction. Do not leave a source described as
fast-path-eligible in one place and excluded in another.

## Acceptance criteria

- [ ] Step 5 and Step 5a agree on the fast-path eligibility class; no source is called fast-path-eligible in one place and excluded in another.
- [ ] The chosen reconciliation matches INV-040/041/042/043 (any invariant wording change is made only with maintainer sign-off).
- [ ] If option (b) is chosen, a non-CORD source is fast-pathed only after a Senzing-readiness verification (no unverified fast-path load).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` — reconcile Step 5 (`:57-58`) with Step 5a (`:67`, `:106-107`).
- `specs/INVARIANTS.md` — only under option (a), to clarify INV-041/042/043 wording (maintainer sign-off).

## Source

- Final review audit (2026-07-20), finding **M3** (medium).
- Priority: Medium
- Related specs: `align-invariants-cord-and-optin.md` (CORD fast-path / opt-in alignment), `cord-fastpath-load-readiness.md`, `rename-transformed-to-senzing-ready.md` (INV-084).

## Maintainer decision (2026-07-20)

Chose **(a) narrow to CORD-only**. Step 5's wording now states CORD is the already-Senzing-ready
fast-path class (offered only for `provenance: cord`); non-CORD compliant data — including data that
looks Senzing-ready — continues to Phase 2, matching Step 5a. INV-041/INV-042/INV-043 were clarified
in place (dated 2026-07-20, "no meaning change"). Option (b) broaden Step 5a was not taken.
Implemented — see `specs/IMPLEMENTED.md`.
