# The host-control handling clause can be read as two 👉 questions in one turn

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The INV-247 clause added to the 👉 protocol on 2026-08-15 (`ground-rules.md:116-120`, commit
`a60b669`) reads:

> - **Answering a question the bootcamper asks is not originating one.** They may raise anything at
>   any time; handle a host-control question under "Any-time bootcamper controls" below, then
>   re-present the pending 👉 question verbatim. A clarifying counter-question inside that answer is
>   that turn's single 👉 under INV-005 — it is still not a gate, and it does not replace the pending
>   question.

Two sentences, each prescribing a turn shape, with nothing saying they are **alternatives**:

- Sentence 1 → answer, then re-present the pending 👉. (One 👉. Correct.)
- Sentence 2 → the clarifying counter-question is "that turn's single 👉".

A guide that follows both in one turn answers, asks a clarifying counter-question, *and* re-presents
the pending question — **two 👉 in one turn**, which is the zero-tolerance violation INV-005 names as
"the #1 bootcamper complaint" fourteen lines above, in the same section.

The phrase "that turn's single 👉" does imply the pending question waits. But it is an implication
carried by one adjective, sitting immediately after a sentence that instructs re-presentation, in a
file that applies on every turn.

## Root cause

The clause was written to settle a different question — whether *responding* to a bootcamper's
host-control question counts as the guide originating a gate (it does not) — and folded in the
counter-question case without stating the turn boundary it changes.

`ground-rules.md:637-638` compounds it. The "Any-time bootcamper controls" preamble, which sentence 1
routes to, says:

> They **never count against the one-question-per-turn rule** and must not be treated as gates.

Read together: the any-time controls do not consume the turn's question budget, so a guide can
reasonably conclude that handling a host-control question leaves the budget free for both the
counter-question **and** the re-presented pending question. The two statements are individually
defensible and jointly permit the violation.

⚠️ **This is the auditor's own text from earlier in this session**, and it is the same mechanism the
2026-08-14b audit recorded against its own same-day work: a rule stated where the defect was noticed,
without sweeping the surrounding contract for what it interacts with.

No test catches it: `test_no_host_control_is_offered_as_a_question.py` asserts the clause is
*present*, never that it is unambiguous, and INV-005's own count rule is a conversational invariant
that reading cannot establish (it is `dry-run` phase 3 territory).

## Proposed change

Make the alternation explicit and name the turn boundary. One clause is enough — no new rule, no new
invariant:

> - **Answering a question the bootcamper asks is not originating one.** They may raise anything at
>   any time; handle a host-control question under "Any-time bootcamper controls" below, then
>   re-present the pending 👉 question verbatim — that re-presented question is the turn's single 👉.
>   **If instead the answer needs a clarifying counter-question, that counter-question is the turn's
>   single 👉 and the pending question waits for the turn after it** (never both in one turn — that
>   would end the turn on two 👉, INV-005). A counter-question is still not a gate, and it never
>   replaces the pending question.

Also worth reconciling: `ground-rules.md:637-638`'s "never count against the one-question-per-turn
rule" should say what it means — that *invoking* an any-time control is not itself a bootcamp
question — rather than reading as a blanket exemption from INV-005's count.

## Acceptance criteria

- [ ] The clause states that the re-presented pending question and a clarifying counter-question are
      **alternatives**, and that a turn carries exactly one of them.
- [ ] The clause names the consequence of doing both (two 👉 in one turn) and cites INV-005.
- [ ] The "Any-time bootcamper controls" preamble distinguishes "invoking a control is not a
      bootcamp question" from "this turn may carry a second 👉".
- [ ] A test asserts the alternation is stated, scoped to the 👉-protocol section rather than the
      whole file (INV-183) — **negative-controlled**, mutation verified to land, then reverted.
- [ ] ⛔ Not runtime-verified by this or any test: whether a guide actually ends such a turn on one
      question is a live-turn property (INV-005), reachable only by `dry-run` phase 3. The test
      asserts the text, never the behaviour.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:116-120`, the alternation;
  `:637-638`, the any-time-controls preamble.
- `tests/test_no_host_control_is_offered_as_a_question.py` — one added assertion.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15
  (`Source: self-observed (assistant retrospective)`). Found by re-reading, in context, text the
  auditor shipped earlier in the same session.
- Priority: **Medium**. It governs every turn and sits in the rule with the worst failure history in
  this plugin. No bootcamper has hit it — the clause is hours old — but the ambiguity is in the file
  the guide consults continuously.
- MCP re-check: **n/a (no Senzing fact).** A conversational-protocol ambiguity; no MCP tool was
  called and no Senzing claim is asserted. Server **1.32.9** recorded this session
  (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper` (introduced the
  clause), `results-presentation-turns-end-with-zero-questions` (the sibling INV-005 turn-boundary
  defect), and INV-005, INV-010, INV-011, INV-247.

## Deviations from this spec, and why (2026-08-15)

- **The fix is a two-branch sub-list, not the single reworded clause this spec drafts.** The drafted
  replacement kept both turn shapes in one paragraph; splitting them into an explicit two-item list
  under "The turn then ends one of **two** ways, never both" makes the alternation structural rather
  than something a reader must infer from the adjective in "that turn's single 👉".
- **A CommonMark hook caught a rendering bug that would have reintroduced the defect.** The ⛔
  consequence line initially followed the nested sub-list with no blank line, making it a lazy
  continuation of the **second** sub-item — so "doing both ends the turn on two 👉" would have
  rendered as applying only to the counter-question branch, which is precisely the misreading this
  spec exists to remove. A blank line separates it, and it now attaches to the parent bullet and
  governs both branches.
- **The any-time-controls preamble was rewritten further than "clarified".** This spec proposed it
  "should say what it means"; the shipped text splits the claim in two — *invoking* a control is not
  a bootcamp question and consumes no step, and INV-005 still binds unconditionally — because the
  original single sentence ("never count against the one-question-per-turn rule") is the half a
  guide would cite to justify a second 👉.
- **No Senzing fact required re-verification.** `get_capabilities` was called this session to date
  the run (server **1.32.9**, 2026-08-15), confirming this spec's `MCP re-check: n/a`.
- ⛔ **The runtime half remains unverified, exactly as this spec's own criterion states.** Whether a
  guide ends such a turn on one question is a live-turn property; the five mutations prove the text
  says the right thing, never that the behaviour follows. `dry-run` phase 3 is still owed.
