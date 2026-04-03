import fitz


def extract_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Extract text page by page from the PDF."""
    doc = fitz.open(pdf_path)
    pages = []

    try:
        for i, page in enumerate(doc):  # type: ignore[arg-type]
            if i >= max_pages:
                break

            text = page.get_text("text")
            if text and text.strip():
                pages.append(text.strip())
    finally:
        doc.close()

    return pages
