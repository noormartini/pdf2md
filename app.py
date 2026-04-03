from config import Config

from extraction.text import extract_pages_from_pdf
from llm.client import convert_pdf_text_to_markdown
from .postprocess import postprocess_markdown

def run(config: Config):
    pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)

    if not pages:
        raise ValueError("No text could be extracted from the PDF.")

    cleaned_pages = []

    for i, page_text in enumerate(pages, start=1):
        print(f"Sending page {i} to LM Studio...")
        cleaned = convert_pdf_text_to_markdown(config.base_url, config.model, page_text)
        cleaned_pages.append(cleaned)

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")