# Senzing Bootcamp Plugin Feedback

Feedback captured during the Senzing Bootcamp. Every entry is saved here, whatever it turns
out to be about. Entries routed `mcp-server` may **also** have been forwarded to Senzing —
only ever with your explicit yes, and with identifying details stripped; each entry's
`Upstream:` field records what happened.

**Started:** 2026-08-25

## Your Feedback

## Improvement: No warning about load time when scaling a generated scenario near the license limit

**Date:** 2026-08-25
**Module:** Discover the Business Problem
**Priority:** Medium
**Source:** bootcamper-reported
**Routing:** plugin — no guidance in the business-case-offer/scenario-generation steps caps default scenario size or warns about load-time implications when scaling toward the bootcamper's license limit
**Upstream:** not applicable

### What happened

The bootcamper asked for a bigger generated scenario after being told a 3-source, ~7,081-record
scenario "doesn't seem enough" against their 100K-record POC license. The scenario was expanded to
5 sources (~93,999 records) with no warning that loading and processing that volume would take
much longer than a typical bootcamp-scale dataset.

### Why it matters

A bootcamp is meant to be a guided walkthrough completable in a reasonable session, not a
multi-hour data-loading wait. Scaling close to a license limit without a heads-up sets the wrong
expectation for how long the remaining modules (especially Data collection and Data processing)
will take.

### Suggested fix

Cap generated scenarios at ~10,000 records by default; if a bootcamper asks to go higher (e.g.
toward their full license limit), warn them plainly that it will take noticeably longer before
generating it.

### Context when reported

- **Time:** 2026-08-25 13:50 UTC
- **Plugin version:** 0.5.2
- **Workstation:** Darwin 25.5.0 (arm64) — macOS Apple Silicon
- **Model / effort:** claude-sonnet-5 / (effort not surfaced in this session context)
- **Context size:** Unknown
- **Module / step:** business_problem / (Phase 1, discovery — scenario sizing, before Step 5)
- **Recent questions:** "Does that summary capture the situation accurately?" (re-asked after the scenario was scaled up); "Why does this matter to you?"; "Do you have a suggested fix?"; "What priority would you give this?"
- **Bootcamper responses:** Asked for a bigger scenario citing a 100K-record POC license; "it will take too much time for a bootcamp"; "suggest you keep it at 10k max if they go over send them a warning just that it will take them longer"; Medium priority.
- **Behind the scenes:** Module 1 (Discover the Business Problem) Phase 1, Business Case Offer (Step 4a) and CORD sourcing (Step 4b) — generating and then re-scaling a Las Vegas CORD-backed scenario.
- **Observed problem:** No warning was given when the scenario was scaled from ~7K to ~94K records about the resulting load/processing time.
- **Expected behavior:** The scenario-generation steps (Phase 1 Steps 4a/4b) currently validate mapping-complexity and category invariants but have no size cap or time-cost warning tied to record volume.
- **Divergence:** The skill file has no step that ties scenario size to a load-time expectation-setting warning; the gap is in the plugin's scenario-generation guidance, not the MCP server.

## Improvement: license_record_limit was recorded from a bootcamper statement rather than a measurement

**Date:** 2026-08-25
**Module:** SDK setup
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — Module 1 Step 5a reads `license_record_limit` but nothing in that step forbids writing it from an unverified claim; the field's contract is "detected", and the guide populated it from conversation.
**Upstream:** not applicable

### What happened

During Discover the Business Problem, the bootcamper said their POC license allows 100,000 records.
I wrote `license_record_limit: 100000` into `config/bootcamp_progress.json` on the strength of that
statement. In SDK setup, running the authoritative `GetLicense` snippet against the freshly installed
SDK returned `recordLimit: 500` with `licenseType: "EVAL (Solely for non-productive use)"` — the
built-in evaluation license. The POC license key had never been applied to this install. I withdrew
the earlier value, set `license_record_limit` to the measured 500, and moved the bootcamper's stated
entitlement to a separate `license_stated_poc_limit` field.

### Why it matters

`license_record_limit` is the field Module 4's Step 8a License Key gate reads, and a value above the
dataset size SUPPRESSES that gate. Recording 100,000 from an unverified claim would have suppressed
the one prompt that exists to warn the bootcamper before they hit the cap mid-load — on a ~94,000
record scenario whose real ceiling is 500. The correction makes the reported capacity worse (500 vs
100,000) and is exactly the kind of reversal worth recording: the earlier number was wrong and the
scenario had already been sized against it.

### Suggested fix

State in Module 1 Step 5a that `license_record_limit` is written only from a detected license (the
`GetLicense`/`getLicense` record limit), never from a bootcamper statement, and give a separate key
for a stated-but-unapplied entitlement so the two cannot be confused. Consider having SDK setup's
Step 5 run the license check and reconcile it against anything already recorded.

### Context when reported

- **Time:** 2026-08-25 14:10 UTC
- **Plugin version:** 0.5.2
- **Workstation:** Darwin 25.5.0 (arm64) — macOS Apple Silicon
- **Model / effort:** claude-opus-5 / (effort not surfaced in this session context)
- **Context size:** Unknown
- **Module / step:** sdk_setup / 5
- **Recent questions:** "Which database would you like to use?"; EULA acceptance.
- **Bootcamper responses:** SQLite; yes to the EULA.
- **Behind the scenes:** SDK setup Step 5 (license), running the `information/GetLicense.java` snippet from `generate_scaffold(language='java', workflow='information')` against Senzing SDK 4.3.4.
- **Observed problem:** Recorded license limit (100,000) contradicted the engine's own reported limit (500).
- **Expected behavior:** `license_record_limit` should reflect a detected license; Module 1 Step 5a treats its presence as proof a custom license "has already been configured".
- **Divergence:** The field was populated from conversation in Module 1, where no license check runs, and nothing in the step prohibits that.

## Improvement: EQUIFAX quality score was wrong until per-RECORD_TYPE applicability was corrected

**Date:** 2026-08-25
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — Phase 1 step 6 states the per-RECORD_TYPE rule and gives a worked sanctions-list example, but the applicability set still has to be authored per source by hand each run, so getting it wrong is the default failure rather than an unusual one.
**Upstream:** not applicable

### What happened

I authored the applicability table for the five sources and marked ADDRESS, PHONE, WEBSITE and
TRUSTED_ID as applying to both record types on EQUIFAX. Measured per type, all four appear on
ORGANIZATION records only (100% / 91.5% / 42.3% / 100%) and on 0% of PERSON records, while EMAIL
and GENDER are the mirror image (0% org, 10.6% / 8.3% person). EQUIFAX's person records are
officer/contact records attached to a company; a business address is data that structurally cannot
exist on them. With the wrong applicability EQUIFAX scored 70.5% and landed in the "acceptable but
has some gaps" band. Corrected, it scores 85.7% and passes cleanly. I withdrew the first score.

I also initially built the Entity Specification attribute catalog with a backticked-token regex,
which found 21 tokens instead of 110 and reported NAME_ORG, ADDR_LINE1 and PHONE_NUMBER as
unrecognized keys. The specification's feature tables list attribute names as plain text in the
first column, not backticked. That was caught by the step's own "sanity-check any 0% or 100%
figure" instruction: four of five sources reporting exactly zero specification attributes is not a
plausible finding about CORD data.

### Why it matters

The wrong applicability would have told the bootcamper to remediate a source with nothing wrong
with it — the exact false alarm INV-264 describes — on the largest source in the project (72,799
records). The wrong catalog would additionally have reported every source as having zero mapped
fields, which feeds the fast-path decision in step 5a and the completeness denominator in step 6.
Both were measurement faults that looked like data findings.

### Suggested fix

Two concrete additions to Phase 1: (1) have step 6 require a per-RECORD_TYPE presence breakdown for
any field marked "applies to both" before the score is reported — a field at 100%/0% across the two
types is an applicability error by construction, and the breakdown is cheap since the profiling pass
already holds the values; (2) state in step 3 or step 5a that the specification's attribute names
appear as plain text in the first column of its feature tables, since a catalog built by scanning
for backticked codes silently under-collects by ~80%.

### Context when reported

- **Time:** 2026-08-25 15:40 UTC
- **Plugin version:** 0.5.2
- **Workstation:** Darwin 25.5.0 (arm64) — macOS Apple Silicon
- **Model / effort:** claude-opus-5 / high
- **Context size:** Unknown
- **Module / step:** data_quality_mapping / Phase 1 step 6
- **Recent questions:** model/effort switch for this module.
- **Bootcamper responses:** Opus 5 at high effort.
- **Behind the scenes:** Phase 1 step 6 quality scoring across five Las Vegas CORD sources.
- **Observed problem:** EQUIFAX scored 70.5% (remediation band) on an applicability error; the specification catalog under-collected attributes by ~80%.
- **Expected behavior:** Step 6 requires per-RECORD_TYPE applicability and warns that a low score with high NAME/ADDRESS coverage is probably an applicability error — both of which caught this, but only after the wrong number had been computed.
- **Divergence:** The rules are correct and were followed; the applicability set is authored by hand per source, so nothing structurally prevents the error before the score is produced.

## Improvement: bundled Java loading snippets import javax.json, which is not on a plain JDK classpath

**Date:** 2026-08-25
**Module:** Data processing
**Priority:** High
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the snippets come from `senzing/code-snippets-v4` via `generate_scaffold(workflow='add_records', language='java')`; the plugin relays them faithfully
**Upstream:** not yet forwarded — offer raised with the bootcamper at graduation close

### What happened

`generate_scaffold(workflow='add_records', language='java')` returned
`java/snippets/loading/LoadWithStatsViaLoop.java`, whose first import is `javax.json.*` and which
calls `Json.createReader(...)` to pull `DATA_SOURCE` and `RECORD_ID` out of each line. `javax.json`
is a Jakarta EE API and is **not** on the classpath of a plain JDK 21 installation, so the snippet
does not compile as shipped. The same applies to `LoadTruthSetWithInfoViaLoop.java` and the other
loading snippets that parse JSON.

This bootcamp had already hit the same wall in an earlier module and had written its own
dependency-free JSON helper, so the fix was a one-line substitution. A Java bootcamper reaching
Data processing without that helper would hit a compile error on the first thing the module tells
them to run.

### Why it matters

The scaffold is presented as "real, compilable code from senzing/code-snippets-v4" and the
workflow's own tool discipline says to compile before running — so the failure surfaces
immediately, but as a Java classpath error rather than as anything recognizably Senzing-related.
It lands at the exact moment a bootcamper is least equipped to diagnose it: they have just been
told not to hand-write loading code, and the code they were given does not build.

### Suggested fix

Either add a `dependencies` note to the `generate_scaffold` response for Java loading workflows
naming the `jakarta.json` / `javax.json` artifact and where to get it, or ship a variant of the
loading snippets that parses the two needed fields without an external JSON API. The scaffold
already returns a `dependencies` array (`com.senzing:sz-sdk-java`) for other topics, so the
mechanism exists.

## Improvement: mapping step-3 validation rejects NAME_ORG and NAME_FULL even when the source fields are disjoint

**Date:** 2026-08-25
**Module:** Data Quality, Mapping, and Transformation
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** mcp-server — the rule is enforced by `mapping_workflow` step-3 validation
**Upstream:** not yet forwarded — offer raised with the bootcamper at graduation close

### What happened

Two of five sources were rejected at step 3 with:

> NAME_ORG cannot co-exist with person name attributes NAME_FIRST, NAME_FULL, NAME_LAST — a
> record is either a person or an organization.

The rule is right about records. It was applied to **field declarations**, though, and in both
sources the fields were already disjoint:

- OPEN-OWNERSHIP: `NAMES.NAME_ORG` and `NAMES.NAME_FULL`, one populated per record by `RECORD_TYPE`.
- EQUIFAX: `PRIMARY_NAME_ORG` / `LEGAL_NAME_ORG` appear only on `Company` and `Parent` rows;
  `FEATURES.NAME_FIRST` / `NAME_LAST` / `NAME_FULL` appear only on `Contact` and `Executive` rows.
  Verified: zero rows carry both.

The required fix is to move every name field into `type_discriminator.field_overrides` even when
no mapping actually changes by type — the override is identity in both branches, declared purely
to satisfy the validator.

### Why it matters

Two costs, neither obvious. First, the rejection message describes a record-level invariant the
mapping already satisfied, so the natural reading is "your data is wrong" rather than "declare it
differently" — the first attempt at OPEN-OWNERSHIP was spent re-checking the data. Second, fields
moved into `field_overrides` stop being counted by the coverage warning, which then reports
`covers 55 of 61 profiled source fields` for a mapping that dispositions all 61. A bootcamper
reasonably reads a coverage shortfall as unmapped data.

### Suggested fix

Either scope the check to fields that can co-occur on one record (the profiler already knows
which source fields co-occur), or make the message say what the fix is: that the names must be
declared through a `type_discriminator` rather than as unconditional field mappings. Counting
`field_overrides` fields toward the coverage total would remove the second surprise.

## Improvement: macOS strips DYLD_* through protected launchers, so a backgrounded SDK process cannot find the native library

**Date:** 2026-08-25
**Module:** Query, Visualize and Discover
**Priority:** Medium
**Source:** self-observed (assistant retrospective)
**Routing:** plugin — `senzing-env.sh` correctly exports `DYLD_LIBRARY_PATH` and its own comments explain why `-Djava.library.path` alone is insufficient; what is missing is the warning about how that variable is lost
**Upstream:** not applicable

### What happened

Starting the visualization server as a background process via `nohup` failed with:

```text
java.lang.UnsatisfiedLinkError: no Sz in java.library.path
```

despite `DYLD_LIBRARY_PATH` being correctly set in the parent shell. macOS System Integrity
Protection sanitizes `DYLD_*` out of the environment when a **protected** binary execs a child, and
`/usr/bin/nohup`, `/usr/bin/env` and `/bin/bash` are all protected. Confirmed directly:

```text
$ echo $DYLD_LIBRARY_PATH        -> /opt/homebrew/opt/senzing/er/lib:...
$ bash -c 'echo $DYLD_LIBRARY_PATH'   -> (empty)
$ nohup bash -c '...'                 -> (empty)
```

Foreground batch programs worked throughout, which is what makes this confusing: they are direct
children of the shell that exported the variable, so nothing is stripped. The failure appears only
when a process is backgrounded or wrapped — exactly what a bootcamper does to run a server.

### Why it matters

The error names `java.library.path`, so the obvious response is to add `-Djava.library.path=...` —
which `senzing-env.sh` already documents as insufficient, and which does not fix it. Nothing points
at the launcher. This is macOS-specific and silent on Linux, so it will not reproduce for a
maintainer testing there.

### Suggested fix

Note it wherever the bootcamp has a bootcamper start a long-running SDK process on macOS: start it
as a direct child of a shell that has sourced `senzing-env.sh`, not through `nohup`, `env`, or a
nested `bash -c`. A one-line caution next to the visualization-server launch instructions would be
enough.
