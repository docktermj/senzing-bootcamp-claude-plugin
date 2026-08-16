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
   internal reasoning — token budget, session length, context pressure, or a judgment that the
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

⚠️ **Not runtime-verifiable here.** Whether a guide actually honors the clause is INV-005–INV-009
territory, which only `dry-run` phase 3 can exercise. The criteria above are all static; the
behavioral half must be disclosed as untested until a dry run covers it.

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

## ⛔ NOT IMPLEMENTED — this spec's premise is false (2026-08-13, same day it was written)

**Do not implement it as written.** `implement-spec` Step 3.2 requires the root cause to be
confirmed in the code before anything changes, and it does not survive that check.

**The claim:** *"absent from `bootcamp-onboarding/ground-rules.md`"*, and therefore that
`module-00`, `module-01`, `module-04`, `module-06` and `module-07` *"never see the rule at all"*.

**What the code says.** `ground-rules.md:87-88`, under "Mandatory gates and step order", already
states it:

> Steps marked `⛔` are mandatory gates. NEVER skip a ⛔ gate or a numbered 👉 step - **no context
> or token-budget reasoning justifies it.** Advance exactly one step at a time.

And every one of the five "silent" modules loads `ground-rules.md` (2–3 references each), so all
of them inherit it. **Neither half of the problem statement is true.**

**How the error was made.** The finding came from grepping for `internal reasoning` and
`absolute precedence`. `ground-rules.md` phrases the same rule as *"no context or token-budget
reasoning justifies it"* — a fifth wording that matches neither probe. Absence was concluded from
two vocabulary misses, which is the same wrong-route reasoning **INV-194** exists to forbid, applied
to this repo's own prose instead of an MCP tool.

**What survives, much weaker.** The rule is stated in **five** places in **five** phrasings —
`ground-rules.md:87`, `module-02/SKILL.md:24`, `module-03-system-verification/SKILL.md:19`,
`module-03b-truthset-visualization/SKILL.md:19`, `module-05-data-quality-mapping/SKILL.md:19`. That
is drifted *restatement*, not a coverage gap, and **INV-183 explicitly sanctions restating a rule at
the step that needs it** — each module copy names a real local hazard (token budget, session length,
tool-returned directives). Whether four differently-worded copies of a rule that is also stated
centrally is a defect at all is a judgment call, and a much smaller one than this spec claims.

**Status: open, premise retracted.** Correcting the spec's body is `feedback-to-specs`' job, not
this skill's; this note is the permitted Step 3.6 append. A future run should re-scope or decline it
rather than implement it.

⚠️ **Process note.** This was the **fourth** wrong table produced from a hasty grep on 2026-08-13 —
and the only one to reach a spec. The other three (INV-149's staleness, INV-200's resolver, the
per-module precedence table itself) were caught by re-reading before they were written down. The
lesson this repo keeps re-teaching: a grep against this corpus is a lead, never a result, because
the same rule is deliberately phrased differently at each site it binds.
