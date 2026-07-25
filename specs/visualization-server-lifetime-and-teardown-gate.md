# Keep the visualization server running until the bootcamper explicitly approves teardown

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two reports, one week apart, both about losing access to a running visualization.

**Report 1 (Module 7 and Truth Set visualization).** "In both the Truth Set visualization module and
this module, the bootcamp stops the live visualization server after the bootcamper finishes exploring,
requiring them to explicitly ask for a restart if they want to look again (which happened **twice** in
this session)." The server was stopped right after the assistant's own verification step
(screenshot/API checks) — before the bootcamper had a chance to explore at all. Their words: "a server
that's already running and working shouldn't be torn down and handed back as a restart request."

**Report 2 (Truth Set visualization).** The bootcamper reported the server being stopped before they
were done exploring, "on multiple occasions across sessions/modules." The module's cleanup step
justifies skipping a confirmation by reusing the earlier tour question — but that question is a
generic "done looking at the guided tour" check, not "okay to stop the server and purge the data now?"
A bootcamper can answer yes to the first without realizing it greenlights the second.

Stopping the server and purging the data are the two most irreversible actions in the module: the live
URL goes dead and the data must be reloaded to explore further.

## Root cause

Two different causes producing the same symptom, in two different modules.

**Truth Set visualization module — the cleanup step forbids the confirmation.**
`phase2-close.md:39-44`:

> ## Step 4: Cleanup
> Terminate the web service and purge the Truth Set data from the database.
> **No separate confirmation gate:** the bootcamper already confirmed they were done exploring at the
> end of Phase 1 (Step 2.5), so proceed directly to cleanup — do NOT re-ask (INV-006).

The gate it defers to is `phase1-visualization.md:291` — "👉 **Are you ready to continue?**" — which
follows the guided tour at `:260`. That question's meaning is "ready to move on in the module", not
"safe to tear down the live server and delete the loaded data". The skill conflates them and then
cites INV-006 (ask once) as the reason not to ask the second one.

**This is not an INV-006 conflict.** INV-006 forbids re-asking *the same* question; "are you done with
the tour?" and "may I stop the server and purge the data?" are different questions with different
consequences. The cleanup step's citation of INV-006 is a misapplication, and correcting it is what
unblocks the fix.

**Module 7 — the server has no specified lifetime at all.**
`phase1-query-visualize.md:200-224` directs the assistant to build the app, present it, write the
standalone snapshot, and capture screenshots for the recap (`:220-223`) — then goes straight to the
Checkpoint at `:226` and "Next: Discover phase" at `:232`. There is **no** statement of how long the
server should stay up, **no** bootcamper exploration gate, and **no** cleanup step (confirmed: no
terminate/stop/cleanup instruction exists anywhere in `skills/module-07-query-visualize-discover/`).
With the last concrete instruction being the assistant's own verification/screenshot pass, stopping the
server afterward is a natural reading — exactly the reported behavior.

## Proposed change

**Establish a server-lifetime contract shared by both modules:** a visualization server, once started,
stays up until the bootcamper has explicitly approved teardown. Agent-side verification (API probes,
screenshot capture) is a *preliminary* step that happens while the server keeps running — never the end
of the interaction.

1. **Module 7: add the missing lifetime and exploration steps** in `phase1-query-visualize.md`, after
   the snapshot/screenshot work at `:220-224`:
   - State explicitly that the server stays running and that screenshot capture must not stop it.
   - Hand the running URL to the bootcamper and let them explore at their own pace (mirroring
     `phase1-visualization.md:260`).
   - End on the teardown gate below before any cleanup.
2. **Truth Set visualization: replace the no-confirmation instruction** at `phase2-close.md:43-44` with
   an explicit gate, pinned verbatim per INV-056, immediately before Step 4 Cleanup:

   > 👉 **Ready for me to stop the visualization server and clean up the Truth Set data?**

   Amend the surrounding text to say *why* this is asked despite the earlier tour question: it is a
   different question about an irreversible action, so INV-006 does not apply. Removing the misapplied
   INV-006 citation is essential — otherwise the next reader restores the old behavior.
3. **On "no", keep it up.** Acknowledge, leave the server running, and wait for the bootcamper's
   go-ahead. Do not re-ask on a loop (INV-006 applies to *this* gate) — proceed when they signal
   they're done.
4. **Never require a restart request.** If the bootcamper asks to look again after teardown, restarting
   is fine — but the flow must not be designed such that a restart request is the normal path. Both
   reports describe the restart request as the symptom.
5. **State that the snapshot is not a substitute.** `phase1-visualization.md:266` already reassures the
   bootcamper they can revisit "any time, even after we stop the server" — true for the standalone
   snapshot, but the snapshot has no live `why`/`how`/`search`
   (`visualization-api-reference.md:337-339`). Make that limitation explicit at the teardown gate so
   the bootcamper's yes is informed.

Check while implementing whether the same gap exists wherever else a server or container is started —
`specs/docker-container-lifecycle-teardown-and-resume.md` established teardown handling for Docker, and
the two should read consistently.

## Acceptance criteria

- [ ] `phase2-close.md` presents a pinned, verbatim 👉 gate specifically naming stopping the server and
      purging the data, before Step 4 Cleanup; the "No separate confirmation gate … do NOT re-ask
      (INV-006)" instruction is gone.
- [ ] The replacement text explains that this is a distinct question about an irreversible action, so
      INV-006 is not violated by asking it.
- [ ] `phase1-query-visualize.md` states that the Module 7 server stays running through agent-side
      verification and screenshot capture, hands the URL to the bootcamper for self-paced exploration,
      and reaches the same teardown gate before any cleanup.
- [ ] A "no"/"not yet" answer leaves the server running and does not re-ask on a loop.
- [ ] The teardown gate states that the standalone snapshot preserves the tabs but not live
      `why`/`how`/`search`, so the bootcamper's consent is informed.
- [ ] Walking either module end to end never requires the bootcamper to ask for a restart in order to
      keep exploring.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): a
      flow/wording change; the server may be written in any language and the gate is independent of how
      the process is started or stopped.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase2-close.md` — Step 4 Cleanup
  (lines ~39-58): add the pinned teardown gate, remove the misapplied INV-006 justification
- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — Step
  2.5 (lines ~260-291): clarify that "Are you ready to continue?" does not authorize teardown; note the
  snapshot's live-feature limitation at line ~266
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  after the step-3c build (lines ~200-226): add the server-stays-running statement, the exploration
  hand-off, and the teardown gate

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_12.md` → "Visualization server is stopped after each
  module, requiring a manual restart" (2026-07-23, Query, Visualize and Discover; also observed in
  Truth Set visualization)
- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_13.md` → "Explicitly ask before stopping the Truth Set
  visualization web server" (2026-07-24, Truth Set visualization)
- Priority: Medium (reported twice, across two modules and two bootcamps)
- Related specs: `specs/docker-container-lifecycle-teardown-and-resume.md`,
  `specs/truthset-visualization-full-apparatus.md`, `specs/capture-visualization-screenshots-for-recap.md`
