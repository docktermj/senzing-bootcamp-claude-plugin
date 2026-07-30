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

``affected``
    Ledgered specs whose ``## Affected files`` predicted a path the entry's
    ``**Files changed:**`` never recorded. A prediction that did not come true is often
    correct (the change turned out not to need that file), which is exactly why this
    cannot be a gate — see ``tests/test_spec_ledger_invariants.py``, which enforces the
    same property only for entries dated on or after its cutoff.

Both are read-only, stdlib-only, and platform-independent (INV-052/INV-108). Run from the
repo root, or pass ``--repo``:

    python3 .claude/skills/dry-run/coverage_reports.py invariants
    python3 .claude/skills/dry-run/coverage_reports.py affected
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", choices=("invariants", "affected", "both"))
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
