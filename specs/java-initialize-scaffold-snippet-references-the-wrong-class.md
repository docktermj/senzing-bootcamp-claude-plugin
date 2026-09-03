# `generate_scaffold(language='java', workflow='initialize')`'s `EnvironmentAndHubs.java` does not compile — upstream

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Following System verification Step 3 exactly as written — call `generate_scaffold(workflow='initialize')`
in the chosen language, fetch each snippet's `raw_url` per its own `access_steps`, save it, execute
it — produces a file that does not compile, for the Java binding.

`generate_scaffold(language='java', workflow='initialize')` returns five snippets, one of them
`java/snippets/initialization/EnvironmentAndHubs.java`. Fetched fresh today from its own `raw_url`
(`https://raw.githubusercontent.com/senzing/code-snippets-v4/main/java/snippets/initialization/EnvironmentAndHubs.java`)
and compiled with `javac` against the installed `sz-sdk.jar`:

```text
build/initialization/EnvironmentAndHubs.java:20: error: cannot find symbol
        String instanceName = EnginePriming.class.getSimpleName();
                              ^
  symbol:   class EnginePriming
  location: class EnvironmentAndHubs
1 error
```

The file is `public class EnvironmentAndHubs`, but line 20 self-references a **different** class,
`EnginePriming` — which is not imported and does not exist in this file, so the reference cannot
resolve under any classpath. This is not a missing-dependency or environment problem; the file is
malformed as delivered.

## Root cause

Not in this repo — the defect is in the `senzing/code-snippets-v4` GitHub repository that
`generate_scaffold` indexes and serves verbatim (per the tool's own description: "real, compilable
code snippets extracted from official GitHub repositories with source attribution").

**Confirmed as a copy-paste artifact, not an isolated typo.** `EnvironmentAndHubs.java` and its
sibling `EnginePriming.java` (same `initialize` workflow, same `package initialization;`) are
near-identical — same settings/null-check/instance-name/build shape. `EnginePriming.java`'s own
self-reference is correct: `String instanceName = EnginePriming.class.getSimpleName();`
(confirmed by fetching it directly). `EnvironmentAndHubs.java` was evidently derived from it by
copying the file and renaming the public class, but the internal self-reference on the
instance-name line was never updated to match.

**Every other Java snippet in the same two workflow groups gets this right** — confirmed by
fetching and checking all three siblings returned alongside it:

| File | Class | Self-reference |
|---|---|---|
| `PurgeRepository.java` | `PurgeRepository` | `PurgeRepository.class.getSimpleName()` — correct |
| `InitDefaultConfig.java` | `InitDefaultConfig` | `InitDefaultConfig.class.getSimpleName()` — correct |
| `RegisterDataSources.java` | `RegisterDataSources` | `RegisterDataSources.class.getSimpleName()` — correct |
| `EnvironmentAndHubs.java` | `EnvironmentAndHubs` | `EnginePriming.class.getSimpleName()` — **wrong** |

So the defect is isolated to this one file, not a pattern across the workflow — which makes it a
one-line upstream fix (`EnginePriming` → `EnvironmentAndHubs`) rather than a systemic template
problem.

**The plugin's own instructions are not at fault.** `phase1-verification.md` Step 3 already tells
the guide to fetch and execute the snippet exactly as the server returns it, and separately (Step 4)
already warns, for a *different* reason, not to trust the naive checks a listing satisfies. Nothing
in the plugin invented or introduced this bug; it surfaces only when the exact documented procedure
is executed against the live server, which is what this dry run did.

## Proposed change

1. **No plugin-file change is indicated.** `phase1-verification.md` Step 3 already does everything
   right: it fetches by `raw_url`, executes, and has a failure branch ("If the script exits
   non-zero... report fail"). A compile failure before execution is the same branch, one step
   earlier; the module's language is general enough to cover it, and adding Java-specific
   knowledge of this one file's brokenness to the plugin would be exactly the kind of upstream
   patching `INV-080`/`INV-169` warn against — the fix belongs at the source, not encoded here.
2. **Report upstream** (maintainer's call, and **not** to be sent by a dry run — see Source): the
   one-line fix is renaming `EnginePriming` to `EnvironmentAndHubs` on line 20 of
   `code-snippets-v4/java/snippets/initialization/EnvironmentAndHubs.java`.
3. **If the maintainer wants defense-in-depth despite (1):** Step 3's failure branch could
   explicitly acknowledge a compile-time (not just runtime/SENZ-code) failure as a valid "script
   exits non-zero" case and instruct calling `generate_scaffold` again or trying a sibling snippet
   from the same workflow rather than hand-patching the fetched file — hand-patching a
   server-provided snippet is exactly the "reconstruct from memory" shape INV-080 forbids, so if
   this needs a documented recovery path, it should be "re-fetch / try the next snippet", not "fix
   the code yourself." This is optional; acceptance criteria below do not require it.

## Acceptance criteria

- [ ] The one-line upstream fix is reported (see Source — deferred, needs maintainer approval).
- [ ] If the maintainer chooses option 3 above: `phase1-verification.md` Step 3 states plainly that
      a compile-time failure in a compiled language counts as "script exits non-zero" for the
      purposes of its failure branch, and that the recovery is re-fetching or trying a sibling
      snippet from the same `generate_scaffold` response — never hand-editing the fetched file.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — though
      the defect itself is Java-specific; the other four bindings' `initialize`-workflow snippets
      were not each individually re-verified this run (see Source below).

## Affected files

- None in this repo, if acceptance criterion 1 (no plugin change) is what the maintainer decides.
- `plugins/senzing-bootcamp/skills/module-03-system-verification/phase1-verification.md` — Step 3,
  only if the maintainer chooses the defense-in-depth option.

## Source

- Feedback: none — found by `/dry-run` phase 3 (fast-forward stretch, analysis off) while
  literally executing System verification Step 3 for a Java bootcamp, 2026-08-27 (`Source:
  self-observed (assistant retrospective)`). The fast-forward's own rule is "no analysis, let it
  go" with one exception — a blocker that stops the guide from proceeding — and a snippet that will
  not compile as delivered is exactly that exception, so this was written up immediately rather
  than deferred to the analysis stretch.
- Priority: **Medium.** It blocks Step 3 exactly as literally specified for one language, but the
  workaround (skip this one file; the module's *initialization* verification is already covered by
  the other four snippets in the same response, and by Module 2's own initialization check) costs
  nothing and the fix upstream is a one-line rename. Not High because no bootcamper-visible harm
  survives past this one script — the guide (or a human reading the compiler's error) can see
  immediately that the file references a class it does not define.
- MCP re-check: **server 1.33.0, 2026-08-27.** `generate_scaffold(language='java',
  workflow='initialize')` called live this session; `EnvironmentAndHubs.java`,
  `EnginePriming.java`, `PurgeRepository.java`, `InitDefaultConfig.java` and
  `RegisterDataSources.java` all fetched fresh from their own `raw_url`s this session and read
  directly — the defect **reproduces**, and is confirmed isolated to `EnvironmentAndHubs.java`
  among the five. No absence claim is made here (the defect is a positive, reproduced result:
  the file does not compile), so `owner-checked:` does not apply.
- Upstream: **sent 2026-08-27** as `submit_feedback(category='bug')`, on the maintainer's
  explicit approval of the verbatim text — see "Upstream report sent" below.
  Not sent during the dry run itself: ⛔ A dry run must not call
  `submit_feedback` under any category (`.claude/skills/dry-run/SKILL.md`, "Absolute rules"), so
  this was deliberately not filed. The correct upstream target is the `senzing/code-snippets-v4`
  GitHub repository directly (a source-code defect, not something `submit_feedback`'s `bug`
  category is shaped for), which the maintainer may prefer to report by other means entirely.
- Related specs: none — this is the first-recorded defect in a `generate_scaffold` snippet's
  compilability; earlier specs (`refresh-the-initialize-workflow-snippet-count-in-step4`) concerned
  the *count* of snippets returned, not whether any one of them compiles.

## Upstream report sent (2026-08-27)

The maintainer approved the drafted text **verbatim** and it was sent as
`submit_feedback(category='bug')` on 2026-08-27 — a separate, maintainer-authorized action, taken
after the dry run closed and therefore outside the skill's ⛔ on invoking `submit_feedback` during a
run. No text was changed between approval and sending. Nothing identifying was included: the message
carries no name, no email and no local path, and the server states submissions are anonymous in any
case (INV-065).

The server's response records that **submissions are anonymous and cannot be followed up**, so no
reply will arrive and none should be waited for. ⚠️ The defect lives in the `senzing/code-snippets-v4`
GitHub repository, not in the server, so `submit_feedback` reaches the Senzing maintainers but not
the repository's issue tracker directly. The maintainer chose this route knowing that; a GitHub
issue against `code-snippets-v4` remains open as a stronger follow-up if the file is still broken on
a later check. Re-fetch `EnvironmentAndHubs.java` and recompile rather than assuming it was fixed.

## Deviations from this spec, and why (2026-08-28)

**None on content — the claim was re-verified live before the spec was closed.** `get_capabilities`
(server **1.33.0**) and `generate_scaffold(language='java', workflow='initialize')` were re-called on
2026-08-28, and `EnvironmentAndHubs.java` was re-fetched from its own `raw_url`: HTTP 200, 2,315 bytes,
byte-size unchanged, `public class EnvironmentAndHubs` on line 10 and
`String instanceName = EnginePriming.class.getSimpleName();` still on line 20. The defect **still
reproduces** one day after the upstream report was sent; it was not fixed in the interval.

**The maintainer resolved this spec's one conditional.** Acceptance criterion 2 reads "if the maintainer
chooses option 3 above", and on 2026-08-28 they chose not to — the spec closes as **no plugin change**,
which is criterion 1 and what the spec's own `## Proposed change` item 1 recommends. The optional
defense-in-depth wording for `phase1-verification.md` Step 3 was therefore **not** written. That is the
conditional resolving, not a departure from the plan.

⚠️ **What remains true and unfixed.** The upstream defect is live, and `submit_feedback` is anonymous
with no follow-up, so nothing will report back. A GitHub issue against `senzing/code-snippets-v4` stays
available as the follow-up that can actually be tracked. Re-fetch and recompile rather than assuming a
later server version carries a fixed file.
