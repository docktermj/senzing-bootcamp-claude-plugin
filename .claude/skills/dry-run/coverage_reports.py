#!/usr/bin/env python3
"""Maintainer coverage reports over `specs/` — where an audit should look next.

Two blind spots let an invariant stand unimplemented for weeks while `IMPLEMENTED.md`
recorded its spec as done (`deep-dive-audit-2026-07-29-minor-fixes`, item 4). Neither is a
test, because neither gap is a defect on its own — both are **reports**, so a real signal
is not buried under legitimate entries:

``invariants``
    Invariants no test file mentions by ID. Many are legitimately enforced by tests that
    cite them by name rather than number, so a hit is not a failure — but this is where
    INV-060 and INV-097 hid, and both would have appeared here.

    ⚠️ **This report is unreliable in BOTH directions, and the second one bites harder.**
    It keys on the ID appearing *anywhere* under ``tests/``, which under-reports as noted
    above — and **over-reports** just as easily, because an incidental mention scores an
    invariant as covered. Observed 2026-08-12: INV-183 was named by five test files, every
    one of them invoking it as *rationale* (*"a rule deliberately restated at the step it
    governs is INV-183"*), and none of them the test INV-183 names as its enforcer. The
    missing citation was therefore invisible here, and a finding that recorded it on
    2026-08-11 went unactioned with nothing failing.

    So a **miss on this report is not evidence of coverage**. For the subset of invariants
    that name their own enforcer, ``tests/test_invariant_enforcer_citations.py`` is the
    reliable check — it asserts the named file exists and cites the ID back, and it fails
    rather than reports.

``affected``
    Ledgered specs whose ``## Affected files`` predicted a path the entry's
    ``**Files changed:**`` never recorded. A prediction that did not come true is often
    correct (the change turned out not to need that file), which is exactly why this
    cannot be a gate — see ``tests/test_spec_ledger_invariants.py``, which enforces the
    same property only for entries dated on or after its cutoff.

``negatives``
    Every ``MCP-NEGATIVE:`` marker — a dated claim that some MCP tool does NOT contain
    something — oldest server version first. This is the worklist a dry run's phase 1
    re-asks. A negative cannot go stale *detectably*: the suite is offline (INV-108), so
    nothing can notice that a tool has since gained the coverage the plugin routed around.
    It has happened twice (``senz7221-now-names-its-own-remedy``,
    ``explain-error-code-now-owns-senz7426``), and the second time the stale claim was
    also written into the guards, so correcting the prose *failed* the suite.

    Scanned under ``NEGATIVE_ROOTS`` — plus the single file ``specs/DECLINED.md``, which is
    the one record with no re-verification path at all: a declined spec never reaches
    ``implement-spec`` Step 3.3, so a dated negative in a ``Revisit if:`` clause is re-read
    as authority and never re-asked. Adding that one file does not open the rest of
    ``specs/``.

``unmarked``
    The complement of ``negatives``: dated absence claims in **shipped plugin prose** that carry
    no marker. ``negatives`` can only list what is already tagged, so an unmarked negative is
    invisible to it by construction — and nothing else looks either.
    ``tests/test_dated_negatives_are_marked.py`` scans ``tests/*.py`` assertion lines, and
    INV-217 covers ``specs/DECLINED.md``; shipped prose, the largest surface, was unswept until
    2026-08-13.

    **The date is the discriminator.** A unit is reported only when it carries an MCP tool name
    *and* absence vocabulary *and* a date or server version. Prose that explains how a tool
    behaves without dating it is not a re-checkable claim — INV-192's rule contains the sentence
    "the payload of a gate is empty by design, not because the topic is undocumented", which is
    true, must never require a marker, and carries no date. Every defect found on 2026-08-13 was
    dated.

    ⚠️ **A report, not a gate, and deliberately so.** Deciding whether a hit is a live claim or
    prose about tool behaviour needs judgement, which is the same reason ``invariants`` and
    ``affected`` are reports. The absence vocabulary is also a phrase list, so it is evadable by
    paraphrase: a miss is weak evidence. The marker is the durable route; this finds the ones
    nobody marked.

All four are read-only, stdlib-only, and platform-independent (INV-052/INV-108). Run from
the repo root, or pass ``--repo``:

    python3 .claude/skills/dry-run/coverage_reports.py invariants
    python3 .claude/skills/dry-run/coverage_reports.py affected
    python3 .claude/skills/dry-run/coverage_reports.py negatives
    python3 .claude/skills/dry-run/coverage_reports.py unmarked
    python3 .claude/skills/dry-run/coverage_reports.py both

Exit status is 0 whatever the findings — these inform an audit, they do not gate one.
"""
import argparse
import os
import re
import sys

INV_DEF = re.compile(r"\*\*INV-(\d{3})\*\*")
INV_REF = re.compile(r"INV-(\d{3})")
LEDGER_HEAD = re.compile(r"^## (\S+)$", re.M)
FILES_CHANGED = re.compile(r"^- \*\*Files changed:\*\*(.*)$", re.M)
PATH_IN_TICKS = re.compile(r"`([A-Za-z0-9_./{}*-]+\.(?:md|py|sh|json|yaml|yml|js|png|pdf))`")

#: `MCP-NEGATIVE: <tool(params) asked> — <what is absent> — owner: <route that owns the fact
#:  + outcome> — server <version>, <YYYY-MM-DD>`
#: The em dash is what the plugin's prose uses; a plain `--` is accepted so the marker can
#: be written in a context where an em dash is awkward.
#:
#: ⛔ `owner:` is REQUIRED, and a marker without it deliberately does not match — it must
#: surface as a missing marker rather than as a well-formed one. Absence evidence and
#: ownership evidence are different claims, and only the second one supports a negative:
#: "`configure` returns no license variable" is a true fact about `configure` and worthless
#: as support for "no license variable exists". The route that would CARRY the fact is what
#: has to be asked (INV-194) and what a re-check must re-ask. Recording only the empty call
#: is what made a wrong-route conclusion look reviewed, twice over — see
#: `specs/mcp-negative-markers-must-name-the-owning-route.md`.
MCP_NEGATIVE = re.compile(
    r"MCP-NEGATIVE:\s*(?P<claim>.+?)\s*(?:—|--)\s*owner:\s*(?P<owner>.+?)\s*(?:—|--)\s*"
    r"server\s*(?P<version>[0-9][0-9.]*)\s*,\s*(?P<date>\d{4}-\d{2}-\d{2})"
)
#: The bare token, used to catch markers that are PRESENT but do not fully parse.
#: Making `owner:` required has a failure mode of its own: a marker missing the clause stops
#: matching `MCP_NEGATIVE`, so without this it would silently drop off the worklist instead of
#: failing — invisibility being the exact condition the marker convention exists to prevent.
#: A malformed marker is therefore worse than a missing one and is reported separately.
#: (Found by negative control: stripping the clause from one marker left the suite green and
#: quietly shrank the worklist from three to two.)
MCP_NEGATIVE_TOKEN = re.compile(r"MCP-NEGATIVE:")
#: A file that legitimately contains the marker text without making a claim (this script,
#: its test, the spec that defines the format) opts out with this line.
NEGATIVE_OPT_OUT = "MCP-NEGATIVE-SCAN: ignore-file"
#: Where a live claim can live. `specs/` and `feedback/` are records, not shipped claims — a
#: spec's Senzing facts are re-verified by `implement-spec` Step 3.3 on the way in, and an
#: `IMPLEMENTED.md` entry's `MCP re-check:` field is a point-in-time record of that check.
NEGATIVE_ROOTS = ("plugins", "tests", os.path.join(".claude", "skills"), "docs")
#: `specs/DECLINED.md` is the one exception, and it is a file rather than a root so that
#: including it does not open the rest of `specs/`. A declined spec is never implemented, so
#: Step 3.3 never runs on it — the re-verification path that justifies excluding `specs/` does
#: not exist here. That makes a negative in a `Revisit if:` clause or a dated revisit note the
#: only Senzing claim in the repo with neither a scanner nor any re-verification path, while
#: `implement-spec` positions this file as the HIGHER authority ("re-verify the condition rather
#: than trusting the spec's original citations"). A `Revisit if:` exists precisely to be
#: re-checked later, so a stale negative inside one sends that recheck to the wrong answer while
#: looking evidenced — which is what happened on 2026-08-13 (`specs/DECLINED.md`'s
#: `no-route-for-bootcampers-who-cannot-add-an-mcp-server` note).
NEGATIVE_EXTRA_FILES = (os.path.join("specs", "DECLINED.md"),)
#: Where shipped prose lives, for the `unmarked` report. Only the plugin: a spec or a test may
#: discuss an absence freely, and both have their own mechanisms (Step 3.3, INV-217, the
#: assertion-line guard).
PROSE_ROOT = os.path.join("plugins", "senzing-bootcamp")
#: The 13 MCP tools. Restated here rather than imported from a test, because this script is the
#: dependency and not the dependent — `tests/test_declined_ledger.py` imports its grammar FROM here.
MCP_TOOLS = (
    "explain_error_code", "search_docs", "sdk_guide", "get_sdk_reference", "reporting_guide",
    "generate_scaffold", "get_sample_data", "find_examples", "mapping_workflow",
    "analyze_record", "get_capabilities", "download_resource", "submit_feedback",
)
PROSE_TOOL = re.compile(r"(?i)(%s)" % "|".join(MCP_TOOLS))
#: Phrasings asserting a tool LACKS content. ⛔ Deliberately excludes a bare `never`: it matched
#: "never from training data", "never `exit 1`" and "never re-read", which is 15 false positives on
#: this corpus (measured 2026-08-13: 23 hits with it, 8 without). Only content-negatives here.
PROSE_ABSENCE = re.compile(
    r"(?i)documents? (?:neither|no\b)|returns? no\b|carr(?:y|ies) no\b|contains? no\b|has no\b|"
    r"no indexed document|appears? nowhere|nowhere in|is not documented|not documented by|"
    r"returns? only|only generic|makes no\b|never names|never documents|"
    r"does (?:\*\*)?not(?:\*\*)? (?:name|document|carry|return|list|mention|cover|answer|contain)"
)
#: What turns prose about a tool into a CLAIM that can expire.
PROSE_DATED = re.compile(r"\b20\d\d-\d\d-\d\d\b|\bserver\s+\d+\.\d+")
#: Block-level escape for prose quoting a retracted claim (same token `implement-spec` documents).
PROSE_QUOTED_HISTORY = "MCP-NEGATIVE-SCAN: quoted-history"
#: Block-level escape for an absence that is NOT about a tool's content. The vocabulary cannot tell
#: "the datastore has no default configuration" — a fact about the Bootcamper's environment — from
#: "the declared schema has no `inline` parameter", and both must stay sayable: the second needs a
#: marker and the first cannot have one, because there is no route to re-ask. Declaring it converts
#: a judgement into a greppable, reviewable decision, which is the same reason `quoted-history`
#: exists. Triaged 2026-08-13: exactly one site in the corpus (`module-02` Step 9's SENZ7221 bullet).
PROSE_NOT_A_CLAIM = "MCP-NEGATIVE-SCAN: not-a-tool-claim"
#: How far from a unit a marker may sit and still cover it. Markers are written as HTML comments
#: immediately before or after the claim, and a fenced claim's marker sits outside the fence.
PROSE_MARKER_WINDOW = 6
SKIP_DIRS = {"__pycache__", "vendor", "node_modules", ".git", ".history", ".pytest_cache"}


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _ledger_entries(repo):
    """Map spec name -> entry body, from specs/IMPLEMENTED.md."""
    txt = _read(os.path.join(repo, "specs", "IMPLEMENTED.md"))
    parts = re.split(LEDGER_HEAD, txt)
    return dict(zip(parts[1::2], parts[2::2]))


def report_invariants(repo):
    """Invariants defined in INVARIANTS.md that no test file cites by ID."""
    inv_txt = _read(os.path.join(repo, "specs", "INVARIANTS.md"))
    defined = sorted({int(n) for n in INV_DEF.findall(inv_txt)})
    tests_dir = os.path.join(repo, "tests")
    cited = set()
    for name in sorted(os.listdir(tests_dir)) if os.path.isdir(tests_dir) else []:
        if name.endswith(".py"):
            cited |= {int(n) for n in INV_REF.findall(_read(os.path.join(tests_dir, name)))}
    uncited = [n for n in defined if n not in cited]
    print("== Invariants cited by no test file ==")
    print("defined: %d   cited by a test: %d   uncited: %d"
          % (len(defined), len(defined) - len(uncited), len(uncited)))
    print("(A hit is not a defect: many invariants are enforced by tests that name them")
    print(" rather than numbering them. It is a list of where to look, not a bug list.)")
    print("(And 'cited' is a proxy for 'asserted': an ID mentioned only in a test's")
    print(" comment or docstring counts as cited here, so this UNDER-reports. A hit is")
    print(" therefore strong evidence of a gap; a miss is weak evidence of coverage.)")
    print()
    line = []
    for n in uncited:
        line.append("INV-%03d" % n)
        if len(line) == 10:
            print("  " + "  ".join(line))
            line = []
    if line:
        print("  " + "  ".join(line))
    return uncited


#: The index group whose members bind the DEVELOPMENT environment, not the shipped plugin.
#: `specs/INVARIANTS.md` names this group as the exemption in its own text, so the rule lives
#: in the data an author already edits (rule 3 makes an index entry mandatory) rather than in
#: a list here that they would have to know to update.
DEV_GROUP = "development record itself"

#: An invariant's text NAMES a shipped artifact when it points at something under `plugins/`.
#: This is the filter that makes the report readable: a rule naming a file, module or step is
#: one INV-183 requires to be reachable AT that step, so an uncited one is a real gap. A rule
#: stating a general property with no artifact ("a value the Bootcamper was asked for MUST
#: outrank...") is honoured by behaviour and is not expected to be cited anywhere in
#: particular — reporting it is the noise that gets a report ignored.
SHIPPED_ARTIFACT = re.compile(
    r"plugins/|"
    r"\bmodule-\d\d|\bModule \d|"
    r"SKILL\.md|phase[0-9A-Za-z-]*\.md|ground-rules\.md|"
    r"scripts/[\w-]+\.py|hooks/[\w-]+\.py|"
    r"\bgraduation\b|\bbootcamp-onboarding\b|\bbootcamp-preparation\b"
)

INDEX_GROUP = re.compile(r"(?m)^- \*\*(?P<name>[^*]+)\*\* — .*?(?=^- \*\*|\Z)", re.DOTALL)

#: File kinds a citation can appear in. `plugins/` also holds PDFs and PNGs.
TEXT_SUFFIXES = frozenset(
    (".md", ".py", ".json", ".yaml", ".yml", ".sh", ".ps1", ".txt", ".js", ".html", ".css")
)


def _index_groups(inv_txt):
    """{group name: {INV ids}} from `### Index by subject`, or {} when absent."""
    start = inv_txt.find("### Index by subject")
    if start < 0:
        return {}
    section = inv_txt[start:]
    end = section.find("<!-- New invariants")
    if end > 0:
        section = section[:end]
    # INV_REF captures the DIGITS; re-attach the prefix so these compare against `INV-NNN`.
    # Getting this wrong is silent and total: the exemption set simply never matches.
    return {m.group("name").strip(): {"INV-" + n for n in INV_REF.findall(m.group(0))}
            for m in INDEX_GROUP.finditer(section)}


def find_uncited_in_shipped(repo):
    """([(id, text)] to report, [ungrouped ids]) — invariants no shipped file cites.

    Three filters, and the second two are what make the output worth reading:

    1. Not cited by any file under `plugins/`.
    2. Not in the `INVARIANTS.md` index group that binds the development environment — those
       are *supposed* to be absent from shipped text, and flagging them trains the reader to
       skip the whole report.
    3. Its own text names a shipped artifact (a path, module, step or bundled script). That is
       the class INV-183 governs: a rule binding a step must be reachable AT that step.

    An invariant in **no** group is returned separately rather than silently exempted — a
    missing index entry must not become a way to disappear from this report.
    """
    inv_txt = _read(os.path.join(repo, "specs", "INVARIANTS.md"))
    entries = re.findall(r"(?m)^- \*\*(INV-\d{3})\*\* — (.+)$", inv_txt)
    groups = _index_groups(inv_txt)
    exempt = set()
    for name, ids in groups.items():
        if DEV_GROUP in name.lower():
            exempt |= ids
    grouped = set().union(*groups.values()) if groups else set()

    # Text only: `plugins/` also carries the certificate PDF and screenshot assets, and
    # `_read` raises UnicodeDecodeError on them. A citation can only live in text anyway.
    plugins = os.path.join(repo, "plugins")
    cited = set()
    for root, _dirs, files in os.walk(plugins):
        for name in files:
            if os.path.splitext(name)[1].lower() not in TEXT_SUFFIXES:
                continue
            # INV_REF captures the DIGITS, not the whole id — re-attach the prefix.
            cited |= {"INV-" + n
                      for n in INV_REF.findall(_read(os.path.join(root, name)))}

    hits, ungrouped = [], []
    for inv_id, text in entries:
        # INV-001–INV-050 are the bootcamp's own OUTCOMES, which `INVARIANTS.md` states are
        # deliberately not indexed ("everything below is a development rule"). They are
        # honoured by the flow existing rather than by any file naming them, so scoring them
        # against shipped citations measures the wrong thing — and, being unindexed, the
        # exemption cannot classify them either way.
        if int(inv_id[4:]) <= 50:
            continue
        if inv_id not in grouped:
            ungrouped.append(inv_id)
        if inv_id in cited or inv_id in exempt:
            continue
        # ⚠️ lowercase BOTH sides. Searching for "INV" inside `text.lower()` never matches,
        # which silently let every superseded invariant through on the first run.
        if "superseded by inv" in text.lower():
            continue
        if not SHIPPED_ARTIFACT.search(text):
            continue
        hits.append((inv_id, text))
    hits.sort(reverse=True)                       # newest ID first: most likely an oversight
    return hits, sorted(ungrouped)


def report_shipped(repo):
    """Invariants that bind a shipped artifact and that no shipped file cites."""
    hits, ungrouped = find_uncited_in_shipped(repo)
    print("== Invariants naming a shipped artifact that NO file under plugins/ cites ==")
    print("The mirror of the `invariants` report, which looks at tests/ only. A rule that")
    print("names a file, module or step must be reachable AT that step (INV-183); one that")
    print("is cited nowhere in shipped text is a rule the guide cannot look up.")
    print("(A hit is not a defect. An invariant can be honoured by behaviour without being")
    print(" named — this is where to look, not a bug list. Development-environment rules are")
    print(" exempt via the INVARIANTS.md index group that declares them; invariants stating a")
    print(" general property with no artifact are not reported at all.)")
    print()
    if ungrouped:
        print("  ⛔ %d invariant(s) are in NO index group, so the exemption could not be"
              % len(ungrouped))
        print("     applied to them. Fix the index (INVARIANTS.md rule 3) — a missing group")
        print("     entry must not become a way to vanish from this report:")
        print("     " + "  ".join(ungrouped))
        print()
    if not hits:
        print("  (none — every invariant naming a shipped artifact is cited in shipped text)")
        return hits
    print("hits: %d, newest first" % len(hits))
    print()
    for inv_id, text in hits:
        print("  %s  %s" % (inv_id, text[:104]))
    return hits


def report_affected(repo):
    """Ledgered specs whose predicted Affected files never reached Files changed."""
    entries = _ledger_entries(repo)
    print("== Predicted-but-unrecorded files (ledgered specs) ==")
    print("A spec's `## Affected files` is a prediction; the entry's `Files changed:` is")
    print("the outcome. A gap is often legitimate — report only, never a gate.")
    print()
    gaps = {}
    for name, body in sorted(entries.items()):
        spec = os.path.join(repo, "specs", "%s.md" % name)
        if not os.path.isfile(spec):
            continue                                   # audits recorded with no spec file
        txt = _read(spec)
        m = re.search(r"^## Affected files\s*$(.*?)(^## |\Z)", txt, re.M | re.S)
        if not m:
            continue
        predicted = sorted(set(PATH_IN_TICKS.findall(m.group(1))))
        recorded = FILES_CHANGED.search(body)
        recorded = recorded.group(1) if recorded else ""
        missing = [p for p in predicted
                   if os.path.basename(p) not in recorded and os.path.basename(p) not in body]
        if missing:
            gaps[name] = missing
    print("ledgered specs examined: %d   with a gap: %d" % (len(entries), len(gaps)))
    print()
    for name, missing in gaps.items():
        print("  %s" % name)
        for p in missing:
            print("      %s" % p)
    return gaps


def _scan_files(repo):
    """Every file a live MCP-NEGATIVE claim could sit in."""
    for root in NEGATIVE_ROOTS:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                if name.endswith((".md", ".py")):
                    yield os.path.join(dirpath, name)
    for rel in NEGATIVE_EXTRA_FILES:                   # named files, not roots — see above
        path = os.path.join(repo, rel)
        if os.path.isfile(path):
            yield path


def find_negatives(repo):
    """[(version_key, version, date, claim, owner, relpath, lineno)] for every marker found."""
    found = []
    for path in _scan_files(repo):
        text = _read(path)
        if NEGATIVE_OPT_OUT in text:
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            m = MCP_NEGATIVE.search(line)
            if not m:
                continue
            version = m.group("version")
            key = tuple(int(p) for p in version.split(".") if p.isdigit())
            found.append((key, version, m.group("date"), m.group("claim").strip(),
                          m.group("owner").strip(), os.path.relpath(path, repo), lineno))
    found.sort(key=lambda r: (r[0], r[2]))
    return found


def find_malformed_negatives(repo):
    """[(relpath, lineno, line)] for every `MCP-NEGATIVE:` that does not fully parse.

    Two causes, and they need different fixes: a missing `owner:` clause, or a marker
    **wrapped across lines** — `MCP_NEGATIVE` is not `re.DOTALL`, so it cannot match past a
    newline and a wrapped marker fails identically to a clauseless one. `tests/
    test_dated_negatives_are_marked.py` diagnoses which per row; do not guess one for both.

    A marker that is present but malformed — whatever the cause, missing its required `owner:`
    clause — is worse than a missing marker: the claim is still shipped and still shapes
    the plugin's routing, but it no longer appears on the re-check worklist. Report it
    loudly rather than letting the count quietly shrink.
    """
    bad = []
    for path in _scan_files(repo):
        text = _read(path)
        if NEGATIVE_OPT_OUT in text:
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            if MCP_NEGATIVE_TOKEN.search(line) and not MCP_NEGATIVE.search(line):
                bad.append((os.path.relpath(path, repo), lineno, line.strip()))
    return bad


def _prose_units(text):
    """[(first_lineno, unit_text)] — one unit per fenced block, per bullet, per paragraph.

    Granularity is the whole game here. A contiguous bullet list read as ONE unit produced a false
    positive on `ground-rules.md`'s tool-routing list: a tool name in one bullet, "returns no" in
    another and a date in a third co-occurred without ever being a single claim. Same lesson as
    `tests/test_declined_ledger.py`, which had to go per-bullet rather than per-entry.

    A fenced block stays whole, because a claim there is routinely split across two comment lines —
    the tool on one, the date on the next.
    """
    units, cur, start, fence = [], [], None, False

    def flush():
        if cur:
            units.append((start, "\n".join(cur)))

    for lineno, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            if fence:                                   # closing
                cur.append(line)
                flush()
                cur, start, fence = [], None, False
            else:                                       # opening
                flush()
                cur, start, fence = [line], lineno, True
            continue
        if fence:
            cur.append(line)
            continue
        if not line.strip():                            # blank line ends a unit
            flush()
            cur, start = [], None
        elif re.match(r"^\s*(?:[-*+]|\d+\.)\s", line):  # a bullet starts its own unit
            flush()
            cur, start = [line], lineno
        elif cur:
            cur.append(line)                            # continuation
        else:
            cur, start = [line], lineno
    flush()
    return units


def find_unmarked_negatives(repo):
    """[(date, relpath, lineno, phrase, excerpt)] for dated tool-absence prose with no marker."""
    base = os.path.join(repo, PROSE_ROOT)
    found = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            text = _read(path)
            if NEGATIVE_OPT_OUT in text:
                continue
            lines = text.split("\n")
            for start, unit in _prose_units(text):
                phrase = PROSE_ABSENCE.search(unit)
                dated = PROSE_DATED.search(unit)
                if not (phrase and dated and PROSE_TOOL.search(unit)):
                    continue
                # A marker or an escape covers the claim when it sits NEAR it, not only inside
                # the same unit: both are written as HTML comments immediately before or after,
                # which puts them in a different unit whenever the claim is a bullet or a fence.
                lo = max(0, start - 1 - PROSE_MARKER_WINDOW)
                hi = min(len(lines), start - 1 + len(unit.split("\n")) + PROSE_MARKER_WINDOW)
                near = "\n".join(lines[lo:hi])
                if PROSE_QUOTED_HISTORY in near or PROSE_NOT_A_CLAIM in near:
                    continue                            # declared not-a-claim / quoted history
                if MCP_NEGATIVE.search(near):
                    continue                            # a marker already covers it
                found.append((dated.group(0), os.path.relpath(path, repo), start,
                              phrase.group(0), " ".join(unit.split())[:150]))
    found.sort()                                        # oldest stamp first, like `negatives`
    return found


def report_unmarked(repo):
    """Dated tool-absence prose carrying no marker — the complement of `negatives`."""
    found = find_unmarked_negatives(repo)
    print("== Dated tool-absence claims in shipped prose with NO marker ==")
    print("`negatives` lists what is already tagged, so it cannot see these. Each is a claim")
    print("that expires with no way to notice: the suite is offline (INV-108), and nothing")
    print("re-asks an unmarked negative. Give each one a marker with its `owner:` clause — after")
    print("re-asking the owning route, never by stamping today's date on an unverified claim.")
    print()
    print("⚠️ Judgement required, which is why this is a report. A hit may be prose ABOUT tool")
    print("behaviour rather than a live claim. The date is what separates the two: undated prose")
    print("is not re-checkable, so it is not reported. Vocabulary is a phrase list and evadable")
    print("by paraphrase — a miss is weak evidence, a hit is worth reading.")
    print()
    if not found:
        print("  (none — every dated tool-absence claim in shipped prose carries a marker)")
        return found
    print("unmarked: %d" % len(found))
    print()
    for stamp, relpath, lineno, phrase, excerpt in found:
        print("  %-12s %s:%d   [%s]" % (stamp, relpath, lineno, phrase))
        print("      %s" % excerpt)
    return found


def report_negatives(repo):
    """Dated 'this tool does not contain X' claims, oldest server version first."""
    found = find_negatives(repo)
    print("== Dated MCP negatives, oldest server version first ==")
    print("A negative about a tool's content cannot go stale detectably: the suite is")
    print("offline (INV-108), so nothing notices when the server gains the coverage the")
    print("plugin routed around. Re-ask for each of these; the oldest is the most likely")
    print("to have moved. When one no longer holds, correct the claim AND invert or")
    print("rescope the guard that pins it — do not delete the guard.")
    print()
    print("⛔ Re-ask the OWNER, not just the route that came back empty. An empty result")
    print("from a tool that never carried the fact is a true statement about that tool and")
    print("no evidence at all for the negative — which is how a wrong-route conclusion")
    print("reaches an invariant looking reviewed (INV-194). The `owner:` line below is the")
    print("route the claim actually rests on; if it is where the fact lives, the negative")
    print("is about ROUTING and the reader should be sent there instead.")
    print()
    malformed = find_malformed_negatives(repo)
    if malformed:
        print("⛔ MALFORMED markers: %d — shipped claims that fell OFF the worklist. A"
              % len(malformed))
        print("   malformed marker is worse than a missing one: the claim still routes the")
        print("   plugin, but nothing re-asks it. Either a missing `owner:` clause or a")
        print("   marker WRAPPED across lines — it must be on ONE line (regex is not DOTALL).")
        for relpath, lineno, line in malformed:
            print("     %s:%d" % (relpath, lineno))
            print("       %s" % line[:150])
        print()
    if not found:
        print("  (none found — if that is a surprise, the markers are missing, not the claims)")
        print("  A marker with no `owner:` clause does NOT parse, by design: it is reported")
        print("  above as malformed rather than silently accepted.")
        return found
    print("markers: %d" % len(found))
    print()
    for _key, version, date, claim, owner, relpath, lineno in found:
        print("  server %-8s %s  %s:%d" % (version, date, relpath, lineno))
        print("      %s" % claim)
        print("      owner: %s" % owner)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report",
                    choices=("invariants", "shipped", "affected", "negatives", "unmarked",
                             "both"))
    ap.add_argument("--repo", default=os.getcwd(),
                    help="repo root (default: current directory)")
    args = ap.parse_args(argv)
    repo = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(repo, "specs")):
        sys.stderr.write("no specs/ under %s — pass --repo\n" % repo)
        return 2
    if args.report in ("invariants", "both"):
        report_invariants(repo)
    if args.report == "both":
        print()
    if args.report in ("shipped", "both"):
        report_shipped(repo)
    if args.report == "both":
        print()
    if args.report in ("affected", "both"):
        report_affected(repo)
    if args.report == "both":
        print()
    if args.report in ("negatives", "both"):
        report_negatives(repo)
    if args.report == "both":
        print()
    if args.report in ("unmarked", "both"):
        report_unmarked(repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
