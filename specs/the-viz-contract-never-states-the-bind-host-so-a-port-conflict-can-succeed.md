# The visualization contract never states the bind host, so a port conflict can succeed silently

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`lsof -ti:8080` reported port 8080 busy — an unrelated `VizServer` from a different project, started
three weeks earlier, bound to `127.0.0.1:8080`. The bootcamp's own server **bound successfully
anyway**, to `*:8080`, because a loopback bind and a wildcard bind do not collide. Two processes
then listened on the same port and **either could answer a localhost request**. The first
`/api/stats` probe happened to reach the new server, which is the only reason it looked fine.

⛔ **Had the browser reached the other one**, the Bootcamper would have been shown a three-week-old
dataset — 100 records, 2 sources — under their own project's title, with nothing indicating anything
was wrong. Every number on the page would have been someone else's, and the keepsake screenshots
would have captured it.

The existing guidance treats a port conflict as a **bind failure**. This one is not a failure; it is
a success that produces nondeterministic results, which is strictly worse — a failure stops the
step, and this does not.

## Root cause

**The Python reference is already safe. The contract that binds every other language is silent.**

`plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1888`:

```python
httpd = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
```

An explicit loopback bind — which is precisely the remedy the entry proposes, already implemented.
A second loopback listener on the same port therefore **fails cleanly** for the bundled server, and
this defect is unreachable through it.

The Bootcamper was not running it. Module 7 step 3c has them build the results app in their own
language — here `src/server/VizServer.java`, ported from the Python reference — and
`module-03b-truthset-visualization/visualization-api-reference.md` is the contract that "binds a
server in **any** language (INV-090/INV-124)" (`:212`). **That contract never states the bind
host.** Searched for `127.0.0.1`, `localhost`, `loopback`, `wildcard` and bind-address language: the
file's only `bind` hits are the Python *binding* (`:134`) and unrelated uses of "binds" (`:212`,
`:609`, `:659`). Nothing requires a loopback bind, so a faithful Java implementation binding
`InetSocketAddress(port)` — the idiomatic default, and a wildcard bind — is **conformant** and
carries the defect.

This is exactly the boundary INV-002 draws and that INV-164 and INV-190 each had to record case by
case: *"a rule constraining what the Bootcamper's code must do MUST be stated as behavior in the
any-language contract, never only in a Python reference implementation. A rule that reaches
generated code solely through the reference violates this invariant even though the reference itself
is exempt."* The loopback bind is such a rule, and it currently reaches generated code only through
the reference.

⚠️ **A bind host alone does not close it.** Loopback binding makes a *colliding loopback* listener
fail cleanly, which is this report's case. It does not help when the pre-existing listener is itself
wildcard-bound — then the bootcamp's loopback bind is the one that succeeds alongside it. Only
verifying *which server answered* covers both directions, which is why the entry proposes both and
why both belong in the contract.

## Proposed change

1. **State the bind host in the contract as required behavior:** the server binds the loopback
   interface explicitly, never the wildcard address. Give the reason — a wildcard bind coexists with
   a loopback listener on the same port instead of failing — so an implementer does not "simplify"
   it back. This is also the correct security posture for a server holding the Bootcamper's resolved
   data, which is a second reason not to leave it to chance.
2. **Require a post-bind identity probe before the URL is handed over.** After binding, request
   `/api/stats` and confirm the responding server is the one just started — compare against a value
   the caller already knows, such as the loaded record count or a nonce minted at startup. A nonce
   is the stronger test: two runs of the *same* project would agree on record count.
3. **Say what to do when the probe disagrees:** stop and report the conflict with the port and both
   figures, rather than proceeding. ⛔ It must not degrade to a warning the Bootcamper scrolls past —
   the whole failure mode is that everything looks fine.
4. **Correct the port-conflict guidance from "bind fails" to "bind may succeed and still be
   wrong."** Wherever the module tells the guide how to handle a busy port, a successful bind is
   currently treated as proof the port was free. It is not.
5. **Implement both in the Python reference too.** It already binds loopback (step 1 is a no-op
   there, and the contract should say so rather than appear to demand a change); the identity probe
   is new for it as well, since a wildcard-bound foreign listener would defeat its loopback bind.

## Acceptance criteria

- [ ] The contract states the loopback-bind requirement with its reason, in the language-agnostic
      section that binds every implementation (INV-090/INV-124).
- [ ] The contract requires a post-bind identity probe and specifies what it compares.
- [ ] A disagreeing probe stops the step and reports the conflict; it does not proceed with a
      warning.
- [ ] Port-conflict guidance no longer treats a successful bind as proof the port was free.
- [ ] The Python reference performs the identity probe; its existing loopback bind is unchanged and
      a test pins it, so a future edit cannot widen it to the wildcard address.
- [ ] Negative-controlled: with a foreign listener occupying the port, the probe detects it — the
      test must construct the two-listener condition rather than asserting the happy path.
- [ ] ⚠️ Stated as behavior, not as a Python idiom, so a Java/C#/TypeScript implementation can
      satisfy it (INV-002) — the failure here was a conformant non-Python implementation.
- [ ] Holds on Linux, macOS, and Windows (per @INVARIANTS.md). ⚠️ The loopback/wildcard coexistence
      was observed on macOS; socket behavior differs across platforms, so the probe — not the bind
      rule — is what must be verified on each.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/visualization-api-reference.md`
  — the any-language contract: bind host and identity probe.
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py` — `:1888` (pin the existing loopback
  bind) and the startup path (add the probe).
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  step 3c's port-conflict guidance.
- `tests/` — the pinned bind host and a two-listener negative control.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "a busy port can still accept a wildcard bind, giving two servers on one port" (2026-08-17, Module Query, Visualize and Discover, step 3c; `Source: self-observed (assistant retrospective)`)
- Priority: **Medium**, and it is the kind of Medium that deserves a second look: the observed run was harmless, and the unobserved branch shows the Bootcamper a stranger's data under their own project's title with no signal. It is rated below the entries that misreport results on every run because it needs a stale listener on the same port to trigger.
- MCP re-check: **n/a (no Senzing fact).** The defect is in the plugin's own server contract and a socket-binding behavior of the host OS. No SDK, flag, response shape or Senzing server behavior is asserted, and no absence about the MCP server is relied on. Server **1.32.9** (`get_capabilities`, 2026-08-17) recorded for this run.
- Upstream: not applicable — routed `plugin` by the entry, and confirmed.
- Related specs: `specs/module-03b-hardcodes-the-port-its-own-text-says-may-differ.md` (the same port handling, from the other direction), `specs/visualization-server-lifetime-and-teardown-gate.md` and `specs/visualization-server-teardown-does-not-record-a-pid.md` (a stale bootcamp server is one way the conflicting listener arises — teardown that misses leaves exactly this), `specs/viz-server-settings-precedence-and-validation.md`, `specs/internal-connection-string-breaks-the-viz-server.md`, and INV-002, INV-090, INV-124.

## One narrowing of the feedback entry

The entry routes this to *"the visualization server's port handling"*, which reads as a defect in the
bundled server. It is not: `senzing_viz_server.py:1888` already binds `127.0.0.1` explicitly — the
entry's own alternative remedy, shipped. The defect is that the **contract** governing every
non-Python implementation never states it, so the Java port the Bootcamper actually ran was
conformant and unsafe. Recorded because an implementer reading the entry alone would go looking for
a bug in the Python server and find none, then conclude the report was mistaken.
