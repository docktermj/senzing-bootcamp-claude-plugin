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

All three are read-only, stdlib-only, and platform-independent (INV-052/INV-108). Run from
the repo root, or pass ``--repo``:

    python3 .claude/skills/dry-run/coverage_reports.py invariants
    python3 .claude/skills/dry-run/coverage_reports.py affected
    python3 .claude/skills/dry-run/coverage_reports.py negatives
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
#: Where a live claim can live. `specs/` and `feedback/` are records, not shipped claims.
NEGATIVE_ROOTS = ("plugins", "tests", os.path.join(".claude", "skills"), "docs")
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

    A marker that is present but malformed — most often missing its required `owner:`
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
        print("   plugin, but nothing re-asks it. Usually a missing `owner:` clause.")
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
    ap.add_argument("report", choices=("invariants", "affected", "negatives", "both"))
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
    if args.report in ("affected", "both"):
        report_affected(repo)
    if args.report == "both":
        print()
    if args.report in ("negatives", "both"):
        report_negatives(repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
