# Align INV-041/042/043/046 wording with the CORD and requested-skip exemptions they already imply

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Four invariants read as unconditional MUSTs that a careful reader can see are already qualified
elsewhere in the same file:

- **INV-041/042/043** describe mapping, transform-code creation, and transformation as always
  happening — but **INV-040** already carves out CORD / already-Senzing-ready sources ("CORD data
  does not require mapping nor transformation"), which fast-path directly to loading. Read literally,
  041–043 contradict 040 for CORD sources.
- **INV-046** says "Code is created to query, visualize, and discover" as a flat MUST — but
  visualization and discovery are **offered**, and a bootcamper may decline, which **INV-014**
  already classifies as a legitimate requested skip. Read literally, 046 forbids the decline that
  014 permits.

These are wording gaps, not behavioral ones: the exemptions already exist (INV-040, INV-014); the
four invariants just never restated them, so an implementer reading only 041–043/046 could take
them as absolute.

## Root cause

- `specs/INVARIANTS.md` INV-041/042/043 — stated unconditionally, without the CORD/fast-path caveat
  that INV-040 establishes.
- `specs/INVARIANTS.md` INV-046 — stated unconditionally, without the offered/opt-in caveat that
  INV-014 establishes.

## Proposed change

Maintainer decision (2026-07-19): **amend the invariant wording** (in-place clarifications, no
meaning change — each exemption already exists via INV-040 / INV-014):

1. **INV-041** — append: CORD / already-Senzing-ready fast-pathed sources are exempt (route directly
   to loading, no mapping), per INV-040.
2. **INV-042** — append: such sources need no transformation, so no transform code is created for
   them, per INV-040.
3. **INV-043** — append: such sources are already Senzing-ready and route directly to loading with
   no transformation, per INV-040.
4. **INV-046** — append: query code is always created; visualization and discovery are offered and
   their code/artifacts are created when the bootcamper accepts — a decline is a requested skip
   (INV-014).

Each amendment carries a dated "Clarified 2026-07-19 … no meaning change" provenance note, per the
invariant-maintenance rules (clarify wording in place; a meaning change would require a new ID).

## Acceptance criteria

- [x] INV-041/042/043 each name the CORD/fast-path exemption and cite INV-040.
- [x] INV-046 names the offered/opt-in reality and cites INV-014.
- [x] Each edit is a clarification with a dated provenance note; no invariant ID is reused, renumbered, or deleted.
- [x] The amended invariants no longer read as contradicting INV-040 / INV-014.
- [x] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-041, INV-042, INV-043, INV-046 clarifications.

## Source

- Audit (third deep-dive, "be extra picky"), 2026-07-19 — invariant-coherence findings (CORD caveat missing from 041–043; opt-in caveat missing from 046); maintainer chose "Amend the invariant wording".
- Priority: Medium.
- Related specs: none.
