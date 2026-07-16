# Evaluate best-value model/effort per skill and capture the configurability findings

Maintain the invariant conditions in @INVARIANTS.md and implement the following improvement:

## Problem

Every plugin skill currently runs on whatever model and reasoning effort the
bootcamper's session happens to be set to — there is no per-skill guidance, and
no captured analysis of which model is the best *value* for each skill's
workload. The plugin ranges from cheap conversational turns (onboarding,
Module 1 discovery) to expensive correctness-critical work (SDK install/config,
Senzing mapping, production-project generation), so a single blanket model is
either over-paying on the light skills or under-powering the heavy ones. Before
tuning anything we also need the facts straight: which plugin component types can
even carry a model/effort override, and with what scope — otherwise "set the
model per skill" gets wired in a way that silently does not do what it looks
like it does.

## Findings (Claude Code model/effort configurability)

Verified against current docs (`code.claude.com/docs/en/{skills,sub-agents,hooks}.md`,
`platform.claude.com/docs/en/about-claude/models/overview`). A model/effort
override only means anything for components that actually invoke Claude;
`type: command` hooks and the scripts they run are deterministic programs and
never "run under a model."

| Component | Different model? | Different effort? | How / scope |
|---|:---:|:---:|---|
| **Skills** (`SKILL.md` frontmatter) | ✅ | ✅ | `model:` + `effort:` (`low`/`medium`/`high`/`xhigh`/`max`). **Turn-scoped.** |
| **Slash commands** (`.md` frontmatter) | ✅ | ❌ | `model:`; no effort field |
| **Subagents** (`agents/*.md`) | ✅ | ✅ | `model:` (`inherit` default) + `effort:`; persists for the subagent's whole run |
| **Command hooks** (`type: command`) | ❌ | ❌ | Deterministic program; only *reads* session effort via `$CLAUDE_EFFORT` |
| **Prompt hooks** (`type: prompt`) | ✅ | ❌ | `model:` in hook config |
| **Agent hooks** (`type: agent`) | ➖ | ➖ | Inherits the spawned subagent's `model:`/`effort:` |
| **Scripts** (run by hooks/commands) | ❌ | ❌ | Not model-executed |

**The load-bearing constraint — a skill override is turn-scoped.** From
`skills.md`: *"The override applies for the rest of the current turn and is not
saved to settings; the session model resumes on your next prompt."* The bootcamp
skills are **interactive and multi-turn** — every step yields to the bootcamper
after one 👉 question, so each subsequent step is a *new user prompt* and the
override resets to the session model/effort. A `model:` on a module skill
therefore governs only the module-start turn, not the module. **The reliable
lever for the bootcamp is the session model/effort, not per-skill `model:`
frontmatter.** Sustained per-skill model control is only available via
`context: fork` (the skill runs in a subagent that holds its own `model:`/`effort:`
for its whole run) — but forking moves the work into an isolated subagent, which
is wrong for the interactive teaching skills that must converse turn-by-turn.

**Model positioning (for "best value").** Fable 5 is **top-tier**, not a budget
tier: ~$10/$50 per MTok, always-on adaptive thinking, slower, aimed at
long-running agents. Opus 4.8 (~$5/$25) is the complex-coding default; Sonnet 5
(~$3/$15) is the speed/cost/capability sweet spot with adaptive thinking; Haiku
4.5 (~$1/$5) is the budget tier and has **no** adaptive thinking. For a
protocol-heavy (⛔ gates, INV-056 pinned wording, one-👉-per-turn) MCP-first
teaching plugin, Haiku's lack of adaptive thinking is a real risk of gate/format
slips, and Fable's 2× premium buys little the workloads here need.

## Per-skill evaluation (best value = capability the workload needs, at the lowest tier that meets it)

| Skill | Workload | Best-value model | Rationale |
|---|---|:---:|---|
| `bootcamp-onboarding` | Gated preface, exact-wording gates, preference capture | **Sonnet 5** | Protocol adherence (⛔ gates, INV-056 pinned text, one-👉) needs adaptive thinking + strong instruction-following; no heavy code → Opus is overkill, Haiku is risky. |
| `module-01-business-problem` | Discovery conversation, document the problem | **Sonnet 5** | Conversation-led, light technical. |
| `module-02-sdk-setup` (696 lines) | Cross-platform install, license/engine/DB config, build-from-source recovery | **Opus 4.8** | Largest, most error-prone, platform-specific; install/config errors are high-cost to recover — pay up for reasoning. |
| `module-03-system-verification` | Run viz server, verify, report | **Sonnet 5** | Mostly run / check / report. |
| `module-04-data-collection` | Gather sources into `data/raw/` | **Sonnet 5** | Data wrangling + light code. |
| `module-05-data-quality-mapping` | Quality scoring + mapping to the Entity Spec via `mapping_workflow` | **Opus 4.8** | Mapping correctness drives resolution quality — the technical crux; needs strong reasoning + careful MCP use. |
| `module-06-data-processing` | Load mapped data (SDK), validate, load-safety rails | **Sonnet 5** (Opus if bespoke load logic) | Heavy mapping already done in M5; M6 executes/validates loads with guardrails. |
| `module-07-query-visualize-discover` | Query SDK code, visualize, discovery | **Sonnet 5** | Iterative query/exploration; Sonnet's speed suits it. |
| `graduation` (199 lines) | Recap reconcile, PDF, production project (code/config/docs), report | **Opus 4.8** | Crown-jewel deliverable; production code/config generation correctness matters most. |

**Summary recommendation:** **Sonnet 5 as the bootcamp session default**, elevated
to **Opus 4.8** for the three correctness-critical workloads — Modules 2 and 5 and
graduation (optionally Module 6 with custom load code). **Haiku 4.5** is not
recommended for any bootcamper-facing skill (protocol risk); **Fable 5** is not
the value pick here. Because skill overrides reset per prompt, realize this by
switching the **session** model up for those modules — not by trusting per-skill
`model:` frontmatter to hold across a module.

## Proposed change

Guidance/documentation only — no behavioral code, and deliberately **not** a
blanket `model:` on every skill (that would imply cross-turn control the
mechanism does not provide):

- **Add a maintainer reference doc** `plugins/senzing-bootcamp/docs/model-selection.md`
  capturing the two tables above (the component capability matrix and the
  per-skill evaluation), the turn-scope constraint with its `skills.md` citation,
  the Fable-5-is-top-tier note, and the summary recommendation — so this is not
  re-investigated (same "record the finding" pattern as `suppress-admin-write-noise`).
- **Record the session-model recommendation** where the maintainer will see it:
  a short pointer from `README.md` to the new doc, and a one-line note in
  `bootcamp-onboarding/ground-rules.md` that the bootcamp is tuned for a **Sonnet 5**
  session with **Opus 4.8** suggested for Modules 2/5 and graduation.
- **Optionally** add `effort:` frontmatter (e.g. `high`) to the heaviest
  single-turn steps' skills (`graduation`, `module-02-sdk-setup`,
  `module-05-data-quality-mapping`), documented in the reference doc as
  **invoking-turn-only** so no one mistakes it for a module-wide setting. Do
  **not** add per-skill `model:` frontmatter to the interactive skills.

## Acceptance criteria

- [ ] `plugins/senzing-bootcamp/docs/model-selection.md` exists and contains: the component capability matrix, the per-skill best-value table covering **all nine** plugin skills, the turn-scope constraint (with the `skills.md` quote), and the Fable-5 positioning note.
- [ ] The summary recommendation (Sonnet 5 default; Opus 4.8 for Modules 2/5 + graduation; Haiku/Fable not the value pick) is recorded, and the doc states plainly that skill `model:`/`effort:` overrides are turn-scoped so the session model is the primary lever.
- [ ] `README.md` points to the new doc; `ground-rules.md` carries the one-line session-model note.
- [ ] No interactive skill gains a `model:` override that would misrepresent turn-scope; any `effort:` added is labeled invoking-turn-only.
- [ ] Holds on Linux, macOS, and Windows and stays language-agnostic (per @INVARIANTS.md) — trivially, the change is documentation.

## Affected files

- `plugins/senzing-bootcamp/docs/model-selection.md` (new) — the findings + per-skill evaluation + recommendation.
- `README.md` — pointer to the model-selection doc.
- `plugins/senzing-bootcamp/skills/bootcamp-onboarding/ground-rules.md` — one-line session-model note.
- (optional) `plugins/senzing-bootcamp/skills/graduation/SKILL.md`, `module-02-sdk-setup/SKILL.md`, `module-05-data-quality-mapping/SKILL.md` — add invoking-turn-only `effort:` frontmatter if adopted.

## Source

- Maintainer request (2026-07-16): capture the plugin model/effort configurability findings and evaluate each skill for its best-value model.
- Priority: Low (advisory tuning + documentation; no bootcamper-visible behavior change).
- Related specs: `suppress-admin-write-noise.md` (the "document the finding so it is not re-investigated" pattern), `defer-commonmark-to-graduation.md`.

## Invariants introduced

- None proposed. Model recommendations are advisory and version-dependent — pinning a specific model as a permanent invariant would age badly as the model lineup changes. The durable finding worth remembering (skill `model:`/`effort:` overrides are turn-scoped, so the session model is the bootcamp's real lever) is captured in the reference doc rather than as an invariant.
