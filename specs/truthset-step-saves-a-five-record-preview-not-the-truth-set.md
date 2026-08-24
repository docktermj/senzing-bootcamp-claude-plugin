# Truth Set step saves a five-record preview, not the Truth Set

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Truth Set visualization Step 1.1 says, on the primary path: "**Available (primary
path):** save the MCP records to `src/system_verification/truthset_data.jsonl`".
`get_sample_data` does not return the records — it returns a **five-record
preview** and a URL for the rest. A guide following the step as written saves
**15 of 159 records** and builds the module's "wow moment" on nine percent of the
data.

Nothing catches it. The step already retrieves the true per-source counts in the
line above, and records "the expected record count for the report" at `:116-117`,
but never compares the saved file against them.

The same visualization is the module's mandatory artifact (INV-077) and the
bootcamp's showpiece. A sparse graph is not an error state — it renders, it looks
plausible, and it silently misrepresents what Senzing did.

## Root cause

`plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md:100-102`
treats `get_sample_data` as returning the dataset. Measured on MCP server 1.32.9,
2026-08-13:

| Call | `records` returned | `total_available` |
|---|---|---|
| `get_sample_data(dataset='truthset', source='list')` | 0 | 159 |
| `get_sample_data(dataset='truthset', source='WATCHLIST')` | **5** | 17 |

The response says so itself, in `citation.note`:

> "Showing 5 of 17 records (**preview**). To get more: `download_url` serves up to
> 10000 records per request and needs only `mcp.senzing.com` allowed;
> `source_download_url` is the complete uncapped file but requires egress to
> `raw.githubusercontent.com`."

**The plugin already knows all of this — in the wrong module.**
`module-04-data-collection/SKILL.md:190-198` documents `download_url` (10,000-record
cap, needs only `mcp.senzing.com`), `source_download_url` (uncapped), and, at
`:234-235`, the verification rule this step is missing:

> "fetched via `source_download_url` → expect exactly `record_count`; fetched via
> `download_url` → expect `min(record_count, download_url_max_records)`"

Data collection is Module 4. Truth Set visualization runs **before** it, so the
first module that downloads a dataset is the one without the guidance.

### `download_url` is rate-limited, and it fails as data

Fetching the three Truth Set sources back to back on 2026-08-13 produced, for the
second and third:

```text
Rate limit exceeded. Try again in 1 second.
```

43 bytes, served with **HTTP 429**. `urllib.request.urlopen` raises on it, but
`curl -sS -o file` does not — `-sS` only suppresses the progress meter, and without
`-f` a 4xx body is written to the output file like any other. So the naive fetch
writes the rate-limit sentence **into `truthset_data.jsonl`**, where it becomes an
unparsable line in the middle of the dataset. The first attempt on this walk did
exactly that and produced a file containing 120 CUSTOMERS records and one line of
English prose.

That is the case for the count check in "Proposed change" step 2 being mandatory
rather than advisory: it is the only thing standing between a rate-limited fetch
and a corrupt data file that still looks like JSONL. Retrying with backoff on 429
recovered all three sources cleanly (120 + 22 + 17 = 159).

One detail does not transfer unchanged: `module-04`'s "`source_download_url` … needs
egress to **senzing.com**" is correct for the CORD collections
(`las-vegas/GLEIF` → `https://senzing.com/datasets/gleif-lasvegas.jsonl`, verified
same server and date) but **not** for the Truth Set, whose `source_download_url` is
`https://raw.githubusercontent.com/Senzing/truth-sets/main/truthsets/demo/watchlist.jsonl`.
The MCP server's own instructions warn that allowing `mcp.senzing.com` does not
cover GitHub content. A firewalled bootcamper told to allow `senzing.com` would
still fail here.

## Proposed change

1. Rewrite Step 1.1's primary path: `get_sample_data` returns a **preview plus
   URLs**; the records come from `download_url` (MCP-hosted, sufficient here since
   every Truth Set source is far below the 10,000 cap) or `source_download_url`.
   Take both URLs from the response, never hardcoded.
2. **Add the count check.** After writing `truthset_data.jsonl`, compare its line
   count against the per-source `record_count` values already retrieved in the
   `source='list'` call, and fail loudly on a mismatch rather than proceeding to
   visualize. This is the one check that turns the whole class of under-fetch into
   a visible error.
3. Name the egress hosts **per dataset, from the response**: `mcp.senzing.com` for
   `download_url`; whatever host `source_download_url` carries — `senzing.com` for
   CORD, `raw.githubusercontent.com` for the Truth Set. Do not restate Module 4's
   sentence, which is CORD-specific.
4. Cross-reference `module-04-data-collection/SKILL.md:186-198` rather than
   duplicating it, and consider hoisting the shared download contract somewhere both
   modules read, since Module 3b needs it first.
5. While there: correct `module-04`'s egress sentence to say the host comes from the
   response, since it is stated as a general rule and is only true for CORD.

## Acceptance criteria

- [ ] Following Step 1.1 on the primary path writes a `truthset_data.jsonl`
      containing **159** records — 120 CUSTOMERS, 22 REFERENCE, 17 WATCHLIST — not
      15.
- [ ] The step compares the written line count against the per-source
      `record_count` values from the `source='list'` response and stops on a
      mismatch.
- [ ] The step names the egress host per URL, taken from the response, and does not
      assert `senzing.com` for the Truth Set.
- [ ] `module-04-data-collection/SKILL.md`'s egress sentence no longer states a
      single host as a general rule.
- [ ] The download retries with backoff on HTTP 429, and never writes a non-JSON
      response body into `truthset_data.jsonl`.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` —
  Step 1.1's primary path, the download route, and the count check.
- `plugins/senzing-bootcamp/skills/module-04-data-collection/SKILL.md` — the
  egress-host sentence.

## Source

- Feedback: dry run phase 3, 2026-08-13 — executed Step 1.1 against the live server
  and got a five-record preview where the step expects the records
  (`Source: self-observed (assistant retrospective)`)
- Priority: **High** — it silently produces the module's mandatory artifact from 9%
  of the data, in the module the bootcamp treats as its showpiece.
- MCP re-check: server 1.32.9, docs indexed 2026-08-11 20:52 UTC, checked
  2026-08-13. `get_sample_data(dataset='truthset', source='list')` → 3 sources, 159
  records; `source='WATCHLIST'` → 5 records of 17 with `citation.note` naming the
  preview and both URLs; `dataset='las-vegas', source='GLEIF', limit=1` → 1 of 1,952
  with `source_download_url` on `senzing.com`. Still reproduces.
- Upstream: not applicable — the server labels the preview clearly; the plugin does
  not read it.
- Related specs: `specs/truthset-cannot-satisfy-the-generated-scenario-invariants.md`
  (the other place a Truth Set property is not accounted for)

## Invariants introduced

- `INV-228` — A step that writes a dataset obtained from the MCP server MUST verify the written record count against the count the server reported, per source, and MUST stop on a mismatch; egress hosts are named per URL from the response. (recorded in `specs/INVARIANTS.md`, 2026-08-14; approved by the maintainer.)
