# The empty `content` INV-160 calls a failed retrieval is now a declared elision, and it has spread to `generate_scaffold`

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

INV-160 and `bootcamp-onboarding/ground-rules.md:113-119` classify a specific `find_examples`
response as a **defect**:

> ⛔ **An empty `content` is never evidence that the file is empty.** If `content` is empty while
> `content_length` is non-zero, the retrieval **failed** — regardless of what `truncated` says — so
> fall back to the `raw_url` … Re-check when the server updates; this caution goes away when the
> retrieval does.

INV-160 states the same as a rule: "a payload that contradicts its own metadata MUST be treated as a
**failed retrieval**".

The text asked to be re-checked when the server updates. It has. On **server 1.32.8, 2026-08-11**,
`find_examples(repo='brianmacy/sz_mem-v4', file_path='mem_load.py')` returns:

```json
{"content": "", "content_length": 20706, "truncated": false, "content_elided": true,
 "access_steps": [{"step":1,"action":"fetch","url":"https://raw.githubusercontent.com/…","note":"Fetch raw_url to read the source code."},
                  {"step":2,"action":"git_clone","command":"git clone --depth 1 https://github.com/…"},
                  {"step":3,"action":"inline","note":"Only if steps 1 and 2 both failed … AND your client forwards arguments that are not in a tool's declared schema … Clients that validate arguments against the declared schema cannot use this step; prefer fetching raw_url or cloning."}]}
```

**The payload no longer contradicts its metadata — it declares itself.** The new `content_elided:
true` field says the omission is intentional, and `access_steps` gives the intended route in order.
This is a design, not a bug.

**Proved, not inferred** — the skill requires reproducing the original failing conditions:

- Large file (`mem_load.py`, `content_length: 20706`): elided.
- Small file (`CHANGELOG.md`, `content_length: 795`): elided **identically**. So it is not a
  size threshold that a smaller request could slip under; file retrieval never returns inline
  content by default.
- Passing `max_lines: 15` did not change it.
- Search mode (`find_examples(query=…)`) still returns real `code_snippet` content with
  `truncated: true` — so the plugin's "search mode is the reliable route" advice is still correct.

**It has also spread beyond `find_examples`.** `generate_scaffold(language='python',
workflow='initialize')` on 1.32.8 returns the same `access_steps` block and **no inline code at all**
— only `snippets[]` with `file_path`, `raw_url`, `size_bytes`, `line_count`. INV-160's scope
("`find_examples` file retrieval") is now narrower than the behavior it governs.

**What has NOT changed:** the `inline` parameter is still **undeclared** in the live
`find_examples` schema (`file_path`, `language`, `list_files`, `max_lines`, `query`, `repo` — no
`inline`), so INV-160's prohibition on adopting it still binds. The server now says so itself:
*"Clients that validate arguments against the declared schema cannot use this step; prefer fetching
raw_url or cloning."* That is the plugin's own rule, endorsed upstream.

Verdict: **`retire-workaround`** — the *premise* retires, the *conclusion* stays.

## Root cause

INV-160 was written 2026-07-28 against server 1.32.1, where an empty `content` beside a non-zero
`content_length` had no accompanying signal and was indistinguishable from a broken retrieval. The
project filed it upstream as a `bug` (2026-07-28, follow-up 2026-07-30). The behavior was not
reverted; it was **documented** — the server added `content_elided` and `access_steps` to say "this
is deliberate, here is how to get the file". A workaround written against an undeclared behavior
survives its own justification when the behavior becomes declared, because nothing re-reads the
premise once the remedy works.

## Proposed change

**Keep every operational instruction. Correct only the classification.**

1. **`ground-rules.md:113-119`** — keep "search mode is the reliable route" and "fetch the `raw_url`",
   which the server's own `access_steps` step 1 now prescribes. Replace "the retrieval **failed**"
   with what the response says: file retrieval elides `content` **by design**, signaled by
   `content_elided: true`, and `access_steps` lists the route (fetch `raw_url` → clone → *not* the
   inline step, which needs an undeclared parameter INV-136 forbids). Delete the promise that "this
   caution goes away when the retrieval does" — it will not; the caution is now permanent guidance,
   not a temporary mitigation.
2. **Keep ⛔ "An empty `content` is never evidence that the file is empty."** Still true, still the
   consequence that matters, and now provable from `content_elided` rather than from a metadata
   contradiction.
3. **Widen the scope note** to say the same elision applies to `generate_scaffold`, which returns
   `snippets[]` with `raw_url` and no inline code. Any step that expects scaffold code inline must
   fetch `raw_url`.
4. **INV-160 — append, never edit away.** Per `INVARIANTS.md`'s own rules and this skill's guardrail,
   add a dated clause: the failed-retrieval premise no longer holds as of server 1.32.8
   (2026-08-11), the elision is declared by `content_elided: true` with an `access_steps` route, the
   behavior now extends to `generate_scaffold`, and **every MUST in the invariant stands** — fall
   back to `raw_url`/clone, never tell the Bootcamper the file is empty, never adopt an undeclared
   parameter. Do **not** delete or renumber it. Whether the changed premise warrants a *new*
   superseding invariant rather than a dated clause is the maintainer's call at implementation time;
   the MUSTs are unchanged either way, which argues for the clause.
5. **INV-160's INV-149 contrast still works** and should stay: an empty `response_schemas` `data`
   array is coverage, not failure. Note that the distinguishing test has improved — the server now
   marks the deliberate case explicitly instead of leaving it to be inferred.

**Fallback (INV-125).** Nothing new depends on a call: this replaces a classification with a
better-sourced one and leaves the access path identical.

## Acceptance criteria

- [ ] `ground-rules.md` no longer calls the elided retrieval a **failure**; it names
      `content_elided: true` and the `access_steps` order, and the "this caution goes away" sentence
      is gone.
- [ ] The ⛔ "never evidence that the file is empty" rule and the raw_url/clone fallback are retained
      verbatim in substance.
- [ ] The undeclared-`inline` prohibition is retained and now cites the server's own statement that
      schema-validating clients cannot use that step (INV-136).
- [ ] The guidance says the elision also applies to `generate_scaffold`, whose `snippets[]` carry
      `raw_url` and no inline code.
- [ ] INV-160 carries a **dated appended clause**; it is **not** deleted, reworded away, or
      renumbered, and its MUSTs still read as binding.
- [ ] **Re-verification clause:** implementing this requires `find_examples(repo=…, file_path=…)` to
      still return `content_elided: true` with `access_steps`, for **both** a large and a small file.
      If inline `content` has returned, this spec is wrong — re-triage instead of implementing.
- [ ] `tests/test_scaffold_citations_and_database_type.py:115-134` (Item 11 / INV-160, the
      undeclared-parameter assertion) still passes unchanged — that half of INV-160 is untouched —
      and any assertion pinning the word "failed" is repointed to the requirement with an INV-181
      docstring.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — `:110-119`.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` and
  `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — both cite
  INV-160; check neither repeats the failed-retrieval framing.
- `specs/INVARIANTS.md` — INV-160, appended clause only.
- `tests/` — the assertions named above.

## Source

- Sweep: `delegate-to-mcp-server`, 2026-08-11. Server **1.32.8** (was 1.32.1 when INV-160 was
  written), docs index **2026-08-11 13:35 UTC** — both axes moved.
- Tools called: `get_capabilities`, `find_examples` (file retrieval x2 at different sizes, `list_files`,
  and search mode), `generate_scaffold(language='python', workflow='initialize')`.
- Priority: **Medium.** No Bootcamper is misled into a wrong action — the fallback the plugin
  prescribes is the one the server prescribes — but an invariant carries a false premise, and
  invariants are load-bearing in a way ordinary prose is not.
- Upstream: previously filed as a `bug` (2026-07-28, follow-up 2026-07-30). **Close it out**: the
  behavior is now documented rather than reverted, so no further report is warranted. One residual
  worth a separate `bug` if the maintainer wants it — `find_examples(repo=…, list_files=true)`
  returns a truncated README ending *"[README truncated. Use find_examples with file_path='README.md'
  for full content.]"*, and that `file_path` call returns elided content. The instruction does not do
  what it says.
- Related specs: `specs/find-examples-file-retrieval-returns-empty-content.md` (the original),
  `specs/inv149-empty-response-schemas-is-coverage` context in `specs/INVARIANTS.md`.

## Deviations from this spec, and why (2026-08-11)

**INV-160 handling: dated clause, not a superseding invariant.** The spec left this to the
maintainer at implementation time; they chose the dated clause, on the grounds that every MUST is
unchanged and a second invariant would duplicate them. INV-160 keeps its number and text; the clause
records the corrected premise, the `content_elided` signal, the unconditional-elision proof, the
widened scope to `generate_scaffold`, and that the guidance is now permanent rather than a
mitigation awaiting a fix.

**The three other INV-160 citation sites needed no change — verified by opening them** (INV-182):
`module-03-system-verification/phase1-verification.md:204` and `:254`, and
`module-02-sdk-setup/SKILL.md:680`, all cite the **undeclared-parameter** half, which this change
does not touch. The spec asked for them to be checked for the failed-retrieval framing; none carries
it.

**The upstream residual named in the spec's Source section was sent** on 2026-08-11 as a
`category='bug'` submission, with the maintainer's explicit approval: `find_examples(list_files=true)`
ends its truncated README with "Use find_examples with file_path='README.md' for full content", and
that call elides. Anonymous, so no reply is possible.
