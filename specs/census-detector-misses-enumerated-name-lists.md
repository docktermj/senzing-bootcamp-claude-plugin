# The census detector misses enumerated name-lists, the drift shape its own comment names

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`coverage_reports.py negatives` reports rationales that pin a **count**, because a count
"cannot survive an index rebuild". It does not report rationales that pin an **enumerated list
of named response elements** — sections, fields, flags — which expires exactly the same way and
for exactly the same reason.

A live instance went undetected in the 2026-09-02 phase-1 sweep. At
`plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:719` the
rationale reads:

> owner: `search_docs` over the Entity Specification IS the route that would carry such a
> precedence rule, and it **returned the *Payload attributes (optional)* and *Mapping
> identifiers* sections**, which establish that payload and registered features are distinct
> categories …

On MCP server **1.36.0, 2026-09-02** that route returns *Payload attributes (optional)*,
*Attributes for the record key* and *Attribute reference*. **There is no *Mapping identifiers*
section in the response at all.** The claim above it still holds, the date certifies the whole
comment, and no report flagged it — the run caught it only because a human-in-the-loop re-ask
happened to read the returned section titles against the rationale's.

The report *did* correctly flag the count-shaped drift in the same sweep
(`specs/DECLINED.md:126`, `'10 hits'`), so the machinery works for the half it implements.

## Root cause

`.claude/skills/dry-run/coverage_reports.py:588-594` — `CENSUS_SHAPED` matches only a numeral
(or `both`) followed by a result-noun:

```python
_RESULT_NOUN = r"(?:hits?|results?|rows?|matches|entries|documents?|chunks?)"
CENSUS_SHAPED = re.compile(
    r"\b(?:(?:all|only|just)\s+)?"
    r"(?:\d+|one|two|…|twelve)\s+" + _RESULT_NOUN + r"\b"
    r"|\bboth\s+" + _COUNTABLE_NOUN + r"\b",
    re.IGNORECASE,
)
```

⛔ **The gap is named in the detector's own docstring and then not implemented.**
`coverage_reports.py:572-575` says: *"On 2026-08-31 two of the three drifted rationales were
exactly this shape — 'all four hits are …' (ten hits by then) **and an exhaustive field list (a
field had been added)**."* The comment identifies the field-list shape as one of the two
observed drift causes; the regex covers only the count. So the report's own evidence base
includes a case its implementation cannot see.

The design instinct in the surrounding comments is right and must be preserved: *"'every hit is
V3-to-V4 material' is a property over whatever came back and survives a rebuild."* The target is
not "any list" — it is an enumeration asserted to be **what the response contained**, where a
server-side addition or rename silently falsifies it.

## Proposed change

Extend `find_census_rationales` (or add a sibling reporter) to also flag a rationale that
enumerates **named response elements presented as what the route returned**. Report, never gate —
consistent with the existing function's docstring, since an enumeration is sometimes the fact
itself.

A workable discriminator, matching the existing phrase-list approach:

- a reporting verb tying the enumeration to the response — `returned`, `carries`, `carry`,
  `holds`, `lists`, `are` — **followed within the same clause by**
- **two or more** coordinated named elements (joined by `and` / `,`), where a named element is
  either emphasized (`*…*`, `` `…` ``) or an ALL-CAPS/`snake_case` identifier, **and**
- a governing element noun — `section(s)`, `field(s)`, `flag(s)`, `key(s)`, `command(s)`,
  `parameter(s)`, `entry/entries`.

⚠️ Must **not** flag (add each as a must-not-flag fixture, the way the `both`/`every` and
`document`-as-verb collisions already are):

- `"every hit is V3-to-V4 material (sz_dbupgrade, sz_configupgrade, breaking-changes, Migration.md)"`
  — a property over whatever came back, with examples.
- `module-02-sdk-setup/SKILL.md:252`'s brew enumeration and `:278`'s scoop enumeration. These
  **are** exhaustive lists and both reproduced exactly on 1.36.0 — but they enumerate what the
  response *carries* as the discriminating fact of an **absence** claim ("no `brew upgrade`
  anywhere; what it does carry is …"), which is the legitimate use. If the discriminator cannot
  separate these from the `:719` case, prefer reporting them and let the reader judge — the
  report's preamble already says a hit needs judgment.
- `module-03-system-verification/phase1-verification.md:251`'s `snippets[]` field list, which
  also reproduced exactly.

Given three of the four enumerations in the corpus are legitimate, the output must stay short
enough to read: report them in their own clearly-labeled block, separate from the count-shaped
hits, with a one-line note that an enumeration is often the fact itself.

Also correct `coverage_reports.py:572-575` so the comment no longer implies the field-list shape
is covered.

## Acceptance criteria

- [ ] `coverage_reports.py negatives` flags `phase2-data-mapping.md:719`'s rationale as an
      enumerated name-list before that rationale is corrected, and stops flagging it after
      `specs/restamp-27-mcp-negatives-to-server-1-36-0.md` rewrites it.
- [ ] The report does **not** flag `"every hit is V3-to-V4 material …"`, and each must-not-flag
      case above is pinned as a fixture in `tests/test_mcp_negative_rationale_shape.py`.
- [ ] Count-shaped and enumeration-shaped hits appear under separate labels, each with its own
      "a hit needs judgment" note; the total stays readable.
- [ ] `coverage_reports.py:572-575` no longer describes the exhaustive-field-list shape as
      something the detector covers unless it now does.
- [ ] Negative control: reintroduce *Mapping identifiers* into the `:719` rationale, confirm the
      report flags it, revert.
- [ ] `coverage_reports.py` stays read-only, stdlib-only, and exits 0 whatever it finds.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `.claude/skills/dry-run/coverage_reports.py` — extend the census reporter; correct the docstring at `:572-575`
- `tests/test_mcp_negative_rationale_shape.py` — fixtures for the new shape and for each must-not-flag case

## Source

- Feedback: `/dry-run` phase 1, 2026-09-02 (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: **server 1.36.0, 2026-09-02.** `search_docs(query='payload attribute versus registered feature attribute record root extracted as feature precedence', category='data_mapping')` returns *Payload attributes (optional)*, *Attributes for the record key*, *Attribute reference* and a DSR-pricing hit — no *Mapping identifiers* section. This spec is about the **detector**, not about a Senzing fact; the MCP call is cited only as the evidence that the undetected shape drifted in practice. The underlying negative's own absence claim is unaffected and carries its `owner:` clause at `phase2-data-mapping.md:719`.
- Upstream: not applicable — this is a maintainer-tool defect, not a server one.
- Related specs: `specs/mcp-negative-markers-carry-rationale-nothing-reverifies.md` (implemented 2026-09-01 — introduced the count-shaped detector this extends), `specs/restamp-27-mcp-negatives-to-server-1-36-0.md` (corrects the instance)


## Deviations from this spec, and why (2026-09-02)

1. **Shipped as a SIBLING reporter, not by extending `find_census_rationales`.** The spec
   offered either ("extend `find_census_rationales` (or add a sibling reporter)"). Extending the
   shared function would have converted a report into a **gate**: the existing
   `NoShippedMarkerPinsACount::test_no_marker_under_plugins_rests_on_a_count` asserts that *no*
   marker under `plugins/` is flagged by that function, so folding the new shape in would have
   failed the suite on `phase2-data-mapping.md:719` — the very hit criterion 1 requires the
   report to produce. `find_enumeration_rationales` therefore sits beside it, and the "report,
   never gate" property in both docstrings survives.

2. **The discriminator needed a FOURTH condition the spec does not name, and without it the
   criterion-2 case flagged.** The spec's three conditions — reporting verb, two or more
   coordinated named elements, a governing element noun — were implemented as written, with the
   noun tested for *presence in the clause*. That flagged
   `module-02-sdk-setup/SKILL.md:387`, which criterion 2 forbids. ⚠️ **The spec quotes that
   fixture truncated** — `"every hit is V3-to-V4 material …"` — and the elided tail is what
   supplies the noun: *"… and the topic list carries no upgrade **entry**"*. There, `entry`
   governs `upgrade` in a separate conjunct, and the parenthesised run is examples under the
   property word `material`. So the noun must **govern** the run: adjacent within 40 characters
   and with **no coordinator in the gap** (`_governing_noun`). That single condition is what
   separates the one real drift from the three legitimate lists.

3. **A tool-call stripper was required and is not in the spec.** The parsed `claim` half
   **includes the invocation**, so `search_docs(query='…', category='data_mapping')` hands the
   matcher two snake_case tokens and a `section` noun for free — on every `search_docs` negative
   in the corpus. Without `_strip_tool_calls` the report would have been useless on its first
   run. ⚠️ Its own first version was too greedy (`\s*\(`) and ate the prose parenthetical in
   *Payload attributes (optional)*, reporting the name as `*Payload  *`; a stripper that removes
   real element names suppresses the hits this exists to find. Now requires no space before `(`
   and an `=` or quote inside.

4. **`phase1-verification.md:251` is left unflagged, and the blind spot is documented rather than
   implied.** The spec lists it must-not-flag and it reproduced exactly on 1.36.0 — but it **is**
   an exhaustive field list, the shape the detector's own comment names as a 2026-08-31 drift
   cause. It escapes because `field` trails in a separate conjunct, the same structure that keeps
   `:387` out. Stated in `find_enumeration_rationales`' docstring and in its guard's docstring,
   with the instruction to widen `_governing_noun` rather than drop the coordinator test if that
   phrasing ever drifts. Reporting it was the alternative; it would also have flagged `:387`.

5. **Two enumeration sites exist that the spec never named (INV-246).** The spec's list is four;
   scanning found six. Both extra sites fall out under the governing-noun rule and are recorded
   here so a future widening knows they are there:
   `module-02-sdk-setup/SKILL.md:887` (*"env_vars holds only PYTHONPATH and LD_LIBRARY_PATH"* —
   a genuine enumeration of response content, and the marker attached to the still-unsent
   `sdk_guide` language-parameter report) and
   `module-07-query-visualize-discover/phase1-query-visualize.md:421` (*"shared by why_entities,
   why_records and why_record_in_entity"* — a list of methods sharing a document, a property).

6. **Criterion 1's second half is mechanism-verified, not tree-verified, and lands with the next
   spec.** "Stops flagging it after `restamp-27-mcp-negatives-to-server-1-36-0` rewrites it" was
   confirmed by rewriting that rationale to the property form and observing the whole
   ENUMERATION-SHAPED block disappear, then restoring the file byte-identical. ⛔ **That control
   also establishes a constraint on the restamp: re-listing today's three section titles keeps the
   rationale flagged, correctly** — `test_a_corrected_enumeration_is_still_flagged` pins it — so
   the correction must name the **property**, not a fresher list.

7. **Two of my own guards were wrong on the first pass, both found by negative control rather than
   review.** They asserted a *contingent* state — that the live tree currently has hits — so the
   next spec's fix would have broken them, one with a bare `IndexError` instead of a diagnosis.
   Rebuilt on a synthetic scratch tree (`tempfile`), with the live-tree claim isolated in
   `TheDriftedSiteIsFlaggedUntilItIsCorrected`, whose failure message names both possible causes
   and says which one to check first. Separately, the block-splitting assertion ran past the
   report's own marker listing and read the fixtures' verbatim text back out of it.

8. **The test file needed the `MCP-NEGATIVE-SCAN: ignore-file` opt-out.** Its synthetic markers
   are concatenated Python literals, so the token lands on a line whose `owner:` clause is on the
   next one — which the scanner correctly reported as three malformed markers. Same route as
   `tests/test_coverage_reports.py`, with the reason stated in the docstring.

## Invariants introduced

None, and deliberately — matching the sibling this extends. The spec that introduced the
count-shaped detector (`mcp-negative-markers-carry-rationale-nothing-reverifies`, 2026-09-01)
registered no invariant either, citing INV-108/INV-246/INV-282 and nothing new. The reason holds
here: this is a **report**, it gates nothing, and the durable rule it serves — a negative's
rationale must state the discriminating property rather than a census of the response — is
already the property the report's own preamble asserts and the guards pin. Minting an invariant
for a maintainer-tool heuristic would bind every future spec to a regex.
