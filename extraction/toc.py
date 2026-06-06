import fitz


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
