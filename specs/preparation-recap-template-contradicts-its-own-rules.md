# Bootcamp preparation's Step 7 recap template breaks two rules the same file states

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`bootcamp-preparation/SKILL.md`'s Step 7 recap template (`:362-371`) is bootcamper-facing text, and
following it literally violates two rules stated elsewhere in the plugin — one of them 100 lines
earlier in the same file. Both were hit while executing the module as written, on a `--fresh` walk,
2026-08-12.

### 1. The template uses the bare word "Language", which the same file forbids

`SKILL.md:264-265`:

> Always say "**programming language**", never the bare word "language" (avoids confusion with
> spoken languages).

`SKILL.md:368`, inside the recap template:

```text
• Language: {programming language}
```

The rule is absolute ("Always… never") and its rationale is explicit. The template's label is
exactly the forbidden form, in text the Bootcamper reads. A guide following the file cannot satisfy
both: honoring the rule means departing from what looks like a pinned template, and honoring the
template means printing the word the rule bans. Neither branch is a good outcome, and the guide has
no way to tell which the authors meant.

### 2. The `Modules:` line is ambiguous, because two module names contain commas

`SKILL.md:366`:

```text
• Modules: {ordered selected module names}
```

Rendered for a Core run, the comma-separated list reads as **fourteen** items rather than eleven:

```text
• Modules: Bootcamp preparation, Entity Resolution Concepts, Discover the Business Problem,
  SDK setup, System verification, Truth Set visualization, Data collection, Data Quality,
  Mapping, and Transformation, Data processing, Query, Visualize and Discover, Graduation
```

Two of the eleven display names carry internal commas — **"Data Quality, Mapping, and
Transformation"** and **"Query, Visualize and Discover"** — and the module table at `:49-61` is the
source of truth for those exact names, which INV-079 requires be used verbatim rather than
abbreviated. So the ambiguity cannot be fixed by renaming the modules; it has to be fixed in the
separator.

**The plugin already solved this exact problem elsewhere, which is what makes it an oversight rather
than a judgment call.** `generate_recap_pdf.py --check --expect-modules` takes a **semicolon**
separated list, and `dry-run/phase2-hooks-and-scripts.md` spells out why: *"with **semicolons** (two
module names contain commas)"*. The Step 7 template inherits the bug that flag was designed to
avoid.

**Severity is low and worth stating plainly.** Nothing breaks, no artifact is wrong, and a
Bootcamper skimming the recap will most likely read past both. The cost is the phase-3 finding class
this walk exists to surface: an instruction that cannot be followed as written teaches the guide to
treat the surrounding instructions as advisory — and the instructions immediately around this one are
the pinned ⛔ gates where paraphrase is the documented failure mode (INV-056).

**No Senzing fact is involved.** Internal consistency only; no MCP tool was called for this finding.

## Root cause

Two independent drifts into one template.

1. **The "programming language" rule was added to the question, not to the recap.** `:264-265` sits
   inside Step 4, where the *question* is composed, and the Step 4 question and prose both honor it.
   The Step 7 template was written separately as a compact fixed-width block where a short label
   reads better, and the rule was never applied backwards over it. Nothing checks the recap against
   Step 4's vocabulary rule.
2. **The comma hazard was discovered in a script, and the fix stayed in the script.** The
   `--expect-modules` semicolon convention was introduced for the PDF checker, which consumes the
   names programmatically. The Step 7 recap merely *displays* them, so it was never revisited —
   even though display is where a human has to disambiguate.

Both are invisible to the suite: no test renders the Step 7 template, and no test asserts the
vocabulary rule against anything but Step 4's question.

## Proposed change

1. **Relabel the recap line** to `• Programming language: {programming language}`, matching
   `:264-265`. Cheapest fix, and it keeps a single vocabulary across the module.
2. **Separate the module list with semicolons** in the template, matching the
   `--expect-modules` convention, and say why inline so the next editor does not "tidy" it back to
   commas — e.g. `• Modules: {ordered selected module names, semicolon-separated — two names contain
   commas}`. A bulleted one-per-line list is an acceptable alternative under `standard`/`detailed`,
   but the template must stay a single line under `minimal` (`:355-356`), so the separator fix is the
   one that works in every verbosity.
3. **Guard both.** A test that renders the template's field labels and asserts (a) no bootcamper-
   facing line uses the bare word "Language" as a label where a programming language is meant, and
   (b) the module-list line does not use comma separation while any display name contains a comma.
   The second is the durable form — it stays correct if a future module name gains a comma.

**Do not renumber or restructure Step 7**, and do not touch the module table's display names: INV-079
requires those exact strings, and `:155-159` names abbreviation as the thing to avoid.

## Acceptance criteria

- [ ] `SKILL.md:368`'s label reads "Programming language" (or another form containing "programming
      language"); no bootcamper-facing line in the recap uses the bare word "Language" as the label
      for a programming language.
- [ ] The `Modules:` line is not comma-separated: it uses semicolons (or one name per line), and
      carries an inline note saying why, so it is not silently reverted.
- [ ] The template still renders as a **single line** under `minimal` verbosity (`:355-356`).
- [ ] Module display names are unchanged — `git diff` shows no edit to the module table at `:49-61`
      (INV-079).
- [ ] A test asserts both properties, with the module-list check written against "any display name
      containing a comma" rather than against the two current names, so it survives a new one.
      Negative-controlled: reverting either fix fails the suite, with the mutation verified to land.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) —
      documentation and a text assertion only.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — the Step 7 recap template
  (`:362-371`, specifically `:366` and `:368`).
- `tests/` — the guard.

## Source

- Dry run: `dry-run` phase 3 (conversational walk), 2026-08-12, `--fresh` project, at Bootcamp
  preparation Step 7 (`Source: self-observed (assistant retrospective)`). Found by executing the
  template rather than reading it: the comma ambiguity is only visible once eleven real names are
  substituted in, and the vocabulary clash only once the label and the Step 4 rule are in the same
  turn.
- Deduplicated: no existing spec or test mentions the "never the bare word language" rule
  (`grep` over `specs/*.md` and `tests/` → nothing), and no test renders the Step 7 template.
- Priority: **Low.** Cosmetic in effect; the reason to fix it is that it is a self-contradiction
  sitting three lines from the pinned-wording gates, and those depend on being read as exact.
- MCP re-check: **n/a — no Senzing fact.** No tool called for this finding.
- Upstream: not applicable.
- Related specs: none directly. `specs/inv050-tree-has-no-reachability-guard.md` and
  `specs/scaffold-banner-ignores-fresh-and-seeded-modes.md` are the same "the artifact drifted from
  the rule and nothing renders it" shape, if a reader wants precedent.

## Deviations from this spec, and why (2026-08-12)

Implemented as specified — both fixes, the module table untouched, no Senzing fact involved so no MCP
re-check applied. One difference in where the reasoning went.

**The "why" is adjacent to the template, not inside it.** *Proposed change* §2 suggests the inline
form `• Modules: {ordered selected module names, semicolon-separated — two names contain commas}`.
The template line instead reads `{ordered selected module names, separated by "; "}`, and the
reasoning — both offending names, the fourteen-vs-eleven miscount, and the `--expect-modules`
precedent — sits in a ⛔ block immediately below the fenced block, alongside the companion rule about
the label. Two reasons: the fenced block is what a guide reads as the thing to print, so a
parenthetical justification inside it competes with the value it is describing; and criterion 3
requires the recap to still render as a single line under `minimal` verbosity, which an inline
explanation works against. The spec offered its wording as an example ("e.g."), so this stays inside
its latitude, and the substance — *say why, so it is not silently reverted* — is met and
test-asserted (`test_the_reason_is_recorded_inline`).
