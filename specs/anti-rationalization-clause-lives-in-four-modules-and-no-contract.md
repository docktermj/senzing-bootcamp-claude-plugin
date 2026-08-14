# The clause that stops a guide reasoning its way past a 👉 question is in 4 modules of 9

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin states, in some modules, that a step containing a 👉 question **has absolute
precedence and that the guide's own internal reasoning may not override it**. That clause is the
anti-rationalization rule: it is what stops a model deciding, mid-run, that a question is
unnecessary this time.

It is present in **4 of 9** module `SKILL.md` files, in **three different phrasings**, and it is
**absent from `bootcamp-onboarding/ground-rules.md`** — the file that holds the interaction
contract:

| Module | The clause |
|---|---|
| `module-02-sdk-setup` | "no internal reasoning **or token-budget concern**…" |
| `module-03-system-verification` | "no internal reasoning **(session length, context…)**" |
| `module-03b-truthset-visualization` | "no internal reasoning **(session length, context…)**" |
| `module-05-data-quality-mapping` | "no internal reasoning **can override it**" |
| `module-00`, `module-01`, `module-04`, `module-06`, `module-07` | **absent** |

`ground-rules.md`'s only "absolute precedence" is the **MCP-first invariant** (`:92`), which is a
different subject entirely. So a guide running Discover the Business Problem, Data collection,
Data processing or Query/Visualize/Discover is never told the rule at all, and the four modules
that do state it each state a slightly different thing.

Corroborating the same shape, weaker evidence: the resume instruction ("Read `current_step` from
`config/bootcamp_progress.json`…") is in **6 of 10** module skills and phrased differently again in
`module-02`.

## Root cause

The rule was established **by repetition rather than centrally.** Each copy was written where a
specific hazard was noticed — a token budget in SDK setup, session length in the two
visualization-adjacent modules, tool-returned conversational directives in Module 5 (INV-205's
originating case) — and each names its own hazard. Nothing ever hoisted the general statement into
the interaction contract, so the modules where nobody hit a hazard have no statement at all.

This is the audit's defect class 1 — *a rule applied to some of the sites it binds* — with the
aggravating detail that the site which should hold it (`ground-rules.md`) is not one of them.

## Proposed change

1. **State the rule once in `ground-rules.md`**, beside the existing 👉-question rules: a step
   containing a 👉 question has the same absolute precedence as a `⛔` mandatory gate, and no
   internal reasoning — token budget, session length, context pressure, or a judgement that the
   answer is already known — may override it.
2. **Keep every per-module copy that names a local hazard**, and have each cite the central rule
   rather than restating it in full. A restatement *at the step that needs it* is INV-183, not
   redundancy; what must stop is each copy being the only statement of the general rule.
3. ⛔ **Do not delete the hazard clauses.** "token-budget concern", "session length, context" and
   the Module 5 tool-directive framing each name a real observed pressure, and the reason a rule
   exists is what stops it being re-argued (the `deep-dive-audit-2026-07-28b` precedent: a
   corrected example with its reason stripped was "helpfully" corrected back).
4. Do **not** add the clause to the five silent modules by copy-paste — that reproduces the defect.
   They inherit it from `ground-rules.md`, which every module already loads.

**Concision effect:** total words go **down** (four divergent copies become one contract statement
plus four short citations) while coverage goes **up** (5 modules gain the rule). This is the
Goldilocks direction the audit sanctions — merge duplicated statements, move the rule to where it
is used, cut no rationale.

## Acceptance criteria

- [ ] `ground-rules.md` states the 👉-precedence and no-internal-reasoning rule once, in the
      interaction-rules section, and names what "internal reasoning" covers.
- [ ] Each of the four modules that names a local hazard keeps that hazard and cites the central
      rule instead of restating the general clause.
- [ ] No module gains a copy-pasted general clause; the five silent modules inherit it.
- [ ] A test asserts the rule is in `ground-rules.md` and that no module `SKILL.md` states the
      general clause without citing it — structural, not wording-pinned (INV-219), and
      negative-controlled.
- [ ] `conformance.py size` shows the shipped word count has not risen as a result of this change.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

⚠️ **Not runtime-verifiable here.** Whether a guide actually honours the clause is INV-005–INV-009
territory, which only `dry-run` phase 3 can exercise. The criteria above are all static; the
behavioural half must be disclosed as untested until a dry run covers it.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the central statement.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md`, `module-03-system-verification/SKILL.md`, `module-03b-truthset-visualization/SKILL.md`, `module-05-data-quality-mapping/SKILL.md` — cite rather than restate; keep each local hazard.
- `tests/` — the new guard.

## Source

- Feedback: none — self-observed during the 2026-08-13 concision pass, by a near-duplicate scan over shipped passages (0.82–0.965 similarity), which is the band verbatim duplication detection cannot see (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium.** No bootcamper-facing text is wrong today, and nothing is broken; the risk is that five modules never state a rule the plugin relies on, and the four that do have already drifted into three phrasings. It is cheap to fix and gets cheaper the sooner it is done.
- MCP re-check: **n/a (no Senzing fact).** The clause concerns the guide's own interaction discipline; no Senzing claim is involved and no MCP tool was called for this finding.
- Upstream: not applicable.
- Related specs: `tool-directives-do-not-override-interaction` territory (INV-205 governs the *tool-returned* directive case, which is Module 5's local hazard and is **not** what this spec changes), `triage-the-twelve-uncited-hard-rules` (the same reverse-contract shape, resolved for hard rules).
