# A check that matches nothing must not report agreement, and no invariant says so

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-03b-truthset-visualization/phase2-close.md` gained this rule on 2026-08-23:

> ⛔ **A comparison that finds ZERO identifiers on both sides has not passed — it has not run.**
> On a dry run the first attempt matched `data-tab="…"`, found none in either file, and reported
> "tab sets match: True"; `data-tab` appears **nowhere** in the generated app. So assert a non-zero
> count on both sides before comparing them, and treat an empty match as a broken check rather than
> agreement.

**Nothing in `INVARIANTS.md` registers that rule**, and it is not a one-off: it is one of the
plugin's most-repeated failure modes, recorded across the ledger under several names and never
generalized.

**Instances already on record, all the same shape — an assertion whose input was empty, passing:**

- The tab-set comparison above (`data-tab` matched nothing, reported agreement).
- `test_every_named_script_exists` and `test_no_hook_parses_its_payload_as_source` keyed off
  `resolved_args()`, so moving the hook scripts out of `args` **emptied their input** and both
  passed while asserting nothing. *"The tell was a 0.000s run that spawned no subprocess."*
  (`stop-hook-ran-bare-python3-and-executed-its-own-payload`, 2026-08-21.)
- `conformance.py rules` reading clean because its pattern missed every stop sign that was not
  first on its line — 145 mid-line rules invisible to every view
  (`the-hard-rule-detector-misses-every-rule-not-first-on-its-line`, 2026-08-21).
- The `implement-spec` skill's own Step 4 warns of it twice in the general — *"a tool that exits 0
  but creates/modifies NO files did not do its job"*, and a malformed ledger heading being
  **absent** rather than invalid to `(?m)^## (\S+)$` — and `test_ledger_files_are_well_formed.py`
  exists solely because *"an entry-shaped assertion cannot notice that a region of the file is not
  an entry, because the parse is the gate"*.
- Found again during the 2026-08-23 run itself, twice, in newly written guards: a
  `search_docs` instruction-site cue silently matched **two of three** sites because the phrase
  wrapped a line, and an exemption-count check tolerated a marker added to a real offender. Both
  were caught only by an explicit anti-vacuity floor.

So the plugin, its maintainer skills and its test suite each carry this rule locally, several of
them having learned it the hard way, and the ruleset that is supposed to bind future work to it says
nothing.

## Root cause

The rule keeps being **re-derived per incident** instead of registered once. Every fix so far has
been an instance fix — a wider regex, an anti-vacuity test, a warning in one skill — which is the
"rule applied to some of the sites it binds" class from the audit's Step 7, with the twist that
here there is no rule to apply incompletely: there is only a habit.

**The adjacent invariants, and why none of them is this rule:**

- **INV-129** — verify the **artifact**, not the exit code. Closest in spirit, and about a produced
  deliverable rather than about a comparison whose operands were empty.
- **INV-218** — a step installing software must verify the artifact on the filesystem rather than
  the installer's exit status. Same spirit, scoped to installs.
- **INV-188** — a user-visible string a script emits must be verified by **executing** the script.
  Adjacent (it exists because scanning source cannot see an f-string's output) and not this.
- **INV-108** — the suite is stdlib-only and offline. Unrelated, but it is *why* this matters: an
  offline suite has no external oracle, so a vacuous assertion has nothing to contradict it.

A check can satisfy all four and still compare two empty sets and report a match.

⛔ **No Senzing fact is in question.** This is a property of the plugin's own checks and guards, so
it needs no MCP call to resolve.

## Proposed change

1. **Register the rule.** Draft wording, for the maintainer's sign-off:

   > **INV-NNN** — Any check the plugin or its guards perform by **matching, counting or comparing**
   > MUST establish that its input is non-empty before reporting a result, and MUST report an empty
   > match as a **failed or unrun check**, never as agreement or as a pass. Where a check compares
   > two sides, both sides MUST be asserted non-empty. A test whose assertion can be satisfied by an
   > empty input MUST carry an explicit anti-vacuity assertion naming the floor it requires. ⛔ **The
   > failure mode is silence, which is why this cannot be left to attention:** an emptied input
   > produces a passing check indistinguishable from a correct one, and every instance on record was
   > found by accident — a 0.000s run that spawned no subprocess, an open count that disagreed with
   > work just done, a comparison that returned `True` on two sets of zero.

2. **Cite it at the sites that already state it**, at the rule (INV-183): `phase2-close.md`'s
   tab-set check, and `hooks/README.md` or `ground-rules.md` if a scan finds the rule stated in
   shipped prose elsewhere.

3. **Adopt it as a test-authoring rule.** The `TheScanIsNotVacuous` / anti-vacuity class already
   appears in many suite files by convention; naming the invariant lets a new guard cite it instead
   of re-deriving it, and lets a reviewer ask for it.

4. ⛔ **Do not attempt to enforce this mechanically across the whole suite in one pass.** A regex
   cannot tell an assertion that *can* be vacuous from one that cannot. Scope any guard to the
   shipped rule's sites; the test-authoring half is a convention the invariant makes citable, not
   something to grep for.

## Acceptance criteria

- [ ] An invariant governing empty-input checks is registered, with the maintainer's sign-off on
      the wording, the next unused ID, and its index entry in the same edit.
- [ ] `phase2-close.md`'s tab-set rule cites it at the rule.
- [ ] A scan establishes whether any other shipped file states the rule uncited, and each such site
      gains the citation.
- [ ] A test asserts the shipped sites carry both halves — the non-zero requirement **and** that an
      empty match is a failure rather than agreement — deriving its site set by scanning
      (INV-246), negative-controlled by softening one site to allow a zero match.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      rule is about check construction, with no platform or language dependency.

## Affected files

- `specs/INVARIANTS.md` — the new invariant plus its index entry.
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` — cite it at
  the tab-set rule.
- `tests/` — the scanning guard.

## Source

- Feedback: none — found by `production-readiness-audit`, 2026-08-23, reading the 19 hard-rule
  lines an unattended `/implement-spec` run had added and searching `INVARIANTS.md` for their
  subjects (`Source: self-observed (assistant retrospective)`)
- Priority: **Medium-High.** No shipped path is currently wrong — the tab check states the rule
  correctly. It is rated above the other reverse-contract findings from the same run because this
  class has recurred at least five times across the plugin, its skills and its suite, and because
  its failure mode is a **false pass**: every instance was found by accident rather than by a check.
- MCP re-check: n/a (no Senzing fact) — the subject is the construction of the plugin's own checks.
  This spec asserts nothing about the server and no absence.
- Upstream: not applicable
- Related specs: `specs/a-step-names-what-to-select-without-naming-the-route.md` (the run that added
  the shipped rule), `specs/stop-hook-ran-bare-python3-and-executed-its-own-payload.md` (two
  assertions emptied and passing), `specs/a-malformed-ledger-entry-is-invisible-to-every-guard.md`
  (absent rather than invalid to the parser),
  `specs/the-hard-rule-detector-misses-every-rule-not-first-on-its-line.md` (a detector reading
  clean on an incomplete pattern)

## Invariants introduced

- `INV-265` — Any check performed by matching, counting or comparing MUST establish its input is non-empty before reporting a result, and MUST report an empty match as a failed or unrun check rather than as agreement; both sides asserted where two are compared, and a test whose assertion can be satisfied by an empty input carries an explicit anti-vacuity assertion (recorded in `specs/INVARIANTS.md`, group *Generator behavior: rendering, encoding, reporting*, alongside INV-129).

Wording signed off by the maintainer on 2026-08-23 ("all"). Two clauses were added beyond the spec's draft, both because the draft was weaker than what is built: the **rendered-first** clause (the collector is keyed by character and returns early on a repeat, so exempting at report time rather than record time would let an exempt passage consume the slot a genuine later occurrence needs — this is INV-266's mechanism, cited here because the same reasoning produced both), and the explicit naming of the four instances on record, so the rule cannot be re-argued as hypothetical.
