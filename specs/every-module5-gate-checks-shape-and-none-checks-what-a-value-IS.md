# Every Module 5 gate confirms a value's shape and none confirms it is the KIND of thing the feature means — two mappings survived all of them and were reversed after the load

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Two mappings passed **every** static gate in Data Quality, Mapping, and Transformation and were
changed after querying the loaded data. Both were caught by the engine, not by the plugin.

**1. `PASSPORT_NUMBER` carrying Japanese issuance notes instead of numbers.** On OPEN-SANCTIONS,
5 of 65 values across 3 records held annotations, e.g.

```text
（1990年11月6日発行、1995年9月13日失効）
```

— an issuance-and-expiry note containing **no passport number at all**. Loaded as a PASSPORT
feature these produced a `-PASSPORT` conflict that **blocked** entity 200025 (OFAC) from resolving
with 700034 (OPEN-SANCTIONS): the same sanctioned individual, with NAME, DOB, ADDRESS,
PLACE_OF_BIRTH and RECORD_TYPE all scoring 100. A confirmed false negative, caused by a mapping
every gate approved.

**2. `THE BEARER` mapped as a person's name.** On ICIJ, 30 records merged into entity 800049 on
`+NAME+ADDRESS`. "The bearer" is the offshore-leaks placeholder for bearer shares — the notation
for *no owner is named*. It was the single most frequent name in the source at **73 occurrences**,
and the profiler had it in plain sight.

**Why this class is worse than a wrong field name.** A wrong field name renders blank and looks
like missing data. These two render as *confident, well-formed features that change resolution
outcomes* — one suppressing a true match, one manufacturing a 30-record entity. The Bootcamper's
deliverables would have shipped both as findings.

## Root cause

**Every Module 5 gate is structural, and the module already says so about a neighboring failure
without generalizing it.** `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md:619-626`:

> ⛔ **The general shape, and the reason every existing gate missed this.** The analyzer, the
> verbatim check and the routing report all confirm the **output matches the plan** and the **plan
> is faithful to the source**. None of them confirms the plan does what the Bootcamper **asked
> for** …

That is the correct diagnosis of a **third** axis. There are three, and the module names two:

| Axis | Question | Checked by |
|---|---|---|
| Structure | is the output what the plan said? | analyzer, routing report |
| Fidelity | is the value faithful to the source? | verbatim check |
| Intent | does the plan do what was asked? | nothing — `:619-626` |
| **Kind** | **is the value the kind of thing this feature means?** | **nothing** |

Applied to case 1: the analyzer saw a well-formed string in a valid attribute; the verbatim check
confirmed it was faithful to the source — **it was, faithfully wrong**; the routing report saw the
field reach a feature. Nothing asks whether a value with no digits in it can be a passport number.

**The existing sentinel guidance is aimed one attribute-family away.** `:430-434` covers null
sentinels as a *completeness* trap —

> ⚠️ **A column's population percentage is not a quality signal when a sentinel token is in use.**
> A null sentinel is a *value*, so the profiler counts it as present: a source using `-0-` for "no
> data" reported **100% population on all 12 columns** when 8 carried no information.

— and `:609-611` names the code-shaped sentinel signature `"XXX; VGB; GBR"`. Both are about codes
and identifiers with recognizable tokens. Case 2's sentinel is a **name**, in prose, and nothing in
the module prompts a check for sentinel values in name fields.

**Senzing already states the rule for case 1, verbatim.** `search_docs(query='do not put dates or
notes in identifier attributes passport number free text', category='data_mapping')` on **server
1.33.0, verified 2026-08-21**, returns the Entity Specification's *Mapping identifiers* section:

> "Some sources use code-driven "identifier" tables for anything lacking a dedicated field. You
> may encounter document dates (e.g., birth-certificate dates), risk categories/statuses, or
> free-text notes. **Do not map these as identifiers (including `OTHER_ID`).** Route to a
> registered feature when appropriate; otherwise use payload attributes or omit when no
> meaningful, spec-compliant placement exists."

and the `PASSPORT` feature's own guidance gives `PASSPORT_NUMBER` the example `123456789` with the
guidance "Passport number." So the rule is not missing from Senzing — **the gates just do not test
for it.** That is the whole of case 1: a documented prohibition with no enforcement anywhere in the
mapping flow.

**For case 2 the specification carries no equivalent rule, and the check must be ours.** The
Entity Specification's `Name > Feature: NAME` section covers object consistency (do not mix
`NAME_FULL` with parsed fields, do not mix `NAME_ORG` with person fields) and `NAME_TYPE`
semantics, and states nothing about placeholder or sentinel name values; the *Mapping identifiers*
and *How to map them* sections likewise. Two further searches over the same route
(`query='placeholder generic name values bearer unknown anonymous do not map'` and
`query='exclude invalid junk values n/a unknown repeated defaults data quality before mapping'`,
both `category='data_mapping'`, same server and date) returned the same sections with no such rule.

## Proposed change

1. **Add a kind check for identifier features at the step-3 mapping gate.** Before an identifier
   feature is accepted, test the values, not the column: a value carrying **no digits at all**, or
   whose script falls outside the range the identifier's issuer would use, is an annotation and not
   an identifier. Present it as a finding at the gate with the offending values, and route it the
   way the Entity Specification says — a registered feature if one fits, else payload, else omit.
   Cite the specification's own sentence so the Bootcamper sees this is Senzing's rule and not the
   bootcamp's opinion.

2. **Add a frequency heuristic for sentinel values in name features.** A name value repeating far
   above the source's own name-frequency distribution is a placeholder until proven otherwise. The
   profiler already computes what is needed — "the single most frequent name at 73 occurrences" was
   available before anything was mapped. Surface the top name values with their counts at the gate
   and ask about any outlier, rather than leaving the Bootcamper to notice a number they were never
   shown. `THE BEARER` is the worked example; the check must not be a hardcoded list of known
   placeholder strings, which would catch this one source and no others (INV-002 framing: the rule
   is distributional, not lexical).

3. **Name the fourth axis where the third is already named.** Extend the `:619-626` block to state
   that the gates verify structure, fidelity and — once implemented — intent, and that **none of
   them verifies semantic kind**, which is what the two checks above add. That block is the right
   home: a reader who has understood why the intent gap exists is one sentence from understanding
   this one.

4. **Do not implement either check by patching the MCP-delivered analyzer** (`:436-437`, INV-173).
   These are gate-time checks in the module's own flow, over the profile and the mapping plan.

## Acceptance criteria

- [ ] The step-3 mapping gate rejects — and reports, with the offending values — an identifier
      feature whose values contain no digits, and cites the Entity Specification's "do not map
      these as identifiers" rule.
- [ ] The gate surfaces the top name values with their occurrence counts, and raises any value whose
      frequency is a distributional outlier as a suspected placeholder.
- [ ] Neither check is implemented as a hardcoded list of known sentinel strings.
- [ ] A record whose only PASSPORT value is a non-Latin free-text note does not reach a PASSPORT
      feature without the Bootcamper having been shown it and decided.
- [ ] `phase2-data-mapping.md:619-626` names semantic kind as a fourth unchecked axis alongside
      intent.
- [ ] Neither check patches `sz_schema_generator.py` (INV-173).
- [ ] The pass/fail behavior is verified against fixtures reproducing both cases; the entity-level
      outcomes (the suppressed 200025↔700034 merge, the 30-record 800049 entity) are noted as
      requiring a live engine and are not asserted by the offline suite.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — the
  step-3 mapping gate gains both checks; the sentinel guidance at `:430-434` and `:609-611` gains
  the name-field case; `:619-626` gains the fourth axis
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase1-quality-assessment.md` —
  the profiler step surfaces top name values with counts, so the frequency check has an input
- `tests/` — fixtures and guards for both checks

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Joel.md` → "Reversed decision: two mappings changed
  after the Discover phase read the engine's output" (2026-08-18, Modules Query, Visualize and
  Discover / Data Quality, Mapping, and Transformation; `Source: agent-observed`)
- Priority: Medium
- MCP re-check: server 1.33.0, 2026-08-21 — **still reproduces**, and the identifier half is
  Senzing's own documented rule.
  `search_docs(query='do not put dates or notes in identifier attributes passport number free
  text', category='data_mapping')` returns the Entity Specification's *Mapping identifiers*
  prohibition verbatim and the `PASSPORT_NUMBER` guidance. For the name-sentinel half the
  specification states no rule: `owner-checked: search_docs(category='data_mapping') over the
  Entity Specification — the route that carries every attribute-level mapping rule, including the
  identifier prohibition this same entry relies on; queried three ways (identifier free-text,
  placeholder/bearer/anonymous names, invalid-value exclusion) and it returns "Name > Feature:
  NAME" (object consistency and NAME_TYPE only), "Mapping usage types", "Mapping identifiers" and
  "How to map them" — none stating a rule about placeholder name values.` The name-frequency
  heuristic is therefore the bootcamp's own check, not a relayed Senzing rule.
- Upstream: not submitted — the identifier rule already exists upstream and needs enforcement here,
  not a report. A feature request that the specification add placeholder-name guidance is defensible
  but was not filed; raise it with the maintainer separately if wanted.
- Related specs: `specs/readiness-gate-acts-on-structure-while-naming-semantics.md`,
  `specs/post-load-match-key-semantic-audit.md`,
  `specs/routing-a-registered-feature-attribute-to-payload-is-silently-a-no-op.md`,
  `specs/capture-reversed-decisions-during-the-run.md`,
  `specs/verbatim-check-cannot-see-field-name-derived-values.md`
