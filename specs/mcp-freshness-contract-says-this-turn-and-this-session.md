# MCP freshness contract says both "this turn" and "this session"

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

The plugin states the MCP-first freshness requirement two different ways and never
reconciles them, so a guide cannot tell whether an MCP result retrieved earlier in
the session may be presented now, or whether a fresh call is required on every turn
that mentions a Senzing specific.

The cost lands on both sides. Read as "this turn", a long module re-issues
identical queries every turn a Senzing name appears — measurable waste against a
rule that claims ⛔-gate precedence, so it is not one a careful guide feels free to
economize on. Read as "this session", the guide presents Senzing content on a turn
with no MCP call, which the pre-response checklist in all thirteen skill files
forbids, and which also breaks the attribution rule that permits crediting the MCP
server only for what "an MCP tool actually produced **this turn**".

## Root cause

Two vocabularies, neither defined:

- **"this turn"** — the pre-response checklist, present in the MCP-grounding
  frontmatter of all thirteen skill files and stated again at
  `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md:96-98`:
  "if your response contains Senzing SDK method names, attribute names, config
  options, error codes, or entity-resolution technical details, you MUST have
  called an MCP tool **this turn** to get them. If not, stop and call it first."
  Reinforced at `ground-rules.md:225`, which allows attributing to the MCP server
  only what a tool "actually produced this turn".
- **"this session"** — ten step-level sites across five module files.

Most of the "this session" uses are **compatible**, because they set a *floor*
rather than a ceiling: they mean "do not trust the literal shipped in this file,
go ask the server at least once this session" —
`module-06-data-processing/phaseA-build-loading.md:97`, `:138`, `:293`;
`module-06-data-processing/phaseD-validation.md:205`, `:267`;
`module-05-data-quality-mapping/phase2-data-mapping.md:749`;
`module-05-data-quality-mapping/phase1-quality-assessment.md:122`;
`module-02-sdk-setup/SKILL.md:615`, `:1247`.

One is **not**, because it reads as a *permission*:
`module-01-business-problem/phase1-discovery.md:23-24` — "Fill those four from
**`search_docs` content returned this session** — never from memory." Presenting
the pattern gallery from a prior turn's results satisfies that sentence and
violates the checklist, on a step whose output also carries an MCP attribution
line.

n/a — no Senzing fact is involved; this is about when a Senzing fact must be
re-fetched.

## Proposed change

Define the vocabulary once in `ground-rules.md`'s MCP-first section, then make
every site use the defined term:

1. **Presentation freshness** — the existing "this turn" rule, unchanged: a reply
   containing a Senzing specific requires an MCP call on that turn. Say
   explicitly that this is what makes the turn's attribution line truthful
   (`ground-rules.md:225`).
2. **Sourcing floor** — a new named term for what the nine compatible sites mean:
   the value must come from the server rather than from the literal shipped in
   the plugin file. Say that a sourcing floor does not relax the presentation
   freshness rule.
3. Rewrite `phase1-discovery.md:23-24` to use the presentation-freshness rule:
   fill the four attributes from `search_docs` content returned **on the turn the
   gallery is presented**, never from memory and never from an earlier turn's
   results.
4. Audit the other nine sites and switch each to the sourcing-floor term, so
   "this session" stops appearing as a freshness claim anywhere.

## Acceptance criteria

- [ ] `ground-rules.md` defines presentation freshness and the sourcing floor as
      distinct named rules, and states that the floor never relaxes the freshness
      rule.
- [ ] `phase1-discovery.md:23-24` no longer permits presenting the gallery from an
      earlier turn's `search_docs` results.
- [ ] No file under `plugins/` uses "this session" as a *freshness* claim; the
      remaining uses are sourcing-floor phrasing under the defined term.
- [ ] A test in the repo-level `tests/` fails if a new "this session" freshness
      phrasing is introduced alongside the "this turn" checklist, and is
      negative-controlled by reintroducing the `phase1-discovery.md` wording.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — define
  both terms in the MCP-first section.
- `plugins/senzing-bootcamp/skills/module-01-business-problem/phase1-discovery.md` —
  the one permission-shaped use; switch to presentation freshness.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md`,
  `module-05-data-quality-mapping/phase1-quality-assessment.md`,
  `module-05-data-quality-mapping/phase2-data-mapping.md`,
  `module-06-data-processing/phaseA-build-loading.md`,
  `module-06-data-processing/phaseD-validation.md` — switch the nine
  sourcing-floor uses to the defined term.

## Source

- Feedback: dry run phase 3, 2026-08-13 — surfaced when Step 3's gallery and Step
  4's follow-up both needed Senzing attribute facts already retrieved two turns
  earlier, and the two rules gave different answers about re-calling
  (`Source: self-observed (assistant retrospective)`)
- Priority: Medium
- MCP re-check: n/a (no Senzing fact)
- Upstream: not applicable
- Related specs: none

## Deviations from this spec, and why (2026-08-14)

- **Twelve sites were rewritten, not nine.** The spec's inventory missed three:
  `module-06-data-processing/phaseA-build-loading.md:136`,
  `module-02-sdk-setup/SKILL.md:631`, and `graduation/SKILL.md:756`. Acceptance criterion 3
  is absolute — *no* file under `plugins/` may use "this session" as a freshness claim — so
  the criterion governed rather than the list.
- **A fourth category turned up that the spec's two-way split does not cover.** Four sites
  were neither presentation-freshness claims nor sourcing floors, but **provenance claims
  about a fact already written into the file** ("Verified this session: `search_docs`
  returns …"). In a shipped file, "this session" there names *the authoring* session, which
  tells the reader nothing and cannot be checked. Those were given a server version and date
  instead of the sourcing-floor term:
  `module-05-data-quality-mapping/phase1-quality-assessment.md:122`,
  `module-02-sdk-setup/SKILL.md:615` and `:1247`, and
  `module-06-data-processing/phaseA-build-loading.md:138`.
- **One of those four had no provenance stamp at all, so it was re-verified live rather than
  re-worded.** The claim that CORD ships both record shapes now reads from a real call:
  `get_sample_data(dataset='london', source='GLOBALDATA')` returns a `FEATURES` array (with
  the raw source columns alongside it at the record root) and
  `get_sample_data(dataset='las-vegas', source='PPP_LOANS')` returns flat root attributes
  and no `FEATURES` array (MCP server 1.32.9, 2026-08-14). The claim holds; only its
  citation was missing.
- **The change spans two commits.** `ground-rules.md`'s half landed in `129b8ce` (the
  sibling `language-gate-does-not-say-where-its-options-render` spec edits the same file and
  was staged first); the rest is `516344f`.
- **An existing test pinned the retired wording.**
  `tests/test_sdk_parameter_shapes.py::test_it_marks_itself_as_needing_per_session_confirmation`
  asserted the literal "Re-confirm both names via MCP this session". Its subject — that the
  worked example must not substitute for the MCP lookup — is unchanged, so it was re-pointed
  at the new phrasing, renamed to drop the retired vocabulary, and additionally asserts the
  old phrasing has not come back.
