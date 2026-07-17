# Make Entity Resolution Concepts a discrete, skippable Module 0

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The "ENTITY RESOLUTION CONCEPTS" teaching is delivered inline inside the
onboarding preface — banner, description, and exploration gate — *before* the
WELCOME banner, as a mandatory part of onboarding. A bootcamper who already
understands entity resolution (or who picks a track that does not need the
primer) cannot skip it: it is not a discrete, numbered, optional unit.

The bootcamper asks that it become **"Module 0"** — separate from the onboarding
preface — so that, as tracks are added, the entity-resolution primer can be made
optional per track rather than a compulsory onboarding step.

> "As tracks are added across the modules, the entity-resolution explanation
> should become an optional module rather than a mandatory part of onboarding."

## Root cause

Not a defect — this is the current designed behavior, and it is pinned by
invariants, which is exactly why the change is non-trivial:

- The concepts step is authored as preface item 1 in
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md:9`
  and `:75-86` (step 3), with the banner, description, and gate defined in
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/entity-resolution-intro.md:1-68`.
- `INVARIANTS.md` INV-019–INV-021 pin the ER concepts banner, description, and
  explore gate as **preface** outcomes, and INV-019–INV-027 fix the preface
  order (concepts first, then WELCOME, level-of-detail, track, language,
  questions). Track selection is INV-025 and happens *after* the concepts step.

The request therefore collides with the invariants and cannot be implemented by
editing skill prose alone. Per the skill guardrails this spec surfaces the
conflicts rather than silently overriding them:

1. **INV-013** pins shipped modules to the range `1 → 2 → … → 7`. A "Module 0"
   sits outside that range. It must either be admitted as an explicitly optional,
   non-counted preamble module (the way graduation is a non-numbered stage), or
   INV-013 must be amended — a change of meaning, i.e. a new invariant per the
   `INVARIANTS.md` maintenance rules.
2. **INV-019–INV-021** locate the concepts banner/description/gate in the
   *preface*. Moving them into a module keeps the outcomes true but changes
   *where* they occur; the wording of INV-019–INV-021 (and the preface-order
   framing of INV-019–INV-027) must be reconciled.
3. **Optional-per-track needs the track known first.** Today the track is chosen
   at `onboarding-flow.md:146-158` (step 6), *after* the concepts step (step 3).
   To make Module 0 skippable by track, the track (or an explicit skip decision)
   must be known before Module 0 runs — which reorders the preface relative to
   INV-025, or defers the skip to an explicit bootcamper choice at the Module 0
   boundary (INV-014: modules are not skipped unless requested).
4. **Per-module apparatus (INV-028–INV-032).** A real numbered module normally
   carries the MODULE banner, journey map, before/after framing, step overview,
   and a completion recap. Module 0 must either carry a lightweight version of
   these or be explicitly exempted; today the concepts step has only its own
   banner and the explore gate.

## Proposed change

Carve the entity-resolution primer out of the onboarding preface into a discrete
**Module 0: Entity Resolution Concepts** that is optional and skippable, while
keeping INV-019–INV-021's outcomes satisfied. Recommended approach:

- Create a `module-00-entity-resolution-concepts` skill (or clearly-scoped
  section) that reuses the banner, MCP-sourced description, and the pinned
  explore gate currently in `entity-resolution-intro.md`.
- Remove the concepts teaching from the preface flow in `onboarding-flow.md`,
  leaving the preface to start at the WELCOME banner; hand off to Module 0 at the
  appropriate point (see the ordering decision below).
- Present Module 0 as **optional**: pin a single 👉 skip/keep question (verbatim,
  INV-056) so the bootcamper — or, in future, the chosen track — can skip the
  primer. On skip, proceed directly to Module 1; on keep, run the primer and its
  explore gate.
- Reconcile the affected invariants as part of implementation (this is invariant
  work the `implement-spec` skill records): amend/append so that (a) an optional
  non-counted Module 0 is permitted alongside INV-013's `1 → 7`, (b) INV-019–
  INV-021's location is updated from "preface" to "Module 0", and (c) skipping
  Module 0 is an allowed, requested skip under INV-014.

**Open sequencing decision (resolve during implementation):** whether Module 0
runs before track selection (skip driven by an explicit 👉 question) or after it
(skip driven by track). The feedback's "optional per track" points at the latter,
but that reorders the preface relative to INV-025. State the chosen ordering
explicitly and reconcile the preface-order invariants to match.

## Acceptance criteria

- [ ] Entity-resolution concepts are delivered as a discrete **Module 0**, not as
      an inline onboarding-preface step; the preface no longer teaches the primer
      inline.
- [ ] The ENTITY RESOLUTION CONCEPTS banner, an MCP-sourced description, and the
      pinned explore gate still occur (INV-019–INV-021 remain satisfied, now in
      Module 0).
- [ ] Module 0 is skippable via a single, pinned-verbatim 👉 question (INV-056),
      and skipping it is treated as a requested skip (INV-014); when skipped the
      bootcamp proceeds to Module 1 with no primer.
- [ ] The invariants are reconciled: an optional, non-counted Module 0 is
      admitted without contradicting INV-013, and INV-019–INV-021 (and the
      preface-order framing of INV-019–INV-027) reflect the new location. The
      chosen Module-0-vs-track ordering is documented.
- [ ] All 👉 questions introduced remain single-meaning (INV-008) with no
      "or"-joined choices (INV-051), and exactly one 👉 ends each yielding turn
      (INV-005).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — remove the inline concepts step (currently step 3, `:75-86`), adjust the preface order list (`:7-16`), add the hand-off to Module 0.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/entity-resolution-intro.md` — becomes the source for Module 0's content (relocated or referenced by the new module skill).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/` — new skill implementing Module 0 (banner, description, explore gate, skip gate), or an equivalently-scoped home for the primer.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — any module-order / journey-map framing that must account for an optional Module 0.
- `specs/INVARIANTS.md` — reconcile INV-013, INV-019–INV-021, INV-014/INV-025 as described (invariant amendments recorded by `implement-spec`).

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Make \"Entity Resolution Concepts\" its own Module 0" (2026-07-17, Module General/Onboarding)
- Priority: High
- Related specs: `specs/advanced-modules-8-11-scope.md` (module-range/track reconciliation, different concern); none covering the concepts primer.

## Invariants introduced

Implemented with **Option A** — Module 0 runs after the onboarding preface and before Module 1
(the preface now opens on the WELCOME banner). Sequencing decision documented in
`onboarding-flow.md`, `bootcamp-onboarding/SKILL.md`, and `ground-rules.md`.

- `INV-072` — Entity Resolution Concepts is an optional "Module 0" after the preface / before
  Module 1, offered via a pinned 👉 skip/keep gate; exempt from INV-013's ordering and INV-014's
  no-skip rule, and not subject to the per-module completion apparatus (recorded in
  `specs/INVARIANTS.md`).
- `INV-073` — When Module 0 is run, it presents the ENTITY RESOLUTION CONCEPTS banner, an
  MCP-sourced description, and the pinned explore gate ("Are you ready to move on to Module 1?")
  before Module 1. Supersedes INV-019, INV-020, INV-021 (recorded in `specs/INVARIANTS.md`).
