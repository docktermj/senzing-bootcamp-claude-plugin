# The two MCP tools now agree on the evaluation license's duration, so the contested-fact note and its guard have outlived their reason — retire both

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin carries a note, a guard test and a scoped exemption, all built to handle a contradiction
between two MCP tools about how long the free Senzing evaluation license lasts. **That
contradiction no longer exists on server 1.33.0.** Both routes now say 10 days.

The plugin's own instruction for this moment is unambiguous.
`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:845-846`:

> Reported upstream as `category='bug'` on 2026-08-12 with the maintainer's approval; **retire this
> note outright — do not amend it — once the two tools agree.**

and `tests/test_eval_license_duration_is_unciteable.py`, in its module docstring:

> "Retire this guard, and the note in module 4, once the two tools agree — the 500-record
> no-license cap is a separate, stable, MCP-confirmed fact and is deliberately NOT covered here."

Both conditions are met. Left in place, the apparatus is worse than inert: it is a shipped,
dated, upstream-cited claim that the server contradicts itself, which the server no longer does —
and a guard that forbids stating a figure the server now states consistently. That is the class of
staleness this repo has already had to retract twice: a workaround outliving the defect it worked
around.

## Root cause

**Nothing re-asks.** The note, the guard and the exemption were each correct when written and each
pinned to a server version (1.32.9, 2026-08-12); the pin records *when* the claim was true and
schedules no re-check. Nothing in the offline suite can detect the retirement condition, because
the condition is a fact about a live server the suite never contacts — so the guard keeps passing
forever on a premise nobody re-tests.

**Both sides re-asked on server 1.33.0, 2026-08-21, in one session:**

- `get_capabilities` → `submit_feedback` tool entry: *"A **10-day**, 250K-record eval license is
  generated and emailed with a download link. One per email, re-requestable after 30 days."* The
  tool's own schema description repeats it: *"A 10-day, 250K-record license is generated and emailed
  with a download link."*
- `sdk_guide(topic='install', platform='macos_arm', language='java')` → `engine_config_notes`, the
  exact route that previously said 5 days, in the same sentence structure: *"(2) request a free
  **10-day** evaluation license (250K records) right now using submit_feedback with
  category='license_request'"*.
- Corroborated on a third route: `sdk_guide(topic='load', language='python', platform='linux_apt',
  record_count=1000)` → `engine_config_notes` carries the same *"free 10-day evaluation license
  (250K records)"* clause.

Three routes, one figure. The disagreement the note documents is resolved.

**Whether Senzing resolved it in response to the 2026-08-12 report is unknown and does not matter
here.** The submission was anonymous, so no reply was possible; the observable fact is that the
tools now agree.

## Three sites carry the workaround

1. `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md:838-846` — the contested-fact
   note: "⛔ **Never state the license's duration — the server contradicts itself about it, so no
   figure is citable.**", quoting both figures, the server version, the date, and the upstream
   report. Its final clause is the retirement instruction.

2. `tests/test_eval_license_duration_is_unciteable.py` — the guard. Two test classes:
   `NoShippedFileStatesTheDuration` (no shipped markdown states a license duration, with a
   `CONTESTED` exemption window for the note itself) and `TheOmissionIsRecordedAsADecision` (the
   note exists in module 4 and cites `1.32.9` / `2026-08-12`). The second class **pins the note's
   existence**, so the note cannot be removed without the guard failing — they retire together or
   not at all.

3. `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md:86-87` —
   a narrower, differently-reasoned caution: "⚠️ Do **not** state the evaluation license's size or
   duration from this file: those figures have changed before and two MCP tools have disagreed about
   them, so take them from a runtime lookup at the moment of use or say they are unavailable."

## Proposed change

1. **Remove the note, per its own instruction — do not amend it.** `SKILL.md:838-846` goes. What
   replaces it is nothing: with the tools in agreement, the license's terms are an ordinary
   runtime-sourced Senzing fact governed by INV-080 like every other, and no special apparatus is
   warranted.

2. **Delete the guard.** `test_eval_license_duration_is_unciteable.py` in full, both classes. Its
   `TheOmissionIsRecordedAsADecision` class asserts the note is present, so it must go in the same
   change as step 1.

3. **Keep `phaseB-load-first-source.md:86-87`, and re-verify its reasoning.** It is not the same
   claim. It says *take the figures from a runtime lookup rather than from this file*, which is
   INV-080 correctly applied and survives the resolution intact; its supporting clause ("two MCP
   tools have disagreed about them") is now historical and should be rephrased to the durable
   reason — these figures change, so read them at the moment of use. Do not delete the caution.

4. **Verify the retirement against the live server at implementation time, not from this spec
   (INV-080).** Re-ask all three routes above. If any still disagrees, **stop**: the note stays and
   this spec is closed as not-yet-applicable rather than partially applied. A half-retired
   contradiction — note gone, disagreement present — is strictly worse than today.

5. **Record what this cost, because the lesson is the reusable part.** A dated negative about a
   server that ships independently of this plugin needs a re-check trigger, not only a timestamp.
   The repo already has specs on this shape (`guards-pinning-a-dated-negative-outlive-it`,
   `module02-dated-negatives-about-sdk-guide-carry-no-marker`); this is the first case where the
   retirement condition was written down explicitly **and still needed a feedback triage run to
   notice it had been met.** Note in `IMPLEMENTED.md` how the condition was detected, so the next
   such guard is checked by something other than luck.

## Acceptance criteria

- [ ] All three routes re-asked live at implementation time and recorded as agreeing, with the
      server version and date; if any disagrees, no file changes.
- [ ] `module-04-data-collection/SKILL.md:838-846` is removed, not rewritten.
- [ ] `tests/test_eval_license_duration_is_unciteable.py` is deleted, and the full suite passes
      without it.
- [ ] `phaseB-load-first-source.md:86-87` still forbids stating the figures from that file, with its
      reason restated as "these figures change — read them at the moment of use" rather than as a
      tool disagreement.
- [ ] No shipped file asserts that two MCP tools disagree about the evaluation license's duration.
- [ ] The 500-record no-license cap and its `SENZ9000|LIMIT` citation are untouched — they were
      never part of this contradiction and remain MCP-confirmed on 1.33.0.
- [ ] `IMPLEMENTED.md` records how the retirement condition was detected.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — remove the contested-fact
  note (`:838-846`)
- `tests/test_eval_license_duration_is_unciteable.py` — delete
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — restate
  the caution's reason (`:86-87`); keep the caution
- `specs/IMPLEMENTED.md` — record the detection route

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Improvement: Assistant asserted the wrong
  built-in evaluation license capacity" (2026-08-18, Module Discover the Business Problem;
  `Source: self-observed (assistant retrospective)`). ⚠️ **The entry does not report this.** It was
  surfaced by re-verifying that entry's license facts against the current server (this skill's
  Step 5), which is where a plugin workaround for a defect the server has since fixed is supposed to
  be caught. The entry's own subject is specced separately as
  `module1-threshold-check-says-the-mcp-server-where-module2-names-the-route`.
- Priority: Medium — nothing is broken for a Bootcamper today; the cost is a shipped false claim
  about the server and a guard enforcing a silence that is no longer warranted.
- MCP re-check: server 1.33.0, 2026-08-21 — **fixed upstream**. `get_capabilities` (the
  `submit_feedback` entry and the tool's schema description),
  `sdk_guide(topic='install', platform='macos_arm', language='java')` and
  `sdk_guide(topic='load', language='python', platform='linux_apt', record_count=1000)` all state
  **10-day, 250K records**. The 5-day figure the note quotes from the `macos_arm` route is gone. No
  absence is asserted against the server.
- Upstream: already sent 2026-08-12 as `category='bug'` (per the note). No follow-up: the finding is
  resolved, submissions are anonymous, and there is no channel or need to confirm it.
- Related specs: `specs/mcp-tools-disagree-on-eval-license-duration.md` (the spec being retired —
  implemented 2026-08-12), `specs/guards-pinning-a-dated-negative-outlive-it.md`,
  `specs/module02-dated-negatives-about-sdk-guide-carry-no-marker.md`,
  `specs/refresh-reverified-provenance-stamps.md`

## Deviations from this spec, and why (2026-08-21)

**The note was not removed wholesale — the 500-record cap's citation was kept, as its own
statement.** Two of this spec's own instructions collide at the text level, and the collision is
only visible once you open the file. Change 1 says *"Remove the note, per its own instruction — do
not amend it"*; the acceptance criteria say *"The 500-record no-license cap and its
`SENZ9000|LIMIT` citation are untouched"*. But that citation lived **inside** the note's final
clause, and it was module-04's **only** MCP citation for the cap — while the same file discusses the
cap in prose three times (`:292`, `:913`, `:939-940`). Deleting the paragraph outright would
therefore have satisfied change 1 by breaking a criterion, leaving Step 8a reasoning about a
500-record limit with no cited source anywhere in the module.

What shipped: the duration contradiction is gone in full — no `5-day` figure, no "the server
contradicts itself", no "no figure is citable", no upstream-report reference — and the cap statement
remains as a short, plainly-worded citation re-confirmed this session on **server 1.33.0,
2026-08-21** via `sdk_guide(topic='load', language='python', platform='linux_apt',
record_count=1000)`.

**It is deliberately no longer a ⛔.** The old paragraph was a hard rule enforced by a guard; the
replacement is a citation plus a routing statement ("the evaluation license's own terms … come from a
runtime lookup at the moment of use (INV-080), not from this file"). Verified with
`conformance.py rules`, which stayed at its baseline of one uncited hard-rule section rather than
rising — the retirement removed a rule and added none.

**`phaseB-load-first-source.md:86-87` was restated, not deleted, as change 3 directed.** Its reason
changed from *"two MCP tools have disagreed about them"* — now historical — to *"those figures change
between releases"*, which is the durable reason and is INV-080 correctly applied.
