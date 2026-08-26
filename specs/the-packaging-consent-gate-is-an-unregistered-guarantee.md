# The packaging flow's consent gate is a hard rule the drafted invariant does not cover

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`skills/bootcamp-onboarding/packaging.md` ships two hard rules governing **what the
Bootcamper consents to** before an archive is written:

- `:22` — ⛔ **Run the dry run first. The question below quotes a measured size, never an
  estimate.**
- `:50` — ⛔ **Option 3 writes nothing at all.**

Neither is registered, and neither is named in the deferral that was supposed to account
for them. `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`'s
`## Invariants introduced` drafts a single invariant covering the archive's **contents** and
**verification** — the two profiles, the top-level directory, `OPEN_ME_FIRST.md`, the
manifest, the exclusion set, the secret scan, the symlink rule, `testzip()` plus the SHA-256
sidecar, and that the plugin transmits nothing. It says nothing about the gate.

⛔ **This is the reverse-contract state the audit exists to catch, on the higher-stakes half
of the feature.** The archive is a distribution artifact: what the Bootcamper is consenting
to is precisely *which of their files travel*, and the measured-size requirement exists so
the question cannot understate that. A rule with no invariant is one nothing binds future
work to — a later edit that lets the question quote an estimate, or that writes on cancel,
would contradict no registered guarantee and fail no test.

## Root cause

The 2026-08-26 implement run followed `implement-spec` Step 5's deferral path correctly in
form and incompletely in substance. Its ledger entry for that spec says the drafted wording
*"is already in the spec file and needs no restating here"* — which is true of the wording
that exists, and silently treats it as covering every hard rule the implementation shipped.

**The deferral was written against the spec's draft rather than against the diff.** Step 5's
guardrail (added by `production-readiness-audit-2026-08-17` after exactly this class) says an
implementation shipping a hard rule owes the invariant **or an explicit deferral naming the
rule, the site, and why**. A deferral that points at a pre-existing draft inherits that
draft's blind spots, and the draft was written before the conversational layer existed.

⚠️ **The same run named its other deferrals rule-by-rule** — the composite-representation
rules at two sites, the verify-by-resolved-path pair, the acknowledge-before-loading pair —
so the discipline was understood and applied everywhere except where a drafted invariant
already existed and looked sufficient.

## Proposed change

**1. Extend the drafted invariant to cover the gate, or draft a sibling.** The guarantee is:
a packaging run asks exactly one pinned, numbered 👉 question before any write; the sizes it
quotes come from a `--dry-run` measurement rather than an estimate; and the cancel option
writes nothing. Prefer extending the existing draft, since it is unminted and the subject is
the same flow — but state the gate as its own sentence so a reader can find it.

**2. Name every hard rule the packaging feature ships, in the ledger entry's deferral.** Not
as prose pointing at a spec file: the list, with `file:line`, so the next audit reads it as
known rather than discovering it.

**3. Add the missing citations once the ID exists.** `packaging.md:22` and `:50` are the
sites; `conformance.py per-rule --uncited` lists both today.

⚠️ **Do not fix this by weakening the rules.** The measured-size requirement is what stops
the consent question understating what travels, and it is cheap — both figures are already
computed by the dry run the flow performs anyway.

## Acceptance criteria

- [ ] The drafted invariant (or a sibling) states the consent-gate guarantee: one pinned
      numbered 👉 question before any write, sizes from `--dry-run` rather than an estimate,
      and cancel writing nothing.
- [ ] The ledger entry for `the-bootcamp-cannot-leave-the-machine-it-was-built-on` names every
      hard rule the feature ships with its `file:line`, rather than pointing at the spec's draft.
- [ ] `conformance.py per-rule --uncited` no longer lists `packaging.md`'s two consent rules
      once an ID exists to cite.
- [ ] A test asserts the flow's consent rules ship: the dry run precedes the question, the
      question is pinned and numbered, and a cancel option is present. ⚠️ Whether a given run
      *obeys* the ordering is not statically testable — say so in the guard's docstring rather
      than implying coverage it cannot have; `dry-run` phase 3 owns it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` — extend the drafted
  invariant to cover the gate
- `specs/IMPLEMENTED.md` — that spec's deferral bullet gains the rule-by-rule list
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/packaging.md` — citations at `:22`, `:50`
- `tests/` — a guard on the consent rules, with its runtime limit disclosed

## Source

- Feedback: n/a — found by `production-readiness-audit-2026-08-26` reading all 36 hard-rule
  lines `conformance.py since --since-last-audit` attributed to the preceding unattended
  implement run; `Source: self-observed (assistant retrospective)`.
- Priority: Medium — the rules are correct and shipped; what is missing is the guarantee that
  binds them. Raised above Low because the subject is consent over which of the Bootcamper's
  files leave the project.
- MCP re-check: n/a (no Senzing fact). The subject is the plugin's agreement with its own
  ruleset; no SDK method, flag, response shape or server behavior is asserted, and no absence
  is claimed, so no `owner-checked:` clause applies.
- Upstream: not applicable.
- Related specs: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` (the feature),
  `specs/seven-hard-rules-shipped-in-one-run-with-no-invariant.md` (the same class, 2026-08-17,
  which produced the Step 5 guardrail this run followed incompletely)
