# Senzing Bootcamp Plugin Feedback

Findings recorded during this bootcamp run. Append only.

## Your Feedback

## Improvement: PyPI `senzing` package silently shadows the SDK-shipped bindings

**Date:** 2026-08-24
**Module:** SDK setup
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the env script Step 3 writes is the place that fixes it; no MCP tool is involved.
**Upstream:** not applicable

### What happened

`import senzing` resolved to a `senzing` package installed under the user's local
site-packages (v4.1.2) rather than the SDK-shipped bindings at
`/opt/senzing/er/sdk/python` (v4.3.4). The import succeeded, so nothing failed
loudly; the wrong version simply answered. It was caught by printing
`senzing.__file__` rather than by any error.

### Why it matters

Step 3's environment script exports `LD_LIBRARY_PATH` but, as written, did not
prepend the SDK's Python path — so on any workstation where the PyPI `senzing`
distribution is installed, every module runs against a different SDK version than
the one the bootcamp just verified. The failure mode is a version skew that
produces plausible output, not an ImportError, which is the hardest class to
notice. Module 2's own Step 1 fallback exists because import checks fail on a
working install; this is the mirror case, where the import *succeeds* wrongly.

### Suggested fix

Have Step 3's env script prepend the SDK path unconditionally:

```bash
export PYTHONPATH="/opt/senzing/er/sdk/python${PYTHONPATH:+:$PYTHONPATH}"
```

and add a Step 4 verification line that prints the resolved `senzing.__file__` and
version, so a shadowing install is reported rather than inferred. Prepending is
the right remedy rather than uninstalling, since the PyPI copy may belong to
another project on the same machine.

### Context when reported

- **Time:** 2026-08-24 14:45 local
- **Plugin version:** 0.5.2
- **Workstation:** Linux 7.0.0-28-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** sdk_setup, step 3 (found), recurring through every later module
- **Recent questions:** SDK setup's database-type question; System verification transition
- **Bootcamper responses:** SQLite; yes
- **Behind the scenes:** `src/scripts/senzing-env.sh` as generated from `sdk_guide(topic='install', platform='linux_apt')` env_vars
- **Observed problem:** `senzing.__file__` pointed at local site-packages v4.1.2, not the 4.3.4 SDK bindings
- **Expected behavior:** the project-local env script makes the installed SDK's bindings authoritative
- **Divergence:** `env_vars` carries `LD_LIBRARY_PATH` but no `PYTHONPATH` entry for the SDK's Python directory, so an unrelated PyPI install wins on `sys.path` order

## Improvement: Entity Graph legend labels per-source participation counts as "Single-source:"

**Date:** 2026-08-24
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — a labelling defect in the bundled visualization server's legend.
**Upstream:** not applicable

### What happened

The Entity Graph legend's second block is headed `Single-source:` and lists
`CRM_CUSTOMERS 65` and `WEBSTORE_ACCOUNTS 70`. Those are per-source
*participation* counts — every entity drawing on that source, including the 14
that draw on both. The arithmetic gives it away: 65 + 70 − 14 = 121, the total
entity count. The true single-source figures are 51 and 56.

### Why it matters

The heading directly above it reads "Entities in more than one source have their
own color", so the two blocks read as a partition of the entity population when
they are not. A bootcamper reading the legend concludes 65 entities are CRM-only.
The numbers are individually correct and the label is what is wrong, which makes
it a defect no plausibility check catches — the figures agree with the counts
shown everywhere else in the app.

### Suggested fix

Either relabel the block `Entities per source:` (keeping the counts), or keep the
`Single-source:` label and subtract the multi-source entities from each count.
The first is less work and arguably more useful, since participation is what the
node colors are keyed on.

### Context when reported

- **Time:** 2026-08-24 14:20 local
- **Plugin version:** 0.5.2
- **Workstation:** Linux 7.0.0-28-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover, step 3c
- **Recent questions:** Would you like an interactive visualization of your results?
- **Bootcamper responses:** yes
- **Behind the scenes:** bundled `scripts/senzing_viz_server.py`, Entity Graph tab legend
- **Observed problem:** legend block headed "Single-source:" listing 65 / 70 against 51 / 56 actual
- **Expected behavior:** a block labelled "Single-source" shows entities present in exactly one source
- **Divergence:** the counts are computed as per-source participation, which double-counts the 14 cross-source entities

## Improvement: `how_entity` omits `MATCH_KEY_DETAILS` under `SZ_INCLUDE_FEATURE_SCORES` alone

**Date:** 2026-08-24
**Module:** Query, Visualize and Discover
**Priority:** Low
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — an observation that strengthens an existing caution in `phase2-discover.md`; nothing to ask the MCP server for.
**Upstream:** not applicable

### What happened

`phase2-discover.md` step 4c instructs generating the `how_entity` call with
`SZ_INCLUDE_FEATURE_SCORES`, and records a 2026-08-18 observation that
`how_entity`'s `MATCH_KEY_DETAILS.CONFIRMATIONS[]` populated on an entity where
`why_records`' equivalent came back empty. On this run (Senzing SDK 4.3.4,
Python), with `SZ_INCLUDE_FEATURE_SCORES` alone, `MATCH_INFO` on the how response
carried only `['CANDIDATE_KEYS', 'ERRULE_CODE', 'FEATURE_SCORES', 'MATCH_KEY']` —
`MATCH_KEY_DETAILS` was **absent**, not empty. On the same entity, the same run,
`why_records` returned `WHY_KEY_DETAILS` populated with three confirmations once
`SZ_INCLUDE_MATCH_KEY_DETAILS | SZ_ENTITY_INCLUDE_ALL_RELATIONS` was passed.

### Why it matters

The step's flag instruction and its observation point in different directions: a
guide following step 4c literally passes only `SZ_INCLUDE_FEATURE_SCORES` and
then finds the breakdown the observation says should be there. Because the step
already forbids rendering an empty section, the correct outcome — stating the
absence and falling back to `FEATURE_SCORES` — is reachable, but the guide has to
reconcile the contradiction under time pressure. This is the same shape as the
why-side ⚠️ the file already carries, one method over.

### Suggested fix

Add this observation beside the existing one in step 4c, with its conditions, and
make the flag instruction pass `SZ_INCLUDE_MATCH_KEY_DETAILS` with a relations
flag on the how call too — matching what step 4b already does for `why_records`.
Per INV-169 the two observations should be recorded side by side rather than
reconciled into one absolute: they were seen on different data and different runs.

### Context when reported

- **Time:** 2026-08-24 14:30 local
- **Plugin version:** 0.5.2
- **Workstation:** Linux 7.0.0-28-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** query_visualize_discover, step 4c
- **Recent questions:** Continue to the next demonstration — How Analysis?
- **Bootcamper responses:** 1 (continue)
- **Behind the scenes:** `how_entity_by_entity_id(200005, SZ_INCLUDE_FEATURE_SCORES)`, dump-before-parse per INV-115
- **Observed problem:** `MATCH_KEY_DETAILS` absent from `HOW_RESULTS.RESOLUTION_STEPS[].MATCH_INFO`
- **Expected behavior:** per the step's recorded 2026-08-18 observation, confirmations populate on the how side
- **Divergence:** the flag was never varied in that observation either; the absence here is consistent with the flag being required on both methods

## Improvement: PostToolUse Markdown hook blocks on rules `ground-rules.md` defers to graduation

**Date:** 2026-08-24
**Module:** General
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — the hook and the ground rule ship together and disagree with each other.
**Upstream:** not applicable

### What happened

The `PostToolUse` Markdown hook rejects writes to `docs/bootcamp_recap.md` for
MD022 (blank lines around headings) and MD032 (blank lines around lists). But
`ground-rules.md` → "Markdown files" explicitly says bootcamp docs are written
plain and that graduation runs a single normalization pass over them, and
`module-completion.md` repeats it: *"Do not spend effort on CommonMark
prettification here … graduation runs one normalization pass over the recap
before the PDF renders."*

### Why it matters

Two shipped components give opposite instructions about the same file, at the
moment of writing it. Following the ground rule means fighting the hook at every
module close; following the hook means hand-formatting eleven recap sections that
`normalize_docs_markdown.py` exists to format in code — and the normalizer's
content guard is the thing that makes the pass safe, so hand-formatting is
strictly worse. I proceeded per the ground rules.

### Suggested fix

Scope the hook to exclude the files graduation normalizes — `docs/bootcamp_recap.md`
at minimum, and arguably all of top-level `docs/*.md`, which is exactly the glob
`normalize_docs_markdown.py` claims. `docs/REVISIT_BOOTCAMP.md` is the one file
written after both passes and so should stay in the hook's scope.

### Context when reported

- **Time:** 2026-08-24 12:10 local
- **Plugin version:** 0.5.2
- **Workstation:** Linux 7.0.0-28-generic (x86_64)
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** first observed at data_quality_mapping close; recurred at every module close
- **Recent questions:** module transition questions
- **Bootcamper responses:** yes
- **Behind the scenes:** `PostToolUse` Markdown lint hook vs. `ground-rules.md` → "Markdown files"
- **Observed problem:** writes to the recap rejected for MD022/MD032
- **Expected behavior:** per the ground rules, plain Markdown is correct until graduation normalizes it
- **Divergence:** the hook enforces at write time what the ground rules defer to graduation
