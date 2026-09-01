# A stray fence START pairs with a later fence's END and silently deletes finalized recap modules

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

## Problem

Both fence handlers in `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` find their END
marker with `text.find(END, start)` — **the next END anywhere in the document**, not the one
belonging to the START they matched. When a first fence is unterminated and a second, terminated
fence follows, the pair spans everything between them, and every finalized module section in that
span is discarded.

Reproduced 2026-09-01 against the shipped script, for **both** fences:

```text
input:   ## Discover the Business Problem      (real, finalized)
         <!-- RECAP-CHECKPOINT:START -->       (unterminated)
         ## SDK setup                          (real, finalized, with content)
         <!-- RECAP-CHECKPOINT:START -->  …  <!-- RECAP-CHECKPOINT:END -->
         ## Data collection                    (real, finalized)

parsed:  ['Discover the Business Problem', 'Data collection']
```

`SDK setup` is gone. The identical shape with `BOOTCAMP-NOTES` markers deletes it too.

⛔ **Three things conspire to make the loss silent, and the third is the worst.**

1. **`audit_recap` fires the wrong warning.** It warns that *"a module was folded by the durability
   hooks but never finalized"* — true, and about a different problem. Nothing says a finalized
   module was deleted.
2. **The content-retention gate reports the recap as healthy.** `_source_content_chars` calls the
   same `_strip_discarded_fences`, so the deleted module is removed from the **denominator** as
   well as the numerator. Measured on the fixture above: **94% retention, no fatal.** A gate whose
   whole purpose is catching content loss actively reassures.
3. **`--expect-modules` cannot catch it either** — it checks that expected modules are *present*,
   never that they were not removed, which is the same asymmetry recorded in
   `recap-checkpoint-block-is-parsed-as-modules-instead-of-being-lifted`.

## Root cause

`generate_recap_pdf.py`, both handlers, same line shape:

- `_extract_notes_block` — `end = text.find(BOOTCAMP_NOTES_END, start)` (**pre-existing**)
- `_strip_discarded_fences` — `end = text.find(end_marker, start)` (**added 2026-09-01** by
  `recap-checkpoint-block-is-parsed-as-modules-instead-of-being-lifted`)

Each handles the *no END at all* case deliberately and documents the choice. Neither considers the
case where an END exists but belongs to a **different** fence — so a stray START silently annexes
the region up to the next fence's terminator.

⚠️ **The safety guard added on 2026-09-01 does not cover this, and its own comment says it should.**
`parse_recap` keeps the unstripped text when stripping would remove **every** module heading, and
its comment states the principle broadly: *"discarding those would delete the Bootcamper's real
module content to avoid phantom headings — a trade this must not make."* The guard implements only
the **total** case. Here two modules survive, so it does not engage, and exactly the trade it
forbids is made on the third.

⚠️ **This is a class, not an instance.** The notes handler shipped with the same flaw long before
the checkpoint one existed; the 2026-09-01 change added a second copy of it rather than
introducing it. Fixing one handler and not the other repeats the defect that spec was written for.

## Proposed change

1. **Bound the search for END by the next START.** If another START occurs between `start` and the
   END that was found, the first fence is unterminated and its END belongs to a later block. Apply
   the handler's existing unterminated-fence policy to that case instead of spanning both:
   - `_strip_discarded_fences` leaves the block in place (its documented choice), so the phantom
     headings render and the audit warns — the lesser loss it already argues for;
   - `_extract_notes_block` keeps its documented end-of-text behavior for a genuinely unterminated
     fence, which is safe because graduation appends notes last.
2. **Fix both handlers in the same change.** One rule, two fences — the shape this file has already
   been bitten by twice.
3. **Make the retention denominator honest about it.** `_source_content_chars` must not strip a
   region the parse path did not actually discard, or the gate keeps reporting a healthy percentage
   over deleted content.
4. **Consider warning distinctly** when a stray START is detected, rather than reusing the
   unfinalized-module warning, so the message names what happened.

## Acceptance criteria

- [ ] A recap with an unterminated fence followed by a terminated one retains every finalized
      module between them, for **both** the `RECAP-CHECKPOINT` and `BOOTCAMP-NOTES` fences.
- [ ] The genuinely-unterminated single-fence behavior is unchanged for both handlers, and both
      still document why they differ.
- [ ] The retention figure reflects content the parse path actually kept — a deleted module cannot
      be excluded from the denominator.
- [ ] The existing "surviving checkpoint block" warning still fires where it did before.
- [ ] A repo-level test covers the two-fence shape for both fences and asserts the module between
      them survives. Negative-controlled: restore the unbounded `find`, confirm it fails, revert.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `_extract_notes_block`,
  `_strip_discarded_fences`, `_source_content_chars`.
- `tests/test_recap_checkpoint_is_lifted_before_module_parsing.py` — extend, or a new guard.

## Source

- Feedback: none — found by `production-readiness-audit` on 2026-09-01, reading the 219 lines of
  shipped Python changed since the previous audit entry, which `conformance.py` does not scan
  (`Source: self-observed (assistant retrospective)`).
- Priority: **High** — it silently deletes a finalized module from `docs/bootcamp_recap.pdf`, the
  keepsake deliverable, while the content-retention gate reports the recap as healthy. Reaching a
  wrong artifact with no signal is the failure class this file's guards exist to prevent.
- MCP re-check: **n/a (no Senzing fact)** — string handling in a bundled generator.
- Upstream: not applicable
- Related specs: `recap-checkpoint-block-is-parsed-as-modules-instead-of-being-lifted.md` — added
  the second copy of this flaw and shipped the total-case guard that does not cover it.

## Deviations from this spec, and why (2026-09-01)

**The notes handler does NOT get its "existing unterminated-fence policy" applied to the stray
case, and the spec was wrong to propose it.** `## Proposed change` item 1 says to apply each
handler's documented unterminated policy when a stray START is found. For `_strip_discarded_fences`
that is right (leave the block in place). For `_extract_notes_block` the documented policy is
**sweep to end of text** — and applying it to a stray would delete *every* module after the stray
marker, which is strictly **worse** than the defect being fixed: the bug deleted the modules between
the two fences; the proposed remedy would delete those *and* everything after.

What shipped instead, for both handlers: a stray START is **skipped, not paired**. The
well-formed fence after it is still handled, its block still lifted, and the modules between them
survive. The end-of-text sweep is now reachable only when there is **no** well-formed block anywhere
— the genuinely-truncated case it was written for, where graduation's append-notes-last ordering
makes it safe.

**Item 4 ("consider warning distinctly") was implemented rather than considered.** `stray_fence_markers()`
reports every stray by marker and offset, and `audit_recap` emits a distinct warning naming it. This
was not optional: leaving the stray's region in place means content the fence was meant to lift stays
in the document, and for the notes fence that is a Bootcamper's private note one heading away from
the recap (INV-100). Neither silently deleting it nor silently rendering it is acceptable — so it is
named.

**Item 3 (the retention denominator) needed no separate change.** `_source_content_chars` calls
`_strip_discarded_fences`, so bounding the span fixed the denominator by construction: it now strips
exactly what the parse path strips, and a module the parse path keeps can no longer be excluded from
the count.

⚠️ **A trade that is deliberate and should not be "tidied" away.** With a stray fence present, the
stray block's own `## ` headings *do* parse as phantom module sections. That is the documented lesser
loss — the same judgment `_strip_discarded_fences` already records for a genuinely unterminated fence
— and it is now accompanied by a warning naming the malformed marker. Deleting a finalized module to
avoid a visible phantom section is the trade this file must not make.
