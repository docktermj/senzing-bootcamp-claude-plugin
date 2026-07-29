# Four interaction-layer defects the phase-3 walk found in the preface, preparation, and Module 0

Maintain the invariant conditions in @INVARIANTS.md and fix the following issue:

> **Found by a `/dry-run` phase 3 walk, 2026-07-29** — the maintainer answering as the Bootcamper
> through: onboarding preface → Bootcamp preparation (all four gates) → Module 0 primer → questions
> invitation → quiz offer. Choices: Core, `standard` verbosity, Python, Linux x86-64 detected, git
> initialized. These are the defects static analysis and phases 1–2 structurally cannot reach: three
> are prose that does not survive contact with the one-👉-per-turn rule or with the live MCP schemas,
> and one is a content gap on the highest-traffic question in the bootcamp.
>
> They are grouped in one spec because each is a two-to-five-line edit in one of two files, and
> splitting four small prose corrections into four specs is bureaucracy. Each carries its own
> acceptance criteria and can be implemented and reverted independently.

## Problem

### 1. The preface has no answer for "how long will this take?" (Medium)

Asked at `onboarding-flow.md` step 4 — *"Do you have any questions before we get started?"* — which
is the preface's only question, making this close to the single most likely thing a Bootcamper says
at that point. The plugin has nothing for it:

- Step 3's overview covers goal, modules, licensing, the recap PDF, and terminology help. **No
  duration.**
- Step 4 gives no instruction for answering a duration question.
- **INV-096's estimate rule is per-module and module-start-only.** `ground-rules.md:416` places it
  "after the step overview and before the model/effort prompt" and explicitly exempts the setup
  modules. It never contemplates the preface.
- **No per-module figures exist to sum.** The module skills state the *requirement* to give an
  estimate, not values. The only number anywhere in the plugin is ground-rules' illustrative
  `"Roughly 15-30 minutes, depending on download/install speed"` — an example of the *form*.

So the guide must improvise a duration at exactly the moment INV-096 exists to stop it inventing
one. The walk's assistant applied INV-096's spirit by refusing a total and leaning on the resume
machinery — but that was a rule written for somewhere else, reached for under improvisation. A
different assistant plausibly answers "about 4–6 hours".

The honest answer is also genuinely conditional: the total depends on the Core-vs-Customized choice
the Bootcamper has **not yet made**, and on install/download speed.

### 2. Bootcamp preparation Step 4 routes a language lookup to a tool that cannot answer it (Low-Medium)

`bootcamp-preparation/SKILL.md:248-249`: *"Call `get_capabilities` or `sdk_guide` on the Senzing MCP
server for the supported programming languages on that platform."* Verified against the live server
(1.32.2, 2026-07-29):

- `sdk_guide(topic='install', platform='linux_apt')` returns platform install detail — commands, env
  vars, default paths, gotchas. **No language list.**
- `sdk_guide(topic='install')` with no platform returns the **platform** decision tree, not a
  language one.

The language set lives in `get_capabilities`, and in the server's model it is
**platform-independent**: Python, Java and C# official; Rust and TypeScript/Node.js
community-maintained wrappers. What varies per platform is the install *mechanism* — which this same
step already tells the guide not to invent, deferring it to Module 2's routing rules and to
`sdk_guide(topic='install', platform=…, language=…)` at the point of need.

So "on that platform" mis-frames the fact: there is no per-platform language list to fetch. The one
genuine platform↔language constraint the server does state sits in the platform decision tree —
`docker` is the *"Fallback for Intel Mac, Windows without Scoop, or Python on macOS/Windows (the
Python SDK is only supported on Linux)"* — and is reachable without a platform argument.

This is the same class as the Truth Set finding fixed in `7683d61`: a documented step naming a call
that does not do what the step says.

### 3. Module 0's "re-present" plus a pinned wording produces a literal repeat (Low)

`module-00-entity-resolution-concepts/SKILL.md:46` instructs: answer the Bootcamper's question via
`search_docs`, verified with a second confirming call, *"then re-present"* the pinned 👉 — whose
wording INV-056 fixes verbatim:

> 👉 **Do you have any questions about entity resolution before we continue?**

So immediately after the Bootcamper has asked something and had it answered, the guide asks the
identical string again, which reads as though their question did not register.

**The preface solves this same situation the other way.** `onboarding-flow.md:139-140` says *"ask
once more whether they have **other** questions"*. Module 0 cannot do that without paraphrasing a
pinned string, so two files handle one conversational case incompatibly and Module 0's version is the
one that reads worse.

Narrower than it first appears: `concepts.md:83-85` deliberately stops this loop leaking into the
readiness gate, so the repeat is bounded to within the invitation.

### 4. Step 3's instruction order cannot be followed as written (Low)

`bootcamp-preparation/SKILL.md:179-200` sequences the verbosity step as: *"Wait for the answer, then
**hold** the chosen verbosity…"* → the yaml → *"Tell them they can change it any time… This is not a
⛔ gate, but it is still a 👉 question the bootcamper answers: wait for their reply."*

Followed literally, "tell them they can change it any time" lands **after** the answer, when it can
no longer inform the choice. Followed usefully, it must precede the question — because INV-005
requires the 👉 to end the turn, so nothing may follow it. Re-stating "wait for their reply" *after*
the tell is what makes the ordering read as if both were possible.

## Root cause

Items 1, 3 and 4 are all **prose written without the one-👉-per-turn constraint in view**: an
overview that never anticipated the question its own gate invites; a "re-present" verb that assumes
paraphrase is available when INV-056 forbids it; a step whose narrative order puts an
answer-informing sentence after the answer. Item 2 is **MCP routing imprecision** — a tool named for
a fact it does not carry, with a platform qualifier the server's model does not apply to that fact.

None of the four is detectable by reading the plugin against itself, which is why 937 tests and four
static audits missed them: each requires either a live schema call (item 2) or an actual
conversational turn (items 1, 3, 4).

## Proposed change

1. **Give the preface a duration answer.** Add one line to step 3's overview: the bootcamp is
   module-sized, each module states its own estimate at its start, and the total depends on the
   Core-vs-Customized choice and on install/download speed. Add a step-4 note that a duration
   question is answered that way and **never** with an invented total — citing INV-096's
   no-fabricated-number rule as the reason. Mention that progress is saved and the bootcamp can be
   resumed across sittings (INV-059/INV-094), which is the genuinely useful part of the answer.
2. **Fix the language-lookup routing.** In Step 4, name `get_capabilities` as the call for the
   supported programming languages, drop `sdk_guide` from that sentence, and state that the language
   set is platform-independent while the install mechanism is not. Keep the existing per-platform
   annotation rules and the existing prohibition on inventing install detail — both are correct.
3. **Pin a follow-up variant for the re-present.** Add a second pinned question to `concepts.md` for
   use after a question has been answered — e.g. *"Do you have any other questions about entity
   resolution before we continue?"* — and have `SKILL.md:46` name it, so the re-present satisfies
   INV-056 without repeating the first-ask wording verbatim. Do not loosen INV-056.
4. **Reorder Step 3's changeability note** so it precedes the question: "Before asking, tell them
   they can change it any time."

## Acceptance criteria

- [ ] Step 3's overview states that the bootcamp is module-sized, that each module estimates itself,
      and that the total depends on path and install/download speed.
- [ ] Step 4 instructs that a duration question is answered without a fabricated total, and says
      progress is saved across sittings.
- [ ] `bootcamp-preparation/SKILL.md` no longer routes a supported-programming-languages lookup to
      `sdk_guide`, and states that the language set is platform-independent.
- [ ] The existing per-platform annotation rules and the do-not-invent-install-detail prohibition are
      unchanged.
- [ ] `concepts.md` pins a follow-up ("other questions") variant, and `module-00/SKILL.md`'s
      re-present instruction names it rather than the first-ask wording.
- [ ] Module 0's first-ask wording is unchanged, and the gate still does not re-issue the invitation
      (`concepts.md:83-85` preserved).
- [ ] Step 3's changeability note precedes its 👉 question.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md): all four
      are interaction prose and MCP routing, independent of platform and of the Bootcamper's chosen
      programming language.

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — step 3 overview, step 4
  note (item 1).
- `plugins/senzing-bootcamp/skills/bootcamp-preparation/SKILL.md` — `:248-249` (item 2),
  `:179-200` (item 4).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/SKILL.md` — `:46` (item 3).
- `plugins/senzing-bootcamp/skills/module-00-entity-resolution-concepts/concepts.md` — the pinned
  follow-up variant (item 3).
- `tests/` — items 1, 2 and 3 are assertable; item 4 is a prose-order fix whose test would be
  brittle, so fix it without one and say so.

## Source

- Dry run phase 3, 2026-07-29, maintainer answering as the Bootcamper. `Source: self-observed
  (assistant retrospective)`; `Routing: plugin`; `Upstream: not applicable`.
- Priority: Medium (item 1); Low-Medium (item 2); Low (items 3 and 4)
- MCP re-check: **server 1.32.2**, 2026-07-29 — item 2's claim established live by calling both
  `sdk_guide` shapes and observing neither returns a language list. Items 1, 3 and 4 assert no
  Senzing fact. Note the server moved 1.32.1 → 1.32.2 *during* this session, and the doc index
  rebuilt (13,884 → 13,899 documents), so re-verify item 2 rather than trusting this note.
- Upstream: not applicable — all four are plugin-side.
- Related specs: `specs/dry-run-mcp-call-contracts.md` (INV-136 — item 2 is the same class),
  `specs/module-preface-time-estimate.md` (INV-096 — item 1 is the gap its per-module rule leaves),
  `specs/onboarding-explore-gate-wording.md` (INV-056 — the pinning item 3 must not loosen)

## Also observed, needing no change

- **The originating dry run's canonical unsatisfiable-rule finding is fixed and works.**
  `ground-rules.md:60-65` carves out the contentless answer and states outright that the requirement
  "is unsatisfiable as literally written" for a bare readiness signal. Exercised three times in this
  walk; correct each time.
- **INV-058 held:** two writes total (one per file) after four answered gates. The walk cannot check
  write *noise* — writes went via `Bash` — only the count.
- **Step 6's ⛔ self-check earns its place:** it asserted eleven tokens with
  `entity_resolution_concepts` present, the guard against the derivation that once silently dropped
  the primer from a Core run.
- **INV-112, INV-075/078, INV-056, INV-061/134, INV-095** all verified correct in the walk; see the
  `IMPLEMENTED.md` entry for the itemised list.
- **INV-080 held under pressure** on a general question ("is entity resolution known by other
  names?") where training data felt sufficient — the rule produced *added* precision (record linkage
  1946, Christen 2012, survivorship framing, and the MDM-is-not-a-synonym distinction).
