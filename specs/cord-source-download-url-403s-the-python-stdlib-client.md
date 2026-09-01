# CORD's `source_download_url` returns 403 to Python's stdlib HTTP client, and the fetch rules have no remedy

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`module-04-data-collection/SKILL.md` → "CORD fetch integrity" specifies three required checks for a
CORD download. Check 1 covers non-2xx responses, and the only status it gives a remedy for is **429**:

> Anything outside 2xx is a **failed fetch** — never treat the body as data. … On **429**, retry with
> a short backoff … for a few attempts before reporting failure.

**403 is reachable on the bootcamp's most likely path, and it has no remedy.** Measured live on
2026-08-31, Ubuntu 24.04.4, Python 3.12.3:

| Client / User-Agent | `senzing.com/datasets/gleif-lasvegas.jsonl` (`source_download_url`) | `mcp.senzing.com/download/las-vegas?source=GLEIF` (`download_url`) |
|---|---|---|
| `urllib.request`, default UA (`Python-urllib/3.12`) | **HTTP 403** | HTTP 200 |
| `urllib.request` with `User-Agent: curl/8.5.0` | HTTP 200 | — |
| `curl`, default UA | HTTP 200 | HTTP 200 |
| `curl -A "Mozilla/5.0"` | **HTTP 403** | — |

So `senzing.com` serves the file to `curl` and refuses it to the Python standard library, on
User-Agent alone. All four `las-vegas` sources of a generated scenario failed identically:

```text
  GLEIF                  expected  1952  fetched     0  HTTP 403 FAILED
  OPEN-OWNERSHIP         expected  2039  fetched     0  HTTP 403 FAILED
  PPP_LOANS              expected  3488  fetched     0  HTTP 403 FAILED
  US-LABOR-VIOLATIONS    expected  1554  fetched     0  HTTP 403 FAILED
```

Why this lands on the common path rather than an edge:

1. **Python is the bootcamp's most likely language** — the only one natively supported on Linux by
   the Senzing SDK, and the default choice for most Bootcampers.
2. The module tells the guide to fetch and count **in the Bootcamper's chosen language**, explicitly
   steering away from shell idioms: *"Count the records in the fetched file (a count, in whatever
   language the Bootcamper chose; this is not a shell idiom)."*
3. `urllib.request` is the zero-dependency choice a guide reaches for first in Python.

The checks behave correctly — the status check caught it, nothing was written to `data/raw/`, and the
staging directory was left empty, exactly as check 3 requires. The gap is purely in **recovery**: the
Bootcamper is told the fetch failed and given no way forward, while a working route
(`download_url`, MCP-hosted) was in the same response all along.

## Root cause

`plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md`, "CORD fetch integrity",
check 1. The section was written from a **429** incident (verified live 2026-08-12, two of four
sources throttled), and its recovery guidance is specific to that status. No other status has a
documented next step, so a 403 terminates collection.

The neighboring guidance makes the omission easy to miss: the section says a lot about *which*
expected count to compare against per URL (`source_download_url` → exactly `record_count`;
`download_url` → `min(record_count, download_url_max_records)`), so both routes look equally
available. Nothing says one of them is materially more likely to be served to a programmatic client.

⚠️ **This is a Senzing-side access policy, observed from one machine, not an MCP-sourced fact**
(INV-080/INV-149). Whether the 403 is a CDN/WAF User-Agent rule, and whether it applies from every
network, is not something any MCP route reports.

## Proposed change

1. **Prefer `download_url` for CORD collection, and say why.** Module 3b's Truth Set step already
   states this preference (*"Prefer `citation.download_url` (MCP-hosted)"*); Module 4 does not. Add
   the same preference here, with the reason: the MCP-hosted endpoint is served to programmatic
   clients, and it is the route that stays available in restricted-egress environments.
2. **Give check 1 a 403 branch**: a 403 is not a throttle and retrying does not help. Re-fetch via
   `download_url` from the same response; if that also fails, report the host and status to the
   Bootcamper rather than leaving collection stalled.
3. **Record the observation with its date and conditions**, marked observation-only per
   INV-080/INV-149: `senzing.com` refused `Python-urllib/3.12` and served `curl/8.5.0` on
   2026-08-31; `mcp.senzing.com` served both.

⚠️ Do **not** fix this by telling the guide to spoof a browser User-Agent. `Mozilla/5.0` was measured
**403** on the same host, so it is not even a working workaround, and instructing a bootcamp to
disguise its client is the wrong shape of advice regardless.

## Acceptance criteria

- [ ] Module 4's CORD fetch guidance states a preference for `download_url` with its reason.
- [ ] Check 1 gives 403 its own branch — not a retry — that routes to the alternate URL from the same
      response.
- [ ] A Python guide using only the standard library can collect every source of a CORD-backed
      generated scenario by following the module as written.
- [ ] The observation is dated, attributed to a measurement, and marked observation-only.
- [ ] No guidance anywhere instructs setting a misleading User-Agent.
- [ ] The existing 429 backoff guidance and the three integrity checks are otherwise unchanged.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — "CORD fetch integrity":
  the route preference and check 1's 403 branch.

## Source

- Feedback: `/dry-run` phase 3 conversational walk, 2026-08-31, Data collection Step 2
  (`Source: self-observed (assistant retrospective)`) — found by collecting a CORD-backed generated
  scenario with the Python standard library, as the module's own "in whatever language the Bootcamper
  chose" instruction directs.
- Priority: Medium
- MCP re-check: server **1.35.1**, 2026-08-31 — both URLs taken from live `get_sample_data`
  responses for `las-vegas`. The 403/200 split is an **observation of Senzing's web host from this
  machine**, not an MCP-reported fact, and is marked observation-only (INV-080/INV-149).
  owner-checked: not required — the spec asserts a plugin recovery gap, not a server absence.
- Upstream: possibly worth reporting to Senzing that `senzing.com/datasets/*` refuses
  `Python-urllib`, but that is the maintainer's call and is **not** actioned by this spec.
- Related specs: none
