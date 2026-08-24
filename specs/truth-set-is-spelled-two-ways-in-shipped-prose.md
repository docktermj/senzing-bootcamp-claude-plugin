# "Truth Set" is spelled two ways in shipped prose

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The shipped plugin spells the dataset both ways: **160 occurrences of "Truth Set"**
against **12 of "TruthSet"**, the one-word form confined to three files. One line
carries both spellings at once —
`module-03-system-verification/phase1-verification.md:596`: "…web-service termination,
**TruthSet** purge, and `## `**Truth Set**…" — which is what makes this drift rather
than a deliberate distinction between a product name and a prose noun.

The twelve:

| File | Lines |
|---|---|
| `module-03-system-verification/phase1-verification.md` | `:46`, `:57`, `:58`, `:181` (×2), `:596` |
| `module-03b-truthset-visualization/SKILL.md` | `:68`, `:74`, `:79`, `:92`, `:94` |
| `module-03-system-verification/SKILL.md` | `:82` |

**Severity is low and the scope is bounded**: all twelve are agent-facing internal prose
(a timeout list, a source-precedence rule, a scope limit, an exclusion rule). None is a
bootcamper-facing string, and none appears inside the module's display name — "Truth Set
visualization" is spelled correctly everywhere the module is named, so INV-079 is not
violated. What it costs is coherence: a reader grepping the plugin for the dataset finds
92% of it, and a rule stated in a spelling the rest of the plugin does not use reads as
being about something else.

## Root cause

Vocabulary drift with no guard. The one-word form is the older spelling — it survives in
the module's **directory** name (`module-03b-truthset-visualization`, correctly lowercase
and permanent, since renaming a skill directory breaks every relative cross-reference) and
in the three files that were written earliest. Later work standardized on the two-word
form, including the shipped example recap (`3642` in the ledger records the residual
"TruthSet-acquisition" being removed from it), but the three files above were never swept,
and nothing asserts a single spelling.

⚠️ **Which spelling is canonical for the DATASET is a Senzing fact, not a repo
decision** (INV-080), and this audit is static — it re-asked no MCP route, so it does not
assert one. What it establishes is only that the plugin currently uses two, and that its
own **module name** is settled internally as two words.

## Proposed change

1. **Confirm the canonical dataset spelling against the live MCP server first** —
   `get_sample_data(source='list')` and `search_docs` name the dataset, and INV-080 makes
   the server the authority. Use whatever it returns.
2. **Sweep the twelve occurrences to that spelling.** Leave the directory name
   `module-03b-truthset-visualization` untouched — it is a path, referenced relatively by
   several files, and lowercase-hyphenated by convention.
3. **Guard it.** A repo-level test (`tests/`, stdlib only) asserting one spelling across
   `plugins/**/*.md`, with the directory-path form and any dated quotation of a server
   response excluded. Without a guard this recurs — it already has once.

## Acceptance criteria

- [ ] Every prose occurrence of the dataset name under `plugins/` uses the single spelling
      the MCP server confirms, with the server's tool, parameters, version and date
      recorded in the ledger entry.
- [ ] `module-03b-truthset-visualization/` and every relative reference to it still
      resolve (the cross-reference sweep stays at zero unresolved).
- [ ] A test fails on a reintroduced second spelling; negative-controlled by
      reintroducing one and confirming red.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Source

`production-readiness-audit`, 2026-08-14, Step 4 (vocabulary is canonical). Found by
sweeping shipped text for terminology retired by later work.

- Establishes no new invariant. ⚠️ If the maintainer wants the spelling *bound* rather
  than merely swept, that is a new invariant and needs their sign-off on the wording —
  INV-079 governs module names only, and reading a dataset spelling into it would widen
  an invariant's meaning in place, which `INVARIANTS.md` rule 2 forbids.

## Deviations from this spec, and why (2026-08-14)

- **The canonical spelling was settled by the server, and it draws a line the spec did not
  anticipate.** Proposed change 1 said to confirm the dataset spelling and use whatever the server
  returns. It returns **both**, systematically: `search_docs` surfaces the Senzing documentation page
  titled "Truth Set Setup" whose prose reads "the Senzing **truth set** demo data" (two words), while
  the one-word form appears only inside identifiers — `truthset_config.g2c`, `truthset_demo.sh`,
  `actual_truthset_key.csv`, and `get_sample_data(dataset='list')`'s key `truthset` / display name
  "Truthset CORD". So the rule implemented is the distinction the corpus itself draws: **prose gets
  two words; identifiers keep their spelling.** That is narrower and more defensible than "sweep to
  one spelling", and it is why the guard excludes identifiers by construction (a negative lookaround
  on identifier characters) rather than by an allowlist.
- **The guard grew a second assertion after a negative control escaped.** The identifier-preservation
  test was a repo-wide presence check, so renaming the token in one file left it present elsewhere
  and passed. A *partial* rename is the actual damage — the progress file written under one spelling
  and read under another — so it now asserts the prose-ified forms exist nowhere.
- **A not-vacuous guard was added** (`test_the_two_word_form_is_actually_present`): the primary
  assertion is an absence, and an absence test passes trivially if the term is ever removed
  wholesale.

## Invariants introduced

- `INV-230` — A Senzing **dataset name** in shipped prose MUST use the spelling Senzing's own
  documentation uses, confirmed against the MCP server rather than chosen (INV-080); the closed-up
  form is reserved for identifiers, and an identifier MUST NOT be rewritten to match prose
  (recorded in `specs/INVARIANTS.md`, maintainer-approved 2026-08-14).
