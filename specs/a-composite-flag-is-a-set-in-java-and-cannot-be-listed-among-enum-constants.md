# A composite flag is a `Set<SzFlag>` in Java and cannot be listed among enum constants, and nothing says so

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Building an explicit flag set for `getEntity` in Java — following the SDK reference's own production
guidance to request exactly the flags whose output is consumed rather than a `*_DEFAULT_FLAGS`
composite — the obvious expression does not compile:

```java
EnumSet.of(SzFlag.SZ_ENTITY_INCLUDE_ENTITY_NAME, ..., SzFlag.SZ_ENTITY_INCLUDE_ALL_RELATIONS)
```

```text
no suitable method found for of(SzFlag,SzFlag,SzFlag,SzFlag,Set<SzFlag>,...)
```

`SZ_ENTITY_INCLUDE_ALL_RELATIONS` is itself a `Set<SzFlag>` composite in the Java binding, and must
be merged with `addAll` rather than listed among enum constants.

Per the entry, `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD', language='java')`
returns composites and individual flags in the **same JSON shape**. `composite_members` is present on
composites and is the only signal; no field or note states the Java type difference.

It costs one compile cycle — but it sits directly on the path the reference itself recommends. The
same response that says *"request exactly the flags whose output you consume"* returns a list in
which some entries cannot be used the way the others can, without saying which. Anyone following
that advice in Java hits it.

## Root cause

⛔ **Unverified — the Senzing MCP server was unreachable at triage time.** The connector requires
authorization and this triage session is non-interactive, so `get_capabilities` could not establish
the server version and `get_sdk_reference(topic='flags', …)` could not be re-asked. **Every Senzing
claim below is carried from the feedback entry, dated 2026-08-25, and must be re-verified before
this spec is implemented.** Do not write any of it into shipped prose on the strength of this spec
alone (INV-080).

What is verifiable offline is the plugin's side, and it confirms the gap is real here too. The
plugin discusses `composite_members` at length and never mentions the binding type:

- `module-07-query-visualize-discover/phase1-query-visualize.md:98` — *"Before parsing an entity
  field out of a response, read the composite's `composite_members` and confirm the flag that
  populates *that* field is in it."*
- `phase1-query-visualize.md:135-145` — the branch for a composite returning **no**
  `composite_members`.
- `phase2-discover.md:194-195` — *"be passed as its members instead — `get_sdk_reference` lists those
  under `composite_members` (`SZ_ENTITY_INCLUDE_ALL_RELATIONS` is the four relation flags; server
  1.32.9, 2026-08-14)."*

That last line is the closest the plugin comes, and it is about *which* members a composite has, for
the purpose of confirming a response field is populated. It never says that in Java the composite
**is** a collection and therefore cannot sit in an `EnumSet.of(...)` argument list.

**INV-132 is the invariant this belongs beside and does not currently cover.** It requires confirming
a *method's parameter shape* for the chosen language binding, and warns that cross-language
documentation is not authoritative for parameter shapes. A flag constant's **type** is the same class
of binding-specific fact — the same name is an enum constant in one binding and a set in another —
and the invariant's wording reaches methods only.

## Proposed change

⛔ **Re-verify first.** Before any prose changes, re-ask
`get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS', language='java')` and
record the server version and date. If the server has since added the binding-type note, this spec
reduces to the plugin-side pointer in item 2 and the upstream report is dropped.

**1. Record the binding-type fact where flags are built, sourced.** In Module 7's flag-composition
guidance, state that a composite may be a **collection** rather than a single constant in the chosen
binding, so it is merged into the set rather than listed among constants — with the Java form
(`addAll`, not `EnumSet.of`) as the worked example. Attribute it to the MCP call that establishes it,
with server version and date (INV-080).

⚠️ **State it as a binding-shape rule, not as a Java rule (INV-002).** The general form — *a
composite's representation is binding-specific; confirm it for the chosen language before composing
a flag set* — is what belongs in the guidance; Java is the illustration.

**2. Extend INV-132's reach, or register a sibling.** The confirm-the-shape-for-your-binding
discipline should cover flag constants and not only method parameters. Prefer a new invariant with a
new ID over editing INV-132, since this is a change of meaning rather than a clarification (per
`INVARIANTS.md` maintenance rule 2).

**3. Report it upstream.** Routed `mcp-server`: the reference returns composites and single flags in
one shape while recommending a usage pattern that only works for one of them. A one-line note on
composite rows naming the binding type would close it. The entry's `Upstream:` field reads *"not yet
offered"*, so this has not been filed.

⛔ **Not sent at this triage.** `submit_feedback` was unreachable for the same reason as the rest of
Step 5. File it when the MCP server is available and the fact has been re-confirmed — and only after
showing the maintainer the exact message, per the skill's Step 8. Submissions are anonymous, so no
reply is possible.

## Acceptance criteria

- [ ] The flag facts are re-verified against a reachable MCP server, and the spec's citations carry
      that server version and date before any prose lands (INV-080).
- [ ] Module 7's flag-composition guidance states that a composite's representation is
      binding-specific and must be confirmed for the chosen language before a flag set is composed,
      with the Java `addAll`-not-`EnumSet.of` case as the worked example.
- [ ] The rule is stated as binding-shape guidance applicable to any language, not as a Java-only
      note (INV-002).
- [ ] An invariant registers the confirm-the-flag-representation-for-your-binding rule, with a new
      ID rather than an edit to INV-132.
- [ ] The upstream report is either sent (with date and category recorded) or explicitly deferred
      with the reason; it is **never** sent under `category='license_request'` (INV-135).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md). ⚠️ The
      compile behavior itself is confirmable only with a live Java SDK — state that in the criterion
      rather than writing a check the offline suite cannot run.

## Affected files

- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  the binding-shape rule, beside the existing `composite_members` guidance
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase2-discover.md` — the
  `SZ_ENTITY_INCLUDE_ALL_RELATIONS` members line gains the representation caveat
- `specs/INVARIANTS.md` — register the flag-representation invariant

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Improvement: SZ_ENTITY_INCLUDE_ALL_RELATIONS is
  a composite Set, not an enum constant, and nothing says so" (2026-08-25, Module: Query, Visualize
  and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: unverified (MCP unreachable at triage time — the Senzing connector requires
  authorization and this session is non-interactive). Intended calls, not run:
  `get_capabilities` for the server version, and
  `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_ALL_RELATIONS', language='java')` for
  the composite's representation. Every Senzing claim here is carried from the entry (2026-08-25) and
  must be re-asked before implementation.
- Upstream: not sent — MCP unreachable at triage. The entry records `not yet offered`, so this
  finding has not been filed; send as `category='feature'` (a documentation coverage gap, not a
  defect) once re-verified and approved by the maintainer.
- Related specs: `specs/why-entities-default-flags-has-no-composite-members.md`,
  `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132),
  `specs/relay-the-default-flags-production-caution.md`,
  `specs/method-default-flags-omit-record-data.md`

## Deviations from this spec, and why (2026-08-26)

Re-verification against MCP server **1.33.0** on **2026-08-26** contradicted this spec's central
absence claim, and the implementation changed shape as a result.

1. **"No field or note states the Java type difference" is false.**
   `get_sdk_reference(topic='parameters', filter='get_entity_by_entity_id', language='java')` returns
   `getEntity(entityId: long, flags: Set<SzFlag>) -> String` plus the warning *"Argument 2 type
   differs across bindings — csharp: `SzFlag?`, java: `Set<SzFlag>`, python: `int`, rust:
   `Option<SzFlags>`, typescript: `bigint`."* The binding type **is** served; this spec's Root cause
   reasoned from `topic='flags'` alone, which is the route that does not carry it. So the shipped
   guidance became a **routing pointer** to `topic='parameters'` rather than a hardcoded Java fact —
   a form that cannot go stale the way a copied type would. The narrower residue (that a composite
   *constant* is itself a collection) is recorded as a routing `MCP-NEGATIVE` marker at
   `phase1-query-visualize.md:177` with `topic='parameters'` as owner.

   Confirmed unchanged: `composite_members` for `SZ_ENTITY_INCLUDE_ALL_RELATIONS` is exactly the four
   relation flags, composites and single flags share one JSON shape, and the production caution still
   recommends requesting only consumed flags.

2. **The plugin already stated this rule, and stated it wrong — that correction was not in scope
   here and shipped anyway.** `phase2-discover.md` (2026-08-14) said *"the composite is a `long`
   bitmask"*. Verified against the installed `sz-sdk.jar` with `javap`, `javac` and `java`
   (2026-08-26, observation-only per INV-080/INV-149 — no MCP route reports a binding's class
   layout): `com.senzing.sdk.SzFlag` is an enum that **also** declares
   `public static final Set<SzFlag>` fields for composites, so
   `SzFlag.SZ_ENTITY_INCLUDE_ALL_RELATIONS` is a `Set<SzFlag>` and is **not** an enum constant;
   the identically-named `long` (value `960`) lives in the *separate plural class*
   `com.senzing.sdk.SzFlags`, which cannot be passed to a `Set<SzFlag>` parameter at all. This spec's
   premise was right and the shipped note was wrong about which class it described. Corrected in
   place; the retracted wording is kept as quoted history.

3. **The compile behavior was runtime-verified, which criterion 6 said was not possible here.**
   A live Java SDK and `javac` are present on this machine, so both arms were compiled:
   `EnumSet.of(..., SzFlag.SZ_ENTITY_INCLUDE_ALL_RELATIONS)` fails with
   `no suitable method found for of(SzFlag,SzFlag,Set<SzFlag>)`, and the `addAll` form compiles and
   yields six flags — the two named plus the composite's four members.

4. **Criterion 4 (register a new invariant) is NOT met — deferred, not skipped.** `implement-spec`
   Step 5 requires maintainer sign-off on invariant wording, and the maintainer was away for this
   run. The two hard rules that shipped, the drafted wording, and the follow-up actions are recorded
   in this spec's `specs/IMPLEMENTED.md` entry under a `DEFERRED INVARIANT` bullet, so the next
   `production-readiness-audit` reads them as known rather than discovering them.

5. **Criterion 5 (upstream report) is deferred, with the reason.** `submit_feedback` requires the
   exact message be shown and confirmed before sending; the maintainer is away. The re-check also
   narrowed what is fileable — the original finding is false, and only the missing
   representation hint / cross-reference on `topic='flags'` rows remains. Draft message and category
   (`feature`, never `license_request` — INV-135) are in the ledger entry.
