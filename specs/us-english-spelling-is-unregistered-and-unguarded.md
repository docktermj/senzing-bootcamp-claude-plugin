# US English spelling is unregistered and unguarded

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The maintainer stated the preference on **2026-08-16**: US English, not British English.
Nothing in the repository had ever said so, and nothing could see a violation. The sweep
that followed found **1,231 British word occurrences across 295 files**, plus **5 CamelCase
class names** the same sweep could not see on its first pass.

They were not confined to a corner. They were in shipped bootcamper-facing prose
(`ground-rules.md`, seven module skills), in `specs/INVARIANTS.md` (62), in
`specs/IMPLEMENTED.md` (261), in test method and class names, and in **five spec
filenames**. The commonest were `behaviour` (304), `licence` (144), `judgement` (71),
`labelled` (39) and `honoured` (35).

⛔ **The repository was not what caught it.** The correction arrived from outside: someone
read the published plugin in the public access repo, hand-corrected the spellings there,
and the corrections came back through `/retrofit-from-public` as commit `2223961`
(2026-08-16 17:12), which rewrote 20 shipped files British → US.

**That retrofit left the suite red, and nobody noticed until the next full run.**
`retrofit.sh:61-70` copies `plugins/`, `.claude-plugin/`, `docs/` and `README.md` from
public into dev. It does not copy `tests/` or `specs/` — those are not in the public mirror
at all, so they cannot come back. The retrofit therefore moved shipped prose out from under
the dev-only tests that pin it **verbatim**, and nothing reconciled the two. Measured
immediately before the migration: **12 failed / 2730 passed**. Ten were that desync, each
pinning a British spelling the retrofit had already changed:

| Failing test | What it pinned |
|---|---|
| `test_data_collection_generated_scenarios` (×2) | `Omit option 2 when the licence already caps the load`; `unreadable licence state as unbounded` |
| `test_fastpath_gates_on_full_mapping` (×3) | `Name every unrecognised column`; `has zero unrecognised keys and still fast-paths`; `The threshold is a count, not a proportion: zero unrecognised keys, or no fast-path offer.` |
| `test_no_pip_install_senzing` | `never authorises pip for the Senzing SDK` |
| `test_sdk_update_offer` | `normalise the separator before comparing` |
| `test_results_validation_is_diagnostic` | `observation of this install's behaviour, not an MCP claim` |
| `test_verbatim_check_limitations_freshness` | `1 and 3 are CURRENT behaviour; only 2 is still un-re-run` |
| `test_example_recap_sync` | the example `.md` had been retrofitted to `Analyzed`; the committed PDF still read `Analysed`, so the INV-065 pair no longer matched |

The remaining two failures (`test_citation_census`, `test_feedback_ledger`) are unrelated and
still open.

## Root cause

**Three independent mechanisms had to be absent at once, and all three were.**

1. **No convention was written anywhere.** Not in `docs/development.md`, not in
   `ground-rules.md`, not in `specs/INVARIANTS.md`. An author reaching for a house style
   found none, so both spellings were equally defensible for every one of the ~370 specs
   and 42 shipped files written to date. This is why the count reached four figures rather
   than a handful.

2. **No guard.** 2,745 tests, and a British spelling was invisible to every one of them.
   ⚠️ The suite is not blind to shipped *wording* in general — it pins wording heavily, which
   is exactly why the retrofit broke ten tests. It pins the sentences it happens to quote; it
   has no notion of the corpus's vocabulary.

3. ⛔ **The only detector was a human reading the published output, and the correction path
   back is lossy by construction.** `propagate-to-public` mirrors four paths outward;
   `retrofit-from-public` copies the same four back (`retrofit.sh:61-70`). `tests/` and
   `specs/` are in neither direction. So a prose edit made downstream returns as a shipped-file
   change with no way to reach the assertions that quote it, and `retrofit-from-public`'s
   SKILL.md does not require running the suite afterwards. The 2026-08-16 retrofit is the
   worked example: a *correct* edit, faithfully retrofitted, left the tree red.

## Why a word list is the honest shape here, and what it cannot do

**INV-246 requires a multi-site guard to derive its site set by scanning, never by hardcoding
a list.** That binds the *sites*, and this guard will honor it — it scans the corpus. It
cannot bind the *vocabulary*: there is no corpus-derived way to enumerate British spellings,
because the corpus is what is being judged. The word list is therefore a genuine hardcoded
list, and the guard must say so rather than read as exhaustive.

Three limitations found during the migration, each of which the guard must state rather than
leave a reader to assume away:

1. ⛔ **`analyses` is both the British verb and the correct US plural of `analysis`.** All 7
   occurrences in the tree were verbs and were migrated by reading each one. A guard cannot
   flag the word without failing on correct US prose, so it must not — and must disclose that
   it under-detects by exactly this word.
2. **Stem matching over-reaches and must not be used.** `organism`, `mechanism`,
   `parallelism`, `characteristic`, `equally`, `totally`, `radialLine` and
   `LabelLayoutAssertions` all contain British-looking stems and are all correct. Exact words
   only, at letter boundaries.
3. ⚠️ **Letter boundaries catch `snake_case` and miss `CamelCase`.** `_` is not a letter, so
   `test_the_behaviour_limit_is_disclosed` is caught for free. `NoStepBehaviourChanged` is
   not. The migration found five such names only on a second pass, and a guard built the
   obvious way would have shipped blind to all five.
4. ⛔ **Three files must contain British spellings to do their job, and the guard is one of
   them.** This spec quotes 19 of them as evidence; `docs/development.md`'s reference table
   carries 20 in its "avoid" column; the guard's own word list is nothing but British
   spellings. A guard that simply exempts all three by path stops watching the two documents
   most likely to be edited on this subject. The mechanism must be **narrower than the file** —
   an inline marker, a fenced/table-cell carve-out, or a per-file expected count that fails when
   it moves — and whichever is chosen, ⚠️ **it must not be reusable as a general silencer**, or
   it becomes the way every future British spelling gets waved through.

## Proposed change

1. **Register the convention as an invariant.** Draft for the maintainer's sign-off, worded
   about the corpus because that is the unit the drift occurs in:

   > Every English word in this repository MUST use its US spelling — shipped plugin prose,
   > specs, invariants, tests, code comments and identifiers alike. Where US and British
   > forms differ (`-ize`/`-yze` not `-ise`/`-yse`, `-or` not `-our`, `-er` not `-re`,
   > `license` not `licence`, single `l` before a suffix), the US form is the only one that
   > may be written. A file exempted from this rule MUST carry its reason.

2. **Write the guard** as `tests/test_us_english_spelling.py`: stdlib-only (INV-108), scanning
   the tracked text corpus, exact-word and letter-boundary matched, plus an explicit CamelCase
   pass. Its docstring states the three limitations above by name.

3. **Encode the three exceptions with their reasons, and assert each one is still live.** An
   exception that no longer matches anything is a stale exception, and the guard should say so
   rather than carry it forever:

   | Exempt | Reason |
   |---|---|
   | `plugins/senzing-bootcamp/scripts/vendor/d3.v7.min.js` | Vendored third party. Its 9 `grey`/`Grey` hits are CSS color-name keys, not prose. |
   | `D:\Programme` — `tests/test_windows_browser_discovery.py:142`, `:143`, `:151`, and where `specs/IMPLEMENTED.md:2149` records it | A **German** localized `%ProgramFiles%` fixture proving environment expansion. It is not English, and rewriting it silently guts the test it belongs to. |
   | `SCOPE_VERBS`, `.claude/skills/compact-dev-environment/widened_scope.py:61` | Deliberately carries both `"generalis"` and `"generaliz"` so the scanner tolerates either spelling in text it reads. |

4. **Keep the `docs/development.md` "Conventions" section as the human-facing statement** and
   cite the new invariant from it, per INV-183 — the rule must be reachable where an author
   looks, not only where the guard lives.

5. ⚠️ **Close the retrofit gap — proposed as a separate, smaller change, and flagged as the
   maintainer's call whether it earns its own invariant.** `retrofit-from-public`'s SKILL.md
   should require running the full suite after the copy and reconciling any test that pins
   prose the retrofit changed. No guard can catch this class: the suite going red **is** the
   signal, and the gap on 2026-08-16 was that nothing told the operator to look. The same
   applies in the outward direction — `propagate-to-public` publishes prose that dev-only tests
   quote, so a downstream editor is editing text they cannot see is pinned.

## Acceptance criteria

- [ ] An invariant states the US-English rule, worded and **approved by the maintainer**, with
      its index entry under *The development record itself* in the same edit.
- [ ] `docs/development.md`'s Conventions section cites the new invariant, and its
      "not yet an invariant" caveat is removed.
- [ ] A guard fails on a British spelling anywhere in the tracked corpus —
      **negative-controlled**, with mutations verified to land and then reverted, covering all
      three shapes: plain prose, `snake_case` identifier, and `CamelCase` identifier.
- [ ] The guard passes on the tree as it stands after the 2026-08-16 migration, with no
      exception added to make it pass.
- [ ] Each of the three exceptions is asserted to be **still matching something**, so a stale
      exception fails rather than lingers.
- [ ] The three files that must quote British spellings — this spec, `docs/development.md`, and
      the guard itself — pass by a mechanism **narrower than a whole-file exemption**, and a
      British spelling added to the *prose* of any of them still fails. ⛔ A negative control
      proves that, or the carve-out is untested and the two documents most likely to be edited on
      this subject are the two nothing watches.
- [ ] ⛔ The guard's docstring states its three limitations by name — `analyses` under-detection,
      the hardcoded vocabulary, and why stem matching is rejected. A clean run means no *listed*
      British spelling is present, never that the corpus is US English.
- [ ] `retrofit-from-public`'s SKILL.md requires a full suite run after the copy, and names the
      2026-08-16 desync as the reason.
- [ ] Full suite green apart from the two failures already open at the time of writing
      (`test_citation_census`, `test_feedback_ledger`), which this spec does not touch.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry. No existing entry
  edited.
- `tests/test_us_english_spelling.py` — new guard.
- `docs/development.md` — cite the new invariant; drop the "not yet an invariant" caveat from
  the Conventions section added 2026-08-16.
- `.claude/skills/retrofit-from-public/SKILL.md` — the post-copy suite-run requirement.
- ⚠️ **No shipped file changes.** The corpus was migrated on 2026-08-16 (1,231 replacements +
  5 CamelCase renames across 295 files, 5 spec files renamed, `bootcamp_recap.example.pdf`
  re-rendered for INV-065). This spec registers and guards that state; it does not re-do it.

## Source

- Feedback: none — maintainer instruction, 2026-08-16
  (`Source: bootcamper-reported`). The maintainer supplied 21 corrected pairs from the public
  repo and asked for a repository-wide migration plus a durable note.
- Priority: **Medium.** Nothing is broken for a bootcamper today — the migration is done and the
  suite is green. The exposure is recurrence: the convention now exists only as prose in a
  maintainer-only file, so the next author who writes `behaviour` reintroduces it silently, and
  the only mechanism that has ever caught this class is a human reading the published output.
- MCP re-check: **n/a (no Senzing fact).** Internal: the repository's own vocabulary. No Senzing
  claim asserted and no absence about the server relied on.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `truth-set-is-spelled-two-ways-in-shipped-prose` (the closest prior art — a
  spelling inconsistency in shipped prose, fixed as a one-off with no rule left behind, which is
  why this one recurred at scale), `never-modify-global-shell-config-is-unregistered` and
  `write-gate-location-logic-is-unregistered` (same class: a real rule bound by no invariant),
  and INV-065, INV-108, INV-183, INV-246.

## Invariants introduced

- `INV-253` — Every English word written in this repository MUST use its US spelling, in shipped
  plugin prose, specs, invariants, tests, code comments and identifiers alike; where the US and
  British forms differ, only the US form may be written, and any exempted file MUST carry its
  reason. (Recorded in `specs/INVARIANTS.md`, indexed under *The development record itself*.)

⚠️ **The ID is provisional.** `INV-252` is the highest defined, and the five ids above it are
already claimed by `bootcamp-notes-capture-and-recap-section`, which is also unimplemented.
Whichever spec lands first takes the lower numbers under @INVARIANTS.md's "next unused
`INV-NNN`" rule, so `implement-spec` MUST re-derive the ID at implementation time rather than
trusting the line above.

⛔ **Those five ids are deliberately not written out here.** Naming them would make this spec a
second citation of each — the hazard `tests/test_spec_ledger_invariants.py` exists to describe,
and one this repo has already tripped over once (`specs/IMPLEMENTED.md:805`). This spec adds
exactly one new dangling reference to `test_citation_census`, its own, taking the count of
undefined ids from 5 to 6.

## Deviations from this spec, and why (2026-08-16)

1. **The invariant minted is `INV-253`, not the provisional id proposed above.** Re-derived at
   implementation time exactly as the note above requires: `INV-252` was the highest defined,
   this spec landed first, so it took the next number rather than the one reserved for it. The
   five ids `bootcamp-notes-capture-and-recap-section` claims therefore shift up by one when that
   spec lands, and its own text will need the same correction — including its lowest claimed id,
   which now resolves to **this** invariant and must not be read as the note-capture rule.

   ⛔ **The provisional id is deliberately not written out here**, for the same reason this spec
   declines to name the other five: writing it would make this section a live citation of an
   undefined invariant, which is the dangling reference `test_citation_census` fails on. Caught
   by that guard on the first run of this very implementation.

2. ⚠️ **One of the three named exceptions turned out not to be needed, and was not added.**
   `SCOPE_VERBS` at `.claude/skills/compact-dev-environment/widened_scope.py:61` carries the
   *fragments* `"generalis"` and `"generaliz"`, not whole words. The guard matches whole words
   only — the very rule this spec's limitation 2 demands — so the fragment never matches and
   needs no exemption. Adding one would have created precisely the stale exception the spec's
   fifth acceptance criterion exists to forbid. Verified by running the matcher against
   `"generalis"` directly; it is pinned in `test_correct_us_prose_and_identifiers_are_left_alone`
   so a future edit that widens the matcher to fragments fails there rather than silently.

3. ⛔ **The set of files needing an exemption is larger than the three this spec names — INV-246
   in action.** A full scan found British forms in **four** further places, none of them defects:

   | Site | Why it may keep them |
   |---|---|
   | `feedback/**` (31 occurrences) | The bootcamper-feedback archive. It is testimony this repo **quotes**, not prose it writes; rewriting a bootcamper's words falsifies the record, and the text is also the content-addressed dedup key `PROCESSED.jsonl` stores, so a correction would break the ledger correspondence too. Exempt whole, liveness-asserted. |
   | `specs/license-cap-branch-offers-no-way-to-apply-the-license-that-may-have-arrived.md` (2) | Quotes a bootcamper's feedback title verbatim in its `Source:` line — the same string the archive above records. Waived word-and-count. |
   | `specs/INVARIANTS.md` (1) | INV-253's own statement names the British form it forbids, so the rule reads without a second lookup. Waived word-and-count. |
   | `specs/IMPLEMENTED.md` (1) | Records the German `D:\Programme` fixture in a ledger entry — the same exception the spec names for the test file, one file further on. Waived word-and-count. |

4. **The carve-out mechanism is a per-file word-and-count waiver, chosen over the spec's other two
   options.** A waiver names the path, the exact word, *and* how many times it may appear. That
   makes it strictly narrower than a whole-file exemption (every other British form in a waived
   file still fails), self-invalidating (a waiver whose word has gone, or whose count moved, fails
   as stale — which is what satisfies criterion 5 for **all** waivers at once rather than by a
   separate liveness test each), and impossible to use as a general silencer, since there is no
   marker an edit can add to a line: a waiver is a path and a number recorded in the guard, where
   it shows up in a diff. The guard's own file is handled differently and deliberately — a
   sentinel-delimited data block holding the vocabulary, the exemption literals and the negative
   controls' probe words is excised before it is scanned, so the guard's **prose** is still
   checked. `test_the_sentinels_are_not_a_general_silencer` proves the sentinels are honored for
   that one path and nowhere else.

5. **`docs/development.md`'s British forms are not confined to its table**, so the line-based
   table carve-out the spec floated would not have covered it: `licence` also appears in the
   prose sentence naming the pairs. The word-and-count waiver covers both without distinguishing.

6. ⚠️ **`tests/test_invariant_enforcer_citations.py` needed its `EXPECTED_PAIRS` raised 65 → 66**
   — not listed in `## Affected files`, but required: INV-253 names its enforcing test, and that
   guard asserts the invariant→test pair count deliberately rather than tracking it.
