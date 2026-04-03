import requests

def convert_pdf_text_to_markdown(base_url: str, model_name: str, text: str) -> str:
    """Send extracted text to LM Studio and get cleaned Markdown back."""
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": """\
Convert the following PDF-extracted text into clean Markdown.

Rules:
- Preserve the original meaning exactly.
- Do not invent or add content.
- Fix broken line breaks inside paragraphs.
- Preserve real paragraph breaks.
- Detect likely headings and format them as Markdown headings.
- Use # for the document title if clearly visible.
- Use ## and ### for section and subsection headings where appropriate.
- If text looks like source code, wrap it in fenced code blocks.
- If text looks like a list, format it as a Markdown list.
- Keep formulas as plain text if unsure.
- Return only the final Markdown.""",
            },
            {"role": "user", "content": f"TEXT:\n{text}"},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }

    response = requests.post(f"{base_url}/chat/completions", json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
