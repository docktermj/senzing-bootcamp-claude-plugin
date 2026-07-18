"""Senzing brand tokens — the single, shipped source of truth for visual styling.

Extracted from the Senzing "Obsidian & Ember" style reference
(`resources/senzing-style-reference.pdf`, a maintainer asset that is NOT shipped
with the plugin). The generators that produce bootcamper-facing visual
deliverables — the Truth-Set visualization web app / snapshot
(`senzing_viz_server.py`) and the recap PDF trophy (`generate_recap_pdf.py`) —
consume these tokens so every artifact shares one look and feel, rather than each
hardcoding its own ad hoc palette.

Both consumers import this module from their own directory (it ships alongside
them in `scripts/`) and fall back to an inlined copy of these same values if the
import ever fails, so they never depend on the PDF at runtime and keep working
even in isolation (mirrors the vendored-D3 offline fallback).

Style-guide key rules encoded here:
- Dark backgrounds are Obsidian/Deep, never pure black.
- The accent is the ember family (ember-core on light, ember-hot as the hotter
  tone), never a flat unrelated orange/red.
- Signal green is reserved for live/resolved states — never decorative. It is NOT
  used for categorical data-source node colors.
- Light sections are warm off-white, never cold grey.
- Body text is softer than headline ink; headlines are strongest.
"""

# --- Core dark palette ----------------------------------------------------- #
OBSIDIAN = "#0F0D0C"          # global dark background
DEEP = "#18160F"             # nav & cards on dark; also dark ink on light
SURFACE_DARK = "#201E16"     # elevated surface on dark

# --- Ember accent ---------------------------------------------------------- #
EMBER_HOT = "#FF4E1F"        # section labels on dark; hotter accent tone
EMBER_CORE = "#F57826"       # headlines/accent on light; primary accent
EMBER_GRAD_START = "#FF4E1F"  # button/grad-text gradient start
EMBER_GRAD_END = "#F0920A"   # button/grad-text gradient end
EMBER_SOFT = "#FDEEE3"       # derived: light ember tint for chips/pills on light

# --- Reserved signal color (live/resolved states ONLY, never decorative) --- #
SIGNAL_GREEN = "#1D9E75"

# --- Light palette (body sections) ----------------------------------------- #
WHITE = "#FFFFFF"            # light section background
WARM_OFF_WHITE = "#FAF8F3"   # warm off-white (never cold grey)
DARK_INK = "#18160F"         # headlines on light
BODY_INK = "#4A4640"         # body text on light (softer than headline ink)
WARM_LINE = "#E5DFD3"        # derived: warm border/divider on light sections

# On-dark text conventions (headlines pure white; body 60% white).
TEXT_ON_DARK = "#FFFFFF"
MUTED_ON_DARK = "rgba(255,255,255,0.6)"
CARD_BORDER_ON_DARK = "rgba(255,255,255,0.08)"

# --- Typography ------------------------------------------------------------ #
# The guide specifies Roboto (Google Fonts). To stay offline-safe (INV-071 — no
# network at render time) we prefer Roboto when the OS has it and fall back to
# system sans; we do NOT @import a web font. The recap PDF uses fpdf2's built-in
# Helvetica as an offline, dependency-free stand-in (embedding a Roboto TTF would
# add a shipped-asset dependency the "always produces a PDF" guarantee avoids).
FONT_STACK = "Roboto, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
CODE_FONT_STACK = "'Fira Code', 'Courier New', Courier, monospace"
PDF_FONT = "Helvetica"

# --- Categorical data-source node colors (functional data-viz) ------------- #
# The style guide does not define data-source colors; categorical distinctness
# matters here ("where appropriate" latitude). The primary source is anchored to
# ember; signal green is deliberately excluded (reserved). Kept brand-harmonious.
SOURCE_COLORS = {
    "CUSTOMERS": EMBER_CORE,
    "REFERENCE": "#3B6EA5",
    "WATCHLIST": "#C8922A",
}
FALLBACK_COLORS = ["#8b5cf6", "#ec4899", "#0ea5e9", "#a3a34a", "#ef4444", "#14b8a6"]


def hex_to_rgb(value):
    """'#RRGGBB' -> (r, g, b) ints, for renderers that take RGB tuples (fpdf2)."""
    v = value.lstrip("#")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
