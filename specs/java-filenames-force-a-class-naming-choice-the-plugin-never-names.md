# The plugin's `.java` filenames force a class-naming choice it never names

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Java requires a **public** top-level class to live in a file named after it. The plugin prescribes
snake_case `.java` filenames in at least two places, so on the Java path the two requirements
collide and `javac` refuses to compile.

**Instance 1 — System verification, Step 5's build table** (`phase1-verification.md`):

| Language | Build Command |
|---|---|
| Java | `javac src/system_verification/verify_pipeline.java` |

**Instance 2 — Module 5 Phase 2, step 4 Phase B**, which prescribes
`data/mapping/<name>_mapper.<ext>` *and*, in the same list, "Idiomatic style for the chosen
language, DRY principle".

**Observed live, phase-3 dry run, 2026-08-14.** Writing the Meridian CRM mapper to the prescribed
path with an idiomatic Java class name failed at compile:

```text
data/mapping/meridian_crm_mapper.java:24: error: class MeridianCrmMapper is public,
  should be declared in a file named MeridianCrmMapper.java
1 error
```

A guide meeting this has three moves and the plugin names none of them:

1. **Rename the class to match the file** — `class meridian_crm_mapper`, `class verify_pipeline`.
   Compiles, but is not idiomatic Java, which the same instruction asks for. (This is what the walk
   did at System verification, silently, before noticing the general problem.)
2. **Rename the file to match the class** — `MeridianCrmMapper.java`. Idiomatic, but abandons the
   prescribed path, which for Module 5 sits under a ⛔ instructing exact paths and which
   graduation's artifact mapping later reads by name.
3. **Drop `public` from the class.** A package-private top-level class may live in **any** filename,
   so the file keeps `meridian_crm_mapper.java` *and* the class keeps `MeridianCrmMapper`.
   `java -cp build MeridianCrmMapper` still launches it. This satisfies both requirements and is the
   move the plugin should name.

Verified: option 3 compiles clean under `javac -Xlint:all` and runs (14 records mapped).

### Why it matters beyond tidiness

- **It is a hard stop, not a style nit.** The bootcamper's first Java compile of the module fails
  with a message about *class visibility* while the actual cause is a **filename convention two
  documents away**. That is a long way from the fault.
- **It hits the two official non-Python bindings.** Java is affected directly. C# has the weaker
  convention (file name matching the type is conventional, not enforced), so it produces
  non-idiomatic-but-compiling code — the silent version of the same defect. Python, Rust and
  TypeScript are unaffected, which is exactly why a Python-centric reading of these filenames looks
  fine.
- **The plugin already knows this class of problem exists for Java.** Module 2 carries a whole block
  on the `javax.json` dependency the MCP Java scaffolds need and the install does not ship, with a
  rule to "record the deviation in the source header". The filename collision is the same shape —
  a Java-specific fact about generated code that the surrounding instructions do not anticipate —
  and has no such block.

## Root cause

The filenames were written in a Python idiom (`verify_pipeline.py`, `<name>_mapper.py`), where
`snake_case` module names are correct and no class/file coupling exists. The `[ext]` substitution
then carries that idiom into languages where it is wrong. Nothing in the plugin states the Java
consequence, and the one instruction that would have surfaced the tension — "Idiomatic style for the
chosen language" — sits in the same list as the prescribed filename without acknowledging that they
conflict.

## Proposed change

1. **State the reconciliation once, centrally**, in `ground-rules.md` next to the existing
   language-specific guidance (the "MCP Java scaffolds may need a JSON library" material in Module 2
   is the closest sibling, but this binds more than one module, so the ground rules are the right
   home): when a prescribed `.java` filename does not match the class name, declare the top-level
   class **package-private** rather than renaming either. Give the one-line reason (only a *public*
   top-level class is filename-bound) and note that `java -cp <dir> <ClassName>` still launches it.
2. **Point at it from both sites** — System verification's Step 5 build table and Module 5's Phase B
   file-naming instruction — without restating the rule (INV-183: named at the step that needs it,
   defined once).
3. **Say what C# does differently**, in one clause: the file/type name correspondence is
   conventional there, not enforced, so the prescribed filename compiles but is unidiomatic; the same
   package-private trick does not apply, and the honest guidance is to keep the prescribed filename
   and name the type idiomatically.
4. **Do not change the prescribed filenames.** They are read by other machinery — graduation maps
   screenshots and artifacts by base name, Module 5's relocation rule source-qualifies exactly these
   three Markdown names, and Module 3's Step 5 table is cited by its own tests. Renaming to
   `PascalCase.java` per language would ripple further than the defect warrants.

## Acceptance criteria

1. `ground-rules.md` states the package-private reconciliation for Java with its reason, and notes
   that the launcher command is unaffected.
2. System verification's Step 5 build table and Module 5 Phase B's file-naming instruction each point
   at that statement; neither restates it.
3. The C# case is addressed in one clause, distinguishing "conventional" from "enforced".
4. No prescribed filename changes; a test asserts `verify_pipeline.java` and the
   `<name>_mapper.<ext>` pattern both survive.
5. A test asserts that every place prescribing a `.java` filename is reachable from the
   reconciliation statement — negative-controlled by removing the statement, which must fail.
6. Python, Rust and TypeScript guidance is unchanged (they have no such coupling).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md`
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md`
- `plugins/senzing-bootcamp/skills/module-05-data-quality-mapping/phase2-data-mapping.md`
- `tests/test_java_filename_class_reconciliation.py` (new)
- `specs/IMPLEMENTED.md`

## Source

- Feedback: none — found by `/dry-run` phase 3 on 2026-08-14, hit twice in one walk: silently worked
  around at System verification (class renamed to `verify_pipeline` to match the prescribed file),
  then diagnosed at Module 5 Phase 2 step 4 when `javac` refused
  `meridian_crm_mapper.java` containing `public class MeridianCrmMapper`
  (`Source: self-observed (assistant retrospective)`). Option 3 was then verified: compiles under
  `javac -Xlint:all`, runs, 14 records mapped.
- Priority: **Low-Medium.** It breaks a documented path on the Java binding — a compile error at the
  bootcamper's first build of the module — but every workaround is one line and a competent guide
  will find one. What the plugin loses by staying silent is consistency: the same run produced a
  snake_case Java class in one module and an idiomatic one in another, both "following the
  instructions".
- MCP re-check: n/a (a Java language rule, not a Senzing fact). Server version this session is
  **1.32.9** (`get_capabilities`, 2026-08-14).

## Invariants introduced

- `INV-237` — Where the plugin prescribes a `snake_case` filename that a chosen language couples to
  a type name, the reconciliation MUST be stated centrally and pointed at from every prescribing
  site, and MUST NOT be resolved by renaming the file or the type (recorded in
  `specs/INVARIANTS.md`).

## Deviations from this spec, and why (2026-08-14)

- **Both language claims were verified empirically rather than taken from this spec**, since the
  whole fix rests on them. On **javac/java 21.0.11**: `public class MeridianCrmMapper` in
  `meridian_crm_mapper.java` reproduces the reported error verbatim; the package-private form
  compiles clean under `javac -Xlint:all`; and `java -cp build MeridianCrmMapper` runs. On
  **.NET 8**: `public class MeridianCrmMapper` in `meridian_crm_mapper.cs` builds with 0 warnings
  and 0 errors, confirming the file/type correspondence is conventional rather than enforced. Option
  3 is therefore confirmed, and so is the C# clause the spec asked for in one sentence.
- **Instance 2's site is not where the spec says it is.** The spec attributes
  `data/mapping/<name>_mapper.<ext>` to "Module 5 Phase 2, step 4 Phase B" — but that path is
  prescribed by **`mapping_workflow`'s own step-4 instructions**, which the guide follows at that
  point; the plugin's own prescription in that module is step 13's
  `src/transform/transform_[name].[ext]`. The pointer was therefore placed at **step 13**, and it
  says explicitly that the rule "applies equally to the `<name>_mapper.<ext>` the workflow's own
  step 4 asks for", so both the plugin-prescribed and the tool-prescribed filename are covered.
  Nothing was invented to make the spec's description true.
- **Two mutations escaped on the first attempt because the mutation was partial, not because the
  guard was weak.** Replacing only the bold lead of each ⛔ left the pointer prose (and, in
  `ground-rules.md`, the second phrasing of the rule) in place, so the assertions still matched.
  Re-run as whole-statement deletions, both are caught — the central-statement control by three
  tests and the mapping pointer by two. Recorded because a mutation that does not actually remove
  the behaviour proves nothing, and reporting it as an escape would have been the wrong conclusion.
