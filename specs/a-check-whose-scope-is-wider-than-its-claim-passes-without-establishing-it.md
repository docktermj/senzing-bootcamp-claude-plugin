# Two checks pass without establishing what they claim, both by scoping too wide

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two independent checks are satisfied by something *near* what they are checking rather than by
the thing itself. Same root shape, two mechanisms:

**(a) The line-scoped citation check is satisfied by an adjacent, unrelated invariant ID.**
`visualization-api-reference.md:938-939` states a hard rule with **no governing citation**:

> a capture that proceeds without it MUST say so (INV-129). ⛔ **A deadline is not a settle
> guarantee, and a longer one is not a better guarantee.**

The `INV-129` belongs to the clause *before* the stop sign — and INV-129 is about verifying a
**rendered artifact rather than an exit status**, which has nothing to do with deadlines versus
settle signals. The rule's actual governors are **INV-298** (the settled signal) and **INV-299**
(the capture-oriented render). `tests/test_new_hard_rules_are_cited_or_deferred` passes anyway,
because it asks whether the **line** carries an `INV-nnn` — and this one does, for a different
rule.

⚠️ **This is the INV-124 class arriving through the checker rather than through an author.** The
2026-09-02 audit found INV-124 cited as authority for a rule it does not govern; `citations.py
verify` was blind because the ID resolved. Here the ID both resolves *and* satisfies the
line-level check, while governing the sentence next door. A reader who follows it lands on
artifact verification and learns nothing about why a deadline is insufficient.

**(b) A guard searches the whole file where it means to check one block.**
`tests/test_capture_render_is_settled_and_fitted.py::test_the_layout_is_driven_synchronously`
asserts the synchronous tick loop appears **anywhere** in `senzing_viz_server.py`. Moving that
loop out of the `if(capture){…}` branch — where it is the only thing that makes a capture settle
— leaves the assertion green. Its sibling
`test_the_finished_layout_is_fitted` had exactly this defect and was corrected during
implementation after its negative control failed to fire; the same correction was not applied to
its neighbor.

## Root cause

A check's **scope** is wider than the claim it is written to establish, so proximity substitutes
for governance:

- `conformance.py`/`test_new_hard_rules_are_cited_or_deferred` scope citations to the **line**.
  A line can hold two rules, or a rule plus another rule's citation — and Markdown reflow decides
  where lines break, so which citation lands on which line is partly incidental.
- The guard in (b) scopes its search to the **file** where the property is about a **branch**.

Neither check is wrong about its own question; both answer a wider question than the one that
matters and report success for it.

## Proposed change

1. **Cite INV-298/INV-299 at the deadline rule** in `visualization-api-reference.md:939`, and
   sweep the file's other stop signs for the same pattern — a ⛔ whose only nearby `INV-nnn`
   belongs to a different sentence. ⛔ **Do not move the INV-129 citation:** it correctly governs
   the "MUST say so" clause, and INV-129 is what makes that clause a rule rather than a
   preference.
2. **Narrow the guard in (b)** to the `if(capture){…}` block, exactly as its sibling now does, and
   re-run the negative control to confirm it fires.
3. **Consider whether the line-level citation check can ask a narrower question** — for example,
   requiring the citation to appear *within* the stop sign's own bolded span rather than anywhere
   on the line. ⚠️ This is the part worth thinking about rather than implementing quickly: a
   stricter rule would flag a large number of existing, legitimately-cited rules whose ID sits
   just outside the bold, and the report has to stay short enough to read. Measure the hit count
   before changing the check.
4. ⛔ **Do not weaken either check to make this go away.** Both directions are findings: a rule
   with no governing citation, and a guard that certifies a definition or a file-wide match. The
   remedy is a narrower question, never a quieter one.

## Acceptance criteria

- [ ] `visualization-api-reference.md`'s deadline rule cites INV-298/INV-299 at its own stop sign.
- [ ] No stop sign in that file has, as its only nearby citation, an ID belonging to a different
      sentence — checked by reading every ⛔ in the file, not only the one found here.
- [ ] `test_the_layout_is_driven_synchronously` asserts the loop is inside the capture branch, and
      its negative control (move the loop out of the branch) makes it fail.
- [ ] A decision is recorded on (3) — either a narrower check with its measured hit count, or a
      note saying why the line remains the unit.
- [ ] Negative control for (a): remove the INV-298/INV-299 citation and confirm something fails.
      ⚠️ If nothing fails, that is itself the finding — say so rather than adding an assertion that
      only pins this one line.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md` — the uncited rule
- `tests/test_capture_render_is_settled_and_fitted.py` — the file-wide search
- `.claude/skills/production-readiness-audit/conformance.py`, `tests/test_new_hard_rules_are_cited_or_deferred.py` — only if (3) changes the question

## Source

- Feedback: `/production-readiness-audit`, 2026-09-03 (`Source: self-observed (assistant retrospective)`)
- Priority: **Medium** — nothing stated is false and no behavior is affected, but a rule whose citation does not govern it is one a later editor cannot look up, and a guard satisfied by a file-wide match certifies what it never tested. Both were produced today, by me, in the change that registered the invariants they should have cited.
- MCP re-check: **n/a (no Senzing fact).** Both halves are internal: which of the plugin's own invariants governs one of its own rules, and the scope of one of its own guards. No Senzing claim is asserted or re-asserted (INV-080).
- Upstream: not applicable.
- Related specs: `specs/inv-124-is-cited-as-the-any-language-rule-it-is-not.md` (the same class, found by the previous audit, where the ID resolved but did not govern)

## Deviations from this spec, and why (2026-09-03)

⛔ **Half of this spec is RETRACTED. Finding (a) was a false positive, and the spec is its own
best example of the thing it describes — a check whose scope was wider than its claim.**

### (a) is withdrawn: the rule IS governed, and by the invariant it restates

The deadline rule at `visualization-api-reference.md:938` is inside a bullet whose **head** reads:

> `- **An animated view MUST expose a settled signal, and the capture MUST wait on it (required —
>   INV-002/INV-090/INV-298).**`

And **INV-298's own registered text contains the same rule, near-verbatim**: *"⛔ A time budget is
not a settle guarantee, and a bigger one is not a better guarantee."* So the shipped ⛔ is a
restatement of the invariant cited four lines above it, in its own bullet. The `INV-129` mid-bullet
governs its own clause correctly. **Nothing is mis-cited and nothing needs a new citation.**

The audit's claim — that the line-level checker was "satisfied by an adjacent unrelated ID" — was
produced by a scanner that read the **line** instead of the **bullet**. The same scanner, run
across the corpus, reported 10 hits of the shape; the **two examined closely were both correctly
cited in their own paragraph**:

- `:938` — cited at its bullet head (INV-298), as above.
- `:838` — `⛔ **Whatever you implement, cover the quotes.**` is cited at `:845`, seven lines later
  in the same paragraph: *"which is why it is a ⛔ and not a nicety **(INV-106)**."*

So criteria 1, 2 and 5 are **void**, not met — there is no defect at either site, and adding a
citation to "fix" one would have been a change made to satisfy a wrong finding.

### The decision on (3), now measured properly — the line stays the unit

Proposed change 3 asked whether the citation check could ask a narrower question, and to measure
before changing it. Three measurements, in order of how much each moved the answer:

| question | corpus-wide hits | verdict |
|---|---|---|
| citation not inside the ⛔'s bolded span | **~537 of 632** | unusable — most rules cite at the bullet head |
| …and the line's only citation precedes the ⛔ | **10** | affordable, but **poor precision** — 2 of 2 examined were correct |
| citation anywhere on the line (**today's check**) | gate, currently clean | kept |

⛔ **Rules are routinely and correctly cited at the head of the bullet they govern**, which is
above the line the stop sign lands on, and Markdown reflow decides where lines break. So a
stricter *line*-level rule flags correct prose, and the honest unit is the **enclosing bullet** —
which is more than a regex should attempt. The existing line-level gate is a cheap approximation
that is satisfied here for the right reason once the bullet is read. **Neither a stricter gate nor
a report in that form is worth adding**, and no scanner was left behind: one that reports 10 hits
with at best middling precision would train its reader to skip it, which is the failure the
`coverage_reports.py` preamble already warns about.

### (b) is real and is fixed

`test_the_layout_is_driven_synchronously` searched the whole of `senzing_viz_server.py` for the
synchronous tick loop. It is now scoped to the `if(capture){…}` branch, and the negative control
fires: moving the loop out of the branch fails it. ⚠️ Its sibling
`test_the_finished_layout_is_fitted` had the identical defect, was caught during implementation
when *its* negative control failed to fire, and the correction was not carried across — which is
the actual, narrow lesson here: **when a negative control catches a scope defect in one assertion,
check its siblings in the same class before moving on.**

## Invariants introduced

None. (b) is a test-scope correction, and (a) is withdrawn.
