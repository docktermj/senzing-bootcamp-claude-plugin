# System verification Step 5 hits the javax.json build gap that `java-scaffold-json-dependency-gap` only fixed in three other modules

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Following System verification (Module 3) Step 4 and Step 5 exactly as written, for a Java
bootcamp, hits the same `javax.json` (JSON-P) build failure that `specs/java-scaffold-json-dependency-gap.md`
already diagnosed and fixed — but the fix never reached this module.

Step 4 calls `generate_scaffold(language='java', workflow='full_pipeline')` and, per its own
correct instruction, picks the loading snippet that reads an external file rather than the
hardcoded demo — `loading/LoadViaLoop.java`. Fetched fresh today and compiled exactly as
Step 5 specifies (`javac src/system_verification/verify_pipeline.java`, class made
package-private per INV-237):

```text
verify_pipeline.java:4: error: package javax.json does not exist
import javax.json.*;
            ^
verify_pipeline.java:62: error: cannot find symbol
                    JsonObject recordJson
                    ^
  symbol:   class JsonObject
verify_pipeline.java:63: error: cannot find symbol
                        = Json.createReader(new StringReader(line)).readObject();
                          ^
  symbol:   variable Json
verify_pipeline.java:75: error: cannot find symbol
                } catch (JsonException | SzBadInputException e) {
                         ^
  symbol:   class JsonException
4 errors
```

The scaffold `import javax.json.*` and uses `Json.createReader(...)` to pull `DATA_SOURCE` and
`RECORD_ID` out of each line. `javax.json` is not part of the Java SE standard library, is not
present in the stock `senzingsdk-runtime` apt install this session verified (`sz-sdk.jar` and
`/opt/senzing/er/lib` carry no `javax/json` classes), and the bootcamp compiles with plain
`javac` — no Maven or Gradle is ever set up. Step 5 as written has no branch for this: it enforces
a 120-second timeout, reports pass/fail on the compiler's exit code, and its failure guidance
("missing SDK libraries, incorrect PATH, missing build tools") does not name a missing
**non-SDK** dependency, so a bootcamper hitting this reads it as an install problem in the module
that just finished verifying the install.

**This is not a new class of defect — it is the same one already found and fixed, missing one
site.** `specs/java-scaffold-json-dependency-gap.md` (implemented 2026-07-25, commit `b3205b7`)
diagnosed this exact failure against `loading/LoadWithInfoViaFutures.java` and added guidance in
three places: `module-02-sdk-setup/SKILL.md` (the general pattern — verify before compiling, the
safety-asymmetry rule, prefer a dependency-free reader, record the deviation),
`module-06-data-processing/phaseA-build-loading.md` Step 3 (checks scaffold imports before
compiling), and `module-05-data-quality-mapping/phase2-data-mapping.md` Step 13 (the mapper's
JSON reader). **System verification's `phase1-verification.md` is not among the three**, even
though its Step 4 independently calls `generate_scaffold(workflow='full_pipeline')` and its own
instructions steer straight at a loading snippet with the identical `javax.json` dependency.

**The gap is not limited to `LoadViaLoop.java`.** Checking two of its five siblings in the same
`full_pipeline` response, both also import `javax.json` for the identical DATA_SOURCE/RECORD_ID
extraction: `LoadViaFutures.java` (confirmed via `sdk_guide(topic='load', language='java')` in
this same session) and, per the original spec's own citation, `LoadWithInfoViaFutures.java`. So
Step 4's file-selection rule ("pick the snippet that reads an input file") routes toward the
dependency, not away from it — there is no sibling escape hatch here the way there was for the
Step 3 initialization bug found earlier in this same walk.

## Root cause

`module-03-system-verification/phase1-verification.md` Step 4 and Step 5 were written and, per
their own MCP-negative markers, last verified against the server on 2026-08-14 — three weeks
**before** the JSON-P gap was diagnosed and fixed elsewhere (2026-07-25 predates that server-check
date, so the fix existed first; the two dates establish only that Step 4/5 were touched again
afterward without picking up the fix). The fix's own scope statement in its ledger entry names
three files; `module-03-system-verification` was never included, and nothing cross-references it
from there or into it.

## Proposed change

Apply the same three-part pattern the original fix established, at this module's Step 5:

1. **Verify before compiling, not after** (mirroring `module-02-sdk-setup`'s item 1): when the
   Step 4 file-selection logic settles on a loading snippet, check its imports for
   `javax.json`/`jakarta.json` before Step 5 runs `javac`, rather than surfacing the raw compiler
   error.
2. **State the safety asymmetry inline, at the point of the check**: replacing the JSON library is
   safe; altering the Senzing SDK calls (`SzRecordKey.of`, `engine.addRecord`, the flag constant)
   is not. This is the load-bearing sentence from the original fix and the reason it needs
   repeating here rather than only cross-referenced — a bootcamper hitting this in Step 5 is
   reading this file, not Module 2's.
3. **Reuse the dependency-free extractor pattern**, not re-derive it: a narrow top-level
   string-field extractor sufficient for pulling `DATA_SOURCE`/`RECORD_ID` (both simple top-level
   string values in the synthetic `VERIFY` records), applied only to the JSON-**extraction**
   lines — every SDK call stays exactly as the scaffold specified. Point to
   `module-02-sdk-setup/SKILL.md`'s statement of the pattern rather than restating the four-item
   list, per this repo's own citation convention (INV-179 in the original spec's language).
4. **Record the substitution in the saved file's header**, exactly as
   `module-06-data-processing/phaseA-build-loading.md` Step 3 already requires downstream — what
   was substituted and why — so the artifact `src/system_verification/verify_pipeline.java`
   self-documents the deviation rather than silently diverging from the MCP-authoritative
   scaffold.

## Acceptance criteria

- [ ] `phase1-verification.md` Step 5 (or a note at Step 4, wherever the fix judges it belongs)
      states the `javax.json` dependency gap and cross-references
      `module-02-sdk-setup/SKILL.md`'s "MCP Java scaffolds may need a JSON library the install
      does not provide" section rather than duplicating its four-item procedure.
- [ ] A test confirms the cross-reference exists (mirroring however
      `java-scaffold-json-dependency-gap`'s own acceptance criteria were tested for its three
      original sites, if a test was added there — check `tests/` for its guard and extend it
      rather than writing an unrelated new one).
- [ ] Re-running Step 5 against a freshly fetched file-reading loading snippet (any of
      `LoadViaLoop.java`, `LoadViaFutures.java`, `LoadWithInfoViaFutures.java`) compiles cleanly
      under plain `javac` after the documented substitution, with every Senzing SDK call
      unchanged from the scaffold.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      defect itself is Java-specific, but the fix's *shape* (verify-before-compile,
      safety-asymmetry statement, cross-reference rather than duplication) is the same pattern
      already applied at three other sites and should read identically here.

## Affected files

- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — Step 4
  and/or Step 5, per the proposed change above
- `tests/` — extend whatever guard `java-scaffold-json-dependency-gap` added for its three sites,
  if one exists, to cover this fourth site

## Source

- Feedback: none — found by `/dry-run` phase 3 (fast-forward stretch, analysis off) while
  literally executing System verification Steps 4–5 for a Java bootcamp, 2026-08-27 (`Source:
  self-observed (assistant retrospective)`). Like the Step 3 finding earlier in the same walk, a
  build failure that stops the guide from completing a documented step is the fast-forward's one
  named exception (a blocker), so this was written up immediately rather than deferred.
- Priority: **Medium.** It reliably blocks Step 5 for every Java bootcamper who reaches System
  verification (not an edge case — Step 4's own selection rule routes toward the dependency), but
  the fix is already designed, already implemented at three sibling sites, and costs only porting
  the same pattern to a fourth. Not High because the workaround (the same dependency-free
  substitution already sanctioned elsewhere) is immediately available and was successfully applied
  in this walk without needing new design work.
- MCP re-check: **server 1.33.0, 2026-08-27.** `generate_scaffold(language='java',
  workflow='full_pipeline')` called live this session; `LoadViaLoop.java` fetched fresh from its
  own `raw_url` and confirmed to `import javax.json.*`; the stock `senzingsdk-runtime` apt
  install's jars were checked and confirmed to carry no `javax/json` classes (this session's
  earlier `dpkg-query`/`sz-sdk.jar` inspection). The underlying facts `java-scaffold-json-dependency-gap`
  established are re-confirmed current, not stale. No absence claim about the server is made — the
  gap is in this repo's own cross-referencing, not in what the server returns — so `owner-checked:`
  does not apply.
- Upstream: not applicable — not a Senzing MCP server defect; this is a within-repo coverage gap.
- Related specs: `specs/java-scaffold-json-dependency-gap.md` (the original diagnosis and fix,
  whose pattern this spec ports to a fourth site);
  `specs/java-initialize-scaffold-snippet-references-the-wrong-class.md` (the other Java-scaffold
  defect found earlier in the same walk, at Step 3 of this same module — unrelated cause, same
  module, same session)

## Deviations from this spec, and why (2026-08-28)

**None on the diagnosis, and the facts are re-confirmed rather than carried over.** Server
**1.33.0**, 2026-08-28: `generate_scaffold(language='java', workflow='full_pipeline')` re-called,
and every `loading/` snippet it returns fetched fresh from its own `raw_url`. No jar under
`/opt/senzing` contains a `javax/json` class — checked against `sz-sdk.jar` and its two siblings
(environment observation, INV-080/INV-149; OpenJDK 21.0.12).

⚠️ **The gap is wider than the spec measured, in the direction that matters.** The spec checked two
of the loading siblings. All seven were checked here, and **six of the six that read an input file**
import `javax.json`: `LoadViaLoop`, `LoadViaFutures`, `LoadWithInfoViaFutures`, `LoadViaQueue`,
`LoadWithStatsViaLoop`, `LoadTruthSetWithInfoViaLoop`. The **only** snippet without the dependency is
`LoadRecords.java`, which hardcodes its records — the file Step 4 item 2 explicitly forbids picking.
So there is no sibling escape hatch at all: Step 4's selection rule routes toward the dependency by
construction, which is a stronger statement than the spec's "routes toward" and is now what the
shipped text says.

⛔ **Acceptance criterion 2 could not be met as written, and the reason is itself a finding.** It
says to *"extend whatever guard `java-scaffold-json-dependency-gap` added for its three sites, if
one exists"*. **No such guard exists** — `grep` across `tests/` found nothing naming `javax.json`,
JSON-P or that spec before today. The original fix shipped to three modules with no test, which is
exactly why those three sites could not tell anyone a fourth was missing. So a new guard was written
covering **all four** sites rather than only the new one:
`tests/test_java_json_dependency_gap_is_covered.py`, whose site set is derived by scanning for files
that fetch a scaffold and compile Java (INV-246).

**Criterion 3 was runtime-verified, not disclosed.** This machine has `javac` and the installed
`sz-sdk.jar`, so the criterion was actually executed rather than reported as unrunnable:

- As delivered, `LoadViaLoop.java` fails with `package javax.json does not exist` (plus the INV-237
  public-class error the module already covers).
- After the documented substitution — the import removed, the class made package-private, and only
  the two JSON-extraction lines replaced by a dependency-free top-level string reader — it
  **compiles cleanly** under plain `javac -cp .../sz-sdk.jar`.
- Every Senzing SDK call is **byte-identical** to the scaffold, verified by diffing the
  `SzCoreEnvironment.newBuilder` / `env.getEngine` / `SzRecordKey.of` / `engine.addRecord` /
  `SZ_NO_FLAGS` lines between the fetched file and the substituted one. The only remaining
  `javax.json` occurrences are the two header comments recording the deviation, which is what the
  guidance requires.

**One invariant is DEFERRED** — see the ledger entry. The rule now ships at four sites and is
registered nowhere; only the maintainer may sign off on invariant wording, so the drafted text is
recorded rather than registered.

## Invariants introduced

- `INV-279` — A step compiling `generate_scaffold` code MUST verify every import is satisfiable before invoking the compiler, and MUST resolve a non-SDK gap by substituting only non-Senzing code. (recorded in `specs/INVARIANTS.md`, registered 2026-08-28 on the maintainer's
  sign-off, from the wording drafted in this spec's ledger entry and carried over unchanged.)
