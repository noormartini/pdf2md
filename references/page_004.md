## Code Examples

This page demonstrates code block handling.

### Python Example

```python
def extract_text_from_pdf(pdf_path: str, max_pages: int = None) -> list[str]:
    """Extract text from each page of a PDF file.

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (optional)

    Returns:
        List of text strings, one per page
    """
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    pages = []

    for i, page in enumerate(doc):
        if max_pages and i >= max_pages:
            break
        text = page.get_text()
        pages.append(text)

    doc.close()
    return pages
```

### Usage Example

```python
if __name__ == "__main__":
    pages = extract_text_from_pdf("document.pdf", max_pages=5)
    for i, text in enumerate(pages):
        print(f"Page {i+1}: {len(text)} characters")
```
