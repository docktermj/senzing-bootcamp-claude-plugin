# Effort above every recommendation triggers a step-down question every module

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The Claude Code CLI's `/effort` offers five levels — `low`, `medium`, `high`,
`xhigh`, `max`. The plugin's per-stage table recommends only `medium` or `high`.
So a Bootcamper who sets `xhigh` or `max` sits **above every recommendation in the
bootcamp**, and `ground-rules.md:605-610` then requires a step-down switch question
at every module start:

> ⛔ **When the recommendation sits *below* the current setting, say so in the
> question itself.**

Twelve stages, twelve step-down questions, each proposing a change the Bootcamper
has already deliberately rejected by setting the higher value. That is the
"pointless switch? every module" outcome `ground-rules.md:625-630` and INV-006 /
INV-012 exist to prevent — reached by following the rules correctly rather than by
breaking them.

## Root cause

Two clauses that are individually right and jointly wrong for values above the
table:

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:649-662` —
  the per-stage table's **Recommended** column contains only "medium effort" and
  "high effort". Nothing above `high` appears anywhere in the plugin.
- `ground-rules.md:605-610` — the step-down clause fires whenever the
  recommendation is below the current setting, with no floor and no
  already-above-the-table case.

The reason this has not been reported before is a third clause that is **more
wrong than it looks**:

- `ground-rules.md:564-569` — "the reasoning effort is exposed nowhere and
  typically cannot be read at all", which sends the effort dial to the
  previous-stage fallback almost always, which suppresses the comparison.

That premise fails in the exact situation the plugin creates. **On the Claude Code
CLI a `/effort` invocation prints the resulting level into the transcript**, so the
value becomes determinable the moment the Bootcamper uses it — and the plugin's own
switch flow (`:612-619`) instructs them to run precisely that command, then gates on
"👉 Are you done modifying the model and effort?". The plugin manufactures the
evidence and then tells the guide it does not exist.

Observed live on this walk, 2026-08-13: at the SDK setup module start the switch
question offered `/effort high`; the Bootcamper ran `/effort` (output: "Set effort
level to **xhigh**") and then declined the switch. From that point the effort dial
was determinable as `xhigh` — above every remaining recommendation in the table —
so the per-dial rule at `:561-577`, applied correctly, produces a step-down question
at Truth Set visualization and at every module after it.

## Proposed change

1. **Add an above-the-table case to the step-down clause.** When the current effort
   is *above* the highest value the table ever recommends, treat the recommendation
   as satisfied: say the stage's recommendation in one line, note that the
   Bootcamper is running higher and that this is fine, and **ask nothing**. A
   deliberate over-provision is not a mismatch to correct.
2. **Fix the determinability premise at `:564-569`.** Replace "exposed nowhere and
   typically cannot be read at all" with what is actually true: the value is not
   exposed by default, **but a `/effort` invocation in the Claude Code CLI prints
   it, and the switch flow asks the Bootcamper to run exactly that** — so once they
   have, the dial is determinable and the previous-stage fallback must not be used
   for it. This is the same failure the clause already warns about for the model
   dial at `:570-577`, and it applies to effort the moment the plugin's own flow has
   run.
3. **Say what the table's values mean.** State that `medium` and `high` are the
   recommended floor for value, not a ceiling — so a reader cannot conclude that
   `xhigh` is out of policy.
4. Consider whether the same above-the-table case is needed for the model dial. It
   is not today, because Opus 5 is the top row, but the shape will recur when a
   stronger model ships and the table lags it — which is the situation
   `docs/model-selection.md`'s dated verification note already anticipates.

## Acceptance criteria

- [ ] With effort at `xhigh` or `max`, no module start asks a step-down effort
      question; each states the recommendation and notes the higher setting is fine.
- [ ] With effort at `medium` entering a `high` stage, the switch question still
      fires as it does today.
- [ ] `ground-rules.md` no longer asserts that reasoning effort cannot be read; it
      states the `/effort`-in-transcript case and forbids the previous-stage
      fallback once the value is known.
- [ ] The table is described as a recommended floor, not a ceiling.
- [ ] `tests/test_model_guidance_sync.py` still passes, and the two tables stay in
      sync.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).
      The `/effort` command is CLI-specific; on Claude Desktop, the web app and IDE
      extensions the dial may still be undeterminable, so both paths must be kept.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the
  step-down clause, the determinability premise, and the table's framing.
- `plugins/senzing-bootcamp/docs/model-selection.md` — mirror any framing change,
  since it is derived from that table.

## Source

- Feedback: dry run phase 3, 2026-08-13 — the maintainer ran `/effort` at the SDK
  setup nudge and set `xhigh`, which made the dial determinable and above every
  remaining recommendation (`Source: self-observed (assistant retrospective)`)
- Priority: Medium — no path breaks, but it produces a question the plugin
  elsewhere forbids, at every module, for a Bootcamper who has actively chosen a
  stronger setting.
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: `specs/effort-only-switch-question-says-keep-your-current-model.md`
  (the other defect in the same pinned question, found on the same walk)

## Deviations from this spec, and why (2026-08-14)

- **⛔ The exemption narrows a recorded maintainer decision, and that is flagged rather
  than absorbed.** `plugins/senzing-bootcamp/docs/model-selection.md` records, from
  2026-07-26: "The pause is **symmetric**: downgrades ask exactly as upgrades do … Making a
  step down a statement instead of a question was considered … and rejected: the choice is
  the bootcamper's in both directions." Proposed change 1 makes a step down a statement for
  one case. It was implemented **confined to above the whole table** — the single case a
  bootcamper cannot resolve by answering, since no available setting stops the question
  short of downgrading — stated as such in both files with the 2026-07-26 decision cited
  beside it, and revertible by deleting one clause. Step downs *within* the table are
  unchanged. Implemented rather than held because the spec is unambiguous about the remedy;
  recorded here because narrowing someone else's decision is not the implementer's call to
  make silently.
- **The `/effort`-prints-its-level claim is shipped as a condition, not as an assertion.**
  The spec states that a `/effort` invocation prints the resulting level. That is a Claude
  Code CLI fact, not a Senzing one, so there is no MCP route to re-verify it, and this
  session could confirm only the five level names (from its own tool contracts) — not the
  output format. The plugin text therefore says the dial is determinable *once an `/effort`
  result is in this conversation*, which holds however the CLI words it, and the 2026-08-13
  observation is cited as the observation it is.
- **Proposed change 4 is answered in place rather than deferred.** The model dial needs no
  equivalent case today because Opus 5 is the table's top row; `ground-rules.md` now says
  exactly that, and says the exemption applies on the model side in the same terms if a
  stronger model ships and the table lags it. A test pins the answer, so the question is
  not re-derived later.
- **An existing guard corrected the first draft.** `tests/test_model_nudge_trigger_direction.py`
  rejected the sentence describing the observed defect, because it named the previous-stage
  comparison with no adjacent prohibition — a description of a wrong behaviour reads as a
  description of the behaviour. Reworded to state the ban explicitly.
