# A guard that pins the *wording* of a claim about an MCP tool fails the person correcting it

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Three instances on 2026-08-13, each found the same way — the suite went red in the hands of the
person fixing a claim, with a message asserting the opposite of what the server returns:

1. **`tests/test_sdk_update_offer.py:195`** pinned two fence comments **in full**, including
   *"documents brew tap / trust / install --cask only"*. When `sdk_guide(topic='install',
   platform='macos_arm')` at server 1.32.9 showed the word "only" was wrong (the response also
   carries `brew uninstall --cask`, `untap`, `install`/`link libpq`, `--prefix`), correcting the
   prose failed the guard. Rescoped to pin the ownership label instead.
2. **`tests/test_sdk_update_offer.py:349`** asserted `INV-129` appears in Step 1b — **the wrong
   citation that `install-verification-has-no-invariant-so-inv129-is-borrowed` existed to fix.**
   Pinning it is what kept it alive. Re-pointed to INV-218.
3. **A guard written the same day** asserted the string `/opt/homebrew` never appears on the macOS
   artifact line, and failed on correct guidance: the row names that form *in order to forbid it*,
   and a substring ban cannot tell a prohibition from a use. Rewritten to extract the backticked
   path and assert it starts with `$(brew --prefix)`.

**One instance remains unfixed.** `tests/test_sdk_update_offer.py:179`:

```python
self.assertRegex(self.flat, r"(?i)never `brew upgrade --cask` or\s+`scoop update`")
```

That pins the wording of a dated absence claim about `sdk_guide`. The claim is currently **true** —
re-confirmed on both platforms at server 1.32.9, 2026-08-13 — which is exactly why it is worth
fixing now rather than when it breaks: the guard will fail the next person who corrects the sentence
after the server starts documenting an update command, and its message will tell them the server
says something it no longer says.

The pattern is already documented in two places, and documentation did not stop three instances in
one day. `tests/test_dated_negatives_are_marked.py`'s docstring states it —
*"A guard that pins a retraction outlives the retraction, and it is consulted precisely by the person
trying to fix the claim… Prefer asserting what IS true over what must not be said"* — and
`coverage_reports.py`'s report text says *"correct the claim AND invert or rescope the guard that
pins it — do not delete the guard."*

## Root cause

The rule is written down in a docstring and a report's prose, and **registered nowhere**. Nothing
binds a new guard to it, and nothing surfaces the existing instances. This is the reverse direction
of the invariant contract, the same mechanism as INV-134 and INV-155: a practice the repo genuinely
follows, with no ID a reviewer can cite and no scan that finds violations.

Why it recurs specifically: pinning a claim's wording is the *easiest* assertion to write. The text
is right there, `assertIn` is one line, and it passes on the day it is written. The correct form —
assert the structural property the text carries — takes a thought about what must remain true when
the server moves.

## Proposed change

1. **Register the rule.** Draft wording for the maintainer's sign-off (`INVARIANTS.md` is
   append-only; `implement-spec` Step 5 requires approval before recording):

   > A test MUST NOT assert the **verbatim wording** of a claim about an MCP tool's content. It
   > asserts the structural property the text must carry — that a citation names the governing
   > invariant, that a fence carries its ownership label, that a path is resolved through a prefix
   > variable — so that correcting the claim when the server moves does not fail the guard. Where a
   > dated claim must be pinned at all, the guard MUST be rescoped rather than deleted, and the
   > reason recorded in its docstring.

2. **Fix the remaining instance** at `tests/test_sdk_update_offer.py:179`. The property that must
   hold is that Step 1b **distinguishes the update command's owner per platform** — not that it uses
   one particular sentence. Assert the ownership distinction (the `plugin-owned` /
   `server-documented` split the section already labels, and which `:195` now pins) and let the
   dated claim live in the `MCP-NEGATIVE` marker, which is the artifact built to carry it and to be
   re-asked.

3. **Record the three fixed instances in the invariant's provenance**, so the next reader sees the
   rule has a history rather than a rationale.

⛔ **A mechanical guard for this is explicitly out of scope, with the reason stated.** Detecting "an
assertion pins wording rather than a property" requires distinguishing the two, which is the same
judgment the rule asks a human to make — a scan keying on "assertion line contains a long verbatim
quote and a tool name" would flag `:195`'s corrected form (which legitimately quotes a label) and
miss a paraphrased pin. Registering the rule and citing it in review is the remedy; proposing a
scanner that cannot work would be worse than none.

## Acceptance criteria

- [ ] An invariant records the rule, worded and **approved by the maintainer**, appended with the
      next unused `INV-NNN` and an index entry in the same edit.
- [ ] `tests/test_sdk_update_offer.py:179` no longer pins the sentence's wording; it asserts the
      per-platform ownership distinction instead.
- [ ] That test still fails if Step 1b stops distinguishing the update command's owner —
      **negative-controlled**, mutation verified to land, then reverted.
- [ ] The dated absence claim itself remains recorded in its `MCP-NEGATIVE` marker, and
      `coverage_reports.py negatives` still lists it (marker count does not drop).
- [ ] The invariant's provenance names all three 2026-08-13 instances.
- [ ] The invariant does **not** name a `tests/test_*.py` path, so
      `tests/test_invariant_enforcer_citations.py` mints no enforcer pair from it.
- [ ] The out-of-scope decision on a mechanical guard is recorded in the invariant or the ledger
      entry, with its reason — so a later run does not re-derive and re-propose it.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `specs/INVARIANTS.md` — one new invariant, appended, plus its index entry.
- `tests/test_sdk_update_offer.py` — the assertion at `:179`.

## Source

- Feedback: none — self-observed across three implementations on 2026-08-13
  (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium.** Nothing is wrong today: the remaining pinned claim is true and every guard
  passes. The cost is paid later and by the wrong person — whoever corrects a Senzing claim meets a
  red suite telling them the server says otherwise, which is the failure mode most likely to make a
  correct fix look wrong.
- MCP re-check: server **1.32.9**, 2026-08-13 — the claim `:179` pins was re-confirmed on both
  `platform='macos_arm'` and `platform='windows'`: neither response carries `brew upgrade --cask` or
  `scoop update`. So this spec proposes changing a guard over a claim that currently **holds**; it is
  not a correction of a stale fact.
- Upstream: not applicable — a repo-authoring rule, not a server defect.
- Related specs: `module02-dated-negatives-about-sdk-guide-carry-no-marker` (instance 1),
  `install-verification-has-no-invariant-so-inv129-is-borrowed` (instance 2),
  `step1-filesystem-fallback-is-linux-only` (instance 3),
  `guards-pinning-a-dated-negative-outlive-it`, INV-209, and
  `plugin-prose-negatives-are-unswept-by-any-guard` (the sibling gap on the prose side).

## Invariants introduced

- `INV-219` — A test MUST NOT pin the **verbatim wording** of a claim about an MCP tool's content or
  about an upstream submission; it asserts the structural property the text must carry instead, and a
  pinned claim that must change is **rescoped, never deleted**, with the reason recorded in its
  docstring. (Recorded in `specs/INVARIANTS.md`, indexed under **The development record itself**
  beside INV-207, approved by the maintainer 2026-08-13.)

## Deviations from this spec, and why (2026-08-13)

Two, and the first widens what this spec proposed.

1. **The approved wording covers upstream-submission claims too, not only MCP tool content.** This
   spec drafted the rule for "a claim about an MCP tool's content" on the strength of three
   instances. A **fourth** appeared while implementing
   `settle-whether-the-install-vs-update-gap-was-reported-upstream`:
   `tests/test_sdk_update_offer.py:239` pins `"same coverage gap reported upstream"` — the phrase but
   **not** the date — so correcting a **false provenance claim** passed it. Had it pinned the date,
   fixing a falsehood would have failed the suite. Both kinds of claim are externally-owned facts the
   offline suite cannot re-check, and both fail the same way, so the maintainer chose the wider scope
   from four options on 2026-08-13. The provenance names all four instances rather than the three this
   spec knew about.

2. **The rescoped test also absorbed the apt/yum half of the distinction.** The spec asked only that
   `:179` assert "the per-platform ownership distinction". The rewritten
   `test_the_macos_and_windows_update_command_is_plugin_owned` asserts `plugin-owned`,
   `server-documented`, **and** "Only on apt and yum is the update command the same" — which
   duplicates the existing `test_only_apt_and_yum_update_via_the_documented_command`. Kept
   deliberately: the ownership distinction is only meaningful as a *contrast*, and a test that
   asserts one half is satisfiable by prose that has lost the other.

**Negative controls, three, and the third is the invariant's own property.** Dropping the
macOS/Windows ownership sentence fails the guard (1 failure); dropping the apt/yum half fails it (2);
and **rewording the dated claim itself — `scoop update` → `scoop upgrade` — now passes**, which is
precisely what INV-219 requires and what the old pin would have failed. Every mutation verified to
land; restored from a `cp` backup.

**A mechanical guard for INV-219 remains deliberately unbuilt**, with the reason this spec gave:
detecting "this assertion pins wording rather than a property" requires making the same judgment the
rule asks a human to make. A scan keying on "assertion line contains a long verbatim quote and a tool
name" would flag `:195`'s *corrected* form, which legitimately quotes an ownership label, and would
miss a paraphrased pin. Registering the rule and citing it in review is the remedy; a scanner that
cannot work would be worse than none.
