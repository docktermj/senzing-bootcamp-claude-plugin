# A syntax error on a just-written file across a bind mount must be retried before it is believed — and the plugin's own troubleshooting table sends the reader to the wrong hypothesis

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Writing a Python file on a macOS host and immediately running it inside the container produced:

```text
SyntaxError: unterminated string literal
```

at a line that was well-formed. Re-running the identical command moments later succeeded, and
`compile()` inside the container confirmed the file parsed. **The container had read a partially-synced
file** across the Docker Desktop bind mount.

**The misdiagnosis it invites is specific, and the plugin points straight at it.** The container runs
Python 3.11 and the host 3.12, so the first hypothesis was a PEP 701 f-string incompatibility —
plausible, wrong, and it cost a verification round trip. A Bootcamper who reaches the same hypothesis
goes and edits correct code.

**This is not a rare configuration.** The bootcamp writes host-side files and executes them
container-side constantly on the Docker path, which routing rules 1, 2 and 4
(`module-02-sdk-setup/SKILL.md:386-395`) select for Python-on-macOS/Windows, every Intel Mac, and
Windows without Scoop.

## Root cause

Two things, and the second is the plugin's own contribution to the misdiagnosis.

**1. Nothing in the plugin mentions bind-mount propagation lag.** A repository-wide search for
bind-mount, propagation or settle guidance returns nothing on this subject — the only "settle" hits
are about settling a Bootcamper's preferences, and the one screenshot settle-budget note
(`bootcamp-onboarding/module-completion.md:282`) is about a web app redrawing a tab. So a transient
read of a partially-written file has no explanation anywhere, on the path where it can happen many
times per module.

**2. `module-02-sdk-setup/SKILL.md:591` offers a version-mismatch explanation for exactly this
symptom.** Its troubleshooting table row reads:

| `NODE_VERSION` | `SyntaxError` on modern syntax, `ERR_UNSUPPORTED_ESM_URL_SCHEME`, Node.js older than 18 | "Node.js Version Conflicts" |

That row is correct for what it covers and it is the nearest match a reader will find for
"SyntaxError". It teaches the shape *SyntaxError → language runtime is too old*, which is the
hypothesis that cost the round trip — and on the Docker path a host/container version split is always
present and always available as a plausible culprit. The plugin therefore supplies the wrong first
hypothesis and no competing one.

**The routing is `host` and the fix is still ours.** The entry routes this `host` — macOS Docker
Desktop bind-mount propagation, not plugin or server logic — and that is right. ⛔ **`host` has no
upstream channel**: Senzing does not ship Docker Desktop or the Claude Code harness, so nothing here
goes to `submit_feedback`. What the bootcamp owns is what it *says* when this happens: a transient,
convincing error on the path the bootcamp itself selected, with the plugin's only relevant
troubleshooting row pointing elsewhere.

**No Senzing fact is involved.** The propagation behavior is Docker Desktop's, the retry is the
bootcamp's guidance, and the version split is a property of the container the bootcamp builds
(`module-02-sdk-setup/SKILL.md:426`, `debian:bookworm-slim` plus the `linux_apt` steps).

## Proposed change

1. **State the retry rule where host-written files are executed container-side.** A syntax or parse
   error on a file written moments earlier, on the Docker path, is **retried once before it is
   believed**. If the second run succeeds, it was propagation lag, not the code — say so and move on.
   If it fails identically, it is a real error. One retry is the whole rule; do not build a
   backoff loop for a transient that resolves in well under a second.

2. **Give the confirming check, so the retry is not superstition.** Compile the file *inside* the
   container (`python3 -m py_compile <file>`, or the chosen language's equivalent — `node --check`,
   `javac`, `tsc --noEmit`) rather than re-running the whole program. That distinguishes "the file the
   container can see is incomplete" from "the code is wrong" in one cheap step, and it is the check
   that actually settled it on the run. The plugin already requires syntax-checking generated tools
   before trusting them (`mapping_workflow` step 4's TOOL DISCIPLINE), so this is the same discipline
   applied to a transient rather than to a bug.

3. **Disarm the version hypothesis explicitly, next to the retry rule.** Say that a host/container
   language-version split is normal on this path and is **not** the first explanation for a syntax
   error on a just-written file — ordering matters here, because the version story is more
   satisfying and arrives first. Where a version incompatibility *is* real, it reproduces on retry,
   which is what makes the retry the correct discriminator rather than a way of avoiding the question.

4. **Cross-reference the `NODE_VERSION` troubleshooting row** (`:591`) so a reader who lands there
   from "SyntaxError" is sent to the retry rule first on the Docker path. Do not weaken the row — it
   is right about genuinely old runtimes.

5. **Consider a settle in the run helper, but do not require it.** A brief settle before executing a
   just-written file would remove the symptom rather than explain it. It is the smaller behavioral
   change and it hides the cause from the next person; the guidance is what generalizes. If a settle
   is added, keep the retry rule too — a fixed wait asserts nothing, which is the same reason the
   teardown contract polls the port instead of sleeping.

## Acceptance criteria

- [ ] The Docker path's guidance states that a syntax or parse error on a just-written file is
      retried once before being believed, and what each outcome means.
- [ ] The in-container compile check is given as the discriminator, in the Bootcamper's chosen
      language rather than Python only.
- [ ] The guidance says a host/container version split is normal on this path and is not the first
      explanation for this symptom, and that a real incompatibility reproduces on retry.
- [ ] The `NODE_VERSION` troubleshooting row (`:591`) cross-references the retry rule for the Docker
      path, and is otherwise unchanged.
- [ ] No fixed sleep is introduced as the sole remedy; if a settle is added, the retry rule remains.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — the
      symptom is bind-mount-specific (macOS and Windows Docker Desktop), the rule is written per
      language rather than for Python.

## Affected files

- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — the Docker path (`:420-435`) gains
  the retry rule and the version-hypothesis caveat; the `NODE_VERSION` row (`:591`) gains the
  cross-reference
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — if the rule belongs with the
  other cross-cutting execution guidance rather than in one module, since files are written host-side
  and run container-side in several modules

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK_Matthew.md` → "Improvement: Docker bind-mount lag on
  macOS makes a just-written script fail with a phantom SyntaxError" (2026-08-18, Module Query,
  Visualize and Discover; `Source: self-observed (assistant retrospective)`)
- Priority: Low
- MCP re-check: n/a (no Senzing fact) — the propagation behavior is Docker Desktop's, and the
  misleading troubleshooting row and missing guidance are the plugin's. Confirmed in the codebase:
  no shipped file mentions bind-mount propagation, and `module-02-sdk-setup/SKILL.md:591` maps
  `SyntaxError` to a Node.js version conflict.
- Upstream: not applicable — the entry routes this `host`, and `submit_feedback` reaches Senzing,
  which ships neither Docker Desktop nor the harness. Step 8 skipped by rule, not by choice.
- Related specs: `specs/container-lifecycle-hooks-assume-docker.md`,
  `specs/docker-container-lifecycle-teardown-and-resume.md`,
  `specs/bytecode-caching-hides-a-latent-syntax-error-from-the-suite.md`,
  `specs/feedback-routing-has-no-verdict-for-a-defect-neither-component-owns.md`
