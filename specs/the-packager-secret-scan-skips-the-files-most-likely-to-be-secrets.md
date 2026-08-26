# The packager's secret scan is filtered by file extension, so a `.pem` private key is packaged

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

`scripts/package_bootcamp.py` scans candidate members for the INV-109 secret patterns before
including them — but only members whose extension appears in `TEXT_SUFFIXES` (`:109`, applied at
`:210`). That list carries `.md`, `.py`, `.json`, `.yaml`, `.csv` and friends. It does **not**
carry `.pem`, `.key`, `.crt`, `.p12`, `.ppk`, or the empty extension.

Measured on a fixture project, `--profile transfer`:

```text
INCLUDED:
    src/keys/id_rsa            <- contains -----BEGIN PRIVATE KEY-----
    src/keys/server.pem        <- contains -----BEGIN RSA PRIVATE KEY-----
EXCLUDED:
    src/loader.py              excluded: content matched a secret pattern (PEM private key)
    src/keys/creds.cfg         excluded: content matched a secret pattern (AWS access-key ID)
```

⛔ **The same private key is excluded from a `.py` and packaged from a `.pem`.** The scan skips
precisely the file types whose *purpose* is to hold a credential, in an archive whose entire
reason to exist is being handed to somebody else.

⚠️ **Severity.** This is not a hypothetical: `transfer` includes `src/`, and a Bootcamper who
keeps a key beside their loader — or an `id_rsa` copied in for a database tunnel — gets it
packaged with no notice. The manifest does not name it as excluded, because it was never
examined. `OPEN_ME_FIRST.md` tells the recipient that *"anything matching a secret pattern"* was
excluded, which is then false.

## Root cause

**An allowlist written to decide "is this worth reading as text?" is being used to decide "can
this contain a secret?"** Those are different questions, and the second must fail **closed**.

`_scan()` returns `None` — meaning "no secret found" — for every unlisted suffix, so the
skip is indistinguishable from a clean result at the call site:

```python
def _scan(path):
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None            # <- "not scanned" reported as "nothing found"
```

⚠️ **The same file gets this right one line away.** The `find_secret` import carries an explicit
fail-closed fallback — *"Fail CLOSED, not open: with no scanner, nothing text-like is
packaged"* — so the author's intent was fail-closed on the scanner being missing, and fail-open
on the suffix, in the same module.

⛔ **`write-gate.py` does NOT have this filter, which is what makes the sync test misleading.**
The gate scans the whole payload regardless of extension. `tests/test_secret_patterns_are_shared.py`
asserts the two **pattern strings** are byte-identical and reports that as the packager being
unable to "protect less than the gate" — but the patterns were never the difference. The
*application* is: identical patterns, one applied to every payload and one applied to an
extension allowlist. A sync test on the constant gave false assurance about the behavior.

**This is the audit method's Step 7 class 3 — a guard narrower than what it claims** — and three
places over-claim on the strength of it:

- `tests/test_package_bootcamp.py`'s docstring: *"Members matching an INV-109 secret pattern are
  excluded and named"*. Its test uses a `.py` fixture, so it passes.
- `tests/test_secret_patterns_are_shared.py`'s docstring: *"`package_bootcamp.py` excludes a
  **member** whose content matches them"*.
- `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`'s drafted invariant: *"MUST
  exclude and name any member matching the INV-109 secret patterns"*.

## Proposed change

**1. Scan by content, not by extension.** Read a bounded prefix of every candidate member and
scan it if it decodes as text; skip only what is genuinely binary. A NUL byte in the first block
is the usual, cheap discriminator, and it costs one read per member on a tree already being
hashed for the manifest.

**2. Where a member cannot be examined, exclude it and say so — never include it silently.**
`_scan()` must distinguish three outcomes, not two: a secret found (exclude and name the class),
nothing found (include), and **not examined** (exclude and name the reason). The third is what
does not exist today.

⚠️ **Keep the manifest's promise honest either way.** `OPEN_ME_FIRST.md` states that anything
matching a secret pattern was excluded; whichever route is taken, that sentence must become true
rather than aspirational.

**3. Correct the three over-claiming docstrings** and add the fixture that would have caught
this: a `.pem` and an extensionless key file carrying real armor lines, asserted excluded.

**4. Make the sync test say what it actually proves.** It pins the pattern **constants** equal;
it does not and cannot establish that the two consumers apply them to the same inputs. Say so in
its docstring, and add an assertion that the packager's scan is **not** gated on an extension
allowlist — the property whose absence caused this.

⛔ **Do not fix this by lengthening `TEXT_SUFFIXES`.** A longer allowlist is the same defect with
a later trigger: the next unlisted extension is a fresh disclosure, and nothing signals which
extensions were forgotten. The list is the wrong mechanism, not an incomplete one.

## Acceptance criteria

- [ ] A member containing a PEM private key is excluded regardless of its extension — asserted
      over a fixture with at least `.pem`, an extensionless file, and one unlisted extension.
- [ ] A member that cannot be examined is excluded and named in `PACKAGE_MANIFEST.json`, never
      silently included.
- [ ] A genuinely binary member (a PNG) is still packaged — the fix must not exclude the
      visualizations the `share` profile exists to carry.
- [ ] `TEXT_SUFFIXES` is no longer the gate on whether a member is scanned.
- [ ] The three over-claiming docstrings state what is actually asserted, and
      `tests/test_secret_patterns_are_shared.py` says plainly that pattern equality does not
      establish equal application.
- [ ] `tests/test_secret_patterns_are_shared.py` additionally asserts the packager's scan is not
      gated on an extension allowlist.
- [ ] Negative-controlled: reintroducing the extension gate fails the new fixture test.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — no
      dependency on `file(1)` or any external tool.

## Affected files

- `plugins/senzing-bootcamp/scripts/package_bootcamp.py` — `_scan()`, `TEXT_SUFFIXES`, and the
  three-outcome contract at the call site in `collect()`
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/packaging.md` — the Step 4 summary of what
  the scan covers
- `tests/test_package_bootcamp.py` — the `.pem`/extensionless fixture; the docstring
- `tests/test_secret_patterns_are_shared.py` — what it proves, and the no-allowlist assertion
- `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` — the drafted invariant's
  secret-scan clause, so the wording awaiting sign-off describes the fixed behavior

## Source

- Feedback: n/a — found by `production-readiness-audit-2026-08-26c` applying Step 7 class 3 ("a
  guard narrower than the invariant it claims to enforce") to the packaging feature added earlier
  the same day; `Source: self-observed (assistant retrospective)`.
- Priority: **High** — a credential-disclosure path in a feature whose purpose is handing files to
  other people, with a manifest that states the opposite. Nothing errors and nothing warns.
- MCP re-check: n/a (no Senzing fact). The secret patterns are the plugin's own (INV-109) and the
  defect is in how they are applied; no SDK method, flag, response shape or server behavior is
  asserted, and no absence is claimed.
- Upstream: not applicable.
- Related specs: `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` (introduced the
  scan), `specs/harden-write-gate.md` (INV-109's patterns, and the consumer that applies them
  correctly — with no extension filter)
