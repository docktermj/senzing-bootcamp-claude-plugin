# Two MCP tools give different evaluation-license durations (10-day vs 5-day) — upstream

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two tools on the **same** MCP server, queried in the **same session**, state different durations for
the free Senzing evaluation licence. Both read from **server 1.32.9, 2026-08-12**:

**`submit_feedback` (tool description, via `get_capabilities` and the loaded tool schema):**

> **To get an eval license** — set category to 'license_request' … A **10-day**, 250K-record eval
> license is generated and emailed with a download link. One per email, re-requestable after 30 days.

**`sdk_guide(topic='install', platform='linux_apt', language='python', version='current')`** — the
same sentence appears twice in that response, in `install.gotchas` and again in
`engine_config_notes`:

> If no license is available, offer three options: (1) continue with just 500 of their records as a
> sample, (2) request a free **5-day** evaluation license (250K records) right now using
> submit_feedback with category='license_request', or (3) request a license at
> https://senzing.com/request-non-prod-license/.

The record cap agrees (250K). The **duration does not**: 10 days versus 5 days. `sdk_guide` is
directing the reader to `submit_feedback`, so the two are describing the identical action — one tool
tells you to call the other, and they disagree about what it gives you.

**The plugin is not currently wrong, and that is the whole reason this is filed as it is.** Checked
2026-08-12: no shipped file states *any* eval-licence duration — `grep` for `10-day`, `10 day`,
`5-day`, `5 day`, `250K`, `250,000` across `plugins/` returns nothing. What the plugin does carry is
the **500-record no-licence cap** (`module-06-data-processing/phaseA-build-loading.md:138` — *"The
cutover is 500 records, sourced from the Senzing MCP server this session"*), which today's response
confirms verbatim (*"Without a license, Senzing limits ingestion to 500 records (error SENZ9000 at
record 501)"*). So the plugin quoted the fact that is stable and declined to quote the one that turns
out to be inconsistent.

**Why it still matters to this plugin.** The licence-request path is a shipped, consent-gated flow
(`module-04-data-collection/SKILL.md`, INV-135) that offers the Bootcamper exactly this licence. Any
future edit that helpfully adds "you'll get 10 days" — or "5 days" — has a coin-flip chance of being
wrong, and would carry a real MCP citation while being wrong, which is the most durable kind of
error this repo produces. A Bootcamper who reads both tools also simply gets contradictory guidance
about a licence they are being asked to request with their name and work email.

## Root cause

**Upstream, not ours.** Two independent copies of the same product fact live in two tool payloads
with no shared source: `submit_feedback`'s hand-written description, and a licence paragraph embedded
in `sdk_guide`'s install `gotchas`/`engine_config_notes` (duplicated within that one response, which
suggests it is templated text pasted into two fields). Nothing on the server appears to derive either
from a single definition, so they drifted.

INV-194's lesson applies in an unusual direction here: it warns against concluding absence from one
tool's silence. This is the mirror case — two tools both *speak*, and their answers conflict. INV-169
governs how to record that: state both with their conditions rather than flattening them into one
absolute. Neither invariant tells you which duration is true, because the repo cannot know; only
Senzing can.

## Proposed change

**No plugin content change, and deliberately so.** Do not pick a duration and do not add one.

1. **File it upstream.** This is a server-side defect and the dry-run skill forbids the run itself
   from calling `submit_feedback` (⛔ "Verify its schema; never invoke it"), so the report needs the
   maintainer's explicit send. Draft, for `category='bug'`, containing: both quotes verbatim, the two
   tools and exact parameters that produced them, server version 1.32.9, the date, and the one-line
   impact — that `sdk_guide` points the reader at `submit_feedback` while disagreeing with it about
   what the licence grants. No PII; nothing identifying the bootcamper, the host, or this repo.
2. **Add a guard that keeps the plugin's silence deliberate rather than accidental.** A test
   asserting no shipped file states an evaluation-licence **duration** (`\d+[- ]day`) near
   licence/eval vocabulary. Today it passes vacuously; its value is that it fails the moment someone
   adds one, and its docstring can carry the reason: two MCP tools disagree, so any duration written
   here is unciteable.
3. **Record the contradiction where a future editor will meet it** — a short dated note in the
   licence-request step (or in `INVARIANTS.md` alongside the existing licence rules) saying the
   duration is contested upstream as of 2026-08-12 and must not be quoted until the server agrees
   with itself. That is the INV-169-shaped outcome: record both observations with their conditions,
   assert neither.

## Acceptance criteria

- [ ] No shipped file states an evaluation-licence duration; the 500-record no-licence cap is
      unchanged and still MCP-cited.
- [ ] A test fails if any shipped file introduces an eval-licence duration. Negative-controlled by
      adding "a 10-day evaluation license" to a shipped file and confirming the suite fails, with the
      mutation verified to land and reverted.
- [ ] A dated note records that the duration is contested upstream (both values, both tools, server
      version), so the omission reads as a decision rather than an oversight.
- [ ] The upstream report is drafted, shown to the maintainer, and **sent only on their explicit
      yes** — or recorded as declined. It contains no PII (INV-135 forbids `license_request` for
      defect reports; this must go as `category='bug'`).
- [ ] Re-verified at implementation time: call both tools again and confirm the contradiction still
      exists. If Senzing has fixed it, the guard and the note still land but the upstream report is
      dropped and the resolution recorded.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      contradiction is in tool text, not platform-specific.

## Affected files

- `tests/` — the no-duration guard.
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` **or**
  `specs/INVARIANTS.md` — the dated contested-fact note (maintainer's choice of home).
- No other plugin file changes.

## Source

- Dry run: `dry-run` phase 3, extended past its documented scope into SDK setup at the maintainer's
  request, 2026-08-12 (`Source: self-observed (assistant retrospective)`). Found because Module 2
  Step 1 requires `sdk_guide(topic='install', …)`, and its licence paragraph could be compared
  directly against the `submit_feedback` description already in context from `get_capabilities`.
- Both quotes are from this session against server **1.32.9**; the `sdk_guide` sentence appears
  **twice** in one response (`install.gotchas` and `engine_config_notes`), so it is not a transcription
  slip on the reading side.
- Priority: **Low for the plugin, Medium upstream.** Nothing in the plugin is wrong today; the cost
  is a trap for the next editor and contradictory guidance for a Bootcamper who reads both tools.
- MCP re-check: **this IS the re-check** — both values read live today. Outcome: **the server
  contradicts itself**, which is neither "confirmed" nor "fixed upstream" but a third case worth
  naming.
- Upstream: **sent 2026-08-12** via `submit_feedback(category='bug')`, on the maintainer's explicit
  approval of the exact message text (shown in full beforehand, per the tool's own contract). Sent
  **after** the dry run closed, as a separate maintainer-authorised action — the run itself never
  called the tool (⛔ dry-run rule). The report carries both quotes verbatim, the two tools and their
  exact parameters, server version, date, impact, a minimal reproduction and a suggested fix; it
  contains **no PII** and no repo or host identifiers. Category was `bug`, never `license_request`
  (INV-135). **Submissions are anonymous, so no reply is possible** — the server's own response
  confirms the Senzing team cannot follow up and directs anyone needing a response to
  support@senzing.com. Nothing further is owed upstream; re-check at implementation time whether the
  contradiction persists.
- Related specs: `specs/module2-license-clarity.md`,
  `specs/reconcile-sdk-guide-license-note-with-detected-limit.md`,
  `specs/license-request-option.md`, `specs/single-license-gate-at-data-processing.md` — all concern
  the same licence flow; none records this contradiction.
