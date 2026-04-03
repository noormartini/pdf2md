PROMPTS = {
    "default": {
        "system": """\
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
        "user": "{text}",
    }
}
