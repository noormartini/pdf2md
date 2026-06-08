import fitz


def toc_page_indices(pdf_path: str, min_matches: int = 5) -> set[int]:
    """Return 0-based indices of pages that are table-of-contents pages.

    Detects TOC pages by counting how many TOC entry titles appear in each
    page's text. Pages with at least `min_matches` hits are skipped during
    LLM conversion — the programmatic TOC already covers their content.
    """
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    if not toc:
        doc.close()
        return set()

    titles = {title.lower().strip() for _, title, _ in toc}
    indices = set()
    for i in range(len(doc)):
        text = doc[i].get_text("text").lower()
        matches = sum(1 for title in titles if title in text)
        if matches >= min_matches:
            indices.add(i)

    doc.close()
    return indices


def extract_toc(pdf_path: str) -> str:
    """Extract the table of contents from a PDF and format it as Markdown.

    Returns an empty string if the PDF has no embedded TOC.
    Each entry is indented by heading level so nested sections are visible.
    """
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    doc.close()

    if not toc:
        return ""

    lines = ["## Table of Contents\n"]
    for level, title, page in toc:
        indent = "  " * (level - 1)
        lines.append(f"{indent}- {title} ({page})")

    return "\n".join(lines)
