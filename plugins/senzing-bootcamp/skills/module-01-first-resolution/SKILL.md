---
name: module-01-first-resolution
description: Bootcamp Module 1 — run a first Senzing entity-resolution demo. Use when the bootcamper starts or resumes Module 1, or asks to run their first resolution.
---

# Module 1: Your First Entity Resolution

**Goal:** the bootcamper loads a small set of sample records and sees Senzing resolve them.

Follow the ground rules in `bootcamp-onboarding` (MCP-only facts, project-relative files,
progress tracking).

## Steps

1. **Get sample data.** Use the `get_sample_data` MCP tool to obtain a small demonstration
   dataset appropriate for a first run.
2. **Scaffold the environment.** Use `generate_scaffold` (workflow `initialize`) in the
   bootcamper's chosen language to produce initialization code. Do not hand-write it.
3. **Map the records.** Use `mapping_workflow` to map the sample source records into the
   Senzing JSON format. Never hand-code attribute names.
4. **Load and resolve.** Guide the bootcamper to load the records and run resolution using
   the generated code.
5. **Explore the result.** Help them search for an entity and read the resolved output.
   Explain what matched and why in plain language.

## Completion

- Summarize what the bootcamper accomplished.
- Update `.bootcamp/progress.json` to mark Module 1 complete.
- Offer to continue to the next module.
