# The one-question-per-turn rule is registered nowhere

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`ground-rules.md` calls it the worst failure the plugin has:

> ⛔ **Doing both ends the turn on two 👉, which INV-005 forbids** — the violation this file calls
> the #1 bootcamper complaint. (`ground-rules.md:124`)

**INV-005 does not forbid it.** Its entire text is one sentence:

> **INV-005** — Each question to the Bootcamper is preceded by "👉".

That is a **marker** rule — every question carries the 👉 prefix. It says nothing about *how many*
questions a turn may contain. A turn ending on three 👉-prefixed questions satisfies INV-005
completely.

The same file cites it for the count four times:

| Site | Text |
|---|---|
| `ground-rules.md:60` | "the turn carries exactly one 👉 (INV-005)" |
| `ground-rules.md:124` | "Doing both ends the turn on two 👉, which INV-005 forbids" |
| `ground-rules.md:654` | "INV-005 governs how many questions *you* ask, and it is unconditional" |
| `ground-rules.md:830` | "(exactly one 👉 per turn — INV-008/INV-009)" |

⚠️ **The last one names two more invariants that are also about something else.** INV-008 is
*"Questions are not ambiguous with respect to a 'Yes' or 'No' answer."* INV-009 is *"Questions are
not 'complex'. The use of 'or' is discouraged."* Ambiguity and complexity — neither is a count.

**No invariant states the rule.** Every one of the 249 invariant entries was parsed and searched in
full for any per-turn question count. Four mention one, and **all four are scoped to a specific
case**, not the general rule:

- **INV-063** — the model/effort switch "MUST pause with a single 👉 yes/no question … its own
  yielding turn, never combined with another 👉 question". Scoped to that nudge.
- **INV-064** — the accepted-switch continuation, "ending that turn on that step's single 👉
  question". Scoped to that continuation.
- **INV-135** — the license-request PII path, "requested one question per turn". Scoped to that flow.
- **INV-225** — cites *"System verification contains exactly one 👉 in the whole module"* as
  supporting evidence for the non-yielding-step rule. An observation, not a condition.

So the bootcamp's most-emphasized interaction guarantee exists in the product, is stated in
**13 shipped places** (swept below), is enforced with ⛔ zero-tolerance framing, and is checked at
runtime by `auto-test`'s transcript linter — while being bound by no invariant, and labeled
everywhere with IDs that govern something else.

## Root cause

**The rule predates the ruleset's habit of registering rules, and nothing since has noticed.**
INV-005–INV-009 read as a block about questions, and the count feels like it belongs among them —
so every site reaching for an authority grabbed the nearest plausible ID. Three things then kept it
invisible:

1. **`citations.py verify` passes.** INV-005 exists, so every reference resolves. The toolchain can
   confirm an ID is real and cannot confirm it is the *right* one — the same blind spot recorded on
   `inv077-supersession-dropped-the-visualization-verification-guarantee` earlier today.
2. **The one place that *does* enforce it embeds the wrong ID in its output.**
   `.claude/skills/auto-test/transcript_lint.py` lints real transcripts and counts 👉 per turn —
   correctly, and it is the only mechanism in the repo that checks the rule as *behavior* rather
   than as text:

   ```python
   def check_one_pointer_per_turn(turns):
       """INV-005: exactly one 👉 per turn, and it ends the turn."""
       ...
       out.append(_finding(BREAKING, "INV-005-multi-question", index,
                           f"{count} 👉 in one turn; exactly one is allowed"))
   ```

   The **finding code itself** is `INV-005-multi-question`. So every auto-test run that catches a
   two-question turn reports the breach against an invariant that does not state the rule, and the
   maintainer reading that report is pointed at a one-line marker rule. The check is right; its
   label is wrong. The offline suite (`tests/`) contains no runtime assertion — correctly, since a
   turn boundary is not reachable from a file read — but three test files *quote* the rule and one,
   `tests/test_non_yielding_steps.py:3`, repeats the misattribution in its own docstring:
   *"INV-005: exactly one 👉 ends each yielding turn"*.
3. ⛔ **The maintainer tooling propagates the same misattribution.** `production-readiness-audit`'s
   own charter says *"INV-005–INV-009 (one 👉 question, asked once, no unrequested skips)"*. Two of
   those three are correctly placed — "asked once" is **INV-006**, "no unrequested skips" is
   **INV-014** — and the count is not any of them. The skill that exists to catch this class states
   the error in its own text.

**The sites, swept rather than assumed (INV-246) — and the first sweep undercounted.** A pattern
requiring "per turn" near "one" found nine sites; widened to catch "exactly one 👉" and
"ends the turn on one" in any phrasing, the rule is stated in **13 shipped places across 9 files**,
plus **9 sites in `tests/`** and **2 in `.claude/`**. Five of those cite an invariant for the count,
and **every one of the five is wrong**:

| Site | Cites | Should cite |
|---|---|---|
| `bootcamp-onboarding/ground-rules.md:60` | INV-005 | the new ID |
| `bootcamp-onboarding/ground-rules.md:830` | INV-008/INV-009 | the new ID |
| `bootcamp-onboarding/feedback.md:250` | INV-006, INV-005 | INV-006 is right (ask-once); INV-005 is not |
| `tests/test_non_yielding_steps.py:3` | INV-005 | the new ID |
| `.claude/skills/auto-test/transcript_lint.py:80` + finding code | INV-005 | the new ID |

Stating the rule with **no** citation at all: `ground-rules.md:34` (the canonical statement) and
`:49`, `bootcamp-onboarding/SKILL.md:69`, `feedback.md:11`, `graduation/SKILL.md:1048`,
`module-00.../concepts.md:149`, `module-03-system-verification/SKILL.md:22`,
`module-04-data-collection/SKILL.md:26` and `:800`,
`module-05-data-quality-mapping/phase1-quality-assessment.md:678`.

⚠️ **`module-01-business-problem/phase2-document-confirm.md:71` also cites INV-005 for "one per
turn"** and was found by the narrower first sweep; it is a sixth wrong citation.

## Why this matters more than an ordinary wrong citation

**A rule with no ID is one a later editor cannot look up, and this rule has already been edited
twice today.** Both of this session's conversational changes — the host-control turn-shape
alternation and the two-branch recovery — argue from "INV-005 forbids two 👉". If a future reader
checks INV-005 against those arguments, they will find a one-line marker rule that does not support
them, and the correct-looking conclusion is that the guidance overreaches.

⚠️ **The scoped invariants make that worse, not better.** INV-063 and INV-064 *do* mandate a single
👉 for their own cases. A reader reconciling them with an unregistered general rule could reasonably
conclude the count applies only where an invariant says so — which is precisely backwards.

## Proposed change

1. **Register the general rule.** Draft for the maintainer's sign-off — wording deliberately about
   the *turn*, since that is the unit the failure occurs in:

   > Every turn that yields to the Bootcamper MUST end on **exactly one** 👉 question. A turn MUST
   > NOT present two or more 👉 questions, and a yielding turn MUST NOT end on none. Questions the
   > Bootcamper raises, and any-time controls they invoke, do not count against this (they are not
   > the guide's questions); the scoped single-question rules at INV-063, INV-064 and INV-135 are
   > instances of this rule, not exceptions to it.

2. **Correct the four `ground-rules.md` citations** and the one in
   `module-01.../phase2-document-confirm.md:71` to the new ID. INV-005 stays cited where it is
   right — the 👉 *marker* — and INV-008/INV-009 for ambiguity and complexity.

3. **Cite the new ID at the canonical statement** (`ground-rules.md:34`), which currently carries
   none, and at the remaining seven sites per INV-183.

4. ⛔ **Correct the audit skill's own charter text.** `.claude/skills/production-readiness-audit/SKILL.md`
   summarizes INV-005–INV-009 as including "one 👉 question". It does not ship, but it is the file
   that tells the next auditor what to check, and it currently teaches the misattribution.

5. **Re-label `transcript_lint.py`'s check and its finding code** to the new ID. The check itself
   is correct and must not change — only the docstring and the `INV-005-multi-question` code, which
   is what a maintainer reads in an auto-test report. ⚠️ **Changing a finding code is a visible
   output change**, so say so where auto-test's codes are documented rather than renaming silently.

6. **Do not write an offline test asserting the runtime behavior.** It is a live-turn property; a
   guard can assert the rule *ships and is cited correctly*, and must say that is all it does. The
   behavioral check already exists and belongs where it is — in `auto-test`, against transcripts.

## Acceptance criteria

- [ ] An invariant states the general one-👉-per-yielding-turn rule, worded and **approved by the
      maintainer**, with its index entry in the same edit.
- [ ] No shipped text cites INV-005, INV-008 or INV-009 as the authority for the *count*; INV-005
      remains cited for the 👉 marker and INV-008/INV-009 for ambiguity/complexity.
- [ ] The canonical statement at `ground-rules.md:34` cites the new invariant.
- [ ] Every shipped site stating the rule is reached — the site set **derived by scanning** for the
      rule's phrasing, not from this spec's list (INV-246), with a membership floor.
- [ ] The audit skill's charter no longer attributes the count to INV-005–INV-009.
- [ ] `transcript_lint.py`'s docstring and finding code name the new invariant, its counting logic
      is unchanged, and the code rename is recorded where auto-test's finding codes are described.
- [ ] A guard fails when a shipped site states the count rule while citing INV-005/008/009 for it —
      **negative-controlled**, mutation verified to land, then reverted.
- [ ] ⛔ Not runtime-verified, and the guard's docstring says so: whether a guide actually ends a
      turn on one question is a live-turn property reachable only by `dry-run` phase 3. A clean run
      means the rule is registered and correctly cited, never that it is obeyed.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry. **No existing entry
  edited** — INV-005/008/009 are correct as written and are not the problem.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:34`, `:60`, `:124`,
  `:654`, `:830`.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase2-document-confirm.md` — `:71`.
- Six further shipped sites stating the rule without a citation (listed in `## Root cause`).
- `.claude/skills/production-readiness-audit/SKILL.md` — the charter summary.
- `.claude/skills/auto-test/transcript_lint.py` — the check's docstring and its
  `INV-005-multi-question` finding code (logic unchanged).
- `tests/test_non_yielding_steps.py` — the docstring's misattribution.
- `tests/` — one new guard.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15k
  (`Source: self-observed (assistant retrospective)`). Found by completing the class-5 read that
  audit **2026-08-15j** left owed: it read 7 of `ground-rules.md`'s 93 citations and disclosed 86 as
  unread. This run read the rest.
- Priority: **High.** It is the rule the plugin itself calls the #1 bootcamper complaint; it is
  stated in nine shipped places; where it cites an authority it cites the wrong one; no invariant
  binds it and no test enforces it. Nothing is broken for a bootcamper *today* — the guidance is
  correct and emphatic — but the rule most likely to be "reconciled" away by a careful future editor
  is the one with no ID behind it.
- MCP re-check: **n/a (no Senzing fact).** Internal: invariant texts against citations of them. No
  Senzing claim asserted, no absence about the server relied on. Server **1.32.9**
  (`get_capabilities`, 2026-08-15) recorded earlier this session.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `inv077-supersession-dropped-the-visualization-verification-guarantee` (same class,
  found the same way, earlier today), `host-control-handling-clause-can-be-read-as-two-questions-in-one-turn`
  and `results-presentation-turns-end-with-zero-questions` (both argue from "INV-005 forbids two 👉"),
  `statement-only-step-cannot-satisfy-one-question-per-turn`, and INV-005, INV-006, INV-008, INV-009,
  INV-014, INV-063, INV-064, INV-135, INV-183, INV-225, INV-246.

## Invariants introduced

- `INV-251` — A turn presented to the Bootcamper MUST NOT contain **two or more** 👉 questions:
  the guide asks exactly one per yielding turn and ends the turn on it. Questions the Bootcamper
  raises, and any-time controls they invoke, do not count against this. (Recorded in
  `specs/INVARIANTS.md`, indexed under *Questions, gates and bootcamper-facing conversation*.)

## Deviations from this spec, and why (2026-08-15)

- ⛔ **The spec proposed a two-part invariant; only ONE part was missing, and the maintainer chose
  the narrower wording.** This spec's draft said *"MUST end on exactly one 👉 … and a yielding turn
  MUST NOT end on none."* The second half is **already registered**: **INV-225** states that a step
  with no 👉 *"MUST NOT end a turn"*, and both zero-case specs
  (`results-presentation-turns-end-with-zero-questions`,
  `statement-only-step-cannot-satisfy-one-question-per-turn`) resolve to INV-225. So INV-251 states
  only the two-or-more prohibition and points at INV-225 for the rest — maintainer decision,
  2026-08-15, on the ground that duplicating a clause across two IDs is how they drift apart.
- **The exemption clause survived into the invariant**, rather than being demoted to prose: the
  any-time-controls path in `ground-rules.md` relies on it, and a reader meeting an unqualified
  "never two 👉" would have no basis for the bootcamper-raised case.
- ⛔ **The guard caught a site I had listed in the spec and then failed to fix.**
  `feedback.md:250` — *"so that exactly one 👉 ends the turn (INV-005)"* — was named in the spec's
  own site table and missed during implementation. `test_no_count_line_cites_a_question_invariant_that_is_not_the_count`
  reddened on it. This is the case for deriving a guard's site set by scanning rather than working
  from a list, including the spec's own list (INV-246).
- **Three existing guards pinned the old citations and had to move with them** —
  `test_ground_rules_nonyielding_presentation.py:89` asserted `INV-005` in the non-yielding
  section, `test_no_host_control_is_offered_as_a_question.py` pinned *"which INV-005 forbids"* in
  the two-turn-shapes clause, and `EXPECTED_PAIRS` went 63 → 64. All three failures were the guards
  working, not collateral damage.
- **`transcript_lint.py` was RELABELED, never rewritten.** Its finding code moved
  `INV-005-multi-question` → `INV-251-multi-question` at **two** sites — the emitter and the
  self-test's expected-code set — which an `assert count == 1` caught before writing. The counting
  logic is untouched, `test_the_counting_logic_is_unchanged` guards that, and the linter's own
  `--selftest` still reports *"all 9 checks behave"*.
- **Three sites state a FACT, not the rule, and deliberately carry no citation:**
  `module-03-system-verification/SKILL.md:22`, `module-04-data-collection/SKILL.md:26` and
  `module-05-data-quality-mapping/phase1-quality-assessment.md:678` say how many 👉 a given module
  or gate contains. That is an observation about content, not a statement of the rule, and citing
  INV-251 there would imply the rule is what makes it true.
- ⛔ **Not runtime-verified, and the guard says so.** Whether a guide ends a turn on one question is
  a live-turn property. The only behavioral check is `auto-test`'s transcript linter, against real
  transcripts; `dry-run` phase 3 judges a live turn. Seven mutations prove the rule is registered
  and correctly cited — nothing proves it is obeyed.
