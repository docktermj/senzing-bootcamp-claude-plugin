# "Agent Rule N" citations are positional and one crosses a module boundary

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two shipped files cite their authority as **"Agent Rule N"** — a bare ordinal into a numbered list
that lives in a third file, in a different module's phase document. Neither citation names the file
it points into, so neither can be resolved from where it is read:

- `module-03b-truthset-visualization/phase1-visualization.md:175` — "Save the load artifacts under
  `src/system_verification/` (Agent Rule 5)."
- `module-03-system-verification/SKILL.md:92` — "System Verification starts **no** web service
  (Agent Rule 9)."

The list is defined at `module-03-system-verification/phase1-verification.md:51`, under the heading
"## Agent Rules" and the preamble *"The following rules are mandatory for the agent executing **this
module**"*.

The cross-module case is the sharp one. `module-03b` is the **Truth Set visualization** module,
which INV-087 makes standalone and separate from System Verification. It cites, as its authority for
where to save Truth Set load artifacts, a rule scoped by its own preamble to a *different* module —
and one sitting in a list whose **Rule 1** reads: *"System Verification MUST NOT acquire, load, or
visualize the Senzing Truth Set … (The Truth Set belongs exclusively to the separate, standalone
**Truth Set visualization** module.)"* So `module-03b` derives its instruction from a ruleset that
explicitly disclaims jurisdiction over what `module-03b` does.

## Root cause

**The placement is correct; the cited authority is not.** Truth Set load artifacts really do belong
under `src/system_verification/` — but the rule that says so is **INV-050** (the project-layout
tree), and the list's own **Rule 8** is where that is written down, citing INV-050 and INV-087 by ID:

> 8. **Overwrite on re-run:** … but leave any Truth Set visualization artifacts untouched (its
>    `truthset_data.jsonl` and load/registration code in `src/system_verification/`, and its
>    visualization server under `src/server/`, INV-050) …

So `phase1-visualization.md:175` cites **Rule 5** ("Artifact isolation: all *verification* artifacts
… MUST be created within `src/system_verification/`") when the governing rule is INV-050, restated
at Rule 8. Rule 5 governs System Verification's own artifacts; the sentence it is attached to is
about the Truth Set's.

Two structural properties make this worse than a one-off mis-citation:

1. **The reference is positional, so it is silently re-pointed by any edit to the list.** That is
   not hypothetical here: `specs/module3-synthetic-verification-data.md` records rewriting this
   exact list (*"rewrite Agent Rules (`:86-92`)"*) when Module 3 moved from Truth Set to synthetic
   verification data. Both external citations survived that rewrite still resolving to plausible
   rules — by luck, not by construction. Nothing re-checked them and nothing would have failed.
2. **It is unreachable at the point of use**, which is what INV-183 exists to prevent: a guide
   executing `module-03b/phase1-visualization.md` has no way to look up "Agent Rule 5". Every other
   cross-file reference in the corpus names its file; a sweep for `(Rule N)` / `per Rule N` returns
   exactly these two sites, and a sweep for `see Step N` / `per Step N` with no file named returns
   none.

`citations.py verify` cannot see this — it resolves `INV-NNN` IDs, and "Agent Rule 5" is not one.

## Proposed change

1. **`module-03b-truthset-visualization/phase1-visualization.md:175`** — cite the rule that actually
   governs, by ID, at the step: replace "(Agent Rule 5)" with a reference to **INV-050** (the layout
   tree places the Truth Set's load artifacts there) and **INV-087** (the modules are separate, which
   is *why* one module's artifacts land in the other's directory and must survive its re-runs).
   Point to `module-03-system-verification/phase1-verification.md` → Agent Rule 8 for the
   don't-overwrite guarantee if a prose pointer is still wanted — named by file, not by ordinal.
2. **`module-03-system-verification/SKILL.md:92`** — same module, so the reference is resolvable in
   principle, but make it non-positional: name the file and the rule's subject rather than its
   number ("`phase1-verification.md` → Agent Rules, *No orphaned processes*"), or cite INV-087,
   which is the registered rule that separates the two modules' web services.
3. **Do not renumber or restructure the Agent Rules list.** The fix is at the citing sites; touching
   the list is what re-points ordinals.

## Acceptance criteria

- [ ] No shipped file cites an "Agent Rule N" ordinal from a file other than the one that defines
      the list.
- [ ] `phase1-visualization.md`'s artifact-placement sentence cites INV-050 (and INV-087), reachable
      at that step per INV-183, rather than a rule scoped to System Verification.
- [ ] Any surviving prose pointer into the Agent Rules names its **file** and the rule's **subject**,
      never a bare ordinal.
- [ ] The Agent Rules list at `phase1-verification.md:51` is unchanged in content and numbering.
- [ ] A test derives its site set by **scanning** shipped Markdown for bare-ordinal rule citations
      (INV-246 — never a hardcoded path list) and fails on any that names no defining file —
      **negative-controlled**, mutation verified to land, then reverted.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-03b-truthset-visualization/phase1-visualization.md` — `:175`, the cross-module citation.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/SKILL.md` — `:92`, the positional citation.
- `tests/test_rule_citations_name_their_file.py` — new.

## Source

- Feedback: none — `production-readiness-audit` 2026-08-15, found by a drifted-near-duplicate scan
  across shipped files that surfaced the same MCP-first instruction carrying "(Agent Rule 7)" at one
  site and not at its twin (`Source: self-observed (assistant retrospective)`).
- Priority: **Medium**. Nothing breaks today — the artifact placement the sentence prescribes is
  correct. The exposure is that a positional cross-module citation is re-pointed silently by any
  edit to a list that has already been rewritten once, and that a guide cannot resolve the reference
  at the step where it must act.
- MCP re-check: **n/a (no Senzing fact).** Entirely internal cross-reference integrity between the
  plugin's own files; no MCP tool was called and no Senzing claim is asserted. Server **1.32.9**
  recorded this session (`get_capabilities`, 2026-08-15) to date the run.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `module3-synthetic-verification-data` (rewrote the Agent Rules list without
  re-checking its external citations), `final-review-doc-coherence` (the prior stale-citation
  sweep, which looked at `INV-NNN` references only), and INV-050, INV-087, INV-183, INV-246.
