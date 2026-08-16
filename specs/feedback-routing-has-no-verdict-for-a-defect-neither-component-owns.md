# Feedback routing has no verdict for a defect neither component owns

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The feedback flow's routing taxonomy (`feedback.md:86-98`) recognizes four verdicts — `plugin`,
`mcp-server`, `both`, `unclear` — and is built on a **two-component world model**: the bootcamp
plugin, and the Senzing MCP server. A defect owned by the **Claude Code harness** fits none of
them, and the discriminating test routes it to the wrong one.

The test as shipped:

> - *Would this still happen if the bootcamp plugin were perfect?* If yes → **MCP server**.
> - *Would this still happen if the Senzing MCP server were perfect?* If yes → **plugin**.
> - Yes to both → **both** (the plugin repeated or failed to guard an upstream defect).
> - Neither answer is clear → **unclear**.

A harness defect answers **yes to both** — it survives a perfect plugin *and* a perfect server —
so the stated rule yields `both`, whose own definition is "the plugin repeated or failed to guard
an **upstream** defect". There is no upstream Senzing defect. The rule produces an affirmatively
false verdict.

**This is not hypothetical: it misfired twice on 2026-08-15**, and both entries said so in prose,
in the field, in the `Routing:` field itself:

> `unclear` — the plugin's skills/hooks contain no reference to "auto-mode"; it appears to
> originate from the surrounding Claude Code CLI harness … so the responsible component **cannot be
> pinned to either of the two options this template distinguishes**.
> — `feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK_1786803006.md:18`

> `unclear` — this is a Claude Code host/harness-level UI nudge …, **not something either the
> bootcamp plugin or the Senzing MCP server generates or controls**, so it cannot be attributed to
> (or fixed via) either component's channel.
> — `feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK_1786814552.md:18`

Both fell back to `unclear` and then wrote a sentence explaining that the option set was
inadequate. That is the plugin reporting its own enumeration as incomplete, twice, in writing.

⚠️ **`unclear` is the wrong record, not merely an imprecise one.** Its shipped definition is *"The
symptom is real but the component **cannot be identified** from the evidence"* (`feedback.md:98`).
Here the component **was** identified, with certainty, by both reporters. Filing it as `unclear`
records the opposite of what is known, and it makes a genuinely ambiguous entry indistinguishable
from a confidently harness-attributed one.

## Root cause

**The taxonomy predates any case that was neither component's**, and three things kept it that way:

1. **The definition site** — `feedback.md:86-98`. Two questions, four rows, no third component.
2. **A guard that pins the closed set without an invariant behind it** —
   `tests/test_feedback_routing.py:42` hardcodes `VERDICTS = ("plugin", "mcp-server", "both",
   "unclear")`, and its module docstring frames the whole subject as *"Feedback is triaged
   **plugin-vs-MCP-server**"* (`:1`). The guard therefore certifies the two-component model rather
   than testing it.
3. ⛔ **No invariant registers the taxonomy at all.** `unclear` appears **zero** times in
   `specs/INVARIANTS.md`. A four-member closed list governs whether bootcamper content is offered
   for transmission off the machine, is enforced by a test, and is bound by no rule — so nothing
   noticed that the list was incomplete, and `conformance.py rules` cannot see it because the
   enclosing section legitimately cites INV-015 and INV-065 for its *other* claims.

**The upstream consequence is the sharp end, and the current mapping gets it right by accident.**
`submit_feedback` reaches **Senzing**. A harness defect sent there misroutes a report to a party
that does not own it. Today `unclear` skips the offer (`feedback.md:169`, `:234`, `:257`), so
nothing wrong is sent — but that is a property of the fallback the reporters happened to choose,
not of the taxonomy. Under the discriminating test as written the verdict is `both`, and `both`
**does** trigger the upstream offer.

## What the analysis changed about the finding's shape

**The first instinct — sharpen `unclear`'s definition — is the weaker fix.** It would make the
record honest but would still collapse "nobody can tell" and "the harness owns this, definitely"
into one bucket, which is precisely the distinction the maintainer's triage needed and had to
re-derive from prose on both entries. A fifth verdict costs one table row and makes the
upstream-suppression rule *derivable* rather than incidental.

## Proposed change

1. **Add a fifth verdict, `host`**, for a defect owned by the Claude Code harness — the interface
   itself, which neither the bootcamp nor Senzing ships. Vocabulary matches what
   `ground-rules.md` already uses ("host control", "host-rendered", "host-level").
2. **Fix the discriminating test** so the third component is asked about *first*, since it is the
   cheapest question and its "yes" short-circuits the other two:

   > - *Would this still happen with a perfect plugin **and** a perfect Senzing MCP server?* If
   >   yes → **host** (the Claude interface owns it; neither component can fix it).
   > - *Would this still happen if the bootcamp plugin were perfect?* If yes → **MCP server**. …

3. **Add the table row**, with the two observed instances as its field examples.
4. ⛔ **Suppress the upstream offer for `host`, and say why** — `submit_feedback` reaches Senzing,
   which does not own the harness, so forwarding misroutes the report. Update `feedback.md:169`,
   `:234` and `:257` so `host` joins `plugin`/`unclear` on the local-only side.
5. **Sweep every site that states the verdict set (INV-246)** — `feedback.md:121` (entry
   template), `graduation/SKILL.md:320` (the retrospective's copy), and the maintainer-side
   `.claude/skills/feedback-to-specs/SKILL.md:192`, which knows only **two** verdicts and so
   disagrees with the flow that feeds it.
6. **Register the taxonomy as an invariant** — the closed verdict set, and the rule that only
   `mcp-server`/`both` may be offered upstream. Draft for the maintainer's sign-off.
7. **Widen the guard** to derive its expectations rather than restate them, and fix the docstring's
   "plugin-vs-MCP-server" framing.

## Acceptance criteria

- [ ] A `host` verdict exists, is defined, and its definition names the Claude interface as the
      owner that neither the bootcamp nor Senzing ships.
- [ ] The discriminating test routes a harness defect to `host`, and no longer yields `both` for
      it — verified by walking the test's own questions against both 2026-08-15 entries.
- [ ] `host` never triggers the upstream offer, and the reason is stated where the rule is (a
      report to Senzing about the Claude harness misroutes it).
- [ ] Every site stating the verdict set carries all five — derived by scanning, not by a
      hardcoded path list (INV-246), with a membership floor.
- [ ] `graduation/SKILL.md`'s retrospective copy and the maintainer-side triage skill agree with
      `feedback.md`; no surface states a different verdict set.
- [ ] An invariant records the closed verdict set and the upstream-eligibility rule, worded and
      **approved by the maintainer**, with its index entry in the same edit.
- [ ] The guard fails when a site omits a verdict or when an ineligible verdict is made
      upstream-eligible — **negative-controlled**, mutation verified to land, then reverted.
- [ ] ⛔ Not runtime-verified by any test: whether a guide *applies* the test correctly to a live
      report. That is a conversational property (`dry-run` phase 3). The guard asserts the text.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/feedback.md` — `:86-98` the test and table;
  `:121` the entry template; `:169`, `:234`, `:257` the upstream gating; `:42` the file header.
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — `:320`, the retrospective's verdict list.
- `.claude/skills/feedback-to-specs/SKILL.md` — `:192`, the maintainer-side verdict set.
- `tests/test_feedback_routing.py` — `:42` and the module docstring.
- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry.

## Source

- Feedback: none directly — `production-readiness-audit` 2026-08-15f
  (`Source: self-observed (assistant retrospective)`). The **evidence** is two bootcamper-reported
  entries whose `Routing:` fields each state the option set was inadequate:
  `feedback/SENZING_BOOTCAMP_PLUGIN_FEEDBACK_1786803006.md` and
  `…_1786814552.md` (both 2026-08-15, Module General; `Source: bootcamper-reported`).
- Priority: **Medium.** No bootcamper is harmed today — the fallback both reporters chose happens
  to suppress the upstream offer — but the taxonomy's own rule yields `both` for this class, and
  `both` sends. The record is also affirmatively wrong, and the maintainer re-derived the
  attribution from prose twice in one day.
- MCP re-check: **n/a (no Senzing fact).** The finding is internal consistency between the
  plugin's routing taxonomy, its guard, its ruleset and its maintainer-side counterpart. No
  Senzing claim is asserted and no absence about the server is relied on. Server **1.32.9**
  established this session (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — and that is the finding's own subject. `submit_feedback` reaches
  Senzing, which does not own the Claude Code harness; there is no upstream channel for this
  class, which is exactly why it needs a verdict that suppresses the offer by rule.
- Related specs: `host-rendered-control-prompt-interrupts-a-pending-question` (the second entry
  and the same root event), `a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper`
  (the first), `guards-enforce-class-scoped-rules-from-hardcoded-site-sets` (the INV-246 pattern
  this guard repeats), and INV-015, INV-065, INV-246.

## Invariants introduced

- `INV-248` — The feedback triage taxonomy is the closed set `plugin`, `mcp-server`, `both`,
  `host`, `unclear`, and every shipped site stating that set MUST state all five (recorded in
  `specs/INVARIANTS.md`, indexed under *Feedback capture*).
- `INV-249` — Only `mcp-server` and `both` MAY be offered upstream; `plugin`, `host` and
  `unclear` stay local, and the shipped rule MUST state why `host` cannot be forwarded
  (recorded in `specs/INVARIANTS.md`, indexed under *Feedback capture*).

## Deviations from this spec, and why (2026-08-15)

- **Two invariants, not the "one new invariant" this spec's `## Affected files` predicted.**
  `INVARIANTS.md` rule 4 requires one testable condition per ID, and the spec's own criterion
  names two conditions — the closed verdict set, and upstream eligibility. Splitting them follows
  the INV-243 → INV-245 and INV-234 → INV-240 precedent.
- ⚠️ **Maintainer sign-off on the wording was STANDING, not per-invariant.** `implement-spec`
  Step 5 requires the maintainer to approve each invariant's wording before it is recorded. They
  were away for this run and granted advance authority to record invariants and list each for
  review on return. **Both IDs are therefore recorded on standing authority and are flagged for
  wording review** — the conditions they state are what this spec and the audit established, but
  the phrasing has not had the usual sign-off.
- **A pre-existing assertion had to change, and it was the right kind of failure.**
  `test_offer_is_gated_on_the_verdict` pinned the exact sentence *"For `plugin` or `unclear`, skip
  this step entirely"*, so widening the skip clause reddened it — the guard doing its job. It was
  rewritten to derive the non-eligible verdicts from `UPSTREAM_ELIGIBLE` rather than pin a
  sentence, so a sixth verdict cannot pass by leaving a literal untouched.
- **A mutation escaped negative-control and the assertion was strengthened.**
  `test_host_is_defined_as_owned_by_the_claude_interface` first checked that "`host`" and "Claude
  interface" appeared *anywhere* in the triage step — but both also appear in the discriminating
  question above the table, so **deleting the entire `host` table row still passed**. Re-anchored
  to the table row itself, and extended to require the row to say neither component ships it.
  All five mutations then landed and reverted cleanly.
- **`tests/test_invariant_enforcer_citations.py` needed `EXPECTED_PAIRS` 60 → 62**, because both
  new invariants name their enforcing test and that file counts invariant→test pairs deliberately
  rather than dynamically. The same file's bidirectional check then required the guard's docstring
  to cite INV-248/INV-249 back, which it now does.
- **`.claude/skills/feedback-to-specs/SKILL.md` was edited although it never ships.** It is the
  maintainer-side counterpart that consumes these entries and it knew only *two* verdicts, so
  leaving it would have preserved the disagreement this spec exists to remove. `propagate.sh` does
  not mirror `.claude/`, so nothing reaches the public repo.
- **No Senzing fact required re-verification.** `get_capabilities` was called this session to date
  the run (server **1.32.9**, 2026-08-15), confirming this spec's `MCP re-check: n/a`. The one
  Senzing-adjacent claim — that `submit_feedback` reaches Senzing and not the Claude Code harness —
  is read directly from the tool's own description in this session's MCP manifest, not from
  training data or a prior spec.
- ⛔ **Not runtime-verified, exactly as the spec's own criterion states.** Whether a guide applies
  the discriminating test correctly to a live report is a conversational property; the guard
  asserts the text says the right thing, never that a triage decision follows it. `dry-run`
  phase 3 is owed.
