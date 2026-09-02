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

