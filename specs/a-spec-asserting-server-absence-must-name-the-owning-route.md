# A spec asserting the server lacks something must name the route that owns the fact

Maintain the invariant conditions in @INVARIANTS.md and fix the following improvement:

## Problem

**INV-209** made the owning-route requirement mechanical for `MCP-NEGATIVE` markers — the negatives
that ship inside plugin prose. It does not reach the place two of the three known instances actually
lived: a **spec's own diagnosis**.

Three wrong-route absence conclusions were produced in a single session (2026-08-13), all by the
same mechanism — a real tool, real parameters, a real empty result, an honest date, and the wrong
tool asked:

1. **`no-license-path-environment-variable`** — concluded "Senzing reads no license-path environment
   variable" from `sdk_guide(topic='configure')`, `sdk_guide(topic='install')` and `search_docs`.
   The variable lives in `sdk_guide(topic='load', record_count=<above the limit>)`. This one
   **shipped**: it became INV-208, plus a guard that banned the correct variable name, and the
   offline suite certified it because guard and claim shared a premise.
2. **`pattern-gallery-asks-for-more-than-mcp-can-supply`** — concluded the server covers only 4 of
   10 use-case categories from two broad queries. Sector-vocabulary queries reach nearly all of
   them. Caught before implementation, but only because INV-194 was deliberately re-applied.
3. The marker convention itself, which INV-209 fixed.

Both surviving instances passed through a spec's `## Root cause` and `## MCP re-check` fields, and
**nothing in the spec format asks the question that would have stopped them**: *which tool would
carry this fact if it existed, and did you ask it?* The `MCP re-check` line's documented outcome
vocabulary — "still reproduces | fixed upstream | server now contradicts the plugin | n/a (no Senzing
fact) | unverified (MCP unreachable)" (`feedback-to-specs/spec-template.md:49`) — has no value for
"the server does not cover this", so an absence conclusion is recorded as though it were one of the
positive outcomes, with the tools called listed as evidence.

A spec is a worse place for this error than shipped prose, because a spec is the **input** to
implementation. Instance 1 shows the path: bad diagnosis → invariant → guard → green suite.

## Root cause

INV-209 was scoped to the marker, which is a *plugin-prose* artifact. The same class of claim in a
*spec* has no equivalent field, and the spec template's outcome list implicitly assumes the server
either has the fact, contradicts the plugin, or was unreachable — never "was asked in the wrong
place".

Care is not a sufficient remedy: instance 2 was caught only because the author had been burned by
instance 1 hours earlier and went looking. That is exactly the argument this repo already made for
making INV-194 mechanical rather than trusting attention (INV-207's "care failed under maximum
attention").

## Proposed change

Mirror INV-209 one level up, into the spec format.

1. **`feedback-to-specs/spec-template.md`** — add `server does not cover it` to the `MCP re-check`
   outcome vocabulary, and require that when the outcome is an absence, the line also carries
   `owner-checked: <route that would carry the fact> — <what it returned>`. Same shape and same
   wording as the marker's `owner:` clause, so the two are recognizably one rule.
2. **`feedback-to-specs/SKILL.md`** — state the requirement where specs are authored, with the
   reason: an empty result from a tool that never carried the fact is a true statement about that
   tool and no evidence for the negative (INV-194).
3. **`implement-spec/SKILL.md`** — at the re-verify step, require the implementer to re-ask the
   **owner** named in `owner-checked:`, not merely the tools the spec listed. An absence claim whose
   owner clause is missing is a **blocker**: re-diagnose before implementing. Instance 2 is the
   worked example of that check paying for itself.
4. **A guard over `specs/`** — for specs dated on or after the cutoff, a `MCP re-check` line
   containing absence vocabulary must also contain `owner-checked:`. Exempt lines that declare
   `n/a (no Senzing fact)`: with no Senzing fact there is no absence claim about the server to
   substantiate. (Measured before designing: across 274 specs exactly one line matches the absence
   vocabulary, and it is such an `n/a` line — so the carve-out is required and retroactivity is
   otherwise a non-issue.)

⛔ **Validate the guard with synthetic fixtures, not the repo's current state.** Both offending
specs have since been corrected, so the repo can no longer demonstrate the shape. Testing only
"`specs/` is clean" would produce a guard that passes because the answer is already empty — the
precise vacuity that let a stubbed detector pass earlier in the same session.

## Acceptance criteria

- [ ] `spec-template.md`'s `MCP re-check` line documents the `server does not cover it` outcome and
      the required `owner-checked:` clause.
- [ ] `feedback-to-specs/SKILL.md` states the requirement and its reason, citing INV-194.
- [ ] `implement-spec/SKILL.md` requires re-asking the named owner, and treats a missing owner clause
      on an absence claim as a blocker rather than a note.
- [ ] A stdlib-only guard fails when a spec dated on/after the cutoff records an absence outcome with
      no `owner-checked:` clause, and passes when the clause is present.
- [ ] The guard exempts `n/a (no Senzing fact)` lines, and a test asserts that exemption directly.
- [ ] The guard is validated by **synthetic fixtures** for both the failing and passing shapes, so it
      cannot pass merely because `specs/` is currently clean.
- [ ] `specs/` passes the guard as it stands.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/feedback-to-specs/spec-template.md` — the `MCP re-check` field.
- `.claude/skills/feedback-to-specs/SKILL.md` — the authoring requirement.
- `.claude/skills/implement-spec/SKILL.md` — the re-verify step.
- `tests/test_spec_absence_claims_name_their_owner.py` — new guard.
- `specs/INVARIANTS.md` — the new invariant.

## Source

- Feedback: none — dry run 2026-08-13, generalizing the session's own repeated error at the
  maintainer's request (`Source: self-observed (assistant retrospective)`)
- Priority: High — it is the input path to implementation, and it has already produced a shipped
  false invariant with a guard enforcing it.
- MCP re-check: **n/a (no Senzing fact)** — this concerns the spec format and this repo's authoring
  discipline; no Senzing behavior is asserted. Server version for the session was 1.32.9.
- Upstream: not applicable.
- Related specs: `specs/mcp-negative-markers-must-name-the-owning-route.md` (INV-209, the same rule
  for shipped prose), `specs/no-license-path-environment-variable.md` (instance 1),
  `specs/pattern-gallery-asks-for-more-than-mcp-can-supply.md` (instance 2).
