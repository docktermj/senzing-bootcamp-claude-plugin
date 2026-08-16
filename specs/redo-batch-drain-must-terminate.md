# Drain the redo queue with a terminating loop, and warn that the MCP redo snippet does not terminate

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Module 6 requires draining the redo queue after loading. `sdk_guide(topic='redo', language='python')`
returns `redo_continuous_futures.py`, which **never terminates**: on an empty queue it prints
"pausing for 30 seconds" and loops indefinitely. That is correct for streaming ingest and wrong for
the bootcamp's batch load. Running it after a load hangs the session — the bootcamper sees a
prompt-less pause with no error, which is the worst shape a failure can take at this point in the
bootcamp because it is indistinguishable from slow work.

The topic's alternatives list offers `add_with_redo` and `redo_with_info_continuous`; neither is a
terminating drain either. The correct pattern was found instead in
`search_docs(category='anti_patterns')`, which additionally warns that `count_redo_records()` must
**not** be used as a loop sentinel: it is a full table scan per call, so polling it makes the drain
O(n²), compounded because processing a redo record generates more redo records. Observed in the
reported session: a backlog of 384 required **400** processed calls.

## Root cause

The plugin states the requirement and leaves the pattern to a tool that answers a different question.

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md:88-91` —
  "Use `generate_scaffold(language='<chosen_language>', workflow='redo', version='current')` for the
  redo processing pattern. The loading program (or a separate script) **should sequentially process
  all pending redos until the queue is empty**." The termination requirement is stated; nothing says
  what to do when the returned snippet does not honor it.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md:149-151` — the
  same instruction for the coordinated multi-source drain, with the same omission.
- `phaseB-load-first-source.md:94-96` then instructs a code comment explaining that "in production,
  redos are typically handled by an always-running redo processor that wakes, checks for pending
  redos, processes them, and sleeps when the queue is empty" — an accurate production note sitting
  immediately beside a batch step, describing exactly the behavior of the snippet that hangs it. The
  two patterns are adjacent and never distinguished.
- **The `count_redo_records` sentinel anti-pattern is absent from the plugin's guidance.** Grep finds
  it only in `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:268`, inside an
  example recap's narrative — a sample deliverable, not instructions anyone follows. No skill file
  mentions it.

**Upstream component (Senzing MCP server), partly.** `sdk_guide(topic='redo')` could add a batch
drain variant, or note in the topic response that the continuous pattern does not terminate and point
to the anti-patterns drain loop. Offered upstream and **declined** — so the plugin must warn, since
the bootcamp is where the mismatch bites.

## Proposed change

1. **Specify the drain as a terminating loop.** At both call sites, state the shape the batch step
   needs, language-agnostically (INV-002): fetch the next redo record; if none is returned, the queue
   is empty — exit the loop; otherwise process it and repeat. The **return value of the fetch is the
   sentinel**. Confirm the method names for the bootcamper's binding from MCP at implementation time
   (INV-080/INV-132) rather than carrying names from this spec.

2. **Warn that the returned snippet may not terminate.** Before running whatever `sdk_guide` /
   `generate_scaffold` returns for redo, check whether it loops on an empty queue — the observed
   `redo_continuous_futures.py` prints a pause message and continues. If it does, adapt it: replace
   the sleep-and-continue with a break, keeping the rest of the pattern (including its concurrency)
   intact. Say plainly that running the continuous form unmodified after a batch load hangs the
   session with no error.

3. **Record the counting anti-pattern in guidance, not only in the example recap.** Never poll a
   redo-count method as the loop condition: it is a full table scan per call, and because processing
   redo generates more redo the loop runs longer than the initial count suggests (384 → 400 in the
   observed run). Cite `search_docs(query='redo', category='anti_patterns')` as the source and
   re-confirm it at implementation time.

4. **Separate the production note from the batch step.** Keep the always-running-processor comment at
   `phaseB:94-96`, but label it explicitly as the *production streaming* pattern and contrast it with
   the *batch drain* the bootcamp runs — so the snippet's non-termination reads as a different
   use case rather than a defect the bootcamper should tolerate.

5. **Make the drain report its own completion.** State the terminal condition in output: the number
   of redo records processed and that the queue reached empty. A drain that finishes silently is
   indistinguishable from one that is still running.

## Acceptance criteria

- [ ] Both `phaseB-load-first-source.md` and `phaseC-multi-source.md` specify the drain as a loop
      whose sentinel is the fetch returning no record, and whose exit condition is an empty queue.
- [ ] Both warn that the MCP-returned redo snippet may be a continuous processor that does not
      terminate on an empty queue, and require checking for and adapting that before running it.
- [ ] Both state that a redo-count method MUST NOT be used as the loop sentinel, with the full-table-scan
      reason and the note that processing redo generates more redo.
- [ ] The production always-running-processor note is explicitly distinguished from the bootcamp's
      batch drain.
- [ ] A batch load followed by the drain completes and returns to the bootcamper, reporting the count
      processed and that the queue is empty — no indefinite pause.
- [ ] Method names and the anti-pattern are MCP-sourced at implementation time, not carried from this
      spec (INV-080).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): the loop
      shape is specified, not a Python snippet.

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseB-load-first-source.md` — step 9
  (`:83-99`): terminating-loop shape, the non-termination warning, the sentinel anti-pattern, and the
  production/batch distinction.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseC-multi-source.md` — step 20
  (`:147-160`): the same for the coordinated drain, added to its "Production redo patterns" list.
- `tests/` — a test asserting both redo steps carry the terminating-loop requirement and the
  count-sentinel prohibition.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "sdk_guide(topic='redo') returns a continuous
  daemon where the bootcamp needs a batch drain" (2026-07-26, Module Data processing;
  `Source: self-observed (assistant retrospective)`; `Routing: both`; `Upstream: offered, declined`)
- Priority: Medium
- Related specs: `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132 — confirming SDK
  shapes per binding), `specs/mcp-grounding-in-every-skill.md` (INV-080),
  `specs/production-volume-question-clarity-and-threading-cutover.md` (the other place a
  `sdk_guide` load-topic answer is adapted to the bootcamp's context)

## Invariants introduced

- `INV-151` — The redo drain MUST terminate, sentineled on the fetch returning no record, never on
  a redo-count method; an MCP-returned snippet MUST be checked for non-termination and adapted, and
  the drain MUST report its terminal condition (recorded in `specs/INVARIANTS.md`).
