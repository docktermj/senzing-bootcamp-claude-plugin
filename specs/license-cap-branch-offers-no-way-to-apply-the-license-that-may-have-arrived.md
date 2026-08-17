# The license-cap branch restates a choice the Bootcamper cannot act on

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

At the moment the evaluation cap first bites — Data processing, Phase B step 7, immediately before
the full load — a Bootcamper with a 7,718-record dataset and a measured `recordLimit: 500` was given
three ways to spend the budget:

1. build an overlap-preserving 500-record subset and load that now (recommended)
2. wait until the evaluation license is applied, then load all 7,718
3. load the first 500 records as they come

Option 2 names an outcome and supplies no way to reach it: no file location, no configuration key,
no verification step. Nothing in the turn mentioned that the free evaluation license they had
**already requested** in Data collection (Step 8a) is delivered by email and may already have
arrived. The recommended path is therefore a workaround for a constraint the Bootcamper may already
have the means to remove — and Modules 6 and 7 need the full dataset to demonstrate the
cross-source resolution the whole bootcamp builds toward.

⚠️ **The three options are not in the plugin.** `phaseB-load-first-source.md` contains **no pinned
👉 question at all**, and no file in the plugin contains this question or the word "budget" in this
sense. The branch says only:

> restate that a larger license lets the full load proceed, as a choice, not a wall; do not force
> downsizing. (`phaseB-load-first-source.md:63-65`)

So the guide **improvised** a three-option question from an instruction to present a choice. What
the Bootcamper meets here varies run to run, and the one option that would dissolve the constraint
is the one an improvising guide is least likely to invent — because the procedure for it lives two
modules away.

## Root cause

**The apply procedure exists, is designed for exactly this moment, and is unreachable from it.**

`module-04-data-collection/SKILL.md` Step 8a sub-step 5 (`:734-744`) is a complete, cross-platform
apply procedure: decode the Base64 key or copy the `.lic` to `licenses/g2.lic`, add
`LICENSEFILE` to the engine-config PIPELINE section, record `license: custom`, then continue to
sub-step 7 to re-detect the limit. Sub-step 6 (`:752-755`) even anticipates this exact case:

> The bootcamp **continues on the built-in evaluation license** meanwhile, so the bootcamper is
> never blocked waiting for the email; the emailed Base64 key can be decoded and applied via
> sub-step 5 whenever it arrives, **even in a later session**.

Nothing ever invokes it. `phaseB-load-first-source.md:61-77` reads `license_record_limit` and
branches on the number, and its cap branch neither names sub-step 5 nor links to it. This is the
INV-183 shape — a procedure that governs a decision is not reachable at the step where the decision
is made — with the aggravation that the plugin *wrote down* the later-session case and then never
built the path back to it.

⛔ **The marker that would trigger the reminder cannot carry it.** The obvious fix — "if
`license: evaluation`, say a license may have arrived" — is wrong as written. `license: evaluation`
is recorded in **three** places in Step 8a, and they do not mean the same thing:

| Site | Meaning |
|---|---|
| `:755` | a request was sent through some channel, or the Bootcamper will obtain one elsewhere |
| `:811` | *"Send only on an explicit yes. On anything else, record `license: evaluation`"* — the Bootcamper **declined** to request one |

So the value means "no custom key is applied", and a reminder keyed to it would tell a Bootcamper
who deliberately declined to go and check their inbox for a license they never asked for. **The
request is not recorded as an event anywhere** — not its channel, not its date. Verified by search:
`license: evaluation` is written at `:755`, `:811` and read back only at `:861`, inside Module 4
itself. No file in `module-06-data-processing/` or `module-07-query-visualize-discover/` reads the
`license` preference at all.

**What the live server says, and it independently names the missing option.** On
**MCP server 1.32.9, 2026-08-16**, `sdk_guide(topic='load', language='python', record_count=1000)`
returns `compatibility_notes` listing exactly three remedies for a dataset over the limit:

> 1. Request an evaluation license — email `sales@senzing.com` … 2. **Provide a license they
> already have — place the license file at the path specified by `SENZING_LICENSE_FILE` or in the
> `etc/` directory** 3. Load only the first 500 records as a sample

The plugin's branch offers versions of 1 and 3 and omits 2 — the one the Bootcamper in this report
was closest to being able to use.

⚠️ **Two different apply mechanisms, and the spec must not conflate them.** The server names the
`SENZING_LICENSE_FILE` environment variable or the `etc/` directory. The plugin's Step 8a wires
`LICENSEFILE` inside the engine-config PIPELINE section. Both are real; the plugin's own procedure
is the one already tested in this bootcamp's file layout, so **reuse Step 8a, do not introduce a
third mechanism** from the server's wording.

## What this must NOT become

⛔ **INV-093 forbids a second License Key prompt.** It requires the prompt be presented *"at most
once across the bootcamp, at the start of Data collection (Module 4) … and every other module reads
the persisted result rather than re-asking"*. Adding "4. I have the license, help me apply it" as a
new **gate** in Module 6 would breach INV-093 and INV-006 directly.

The distinction that makes the fix admissible: the *decision* — do you have a key, do you want to
request one — was correctly asked once and is settled. What is missing is a **procedure** and a
**status readout**, which are not a gate. The turn must remain the single question the branch
already needs (INV-251), not become two.

## Proposed change

1. **Record the request as an event, not as the absence of a key.** In Step 8a sub-step 6, when a
   request is actually sent, persist a distinct marker — channel and date — separate from
   `license: evaluation`. Without it no later step can tell "waiting on an email" from "declined",
   and every downstream reminder is a guess.
2. **Make Phase B's cap branch read that marker** and, only when a request is outstanding, state
   plainly that the license is delivered by email, may already have arrived, and can be applied now.
3. **Carry the apply route at the branch** as a pointer to Step 8a sub-step 5 — not a copy
   (INV-183 is satisfied by reachability, and a second copy of a platform-specific procedure is a
   drift hazard). Name the verification: re-read `SzProduct.getLicense()`, parse `recordLimit`,
   confirm it moved, and re-enter the three branches with the new value, which the branch structure
   at `:61-77` already supports.
4. **Give the branch a pinned question** (INV-056), so what the Bootcamper meets is not improvised.
   It replaces the improvised one rather than adding to it, and it is one 👉 ending the turn.
5. ⚠️ **State the expected magnitude only from a runtime lookup, never from this file.** The eval
   license's size and duration have changed before and two MCP tools have disagreed about them
   (`specs/mcp-tools-disagree-on-eval-license-duration.md`); `submit_feedback`'s own description on
   1.32.9 advertises a 10-day, 250K-record license, which would remove the cap for this dataset
   entirely — but that figure belongs in a runtime call at the moment of use, not baked into the step.

## Acceptance criteria

- [ ] Step 8a persists a request-sent marker distinct from `license: evaluation`, carrying the
      channel and the date, written only on an actual send.
- [ ] A Bootcamper who **declined** to request a license gets **no** "check your email" reminder —
      negative-controlled, since this is the failure the obvious implementation introduces.
- [ ] Phase B's cap branch reads that marker and, when a request is outstanding, states that the
      license arrives by email and may already have landed.
- [ ] The branch points at Module 4 Step 8a sub-step 5 for the apply procedure and does **not**
      restate it; a test asserts the platform-specific commands appear in exactly one place.
- [ ] After applying, the step re-measures via `SzProduct.getLicense()` → `recordLimit` and
      re-enters the three branches with the measured value.
- [ ] The branch ends on **one** pinned 👉 question (INV-056, INV-251), and **no new License Key
      gate is introduced** — a test asserts Module 6 never asks the Module 4 question (INV-093).
- [ ] No capacity or duration figure for the evaluation license is hardcoded in any shipped file.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      apply procedure is already dual-platform at Step 8a and the reminder is prose.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — sub-step 6 (`:746-755`) and
  the decline path (`:811`): record the request as an event.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` —
  the cap branch (`:63-65`), which gains the readout, the pointer and a pinned question.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — check
  whether its mirror of this branch needs the same treatment (`:61-77`'s note says Phase A carries
  the same three branches).
- `tests/` — guards for the decline case, the single-copy procedure, and the no-second-gate rule.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Licence-budget question gives no path to applying a Senzing licence" (2026-08-16, Module Data processing; `Source: bootcamper-reported`)
- Priority: **Medium.** Nothing is broken and no data is lost, but the Bootcamper is steered into a 500-record workaround at the one moment the full dataset becomes reachable, and the modules that follow are the ones the reduced dataset degrades.
- MCP re-check: **server 1.32.9, 2026-08-16 — still reproduces, and the server names the missing option.** `sdk_guide(topic='load', language='python', record_count=1000)` returns `compatibility_notes` whose remedy 2 is *"Provide a license they already have — place the license file at the path specified by `SENZING_LICENSE_FILE` or in the `etc/` directory"*. `sdk_guide(topic='configure', language='python')` returns no license key or variable of any kind, re-confirming the `MCP-NEGATIVE` marker the plugin already records at `module-02-sdk-setup/SKILL.md:851`. owner-checked: `sdk_guide(topic='load', record_count=<above the limit>)` — that is the route the plugin's own marker names as the sole owner of the license-variable fact, and it returned it verbatim today.
- Upstream: not applicable — routed `plugin`. The server's guidance is correct and complete; the plugin does not carry it to the step that needs it.
- Related specs: `specs/single-license-gate-at-data-processing.md` (established **INV-093**, the at-most-once rule this fix must not breach), `specs/inv244-absent-license-branch-exists-in-module-4-too.md` (the same three-branch structure), `specs/license-limit-assumed-when-it-could-be-measured.md` and `specs/load-time-warning-ignores-the-license-cap-decided-one-step-earlier.md` (the measure-then-decide discipline), `specs/no-license-path-environment-variable.md` (why the variable name is handled carefully), `specs/mcp-tools-disagree-on-eval-license-duration.md` (why no capacity figure is written down), `specs/overlap-preserving-sampling-at-the-license-gate.md` (the recommended option this one competes with).

## One correction to the feedback entry

The entry concludes that *"Module 4 Step 8a owns the request path; nothing owns the apply path, so it
falls in the gap between the two modules."* **The apply path is owned** — Step 8a sub-step 5
(`:734-744`) is a complete cross-platform procedure, and sub-step 6 explicitly contemplates applying
an emailed key in a later session. The defect is narrower and more fixable than the entry states:
the procedure exists and is simply not reachable from the step where the constraint is felt.
Recorded so implementation extends the pointer rather than writing a second apply procedure.
