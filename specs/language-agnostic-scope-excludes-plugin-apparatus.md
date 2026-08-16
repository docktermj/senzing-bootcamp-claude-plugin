# INV-002 states language-agnosticism without scope, while INV-052 and INV-108 mandate Python

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

**INV-002** (`specs/INVARIANTS.md:53`) is unqualified:

> The SBCP MUST be programming-language agnostic.

Three live invariants mandate a specific language:

- **INV-052** (`:389`) — *"All plugin hooks MUST be Python 3 scripts invoked in Claude Code
  exec form … Hooks may require only `python3` on `PATH`"*.
- **INV-108** (`:445`) — dev-only tests *"MUST rely only on the standard library and run via
  `python3 -m unittest discover -s tests`"* — i.e. Python.
- **INV-090** (`:427`) — the bundled Python `senzing_viz_server.py` is a reference model, and
  the invariant says it *"strengthens INV-002"*.

In practice the ruleset resolves this consistently: INV-002 governs what the **Bootcamper
builds** — their transform, load, query and visualization code, which must work in their
chosen language — while hooks, bundled generators and the dev test suite are **plugin
apparatus**, exempt because the Bootcamper neither writes nor runs them. INV-090's phrasing
shows the intent: making the *server* language-native is what strengthens INV-002, while the
Python reference remains.

**But that scoping is never written down.** INV-002 says "the SBCP", which on its face
includes the plugin's own scripts. No invariant states the apparatus carve-out, and no
invariant that mandates Python explains why it does not violate INV-002 — INV-052 offers a
portability rationale ("no shell dependency on Linux, macOS, or Windows") that is about
INV-001, not INV-002.

**What the gap costs.** Unlike this pass's other findings, nothing here is contradictory in
effect — it is an unstated premise, which is why it is filed as an improvement rather than a
fix. The cost is that the boundary must be re-derived by every reader, and a reader who
derives it differently reaches a defensible-but-wrong conclusion in either direction: that a
Python hook violates a foundational invariant, or — more damaging — that INV-002 is satisfied
by shipping a Python-only path for something the Bootcamper *does* run. INV-164 and INV-190
both record real defects of the second kind, where a rule lived only in the Python reference
implementation and reached generated code because no written rule carried it; both had to
state explicitly that they bind a program *"in any language (INV-090/INV-124)"*. Those
invariants are doing, case by case, the scoping INV-002 does not state once.

## Root cause

INV-002 is an original foundational invariant, written before the plugin had hooks, bundled
generators, or a dev test suite. Each of those arrived later with its own invariant, and each
was correct locally, so nothing forced a reconciliation with INV-002's wording. The
distinction that makes them compatible — bootcamper-authored artifact versus plugin apparatus
— emerged in practice and was recorded piecemeal (INV-090's "strengthens INV-002", INV-164's
and INV-190's "in any language" clauses) rather than once at the top.

## Proposed change

**Clarify INV-002 in place to state the scope it already has**: the requirement binds
everything the Bootcamper builds, runs, or takes away — their code, the generated project, and
every artifact produced from their chosen language — and does **not** bind the plugin's own
apparatus (hooks per INV-052, bundled reference generators and scripts, and the dev test suite
per INV-108), which the Bootcamper neither authors nor maintains.

Then name the boundary test that resolves the ambiguous case, because that is the half with
teeth: **if a rule constrains something the Bootcamper's code must do, it MUST be stated as
behaviour in the any-language contract and not only in a Python reference implementation**
(INV-090/INV-106/INV-124, and the pattern INV-164 and INV-190 had to state case by case). A
rule that reaches generated code only through the Python reference is an INV-002 violation
even though the reference itself is exempt.

This is an in-place clarification under rule 2 — the scope is already what the ruleset
implements, and no behaviour changes. It makes an unstated premise explicit rather than
altering a requirement.

⚠️ **Do not "fix" this by rewriting the apparatus in another language or by making the hooks
language-selectable.** INV-052's Python-3-exec-form requirement is a deliberate
cross-platform guarantee (INV-001), and INV-108's stdlib-only rule is what keeps the dev tests
out of the public mirror. Both stay.

## Acceptance criteria

- [ ] INV-002 states its scope: bootcamper-authored and bootcamper-run artifacts are bound;
      plugin apparatus (hooks, bundled reference scripts, dev tests) is not.
- [ ] The clarification names the exempting invariants (INV-052, INV-108) and the invariant
      that shows the intent (INV-090).
- [ ] The clarification states the boundary test — a rule constraining bootcamper code MUST
      appear as behaviour in the any-language contract, never only in the Python reference —
      and cites the invariants that already apply it (INV-164, INV-190, INV-106, INV-124).
- [ ] INV-052, INV-108 and INV-090 are unchanged; no apparatus is rewritten and no hook
      becomes language-selectable.
- [ ] The edit is recorded as a dated in-place clarification stating that no meaning changed;
      no invariant is deleted or renumbered.
- [ ] A test asserts INV-002's text names both halves of the scope, so a later trim cannot
      silently restore the unqualified form.
- [ ] `python3 .claude/skills/compact-dev-environment/citations.py verify` stays clean.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — INV-002 (`:53`), scope clarification.
- `tests/` — the assertion that INV-002 states both halves of its scope.

## Source

- **Found by:** maintainer question — *"Are there any invariants in @specs/INVARIANTS.md
  that conflict with each other?"* — 2026-07-31. Reported in that answer as a latent gap
  rather than a conflict, because the ruleset resolves it consistently in practice; filed here
  because the resolution is nowhere written.
- Priority: **Low.** Nothing is broken and no invariant is violated in effect. The value is
  removing an unstated premise from a foundational invariant, and giving INV-164's and
  INV-190's case-by-case "in any language" clauses a single rule to point at.
- MCP re-check: **n/a (no Senzing fact).** This is the plugin's own language-scope policy; no
  MCP tool owns it and none was called.
- Upstream: not applicable.
- Related specs: `specs/visualization-server-in-chosen-language.md` (INV-090, which
  "strengthens INV-002" and is the clearest existing statement of the intent),
  `specs/organization-search-requires-name-org.md` (INV-164, the defect class this scoping
  prevents), `specs/search-attribute-fallback-survives-a-failed-attempt.md` (INV-190, the
  same class on the error path).
