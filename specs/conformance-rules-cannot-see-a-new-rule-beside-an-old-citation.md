# `conformance.py rules` is section-scoped, so a new unregistered rule is invisible whenever it lands beside any existing citation

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`conformance.py rules` is the mechanical half of the audit's reverse contract: it lists hard rules
(`⛔` / bolded MUST/NEVER) whose **enclosing section** cites no invariant. Its output is what an
unattended run watches to know whether it has shipped an unregistered guarantee, and
`implement-spec` Step 5 now instructs exactly that — *check the count before writing the ledger
entry*.

**The count cannot answer the question it is being used for.** Because the unit is the *section*, a
brand-new rule passes the moment it sits anywhere near an unrelated `INV-nnn`. On 2026-08-21 a run
added **37 hard-rule lines** and the count held at **1**, its session baseline — while three of those
rules were on subjects `INVARIANTS.md` mentions nowhere, and two more restated a rule governed by an
invariant they did not cite.

So the metric read "clean" through precisely the failure it exists to catch. Worse, it reads clean
*more* reliably as the plugin matures: the denser the citations, the less likely any new rule lands in
a section without one.

## Root cause

The check's granularity and its purpose disagree.

- **Purpose:** does the plugin guarantee something the ruleset does not record?
- **Unit:** does the section containing this rule mention an invariant?

A section can mention an invariant for an unrelated reason. Module 2's Step 7 SQLite branch cites
INV-200 (file placement), INV-080 (MCP sourcing) and INV-048 (non-blocking) — all correct, all
irrelevant to the new rule that the datastore's filesystem must be measured before it is created.
The rule is unregistered; the section is well-cited; the check passes.

⚠️ **The 2026-08-17 run is the evidence this is not hypothetical, from the other direction.** There the
count moved 1 → 10 and the audit found seven genuinely unregistered rules. Those seven were visible
only because they happened to land in sections with no citation at all. Nothing establishes that
seven was the whole set — the same run's rules that landed beside a citation would not have been
counted, and the audit reported that it *"targeted the surface that changed today"* rather than
sweeping.

**Why no test catches this.** The suite is offline and asserts N things about N places (INV-108). It
cannot notice that place N+1 states a rule the ruleset omits — that is INV-003's whole-of-plugin
property, which the audit skill's own preamble says is enforced by a person or not at all. The
`rules` count is the only mechanical assistance available, and its granularity silently narrows what
that assistance covers.

## Proposed change

1. **Report the two questions separately, because they need different granularity.** Keep the
   existing section-scoped count — it is a genuine signal and its history is comparable across runs —
   and add a per-rule mode that, for **each** hard-rule line, extracts its subject and reports the
   invariant IDs cited *within the rule itself or its immediately adjacent sentence*, not merely
   somewhere in the section.
2. **Do not attempt to decide registration automatically.** A regex cannot match a rule's subject
   against 260 invariants' prose; attempting it would produce a confident wrong answer, which is worse
   than the current silence. The output should be a **worklist**: rule text, its own citations, and
   the file:line — leaving the judgment where the skill already says it belongs.
3. **Make the diff the unit for an unattended run.** What a run needs is not the corpus count but
   *the rules this run added*. A `--since <ref>` mode listing hard-rule lines introduced since a git
   ref would have surfaced all 37 of the 2026-08-21 additions for review, rather than one aggregate
   number that did not move.
4. **State the limitation in `conformance.py`'s own output and in the audit skill's Step 3.** Until
   the above exists, a run reading "1 in a section citing no invariant" must know that this is *not*
   "1 unregistered rule". The current wording — *"each is EITHER an unregistered rule … OR a missing
   citation"* — is true of the hits and silent about the misses, which is what made it misleading.
5. **Amend `implement-spec` Step 5's instruction**, which currently says to check this count before
   writing the ledger entry. That instruction is load-bearing for unattended runs and currently
   points at a metric that cannot see the class. It should require the per-rule or `--since` view.

## Acceptance criteria

- [ ] `conformance.py` gains a per-rule view reporting each hard-rule line with the invariant IDs
      cited in the rule itself, distinct from the section-scoped count.
- [ ] A `--since <ref>` mode lists hard-rule lines added since a git ref; run against the
      2026-08-21 session range it lists all 37.
- [ ] Neither mode claims to determine whether a rule is registered; both are worklists.
- [ ] `conformance.py rules` output states that the count sees only rules in uncited sections and is
      not a count of unregistered rules.
- [ ] `implement-spec` Step 5 points at the view that can see the class.
- [ ] A test covers the per-rule extraction and the `--since` filter, negative-controlled by adding a
      hard rule beside an unrelated citation and confirming the new view reports it while the
      section-scoped count does not move.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      `conformance.py` is stdlib-only maintainer tooling and reads markdown.

## Affected files

- `.claude/skills/production-readiness-audit/conformance.py` — the new views and the output caveat.
- `.claude/skills/production-readiness-audit/SKILL.md` — Step 3's instruction.
- `.claude/skills/implement-spec/SKILL.md` — Step 5's pre-entry check.
- `tests/` — coverage for the new views.

## Source

- Audit: `production-readiness-audit`, 2026-08-21. Found while checking whether that session's own
  17 implementations had shipped unregistered rules — the count said no, reading said three did.
- Priority: **High.** This is the mechanism that let the 2026-08-17 finding happen and that hid this
  run's equivalent. Every future unattended run inherits it.
- MCP re-check: n/a (no Senzing fact) — maintainer tooling and the plugin's own ruleset.
- Upstream: not applicable.
- Related specs: `specs/the-2026-08-21-run-shipped-three-unregistered-guarantees.md` (what it missed),
  `specs/seven-hard-rules-shipped-in-one-run-with-no-invariant.md` (what it caught, and why that set
  may be incomplete), `specs/guards-enforce-class-scoped-rules-from-hardcoded-site-sets.md`
