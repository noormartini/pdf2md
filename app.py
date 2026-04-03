import fitz
import requests


def extract_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Extract text page by page from the PDF."""
    doc = fitz.open(pdf_path)
    pages = []

    try:
        for i, page in enumerate(doc): # type: ignore[arg-type]
            if i >= max_pages:
                break

            text = page.get_text("text")
            if text and text.strip():
                pages.append(text.strip())
    finally:
        doc.close()

    return pages


def clean_text_with_llm(base_url: str, model_name: str, text: str) -> str:
    """Send extracted text to LM Studio and get cleaned Markdown back."""
    payload = {
        "model": model_name,
        "input": (
            "Convert the following PDF-extracted text into clean Markdown.\n\n"
            "Rules:\n"
            "- Preserve the original meaning exactly.\n"
            "- Do not invent or add content.\n"
            "- Fix broken line breaks inside paragraphs.\n"
            "- Preserve real paragraph breaks.\n"
            "- Detect likely headings and format them as Markdown headings.\n"
            "- Use # for the document title if clearly visible.\n"
            "- Use ## and ### for section and subsection headings where appropriate.\n"
            "- If text looks like source code, wrap it in fenced code blocks.\n"
            "- If text looks like a list, format it as a Markdown list.\n"
            "- Keep formulas as plain text if unsure.\n"
            "- Return only the final Markdown.\n\n"
            f"TEXT:\n{text}"
        ),
    }

    response = requests.post(f"{base_url}/chat", json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    print("LM Studio response:", data)

    if "output" in data and isinstance(data["output"], list) and len(data["output"]) > 0:
        first_output = data["output"][0]
        if isinstance(first_output, dict) and "content" in first_output:
            return first_output["content"]

    raise ValueError(f"Unexpected LM Studio response: {data}")


def postprocess_markdown(md: str) -> str:
    """Simple cleanup for line endings and excessive blank lines."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip() + "\n"
