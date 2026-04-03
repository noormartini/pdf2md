from config import Config

from extraction.text import extract_pages_from_pdf
from postprocess import postprocess_markdown
from strategies.text_only import text_strategy

def run(config: Config):
    pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)

    if not pages:
        raise ValueError("No text could be extracted from the PDF.")

    cleaned_pages = []

    match (config.strategy):
        case "text":
            for i, page_text in enumerate(pages, start=1):
                print(f"Sending page {i} to LM Studio...")
                cleaned = text_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default"
                )
                cleaned_pages.append(cleaned)
        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}") 

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")
