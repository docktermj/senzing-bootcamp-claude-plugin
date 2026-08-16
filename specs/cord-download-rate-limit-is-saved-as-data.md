# A rate-limited CORD download is saved as the source's data file

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Collecting several CORD sources in quick succession trips a rate limit on the MCP server's download
endpoint, and the limit message comes back **as the response body** — so it lands in
`data/raw/<source>.jsonl` looking like a successful, very small download.

Reproduced live, 2026-08-12, fetching the four sources of a generated Las Vegas scenario back to back
via the `download_url` that `get_sample_data` itself returns:

| Source | MCP-reported records | Lines fetched | File content |
|---|---|---|---|
| `PPP_LOANS` | 3,488 | 3,488 | records ✅ |
| `OPEN-OWNERSHIP` | 2,039 | **1** | `Rate limit exceeded. Try again in 1 second.` ❌ |
| `GLEIF` | 1,952 | **1** | `Rate limit exceeded. Try again in 1 second.` ❌ |
| `US-LABOR-VIOLATIONS` | 1,554 | 1,554 | records ✅ |

**Why this is the dangerous shape rather than a loud failure.** The request does not fail: `curl -sS`
reports success and writes a file. There is no exception, no non-zero exit, no HTTP error for a caller
to branch on. Two of four sources are now one-line files whose single line is English prose. A guide
that checks "did the download succeed" gets yes; a guide that checks "is the file non-empty" gets yes.
Only comparing the **line count against the count MCP already told you** catches it — which is how it
was caught here.

**What happens next if it is not caught.** `data/raw/las-vegas_GLEIF.jsonl` containing
`Rate limit exceeded. Try again in 1 second.` flows into Module 5's mapping (a JSON parse failure on
line 1, or worse a "source has 1 record" quality assessment) and into Module 6's load. The Bootcamper
would be debugging their *mapping* for a problem created three modules earlier by a network response
nobody inspected.

**The plugin has no rate-limit awareness at all.** `grep -ri 'rate limit|rate-limit|429|too many
requests'` across `plugins/` returns **nothing** (2026-08-12). So a guide has no reason to expect the
condition, space its requests, or retry.

**The existing safeguard is close but not sufficient.** `SKILL.md:296` does require post-collection
validation — *"non-empty, expected format/encoding, plausible record count"* — and a diligent guide
comparing against MCP's figure would catch this. But:

- `:284` records `record_count` as *"(if known, else null)"* — optional, so nothing forces the
  comparison to exist.
- *"Plausible"* is a judgement, not a check. One line is arguably "plausible" for a source whose size
  the guide never looked up.
- The exact expected count is **already in hand**: `get_sample_data(dataset='las-vegas',
  source='list')` returns `record_count` per source. The check that catches this costs nothing and is
  currently not prescribed.

**This gets worse with more sources, which is the normal case.** `las-vegas` has **11** sources; a
generated scenario can legitimately use several, and the more sources fetched in sequence the more
likely the limit trips. The two that failed here were the 2nd and 3rd of four.

**Severity: medium-high.** No Senzing fact is wrong and nothing crashes — but silent data corruption
at the collection step, surfacing as a mapping or load problem two modules later, is among the most
expensive failure shapes this bootcamp can produce.

## Root cause

Two independent gaps meeting.

1. **Upstream shape (not a defect to file).** The download endpoint answers a rate-limited request
   with a 200-ish body containing prose rather than a machine-readable error. That is the server's
   choice and it is entitled to it — but it means callers cannot distinguish success from throttling
   without reading the body. The message even says *"Try again in 1 second"*, so the remedy is trivial
   **once you know to look**.
2. **Plugin gap (the fixable half).** Module 4's collection step tells the guide to fetch each source
   and then validate "plausible record count", without prescribing the comparison that makes the
   validation decisive, and without any awareness that a throttled response can masquerade as data.
   The exact expected count is available from the same tool call that supplied the download URL, so
   the omission is an oversight rather than a trade-off.

Nothing in the suite could catch this: it needs a live multi-source fetch, which is exactly what a
dry run does and no offline test can.

## Proposed change

1. **Prescribe the count comparison, not a judgement.** In Module 4's collection step, require that
   each fetched CORD source's record count be compared against the `record_count` returned by
   `get_sample_data(dataset=…, source='list')` for that source, and treat a mismatch as a **failed
   collection** — not a warning. Record both numbers in `config/data_sources.yaml` so the check is
   auditable later.
2. **Name the throttling case explicitly and handle it.** Add guidance that a download response may
   be a rate-limit message rather than records: if the fetched content does not parse as JSON Lines,
   or is implausibly short against the expected count, **retry with a short backoff** (the server's
   own message suggests one second) before reporting failure. Space sequential source fetches.
3. **Never write a failed fetch to `data/raw/` under the source's name.** Fetch to a temporary name
   within the project and move it into place only after the count check passes, so a throttled
   response can never be mistaken for the source's data by a later module. (Project-relative
   throughout — INV-200.)
4. **Guard what can be guarded offline.** A test asserting Module 4's collection step requires the
   count comparison and names the rate-limit/retry case. The condition itself needs the network, but
   the *instruction* is text and can be pinned.

**Consider an invariant.** "A collected data source MUST NOT be recorded as collected unless its
record count matches the count the MCP server reported for it" is a durable, testable rule of the
kind this repo registers. Offer it to the maintainer rather than assuming it.

## Acceptance criteria

- [ ] Module 4's collection step requires comparing each fetched source's record count against the
      MCP-reported `record_count`, and treats a mismatch as a failed collection rather than a warning.
- [ ] The rate-limit/throttled-response case is named explicitly, with a retry-and-backoff instruction
      and advice to space sequential fetches.
- [ ] A fetch is not written into `data/raw/` under the source's final name until its count check
      passes; the staging path stays inside the project (INV-200).
- [ ] `config/data_sources.yaml` records both the expected and actual record counts per source.
- [ ] A test pins the presence of the count comparison and the rate-limit handling in the collection
      step. Negative-controlled: removing either instruction fails the suite, with the mutation
      verified to land.
- [ ] Re-verified at implementation time: attempt a rapid multi-source CORD fetch and confirm the
      condition still reproduces. If the server has changed its throttling or now returns a real HTTP
      error, implement what it does then and record the deviation.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the check
      is a count comparison, not a shell idiom, and must not be specified as a `wc -l` pipeline.

## Affected files

- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the collection step
  (`:139-176` region) and the validation instruction (`:284`, `:296`).
- `tests/` — the guard.
- `specs/INVARIANTS.md` — only if the maintainer approves the invariant above.

## Source

- Dry run: `dry-run` phase 3, extended into Data collection at the maintainer's request, 2026-08-12
  (`Source: self-observed (assistant retrospective)`). Found by fetching four CORD sources in
  sequence and comparing line counts against the counts `get_sample_data` had already reported — the
  comparison the plugin does not currently prescribe.
- Server **1.32.9**. Endpoint: `https://mcp.senzing.com/download/las-vegas?source=<SRC>&limit=10000`,
  the `download_url` form the tool itself returns.
- Priority: **Medium-high.** Silent data corruption at collection time, surfacing two modules later as
  a mapping or load fault. Likelihood rises with source count, and multi-source scenarios are the
  norm.
- MCP re-check: **still reproduces** — observed live today, twice in one four-source fetch.
- Upstream: **arguably worth reporting** — a throttled response that is indistinguishable from data
  without body inspection is a client trap. Needs the maintainer's approval to send (the dry run must
  not call `submit_feedback`), and is lower priority than the plugin-side fix, which works regardless
  of what the server does.
- Related specs: `specs/cord-fastpath-load-readiness.md` and
  `specs/module5-fastpath-cord-only-vs-senzing-ready.md` (what happens to a CORD source downstream);
  `specs/get-sample-data`-adjacent work on provenance. None covers fetch integrity.

## Invariants introduced

- `INV-203` — A fetched data source MUST NOT be written to `data/raw/` under its final name, nor
  recorded as collected in `config/data_sources.yaml`, until both checks pass: the fetch returned a
  2xx HTTP status, and its measured record count equals the expected count (`record_count` for an
  uncapped fetch, `min(record_count, download_url_max_records)` for a capped `download_url` fetch).
  Both counts are recorded in the registry entry; a mismatch is a failed collection, never a
  warning; a throttled response (HTTP 429) is retried with a short backoff rather than treated as
  data. Maintainer-approved 2026-08-12 and recorded in `specs/INVARIANTS.md`, indexed under *Data
  quality, mapping and validation gates*. The wording extends what this spec proposed: the 2xx
  clause and the cap clause both come from the implementation-time re-check below, not from this
  spec's text.

## Deviations from this spec, and why (2026-08-12)

Re-verified against MCP server **1.32.9** on 2026-08-12 before any code changed. The condition
**still reproduces** — fetching the same four `las-vegas` sources back to back, `OPEN-OWNERSHIP` and
`US-LABOR-VIOLATIONS` came back throttled (43-byte prose bodies), `PPP_LOANS` and `GLEIF` complete.
Two of this spec's factual claims did not survive that check, and both changed what was built.

1. **The throttled response is a real HTTP `429`, not an unbranchable 200.** This spec's *Problem*
   says *"There is no exception, no non-zero exit, no HTTP error for a caller to branch on"* and its
   *Root cause* §1 calls the response *"a 200-ish body containing prose rather than a
   machine-readable error … the server's choice and it is entitled to it"*. Measured with
   `curl -sS -w '%{http_code}'`: **`http=429`** on both throttled sources. The response *is*
   machine-readable. What is true is narrower: `curl -sS -o <file> <url>` exits **0** and writes the
   prose body regardless, because no status check was requested.

   **Effect on the fix:** the HTTP-status check leads, as check 1 of three, and is the decisive test;
   the count comparison this spec proposed is kept as an independent second check rather than the
   primary one. Both are required, so nothing this spec asked for was dropped — the ordering changed
   and a stronger check was added ahead of it.

   **Effect on the upstream question:** this spec's *Upstream* note reasons from the refuted premise
   (*"a throttled response that is indistinguishable from data without body inspection is a client
   trap"*). It is distinguishable, by status code. No upstream report is warranted, and none was
   sent.

2. **`download_url` caps its response, so "mismatch = failure" cannot be a bare equality test.**
   The citation carries `download_url_max_records: 10000` (`get_sample_data(dataset='las-vegas',
   source='GLEIF', limit=1)`, 1.32.9, 2026-08-12), and the cap bites: `NOMINO-RISK`, MCP
   `record_count` 14,119, returned **exactly 10,000** records. *Proposed change* §1 says to compare
   against `record_count` and treat any mismatch as a failed collection; implemented literally that
   fails **6 of the 11** `las-vegas` sources on correct data. This spec's four sample sources were
   all under the cap (3,488 / 2,039 / 1,952 / 1,554), so it never surfaced.

   **Effect on the fix:** the expected count is `min(record_count, download_url_max_records)` for a
   `download_url` fetch and exactly `record_count` for a `source_download_url` fetch. Mismatch
   remains a failed collection, as specified.

3. **One correction outside this spec's scope, required by it.** `SKILL.md:183` told the guide to
   present `download_url` *"so the bootcamper can download the full JSONL file"* — untrue for the 6
   `las-vegas` sources above the cap. The count rule in §2 cannot be stated correctly without
   distinguishing the two URLs, so that sentence was replaced with the distinction rather than left
   to contradict the new check.

4. **Staging path chosen from the existing layout, not invented.** *Proposed change* §3 asks for "a
   temporary name within the project". Implemented as `data/temp/<source>.jsonl` — the scratch
   directory INV-050's layout tree already provides — because a new directory would need registering
   in that tree under INV-202. Project-relative throughout, as INV-200 requires.

5. **The retry remedy was verified, not just prescribed.** The same four-source fetch that lost two
   sources returned all four complete, at full record counts, when each request retried with a
   one-second backoff (1.32.9, 2026-08-12).

Not runtime-verified: no macOS or Windows host was available, so the cross-platform criterion rests
on the instruction being platform-neutral (asserted by test) rather than on execution. The condition
itself remains network-dependent and unreachable by the offline suite, exactly as this spec states.
