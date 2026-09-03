# The measured-only guard enumerates three of four absence branches, and its property matcher breaks on inline bold

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`tests/test_license_limit_is_written_only_from_a_measurement.py` requires every INV-244 absence
branch to state the measured-only property. It enumerates those branches with an `ABSENCE` regex,
and **that regex reaches three of the four**:

| Site | Phrasing | Guard sees it? |
|---|---|---|
| `module-01/phase1-discovery.md` | *"absence still means not yet measured"* | yes |
| `module-06/phaseA-build-loading.md` | *"absent no matter **what** license is installed"* | yes |
| `module-06/phaseB-load-first-source.md` | *"absence says nothing about the installed license"* | yes |
| `module-04-data-collection/SKILL.md:99` | *"absent no matter **which** license is installed"* | **no** |

One word — *which* against *what* — and that branch is outside the guard entirely.

**Second, the property matcher breaks on inline bold.** `MEASURED_ONLY` looks for
`writes only a measured value`. Three sites wrap the whole phrase in `**…**`, so the flattened text
still contains it. `module-04:99` writes *"writes only a **measured** value"*, with the emphasis
inside the phrase — so the substring is `writes only a **measured** value` and the matcher misses
it. ⚠️ **The property is present and correct at that site**; only the matcher cannot see it. Both
defects therefore hide each other: the site the regex cannot reach is also the site whose property
the other regex could not match if it did.

⛔ **This is the fifth instance of one failure shape in a single day, and it is in the guard written
to fix the fourth.** The sequence: the writer count was wrong → the correction minted a new count →
the guard against counts enumerated the phrasings already seen → the concept-level rewrite
over-matched a compound adjective → and now the *other* regex in the same file enumerates the
absence phrasings already seen. Every step fixed its instance and reproduced the shape.

## Root cause

`ABSENCE` was written by reading the three sites the previous spec touched. `module-04:99` was
never one of them, so its wording was never in the sample — the same derivation error the spec that
created this guard was written to correct, in the *other* regex of the same file. Nothing forced the
enumeration to be checked against the full set of sites, because the set of sites is what the regex
is used to compute.

The bold-marker fragility is narrower: flattening collapses whitespace but leaves Markdown emphasis
in place, so any matcher written against a phrase is sensitive to where an author put `**`. Three
sites happened to bold the whole phrase and one happened to bold a word inside it.

## Proposed change

1. **Strip Markdown emphasis in `flatten()`**, alongside whitespace collapsing, so a matcher tests
   the *text* rather than the author's emphasis choices. ⚠️ This is the general fix and it makes
   every matcher in the file less brittle, not only this one.
2. **Derive the absence-branch set from something stable**, not from a list of phrasings. The
   durable marker is that these are the bullets INV-244 governs: each is an *absent-or-null* branch
   that cites INV-244. Match on that structure — an `Absent or null` bullet citing INV-244 in a file
   that discusses `license_record_limit` — and the wording is then free to differ per site, which it
   should, because each module says it in its own voice.
3. **Assert the count of branches found**, so the set shrinking is a failure rather than a quieter
   pass. Four today; a fifth module adding the branch should raise it, and a branch disappearing
   should fail.
4. ⛔ **Do not normalize the four sites to one sentence.** They are deliberately phrased per module,
   and INV-179 does not apply — this is a conclusion each branch draws locally, not a rule stated
   once. Making the prose uniform to suit a regex is fixing the wrong artifact.

## Acceptance criteria

- [ ] `flatten()` strips `**`, `*`, `` ` `` and `_` emphasis before matching, and a test pins that a
      phrase bolded inline still matches.
- [ ] The absence-branch set is derived from the `Absent or null` + INV-244 structure, not from a
      list of conclusion phrasings, and it finds **four** sites including
      `module-04-data-collection/SKILL.md:99`.
- [ ] A floor asserts the number of branches found, so the set shrinking fails rather than passing
      quietly (INV-265).
- [ ] All four sites are confirmed to state the measured-only property; none is reworded to suit the
      matcher.
- [ ] Negative-controlled: removing the property from **any** of the four fails, including
      `module-04`, which the current guard cannot reach.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `tests/test_license_limit_is_written_only_from_a_measurement.py` — `flatten()`, `ABSENCE`, and the
  branch floor

## Source

- Feedback: none — found by `/production-readiness-audit` on 2026-08-28, cycle 5 of the second
  unattended loop, which is that loop's cap (`Source: self-observed (assistant retrospective)`).
  Found by tracing the license state machine one file at a time with an independently written probe
  and comparing its answer against the guard's — the probe used `(?:what|which)` and the guard did
  not, which is the whole finding.
- Priority: **Low.** Nothing shipped is wrong: all four sites state the property correctly, and the
  three the guard reaches are protected. The exposure is that `module-04:99` could lose the property
  silently. Filed rather than dropped because it is the fifth instance of a recurring shape and the
  deferred invariant drafted in
  `the-writer-count-matcher-enumerates-phrasings-not-the-concept` is meant to stop exactly this —
  which makes this spec evidence for that invariant's wording as much as a fix.
- MCP re-check: **n/a (no Senzing fact).** The subject is two regexes in one test file.
  `get_capabilities` dated the run: server **1.33.0**, 2026-08-28.
- Upstream: not applicable.
- Related specs: `specs/the-writer-count-matcher-enumerates-phrasings-not-the-concept.md` (the guard
  this completes, and whose deferred invariant this is evidence for);
  `specs/counting-the-writers-of-license-record-limit-is-the-wrong-invariant.md`;
  `specs/sdk-setups-license-reconciliation-does-not-say-whether-to-persist.md`

## Deviations from this spec, and why (2026-08-28)

⚠️ **One deviation, on item 2, and the spec's own premise was the thing that was wrong.** It
proposes deriving the branch set from *"an `Absent or null` bullet citing INV-244"*. That marker
exists at only **three** of the four sites: `phaseA`, `phaseB` and `module-04` carry it;
**Module 1's Step 5a does not** — it reasons about the field being absent inside a record-count
threshold check, not in a branch bullet. Implementing item 2 literally would have dropped Module 1
and traded one blind spot for another, which is the exact failure this spec exists to correct.

**Two alternatives were tried and rejected before settling.** A file-level *"cites INV-244"*
derivation collects **five** files — it pulls in `module-02-sdk-setup`, which cites INV-244 four
times for the **reconciliation**: that file is the *writer*, not a reader drawing the
not-yet-measured conclusion, so requiring the property there is meaningless. Narrowing to
*"INV-244 within N characters of 'absen'"* still collects module-02, because its rule *"Never write
this field when it is ABSENT"* legitimately mentions absence.

**What shipped is a documented union of two markers**: the `Absent or null` bullet (structural, and
what a new module adding this branch will carry) **or** the absence conclusion, matched at concept
level with `wh(?:at|ich)` alternation rather than as three literal sentences. Four sites, floor of
four, and `test_the_branch_scan_reaches_the_bullet_only_site` pins module-04 by name because it is
the site that motivated the spec. The union and the module-02 exclusion are both explained in the
test's docstring, so the next reader does not re-derive them.

⛔ **Item 1 needed narrowing too, and the first attempt broke the file.** Stripping `*`, `_` and
backticks turned `bootcamp_progress.json` into `bootcampprogress.json` and `license_record_limit`
into `licenserecordlimit`, breaking every needle that names a field — the suite caught it
immediately. `flatten()` strips `*` and backticks only. Underscore-italics are not used in this
corpus and `_` is an identifier character throughout it, so the trade is not close; the limitation
is **pinned as an assertion** (`_measured_` must NOT match) rather than left as an untested
assumption, with the reason beside it.

⚠️ **Three negative controls initially passed, and none of the three was a real pass.** Two were
**unlanded mutations** — the sed used a literal space where the files wrap the phrase across a line,
and module-04 writes `**measured**` in lowercase where the pattern expected uppercase. The third was
a genuine pass for a reason worth keeping: `phase1-discovery.md` states the property in **two**
forms, so removing one left the other. Re-run with a whitespace- and case-tolerant mutation that
removes **every** accepted form and reports how many it removed, all four fail. ⛔ **This is the
hazard `dry-run` names — a missed target and an escaped mutation look identical in a loop's
output** — and it is why each mutation now prints its substitution count.

**No shipped file changed**, as the spec's `## Affected files` predicts: `git status -- plugins/` is
empty and `conformance.py since` reports **0** hard rules added. Suite **3,744 passed, 4 skipped**.
