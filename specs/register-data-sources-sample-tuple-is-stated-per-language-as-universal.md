# The register-data-sources sample tuple is a Python detail stated as universal

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`phaseA-build-loading.md`'s Step 4a warns that `sdk_guide(topic='configure', data_sources=[…])`
selects the registration snippet but substitutes nothing, and tells the guide what the returned
code contains:

> But the returned code still hardcodes the sample tuple `("CUSTOMERS", "REFERENCE",
> "WATCHLIST")`, and its own `notes` say *"Replace sample data source names with your own"*

That tuple is the **Python** snippet's. The **Java** snippet ships a different one. Measured on
MCP server **1.36.0, 2026-09-02**, calling
`sdk_guide(topic='configure', language='java', data_sources=['RETAIL_POS','LOYALTY_APP','SUPPORT_TICKETS'])`:

```java
// create an array of the data sources to add
String[] dataSources = {"CUSTOMERS", "EMPLOYEES", "WATCHLIST"};
```

`EMPLOYEES`, not `REFERENCE`. A Bootcamper on Java — or a guide following the step literally on
Java — is told to look for a tuple that is not in the response they received.

The **rule** the ⛔ states is correct and reproduced exactly on Java: `data_sources` made
`RegisterDataSources.java` primary (`source_path: java/snippets/configuration/RegisterDataSources.java`,
with `InitDefaultConfig` demoted to `alternatives`), none of the three supplied codes appeared
anywhere in the response, and `notes` carried *"Replace sample data source names with your own"*
verbatim. Only the illustrative tuple is wrong for this language.

⚠️ **A second per-language divergence sits in the same pair of snippets and is not mentioned at
all.** The two languages use different config-replacement mechanics:

| | Python (`register_data_sources.py`) | Java (`RegisterDataSources.java`) |
|---|---|---|
| replace mechanism | `register_config()` then `replace_default_config_id(current, new)` | same pair, **wrapped in a retry loop** |
| conflict handling | none in the snippet | `catch (SzReplaceConflictException)` and re-read the current default config id |

The Java snippet is the more defensive of the two, and the step's prose describes neither. A guide
that "substitutes the codes into the snippet" is fine either way, but a reader comparing the two
languages has no warning that the shapes differ.

## Root cause

`plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md:319-326`. The ⛔
was verified against Python — the block says so in its own closing parenthetical, *"(Re-verified
with the three codes passed explicitly: `sdk_guide(topic='configure', language='python',
data_sources=[…])`, server **1.33.0, 2026-08-21**.)"* — and the same block states the tuple
without repeating that scoping. The MCP-NEGATIVE marker immediately above it is correctly scoped to
`language='python'`; the prose beneath it is not.

This is the failure mode INV-002 and INV-090 exist for, arriving through an *illustration* rather
than through an instruction: the surrounding step is careful to read `programming_language` from
preferences and never hardcode a language, and then hands the guide a language-specific literal to
match against.

## Proposed change

1. **Scope the tuple to the language it came from.** Either name it as Python's
   (`("CUSTOMERS", "REFERENCE", "WATCHLIST")` — Python; `{"CUSTOMERS", "EMPLOYEES", "WATCHLIST"}` —
   Java), or drop the literal entirely and state the discriminating property instead: *the returned
   snippet hardcodes a sample tuple of Senzing's own demo data source codes, and none of the codes
   you passed appears anywhere in the response.* ⚠️ Prefer the property — it is what the guide acts
   on, it holds in every language, and it cannot go stale when a snippet is re-authored. This is the
   same census-versus-property choice `.claude/skills/dry-run/phase1-mcp-contracts.md` prescribes
   for negative rationales.
2. **Add one line noting that the replacement mechanics differ per language**, and that the
   substitution rule is unaffected: keep every Senzing method, signature and flag as the snippet has
   them, whichever shape it uses. Do not describe either shape as canonical.
3. Leave the MCP-NEGATIVE marker as it is — it is correctly scoped already.

## Acceptance criteria

- [ ] Step 4a no longer states a sample tuple as though it were language-independent: either each
      language's tuple is named as that language's, or the literal is replaced by the property.
- [ ] Following Step 4a on Java does not send the reader looking for `REFERENCE`.
- [ ] The step notes that the config-replacement shape differs per language (Java wraps the
      replace in an `SzReplaceConflictException` retry loop; Python does not) without ranking them.
- [ ] A test asserts that Step 4a's prose carries no unscoped data-source-code literal — i.e. any
      sample tuple it names is attributed to a language.
- [ ] Negative control: reintroduce the unscoped tuple and confirm the test fails.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — scope or replace the tuple; note the per-language replace mechanics
- `tests/` — new guard for unscoped sample-code literals in Step 4a

## Source

- Feedback: `/dry-run` phase 3, 2026-09-02, Data processing Phase A Step 4a (`Source: self-observed (assistant retrospective)`)
- Priority: Low — the rule the step teaches is correct and was reproduced on Java; only the illustration is wrong for non-Python languages, and a guide that follows the *rule* substitutes correctly regardless
- MCP re-check: **server 1.36.0, 2026-09-02 — server behavior matches the step's rule and contradicts its illustration.** Tools called: `sdk_guide(topic='configure', language='java', data_sources=['RETAIL_POS','LOYALTY_APP','SUPPORT_TICKETS'])` and, earlier in the same session, `sdk_guide(topic='configure', language='java')` with no `data_sources` (which returned `InitDefaultConfig` as primary, confirming the selection half of the rule) and `sdk_guide(topic='configure', language='python', data_sources=[…])`. Not an absence claim about the server — the finding is that the response's literal differs from the plugin's stated literal, read directly from both.
- Upstream: not applicable — the server is behaving as documented; the plugin's illustration is what is out of date.
- Related specs: none

