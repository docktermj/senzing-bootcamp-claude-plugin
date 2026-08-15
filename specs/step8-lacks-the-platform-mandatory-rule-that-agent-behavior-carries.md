# Step 8 lacks the `platform`-is-mandatory rule that Agent Behavior carries

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-02-sdk-setup/SKILL.md` states the engine-configuration rule **twice**, 269 lines apart,
and the two statements are not the same. The half that only exists in the summary is the half
that tells the guide what goes wrong.

**Step 8 — where the artifact is actually produced** (`:1104-1252`, 149 lines):

> **🚨 NEVER guess the engine-configuration VALUES.** `CONFIGPATH`, `RESOURCEPATH`, `SUPPORTPATH`
> and the connection-string form all come from
> `sdk_guide(topic='configure', platform='<user_platform>', language='<chosen_language>', version='current')`
> — never from directory patterns or memory (INV-080).

**`## Agent Behavior` — a summary list at the end of the file** (`:1381-1391`):

> - **NEVER guess engine configuration values:** … ⛔ **`platform` is not optional here.** Omitting
>   it returns the config-bootstrap *code* only, with no `engine_config` block at all — verified on
>   server 1.32.9, 2026-08-13: `topic='configure', language='python'` returned
>   `init_default_config.py` and nothing else, while adding `platform='linux_apt'` returned
>   `environment.engine_config` carrying CONFIGPATH, RESOURCEPATH and SUPPORTPATH.

Step 8 shows `platform=` inside the call and says **nothing** about omitting it. Probing its full
149-line span for `not optional`, `Omitting`, `omit` and `decision tree` returns **absent** for all
four; only the literal `platform=` is present.

⚠️ **The asymmetry looks deliberate in one direction and accidental in the other.** The Agent
Behavior bullet explicitly defers the `engine_config` brace-doubling detail downward — *"(Step 8
states both corrections it needs, and its failure modes)"* — so the author was pairing the two
sites consciously. The ⛔ platform rule travelled the opposite way and no pointer was left behind.

## Root cause

**A rule governing an artifact lives only in a general behaviour summary, not at the step that
produces the artifact — which is INV-183 exactly:**

> A step that instructs the guide to generate a bootcamper-facing artifact MUST, **at that step**,
> name every rule governing how the artifact is produced — or cite the file that states it — and
> MUST NOT rely on a rule stated only elsewhere. The step is the only text the guide is certainly
> reading when it authors the artifact.

Step 8 generates the engine configuration document that gets written into the bootcamper's
project. `platform`'s optionality is a rule governing how that document is produced. It is stated
only 269 lines later, under a heading (`## Agent Behavior`) a guide executing Step 8 has no reason
to have read.

**Why the omission bites rather than being cosmetic.** Re-verified against the live schema this
session (server **1.32.9**, 2026-08-15): `sdk_guide`'s `platform` parameter is declared
`"default": null` with the description *"Target platform. Omit to get the platform decision
tree."* So omitting it is a **legal call that succeeds** and returns something structurally
different — no `engine_config`, no `environment.default_paths`. Step 8's very next instruction is:

> **Build the JSON from `environment.default_paths`, not from the `engine_config` blob.** That
> response carries both.

Against a platform-less response that sentence is false — the response carries neither — and Step 8
offers no diagnosis, because the diagnosis is in `## Agent Behavior`.

## What re-verification changed about this finding

**One difference between the two sites is NOT a defect, and I would have filed it as one.** Step 8
passes `version='current'` and the Agent Behavior bullet does not. The live schema declares
`version` with `"default": "current"`, so Step 8 is passing the default explicitly — redundant,
legal, and no breach of INV-136 (which forbids *undeclared* parameters, not redundant declared
ones). Both call forms are correct. **Only the missing ⛔ rule is the finding.**

## Proposed change

1. **State the `platform`-is-mandatory rule at Step 8**, where the call is made — the ⛔ sentence,
   what a platform-less response returns instead, and the dated server evidence. This is the
   INV-183 fix and it removes nothing.
2. **Leave the Agent Behavior bullet in place.** Repetition required *at* a step is INV-183, not
   redundancy; the summary is a legitimate second surface. Add a back-pointer to Step 8 so the
   pairing is symmetric, mirroring the one the bullet already carries in the other direction.
3. ⛔ **Do not "reconcile" the two call signatures by stripping `version='current'`.** Both are
   valid against the current schema (above). A cosmetic edit here would look like a fix and change
   nothing.

## Acceptance criteria

- [ ] Step 8 states that `platform` is not optional, and what a platform-less response returns
      instead, with its server version and date.
- [ ] Step 8's `environment.default_paths` instruction is no longer the first thing a guide meets
      after a possibly-platform-less call without a diagnosis available at that step.
- [ ] The Agent Behavior bullet still states the rule and now points to Step 8, symmetric with its
      existing "(Step 8 states both corrections it needs…)" pointer.
- [ ] A test asserts the ⛔ rule is present **within the Step 8 span** — derived by locating the
      heading and its following `## `, not by a hardcoded line number (INV-246) — **negative-
      controlled**, mutation verified to land, then reverted.
- [ ] ⛔ Not runtime-verified: whether a guide actually passes `platform` is a live-turn property.
      The guard asserts the rule is reachable at the step, never that the call is made correctly.
      `dry-run` phase 1 exercises the call itself.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — `:1106-1111` (Step 8, add the
  rule); `:1387-1391` (Agent Behavior, add the back-pointer).
- `tests/` — one new or extended guard asserting the rule sits inside the Step 8 span.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15i
  (`Source: self-observed (assistant retrospective)`). Found by Step 6's drifted-repetition probe:
  scanning shipped Markdown for rule-bearing lines that are 82–99% similar across sites surfaced
  six pairs, of which four are legitimate phase-header differences and one is punctuation-only.
- Priority: **Medium.** The failure is loud rather than silent — a platform-less response visibly
  lacks the block Step 8 asks for — but the explanation sits 269 lines away, so a guide that hits
  it at Step 8 has no local diagnosis and the bootcamper waits while it is rediscovered.
- MCP re-check: **Server 1.32.9, 2026-08-15 — one fact re-verified, and it CHANGED the finding.**
  `sdk_guide`'s live parameter schema declares `platform` as `"default": null` ("Omit to get the
  platform decision tree"), confirming a platform-less call is legal and returns a different shape
  — which is what makes the missing rule bite. The same schema declares `version` with
  `"default": "current"`, which **removed** the second half of the finding I was about to file:
  Step 8's redundant `version='current'` is legal, not an INV-136 breach.
- Upstream: not applicable — not a Senzing MCP server defect. The server behaves as documented;
  the plugin states it in the wrong place.
- Related specs: `sdk-guide-configure-unseeded-datastore`,
  `engine-config-returned-by-sdk-guide-is-not-valid-json` (the other half of this step's contract,
  which correctly lives *at* Step 8), `module02-dated-negatives-about-sdk-guide-carry-no-marker`,
  and INV-080, INV-136, INV-183, INV-246.
