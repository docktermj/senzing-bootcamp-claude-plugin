# Reconcile `sdk_guide`'s default-license warning against the license limit the bootcamp already detected

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`sdk_guide(topic='load', language='python', record_count=23152)` returned, in its
`compatibility_notes`:

```text
LICENSE REQUIRED: You have 23152 records, which exceeds the default Senzing license limit of 500.
The user must choose one of: 1) Request an evaluation license ... 3) Load only the first 500
records as a sample
```

The installed license reported `recordLimit: 0` — **no cap** — via `SzProduct.get_license()`. No
license action was required and the full 23,152 records were loadable.

The note reads as a hard blocker and prescribes three remedies, none of which applied. A bootcamper
acting on it would sample down to 500 records unnecessarily, or chase an evaluation license they
already have more capacity than. Both outcomes shrink the dataset that Modules 6 and 7 are built
around, and the smaller dataset then under-demonstrates cross-source resolution — the payoff the
bootcamp exists to show.

The note is generated from `record_count` alone; `sdk_guide` has no way to know the caller's licensed
capacity. The plugin does know it, and does not use it here.

## Root cause

The bootcamp detects and persists the real limit, and applies it to **its own** warnings but not to
MCP-sourced ones.

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:486-492` — Step 8a generates a
  scaffold calling `SzProduct.get_license()`, saves it to `config/license.json`, parses `recordLimit`
  (`0` = unlimited), and writes `license_record_limit` into `config/bootcamp_progress.json`.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md:44-55`
  already has exactly the right rule for the plugin's own message: read `license_record_limit` and
  "drive the decision from that effective limit, never a remembered or hardcoded figure" — omitting
  the capacity warning entirely when the limit is `0` or ≥ the dataset size.
- No equivalent rule exists for text the **MCP server** returns.
  `phaseA-build-loading.md:134-143` discusses the 500-record boundary only as `sdk_guide`'s
  *threaded-vs-single-threaded template selector*, and correctly requires re-confirming it from MCP.
  It never mentions that the same call also emits a licensing verdict derived from the same number,
  or that this verdict is unconditional.
- The result is asymmetric: INV-080 makes MCP output authoritative for Senzing facts, and nothing
  distinguishes a **general fact** (what the default license permits) from a **claim about this
  environment's state** (what *your* license permits) — which the bootcamp has already measured.

**Upstream component (Senzing MCP server), not fixable in this repository.** The note should be
phrased conditionally ("if you are on the default evaluation license …") or omitted when the caller
has not stated their licensed capacity. Offered upstream and **declined**, so the plugin-side
reconciliation below is the durable fix.

## Proposed change

1. **State the reconciliation rule where the call is made.** In `phaseA-build-loading.md`, beside the
   existing note that `record_count` selects the template, add: the same call also returns a
   licensing note computed from the record count alone. Before relaying or acting on it, read
   `license_record_limit` from `config/bootcamp_progress.json` and apply the effective-limit rule
   already written at `phaseB-load-first-source.md:44-55`:
   - **`0` (no cap), or ≥ the dataset size** — the note does not apply. Suppress it; do not mention
     sampling or evaluation licenses. Use the returned code and ignore the licensing prose.
   - **Positive and below the dataset size** — the note applies. The single License Key gate
     (Module 4, Step 8a) has already offered to expand capacity; restate the choice, do not force
     downsizing.
   - **Absent or null** — no custom license was detected, so the default-limit note is the correct
     assumption. Relay it.

2. **Generalize it once, in the ground rules.** MCP output is authoritative for Senzing facts
   (INV-080); a note about the *installed environment* derived from a parameter the caller supplied
   is a conditional, not a fact about this system. Where the bootcamp holds a measured value for the
   same thing — a detected license limit, a detected SDK version, a detected platform — the measured
   value governs, and the divergence is recorded rather than silently resolved. This is not a licence
   to answer from training data: both sides here are MCP-sourced, one generically and one by
   measurement of the bootcamper's machine.

3. **Never surface a suppressed note as a bootcamper-facing warning.** A licensing warning that does
   not apply is noise the bootcamper cannot evaluate (INV-012). Suppress it; if the divergence is
   worth keeping, record it in the checkpoint, not in the conversation.

## Acceptance criteria

- [ ] `phaseA-build-loading.md` states that `sdk_guide(topic='load', record_count=…)` returns a
      licensing note derived from the record count alone, and requires reconciling it against
      `license_record_limit` before relaying or acting on it.
- [ ] With `license_record_limit` = `0`, a dataset of any size produces no sampling prompt, no
      evaluation-license prompt, and no licensing warning in bootcamper-facing output.
- [ ] With `license_record_limit` positive and below the dataset size, the bootcamper is told the
      cap applies and is offered the choice, never forced to downsize.
- [ ] With `license_record_limit` absent or null, the default-limit note is relayed unchanged.
- [ ] The ground rules state that a measured environment value governs over generic guidance about
      the same value, and that the divergence is recorded — without weakening INV-080's ban on
      answering from training data.
- [ ] A suppressed licensing note produces no bootcamper-facing output (INV-012).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the
      detected limit comes from the chosen language's `get_license` equivalent, already established
      in Module 4 Step 8a.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — `:134-143`,
  the `record_count` discussion: add the licensing-note reconciliation beside the template-selection
  note.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the measured-value-governs
  rule, scoped so it cannot be read as relaxing INV-080.
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — Step 8b (`:500-560`): make
  the persisted limit the input to any capacity framing raised at collection time.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sdk_guide load guidance asserts the 500-record
  default license limit regardless of the installed license" (2026-07-26, Module Data collection;
  `Source: self-observed (assistant retrospective)`; `Routing: mcp-server`;
  `Upstream: offered, declined`)
- Priority: Medium
- Related specs: `specs/single-license-gate-at-data-processing.md` (the one licence gate this
  defers to), `specs/module2-license-clarity.md`, `specs/license-request-option.md`,
  `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/production-volume-question-clarity-and-threading-cutover.md` (the other consumer of
  `record_count`)
