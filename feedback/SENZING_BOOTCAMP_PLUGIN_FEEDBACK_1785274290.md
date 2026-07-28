
## Improvement: Visualization search sends NAME_FULL only, silently missing organizations

**Source:** self-observed (assistant retrospective)
**Module:** Query, Visualize and Discover
**Routing:** plugin — the defect is in the shipped visualization server's search method, not in an MCP tool.
**Upstream:** n/a (plugin-side)

**Context when reported:**
`VizModel.search()` built its search payload as `{"NAME_FULL": q}` only. Measured against 10
ORGANIZATION names from a resolved 390-entity master list: 9 matched on both `NAME_FULL` and
`NAME_ORG`, and 1 (`EKT SMART TECHNOLOGY`) matched on `NAME_ORG` **only** — `NAME_FULL` returned
zero results and raised nothing. The failure is invisible: an empty result set reads as "not in
your data". Module 7's own SKILL text already warns about this, which means the shipped server
contradicts the skill that ships with it. Suggested fix: search both attributes and merge by
`ENTITY_ID`, and report an empty result as "nothing matched the attributes tried", naming them.

## Improvement: Visualization snapshot hardcodes port 8080 and calls the data "this Truth Set"

**Source:** self-observed (assistant retrospective)
**Module:** Query, Visualize and Discover
**Routing:** plugin — string literals in the shipped visualization server.
**Upstream:** n/a (plugin-side)

**Context when reported:**
The Search/Probe tab's snapshot text reads "example searches run against this Truth Set. In the
live app (http://localhost:8080)". In Module 7 the app points at the bootcamper's own data, not
the Truth Set, and the server may run on any `--port`. Both strings ship into
`docs/visualizations/*.html`, which is the retained keepsake — so the artifact tells the reader to
open a port nothing is listening on, and mislabels their own data. Suggested fix: derive the port
from the parsed `--port` value and make the dataset wording neutral.

## Improvement: sdk_guide(topic='configure') snippet fails on a fresh datastore (SENZ7221)

**Source:** self-observed (assistant retrospective)
**Module:** Data Quality, Mapping, and Transformation (Phase 3 sandbox), and Data processing
**Routing:** mcp-server — the returned code snippet is the artifact that needs the fix.
**Upstream:** offered to the bootcamper as a batch with the other mcp-server finding below.

**Context when reported:**
The `RegisterDataSources` snippet returned by `sdk_guide(topic='configure')` opens with
`configMgr.getDefaultConfigId()` then `configMgr.createConfig(configId)`. Against a freshly
schema-created SQLite database — exactly what the same tool's own notes tell you to create with
`szcore-schema-sqlite-create.sql` — `getDefaultConfigId()` returns `0` and `createConfig(0)` throws
`SENZ7221 EAS_ERR_NO_CONFIG_REGISTERED_FOR_DATA_ID`. The `InitDefaultConfig` alternative is listed
but not signposted as the required path for an unseeded datastore. Suggested fix: have the primary
snippet branch on `getDefaultConfigId() == 0` and seed from `createConfig()` (template) +
`setDefaultConfig()`, or state the precondition explicitly in the notes.

## Improvement: sz_verbatim_check cannot pass a non-string source value

**Source:** self-observed (assistant retrospective)
**Module:** Data Quality, Mapping, and Transformation
**Routing:** mcp-server — `sz_verbatim_check.py` is delivered as a workflow resource.
**Upstream:** offered to the bootcamper as a batch with the finding above.

**Context when reported:**
`collect_strings()` harvests only `isinstance(obj, str)` values from the source, so any source value
stored as a JSON **number** can never appear in the allowed set. ICIJ stores `REL_POINTER_KEY` as a
number; emitting it faithfully (as a number) is invisible to the checker, and emitting it as a
string fails the gate on all 53,321 relationship rows. Either choice fails, so the gate is
unsatisfiable for numeric source values. Resolving it required an empirical engine test to confirm
Senzing links disclosed relationships for both a string and a numeric pointer key. Suggested fix:
harvest numeric/boolean source values too (stringified for comparison), or exempt a value whose
emitted JSON type matches the source's.

## Improvement: Screenshot guidance should note the default tab needs no injected tab switch

**Source:** self-observed (assistant retrospective)
**Module:** Query, Visualize and Discover
**Routing:** plugin — capture guidance in module-completion / visualization-api-reference.
**Upstream:** n/a (plugin-side)

**Context when reported:**
Capturing per-tab screenshots by injecting `activate('<tab>')` on page load works for every tab
except the one already active by default (Entity Graph). Re-activating it restarts the D3 force
simulation partway through the capture window, and the screenshot comes out with all nodes
collapsed in a corner — a plausible-looking but empty graph, 47 KB instead of 227 KB. It exits 0
and produces a valid PNG, so nothing flags it. Suggested fix: state that the default tab must be
captured with no injection, and that a force-directed graph needs a longer virtual-time budget than
the static tabs.

## Improvement: Certificate name comes from the recap Markdown, so the INV-113 fix does not reach it

**Source:** self-observed (assistant retrospective)
**Module:** Graduation
**Routing:** plugin — the graduation pre-check and `generate_recap_pdf.py` disagree about where the name lives.
**Upstream:** n/a (plugin-side)

**Context when reported:**
The graduation pre-check correctly rejected the auto-detected handle `docktermj`, asked the pinned
certificate-name question, and persisted the answer as `name` in
`config/bootcamp_preferences.yaml` — exactly as the skill instructs. But
`generate_recap_pdf.py` reads the certificate name from the `**Bootcamper:**` line in
`docs/bootcamp_recap.md`, which Bootcamp preparation wrote at the start of the run. The rendered
certificate therefore printed `docktermj` — the very value the pre-check rejected — while
exiting 0 with 99% content retention and no warning. This is an INV-065 violation reached
through a documented, correctly-followed path, and only an artifact probe (`pdftotext | grep`)
caught it. Suggested fix: have the pre-check update the recap's `**Bootcamper:**` line as well as
preferences, or have the generator prefer `name` from preferences when present.
