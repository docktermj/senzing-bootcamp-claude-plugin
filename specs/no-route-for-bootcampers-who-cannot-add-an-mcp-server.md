# A bootcamper whose employer forbids adding an MCP server has no documented route into the bootcamp

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The whole bootcamp rests on the Senzing MCP server: INV-080 makes it the sole source of every
Senzing fact, and `ground-rules.md`'s MCP-first clause forbids answering from training data. The
plugin ships `.mcp.json` pointing at the public `https://mcp.senzing.com/mcp` endpoint and treats
reaching it as a given.

At commercial companies, adding a **new external MCP server** is frequently restricted by security
policy and sometimes prohibited outright. A bootcamper in that position cannot start — and the
plugin has nothing to say to them.

The onboarding MCP health check (`onboarding-flow.md` step 0b) covers **connectivity** —
internet reachability, proxy allowlisting. An organisational policy blocking the *addition of a
server* is a different blocker with a different remedy, and neither `onboarding-flow.md` nor
`ground-rules.md` addresses it. The failure mode is the worst kind: the bootcamper does everything
right, the health check tells them the server is unreachable, and the only advice available is to
fix a network problem they do not have.

**A route exists, and the server itself names it — the plugin just never mentions it.** Verified
2026-07-31 against server **1.32.3**, from the live tool descriptions this session:

- `sdk_guide`'s description distinguishes two transports: *"In HTTP mode the package `url` is hosted
  on this MCP server (mcp.senzing.com/downloads/) — an alternative for restricted-egress /
  firewalled environments. **In stdio mode** the package `url` is a local **`sz-mcp-coworker
  extract`** command that pulls the .deb from the binary's embedded bundle."*
- `get_sample_data`'s description names a second deployment shape: *"For full record access, call the
  MCP server endpoint directly (https://mcp.senzing.com/mcp) **or use the private deployment**."*
- `get_capabilities` records that the server *"hosts official Senzing SDK .deb packages at
  /downloads/ … eliminating the need to configure apt/yum repositories in firewalled environments"*.

So the server ships as a **local binary runnable over stdio**, and a **private deployment** is a
recognised configuration. Either would satisfy a policy that forbids adding an external endpoint
while permitting a locally-run tool — which is the common corporate shape.

**What could not be established.** `search_docs(query='self-hosted private MCP server deployment
stdio local install restricted network')` on the re-indexed corpus (**index_built 2026-07-31 20:21
UTC, 14,078 documents**) returned **no** documentation for obtaining or running either. The top hits
were Entity Specification relationship sections and a community SDK deployment guide — keyword
matches, not coverage. **The routes are named by the tooling and undocumented in the corpus.**

## Root cause

The plugin was built against the public endpoint and never modelled a bootcamper who is permitted to
run the bootcamp but not to add the server it depends on. Step 0b was written as a *connectivity*
check because connectivity is the failure the authors could reproduce; policy refusal produces the
same surface symptom (no server) from a cause no amount of proxy configuration fixes.

Nothing catches it: every test and every dry run has had the public endpoint available, so the
unreachable-by-policy path has never executed.

## Proposed change

1. **Split the health check's failure branch in two.** When the server is unreachable, distinguish
   *cannot connect* (network, proxy, allowlist — the existing advice) from *not permitted to add it*
   (policy). One added question at the point of failure separates them, and they need different
   answers.
2. **Give the policy branch a real route**, not an apology: name the two shapes the server itself
   documents — running `sz-mcp-coworker` locally in **stdio mode**, and the **private deployment** —
   and say plainly that the plugin cannot supply either, so the bootcamper should ask their Senzing
   contact or `support@senzing.com`. Cite the tool descriptions as the source with server version and
   date (INV-080).
3. **State the limit honestly.** The plugin must not imply it knows how to obtain or configure either
   route: `search_docs` does not document them as of the 2026-07-31 corpus. Saying "this exists, here
   is who to ask" is useful; inventing setup steps would be a fabricated Senzing fact.
4. **Do not offer to proceed without the server.** INV-080 is not negotiable and there is no offline
   mode — a bootcamp that answers Senzing questions from training data is worse than one that does
   not start. The honest outcome for a blocked bootcamper is a clear explanation and a named contact.

⚠️ **Do not present stdio mode as verified to satisfy any particular policy.** Whether a locally-run
binary is permitted is the bootcamper's organisation's decision, not a fact the plugin can assert.
Offer it as the route to ask about.

⚠️ **Do not write installation instructions for `sz-mcp-coworker`.** They are not in the indexed
corpus, so anything written would be from outside MCP — precisely what INV-080 forbids. Name the
binary, name who to ask.

## Acceptance criteria

- [ ] The onboarding MCP health-check failure path distinguishes a connectivity failure from a
      policy restriction, and asks the one question that separates them.
- [ ] The policy branch names **stdio mode** (`sz-mcp-coworker`) and the **private deployment**, each
      attributed to the tool description that documents it, with server version and date.
- [ ] The plugin states that neither route's setup is documented in the indexed corpus and directs
      the bootcamper to their Senzing contact or `support@senzing.com` — no invented setup steps.
- [ ] No path offers to continue the bootcamp without a reachable MCP server (INV-080).
- [ ] A test asserts the policy branch exists and names both routes, so it cannot be collapsed back
      into the connectivity advice.
- [ ] **Not runtime-verified, and disclosed:** neither stdio mode nor a private deployment was
      exercised — this environment reaches the public endpoint. The evidence is the server's own tool
      descriptions, which name the modes but not how to obtain them.
- [ ] **Re-verification clause:** implementing this requires re-reading the `sdk_guide`,
      `get_sample_data` and `get_capabilities` descriptions, and re-running the `search_docs` query.
      If the corpus has since gained self-hosting documentation, the spec's answer changes from
      "named but undocumented — ask" to "here is the documented route", which is a materially better
      outcome and must be taken.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — the step 0b health
  check's failure branch.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the MCP-first clause, which
  should point at the policy branch rather than assuming reachability.
- `tests/` — the policy-branch assertion.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Document a workaround for companies that
  restrict adding new MCP servers" (2026-07-27, Module: Entity Resolution Concepts; Priority: High;
  `Source: bootcamper-reported`).
- Priority: **High**, as filed. It is the only entry that can stop a bootcamper participating at all,
  and it targets exactly the commercial users the bootcamp exists to reach.
- MCP re-check: **server 1.32.3, docs index 2026-07-31 20:21 UTC, 2026-07-31 — the re-check changed
  the spec's answer.** The entry asked for "a workaround … e.g. pointing to a private/self-hosted
  deployment", framed as something the plugin authors would have to invent. The server's own tool
  descriptions already name both a stdio-mode local binary and a private deployment, so the spec
  proposes naming real routes rather than documenting an invented one. `search_docs` returned no
  coverage for obtaining either, so the honest half — "named but undocumented, ask your contact" — is
  also MCP-established. Tools called: `get_capabilities`, `sdk_guide`, `get_sample_data` (schema),
  `search_docs`.
- Upstream: **sent 2026-07-31 via `submit_feedback` (`category='feature'`, anonymous)**, with the
  maintainer's explicit approval — quoting both tool descriptions, naming the `search_docs` query and
  the corpus stamp that returned no coverage, and asking either for the documentation to be indexed
  or for the descriptions to say the routes are not self-service. `feature` rather than `bug`: the
  tools are not wrong, the corpus is incomplete. Anonymous, so no reply is possible. **This does not
  block the spec** — the plugin change stands either way, since naming the routes and directing the
  bootcamper to their Senzing contact is useful whether or not the corpus later documents them. If it
  does, the re-verification clause above requires taking the better answer.
- Related specs: none — no existing spec covers MCP reachability or the policy path.
