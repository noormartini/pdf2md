import fitz
from collections import Counter


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
