# Auto-detect the platform early and stop re-asking for it

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Two related frictions around operating-system handling:

1. **Module 2 asks for the OS it already knows.** Step 2 presents a mandatory
   numbered 👉 question — "What operating system are you on? Reply with a number:
   (1) Linux (2) macOS (3) Windows" — even though the environment/system context
   already provides the OS and architecture (the guide had just run `uname`
   confirming Apple Silicon). Asking for information the tool already has adds
   friction and makes the bootcamp feel less capable.
2. **Language is chosen without the OS-dependent install trade-off.** Language
   choice has real, OS-dependent consequences: on macOS Apple Silicon the Python
   SDK is Linux-only and must run in Docker, whereas Java/C# install natively.
   Today that trade-off is not surfaced at the language decision point, so a
   bootcamper can pick Python without knowing they have signed up for the Docker
   path — then hit it in Module 2.

## Root cause

- `module-02-sdk-setup/SKILL.md:100-110` hard-codes Step 2 as a mandatory numbered
  👉 OS question ("*(Internal: end the turn on this question and wait.)*"),
  independent of the environment context or anything onboarding already knew. The
  routing rules that follow (`:125-135`) derive the platform (e.g. Python +
  macOS/Windows → Docker) from the OS, but the OS itself is gathered by **asking**,
  not detecting.
- `onboarding-flow.md:156-163` (step 7, the programming-language gate) already says
  "Detect the platform, then call `get_capabilities`/`sdk_guide` … for the
  supported programming languages on that platform" and to relay
  discouraged/unsupported flags — but it does not (a) **state** the detected
  platform to the bootcamper, (b) **annotate** each language with its per-platform
  install path (the Docker trade-off), or (c) **persist** the detected OS/arch. The
  consolidated preface write (`onboarding-flow.md:168,185`) persists
  verbosity/track/language/name but **not** OS/arch, so Module 2 has nothing to
  reuse and re-asks.

## Proposed change

- **Onboarding step 7 (`onboarding-flow.md`):** before presenting languages,
  **detect OS + architecture deterministically** (environment/system context, else
  `uname`/`systeminfo`) and **state it** ("Detected macOS on Apple Silicon"). When
  presenting the MCP-returned language list, **annotate each option with its
  install path for the detected platform** (e.g. on macOS ARM: "Python — runs via
  Docker, the SDK is Linux-only; Java / C# — native"), consistent with the Module 2
  routing rules (`module-02-sdk-setup/SKILL.md:125-135`). **Persist `os`/`arch`** in
  the step-8 consolidated preface write so downstream modules can reuse it.
- **Module 2 Step 2 (`module-02-sdk-setup/SKILL.md:100-110`):** switch from a
  mandatory numbered question to **detect-then-confirm**. Read the persisted
  `os`/`arch` (or re-detect from the environment); **state the detected platform
  and proceed** without a numbered question when detection is unambiguous. Keep the
  pinned numbered 👉 question as a **fallback** only, shown when detection is
  missing/ambiguous, plus a one-line correction path ("say so if that's wrong").
  The platform-determination step is still executed (detection replaces the
  question as the primary path — the gate is **not** skipped), and the routing
  rules are unchanged.

## Acceptance criteria

- [ ] With OS/arch available from the environment, Module 2 Step 2 states the detected platform and proceeds **without** presenting the numbered OS question; the numbered question still appears as a fallback when detection is missing/ambiguous.
- [ ] The Module 2 fallback question keeps its exact wording pinned verbatim in the skill (INV-056) and the neutral-lead + numbered-list format (INV-009/INV-051); no 👉 step is dropped in a way that creates a dead-end turn.
- [ ] Onboarding step 7 states the detected platform and annotates each presented programming language with its per-platform install path (Docker vs. native), consistent with the Module 2 routing rules.
- [ ] The detected `os`/`arch` is persisted in the consolidated preface write (INV-058) and reused by Module 2 (no redundant re-ask).
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md).

## Affected files

- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/onboarding-flow.md` — step 7: detect + state platform, annotate languages with per-platform install paths, persist `os`/`arch` in the step-8 consolidated write.
- `plugins/senzing-bootcamp/skills/module-02-sdk-setup/SKILL.md` — Step 2: detect-then-confirm using the persisted/environment OS; keep the pinned numbered question as the fallback only.

## Source

- Feedback: `SENZING_BOOTCAMP_PLUGIN_FEEDBACK.md` → "Auto-detect the operating system instead of asking" and "Detect the OS before asking for the programming language" (2026-07-16, Module 2 Step 2 / Onboarding language gate).
- Priority: Medium.
- Related specs: `interaction-or-questions.md` (INV-051 numbered-list questions), `onboarding-explore-gate-wording.md` (INV-056 pinned gate wording), `suppress-admin-write-noise.md` (INV-058 consolidated preface write).

## Invariants introduced

- `INV-061` — The bootcamp MUST auto-detect the operating system and architecture (from the environment, else `uname`/`systeminfo`), persist them during onboarding, and reuse them in later modules rather than re-asking; a platform question may be presented only as a fallback when detection is genuinely unavailable or ambiguous, with its wording pinned verbatim (INV-056) (recorded in `specs/INVARIANTS.md`).
