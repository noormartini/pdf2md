import re

import fitz
from collections import Counter

# Substrings of PDF font names that indicate a monospace/typewriter font,
# used to detect source-code listings set in a fixed-width font (as opposed
# to the proportional serif/sans fonts used for body text).
_MONOSPACE_FONT_MARKERS = (
    "mono", "courier", "consolas", "menlo", "typewriter", "terminal",
    "firacode", "sourcecodepro", "inconsolata", "dejavusansmono",
    "lucidaconsole", "sftt", "couriernew",
)

# A footnote number immediately glued to a URL (no space), e.g.
# "5https://github.com/...". LaTeX footnote URLs are often set in the same
# monospace/typewriter font as \texttt code, but the line is a footnote, not
# a source-code line — a real listing's line-number gutter is always
# followed by a space.
_FOOTNOTE_URL_RE = re.compile(r"^\d+https?://")

# Bibliography entries commonly set URLs, DOIs and arXiv IDs in the same
# monospace/typewriter font as \texttt code (e.g. "url: https://arxiv.org/
# abs/2404.17605."). These are citation text, not source code, even though
# they share the font — exclude any line carrying one of these markers.
_CITATION_MARKER_RE = re.compile(r"arxiv|doi\.org|https?://", re.IGNORECASE)

# A long URL wrapped across a page can leave a trailing fragment (e.g.
# "abs/2504.08066.") with no "arxiv"/"http" substring left to catch above —
# so as a second line of defence, require at least one genuinely code-shaped
# line (a listing line-number gutter, a Markdown-style "#" line, or common
# code punctuation) to exist anywhere on the page before trusting *any* of
# its monospace lines. Pages that are just citation/URL fragments in a
# \texttt font won't match any of these and get dropped entirely.
_CODE_SIGNAL_RE = re.compile(r"^\d+\s|^#{1,3}\s|[=(){}]|\):\s*$")


def _empirically_monospace_fonts(page: fitz.Page) -> set[str]:
    """Return font names on this page that are fixed-width, by measurement.

    Some PDFs reference their code font internally under a generic name
    (e.g. "F91") that doesn't contain any of the usual monospace name
    substrings. Detect it directly instead: a true monospace font renders
    every character at the same glyph width, while a proportional (body
    text) font doesn't — so measure per-character widths and flag any font
    where they're all nearly identical.
    """
    widths_by_font: dict[str, dict[str, float]] = {}
    for block in page.get_text("rawdict").get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font = span["font"]
                for ch in span.get("chars", []):
                    c = ch["c"]
                    if not c.strip():
                        continue
                    bbox = ch["bbox"]
                    widths_by_font.setdefault(font, {})[c] = bbox[2] - bbox[0]

    monospace_fonts = set()
    for font, widths in widths_by_font.items():
        if len(widths) < 8:
            continue
        vals = list(widths.values())
        avg = sum(vals) / len(vals)
        if avg <= 0:
            continue
        if max(abs(v - avg) for v in vals) / avg < 0.15:
            monospace_fonts.add(font)
    return monospace_fonts


def extract_monospace_lines(page: fitz.Page) -> list[str]:
    """Return the text of every line on a page set in a monospace font, in order.

    Source-code listings are typically typeset in a fixed-width font distinct
    from the body text. pymupdf4llm doesn't recognise this as a signal to wrap
    the content in a fenced code block, so callers use this to reconstruct
    proper code fences in postprocessing.
    """
    empirical_fonts = _empirically_monospace_fonts(page)
    lines: list[str] = []
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            line_text = "".join(s["text"] for s in spans)
            stripped = line_text.strip()
            if not stripped or _FOOTNOTE_URL_RE.match(stripped) or _CITATION_MARKER_RE.search(stripped):
                continue
            # A LaTeX listing's line-number gutter is often set in the body
            # font at a small size, not the monospace code font — so require
            # only a character-weighted majority to be monospace, not all of it.
            total_chars = sum(len(s["text"]) for s in spans)
            mono_chars = sum(
                len(s["text"]) for s in spans
                if any(marker in s["font"].lower() for marker in _MONOSPACE_FONT_MARKERS)
                or s["font"] in empirical_fonts
            )
            if total_chars and mono_chars / total_chars >= 0.6:
                lines.append(line_text)

    if not any(_CODE_SIGNAL_RE.search(l) for l in lines):
        return []
    return lines


def _font_size_to_heading_level(size: float, body_size: float) -> int:
    """Return heading level 1–3 based on ratio to body size, or 0 for body text."""
    if body_size <= 0:
        return 0
    ratio = size / body_size
    if ratio >= 1.8:
        return 1
    if ratio >= 1.4:
        return 2
    if ratio >= 1.15:
        return 3
    return 0


def _page_to_markdown(page: fitz.Page) -> str:
    """Convert a page to markdown text, mapping larger font spans to headings."""
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

    # Character-weighted tally to find body font size (most common by char count)
    size_tally: Counter = Counter()
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if text:
                    size_tally[round(span["size"])] += len(text)

    body_size: float = size_tally.most_common(1)[0][0] if size_tally else 12

    md_lines: list[str] = []
    for block in blocks:
        if block.get("type") != 0:  # skip image and other non-text blocks
            continue
        for line in block.get("lines", []):
            # Dominant size = font size of the span with the most characters
            dominant_size = body_size
            max_chars = 0
            line_text = ""
            for span in line.get("spans", []):
                line_text += span["text"]
                n = len(span["text"].strip())
                if n > max_chars:
                    max_chars = n
                    dominant_size = span["size"]

            stripped = line_text.strip()
            if not stripped:
                continue

            level = _font_size_to_heading_level(dominant_size, body_size)
            if level:
                md_lines.append("#" * level + " " + stripped)
            else:
                md_lines.append(stripped)

    return "\n".join(md_lines)


def extract_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Extract text page by page, using font sizes to detect headings."""
    doc = fitz.open(pdf_path)
    pages = []

    try:
        for i, page in enumerate(doc):  # type: ignore[arg-type]
            if i >= max_pages:
                break
            text = _page_to_markdown(page)
            if text.strip():
                pages.append(text)
    finally:
        doc.close()

    return pages
