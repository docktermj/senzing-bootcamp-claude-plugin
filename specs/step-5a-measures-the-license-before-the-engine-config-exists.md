# SDK setup Step 5a measures the license before the engine config exists, and records the wrong limit

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`license_record_limit` is the field the INV-244 / INV-278 apparatus exists to make trustworthy. Its
whole authority rests on being **measured** rather than stated, defaulted or inferred — the plugin
says so repeatedly, and forbids writing it from anything but a reading.

Step 5a takes that reading at a point where it cannot see the Bootcamper's license, and writes the
wrong number. Because the number is genuinely measured, it passes every check the plugin has.

`module-02-sdk-setup/SKILL.md` Step 5 states the resolution order the reading depends on:

> **License check order:** project-local `licenses/g2.lic` → the `SENZING_LICENSE_FILE` path →
> system CONFIGPATH → the built-in evaluation license.

`CONFIGPATH` is a `PIPELINE` key in the engine configuration — and the engine configuration is
written by **Step 8**, three steps *after* the measurement. At Step 5a the settings string is
whatever exists beforehand, so the third tier is structurally unreachable and the reading falls
through to the built-in evaluation license.

**Measured live on 2026-08-31**, Ubuntu 24.04.4, SDK 4.4.0 (`SzProduct.get_version()`), on a machine
carrying a real license at `/etc/opt/senzing/g2.lic`:

| Settings passed to `SzProduct.get_license()` | `recordLimit` | `licenseType` | `expireDate` |
|---|---|---|---|
| What Step 5a actually has (`{"PIPELINE": {}}`) | **500** | `EVAL (Solely for non-productive use)` | *(none)* |
| What Step 8 later writes (`PIPELINE.CONFIGPATH=/etc/opt/senzing`) | **0** — no cap | `EVAL (Solely for non-productive use)` | `2027-03-12` |

Same machine, same SDK, same call, two steps apart in the module: **500 versus unlimited.**

### Why it propagates instead of self-correcting

Module 4's Step 8a re-measures — but **only when the field is absent or null**
(`module-04-data-collection/SKILL.md:98`). A present `500` takes the other branch
(`:93`):

> **Present and greater than 0** (custom license with a finite record cap): the effective limit is
> that value. Recommend sampling for license reasons only when the dataset total genuinely exceeds
> it.

So on the walk that found this — a generated scenario of **9,033 records** against a recorded limit
of **500** — Module 4 would recommend sampling down to 500, and Step 8a's License-Key gate would fire,
for a Bootcamper whose license has **no cap at all**. The field then feeds Module 6 and graduation
unchallenged.

The plugin already names this exact harm, one branch away, for the *absent* case:

> Treating that silence as "no custom license" is what steers a bootcamper whose license has **no
> cap** toward a smaller dataset, here, in the module where the sampling decision is actually made.

The same harm is reached by a **present but wrongly-measured** value, and nothing guards that path —
because presence is treated as proof that a measurement happened, which is precisely what INV-278
warns about from the other direction: *"Presence is not proof of detection, which is why the reading
comes first."* Here the reading did come first; it just came too early.

⚠️ **A measured-but-wrong value is worse than an absent one**, because absence triggers the
re-measure branch and presence suppresses it. Step 5a's contribution on this machine is strictly
negative: had it written nothing, Module 4 would have measured correctly.

## Root cause

Ordering. `module-02-sdk-setup/SKILL.md` places Step 5a immediately after Step 4's verification, and
its rationale for that placement is sound as far as it goes:

> This is the first step where the measurement is possible: Step 3 wrote the env script that supplies
> the settings and Step 4 has just verified the SDK works.

"Possible" is true — `SzProduct` needs no engine configuration, which the step correctly notes is why
its call succeeds while engine calls still raise `SENZ7426`. But *possible* is not *complete*: the
license resolution reads `CONFIGPATH` out of the settings, and the settings do not carry it until
Step 8. The step's own check order documents a tier that its own position makes unreachable.

The env script (Step 3) exports `SENZING_ENGINE_CONFIGURATION_JSON` from
`config/engine_config.json`, so on a fresh project that is whatever placeholder exists before Step 8
— on the scaffolded project used here, `{"PIPELINE": {}}`.

## Proposed change

Pick one of these; (1) is the smaller change and (2) is the more robust.

1. **Re-measure after Step 8.** Keep Step 5a where it is — an early reading is useful and its
   "cannot measure yet" branch is already correct — but add a required re-measure at the end of
   Step 8a (seed the default configuration), once `CONFIGPATH` is in force. Apply Step 5a's own
   sub-step 3 rules to the result: replace the recorded value when it disagrees, and **say the
   earlier figure was withdrawn, naming both numbers** — machinery that already exists and is
   currently unreachable, since nothing else writes the field in this module.

2. **Move the measurement to after Step 8**, leaving Step 5 to explain the license model and the
   check order without taking a reading. This removes the wrong-value window entirely rather than
   correcting it afterwards.

Either way:

3. **State the precondition at the point of the reading**: `SzProduct.get_license()` resolves the
   license from the settings it is given, so a reading taken with no `CONFIGPATH` can only ever
   return one of the first two tiers or the built-in default. A reading is only complete once the
   engine configuration is.

4. **Close the propagation path** in `module-04-data-collection/SKILL.md`: on the
   *present-and-greater-than-0* branch, the value is trustworthy only if it was taken with a
   configuration in force. Record alongside the figure **when** it was measured (a
   `license_record_limit_measured_at` step marker, or equivalent), and re-measure on the Module 4
   gate when the recorded reading predates the engine configuration.

## Acceptance criteria

- [ ] On a machine whose license is resolved via `CONFIGPATH`, the `license_record_limit` recorded by
      the end of SDK setup equals the value `SzProduct.get_license()` returns **with the engine
      configuration in force** — verified by taking both readings and comparing.
- [ ] When an early reading is later contradicted, the recorded figure is replaced and both numbers
      are stated to the Bootcamper, per Step 5a sub-step 3.
- [ ] Module 4's Step 8a does not treat a pre-configuration reading as authoritative — it either
      re-measures or is guaranteed a post-configuration value.
- [ ] Step 5's documented license check order contains no tier that the step's own position makes
      unreachable.
- [ ] A Bootcamper with an uncapped license (`recordLimit: 0`) is never steered toward sampling for
      license reasons, on any path.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 5/5a: the reading's
  precondition and the re-measure (or the move to after Step 8).
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the
  present-and-greater-than-0 branch: do not treat a pre-configuration reading as authoritative.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, SDK setup Step 5a
  (`Source: self-observed (assistant retrospective)`) — found by executing the step's own measurement
  procedure, then re-running the identical call with the configuration Step 8 will later write. No
  previous phase-3 walk had a Senzing install, so no previous walk could take either reading.
- Priority: **High** — it is the one field the plugin's license apparatus treats as authoritative
  *because* it is measured, and the failure is silent, self-consistent and propagates to the sampling
  decision, Module 6 and graduation.
- MCP re-check: server **1.35.1**, 2026-08-31 — `SzProduct.get_license()` confirmed as the reading
  route (`get_sdk_reference(topic='parameters', filter='getLicense')`); both readings above were taken
  against the installed SDK, not against documentation. The **engine-side** license-resolution
  behavior (which tier wins for a given settings string) is a property of the installed engine that
  no MCP route reports, so it is recorded as **observation-only** (INV-080/INV-149) with the SDK
  version it was measured against: **4.4.0**, build `2026_08_30__22_20`.
- Upstream: not applicable — the ordering is the plugin's.
- Related specs: `specs/step-1-says-skip-step-3-entirely-then-says-not-entirely.md`,
  `specs/prefer-the-package-manager-version-is-wrong-for-an-unmanaged-install.md` — same module, both
  found on the same install.
