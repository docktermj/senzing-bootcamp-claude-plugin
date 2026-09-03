# A non-UTF-8 recap crashes three hooks and both PDF generators — and the obvious fix destroys the recap

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

A `docs/bootcamp_recap.md` that is not valid UTF-8 — the ordinary result of a Windows bootcamper
opening it in an editor that saves cp1252, then adding a smart quote or an en dash — makes **three of
the seven hooks** die with an unhandled Python traceback, and makes **both keepsake PDF generators**
do the same.

Reproduced 2026-08-27 against a scratch project whose recap was written as cp1252 (`’` = `0x92`,
`—` = `0x97`):

```text
precompact-recap.py    ❌ CRASHED (rc=1): UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97 …
session-start.py       ❌ CRASHED (rc=1): UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97 …
session-end.py         ❌ CRASHED (rc=1): UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97 …
checkpoint-tick.py     ✅ rc=0, no traceback
stop-nudge.py          ✅ rc=0, no traceback
generate_recap_pdf.py       ❌ UnicodeDecodeError traceback, no PDF
generate_discoveries_pdf.py ❌ UnicodeDecodeError traceback, no PDF
```

These are not on-request paths. `precompact-recap.py` is the **PreCompact durability hook** — the
mechanism INV-059 exists for — so the failure lands exactly when the recap is about to be needed: the
fold does not happen, the in-progress narrative is never written into the recap, and the bootcamper's
only signal is a traceback in a hook they never invoked.

**`normalize_docs_markdown.py` handles the identical input correctly**, which is what makes this a
gap rather than an accepted limit:

```text
docs/bootcamp_recap.md: could not read ('utf-8' codec can't decode byte 0x97 in position 37: invalid start byte); left untouched.
normalized 0 of 3 file(s) in docs        (exit 0)
```

One script in the family names the failure, leaves the file alone, and exits 0. Five crash.

## Root cause

A single choke point: `plugins/senzing-bootcamp/scripts/recap_checkpoint.py:99-104`.

```python
def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None
```

`UnicodeDecodeError` derives from `ValueError`, **not** `OSError`, so it escapes this handler and
propagates out of every hook that folds or reads the recap — `precompact-recap.py`,
`session-start.py` and `session-end.py` all reach the recap through this one function.

The fix is already written two functions above it. `current_module()`
(`recap_checkpoint.py:83-96`) catches `(OSError, ValueError)` and documents exactly why: *"Never
raises: a malformed or partly-written progress file must not break a hook (INV-048)."* The rule was
stated, and `_read` — in the same file, eleven lines down — does not honor it. The two PDF generators
read their source directly (`generate_recap_pdf.py:3751`, `generate_discoveries_pdf.py:893`, both
bare `read_text(encoding="utf-8")`) and have the same omission independently.

### ⛔ The obvious one-line fix silently destroys the recap. Do not apply it.

Adding `UnicodeDecodeError` to `_read`'s `except` clause is the natural patch and it is **worse than
the crash**. `fold()` reads the recap at `recap_checkpoint.py:223` as

```python
recap = _read(RECAP) or ""
```

and then opens `RECAP` in `"w"` mode at `:235`. With `_read` returning `None` for a *present but
undecodable* file, `recap` becomes `""`, the `if recap.strip():` branch is skipped, and `merged`
becomes the current checkpoint block alone — which is then written over the real file.

Demonstrated 2026-08-27 by applying **only** that one-line change to a copy of the two scripts
outside the repo, against a recap holding two completed modules:

```text
BEFORE: recap is 279 bytes, 2 module sections
recap-checkpoint: folded docs/progress/recap_checkpoint.md into docs/bootcamp_recap.md (97 characters)
AFTER:  recap is 98 bytes, 0 module sections
```

Both completed sections — Entity Resolution Concepts and Data collection — were erased, and the hook
reported a **successful fold**. That is unannounced destruction of the bootcamper's keepsake,
reported as success, on an automatic hook. The crash it replaces at least leaves the file intact.

The underlying flaw is that `_read` collapses two different states into one `None`: *absent* (safe to
create) and *present but unreadable* (must never be overwritten). Only the first is safe for a caller
that goes on to write.

## Proposed change

1. **Make `_read` distinguish absent from unreadable**, rather than widening its `except`. Return
   `None` only when the file is genuinely absent; signal "present but undecodable" distinctly (a
   sentinel, or a small custom exception raised for that case). This is the class fix — all three
   hooks reach the recap through this one function, so correcting it here fixes them together rather
   than at five call sites.
2. **`fold()` must abort on an unreadable recap and write nothing.** Report it in the shape
   `normalize_docs_markdown.py:241-242` already uses — name the file, name the decode error, say the
   recap was left untouched and that the narrative is still in the checkpoint — then return `False`.
   ⛔ It must never fall through to the `open(RECAP, "w")` at `:235`. Same treatment when the
   *checkpoint* is the undecodable file (`checkpoint_state()` reads it through `_read` at `:158`).
3. **Guard both PDF generators** at their own read sites (`generate_recap_pdf.py:3751`,
   `generate_discoveries_pdf.py:893`): catch the decode failure, report which file is not UTF-8, and
   exit non-zero writing **no** PDF. INV-110's no-junk-PDF guarantee already holds by accident here;
   this makes it hold by construction and replaces the traceback with a message the guide can relay.
4. **Do not "repair" the bootcamper's file.** Re-reading with `errors="replace"` or transcoding it
   silently would mutate a document the bootcamper owns and is invited to keep and share. Refuse
   clearly and say what is wrong; the fix is theirs to make.

## Acceptance criteria

- [ ] With `docs/bootcamp_recap.md` written as cp1252, all seven hook entries exit 0 (or non-zero
      with a diagnostic) and **none** emits a `Traceback`.
- [ ] With that same recap, `precompact-recap.py` leaves it **byte-identical** — verified by hash
      before and after — and reports on stderr that the file is not UTF-8 and was left untouched.
- [ ] ⛔ Negative control, and the point of the whole spec: a test asserts the recap is byte-identical
      after a fold against an undecodable recap. Applying the naive `except (OSError,
      UnicodeDecodeError)` patch alone must make that test **fail**, not pass.
- [ ] A completed-module section present before such a fold is still present after it.
- [ ] Both PDF generators exit non-zero, write no PDF, and print a message naming the offending file
      and the encoding problem — no traceback.
- [ ] `normalize_docs_markdown.py`'s existing behavior is unchanged (reports, leaves untouched,
      exit 0).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/recap_checkpoint.py` — `_read` distinguishes absent from
  undecodable (`:99-104`); `fold()` aborts without writing (`:215-235`); `checkpoint_state()`'s read
  (`:158`)
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — guard the source read at `:3751`
- `plugins/senzing-bootcamp/scripts/generate_discoveries_pdf.py` — guard the source read at `:893`
- `tests/test_undecodable_recap_is_never_overwritten.py` — new guard, stdlib only, hooks driven as
  subprocesses so nothing under `plugins/` is imported (INV-108)

## Source

- Feedback: none — found by `/dry-run` phase 2 on 2026-08-27 (`Source: self-observed (assistant
  retrospective)`). Surfaced from the phase-2 instruction to feed the generators junk for INV-110:
  the binary-junk probe produced a raw `UnicodeDecodeError` instead of a diagnostic, and asking why a
  *realistic* file would decode-fail led to cp1252, then to the shared `_read`, then to the
  destructive behavior of the obvious fix.
- Priority: **High.** The crashing path is an automatic hook, and the one it breaks is the durability
  mechanism itself — so the recap stops being checkpointed at precisely the moment context is being
  compacted, which is the failure INV-059 was written to prevent. The escalating factor is the trap
  in the fix: the next person to touch this will very plausibly widen the `except`, at which point
  the plugin silently deletes completed modules from the bootcamper's keepsake and prints a success
  line. Filed High for the second reason more than the first.
- MCP re-check: **n/a (no Senzing fact).** This spec asserts nothing about Senzing, the SDK, the
  entity specification or the MCP server — it concerns the plugin's own scripts, hooks and artifacts
  — so there is no server fact to re-verify and no absence claim about the server to substantiate
  (the `owner-checked:` clause is exempt for this reason). `get_capabilities` was called once at the
  start of this run to date it: server **1.33.0**, 2026-08-27.
- Upstream: not applicable — not a Senzing MCP server defect.
- Related specs: `specs/recap-durability.md` (INV-059, the fold guarantee this breaks);
  `specs/generators-warn-on-dropped-unencodable-characters.md` (the same encoding class on the
  **output** side — this is its input-side counterpart, and the pair is the argument for treating
  encoding as a first-class concern in these scripts);
  `specs/harden-write-gate.md` (INV-109, the other place a hook must fail safe rather than loudly)
