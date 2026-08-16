# `minimal` verbosity is undefined where it meets structured output

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The verbosity system defines `minimal` as a statement about *explanatory* output:

> **minimal** is near-zero explanatory output (all five categories at 0) for experts who want to
> move fast; it reduces only explanatory output and NEVER suppresses required output — 👉 questions,
> gates, module banners, end-of-module summaries, and the recap always appear.
> — `bootcamp-onboarding/ground-rules.md:443-446`

That binary — explanatory vs required — is enough for prose. It is **not** enough for output with a
prescribed *shape*, and there are two such sites where a guide under `minimal` has no rule to
follow. Both were reached in the dry-run seeded walk (2026-08-13), and both were resolved by
improvisation.

### Instance 1 — the onboarding overview: 2 of 10 bullets carry guidance

`bootcamp-onboarding/onboarding-flow.md` step 3 gives a **ten-bullet** overview. Exactly two bullets
are marked verbosity-aware: the plugin version line (`:101-102`, "when it is `minimal`, suppress this
line") and the feedback-trigger bullet (`:143-144`, "under `minimal`, suppress it; under `concise`,
one line"). The remaining eight — the guided-discovery framing, the goal, the recap PDF, the module
list, the Truth Set caveat, licensing, the unfamiliar-terms offer, and the how-long-it-takes
paragraph — carry no verbosity treatment at all.

They are plainly explanatory, so `minimal` should reduce them, but nothing says by how much, and
they are not uniform: the module list is arguably orientation the bootcamper needs, while the
guided-discovery framing is pure encouragement. Under `minimal` one guide will print all eight
verbatim (they are not marked for suppression), another will cut to a single sentence. Both are
defensible readings of the same file.

### Instance 2 — the setup recap: a one-line budget against a per-line annotation rule

`bootcamp-preparation/SKILL.md` step 7 gives a **six-line** recap template (`:375-384`) and then two
instructions that collide under `minimal`:

- `:368-369` — "Respect the active verbosity preset — shorten under `concise`, and keep it to **a
  single line** under `minimal`."
- `:371-373` — "⛔ **State every honored value once in the Step 7 recap**, marked as coming from the
  saved file … Append ` — from your saved preferences` to **any line** whose question Step 0
  suppressed."

The provenance marker is defined **per line**, and the ⛔ makes stating every honored value
mandatory. Under `minimal` there is only one line to hang three markers on — and the collision is
guaranteed precisely in the case the marker exists for: a returning bootcamper who has pre-seeded
`path`, `verbosity` and `programming_language`, which is the seeded fixture and the documented
INV-133 scenario. The two instructions are jointly satisfiable only by collapsing the six lines into
one and attaching the markers inline, which is what the walk did. Nothing in the file says to do
that, and a guide that honours the ⛔ literally will emit three or four lines under a one-line budget.

Neither instance is a broken path, and no bootcamper-facing output was wrong in the walk. The defect
is divergence: the same preset, the same fixture, two guides, visibly different output — in the one
place a returning bootcamper is meant to *check what is in force and correct it*.

## Root cause

`minimal` is specified as a filter over content *kinds* (five categories, each 0–3) but both sites
constrain output *form* — a fixed template, and a per-line annotation. The category model has no
vocabulary for "collapse this structure while preserving these required elements", so where form and
filter meet, the file falls silent.

INV-011/INV-012 govern what is suppressed and what is not narrated; INV-096 gives the time estimate
its per-preset treatment and is cited at `:143-144` as the pattern to copy. That pattern was copied
to exactly two bullets and one recap line, and not generalized — so the gap is an incomplete
application of an existing convention rather than a missing idea.

## Proposed change

Do **not** add a new verbosity mechanism. Extend the existing one to cover form:

1. **State the collapse rule once**, in `ground-rules.md`'s Verbosity section, alongside the
   explanatory/required split: where output has a prescribed multi-line shape and the active preset
   budgets fewer lines, the **required elements are preserved and merged onto the permitted lines**,
   separated by `;` — never dropped to fit the budget. Any per-line annotation (such as the
   saved-preferences marker) attaches inline to the value it qualifies rather than to a line.
2. **`onboarding-flow.md` step 3** — give the eight unmarked bullets a per-preset treatment, in one
   sentence covering the group rather than eight separate notes: under `minimal`, reduce the overview
   to the module list plus the resume-and-time sentence; under `concise`, drop the guided-discovery
   and unfamiliar-terms bullets; otherwise show all ten. This keeps orientation and discards
   encouragement, which is the distinction the bullets actually differ on.
3. **`bootcamp-preparation/SKILL.md` step 7** — state that under `minimal` the six template lines
   collapse to one `;`-separated line with every honored value still marked inline, and show the
   collapsed form once so it is not re-derived. Note that the module-name list compresses to a count
   under `minimal` (the names were just given in the preface), and that a count is not a module
   number so INV-079 is unaffected.

## Acceptance criteria

- [ ] `ground-rules.md`'s Verbosity section states the collapse rule for prescribed-shape output:
      required elements merge onto the permitted lines rather than being dropped, and per-line
      annotations attach inline.
- [ ] `onboarding-flow.md` step 3 gives every overview bullet a verbosity treatment — no bullet is
      left with none — expressed as a group rule, not eight notes.
- [ ] `bootcamp-preparation/SKILL.md` step 7 shows the `minimal` collapsed recap form explicitly,
      carrying all three provenance markers inline, and states the module-list-to-count compression.
- [ ] Under `minimal` with all three preferences seeded, the Step 7 recap is one line **and** names
      every honored value as saved — the two instructions no longer conflict.
- [ ] A repo-level stdlib-only test asserts step 3 leaves no overview bullet without a verbosity
      treatment, and that step 7 contains a worked `minimal` example carrying the saved-preferences
      marker.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the collapse rule.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — step 3's overview.
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — step 7's recap under `minimal`.
- `tests/test_minimal_verbosity_scope.py` — new guard.

## Source

- Feedback: none — dry run phase 3 (2026-08-13), the `--seeded` walk, which is the only configuration
  that reaches both instances: `verbosity: minimal` must already be present for the preface
  suppression path to run at all, and all three preferences must be seeded for the recap collision to
  occur. `Source: self-observed (assistant retrospective)`
- Priority: Low — nothing bootcamper-facing was wrong in the walk, and the guide resolves both by
  analogy with the marked cases. Worth fixing because the divergence lands on the setup-choices recap,
  whose stated purpose (INV-099/INV-133) is to let a returning bootcamper see what is in force and
  correct it — the one output where an inconsistent shape costs something real.
- MCP re-check: n/a (no Senzing fact) — entirely interaction-layer and presentation.
- Upstream: not applicable.
- Related specs: `specs/pattern-gallery-asks-for-more-than-mcp-can-supply.md` and
  `specs/reassurance-must-precede-its-pinned-question.md` — the same dry-run's other
  under-specification findings. Distinct root causes (a source-coverage shortfall, and an ordering
  contradiction), so they are filed separately rather than merged here.
