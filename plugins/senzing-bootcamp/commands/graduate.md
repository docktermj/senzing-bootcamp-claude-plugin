---
description: 'Graduate the Senzing bootcamp: generate the recap PDF and a production-ready project.'
---

The bootcamper wants to graduate the Senzing bootcamp.

Invoke the `graduation` skill and follow it: show the GRADUATION banner, finalize
`docs/bootcamp_recap.md` and render `docs/bootcamp_recap.pdf`, build the
`production/` project, and end with the guaranteed-recap announcement and the
single closing 👉 question.

The bundled recap PDF generator is available at
`${CLAUDE_PLUGIN_ROOT}/scripts/generate_recap_pdf.py`; pass that path when the
graduation skill renders the PDF.

If no `config/bootcamp_progress.json` exists in the working directory, tell the
bootcamper there is no bootcamp to graduate and offer to start one with
`/start-bootcamp`.
