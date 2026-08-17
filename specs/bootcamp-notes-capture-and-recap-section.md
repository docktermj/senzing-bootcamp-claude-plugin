# The Bootcamper can capture feedback about the plugin, but has nowhere to put an idea, a question, a reminder or a to-do of their own

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

The bootcamp has exactly one any-time capture channel, and it points **outward**: `feedback.md`
records what is wrong with the *plugin*, routes it (`plugin` | `mcp-server` | `both` | `host` |
`unclear`, INV-248), and offers to forward it to Senzing. It is a defect-report pipeline, and it is
the only durable thing a Bootcamper can write into during a run.

Nothing catches what points **inward** — the thought the Bootcamper has *about their own work*
while the bootcamp is running:

- *"Idea: we could map the vendor file's `dba_name` as a second NAME rather than payload."*
- *"Question: does `SzEngine.whyEntities` need a flag I haven't set?"*
- *"Reminder: check the truth-set counts against the source system before I trust this."*
- *"To-do: ask Legal whether we can load the third source at all."*

Today these have three destinations, all bad. Filed as feedback, they land in a defect file under a
`Routing:` verdict that fits none of them and pollutes the maintainer's triage input. Said in
passing, they are lost at the next compaction boundary. Written down outside the bootcamp, they are
absent from the one artifact the Bootcamper keeps.

The keepsake makes this concrete. `docs/bootcamp_recap.pdf` records, per module, what the bootcamp
told the Bootcamper, what the bootcamp asked them, and what the bootcamp did. **The Bootcamper's own
thinking during the run appears nowhere in it** — the closest thing is the optional
`**Bootcamper's takeaway:**` line, one line per module, written by the guide at module close.

## Root cause

Not a defect — the capability was never specified. INV-010 gives the Bootcamper one any-time
capture control (feedback) and INV-011 gives them one any-time preference control (verbosity);
`ground-rules.md:649-702` ("Any-time bootcamper controls") lists exactly four controls and none of
them is "write something down".

The recap has the matching gap in its structure. `generate_recap_pdf.py` parses the recap as a flat
list of module sections (`parse_recap`, `:525-617`) and every downstream consumer treats every `## `
heading as a module: `verify_recap` demands the four subsections of each (`:623-676`), `_cert_fields`
joins every title into the certificate's module citation (`:1736-1739`), `_render_toc` lists them
(`:2281-2294`), and the cover counts them (`:1663-1694`). **There is no representation for a recap
section that is not a module**, which is precisely what a notes section is.

## Proposed change

Four pieces: a capture flow, a trigger, a durable file, and a recap/PDF section.

### 1. The note capture flow — `bootcamp-onboarding/notes.md` (new)

A sibling of `feedback.md`, deliberately **not** a variant of it: no routing verdict, no upstream
offer, no `submit_feedback` path. A note is the Bootcamper's, it stays on their machine, and it ends
up in their keepsake rather than in the maintainer's inbox. Follow `ground-rules.md` throughout —
one 👉 question per yielding turn (INV-251), and the turn ends on it.

**Step 0 — capture context silently.** Time, `current_module`/`current_step` from
`config/bootcamp_progress.json`, and the pending 👉 question. Gather only from available sources;
never spend a question on it; record "Unknown" rather than a guess. This is what Step 3's option 2
offers to attach, so it must already be in hand when that question is asked.

**Step 1 — ensure `docs/bootcamp_notes.md` exists.** Create it with this header once:

```markdown
# Senzing Bootcamp Notes

Ideas, questions, reminders and to-dos captured during the Senzing Bootcamp, in your own
words. Every note here is folded into your recap at graduation and appears in
`docs/bootcamp_recap.pdf`. Nothing here is ever sent anywhere.

**Started:** YYYY-MM-DD

## Your Notes
```

It is a top-level `docs/*.md` file, so INV-017 is satisfied and graduation's normalizer picks it up
with the rest (see part 4).

**Step 1b — entry banner, pinned verbatim.** The first Bootcamper-facing moment of the flow, shown
before the first 👉 question, in the same turn. A statement, so it never counts against INV-251:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌📌📌  BOOTCAMP NOTE  📌📌📌
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

⛔ **The emoji is 📌, not 📝.** 📝 is the feedback banner's (INV-074). Two any-time flows that open
with the same glyph are two flows the Bootcamper cannot tell apart at a glance, which is the whole
reason INV-074 exists.

**Step 2 — get the note.** If the triggering message already carries it — *"remind me to check the
truth-set counts"* — **take it from the message and do not ask.** They already said it; asking is the
pointless question INV-006 and INV-012 forbid. Only when the trigger carried no content ("make a
note", `/bootcamp-note` with no argument) ask, pinned verbatim:

> 👉 **What would you like to note?**

**Step 2b — classify silently.** Assign a type — `idea` | `question` | `reminder` | `to-do` | `memo`
— from the wording, as an assessment, exactly as feedback Step 2b triages routing. ⛔ **Do not ask
for it.** The Bootcamper reported a thought; naming its kind is the plugin's job, and a 👉 spent on
a taxonomy is a 👉 spent on nothing they care about.

**Step 3 — recite for approval.** Show the note as it will be saved, then this pinned 👉 question
(INV-056), and end the turn on it:

> 👉 **Here's your note — save it as is? Reply with a number:**
>
> 1. **Save it** — exactly as written above.
> 2. **Add my bootcamp context** — record where I was when I made this note.
> 3. **Elaborate it** — expand it into a fuller note, marked as the bootcamp's words.
> 4. **Reword it** — I'll type the correction.

Options 2, 3 and 4 apply the change and **re-present the recital**. That is not a re-ask under
INV-006: the note being recited is different, and ask-once protects the Bootcamper from answering
the same question twice, not from confirming a changed artifact. Options 2 and 3 are each offered
**once** — once applied, that option drops off the list — so the loop is finite by construction and
the Bootcamper cannot be walked round it.

**Step 3b — attribution is structural, not stylistic.** The note body is the Bootcamper's words. An
elaboration (option 3) is stored under its own `**Elaboration:**` label and the context block
(option 2) under `**Context:**`. ⛔ **Never merge an elaboration into the note body.** This is a
keepsake with their name on the certificate; a paragraph they did not write, indistinguishable from
one they did, is the plugin putting words in their mouth permanently.

**Step 3c — the context block is machine-composed, so INV-065 binds it.** No hostname, username,
home-directory path or IP address. Module, step, time and the pending question are the content;
environment facts are not.

**Step 4 — append, then verify it landed.** Append (never rewrite) to `docs/bootcamp_notes.md`:

```markdown
### {Type}: {short title}

**Captured:** {ISO 8601 timestamp with timezone offset}
**Module:** {module name at capture time, or "General"}
**Type:** {idea | question | reminder | to-do | memo}

{the note, in the Bootcamper's own words, as approved}

**Context:** {module/step, the pending 👉 question, and the time — only when option 2 was taken}
**Elaboration:** {the bootcamp's expansion — only when option 3 was taken}
```

Then immediately re-read the file and confirm the entry is present; if it is missing, append again
and re-read. Only continue once it is confirmed on disk. This is `feedback.md` Step 3b's discipline
(INV-015) applied to the notes file, and for the same reason: a note the Bootcamper was told was
saved and which is not on disk is worse than one they know was never captured.

**Step 5 — exit banner and return.** Only after Step 4 confirms the entry on disk, present the
pinned exit banner verbatim:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌  NOTE SAVED — BACK TO THE BOOTCAMP  📌
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then one line: "Saved to `docs/bootcamp_notes.md` — it'll be in your recap at graduation. Add
another anytime by saying \"make a note\"." The banner and the line are statements; immediately
after them, re-present the exact pending 👉 bootcamp question verbatim, so exactly one 👉 ends the
turn (INV-006/INV-251). Do not merge the note flow's questions with the resumed bootcamp question.

**Non-blocking throughout (INV-048).** A failed write, a failed re-read, or an unreachable notes file
warns in one line and returns the Bootcamper to the bootcamp. A note is never a gate.

### 2. The trigger — `scripts/feedback-capture.py` and `/bootcamp-note`

Add a third branch to the existing `UserPromptSubmit` hook alongside `FEEDBACK` and `VERBOSITY`, and
extend the hook's documented purpose (INV-016 — it must still begin with "to").

⛔ **Inherit the asymmetry warning already in that file, do not repeat its mistake in a new
vocabulary.** The note pattern must be anchored on an **imperative to record something**, never on
the bare verb:

- **Fires:** "make a note", "take a note", "note to self", "jot (this/that) down", "remind me",
  "don't let me forget", "add a to-do", "put this on my list", "for my notes", "make a memo",
  "capture this idea", "bootcamp note", "remember to {verb}".
- ⛔ **Must not fire:** "do you remember", "remember when", "I remember", "note that {claim}", "as
  noted above", or any bare "remember"/"note" without a record-this imperative. In Modules 5-7 the
  Bootcamper is debugging their own code and asking the guide to recall things constantly; a
  spurious note capture there prepends a banner and a recital to a turn where they wanted a
  traceback explained.

A missed capture is far cheaper than a spurious one — the same trade the `FEEDBACK` comment block
argues, and for the same reason: the flow stays reachable by `/bootcamp-note` and by `notes.md`,
while a derailed debugging turn is not recoverable.

**Precedence when both patterns match** — "make a note that the bootcamp is broken" — is
**feedback**, and this must be stated in the code rather than left to branch order. `FEEDBACK`'s
fault half only matches when the bootcamp, plugin, module or tutorial is **named as the thing at
fault**, so a message satisfying both is an attributed defect report that happens to be phrased as a
note. Nothing is lost: the feedback flow is also durable, also banner-bracketed, and also returns the
Bootcamper to the pending question. Record the decision in a comment; it will be re-litigated
otherwise.

Add `commands/bootcamp-note.md` (`/bootcamp-note`, optionally taking the note as its argument),
mirroring `commands/bootcamp-feedback.md`.

### 3. Teach the control — `ground-rules.md`

Add a fifth entry to "Any-time bootcamper controls" (`:649-702`), stating the trigger phrasings, the
banners, the notes file, and that notes reach the recap at graduation. The control must also be
**named where the Bootcamper is told what they can do at any time** during the onboarding preface,
next to the existing feedback and verbosity affordances — an any-time control nobody is told about
is an any-time control nobody uses.

### 4. The recap section and the PDF page

**Where it goes in the Markdown.** At graduation Step 1a, after the module reconcile and **before**
the normalize pass and the render, fold `docs/bootcamp_notes.md` into `docs/bootcamp_recap.md`,
appended after the last module section, fenced by explicit markers:

```markdown
<!-- BOOTCAMP-NOTES:START -->
## Notes, Ideas and Questions

{the note entries, in capture order}
<!-- BOOTCAMP-NOTES:END -->
```

⛔ **The fence is the discriminator, not the heading text.** Every `## ` heading in the recap is
parsed as a module (`parse_recap:562-578`), so a notes section recognized by its *title* is one
renamed module away from being mis-parsed, and a Bootcamper's note is one heading away from being
cited on their certificate. The marker convention is already in this file for exactly this reason —
`RECAP-CHECKPOINT:START`/`:END` (`generate_recap_pdf.py:119-123`).

The fold is **append-only and idempotent** (INV-085): re-running graduation does not duplicate it,
and it never touches a module section. When there are no notes, **write nothing** — no section, no
heading, no "(none)" page. An empty section on a keepsake is worse than an absent one.

**Where it goes in the PDF.** Between the last module page (Query, Visualize and Discover on a Core
run) and the Certificate of Completion — that is, rendered after the module loop and before
`_render_certificate`, in `render_with_fpdf2` (`:1500-1512`) **and** in the stdlib fallback
(module loop `:2874-2891`), which INV-066 requires to keep parity. The stdlib path has no table of
contents, so the TOC row below applies to the fpdf2 renderer only; its cover carries a
`Modules completed:` line instead (`:2861-2867`), which the notes title must stay out of for the same
reason it stays off the certificate.

**What must change in `generate_recap_pdf.py`, and what must not:**

| Concern | Required behavior |
|---|---|
| `parse_recap` | The fenced block is parsed into a new `Recap.notes` field, **not** into `Recap.modules`. |
| `verify_recap` / `--check` | Never demands the four module subsections of the notes section. A recap whose only defect is "notes present" reports zero problems. |
| `_cert_fields` (`:1736-1739`) | The notes title MUST NOT appear in the certificate's module citation (INV-100 — it certifies modules completed). |
| Cover module list/count (fpdf2 `:1663-1694`, stdlib `:2861-2867`) | Unchanged by the presence of notes. |
| `_render_toc` (`:2281-2294`, fpdf2 only) | Gains one row for the notes section, with its real start page, **after** the module rows. |
| `_rendered_content_chars` (`:695`) | **Counts the notes section's characters.** ⚠️ Miss this and a Bootcamper with a lot of notes gets a retention figure that falls with every note they wrote, and a long enough notes file crosses `MIN_CONTENT_RETENTION` (0.60) and makes the generator refuse to render their recap (INV-110). The fence markers themselves are excluded from `_source_content_chars`, like `---` already is. |
| Two-pass pagination (`:1491-1512`) | The measure pass and the final pass MUST both render the notes page. Rendering it in one and not the other shifts every TOC page number after it. |
| `audit_recap` "bodyless" refusal (`:986-996`) | Unaffected — the notes section is not among the `## ` sections it counts. |

**Rendering.** One page (continuing onto further pages as needed), styled as the module pages are but
visibly its own thing — its own header band color and a heading that reads as the Bootcamper's rather
than the bootcamp's. Each note renders its type, its title, its timestamp, the module it was captured
in, the body, and — when present — the labeled `Context:` and `Elaboration:` blocks, with the
elaboration visibly attributed to the bootcamp.

**Graduation housekeeping.** Add `docs/bootcamp_notes.md` to Step 2's **Exclude (never copy)** list
for `production/` — it is a bootcamp artifact, not production content, exactly as
`docs/bootcamp_recap.md` and `docs/feedback/` are. It stays in the normalizer's `docs/*.md` glob
(desirable: it is prose, and the normalizer's content fingerprint restores the file on any loss), and
it survives graduation intact on disk in addition to being folded into the recap.

## Deviations from the requested steps, and why

The request listed six steps. Five are implemented as asked. **The elaborate/context/recite steps
(2, 3, 4) are consolidated into the single recital question** in Step 3 above, rather than asked as
three consecutive 👉 questions.

The reason is turn cost. INV-251 puts each 👉 on its own yielding turn, so the requested shape makes
*"remind me to check the truth-set counts"* — a five-second thought — cost four round trips before
the Bootcamper gets back to the module they were in the middle of. A capture affordance that
expensive gets used once and then abandoned, which defeats the feature. The consolidated recital
offers the same three choices, in the numbered-list shape the plugin already uses for its other
multi-way questions (`feedback.md` Step 3c, graduation Step 2), and costs one turn for the common
case where the note is fine as written.

⚠️ **This is the one judgment call in the spec that is easy to reverse.** If the maintainer wants
the three questions asked separately, only Step 3 of `notes.md` changes; nothing else in this spec
depends on it.

## Acceptance criteria

- [ ] A Bootcamper saying "make a note", "remind me", "don't let me forget", "add a to-do", "note to
      self", "jot this down" or `/bootcamp-note` enters the note flow, from any module, onboarding or
      graduation.
- [ ] "Do you remember what module 3 covered?" and similar bare recall requests do **not** enter it.
- [ ] A message matching both the note and feedback vocabularies enters the **feedback** flow, and
      the precedence is stated in `feedback-capture.py` rather than implied by branch order.
- [ ] The flow opens with the pinned 📌 **BOOTCAMP NOTE** banner and closes with the pinned
      📌 **NOTE SAVED — BACK TO THE BOOTCAMP** banner (a statement), both verbatim from `notes.md`.
- [ ] When the triggering message already contains the note, the "What would you like to note?"
      question is **not** asked (INV-006).
- [ ] The note is recited before it is saved, and is saved only after the Bootcamper approves it.
- [ ] Elaboration and context are stored under their own labels, never merged into the Bootcamper's
      own words; the context block contains no hostname, username, home path or IP (INV-065).
- [ ] Every approved note is appended to `docs/bootcamp_notes.md` and confirmed present by a re-read
      before the Bootcamper is told it was saved; a failed write warns and never blocks (INV-048).
- [ ] After the exit banner, the exact pending 👉 bootcamp question is re-presented verbatim, and the
      turn ends on exactly one 👉 (INV-251).
- [ ] At graduation the notes are folded into `docs/bootcamp_recap.md` inside
      `<!-- BOOTCAMP-NOTES:START/END -->`, appended after the last module section, idempotently and
      without touching any module section (INV-085).
- [ ] `docs/bootcamp_recap.pdf` renders the notes section between the last module page and the
      Certificate of Completion, in **both** the fpdf2 renderer and the stdlib fallback (INV-066).
- [ ] The notes section is never treated as a module: absent from the certificate's module citation
      (INV-100), absent from both renderers' cover module lists, and never reported by `--check` as
      missing the four module subsections.
- [ ] The notes section **is** in the fpdf2 renderer's table of contents, with a correct page number,
      and TOC page numbers for every preceding page are unchanged.
- [ ] The notes section's characters count toward the generator's content-retention figure, so a
      Bootcamper with many notes never sees retention fall or the render refuse (INV-110).
- [ ] With no notes captured, nothing changes: no notes file is folded, no section, no TOC row, no
      page — and an existing recap without the fence renders exactly as it does today.
- [ ] `docs/bootcamp_notes.md` is excluded from `production/` and survives graduation intact.
- [ ] Tests cover the trigger vocabulary (both halves and the precedence rule) and the generator
      (notes page placement, certificate exclusion, TOC row, retention accounting, and the no-notes
      no-op).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/notes.md` — **new**; the capture flow.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — fifth any-time control
  (`:649-702`).
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — name the control where
  the Bootcamper is told what is available at any time.
- `plugins/senzing-bootcamp/commands/bootcamp-note.md` — **new**; `/bootcamp-note`.
- `plugins/senzing-bootcamp/scripts/feedback-capture.py` — third branch, precedence comment, updated
  docstring/purpose (INV-016).
- `plugins/senzing-bootcamp/hooks/README.md` — the hook's Purpose column ("to …", INV-016).
- `plugins/senzing-bootcamp/skills/graduation/SKILL.md` — Step 1a fold (before normalize and render);
  Step 2 exclusion list.
- `plugins/senzing-bootcamp/scripts/generate_recap_pdf.py` — `Recap.notes`, fenced parse, both
  renderers, TOC row, retention accounting, certificate/cover exclusion.
- `plugins/senzing-bootcamp/docs/examples/bootcamp_recap.example.md` / `.example.pdf` — regenerate so
  the shipped reference shows the section (`tests/test_example_recap_sync.py` compares them).
- `tests/test_feedback_capture_triggers.py`, `tests/test_recap_pdf_guard.py` — extend; plus a new
  guard for notes placement and certificate exclusion.

## Source

- Maintainer feature request, 2026-08-16: "Similar to 'bootcamp feedback', the Bootcamper needs a way
  to jot down ideas, questions, reminders, memos, etc. … During Bootcamp Graduation, all ideas,
  questions, reminders, memos, etc. will be added to a new section in the `bootcamp_recap.pdf`
  document. This section will be between 'Query, Visualize and Discover' and the 'Certificate of
  Completion'."
- Priority: Medium — no defect is being fixed; a missing capability is being added.
- MCP re-check: n/a (no Senzing fact). Everything here is plugin-owned: the flow, the hook, the
  generator and the recap.
- Upstream: not applicable.
- Related specs: `specs/feedback-flow-boundary-banner.md` (the banner-bracketing precedent this
  reuses, INV-074); `specs/feedback-file-durability.md` (the verify-it-landed discipline);
  `specs/feedback-capture-misses-natural-phrasings.md` (why the trigger vocabulary is widened
  carefully rather than aggressively); `specs/certificate-of-completion-from-template.md` (what the
  certificate cites, and why the notes title must stay out of it).

## Invariants introduced

⚠️ **The five ids shifted up by one at implementation time.** `us-english-spelling-is-unregistered-and-unguarded`
landed first and took `INV-253`, so these were re-derived per @INVARIANTS.md's "next unused
`INV-NNN`" rule. The wording is unchanged from what this spec drafted.

- `INV-254` — At any time, a Bootcamper can capture a note (idea, question, reminder, to-do or memo),
  from onboarding, any module, or graduation. (The inward counterpart to INV-010.)
- `INV-255` — The note capture flow MUST be bracketed by pinned-verbatim banners — a 📌 "BOOTCAMP
  NOTE" entry banner before its first 👉 question, and a 📌 "NOTE SAVED — BACK TO THE BOOTCAMP" exit
  banner (a statement) after the note is confirmed saved and before the pending bootcamp 👉 question
  is re-presented — using a glyph distinct from the feedback flow's 📝 (INV-074).
- `INV-256` — Every approved note MUST be appended to `docs/bootcamp_notes.md` and confirmed present
  on disk by a re-read before the Bootcamper is told it was saved.
- `INV-257` — A note MUST be recited to the Bootcamper for approval before it is saved, MUST be
  stored in the Bootcamper's own words, and any bootcamp-authored elaboration or context MUST be
  stored under its own label, never merged into the Bootcamper's text.
- `INV-258` — When the recap carries a `<!-- BOOTCAMP-NOTES:START/END -->` section, the recap PDF
  MUST render it between the last module page and the Certificate of Completion in both renderers
  (INV-066), MUST list it in the table of contents where the renderer has one, MUST count its
  characters toward the content-retention figure (INV-110), and MUST NOT treat it as a module — it
  never appears in the certificate's module citation (INV-100), in either renderer's cover module
  list, or in the four-subsection check (INV-103).

## Deviations from this spec, and why (2026-08-16)

1. **The five invariants are `INV-254`–`INV-258`, not `INV-253`–`INV-257`**, as recorded above.

2. ⛔ **An unterminated fence now runs to end of text, which this spec did not specify.** The first
   implementation treated a missing `<!-- BOOTCAMP-NOTES:END -->` as "no fence present" — and that
   is the one failure mode this whole section is designed to prevent: the `## Notes, Ideas and
   Questions` heading is then parsed as a **module**, which puts a Bootcamper's private note on
   their Certificate of Completion (INV-100). Since graduation appends the block *after* the last
   module section, everything past the opening marker is notes, so running to end of text is both
   safe and correct. Caught by a negative control written for the opposite expectation.

3. **Retention is accounted at parse time from the lines the parser placed, not recomposed from the
   fields.** Summing `title + type + captured + module + body + context + elaboration` undercounts
   every note by its label markup — `**Captured:** ` is 14 characters the renderer draws as a stamp
   rather than as literal text — so retention fell measurably with each note added (0.94 → 0.89 on
   the test fixture). That is the exact direction of failure criterion 14 forbids, merely too small
   to cross `MIN_CONTENT_RETENTION` on a short file. Lines the parser could **not** place stay
   uncounted, so a note that fails to parse still registers as content loss.

4. **`tests/test_example_recap_sync.py` needed its sampler taught about `Elaboration:`** — not in
   `## Affected files`, but required. That sampler compares each source line against the PDF's
   extracted text, and the renderer draws the elaboration's label separately from its value (the
   label carries the "written by the bootcamp" attribution INV-257 requires on the page). This is
   the same shape as the existing `Why it matters:` carve-out immediately above it, for the same
   reason. `Context:` needed no rule: its label is drawn immediately before its value, so the
   squashed run still matches.

5. **`tests/test_invariant_enforcer_citations.py` needed `EXPECTED_PAIRS` raised 66 → 73** — also
   unlisted, also required, since each new invariant names its enforcing test and that guard pins
   the invariant→test pair count deliberately rather than tracking it.

6. **A second guard file was added beyond the two the spec names.** `tests/test_recap_notes_section.py`
   covers the generator as specified; `tests/test_bootcamp_notes_flow.py` covers the shipped
   **prose** contract — the banners and their glyph, the no-routing/no-upstream boundary, the
   attribution rule, the graduation fold and the `production/` exclusion. Without it INV-255,
   INV-256 and INV-257 would have been registered with no enforcer at all, since every one of them
   governs a rule that lives in Markdown rather than in code.

7. ⚠️ **Nothing here is runtime-verified as a conversation.** Whether a live turn presents the
   banner, asks exactly one 👉, and re-presents the pending question verbatim cannot be tested by
   an offline suite (INV-108) — it needs `dry-run` phase 3. The static half is fully asserted; the
   conversational half is disclosed, not ticked.
