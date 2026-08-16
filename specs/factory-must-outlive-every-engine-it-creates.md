# State that the Senzing factory must outlive every engine it creates

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A helper that created the factory in a local variable and returned only the engine failed on the
engine's first use:

```text
SzSdkError - engine object has been destroyed and can no longer be used, create a new one
```

The factory was garbage-collected when the helper returned, taking the engine with it. Holding the
factory for the process lifetime fixed it.

Two things make this costly out of proportion to its size. The failure appears at the **first engine
call**, far from the line that caused it — the helper that returned the engine looked fine and
returned successfully. And the message says the engine "has been destroyed", which reads as
*something explicitly destroyed it*, sending the reader looking for a `destroy()`/`close()` call that
does not exist. Factoring engine creation into a helper is the first thing anyone does when writing
more than one script, so the bootcamper meets this exactly when they start writing their own code.

## Root cause

The plugin knows this rule and never tells the bootcamper. It appears only inside implementation the
bootcamper does not read:

- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1276-1280` — a code comment on
  `build_model`: "Keep the factory alive for the caller's lifetime: if it is garbage …", which is why
  the function returns `factory` alongside `engine` at `:1295`.
- `plugins/senzing-bootcamp/scripts/senzing_viz_server.py:1486-1487` — `_ = factory` with the
  comment "`factory` must stay referenced for the whole run so the engine survives".
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md:268` — "initialize the
  factory/environment once per process", inside a **sample recap's narrative**. That is an example
  deliverable, not guidance anyone follows.

A grep for `factory` across every skill file returns **nothing**. The bundled reference server had to
solve this to work at all, and the solution stayed in its comments.

The related rule the plugin does have — one factory per process, for thread-safety — is the same
constraint seen from another angle. Object lifetime is the angle a bootcamper hits first, and it is
the one that is missing.

## Proposed change

1. **Add the rule where SDK code is written.** One line in the ground rules' SDK guidance: the
   factory (environment) must outlive every engine it creates — never let it fall out of scope. In a
   garbage-collected language, a helper that constructs a factory locally and returns only the engine
   returns a dead engine. Hold the factory for the process lifetime, or return it alongside whatever
   it created.

2. **Name the symptom, so it is searchable.** Record the error text verbatim
   (`engine object has been destroyed and can no longer be used, create a new one`) with the note
   that it usually means *collected*, not *explicitly destroyed*, and that the cause is at factory
   creation, not at the failing call. Confirm the wording against the installed SDK at
   implementation time rather than carrying it from this spec (INV-080).

3. **Frame it as ownership, not as a Python idiom** (INV-002). The requirement is that the factory's
   lifetime encloses every engine's; how a language expresses that — holding a reference, a field, a
   context manager, `using`/`try-with-resources` scoping — is the implementer's choice.

4. **Point at the reference implementation.** `senzing_viz_server.py:1276-1295` already does it
   correctly by returning the factory with the engine. Cite it as the worked example so the guidance
   has something concrete behind it.

## Acceptance criteria

- [ ] The ground rules state that the factory must outlive every engine it creates, and that a helper
      returning only the engine is the common way to violate it.
- [ ] The destroyed-engine error text is recorded with its real cause (collection, not explicit
      destruction) and the note that it surfaces far from the offending line.
- [ ] The rule is stated language-agnostically, with the Python garbage-collection case as the named
      instance rather than the rule itself.
- [ ] The modules that write engine-using code (Data processing, Query, Visualize and Discover) reach
      the rule from where the code is written — directly or by reference to the ground rules.
- [ ] A grep for the factory-lifetime rule across the skills returns a non-zero number of references.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — the factory-lifetime rule
  beside the existing SDK-usage discipline.
- `plugins/senzing-bootcamp/skills/module-06-data-processing/phaseA-build-loading.md` — reference it
  where the loading program is structured into helpers.
- `plugins/senzing-bootcamp/skills/module-07-query-visualize-discover/phase1-query-visualize.md` —
  reference it where query code is first written.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "holding the Senzing factory in a local variable
  destroys the engine on return" (2026-07-26, Module Query, Visualize and Discover;
  `Source: self-observed (assistant retrospective)`; `Routing: plugin — a documentation gap; the SDK
  behavior is reasonable`)
- Priority: Low
- Related specs: `specs/verify-sdk-parameter-shapes-and-flag-families.md` (INV-132 — the sibling
  rule for call shapes), `specs/lookup-sdk-response-schemas-before-parsing.md` (INV-115),
  `specs/mcp-grounding-in-every-skill.md` (INV-080 — confirm the error text from the installed SDK)

## Invariants introduced

- `INV-152` — The Senzing factory MUST outlive every engine it creates; a helper returning only the
  engine returns a dead engine (recorded in `specs/INVARIANTS.md`).
