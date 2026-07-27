"""No text path may hand fpdf2's Latin-1 core font a character it cannot encode.

The recap PDF has two renderers: a designed fpdf2 one and a plainer stdlib fallback.
INV-048 wants the professional-looking artifact, so the fpdf2 path is the one bootcampers
should normally get; INV-111 requires *saying* when a fallback happens. Both worked. What
failed was subtler and only a dry run against a realistic recap exposed it.

`_clip()` truncated with a U+2026 "…" — and every call site is `_clip(_safe(x), n)`, so
`_safe` runs **first** and never sees the character `_clip` appends afterwards. fpdf2 then
raised `Character "…" … outside the range of characters supported by the font used`,
`render_with_fpdf2` caught it exactly as designed, and the only visible symptom was the
bootcamper quietly receiving the plainer PDF. `_UNICODE_MAP` already mapped "…" to "..." —
the defect was purely order of operations.

It fired on the cover's module chips, `_clip(..., 46)`: "Data Quality, Mapping, and
Transformation" is 41 characters and survives bare, so the shipped example recap renders
fine, but it clips the moment a number prefix or timestamp is appended. That is why no
existing test caught it — the fixture was just under the threshold.

What this pins:

* `_clip` introduces nothing outside Latin-1, at every width the source actually uses.
* The shipped composition order `_clip(_safe(x))` survives adversarial input.
* `_UNICODE_MAP` covers the non-ASCII characters the plugin's own recap templates use.
* End-to-end (skipped without fpdf2, which is not stdlib — INV-108): a recap whose title
  is long enough to clip still renders with **fpdf2**, not the fallback.

Run:  python3 -m unittest discover -s tests
"""
import importlib.util
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = (
    REPO_ROOT / "plugins" / "senzing-bootcamp" / "scripts" / "generate_recap_pdf.py"
)


def load_generator():
    """Import the generator by path.

    It must be registered in ``sys.modules`` before ``exec_module``: the generator
    defines dataclasses, and ``dataclasses._is_type`` resolves annotations through
    ``sys.modules[cls.__module__]``, which is ``None`` for an unregistered module.
    """
    import sys

    spec = importlib.util.spec_from_file_location("_recap_gen", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GEN = load_generator()

# Characters the plugin's own recap templates and module names actually contain.
TEMPLATE_CHARS = ("—", "…", "·", "→", "’", "“", "”", "✅", "👉", "⏱️")

# Characters the *bootcamper's own* deliverables carry, which the plugin's
# templates never emit — so scanning the templates could not find them. `↔` and
# `⚠️` shipped as `?` in both PDFs for exactly that reason: a source-pair table
# read "GLEIF ? OPEN-OWNERSHIP" and every caveat began "??". The variation
# selector that trails an emoji is its own character and needs its own entry.
#
# ⛔ This list is about what a *generated deliverable* can contain, not what the
# plugin writes. Add to it whenever a generator learns to render new content.
DELIVERABLE_CHARS = (
    "↔", "⚠️", "⚠", "️", "≈", "±", "×", "–", "•", "⛔",
    "≤", "≥", "≠", "∞", "€", "™", "⇒", "↑", "↓", "←",
    "‑",  # non-breaking hyphen — indistinguishable from "-" on sight
    "​",  # zero-width space — invisible, and it corrupted to "?" all the same
)

# A title long enough to clip at every width the source uses, built from the longest
# real module name so the case stays realistic rather than synthetic.
LONG_TITLE = "Data Quality, Mapping, and Transformation for the Customer Domain"


def latin1_ok(s):
    try:
        s.encode("latin-1")
        return True
    except UnicodeEncodeError:
        return False


def clip_widths():
    """Every width `_clip` is called with in the generator."""
    src = GENERATOR.read_text(encoding="utf-8")
    widths = {int(n) for n in re.findall(r"_clip\([^)]*?,\s*(\d+)\s*\)", src, re.S)}
    return widths


class TestClipStaysLatin1(unittest.TestCase):

    def test_clip_widths_were_found(self):
        """If the call sites stop parsing, the width loop below goes vacuous."""
        self.assertTrue(clip_widths(), "no _clip(x, n) call sites parsed from the source")

    def test_clip_introduces_nothing_outside_latin1(self):
        for width in sorted(clip_widths()):
            with self.subTest(width=width):
                out = GEN._clip(LONG_TITLE, width)
                self.assertLess(len(out), len(LONG_TITLE), "input must actually clip")
                self.assertTrue(
                    latin1_ok(out),
                    f"_clip(..., {width}) produced a non-Latin-1 character: {out!r}. "
                    "Every call site is _clip(_safe(x), n), so _safe cannot sanitize "
                    "what _clip appends — the suffix must be ASCII.",
                )

    def test_the_shipped_composition_order_survives(self):
        """_clip(_safe(x)) is the order in the source; it must be encodable."""
        for width in sorted(clip_widths()):
            for probe in (LONG_TITLE, LONG_TITLE + " — 2026-07-26T14:00:00-07:00"):
                with self.subTest(width=width, probe=probe[:30]):
                    self.assertTrue(latin1_ok(GEN._clip(GEN._safe(probe), width)))

    def test_safe_alone_handles_every_template_character(self):
        for ch in TEMPLATE_CHARS:
            with self.subTest(char=ch):
                self.assertTrue(
                    latin1_ok(GEN._safe(f"prefix {ch} suffix")),
                    f"_safe does not reduce {ch!r} to Latin-1; add it to _UNICODE_MAP",
                )

    def test_safe_handles_characters_the_deliverables_carry(self):
        """Latin-1-encodable is necessary but not sufficient — `?` is encodable."""
        for ch in DELIVERABLE_CHARS:
            with self.subTest(char=ch):
                out = GEN._safe(f"prefix {ch} suffix")
                self.assertTrue(
                    latin1_ok(out),
                    f"_safe does not reduce {ch!r} to Latin-1; add it to _UNICODE_MAP",
                )
                self.assertNotIn(
                    "?", out,
                    f"_safe replaced {ch!r} with '?' — encodable, but the reader sees "
                    "a corrupted glyph. Map it to an ASCII equivalent instead.",
                )


class TestRealisticRecapUsesThePreferredRenderer(unittest.TestCase):
    """The end-to-end symptom: a clipping title must not force the fallback."""

    RECAP = """# Senzing Bootcamp Recap

**Bootcamper:** Ada Lovelace
**Started:** 2026-07-26T09:00:00-07:00

---

## {title} — 2026-07-26T14:00:00-07:00

### Information Shared
- A line with an em dash — and an ellipsis … and a bullet ·

### Questions & Responses
- **Q:** Did the cover chip clip?
    - **R:** Yes — that is the point.

### Actions Taken
- Rendered the cover, whose module chip clips at 46 characters.

### End-of-Module Summary
**What you accomplished:**
- Proved the preferred renderer is still selected.

**Files produced:**
- `docs/bootcamp_recap.pdf` — the keepsake.

**Why it matters:** A silent downgrade to the plainer renderer defeats INV-048.

---
"""

    def setUp(self):
        if importlib.util.find_spec("fpdf") is None:
            self.skipTest("fpdf2 not installed (it is not stdlib — INV-108)")

    def test_a_clipping_title_still_renders_with_fpdf2(self):
        import tempfile

        recap = GEN.parse_recap(self.RECAP.format(title=LONG_TITLE))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "recap.pdf"
            ok = GEN.render_with_fpdf2(recap, out)
            self.assertTrue(
                ok,
                "the designed fpdf2 renderer refused a recap whose module title clips — "
                "the exact silent-downgrade defect this module exists to pin",
            )
            self.assertTrue(out.is_file() and out.stat().st_size > 0)

    def test_the_module_title_actually_clips(self):
        """Otherwise the test above passes without exercising the defect."""
        self.assertGreater(
            len(LONG_TITLE),
            min(clip_widths()),
            "LONG_TITLE no longer exceeds the narrowest clip width, so the "
            "end-to-end assertion would pass vacuously",
        )


if __name__ == "__main__":
    unittest.main()
